from node import Node


"""
Race conditins have to check
"""

class p2p_System:
    def __init__(self):
        # self.count = 0
        self.nodes_list = []
        
    def get_pos(self):
        for i in range(len(self.nodes_list)):
            if self.nodes_list[i] == None:
                return i
        return len(self.nodes_list)
        
        
    def add_node(self,name:str,ip,port,node:Node=None):
        self.nodes_list.append(node)
        self.broadcast(node.position)
        
    def broadcast(self,pos:int):
        name,pub_key,ip,port = self.nodes_list[pos].name,self.nodes_list[pos].public_key,self.nodes_list[pos].ip,self.nodes_list[pos].port
        for i in range(len(self.nodes_list)):
            if self.nodes_list[i] and i != pos:
                self.nodes_list[i].update_directory(name,"J",pub_key,ip,port)
                o_name,o_pub_key,o_ip,o_port = self.nodes_list[i].name,self.nodes_list[i].public_key,self.nodes_list[i].ip,self.nodes_list[i].port
                self.nodes_list[pos].update_directory(o_name,"J",o_pub_key,o_ip,o_port)
        
    def remove_node(self,name:str):
        for nde in self.nodes_list:
            if nde:
                nde.update_directory(name,"L")
        for i, node in enumerate(self.nodes_list):
            if node and node.name == name:
                self.nodes_list[i] = None
                break
        
    