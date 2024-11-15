import logging

# Set up logging for debugging, info, warnings, errors, and critical messages
def setup_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

# Utility function to get a formatted timestamp for log entries
def get_timestamp():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Utility to safely close socket connections
def close_socket(sock, logger):
    try:
        sock.close()
        logger.info("Socket closed successfully.")
    except Exception as e:
        logger.error(f"Error closing socket: {e}")

# Function to validate that the incoming data is a dictionary (used for safety checks)
def is_valid_dict(data, logger):
    if isinstance(data, dict):
        return True
    logger.warning(f"Invalid data format received: {data}")
    return False

# Utility function to log connection attempts (successful or not)
def log_connection_attempt(client_ip, success, logger):
    timestamp = get_timestamp()
    if success:
        logger.info(f"{timestamp} - Successfully connected from {client_ip}")
    else:
        logger.error(f"{timestamp} - Failed connection attempt from {client_ip}")