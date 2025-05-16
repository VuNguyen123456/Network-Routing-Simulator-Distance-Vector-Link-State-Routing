import socket
import json
from copy import deepcopy
import time
from threading import Thread, Condition

# Global variables
graph = []
N = 5
stop_simulation = False
shared_turn = 0
turn_lock = Condition()
global_round = 0

BASE_PORT = 10280
node = {
    0: 'A',
    1: 'B',
    2: 'C',
    3: 'D',
    4: 'E'
}

class Node(Thread):
    def __init__(self, node_id, node_index, dv_vector):
        Thread.__init__(self)
        self.node_id = node_id
        self.node_index = node_index
        self.dv_matrix = [[999] * N for _ in range(N)]
        self.dv_matrix[self.node_index] = dv_vector[:]
        self.last_dv_matrix = deepcopy(self.dv_matrix)
        self.neighbor_index = [i for i, cost in enumerate(dv_vector) if cost != 0 and cost < 999]
        for neighbor in self.neighbor_index:
            self.dv_matrix[neighbor][self.node_index] = dv_vector[neighbor]
        self.socket = self.initialize_socket()
        self.updated = False
        self.daemon = True 

    def initialize_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', BASE_PORT + self.node_index))
        server_socket.listen(5)
        return server_socket

    def send_neighbor_dv(self):
        dv_message = {
            'from': self.node_index,
            'dv': self.dv_matrix[self.node_index]
        }
        encoded = json.dumps(dv_message).encode()

        for neighbor in self.neighbor_index:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(('localhost', BASE_PORT + neighbor))
                    s.sendall(encoded)
            except Exception as e:
                print(f"Node {self.node_id} failed to send to {neighbor}: {e}")
        
        if self.dv_matrix != self.last_dv_matrix:
            self.updated = True
            self.last_dv_matrix = deepcopy(self.dv_matrix)

    def update_dv(self, received_dv, from_node):
        old_dv = deepcopy(self.dv_matrix[self.node_index])
        
        # store the sender's DV into their row in  matrix
        self.dv_matrix[from_node] = deepcopy(received_dv)
        
        for dest in range(N):
            if dest == self.node_index:
                continue
            
            # Current cost to destination
            current_cost = self.dv_matrix[self.node_index][dest]
            
            # Cost through the neighbor that  sent their DV
            new_cost = self.dv_matrix[self.node_index][from_node] + received_dv[dest]
            
            if new_cost < current_cost:
                self.dv_matrix[self.node_index][dest] = new_cost
        
        # Check if DV has changed
        if self.dv_matrix[self.node_index] != old_dv:
            return True
        return False

    def listen_for_dv(self):
        self.socket.settimeout(1.0)
        while not stop_simulation:
            try:
                client_socket, _ = self.socket.accept()
                data = client_socket.recv(1024)
                if data:
                    message = json.loads(data.decode())
                    from_node = message['from']
                    received_dv = message['dv']
                    print(f"Node {self.node_id} received DV from {node[from_node]}")
                    
                    changed = self.update_dv(received_dv, from_node)
                    
                    if changed:
                        print(f"Updating DV matrix at node {self.node_id}")
                        print(f"New DV matrix at node {self.node_id} = {self.dv_matrix[self.node_index]}")
                    else:
                        print(f"No change in DV at node {self.node_id}")
                
                client_socket.close()
            except socket.timeout:
                continue  # timeout to check stop_simulation
            except Exception as e:
                print(f"Node {self.node_id} error in listen_for_dv: {e}")

    def run(self):
        global shared_turn, stop_simulation, global_round

        # Start listener thread
        listener_thread = Thread(target=self.listen_for_dv)
        listener_thread.daemon = True
        listener_thread.start()

        while not stop_simulation:
            with turn_lock:
                while shared_turn != self.node_index and not stop_simulation:
                    turn_lock.wait()
                
                if stop_simulation:
                    break
                
                if self.node_index == 0:
                    global_round += 1
                    print(f"-------\nRound {global_round}: {self.node_id}")
                else:
                    print(f"-------\nRound {global_round}: {self.node_id}")
                
                print(f"Current DV matrix = {self.dv_matrix[self.node_index]}")
                print(f"Last DV matrix = {self.last_dv_matrix[self.node_index]}")
                
                was_updated = self.updated
                self.updated = False
                
                print(f"Updated from last DV matrix or the same? {'Updated' if was_updated else 'No'}")
                
                # Send DV to neighbors
                for neighbor in self.neighbor_index:
                    print(f"Sending DV to node {node[neighbor]}")
                
                self.send_neighbor_dv()
                
                shared_turn = (shared_turn + 1) % N
                turn_lock.notify_all()
            
            time.sleep(1)
            
            # Check for convergence when all nodes have turn
            if shared_turn == 0:
                with turn_lock:
                    # Check if any node updated its DV
                    all_stable = True
                    for n in nodes:
                        if n.updated:
                            all_stable = False
                            break
                    
                    if all_stable:
                        stop_simulation = True
                        turn_lock.notify_all()
                        print("Stopping simulation. No DV changes detected.")

def run_dvr(filename="network.txt"):
    global graph, N, nodes, shared_turn, stop_simulation, global_round
    
    # Reset globals
    graph = []
    shared_turn = 0
    stop_simulation = False
    global_round = 0
    
    # Read the topology
    with open(filename, "r") as f:
        input_lines = f.readlines()
        for line in input_lines:
            row = list(map(int, line.strip().split()))
            graph.append(row)
    
    N = len(graph)
    
    # Initialize nodes
    nodes = []
    for i in range(N):
        dv_row = []
        for j, cost in enumerate(graph[i]):
            if i == j:
                dv_row.append(0) 
            else:
                if cost == 0:
                    dv_row.append(999)
                else:
                    dv_row.append(cost)
        
        node_instance = Node(node_id=chr(ord('A') + i), node_index=i, dv_vector=dv_row)
        nodes.append(node_instance)
    
    # Start all nodes
    for t in nodes:
        t.start()
    
    # Wait for all nodes to finish
    for t in nodes:
        t.join()
    
    # Print final output
    print("\nFinal output:")
    for i in range(N):
        print(f"Node {node[i]} DV = {nodes[i].dv_matrix[i]}")
    
    print(f"Number of rounds till convergence = {global_round}")
    
    return global_round

def main():
    # Run DVR for Graph 1
    print("Running DVR on Graph 1...")
    rounds_graph1 = run_dvr("network.txt")
    print(f"DVR for Graph1: {rounds_graph1} rounds")
    
    # Run DVR for Graph 2
    print("\nRunning DVR on Graph 2...")
    rounds_graph2 = run_dvr("network2.txt")
    print(f"DVR for Graph2: {rounds_graph2} rounds")
    
    # Write results to OUTPUT.txt
    with open("OUTPUT.txt", "w") as f:
        f.write(f"DVR for Graph1: {rounds_graph1} rounds\n")
        f.write(f"DVR for Graph2: {rounds_graph2} rounds\n")

if __name__ == '__main__':
    main()