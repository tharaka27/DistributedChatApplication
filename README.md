# Distributed Chatting Application

This project is about implementing a distributed client-server chat system consisting of two main distributed components: chat servers and chat clients, which can run on different hosts.

Chat clients can connect to at most one available server where they can be used to send requests to create, join, delete, list and quit chat rooms. They can also communicate with other chat clients that are linked to the same chat room.

Chat servers are programs accepting multiple incoming TCP connections from chat clients. There are multiple servers working together to serve chat clients. Once the system is active, the number of servers is fixed. Each server is responsible only for a subset of the system's chat rooms. In order to join a particular chat room, clients must be connected to the server managing that chat room. As a result, clients are redirected between servers when a client wants to join a chat room managed by a different server. Chat servers are also responsible for broadcasting messages received from clients to all other clients connected to the same chat room.

