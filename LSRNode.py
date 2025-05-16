import threading
import time
import heapq
import copy

# Shared variables
shared_turn = 0
stop_simulation = False
turn_lock = threading.Condition()
N = 0  # Total number of nodes
node_ids = []
global_round = 0

class LSRNode(threading.Thread):
    def __init__(self, node_index, node_id, neighbors):
        super().__init__()
        self.node_index = node_index
        self.node_id = node_id
        self.neighbors = neighbors  
        self.lsdb = {} 
        # Initialize LSDB 
        self.lsdb[self.node_id] = self.neighbors.copy()
        self.routing_table = {} 
        self.received_lsas = set()
        self.seq_no = 0
        self.updated = False

    def generate_lsa(self):
        lsa = {
            "source": self.node_id,
            "neighbors": self.neighbors.copy(),
            "seq": self.seq_no
        }
        self.seq_no += 1
        return lsa

    def flood_lsa(self, lsa, sender=None):
        for neighbor in nodes:
            if neighbor.node_id != self.node_id and neighbor.node_id != sender:
                neighbor.receive_lsa(copy.deepcopy(lsa), self.node_id)

    def receive_lsa(self, lsa, sender):
        lsa_key = (lsa["source"], lsa["seq"])
        if lsa_key not in self.received_lsas:
            self.received_lsas.add(lsa_key)
            self.lsdb[lsa["source"]] = lsa["neighbors"]
            self.run_dijkstra()
            self.updated = True
            self.flood_lsa(lsa, sender)

    def run_dijkstra(self):
        graph = self.build_graph()
        old_routing_table = self.routing_table.copy()
        self.routing_table = {}
        heap = [(0, self.node_id, self.node_id)] 

        visited = {}
        while heap:
            cost, current, first_hop = heapq.heappop(heap)
            if current in visited:
                continue
            visited[current] = (first_hop, cost)

            for neighbor, weight in graph.get(current, {}).items():
                if neighbor not in visited:
                    # first hop use neighbor
                    next_hop = neighbor if current == self.node_id else first_hop
                    heapq.heappush(heap, (cost + weight, neighbor, next_hop))

        for dest, (next_hop, cost) in visited.items():
            if dest != self.node_id: 
                self.routing_table[dest] = (next_hop, cost)
        
        # Check if routing table changed
        if old_routing_table != self.routing_table:
            self.updated = True

    def build_graph(self):
        graph = {}
        for src, neighbors in self.lsdb.items():
            graph[src] = neighbors
        return graph

    def run(self):
        global shared_turn, stop_simulation, global_round

        first_broadcast_done = False

        while not stop_simulation:
            with turn_lock:
                while shared_turn != self.node_index and not stop_simulation:
                    turn_lock.wait()
                if stop_simulation:
                    break

                if self.node_index == 0:
                    global_round += 1
                    print(f"-------\nRound {global_round}")

                print(f"Node {self.node_id} Routing Table: {self.routing_table}")

                was_updated = self.updated
                self.updated = False

                if not first_broadcast_done:
                    lsa = self.generate_lsa()
                    self.receive_lsa(copy.deepcopy(lsa), None)
                    self.flood_lsa(lsa)
                    first_broadcast_done = True
                    was_updated = True

                print(f"Updated from last routing table? {'Updated' if was_updated else 'No'}")

                shared_turn = (shared_turn + 1) % N
                turn_lock.notify_all()

            time.sleep(0.1)

            # Check for convergence
            if shared_turn == 0:
                with turn_lock:
                    if not any(node.updated for node in nodes):
                        stop_simulation = True
                        turn_lock.notify_all()
                        print("Stopping simulation. No LSA changes detected.")

        print(f"\nFinal routing table for Node {self.node_id}: {self.routing_table}")



nodes = []

# Read the network file
def setup_network_from_file(filename="network.txt"):
    global N, node_ids, nodes, shared_turn, stop_simulation, global_round
    
    shared_turn = 0
    stop_simulation = False
    global_round = 0
    nodes = []
    
    # Read the network from the file
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Build matrix
    adj_matrix = []
    for line in lines:
        parts = line.strip().split()
        row = list(map(int, parts))
        adj_matrix.append(row)


    node_labels = [chr(ord('A') + i) for i in range(len(adj_matrix))]
    topology = {}
    for i in range(len(adj_matrix)):
        neighbors = {}
        for j in range(len(adj_matrix)):
            if adj_matrix[i][j] != 0:
                neighbors[node_labels[j]] = adj_matrix[i][j]
        topology[node_labels[i]] = neighbors

    N = len(topology)
    node_ids = list(topology.keys())

    for idx, node_id in enumerate(node_ids):
        node = LSRNode(idx, node_id, topology[node_id])
        nodes.append(node)

    for node in nodes:
        node.start()

    for node in nodes:
        node.join()

    return global_round

# Main run
if __name__ == "__main__":
    # Run with the first network
    print("Running LSR on Graph 1...")
    rounds_graph1 = setup_network_from_file("network.txt")
    print(f"LSR for Graph1: {rounds_graph1} rounds")
    
    # Run with the second network
    print("\nRunning LSR on Graph 2...")
    rounds_graph2 = setup_network_from_file("network2.txt")
    print(f"LSR for Graph2: {rounds_graph2} rounds")

    # Output to file
    with open("OUTPUT.txt", "a") as f:
        f.write(f"LSR for Graph1: {rounds_graph1} rounds\n")
        f.write(f"LSR for Graph2: {rounds_graph2} rounds\n")