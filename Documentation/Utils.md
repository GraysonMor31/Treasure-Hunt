# Utils Module Documentation

## Overview
This module provides utility functions for logging, timestamp generation, socket management, data validation, and logging connection attempts.

## Functions

### `setup_logging()`
Sets up logging for debugging, info, warnings, errors, and critical messages.

- **Returns**: 
  - `Logger`: A logger instance.

### `get_timestamp()`
Gets a formatted timestamp for log entries.

- **Returns**: 
  - `str`: The current timestamp in the format "YYYY-MM-DD HH:MM:SS".

### `close_socket(sock, logger)`
Safely closes socket connections.

- **Parameters**: 
  - `sock` (socket): The socket to close.
  - `logger` (Logger): The logger instance to log messages.

### `is_valid_dict(data, logger)`
Validates that the incoming data is a dictionary.

- **Parameters**: 
  - `data` (any): The data to validate.
  - `logger` (Logger): The logger instance to log messages.
- **Returns**: 
  - `bool`: `True` if the data is a dictionary, `False` otherwise.

### `log_connection_attempt(client_ip, success, logger)`
Logs connection attempts, whether successful or not.

- **Parameters**: 
  - `client_ip` (str): The IP address of the client.
  - `success` (bool): Indicates if the connection attempt was successful.
  - `logger` (Logger): The logger instance to log messages.