# GameServer

## Protocol Class
#### Handles the defined JSON custom protocol
* EncodeMessage() - Encodes data into a JSON format for transport to be sent back to the client
* DecodeMessage() - Decodes from JSON format to be able to be used an processed by the server after its been sent from the server
* DecodeHeader() - Decodes the header to be processed by ProtoHeader and other functions where protocol information may be necessary
---

## Message Class
#### Handles processing and, creating of messages sent from the Client
* Init() - Initializes 
* SetSelectorEventsMask() - Sets the selector to either be a read or write to or from the socket these flags are used in later functions when processing data or creating a response
* Read() - Reads the request data from the socket to a buffer of 12KB before being processed (12KB because later images and HTML pages are going to be sent)
* Write() - Writes the response data to a buffer before being sent to the client socket
* ProcessEvents() - Calls appropriate functions based on wether the w or r is set from the SetSelectorEventMask() function, to be able to read or write to or from the socket.
* ProcessProtoHeader() - Reads and processes protocol header data 
* ProcessJSONHeader() -
* ProcessRequest() - Takes the read request and 
* CreateResponse() - Determines the action sent from the client, creates a message based on the reult of the action and writes it to the buffer
* Close() - Closes the connection between the server and client by unregistering the bound socket after some information has been passed between both entities
 ----

## GameState Class
#### Stores the state of the game on the server
* Init() - Defines an empty array for each game for the players and their stats to be stored in as long as the server is up
* AddPlayer() - Appends a player to the array (will be able to check duplicates in the future)
* GetState() - Called to return what is currently in the Array (will eventually return much more information)