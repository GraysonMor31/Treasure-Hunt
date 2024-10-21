# GameClient 

## Message class
### handles processing and creation message sent from Client
* _set_selector_event_mask() - set selector to listen for events: reading, writing, both reading and writing
* _read() - reads the data from the socket 
* _write() - writes data from the send buffer to the socket
* _json_encode() - an object is being encodes to a JSON format
* _json_decode() -  JSON bytes being decodes into python object
* _create_message() - header and content are including to a comlete message
* _process_response_binary_content() - binary response content 
* process_events() - read and wirte events are being process based on the mask 
* read() - read data is being handles from the socket
* write() - writing data is being handles to the socket
* close() - close the connection to the server 
* queue_request() - request a queues to be sent to the server
* process_protoheader() - the protocal header is being processes from the received data
* process - jsonheader() - JSON header is being processes from the received data 
* process_response() - response is being process from the server 