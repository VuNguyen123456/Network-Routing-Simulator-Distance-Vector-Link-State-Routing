# Network-Routing-Simulator-Distance-Vector-Link-State-Routing
Simulate the Distance Vector Routing (DVR) protocol and implement the Link State Routing (LSR) protocol in a distributed, multithreaded environment. Each node in the network will run as an independent thread, only aware of its direct neighbors. Nodes exchange routing information using TCP sockets and update their distance vectors based on the Bellman-Ford algorithm.

The DVR implementation must support distributed, concurrent, and asynchronous operation—each node sends its distance vector in a predefined order during each round and updates its routing table if changes are detected. Also implement logic to detect convergence across the network and output debug logs and final DV tables per node.

Following the DVR implementation, implement the LSR algorithm using Dijkstra’s algorithm. Each node will construct and flood Link State Advertisements (LSAs) to learn the complete network topology. Nodes will build a Link State Database (LSDB) and compute the shortest paths to all other nodes. LSR must also support asynchronous communication, run on separate threads per node, and detect convergence.

Finally, DVR and LSR will be compared by reporting the number of rounds needed for each algorithm to converge on the same network topologies. The implementation must handle file I/O, socket communication, and multithreading, and produce clear debug output along with final routing tables and round counts for both DVR and LSR.

How to run:
1. To run Distance Vector Routing:
   python DVR.py

2. To run Link State Routing:
   python LSRNode.py

Both programs will:
- Read network topology from network.txt and network2.txt
- Create threads for each node in the network
- Exchange routing information until convergence
- Output the final routing tables
- Record the number of rounds until convergence in OUTPUT.txt

Requirements:
- Python 3.6 or higher

Notes:
- Make sure all files are in the same directory
- The program will automatically run on both network topologies
- The OUTPUT.txt file will show a comparison of convergence times
