# GameServer

## Protocol Class
#### Handles the defined JSON custom protocol
* EncodeMessage() - 
* DecodeMessage() - 
* DecodeHeader() -
---

## Message Class
#### Handles processing and, creating of messages sent from the Client
* Init() - 
* SetSelectorEventsMask() -
* Read() - 
* Write() -
* ProcessEvents() -
* ProcessProtoHeader() - 
* ProcessJSONHeader() -
* ProcessRequest() - 
* CreateResponse() - Determines the action sent from the client, creates a message based on the reult of the action and writes it to the buffer
* Close() - Closes the connection between the server and client by unregistering the bound socket after some information has been passed between both entities
 ----

## GameState Class
#### Stores the state of the game on the server
* Init() - Defines an array to hold players and their stats, this is what the game consists of currently
* AddPlayer() - Appends a player to the array (will be able to check duplicates in the future)
* GetState() - Called to return what is currently in the Array (will eventually return much more information)