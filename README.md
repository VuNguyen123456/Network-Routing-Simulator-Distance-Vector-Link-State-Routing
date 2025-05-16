# Network-Routing-Simulator-Distance-Vector-Link-State-Routing
Simulate the Distance Vector Routing (DVR) protocol and implement the Link State Routing (LSR) protocol in a distributed, multithreaded environment. Each node in the network will run as an independent thread, only aware of its direct neighbors. Nodes exchange routing information using TCP sockets and update their distance vectors based on the Bellman-Ford algorithm.

The DVR implementation must support distributed, concurrent, and asynchronous operation—each node sends its distance vector in a predefined order during each round and updates its routing table if changes are detected. Also implement logic to detect convergence across the network and output debug logs and final DV tables per node.

Following the DVR implementation, implement the LSR algorithm using Dijkstra’s algorithm. Each node will construct and flood Link State Advertisements (LSAs) to learn the complete network topology. Nodes will build a Link State Database (LSDB) and compute the shortest paths to all other nodes. LSR must also support asynchronous communication, run on separate threads per node, and detect convergence.

Finally, DVR and LSR will be compared by reporting the number of rounds needed for each algorithm to converge on the same network topologies. The implementation must handle file I/O, socket communication, and multithreading, and produce clear debug output along with final routing tables and round counts for both DVR and LSR.


