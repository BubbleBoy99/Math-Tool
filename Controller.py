import socket
import json
from SolverModel import SolverModel
from CalculatorModel import CalculatorModel
from PlotterModel import PlotterModel
from MatrixModel import MatrixModel
from ModelUtils import handle_model_request
import threading
import time

class Controller:
    """Controller for mathematical models, handling JSON requests and data formatting."""
    def __init__(self, client_host='localhost', client_port=12345):
        self.calc_model = CalculatorModel()
        self.solver_model = SolverModel()
        self.plotter_model = PlotterModel()
        self.matrix_model = MatrixModel()
        self.client_host = client_host
        self.client_port = client_port

    def process_json_request(self, json_str: str) -> str:
        try:
            data = json.loads(json_str)
            model_name = data.get("model")
            instructions = data.get("instructions", {})
            result = handle_model_request(self, model_name, instructions)
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def send_to_client(self, json_str: str) -> str:
        """Send a JSON string to the client over TCP and return the response as a string."""
        try:
            with socket.create_connection((self.client_host, self.client_port), timeout=10) as sock:
                sock.sendall(json_str.encode('utf-8'))
                sock.shutdown(socket.SHUT_WR)
                response = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                return response.decode('utf-8')
        except Exception as e:
            return json.dumps({"error": str(e)})

    def handle_client(self, conn, addr):
        with conn:
            print(f"Connected by {addr}")
            start = time.time()
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
            print(f"Received data in {time.time() - start:.3f} seconds")
            if data:
                request_str = data.decode('utf-8')
                response_str = self.process_json_request(request_str)
                print(f"Processed request in {time.time() - start:.3f} seconds")
                conn.sendall(response_str.encode('utf-8'))
            print(f"Total handle_client time: {time.time() - start:.3f} seconds")

    def run_server(self, host='0.0.0.0', port=12345):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.bind((host, port))
            server_sock.listen()
            print(f"Controller server listening on {host}:{port}")
            while True:
                conn, addr = server_sock.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                client_thread.start()

if __name__ == "__main__":
    controller = Controller()
    controller.run_server(host='0.0.0.0', port=12345)