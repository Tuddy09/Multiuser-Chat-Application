A chat application using Python sockets. Features multi-user communication, dynamic client management, end-to-end communication between clients through UDP.
The server listens for incoming clients using TCP and keeps a list of all the connections, when a new client arrives the server sents the list with all the connected clients to the incoming one and increments the list of the already connected clients.
The communication between clients is done through UDP and the server acts as an control center that signals the connection/disconnection of the clients.

Technologies Used:<br>
Python: The primary programming language used for development.<br>
Socket Programming: Leveraged Python's socket library for network communication.<br>
Threading: Utilized threading to handle multiple client connections concurrently.<br>
