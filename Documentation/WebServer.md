# Web_Server 

# Overview
 This script creates a simple HTTP server that handles both 
 "GET" and "POST" requests. The code use the built-in http.server module
 along with socketserver to set up the server. The logging module to provide detailed logs of the
 server's activity. 

# Logging Setup 
Beginning the code it use logging.basicConfig. Which defines the log level, logger instance, and
log format.

# do_GET()
this method check to see if the path is "/" to serve the index.html file. 

# do_POST()
this method received "POST" request and the data and log it.


