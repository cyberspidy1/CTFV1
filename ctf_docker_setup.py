#!/usr/bin/env python3
"""
CTF Docker Environment Setup Script
Creates a controlled cybersecurity training environment with:
- Kali Linux attacker container
- Vulnerable target container with intentional security flaws
- Live dashboard for flag tracking
- Private Docker network
"""

import os
import subprocess
import time
import base64
from pathlib import Path

class CTFEnvironment:
    def __init__(self):
        self.project_dir = Path("ctf_environment")
        self.network_name = "ctf_network"
        
    def create_project_structure(self):
        """Create necessary directories and files"""
        print("[+] Creating project structure...")
        
        # Create directories
        dirs = [
            self.project_dir,
            self.project_dir / "vulnerable_container",
            self.project_dir / "dashboard",
            self.project_dir / "kali"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
    def create_vulnerable_dockerfile(self):
        """Create Dockerfile for vulnerable container with intentional CVEs"""
        print("[+] Creating vulnerable container Dockerfile...")
        
        # Encode flags in base64
        flag1 = base64.b64encode(b"CTF{y0u_f0und_th3_f1rst_fl4g}").decode()
        flag2 = base64.b64encode(b"CTF{pr1v1l3g3_3sc4l4t10n_m4st3r}").decode()
        flag3 = base64.b64encode(b"CTF{r00t_4cc3ss_4ch13v3d}").decode()
        
        dockerfile_content = f'''FROM ubuntu:18.04

# Disable interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install vulnerable versions and services
RUN apt-get update && apt-get install -y \\
    openssh-server \\
    vsftpd \\
    apache2 \\
    php \\
    curl \\
    netcat \\
    sudo \\
    python3 \\
    python3-pip

# Vulnerability 1: Weak SSH credentials
RUN useradd -m -s /bin/bash ctfuser && \\
    echo 'ctfuser:password123' | chpasswd && \\
    echo 'ctfuser ALL=(ALL) NOPASSWD: /usr/bin/find' >> /etc/sudoers

# Hide FLAG 1 in user's home (accessible after SSH)
RUN echo "{flag1}" > /home/ctfuser/.flag1.txt && \\
    chmod 600 /home/ctfuser/.flag1.txt && \\
    chown ctfuser:ctfuser /home/ctfuser/.flag1.txt

# Vulnerability 2: Command injection in web application
RUN mkdir -p /var/www/html

# Create vulnerable PHP file
COPY ping.php /var/www/html/ping.php

# Hide FLAG 2 in web directory (accessible via command injection)
RUN echo "{flag2}" > /var/www/.flag2.txt && \\
    chmod 644 /var/www/.flag2.txt

# Hide FLAG 3 in root (requires privilege escalation)
RUN echo "{flag3}" > /root/flag3.txt && \\
    chmod 600 /root/flag3.txt

# Configure SSH
RUN mkdir /var/run/sshd && \\
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \\
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Setup flag submission script
RUN pip3 install requests

# Create flag submission script
COPY submit_flag.py /usr/local/bin/submit_flag.py
RUN chmod +x /usr/local/bin/submit_flag.py

# Expose ports
EXPOSE 22 80

# Start services
CMD service ssh start && apache2ctl -D FOREGROUND
'''
        
        # Create the ping.php file separately
        ping_php_content = '''<?php
if(isset($_GET['ip'])) {
    $ip = $_GET['ip'];
    // Vulnerable to command injection
    $output = shell_exec("ping -c 1 " . $ip);
    echo "<pre>$output</pre>";
}
?>
<html>
<body>
<h2>Network Ping Tool</h2>
<form method="get">
IP Address: <input type="text" name="ip">
<input type="submit" value="Ping">
</form>
</body>
</html>
'''
        
        # Create the submit_flag.py script separately
        submit_flag_content = '''#!/usr/bin/env python3
import requests
import sys
import base64

if len(sys.argv) != 2:
    print("Usage: submit_flag.py <flag>")
    sys.exit(1)

flag = sys.argv[1]
try:
    # Try to decode if it's base64
    decoded = base64.b64decode(flag).decode()
    if decoded.startswith("CTF{"):
        flag = decoded
except:
    pass

try:
    response = requests.post('http://dashboard:5000/submit', 
                           json={'flag': flag},
                           timeout=5)
    print(response.text)
except Exception as e:
    print(f"Error submitting flag: {e}")
'''
        
        with open(self.project_dir / "vulnerable_container" / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        with open(self.project_dir / "vulnerable_container" / "ping.php", "w") as f:
            f.write(ping_php_content)
        
        with open(self.project_dir / "vulnerable_container" / "submit_flag.py", "w") as f:
            f.write(submit_flag_content)
    
    def create_kali_dockerfile(self):
        """Create Dockerfile for Kali Linux with tools"""
        print("[+] Creating Kali Linux Dockerfile...")
        
        dockerfile_content = '''FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

# Update and install metasploit and common tools
RUN apt-get update && apt-get install -y \\
    metasploit-framework \\
    nmap \\
    sqlmap \\
    nikto \\
    hydra \\
    john \\
    dirb \\
    netcat-traditional \\
    curl \\
    wget \\
    python3 \\
    python3-pip \\
    vim \\
    && apt-get clean

# Initialize metasploit database
RUN msfdb init || true

# Copy helpful readme
COPY README.txt /root/README.txt

WORKDIR /root
CMD ["/bin/bash"]
'''
        
        readme_content = '''=== CTF Challenge Environment ===

Target: vulnerable_target (use this hostname)

Services running on target:
- SSH (port 22) - Try to find credentials
- HTTP (port 80) - Check for web vulnerabilities

Hints:
1. Start with reconnaissance (nmap)
2. Look for weak credentials
3. Examine web applications for injection flaws
4. Think about privilege escalation

Flags are base64 encoded. Decode them and submit via:
  curl -X POST http://dashboard:5000/submit -H "Content-Type: application/json" -d '{"flag":"YOUR_DECODED_FLAG"}'

Or from the target machine:
  python3 /usr/local/bin/submit_flag.py <base64_flag>

Good luck!
'''
        
        with open(self.project_dir / "kali" / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        with open(self.project_dir / "kali" / "README.txt", "w") as f:
            f.write(readme_content)
    
    def create_dashboard(self):
        """Create live dashboard application"""
        print("[+] Creating dashboard application...")
        
        # Dashboard Dockerfile
        dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates templates/

EXPOSE 5000

CMD ["python", "app.py"]
'''
        
        # Requirements
        requirements = '''flask==2.3.0
flask-socketio==5.3.0
python-socketio==5.9.0
'''
        
        # Flask application
        app_content = '''from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import base64
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ctf_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Expected flags (base64 decoded versions)
VALID_FLAGS = {
    "CTF{y0u_f0und_th3_f1rst_fl4g}": "Flag 1: SSH Access",
    "CTF{pr1v1l3g3_3sc4l4t10n_m4st3r}": "Flag 2: Command Injection",
    "CTF{r00t_4cc3ss_4ch13v3d}": "Flag 3: Root Access"
}

captured_flags = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_flag():
    data = request.get_json()
    flag = data.get('flag', '').strip()
    
    # Try to decode if base64
    try:
        decoded = base64.b64decode(flag).decode()
        if decoded in VALID_FLAGS:
            flag = decoded
    except:
        pass
    
    if flag in VALID_FLAGS:
        if flag not in [f['flag'] for f in captured_flags]:
            flag_data = {
                'flag': flag,
                'name': VALID_FLAGS[flag],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            captured_flags.append(flag_data)
            
            # Broadcast to all connected clients
            socketio.emit('flag_captured', flag_data, broadcast=True)
            
            return jsonify({
                'success': True, 
                'message': f'Congratulations! {VALID_FLAGS[flag]} captured!',
                'total': len(captured_flags)
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Flag already captured!'
            })
    else:
        return jsonify({
            'success': False, 
            'message': 'Invalid flag!'
        })

@app.route('/status')
def status():
    return jsonify({
        'captured': len(captured_flags),
        'total': len(VALID_FLAGS),
        'flags': captured_flags
    })

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
'''
        
        # HTML template
        html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>CTF Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #00ff00;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.8);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        h1 {
            text-align: center;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
        }
        .stat-box {
            background: rgba(0, 255, 0, 0.1);
            padding: 20px;
            border-radius: 5px;
            border: 2px solid #00ff00;
            text-align: center;
            min-width: 150px;
        }
        .stat-number {
            font-size: 48px;
            font-weight: bold;
        }
        .flags-list {
            margin-top: 30px;
        }
        .flag-item {
            background: rgba(0, 255, 0, 0.1);
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #00ff00;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            from {
                transform: translateX(-100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        .flag-name {
            font-size: 18px;
            font-weight: bold;
            color: #00ff00;
        }
        .flag-value {
            color: #888;
            font-size: 14px;
        }
        .timestamp {
            color: #666;
            font-size: 12px;
            float: right;
        }
        .blink {
            animation: blink 1s infinite;
        }
        @keyframes blink {
            50% { opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚩 CTF CHALLENGE DASHBOARD 🚩</h1>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number" id="captured-count">0</div>
                <div>Flags Captured</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">3</div>
                <div>Total Flags</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="progress">0%</div>
                <div>Progress</div>
            </div>
        </div>
        
        <div class="flags-list">
            <h2>Captured Flags <span class="blink" id="status-indicator" style="display:none;">●</span></h2>
            <div id="flags-container">
                <p style="color: #666; text-align: center;">No flags captured yet. Start hacking!</p>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let capturedCount = 0;
        const totalFlags = 3;
        
        socket.on('connect', function() {
            console.log('Connected to dashboard');
            loadStatus();
        });
        
        socket.on('flag_captured', function(data) {
            showStatusIndicator();
            addFlag(data);
        });
        
        function showStatusIndicator() {
            const indicator = document.getElementById('status-indicator');
            indicator.style.display = 'inline';
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 2000);
        }
        
        function loadStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    capturedCount = data.captured;
                    updateStats();
                    
                    const container = document.getElementById('flags-container');
                    if (data.flags.length > 0) {
                        container.innerHTML = '';
                        data.flags.forEach(flag => {
                            addFlag(flag, false);
                        });
                    }
                });
        }
        
        function addFlag(flag, animate = true) {
            const container = document.getElementById('flags-container');
            if (capturedCount === 0) {
                container.innerHTML = '';
            }
            
            const flagDiv = document.createElement('div');
            flagDiv.className = 'flag-item';
            if (!animate) flagDiv.style.animation = 'none';
            
            flagDiv.innerHTML = `
                <span class="timestamp">${flag.timestamp}</span>
                <div class="flag-name">${flag.name}</div>
                <div class="flag-value">${flag.flag}</div>
            `;
            
            container.appendChild(flagDiv);
            
            capturedCount++;
            updateStats();
        }
        
        function updateStats() {
            document.getElementById('captured-count').textContent = capturedCount;
            const progress = Math.round((capturedCount / totalFlags) * 100);
            document.getElementById('progress').textContent = progress + '%';
        }
        
        // Initial load
        loadStatus();
    </script>
</body>
</html>
'''
        
        # Write all dashboard files
        with open(self.project_dir / "dashboard" / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        with open(self.project_dir / "dashboard" / "requirements.txt", "w") as f:
            f.write(requirements)
        
        with open(self.project_dir / "dashboard" / "app.py", "w") as f:
            f.write(app_content)
        
        (self.project_dir / "dashboard" / "templates").mkdir(exist_ok=True)
        with open(self.project_dir / "dashboard" / "templates" / "index.html", "w") as f:
            f.write(html_content)
    
    def create_docker_compose(self):
        """Create docker-compose.yml for orchestration"""
        print("[+] Creating docker-compose configuration...")
        
        compose_content = f'''version: '3.8'

services:
  vulnerable_target:
    build: ./vulnerable_container
    container_name: ctf_vulnerable_target
    hostname: vulnerable_target
    networks:
      - {self.network_name}
    ports:
      - "2222:22"
      - "8080:80"
    cap_add:
      - NET_ADMIN

  kali_attacker:
    build: ./kali
    container_name: ctf_kali_attacker
    hostname: kali_attacker
    stdin_open: true
    tty: true
    networks:
      - {self.network_name}
    depends_on:
      - vulnerable_target
      - dashboard

  dashboard:
    build: ./dashboard
    container_name: ctf_dashboard
    hostname: dashboard
    networks:
      - {self.network_name}
    ports:
      - "5000:5000"

networks:
  {self.network_name}:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
'''
        
        with open(self.project_dir / "docker-compose.yml", "w") as f:
            f.write(compose_content)
    
    def build_and_deploy(self):
        """Build and start all containers"""
        print("[+] Building and deploying CTF environment...")
        print("    This may take several minutes...")
        
        os.chdir(self.project_dir)
        
        # Build containers
        subprocess.run(["docker-compose", "build"], check=True)
        
        # Start containers
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        print("\n" + "="*60)
        print("CTF ENVIRONMENT DEPLOYED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📊 Dashboard: http://localhost:5000")
        print(f"🎯 Vulnerable Target SSH: localhost:2222")
        print(f"🌐 Vulnerable Target Web: http://localhost:8080")
        print(f"\n🔧 Access Kali Linux:")
        print(f"   docker exec -it ctf_kali_attacker /bin/bash")
        print(f"\n📝 View logs:")
        print(f"   docker-compose logs -f")
        print(f"\n🛑 Stop environment:")
        print(f"   docker-compose down")
        print("="*60)
        
        # Wait for services to be ready
        print("\n[+] Waiting for services to start...")
        time.sleep(10)
        
        print("\n✅ Environment is ready! Happy hacking!")
    
    def run(self):
        """Execute the full setup"""
        try:
            self.create_project_structure()
            self.create_vulnerable_dockerfile()
            self.create_kali_dockerfile()
            self.create_dashboard()
            self.create_docker_compose()
            self.build_and_deploy()
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error during deployment: {e}")
            print("Make sure Docker and docker-compose are installed and running.")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║        CTF Docker Environment Setup Script                ║
║        Educational Cybersecurity Training Platform        ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    print("⚠️  WARNING: This creates intentionally vulnerable systems")
    print("    for educational purposes only. Use in isolated")
    print("    environments. Never expose to the internet!\n")
    
    ctf = CTFEnvironment()
    ctf.run()
