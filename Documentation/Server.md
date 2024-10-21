# Server

## No Classes
* AcceptWrapper() - Accept a connection from a client and ensure it is a non-blocking socket
* GetHost() - Gets the host (either IP or hostname) from standard input (CLI) if one is not valid or not provided a defualt (localhost) will be assigned to that the server can be set up regardless of human error
* GetPort() - Gets the port from standard input (CLI) if one is not valid or not provided a defualt will be assigned so that the server can be setup properly regardless of human error
* Main() - Binds the socket using host and port numbers, sets to be a non-blocking socket and handles keeping the TCP connection open and stable by listening to any incoming connections