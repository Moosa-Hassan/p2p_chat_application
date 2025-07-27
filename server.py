from flask import Flask, request, jsonify, render_template
from node import Node
from system import p2p_System
from flask import session
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
system = p2p_System()

# Store node instances by name
active_nodes = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join', methods=['POST'])
def join():
    data = request.get_json()
    name = data['name']
    ip = data['ip']
    port = int(data['port'])
    session['username'] = name

    if name in active_nodes:
        return jsonify({'status': 'error', 'message': 'Node already exists'}), 400

    node = Node(name, system.get_pos(), ip, port)
    node.listener(ip, port)
    system.add_node(name, ip, port,node)
    active_nodes[name] = node

    return jsonify({'status': 'success', 'message': f'{name} joined on {ip}:{port}'}), 200

@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']

    if sender not in active_nodes:
        return jsonify({'status': 'error', 'message': 'Sender not found'}), 400

    try:
        active_nodes[sender].send_message(receiver, message)
        return jsonify({'status': 'success', 'message': 'Message sent'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/leave', methods=['POST'])
def leave():
    data = request.get_json()
    name = data['name']

    if name not in active_nodes:
        return jsonify({'status': 'error', 'message': 'Node not found'}), 400

    node = active_nodes[name]
    node.leave(system)
    system.remove_node(name)
    del active_nodes[name]

    return jsonify({'status': 'success', 'message': f'{name} has left'}), 200

@app.route('/inbox/<name>', methods=['GET'])
def inbox(name):
    if session.get('username') != name:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    for node in system.nodes_list:
        if node and node.name == name:
            for i in range(len(system.nodes_list)):
                if system.nodes_list[i] and system.nodes_list[i].name == name:
                    pos = i
                    break
            node = system.nodes_list[pos]
            return jsonify({'messages': node.inbox}), 200
    return jsonify({'status': 'error', 'message': 'Node not found'}), 400

@app.route('/nodes', methods=['GET'])
def nodes():
    return jsonify({'nodes': list(active_nodes.keys())})

if __name__ == '__main__':
    app.run(debug=True)
