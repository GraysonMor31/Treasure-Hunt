# Client

## Overview 
    This is a non-blocking TCP connection to a server, which sends a request based on user-provided action and value. The goal is to able to interact with a server, where the client can send actions such as "add_player" or "get_state" and handle the responses. 

## Methods
* def create_request() - create a request dictionary based on the specified action. Returns: dictionary type, encoding, and content. 
* start_connection() - establishing a connection to a game server and registers the socket. 
* main() - handling command-line arguments, establising a connection, and event loop whichs wait for events on the registerd sockets. 
