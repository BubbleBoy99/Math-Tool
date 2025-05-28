import json  # For JSON serialization/deserialization
import socket  # For network communication
import time  # For retry delays
import threading
import logging  # For logging events and data

class MathClientController:
    """Controller for the View. Handles all server communication and UI updates."""
    def __init__(self, view, host='localhost', port=12345):
        self.view = view
        self.host = host
        self.port = port
        self.connection_timeout = 5
        self.response_timeout = 10
        self.max_retries = 1  # Reduced for faster feedback
        self.retry_delay = 0.1  # Reduced for faster feedback
        self.logger = logging.getLogger('MathClient')
        self.logger.setLevel(logging.INFO)  # Set logging level
        handler = logging.FileHandler('logs/client.log')  # Changed to relative path
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        # Wire up UI events
        if hasattr(view, 'calc_buttons'):
            for key, btn in view.calc_buttons.items():
                if key == '=':
                    btn.configure(command=self.on_calculate)
                elif key in ['CE']:
                    btn.configure(command=self.on_calc_clear)
                elif key in ['⌫']:
                    btn.configure(command=self.on_calc_backspace)
                elif key in ['BIN', 'OCT', 'DEC', 'HEX']:
                    btn.configure(command=lambda b=key: self.on_base_change(b))
                else:
                    btn.configure(command=lambda k=key: self.on_calc_button_press(k))
        if hasattr(view, 'solve_button'):
            view.solve_button.configure(command=self.on_solve)
        if hasattr(view, 'plot_button'):
            view.plot_button.configure(command=self.on_plot)
        if hasattr(view, 'add_matrices_btn'):
            view.add_matrices_btn.configure(command=self.on_matrix_add)
        if hasattr(view, 'subtract_matrices_btn'):
            view.subtract_matrices_btn.configure(command=self.on_matrix_subtract)
        if hasattr(view, 'multiply_matrices_btn'):
            view.multiply_matrices_btn.configure(command=self.on_matrix_multiply)
        # Navigation buttons to update UI
        if hasattr(view, 'calc_nav_button'):
            view.calc_nav_button.configure(command=view.show_calculator)
        if hasattr(view, 'solver_nav_button'):
            view.solver_nav_button.configure(command=view.show_solver)
        if hasattr(view, 'matrix_nav_button'):
            view.matrix_nav_button.configure(command=view.show_matrix)

    def is_server_running(self):
        try:
            with socket.create_connection((self.host, self.port), timeout=2):
                return True
        except Exception:
            return False

    def update_server_status(self):
        if self.is_server_running():
            self.view.set_server_status('Online', color='green')
        else:
            self.view.set_server_status('Offline', color='red')

    def send_request(self, request_dict):
        self.logger.info(f'Sending request: {request_dict}')  # Log the request
        self.update_server_status()  # Update status before sending
        retries = 0
        last_exception = None
        start = time.time()
        while retries < self.max_retries:
            try:
                with socket.create_connection((self.host, self.port), timeout=self.connection_timeout) as sock:
                    sock.settimeout(self.response_timeout)
                    request_data = json.dumps(request_dict).encode('utf-8')
                    sock.sendall(request_data)
                    sock.shutdown(socket.SHUT_WR)
                    response = b""
                    while True:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        response += chunk
                    received_response = json.loads(response.decode('utf-8'))
                    self.logger.info(f'Received response: {received_response}')  # Log the response
                    self.update_server_status()  # Update status after successful response
                    print(f"Request/response roundtrip: {time.time() - start:.3f} seconds")
                    return received_response
            except Exception as e:
                last_exception = str(e)
                self.logger.error(f'Error in send_request: {e}')  # Log the error
                retries += 1
                time.sleep(self.retry_delay)
        self.update_server_status()  # Update status after failure
        print(f"Request failed after {time.time() - start:.3f} seconds")
        error_response = {"error": f"Server is offline or unreachable. Failed to connect after {self.max_retries} attempts. Last error: {last_exception}"}
        self.logger.error(f'Request failed: {error_response}')  # Log the failure
        return error_response

    def on_calculate(self):
        expr = self.view.get_calc_entry()
        base = getattr(self.view, 'current_base', 'DEC')
        self.logger.info(f'Calculating expression: {expr} in base {base}')  # Log calculate event
        def worker():
            request = {"model": "calculator", "instructions": {"expr": expr, "base": base}}
            response = self.send_request(request)
            def update_ui():
                if "result" in response:
                    self.logger.info(f'Calculation result: {response["result"]}')  # Log result
                    result = response["result"]
                    try:
                        if base == 'DEC':
                            dec_value = int(float(result))
                        else:
                            dec_value = int(result, {'BIN': 2, 'OCT': 8, 'HEX': 16}[base])
                        base_values = {
                            'BIN': bin(dec_value)[2:] if dec_value >= 0 else '-' + bin(-dec_value)[2:],
                            'OCT': oct(dec_value)[2:] if dec_value >= 0 else '-' + oct(-dec_value)[2:],
                            'DEC': str(dec_value),
                            'HEX': hex(dec_value)[2:].upper() if dec_value >= 0 else '-' + hex(-dec_value)[2:].upper()
                        }
                    except Exception:
                        base_values = {'BIN': 'Err', 'OCT': 'Err', 'DEC': str(result), 'HEX': 'Err'}
                    self.view.set_base_displays(base_values)
                    self.view.set_calc_display(str(result))
                else:
                    self.logger.error(f'Calculation error: {response.get("error", "Unknown error")}')  # Log error
                    self.view.set_calc_display(f"Error: {response.get('error', 'Unknown error')}")
                    self.view.set_base_displays({'BIN': '', 'OCT': '', 'DEC': '', 'HEX': ''})
            self.view.root.after(0, update_ui)
        threading.Thread(target=worker, daemon=True).start()

    def on_solve(self):
        equation = self.view.get_solver_entry()
        self.logger.info(f'Solving equation: {equation}')  # Log solve event
        request = {"model": "solver", "instructions": {"equation": equation}}
        response = self.send_request(request)
        if "result" in response:
            self.logger.info(f'Solve result: {response["result"]}')  # Log result
            self.view.set_solver_output(response["result"])
        else:
            self.logger.error(f'Solve error: {response.get("error", "Unknown error")}')  # Log error
            self.view.set_solver_output(f"Error: {response.get('error', 'Unknown error')}")

    def on_matrix_add(self):
        m1, m2 = self.view.get_matrix_values()
        request = {"model": "matrix", "instructions": {"operation": "add", "matrix1": m1, "matrix2": m2}}
        response = self.send_request(request)
        if "result" in response:
            self.view.display_matrix_result(response["result"])
        else:
            self.view.show_matrix_error(response.get('error', 'Unknown error'))
    def on_matrix_subtract(self):
        m1, m2 = self.view.get_matrix_values()
        request = {"model": "matrix", "instructions": {"operation": "subtract", "matrix1": m1, "matrix2": m2}}
        response = self.send_request(request)
        if "result" in response:
            self.view.display_matrix_result(response["result"])
        else:
            self.view.show_matrix_error(response.get('error', 'Unknown error'))

    def on_matrix_multiply(self):
        m1, m2 = self.view.get_matrix_values()
        request = {"model": "matrix", "instructions": {"operation": "multiply", "matrix1": m1, "matrix2": m2}}
        response = self.send_request(request)
        if "result" in response:
            self.view.display_matrix_result(response["result"])
        else:
            self.view.show_matrix_error(response.get('error', 'Unknown error'))

    def on_plot(self):
        equation = self.view.get_solver_entry()
        request = {"model": "plotter", "instructions": {"equation": equation}}
        response = self.send_request(request)
        if "result" in response:
            self.view.set_solver_output(response["result"])
        else:
            self.view.set_solver_output(f"Error: {response.get('error', 'Unknown error')}")

    def on_calc_button_press(self, key):
        if key == '√':
            entry = self.view.get_calc_entry() + '√'  
            self.view.set_calc_display(entry)
        elif key == '^':
            entry = self.view.get_calc_entry() + '^'  
            self.view.set_calc_display(entry)
        elif key == '!':
            entry = self.view.get_calc_entry() + '!'  
            self.view.set_calc_display(entry)
        else:
            entry = self.view.get_calc_entry() + key  
            self.view.set_calc_display(entry)

    def on_calc_clear(self):
        self.view.set_calc_display("")

    def on_calc_backspace(self):
        entry = self.view.get_calc_entry()
        self.view.set_calc_display(entry[:-1])

    def on_base_change(self, base):
        self.view._update_button_states(base)
        # Clear all fields when switching base
        self.view.set_calc_display("")
        self.view.set_base_displays({'BIN': '', 'OCT': '', 'DEC': '', 'HEX': ''})
