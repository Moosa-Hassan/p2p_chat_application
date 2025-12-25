from flask import Flask, request, jsonify, render_template
from node import Node
from system import p2p_System
from flask import session
import secrets,socket

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # session key
system = p2p_System()

# Store active node instances by name
active_nodes = {}

def get_ip():
    "Gets IP Address of the machine"
    try:
        # create a socket with external ip and get your ip from sicket information
        soc = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        soc.connect(("8.8.8.8",80))
        ip = soc.getsockname()[0] # return tuple of ip and socket on pur machine
        soc.close()
        return ip
    except:
        return "127.0.0.1" # placeholder 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join', methods=['POST'])
def join():
    data = request.get_json()
    name = data['name']
    session['username'] = name

    if name in active_nodes:
        return jsonify({'status': 'error', 'message': 'Node already exists'}), 400
    
    ip = get_ip()
    port = system.find_available_port()

    node = Node(name,system.get_pos(),ip,port)
    node.listener(ip,port)
    system.add_node(name,ip,port,node)
    active_nodes[name] = node
    system.heartbeat(name)

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
    node.leave()
    system.remove_node(name)
    del active_nodes[name]  

    return jsonify({'status': 'success', 'message': f'{name} has left'}), 200

@app.route('/inbox/<name>', methods=['GET'])
def inbox(name, chat_with=None):
    if session.get('username') != name:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    chat_with = request.args.get("with")

    node = active_nodes.get(name)
    if not node:
        return jsonify({'status': 'error', 'message': 'Node not found'}), 400

    if chat_with:
        # return only one conversation with reciever
        messages = node.inbox.get(chat_with,[])
        return jsonify({'messages': messages}), 200
    else:
        # return all chats not ideal but good for now
        return jsonify({'inbox': node.inbox}), 200

@app.route('/nodes', methods=['GET'])
def nodes():
    lst =[]
    for name in system.nodes_list:
        if name :
            lst.append(name.name)
    return jsonify({'nodes': lst})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    name = data['name']
    if name in active_nodes:
        system.heartbeat(name)
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400


if __name__ == '__main__':
    ip = get_ip()
    print(f"\n{'='*50}")
    print(f"Server starting on {ip}:5000")
    print(f"Access from this machine: http://localhost:5000")
    print(f"Access from network: http://{ip}:5000")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
