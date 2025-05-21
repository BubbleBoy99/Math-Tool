import json  # For JSON serialization/deserialization
import socket  # For network communication
import time  # For retry delays
from CalculatorModel import CalculatorModel
from SolverModel import SolverModel

class MathClient:
    """A robust client for interacting with the mathematical processing server.
    
    This client provides a reliable interface to the mathematical server, handling
    network communication, request formatting, and response processing. It includes
    retry logic, timeout handling, and robust error management.
    
    Key Features:
    - Automatic connection management
    - Retry logic for failed connections
    - Timeout handling for operations
    - JSON-based communication
    - Comprehensive error handling
    - Local model integration for response processing
    
    Supported Operations:
    - Mathematical calculations
    - Equation solving
    - Function plotting
    - Matrix operations (addition, subtraction, multiplication)
    
    Communication Protocol:
    - Message framing with 4-byte size prefix
    - JSON-encoded payloads
    - Request-response pattern
    - Error reporting
    
    Integration:
    - Uses CalculatorModel for calculation response processing
    - Uses SolverModel for equation solving response processing
    """
    
    def __init__(self, host='localhost', port=12345):
        """Initialize the client with connection parameters and models.
        
        Configuration:
        1. Network parameters (host, port)
        2. Timeout settings
        3. Retry configuration
        4. Local models for response processing
        
        Args:
            host: Server hostname or IP address
            port: Server port number
            
        Attributes:
            connection_timeout: Time limit for initial connection
            response_timeout: Time limit for server responses
            max_retries: Maximum connection attempts
            retry_delay: Seconds between retry attempts
        """
        self.calc_model = CalculatorModel()
        self.solver_model = SolverModel()
        self.client_socket = None
        self.host = host
        self.port = port
        self.connection_timeout = 5  # Connection timeout in seconds
        self.response_timeout = 10   # Response timeout in seconds
        self.max_retries = 3        # Maximum number of connection retries
        self.retry_delay = 2        # Delay between retries in seconds

    def connect(self):
        """Connect to the server with retry logic.
        
        Connection Process:
        1. Create new socket
        2. Set connection timeout
        3. Attempt connection
        4. Set response timeout
        5. Retry on failure
        
        Retry Logic:
        - Attempts up to max_retries times
        - Waits retry_delay seconds between attempts
        - Cleans up failed connections
        
        Raises:
            ConnectionError: If all connection attempts fail
        """
        retries = 0
        last_exception = None
        while retries < self.max_retries:  # Retry connection up to max_retries
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket
                self.client_socket.settimeout(self.connection_timeout)  # Set connection timeout
                self.client_socket.connect((self.host, self.port))  # Connect to server
                self.client_socket.settimeout(self.response_timeout)  # Set response timeout
                print(f"Connected to server at {self.host}:{self.port}")
                return
            except socket.timeout:
                last_exception = "Connection timed out"
            except ConnectionRefusedError:
                last_exception = "Server is not available"
            except Exception as e:
                last_exception = str(e)
            retries += 1
            if retries < self.max_retries:  # If we have retries left
                print(f"Connection attempt {retries} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)  # Wait before retrying
            self.close()
        raise ConnectionError(f"Failed to connect after {self.max_retries} attempts. Last error: {last_exception}")

    def send_request(self, request):
        """Send a request to the server and get the response with timeout handling.
        
        Communication Protocol:
        1. Connect if not connected
        2. Add message size prefix
        3. Send request
        4. Receive response size
        5. Receive response data
        
        Error Handling:
        - Connection failures
        - Timeout conditions
        - Invalid responses
        - Server disconnections
        
        Args:
            request: Dictionary containing the request data
            
        Returns:
            Dictionary containing the server's response
            
        Raises:
            ConnectionError: If connection fails
            TimeoutError: If server response times out
        """
        if not self.client_socket:  # If not connected
            self.connect()
        try:
            request_data = json.dumps(request).encode()  # Serialize request to JSON bytes
            size_prefix = len(request_data).to_bytes(4, byteorder='big')  # 4-byte length prefix
            print(f"Sending request: {json.dumps(request)}")
            self.client_socket.sendall(size_prefix + request_data)  # Send size + data
            size_data = self._recv_all(4)  # Receive 4-byte response size
            if not size_data:  # If connection closed
                raise ConnectionError("Connection closed by server")
            response_size = int.from_bytes(size_data, byteorder='big')  # Convert bytes to int
            response_data = self._recv_all(response_size)  # Receive response data
            if not response_data:  # If connection closed
                raise ConnectionError("Connection closed by server")
            response = json.loads(response_data.decode())  # Deserialize JSON response
            print(f"Received response: {json.dumps(response)}")
            return response
        except socket.timeout:
            print("Request timed out")
            self.close()
            raise TimeoutError("Server response timed out")
        except Exception as e:
            print(f"Communication error: {str(e)}")
            self.close()
            raise

    def _recv_all(self, n):
        """Helper method to receive exactly n bytes from the socket.
        
        Features:
        - Handles partial receives
        - Detects connection closure
        - Respects timeout settings
        
        Args:
            n: Number of bytes to receive
            
        Returns:
            bytearray containing exactly n bytes, or None if connection closed
            
        Raises:
            socket.timeout: If receive operation times out
        """
        data = bytearray()
        while len(data) < n:  # Loop until all n bytes are received
            try:
                packet = self.client_socket.recv(n - len(data))  # Receive up to n bytes
                if not packet:  # If connection closed
                    return None
                data.extend(packet)
            except socket.timeout:
                raise
        return data

    def send_calculation(self, expr, base):
        """Send a calculation request to the server.
        
        Process:
        1. Format calculation request
        2. Send to server
        3. Process response
        4. Handle errors
        
        Args:
            expr: Mathematical expression to evaluate
            base: Number base for calculation (BIN, OCT, DEC, HEX)
            
        Returns:
            String containing result or error message
            
        Error Handling:
        - Server errors
        - Connection issues
        - Timeout conditions
        - Invalid responses
        """
        try:
            request = {"type": "calculate", "expr": expr, "base": base}
            response = self.send_request(request)
            if "error" in response:  # If server returned error
                return f"Error: {response['error']}"
            expr, base, result = self.calc_model.deserialize_calculation(response)
            return f"{base}: {result}"
        except TimeoutError:
            return "Error: Server response timed out"
        except ConnectionError as e:
            return f"Error: Connection failed - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def send_solve(self, equation):
        """Send an equation solving request to the server.
        
        Process:
        1. Format solve request
        2. Send to server
        3. Process solution steps
        4. Handle errors
        
        Args:
            equation: Equation to solve
            
        Returns:
            List of solution steps or error message
            
        Error Handling:
        - Server errors
        - Connection issues
        - Timeout conditions
        - Invalid responses
        """
        try:
            request = {"type": "solve", "equation": equation}
            response = self.send_request(request)
            if "error" in response:  # If server returned error
                return f"Error: {response['error']}"
            print(f"Debug - Response type: {type(response)}")
            print(f"Debug - Response content: {json.dumps(response, indent=2)}")
            print(f"Debug - Steps type: {type(response.get('steps'))}")
            equation, steps = self.solver_model.deserialize_solution(response)
            return steps
        except TimeoutError:
            return "Error: Server response timed out"
        except ConnectionError as e:
            return f"Error: Connection failed - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def send_plot(self, equation):
        """Send a plotting request to the server.
        
        Process:
        1. Format plot request
        2. Send to server
        3. Process plot result
        4. Handle errors
        
        Args:
            equation: Equation or function to plot
            
        Returns:
            Status message or error message
            
        Error Handling:
        - Server errors
        - Connection issues
        - Timeout conditions
        - Invalid responses
        """
        try:
            request = {"type": "plot", "equation": equation}
            response = self.send_request(request)
            if "error" in response:  # If server returned error
                return f"Error: {response['error']}"
            equation, message = self.solver_model.deserialize_plot(response)
            return message
        except TimeoutError:
            return "Error: Server response timed out"
        except ConnectionError as e:
            return f"Error: Connection failed - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def _prepare_matrix_for_json(self, matrix):
        """Convert matrix elements to JSON-serializable types.
        
        Conversion Rules:
        - Numbers → float
        - NumPy types → float
        - Other types → string representation
        - Preserves matrix structure
        
        Args:
            matrix: Input matrix (list of lists or string)
            
        Returns:
            Matrix with JSON-serializable elements
            
        Note:
            Handles both string format and list format matrices
        """
        if isinstance(matrix, str):  # If already a string
            return matrix
        if not matrix:  # If matrix is empty
            return matrix
        result = []
        for row in matrix:  # Loop over matrix rows
            new_row = []
            for element in row:  # Loop over elements in row
                try:
                    if hasattr(element, 'item'):  # numpy type
                        new_row.append(float(element.item()))
                    else:
                        new_row.append(float(element))
                except (TypeError, ValueError):
                    new_row.append(str(element))
            result.append(new_row)
        return result

    def send_matrix_add(self, matrix1, matrix2):
        """Send a matrix addition request to the server.
        
        Process:
        1. Convert matrices to JSON format
        2. Send request to server
        3. Process response
        4. Handle errors
        
        Args:
            matrix1: First matrix operand
            matrix2: Second matrix operand
            
        Returns:
            Dictionary containing result matrix and metadata, or None on error
            
        Error Handling:
        - Matrix format errors
        - Server errors
        - Connection issues
        """
        try:
            json_matrix1 = self._prepare_matrix_for_json(matrix1)
            json_matrix2 = self._prepare_matrix_for_json(matrix2)
            request = {
                "type": "matrix_add",
                "matrix1": json_matrix1,
                "matrix2": json_matrix2
            }
            print(f"Debug - Sending matrices: {json.dumps(request)}")  # Debug print
            response = self.send_request(request)
            if "error" in response:  # If server returned error
                return None
            return response["result"]
        except Exception as e:
            print(f"Error in matrix addition: {str(e)}")
            return None

    def send_matrix_subtract(self, matrix1, matrix2):
        """Send a matrix subtraction request to the server.
        
        Process:
        1. Convert matrices to JSON format
        2. Send request to server
        3. Process response
        4. Handle errors
        
        Args:
            matrix1: Matrix to subtract from
            matrix2: Matrix to subtract
            
        Returns:
            Dictionary containing result matrix and metadata, or None on error
            
        Error Handling:
        - Matrix format errors
        - Server errors
        - Connection issues
        """
        try:
            json_matrix1 = self._prepare_matrix_for_json(matrix1)
            json_matrix2 = self._prepare_matrix_for_json(matrix2)
            request = {
                "type": "matrix_subtract",
                "matrix1": json_matrix1,
                "matrix2": json_matrix2
            }
            print(f"Debug - Sending matrices: {json.dumps(request)}")  # Debug print
            response = self.send_request(request)
            if "error" in response:  # If server returned error
                return None
            return response["result"]
        except Exception as e:
            print(f"Error in matrix subtraction: {str(e)}")
            return None

    def send_matrix_multiply(self, matrix1, matrix2):
        """Send a matrix multiplication request to the server.
        
        Process:
        1. Convert matrices to JSON format
        2. Send request to server
        3. Process response
        4. Handle errors
        
        Args:
            matrix1: First matrix operand
            matrix2: Second matrix operand
            
        Returns:
            Dictionary containing result matrix and metadata, or None on error
            
        Error Handling:
        - Matrix format errors
        - Server errors
        - Connection issues
        """
        try:
            json_matrix1 = self._prepare_matrix_for_json(matrix1)
            json_matrix2 = self._prepare_matrix_for_json(matrix2)
            request = {
                "type": "matrix_multiply",
                "matrix1": json_matrix1,
                "matrix2": json_matrix2
            }
            print(f"Debug - Sending matrices: {json.dumps(request)}")  # Debug print
            response = self.send_request(request)
            if "error" in response:  # If server returned error
                return None
            return response["result"]
        except Exception as e:
            print(f"Error in matrix multiplication: {str(e)}")
            return None

    def close(self):
        """Close the connection to the server.
        
        Process:
        1. Shutdown socket gracefully
        2. Close socket
        3. Clear socket reference
        4. Handle cleanup errors
        
        Error Handling:
        - Socket errors
        - Already closed connections
        """
        try:
            if self.client_socket:  # If socket is open
                self.client_socket.shutdown(socket.SHUT_RDWR)  # Shutdown socket
                self.client_socket.close()  # Close socket
                self.client_socket = None
                print("Disconnected from server")
        except Exception as e:
            print(f"Error closing connection: {str(e)}")

    def __del__(self):
        """Destructor to ensure socket is closed.
        
        Ensures proper cleanup of network resources when the client
        object is garbage collected.
        """
        self.close()  # Ensure socket is closed on deletion