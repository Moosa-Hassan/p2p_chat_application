from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import socket
import threading
import requests, time


class Node:
    
    def __init__(self,name:str,pos:int,ip,port):
        """
        this is supposed to have a private public keys, the name of host, position 
        in the list and holds a directory of name to list of ip address and public key
        """
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.__private_key.public_key()
        self.name = name
        self.position = pos
        self.ip = ip 
        self.port = port
        # directory = [name] -> [ipaddress,port,pubkey]
        self.directory = {}
        self.running = True
        self.inbox = {}  # {name : [(sender, message)]}
        self.server_soc = socket.socket()
        
    def connect(self, system:dict):
        """
        Used to connect a node to the p2p network
        """
        system[self.name] = self.public_key
        
    def update_directory(self,name:str,flag,pub_key=None,ip="0.0.0.0",port=3000):
        """
        Used to update directory.
        J means join
        L means leave
        """
        if flag=="J":
            self.directory[name]=[ip,port,pub_key]
        elif flag=="L":
            self.directory.pop(name,None)
            
    def get_name(self, addr):
        """
        Returns the name of node corresponding to the address
        """
        ip,port = addr
        for name, details in self.directory.items():
            print(f"Checking {name} against {addr[0]} with details {details[0]}")
            n_ip,n_port = details
            if ip==n_ip and port==n_port:
                return name
        return None
        
    def listener(self, ip:str,port:int):
        def run_server():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((ip, port))
            server.settimeout(1)
            server.listen()
            self.server_soc = server
            print(f"[{self.name}] Listening on {ip}:{port}")

            while self.running:
                try:
                    conn, addr = server.accept()
                except:
                    continue
                try: 
                    data = conn.recv(4096)
                    if data:
                        message = self.recieve_message(data)
                        print(f"[{self.name}] Received message from {addr}: {message}")
                        message_split = message.split("|")
                        if message not in ["Error Code 9329", "Error Code 2746"]:
                            sender, text = message.split("|", 1)
                            # make sure inbox exists
                            self.inbox.setdefault(sender, [])
                            self.inbox[sender].append((sender, text))
                        if message == "Error Code 9329":# decryption failed
                            continue
                        if message == "Error Code 2746":# node left
                            conn.close()
                            break
                        print(f"[{self.name}] Message from {message_split[0]}: {message_split[1]}")
                finally:
                    conn.close()
            server.close()

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

        
    def recieve_message(self,msg):
        """
        Decodes the message recieved
        """
        try:
            return self.__private_key.decrypt(msg,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)).decode()
        except:
            return "Error Code 9329"
    
    def send_message(self,name:str,msge:str):
        """
        Takes message from user and creates a socket with target 
        """
        if name not in self.directory.keys():
            print("User not in directory")
            return
        msg = f"{self.name}|{msge}"
        self.inbox.setdefault(name, [])
        self.inbox[name].append(("You", msge))
        cipher_text = self.directory[name][2].encrypt(msg.encode(),padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.directory[name][0],self.directory[name][1]))
            sock.sendall(cipher_text)
        
        
    def leave(self):
        """
        Leaves the system
        """
        self.running = False  # Stop the listener loop
        self.directory.pop(self.name,None)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.ip, self.port))
                sock.sendall(b'Error Code 2746')# to close circuit
                self.server_soc.close()
        except:
            pass  
        
