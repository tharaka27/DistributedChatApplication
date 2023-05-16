# Distributed Chat Client

Here We have provided a executable Java file of the distributed client. You can use this executable file as the chat client for our implemented distributed chat server.

You can execute the file by using the below command,

```java -jar client.jar -h server_address [-p server_port] -i identity [-d]```

*  server_address: corresponds to the ip address or hostname of the server to
   which the client is connecting to.
* server_port: corresponds to the port in which the server is listening for
  incoming client connections (default port is 4444).
* identity: corresponds to the client's identity (i.e. username) which must be unique in the entire system. If the identity already exists, the server will send a message to the client indicating the error and will then close the connection. If the identity doesn't exist, a connection is established and the server places the client on its MainHall chat room. More details on this are given later.
* The -d option can be used to start the client in debug mode. This means that all the received and sent messages will be printed on the standard output.

The client user interface is command-line based and reads input from the standard input. Each line of input is terminated by a new line and is interpreted by the client as either a command or a message. If the line of input starts with a hash character "#" then it is interpreted as a command, otherwise it is interpreted as a message that should be broadcasted by the chat server to other clients in the same chat room. The list of commands supported by chat clients is as follows:
* #list - List of chat rooms in the system
* #who - List of clients in the current chat room
* #createroom roomid - A connected client can create a chat room by using this command
* #joinroom roomid - A client can join other rooms if he/she is not the owner of the current chat room
* #deleteroom roomid - If the client is the owner of the chat room, he/she can delete the room
* #quit - The client can send a quit message at any time

Pressing Ctrl-C terminate chat clients and works similar to #quit.

