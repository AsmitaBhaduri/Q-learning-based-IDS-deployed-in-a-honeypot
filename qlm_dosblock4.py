import os
import sys
import time
import numpy as np
from collections import defaultdict
from scapy.all import sniff, IP
from flask import Flask, jsonify, render_template, request
from threading import Thread

# Flask app setup
app = Flask(__name__)

# Q-learning parameters
num_states = 10
num_actions = 2  # 0: Allow, 1: Block
q_table = np.zeros((num_states, num_actions))
learning_rate = 0.7
discount_factor = 0.9
exploration_rate = 1.0
exploration_decay = 0.995
THRESHOLD = 150  # Packet rate threshold

packet_count = defaultdict(int)
start_time = [time.time()]
blocked_ips = set()
detection_active = [False]  # Control flag for detection

def reward_function(action, packet_rate):
    malicious = 1 if packet_rate > THRESHOLD else 0
    return 1 if action == malicious else -2

def choose_action(state):
    global exploration_rate
    if np.random.rand() < exploration_rate:
        return np.random.choice(num_actions)
    return np.argmax(q_table[state])

def update_q_table(state, action, reward, next_state):
    best_next_action = np.argmax(q_table[next_state])
    q_table[state, action] += learning_rate * (
        reward + discount_factor * q_table[next_state, best_next_action] - q_table[state, action]
    )

def get_state(packet_rate):
    state = int(packet_rate // (THRESHOLD / num_states))
    return min(state, num_states - 1)

def packet_callback(packet):
    if not detection_active[0]:
        return

    src_ip = packet[IP].src
    packet_count[src_ip] += 1
    current_time = time.time()
    time_interval = current_time - start_time[0]

    if time_interval >= 1:  # Process traffic every second
        for ip, count in packet_count.items():
            packet_rate = count / time_interval
            state = get_state(packet_rate)
            action = choose_action(state)
            reward = reward_function(action, packet_rate)
            next_state = get_state(packet_rate)
            update_q_table(state, action, reward, next_state)

            if action == 1 and ip not in blocked_ips:
                print(f"Blocking IP: {ip}, Packet Rate: {packet_rate}")
                os.system(f"iptables -A INPUT -s {ip} -j DROP")
                blocked_ips.add(ip)

        packet_count.clear()
        start_time[0] = current_time

        global exploration_rate
        exploration_rate = max(exploration_rate * exploration_decay, 0.1)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/start_detection', methods=['POST'])
def start_detection():
    detection_active[0] = True
    return jsonify({'message': 'Detection started!'})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    detection_active[0] = False
    return jsonify({'message': 'Detection stopped!'})

@app.route('/blocked_ips')
def get_blocked_ips():
    return jsonify({"blocked_ips": list(blocked_ips)})

def sniff_traffic():
    sniff(filter="ip", prn=packet_callback)

def start_flask():
    app.run(host="127.0.0.1", port=5050)

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("This script requires root privileges.")
        sys.exit(1)

    print("Starting Flask server on http://127.0.0.1:5050")
    print("and packet sniffing..")
    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    sniff_traffic()
