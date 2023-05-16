# DistributedChatClient

## Requirements 
The module depends on following external libraries. For correct configuration please install the requirements.txt
* Flask==2.0.3
* parse==1.19.0
* pyzmq==22.3.0


## To execute the server

When executing the server it will read the configuration.txt file in the project directory which contains configurations about the distributed servers. So before the execution of the server change the server configurations acoordingly (We have configured 6 chat servers).

Configuration file data format is,
* serverID ServerIP ClientPort  CoordinationPort ID

  - ServerID - Identity name of the server.

  - ServerIP - IP of the server

  - ClientPort - Port which clients connect to the server

  - CoordinationPort - Port used by servers to communicate between them

  - ID - Priority number when electing leaders

* When you have configured the configuration file, you can execute the below command.

```python3 app.py```


### Distributed chat server application
In this project, we had to implement a distributed chat client application. Overall systems consist mainly of two parts as server and the client. The scope of the project was to implement the server component of the system. The server is a distributed system where chat clients can connect to an existing server. An individual server is responsible for managing a subset of chat clients. Because clients are connected to a single server, if a client wants to join a chat room located in another server, redirecting of chat clients between the servers is required. And also having unique client and chat room identities across the whole system is also important. 

According to CAP theory, a distributed system can only have two factors out of partition tolerance, consistency, and availability. In our implementation, we focused on building a partition tolerant and consistent distributed system. 

In the chat application, there are two essential requirements,
* Have unique client identities when a new chat client is joined
* Have unique room identities when creating a new room
To achieve these two requirements, either server individually has to check with other servers whether these requirements are met or the system can have a separate coordinator server that performs the coordination between servers in addition to responding to the chat clients connected to the server. In our implementation, we used a separate server as the coordinator for the system. The coordinator server maintains up-to-date information about the existing clients and the rooms.

To elect a coordinator for the system Fast Bully Algorithm (FBA) was used[1]. FBA uses priorities of the servers to elect a coordinator at the beginning, if a coordinator fails for some reason, the server that first detects the failure calls an election and appoints a new coordinator. There are both positive and negative impacts of having a coordinator server in the system.


## References
[1] Seok-Hyoung Lee and Hoon Choi. “The Fast Bully Algorithm: For Electing a Coordinator Process in Distributed Systems”. In: Revised Papers from the International Conference on Information Networking, Wireless Communications Technologies and Network Applications-Part II. ICOIN ’02.

[2]	Gupta R., Maali A.C., and Singh Y.N.. "Adaptive Push-Then-Pull Gossip Algorithm for Scale-free Networks." arXiv preprint arXiv:1310.5985 (2013).
