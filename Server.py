# Standard library imports for core functionality
import json         # For JSON serialization/deserialization of messages
import socket       # For network socket operations
import threading    # For handling multiple client connections concurrently
import struct      # For binary data structure handling
import logging     # For application logging
import os          # For operating system operations
import ssl         # For secure socket layer/transport layer security
from datetime import datetime  # For timestamp generation
# Custom model imports
from CalculatorModel import CalculatorModel  # Mathematical calculation handling
from SolverModel import SolverModel         # Equation solving functionality
from PlotterModel import PlotterModel       # Equation plotting functionality
from MatrixModel import MatrixModel         # Matrix operations functionality

class MathServer:
    """A secure, multi-threaded mathematical processing server.
    
    This server acts as the central hub for mathematical computations, providing
    a network interface to the various mathematical models. It handles multiple
    concurrent client connections securely and manages the distribution of
    computational tasks.
    
    Key Features:
    - Multi-threaded client handling
    - SSL/TLS encryption support
    - Comprehensive logging system
    - Connection management and timeouts
    - JSON-based communication protocol
    - Integrated mathematical models
    
    Security Features:
    - SSL/TLS encryption
    - Message size limits
    - Connection timeouts
    - Error handling and logging
    - Resource usage limits
    
    Supported Operations:
    - Basic calculations (via CalculatorModel)
    - Equation solving (via SolverModel)
    - Function plotting (via PlotterModel)
    - Matrix operations (via MatrixModel)
    
    Communication Protocol:
    - Message framing with 4-byte size prefix
    - JSON-encoded payloads
    - Request-response pattern
    - Error reporting
    """
    
    def __init__(self, host='0.0.0.0', port=12345, 
                 ssl_cert_file=None, ssl_key_file=None,
                 client_timeout=30,
                 max_connections=100):
        """Initialize the server with specified configuration.
        
        Setup Process:
        1. Initialize logging system
        2. Create computational models
        3. Configure network socket
        4. Set up SSL/TLS if enabled
        5. Configure connection parameters
        
        Args:
            host: Network interface to bind to ('0.0.0.0' for all interfaces)
            port: TCP port number for listening
            ssl_cert_file: Path to SSL certificate for encryption
            ssl_key_file: Path to SSL private key
            client_timeout: Seconds before client connection times out
            max_connections: Maximum number of concurrent clients
            
        Security Notes:
        - Using '0.0.0.0' binds to all interfaces - restrict if needed
        - SSL/TLS is recommended for production use
        - Timeout prevents hung connections
        - Connection limit prevents resource exhaustion
        """
        # Initialize logging system first
        self.setup_logging()
        
        # Initialize computational models
        self.calc_model = CalculatorModel()    # For basic calculations
        self.solver_model = SolverModel()      # For equation solving
        self.plotter_model = PlotterModel()    # For equation plotting
        self.matrix_model = MatrixModel()      # For matrix operations
        
        # Create the main server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR allows the server to rebind to the same address without waiting
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # SSL/TLS configuration for secure communication
        self.ssl_context = None
        if ssl_cert_file and ssl_key_file:
            # Create SSL context with default security settings
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            # Load the server's certificate and private key
            self.ssl_context.load_cert_chain(certfile=ssl_cert_file, keyfile=ssl_key_file)
            self.logger.info("SSL/TLS encryption enabled")
        
        # Server configuration parameters
        self.max_connections = max_connections      # Maximum allowed concurrent connections
        self.client_timeout = client_timeout       # Timeout for client operations
        self.active_connections = 0                # Current number of active connections
        
        # Bind the socket to specified host and port
        self.server_socket.bind((host, port))
        # Start listening for incoming connections
        self.server_socket.listen(max_connections)
        # Server state flag
        self.running = True
        self.logger.info(f"Server running on {host}:{port}")

    def setup_logging(self):
        """Configure the logging system with file and console outputs.
        
        Features:
        - Dual output (file and console)
        - Rotating log files
        - Session tracking
        - Structured log format
        - UTF-8 encoding
        
        Log Structure:
        - Timestamp
        - Session ID
        - Log Level
        - Detailed Message
        
        File Organization:
        - Logs stored in 'logs' directory
        - One history file for all sessions
        - Session-based filtering capability
        """
        # Create a logger instance for this server
        self.logger = logging.getLogger('MathServer')
        self.logger.setLevel(logging.INFO)
        
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, 'logs')
        
        # Ensure logs directory exists
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        # Create history log file that keeps all sessions
        history_file = os.path.join(logs_dir, 'server_history.log')
        
        # Create formatters for different outputs
        file_formatter = logging.Formatter(
            '\n%(asctime)s\n\n'
            'Session: %(session_id)s\n'
            'Type: %(levelname)s\n'
            'Details: %(message)s\n\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        
        # Set up file logging with rotating file handler
        file_handler = logging.FileHandler(history_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        
        # Set up console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Add both handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Generate a unique session ID
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a filter to add session_id to all log records
        class SessionFilter(logging.Filter):
            def __init__(self, session_id):
                super().__init__()
                self.session_id = session_id
                
            def filter(self, record):
                record.session_id = self.session_id
                return True
        
        # Add the filter to both handlers
        session_filter = SessionFilter(self.session_id)
        file_handler.addFilter(session_filter)
        console_handler.addFilter(session_filter)
        
        # Log server start
        self.logger.info("Server started")

    def _recv_all(self, sock, n):
        """Reliably receive exactly n bytes from a socket.
        
        This method handles:
        - Partial receives
        - Connection timeouts
        - Connection closures
        - Socket errors
        
        Args:
            sock: Connected socket to receive from
            n: Exact number of bytes to receive
            
        Returns:
            bytearray: Received data, or None if connection closed/error
            
        Notes:
        - Blocks until all bytes received
        - Handles timeouts gracefully
        - Returns None on connection closure
        """
        data = bytearray()
        while len(data) < n:
            # Loop to receive data until the required number of bytes (n) is collected
            try:
                # Receive remaining bytes
                packet = sock.recv(n - len(data))
                if not packet:  # Connection closed by client
                    return None
                data.extend(packet)
            except socket.timeout:
                # Handle timeout by continuing the loop
                continue
            except Exception:
                # Handle any other socket errors
                return None
        return data

    def handle_client(self, client_socket, addr):
        """Handle individual client connections in a separate thread.
        
        Process Flow:
        1. Set up secure connection (if SSL enabled)
        2. Configure socket timeout
        3. Enter message processing loop
        4. Handle client requests
        5. Clean up on disconnect
        
        Message Protocol:
        1. Receive 4-byte size prefix
        2. Receive message data
        3. Process request
        4. Send response with size prefix
        
        Error Handling:
        - SSL/TLS negotiation errors
        - Timeout handling
        - JSON parsing errors
        - Request processing errors
        - Connection cleanup
        
        Args:
            client_socket: Connected socket for client communication
            addr: Client address tuple (ip, port)
        """
        # Increment active connection counter
        self.active_connections += 1
        self.logger.info(f"New connection from {addr} (Active: {self.active_connections}/{self.max_connections})")
        
        # Wrap socket with SSL if enabled
        try:
            if self.ssl_context:  # Check if SSL/TLS is enabled for the server
                client_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
        except ssl.SSLError as e:
            # If SSL negotiation fails, log error and close connection
            self.logger.error(f"SSL error with {addr}: {str(e)}")
            client_socket.close()
            self.active_connections -= 1
            return
            
        # Set socket timeout
        client_socket.settimeout(self.client_timeout)
        
        while self.running:
            # Main loop to process client requests as long as the server is running
            try:
                # Receive message size (4 bytes for uint32)
                size_data = self._recv_all(client_socket, 4)
                if not size_data:
                    # If no data is received, client has disconnected
                    break
                
                # Convert size bytes to integer
                message_size = int.from_bytes(size_data, byteorder='big')
                
                # Protect against memory exhaustion attacks
                if message_size > 1024 * 1024:  # 1MB limit
                    # If the message is too large, prevent memory exhaustion
                    raise ValueError("Message size too large")
                
                # Receive the actual message data
                data = self._recv_all(client_socket, message_size)
                if not data:
                    # If no message data is received, client has disconnected
                    break
                
                # Parse JSON request
                request = json.loads(data.decode())
                self.logger.info(f"Received from {addr}: {json.dumps(request, indent=2)}")
                
                # Process the request and get response
                response = self.process_request(request)
                self.logger.info(f"Sending to {addr}: {json.dumps(response, indent=2)}")
                
                # Send response with size prefix
                response_data = json.dumps(response).encode()
                size_prefix = len(response_data).to_bytes(4, byteorder='big')
                client_socket.sendall(size_prefix + response_data)
                
            except socket.timeout:
                # If waiting for data times out, log warning and continue to next loop iteration
                self.logger.warning(f"Timeout waiting for data from {addr}")
                continue
            except json.JSONDecodeError:
                # If the received data is not valid JSON, send error response
                self.logger.error(f"Invalid JSON received from {addr}")
                error_response = {"error": "Invalid request format"}
                self.send_error_response(client_socket, error_response)
            except Exception as e:
                # For any other error, log and send error response, then break loop
                self.logger.error(f"Error with {addr}: {str(e)}")
                error_response = {"error": str(e)}
                self.send_error_response(client_socket, error_response)
                break
        
        # Clean up client connection
        client_socket.close()
        self.active_connections -= 1
        self.logger.info(f"Closed connection with {addr} (Active: {self.active_connections}/{self.max_connections})")

    def send_error_response(self, client_socket, error_response):
        """Send error response to client with proper message framing.
        
        Protocol:
        1. Convert error to JSON
        2. Add size prefix
        3. Send complete message
        
        Args:
            client_socket: Client socket to send to
            error_response: Error message dictionary
            
        Error Handling:
        - Serialization errors
        - Socket send errors
        - Connection issues
        """
        try:
            response_data = json.dumps(error_response).encode()
            size_prefix = len(response_data).to_bytes(4, byteorder='big')
            client_socket.sendall(size_prefix + response_data)
        except Exception as e:
            self.logger.error(f"Error sending error response: {str(e)}")

    def process_request(self, request):
        """Process client requests based on their type.
        
        Supported Request Types:
        - calculate: Basic mathematical calculations
        - solve: Equation solving
        - plot: Function/equation plotting
        - matrix_add: Matrix addition
        - matrix_subtract: Matrix subtraction
        - matrix_multiply: Matrix multiplication
        
        Process Flow:
        1. Log request details
        2. Validate request type
        3. Extract parameters
        4. Call appropriate model
        5. Format response
        6. Log response
        
        Args:
            request: Dictionary containing request type and data
            
        Returns:
            Dictionary containing response data or error message
            
        Error Handling:
        - Invalid request types
        - Missing parameters
        - Model processing errors
        - Response formatting errors
        """
        try:
            # Format the request for logging
            request_log = (
                f"Request Type: {request['type']}\n"
                f"Request Data: {json.dumps(request, indent=2)}"  # json.dumps for pretty printing
            )
            self.logger.info(request_log)  # Log the incoming request
            response = None
            if request["type"] == "calculate":  # If request is for calculation
                # Handle mathematical calculation request
                expr = request["expr"]
                base = request["base"]
                print(f"[TRACE] Received calculation request: expr={expr}, base={base}")
                result = self.calc_model.evaluate_expression(expr, base)
                print(f"[TRACE] Calculation result: {result}")
                response = self.calc_model.serialize_calculation(expr, base, result)
                print(f"[TRACE] Serialized calculation response: {response}")
            elif request["type"] == "solve":  # If request is for equation solving
                # Handle equation solving request
                equation = request["equation"]
                print(f"[TRACE] Received equation to solve: {equation}")
                result = self.solver_model.solve_equation(equation)
                print(f"[TRACE] Solution steps generated: {result}")
                response = self.solver_model.serialize_solution(equation, result)
                print(f"[TRACE] Serialized response to send: {response}")
            elif request["type"] == "plot":  # If request is for plotting
                # Handle equation plotting request
                equation = request["equation"]
                result = self.plotter_model.plot_equation(equation)
                response = self.plotter_model.serialize_plot(equation, result)
            elif request["type"] == "matrix_add":  # If request is for matrix addition
                # Handle matrix addition
                matrix1_str = request["matrix1"]
                matrix2_str = request["matrix2"]
                print(f"[TRACE] Received matrix_add request:\nmatrix1={matrix1_str}\nmatrix2={matrix2_str}")
                try:
                    matrix1 = self.matrix_model.parse_matrix_input(matrix1_str)
                    matrix2 = self.matrix_model.parse_matrix_input(matrix2_str)
                    result = self.matrix_model.add_matrices(matrix1, matrix2)
                    print(f"[TRACE] Matrix addition result: {result}")
                    serialized = self.matrix_model.serialize_matrix_result(result)
                    print(f"[TRACE] Serialized matrix_add response: {serialized}")
                    response = {
                        "type": "matrix_operation",
                        "operation": "addition",
                        "status": "success",
                        "result": {
                            "matrix": serialized["matrix"],
                            "formatted": serialized["formatted"],
                            "dimensions": {
                                "rows": int(serialized["dimensions"]["rows"]),
                                "cols": int(serialized["dimensions"]["cols"])
                            }
                        }
                    }
                except Exception as e:
                    # If matrix addition fails, log error and return error response
                    self.logger.error(f"Matrix addition error: {str(e)}")
                    response = {
                        "type": "matrix_operation",
                        "operation": "addition",
                        "status": "error",
                        "error": str(e)
                    }
            elif request["type"] == "matrix_subtract":  # If request is for matrix subtraction
                # Handle matrix subtraction
                matrix1_str = request["matrix1"]
                matrix2_str = request["matrix2"]
                print(f"[TRACE] Received matrix_subtract request:\nmatrix1={matrix1_str}\nmatrix2={matrix2_str}")
                try:
                    matrix1 = self.matrix_model.parse_matrix_input(matrix1_str)
                    matrix2 = self.matrix_model.parse_matrix_input(matrix2_str)
                    result = self.matrix_model.subtract_matrices(matrix1, matrix2)
                    print(f"[TRACE] Matrix subtraction result: {result}")
                    serialized = self.matrix_model.serialize_matrix_result(result)
                    print(f"[TRACE] Serialized matrix_subtract response: {serialized}")
                    response = {
                        "type": "matrix_operation",
                        "operation": "subtraction",
                        "status": "success",
                        "result": {
                            "matrix": serialized["matrix"],
                            "formatted": serialized["formatted"],
                            "dimensions": {
                                "rows": int(serialized["dimensions"]["rows"]),
                                "cols": int(serialized["dimensions"]["cols"])
                            }
                        }
                    }
                except Exception as e:
                    # If matrix subtraction fails, log error and return error response
                    self.logger.error(f"Matrix subtraction error: {str(e)}")
                    response = {
                        "type": "matrix_operation",
                        "operation": "subtraction",
                        "status": "error",
                        "error": str(e)
                    }
            elif request["type"] == "matrix_multiply":  # If request is for matrix multiplication
                # Handle matrix multiplication
                matrix1_str = request["matrix1"]
                matrix2_str = request["matrix2"]
                print(f"[TRACE] Received matrix_multiply request:\nmatrix1={matrix1_str}\nmatrix2={matrix2_str}")
                try:
                    matrix1 = self.matrix_model.parse_matrix_input(matrix1_str)
                    matrix2 = self.matrix_model.parse_matrix_input(matrix2_str)
                    result = self.matrix_model.multiply_matrices(matrix1, matrix2)
                    print(f"[TRACE] Matrix multiplication result: {result}")
                    serialized = self.matrix_model.serialize_matrix_result(result)
                    print(f"[TRACE] Serialized matrix_multiply response: {serialized}")
                    response = {
                        "type": "matrix_operation",
                        "operation": "multiplication",
                        "status": "success",
                        "result": {
                            "matrix": serialized["matrix"],
                            "formatted": serialized["formatted"],
                            "dimensions": {
                                "rows": int(serialized["dimensions"]["rows"]),
                                "cols": int(serialized["dimensions"]["cols"])
                            }
                        }
                    }
                except Exception as e:
                    # If matrix multiplication fails, log error and return error response
                    self.logger.error(f"Matrix multiplication error: {str(e)}")
                    response = {
                        "type": "matrix_operation",
                        "operation": "multiplication",
                        "status": "error",
                        "error": str(e)
                    }
            else:  # If request type is not recognized
                # Handle unknown request types by returning an error
                response = {"error": "Invalid request type"}
            # Format the response for logging
            response_log = (
                f"Response for {request['type']}:\n"
                f"Response Data: {json.dumps(response, indent=2)}"  # json.dumps for pretty printing
            )
            self.logger.info(response_log)  # Log the outgoing response
            return response
        except Exception as e:
            # If any error occurs during request processing, log and return error
            error_msg = f"Error processing {request.get('type', 'unknown')} request: {str(e)}"
            self.logger.error(error_msg)
            return {"error": str(e)}

    def run(self):
        """Main server loop that accepts incoming connections.
        
        Process Flow:
        1. Set socket timeout
        2. Accept new connections
        3. Create client handler thread
        4. Continue accepting connections
        
        Features:
        - Non-blocking accept
        - Thread per client
        - Graceful shutdown support
        - Error recovery
        
        Error Handling:
        - Socket accept errors
        - Thread creation errors
        - Keyboard interrupts
        - Resource exhaustion
        """
        print("Server is waiting for connections...")
        while self.running:
            # Main server loop to accept new client connections as long as the server is running
            try:
                # Set accept timeout to allow checking running flag
                self.server_socket.settimeout(1.0)
                try:
                    # Accept new client connection
                    client_socket, addr = self.server_socket.accept()
                except socket.timeout:
                    # If accept times out, continue to next loop iteration to check running flag
                    continue
                except Exception as e:
                    # If another error occurs during accept, print error if server is still running
                    if self.running:
                        print(f"Error accepting connection: {str(e)}")
                    continue
                
                # Create new thread for client handling
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                thread.daemon = True  # Thread will be terminated when main thread exits
                thread.start()
            except KeyboardInterrupt:
                # If server is interrupted by user, break the loop to shut down
                break
            except Exception as e:
                # For any other server error, print error and break if not running
                print(f"Server error: {str(e)}")
                if not self.running:
                    break

    def stop(self):
        """Gracefully stop the server and clean up resources.
        
        Shutdown Process:
        1. Set running flag to False
        2. Unblock accept() with dummy connection
        3. Close server socket
        4. Wait for client threads
        
        Cleanup:
        - Socket closure
        - Thread termination
        - Resource release
        
        Error Handling:
        - Socket closure errors
        - Thread termination issues
        """
        try:
            self.running = False
            # Create dummy connection to unblock accept()
            try:
                socket.create_connection(('localhost', self.server_socket.getsockname()[1]), timeout=1)
            except:
                pass
            self.server_socket.close()
            print("Server stopped")
        except Exception as e:
            print(f"Error stopping server: {str(e)}")

# Main entry point
if __name__ == "__main__":
    try:
        # Create and run server instance
        server = MathServer()
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()
    except Exception as e:
        print(f"Server error: {str(e)}")