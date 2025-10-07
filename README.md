# CTFV1
An automated, isolated Capture The Flag (CTF) environment for learning penetration testing and cybersecurity concepts. Features intentionally vulnerable systems, a Kali Linux attacker machine, and a real-time flag tracking dashboard.
⚠️ Security Warning
EDUCATIONAL USE ONLY: This project creates intentionally vulnerable systems for cybersecurity training. Never expose these containers to the internet or use in production environments. Use only in isolated lab/testing environments.
✨ Features

🐧 Kali Linux Attack Machine: Pre-configured with Metasploit, Nmap, Hydra, and 15+ pentesting tools
🎯 Vulnerable Target System: Ubuntu container with multiple exploitable vulnerabilities
📊 Live Dashboard: Real-time flag capture tracking with WebSocket updates
🔒 Isolated Network: Private Docker network for safe testing
🏁 3 Hidden Flags: Base64-encoded challenges testing different exploitation techniques
🚀 One-Click Deployment: Single Python script sets up entire environment

🎓 Learning Objectives
This CTF teaches:

Network reconnaissance and scanning
Credential brute-forcing
Web application vulnerabilities (Command Injection)
SSH exploitation
Linux privilege escalation
Post-exploitation techniques

🛠️ Prerequisites

Docker Engine 20.10+
Docker Compose 2.0+
Python 3.8+
4GB+ RAM
10GB+ free disk space

1. Clone and Deploy
bash# Download the script
git clone https://github.com/yourusername/ctf-docker-environment.git
cd ctf-docker-environment

# Run the deployment script
sudo python3 ctf_docker_setup.py
The script will:

Create project structure
Build 3 Docker containers
Set up private network
Deploy the entire environment

Build time: 5-10 minutes (downloads Kali Linux and installs tools)
2. Access the Environment
Dashboard (Flag Tracker):
http://localhost:5000
Vulnerable Target:

SSH: localhost:2222
Web: http://localhost:8080

Kali Linux:
bashdocker exec -it ctf_kali_attacker /bin/bash
🎯 Challenge Overview
Vulnerabilities Implemented
VulnerabilityTypeDifficultyFlagWeak SSH CredentialsAuthenticationEasyFlag 1PHP Command InjectionWeb ApplicationMediumFlag 2Sudo MisconfigurationPrivilege EscalationMediumFlag 3
Flag Locations

Flag 1: /home/ctfuser/.flag1.txt - Requires SSH access
Flag 2: /var/www/.flag2.txt - Requires web exploitation
Flag 3: /root/flag3.txt - Requires root privileges

All flags are base64 encoded.
📖 Walkthrough Hints
<details>
<summary>🔍 Hint 1: Reconnaissance</summary>
Start by scanning the target:
bashnmap -sV -p- vulnerable_target
Look for open ports and running services.
</details>
<details>
<summary>🔑 Hint 2: Initial Access</summary>
Try common/weak credentials on SSH:
bashhydra -l ctfuser -P /usr/share/wordlists/rockyou.txt vulnerable_target ssh
Or guess common passwords manually.
</details>
<details>
<summary>🌐 Hint 3: Web Exploitation</summary>
The web application has a ping tool. Test for command injection:
http://vulnerable_target/ping.php?ip=127.0.0.1;ls
Try different payloads to read files.
</details>
<details>
<summary>⬆️ Hint 4: Privilege Escalation</summary>
Check sudo permissions:
bashsudo -l
The find command can be exploited for privilege escalation.
</details>
🏆 Submitting Flags
Method 1: From Kali Container
bashcurl -X POST http://dashboard:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"flag":"CTF{decoded_flag_here}"}'
Method 2: From Target (if compromised)
bashpython3 /usr/local/bin/submit_flag.py <base64_encoded_flag>
Method 3: From Host Machine
bashcurl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"flag":"CTF{decoded_flag_here}"}'
The dashboard updates in real-time when flags are captured! 🎉
🔧 Management Commands
View Logs
bashcd ctf_environment
docker-compose logs -f
Restart Services
bashdocker-compose restart
Stop Environment
bashdocker-compose down
Rebuild from Scratch
bashdocker-compose down -v
docker-compose up -d --build
Access Container Shells
bash# Kali Linux
docker exec -it ctf_kali_attacker /bin/bash

# Vulnerable Target
docker exec -it ctf_vulnerable_target /bin/bash

# Dashboard
docker exec -it ctf_dashboard /bin/bash
📁 Project Structure
ctf_environment/
├── docker-compose.yml          # Orchestration configuration
├── vulnerable_container/       # Target system
│   ├── Dockerfile
│   ├── ping.php               # Vulnerable web app
│   └── submit_flag.py         # Flag submission script
├── kali/                      # Attacker machine
│   ├── Dockerfile
│   └── README.txt             # Challenge hints
└── dashboard/                 # Web dashboard
    ├── Dockerfile
    ├── app.py                 # Flask application
    ├── requirements.txt
    └── templates/
        └── index.html         # Dashboard UI
🛡️ Security Considerations

Network Isolation: Uses private Docker network (172.20.0.0/16)
No Internet Exposure: Containers are not accessible from outside the host
Controlled Vulnerabilities: Only specific, documented vulnerabilities exist
Educational Purpose: Designed for learning, not real-world exploitation

🐛 Troubleshooting
Dashboard won't start
bashdocker-compose restart dashboard
docker-compose logs dashboard
Can't connect to containers
bashdocker network inspect ctf_environment_ctf_network
Ports already in use
Edit docker-compose.yml to change ports:
yamlports:
  - "2223:22"  # Change 2222 to 2223
  - "8081:80"  # Change 8080 to 8081
Reset everything
bashdocker-compose down -v
sudo python3 ctf_docker_setup.py
🎓 Learning Resources

OWASP Top 10
Metasploit Unleashed
HackTheBox Academy
TryHackMe
