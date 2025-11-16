from node import Node
import time, threading

class p2p_System:
    def __init__(self):
        self.nodes_list = []
        self.last_seen = {}  # {name: timestamp}
        self.lock = threading.Lock() 
        self.used_ports = set()  # Tracks used ports
        self.next_port = 8000  # Start assigening ports from port 8000
        threading.Thread(target=self.cleanup, daemon=True).start()
        
    def find_available_port(self):
        """ To find a port which is available"""
        with self.lock:
            while self.next_port in self.used_ports:
                self.next_port += 1
            self.used_ports.add(self.next_port)
            self.next_port += 1
            return self.next_port -1
        
    def release_port(self,port):
        """ Mark a port as free so it may be used"""
        with self.lock:
            self.used_ports.discard(port)
        
    def get_pos(self):
        with self.lock:
            for i in range(len(self.nodes_list)):
                if self.nodes_list[i] == None:
                    return i
            return len(self.nodes_list)
    
    def heartbeat(self, name):
        with self.lock:
            self.last_seen[name] = time.time()
        
    def cleanup(self):
        while True:
            time.sleep(3)
            with self.lock:
                now = time.time()
                to_remove = [name for name, ts in self.last_seen.items() if now - ts > 10]
            
            for name in to_remove:
                self.remove_node(name)
                with self.lock:
                    self.last_seen.pop(name, None)
        
    def add_node(self, name: str, ip, port, node: Node = None):
        with self.lock:
            self.nodes_list.append(node)
            # Initialize heartbeat timestamp immediately
            self.last_seen[name] = time.time()
        self.broadcast(node.position)
        
    def broadcast(self, pos: int):
        with self.lock:
            if pos >= len(self.nodes_list) or self.nodes_list[pos] is None:
                return
            
            name = self.nodes_list[pos].name
            pub_key = self.nodes_list[pos].public_key
            ip = self.nodes_list[pos].ip
            port = self.nodes_list[pos].port
            
            for i in range(len(self.nodes_list)):
                if self.nodes_list[i] and i != pos:
                    self.nodes_list[i].update_directory(name, "J", pub_key, ip, port)
                    o_name = self.nodes_list[i].name
                    o_pub_key = self.nodes_list[i].public_key
                    o_ip = self.nodes_list[i].ip
                    o_port = self.nodes_list[i].port
                    self.nodes_list[pos].update_directory(o_name, "J", o_pub_key, o_ip, o_port)
        
    def remove_node(self, name: str):
        with self.lock:
            port_to_release = None
            for nde in self.nodes_list:
                if nde:
                    nde.update_directory(name, "L")
            # find port
            for i, node in enumerate(self.nodes_list):
                if node and node.name == name:
                    port_to_release = node.port
                    self.nodes_list[i] = None
                    break
            # release port
            if port_to_release:
                self.release_port(port_to_release)
