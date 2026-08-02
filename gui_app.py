import tkinter as tk
from tkinter import messagebox
import secure_auth
import mfa

# keeps track of who is mid-login (passed step 1, waiting for MFA code)
pending_login = {"username": None}


def show_secret_dialog(username, secret):

    win = tk.Toplevel(root)
    win.title("Save your MFA secret")
    win.geometry("380x180")
    win.grab_set()  # keeps focus on this window until closed

    tk.Label(win, text=f"Registered '{username}' successfully!",
             font=("Arial", 10, "bold")).pack(pady=(15, 5))

    tk.Label(win, text="Add this key to Google Authenticator\n"
                        "(Manual entry -> Time based):").pack()

    secret_box = tk.Entry(win, width=36, justify="center", font=("Courier", 11))
    secret_box.insert(0, secret)
    secret_box.config(state="readonly")
    secret_box.pack(pady=8)
    secret_box.selection_range(0, tk.END)  # pre-selects the text on open

    def copy_to_clipboard():
        win.clipboard_clear()
        win.clipboard_append(secret)
        win.update()  # keeps clipboard content after window closes
        copy_btn.config(text="Copied!")
        win.after(1200, lambda: copy_btn.config(text="Copy to Clipboard"))

    copy_btn = tk.Button(win, text="Copy to Clipboard", command=copy_to_clipboard)
    copy_btn.pack(pady=5)

    tk.Button(win, text="Done", command=win.destroy).pack(pady=5)


def do_register():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Missing info", "Enter both username and password.")
        return

    result = secure_auth.register(username, password)

    if result["success"]:
        show_secret_dialog(username, result["mfa_secret"])
    else:
        messagebox.showerror("Registration failed", result["message"])

    password_entry.delete(0, tk.END)  # never leave the password sitting in the field


def do_login_password():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Missing info", "Enter both username and password.")
        return

    result = secure_auth.login_step1_password(username, password)
    password_entry.delete(0, tk.END)

    if result["success"]:
        pending_login["username"] = username
        mfa_frame.pack(pady=10)  # reveal the MFA code entry box
        messagebox.showinfo("Step 1 passed", result["message"])
    else:
        messagebox.showerror("Login failed", result["message"])


def do_login_mfa():
    username = pending_login["username"]
    if not username:
        messagebox.showwarning("Wait", "Enter your password first.")
        return

    code = mfa_entry.get().strip()
    result = secure_auth.login_step2_mfa(username, code)
    mfa_entry.delete(0, tk.END)

    if result["success"]:
        messagebox.showinfo("Welcome", result["message"])
        pending_login["username"] = None
        mfa_frame.pack_forget()
    else:
        messagebox.showerror("MFA failed", result["message"])


def fill_dev_code():

    username = pending_login["username"]
    if not username:
        messagebox.showwarning("Wait", "Enter your password first.")
        return

    users = secure_auth.load_users()
    secret = users[username]["mfa_secret"]
    code = mfa.get_current_otp(secret)

    mfa_entry.delete(0, tk.END)
    mfa_entry.insert(0, code)


# ---------------- window layout ----------------

root = tk.Tk()
root.title("CloudExify Secure Auth")
root.geometry("380x480")
root.resizable(True, True)

tk.Label(root, text="CloudExify Secure Login", font=("Arial", 14, "bold")).pack(pady=10)

tk.Label(root, text="Username").pack()
username_entry = tk.Entry(root, width=30)
username_entry.pack()

tk.Label(root, text="Password").pack()
password_entry = tk.Entry(root, width=30, show="*")
password_entry.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Register", width=12, command=do_register).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Login", width=12, command=do_login_password).grid(row=0, column=1, padx=5)

# MFA box - hidden until password step succeeds
mfa_frame = tk.Frame(root)
tk.Label(mfa_frame, text="Enter MFA code from your authenticator app").pack()
mfa_entry = tk.Entry(mfa_frame, width=15, justify="center")
mfa_entry.pack(pady=5)
tk.Button(mfa_frame, text="Verify Code", command=do_login_mfa).pack(pady=2)
tk.Button(mfa_frame, text="[DEV] Autofill current code", fg="gray",
          command=fill_dev_code).pack(pady=2)

tk.Label(
    root,
    text="Passwords: 12+ chars, 1 number, 1 symbol.\n3 wrong tries locks the account 60s.",
    fg="gray", font=("Arial", 8), justify="center"
).pack(pady=10)

if __name__ == "__main__":
    root.mainloop()