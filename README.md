# Q-learning-based-IDS-deployed-in-a-honeypot
Simulating a Q-learning-powered IDS on Kali Linux, integrating a honeypot to detect and mitigate DoS attacks in real time by analyzing packet rates and dynamically blocking malicious IP addresses.

# Features
1. Machine Learning-based Detection using Q-learning.
2. Real-time DoS Mitigation with automated IP blocking.
3. Honeypot Integration for attack analysis.
4. Web Dashboard to monitor blocked IPs.

# Setup & Usage
1. Clone the repository:<br>
    git clone https://github.com/AsmitaBhaduri/Q-learning-based-IDS-deployed-in-a-honeypot.git <br>
    cd Q-learning-based-IDS-deployed-in-a-honeypot
2. Install dependencies: <br>
    pip install flask numpy scapy
3. Run the script with root privileges:<br>
    sudo python3 qlm_dosblock4.py
4. Access the web dashboard:<br>
    http://127.0.0.1:5000
