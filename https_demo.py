

from flask import Flask, request, session
import secure_auth

app = Flask(__name__)
# needed so Flask can remember "who passed step 1" between the two requests
app.secret_key = "cloudexify-demo-secret-key-not-for-production"

LOGIN_PAGE = """
<h2>CloudExify Secure Login (running over HTTPS)</h2>
<p>Look at your browser's address bar - the lock icon means this page
and anything you type is encrypted in transit.</p>
<form method="POST" action="/login">
    Username: <input name="username"><br><br>
    Password: <input name="password" type="password"><br><br>
    <input type="submit" value="Login">
</form>
"""

MFA_PAGE = """
<h2>Step 2 - Multi-Factor Authentication</h2>
<p>Password correct for <b>{username}</b>. Enter the 6-digit code from
your authenticator app (Google Authenticator / WinOTP / etc).</p>
<form method="POST" action="/verify-mfa">
    MFA Code: <input name="code" autocomplete="off"><br><br>
    <input type="submit" value="Verify Code">
</form>
"""


@app.route("/")
def home():
    return LOGIN_PAGE


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    # NOTE: we never print/log the raw password - only pass it straight
    # into the hashing/verification function.
    result = secure_auth.login_step1_password(username, password)

    if result["success"]:
        # remember who's mid-login so /verify-mfa knows whose secret to check
        session["pending_user"] = username
        return MFA_PAGE.format(username=username)
    else:
        return result["message"]


@app.route("/verify-mfa", methods=["POST"])
def verify_mfa():
    username = session.get("pending_user")
    if not username:
        return "Session expired - go back to / and log in again with your password first."

    code = request.form["code"].strip()
    result = secure_auth.login_step2_mfa(username, code)

    if result["success"]:
        session.pop("pending_user", None)  # clear so it can't be reused
        return f"<h2>{result['message']}</h2><p>Welcome, {username}!</p>"
    else:
        return f"<h2>{result['message']}</h2><p><a href='/'>Try again</a></p>"


if __name__ == "__main__":
    print("Starting HTTPS server at https://127.0.0.1:5000")
    print("Your browser will warn about the self-signed certificate -")
    print("that's expected for a local dev demo. Click 'Advanced -> Proceed'.")
    # 'adhoc' tells Flask to auto-generate a temporary self-signed cert
    app.run(host="127.0.0.1", port=5000, ssl_context="adhoc", debug=False)