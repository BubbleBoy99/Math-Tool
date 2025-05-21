import os  # For file and path operations
import sys  # For system-specific parameters and functions
import tkinter as tk  # Tkinter for GUI
import threading  # For running server in a separate thread
from Client import MathClient
from Server import MathServer
from typing import Dict, Any

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory
if current_dir not in sys.path:
    sys.path.append(current_dir)  # Ensure local imports work

# Now import the local modules
from SolverModel import SolverModel
from CalculatorModel import CalculatorModel
from PlotterModel import PlotterModel
from View import CalculatorView
from MatrixModel import MatrixModel

class Controller:
    """Main controller for the mathematical application suite.
    
    This class serves as the central coordinator between the user interface,
    mathematical models, and network communication components. It implements
    the MVC (Model-View-Controller) pattern to manage:
    
    Components:
    1. User Interface (View)
       - Calculator interface
       - Equation solver interface
       - Matrix operations interface
       
    2. Mathematical Models
       - Calculator operations and base conversions
       - Equation solving and symbolic mathematics
       - Matrix operations and validations
       - Function plotting and visualization
       
    3. Network Communication
       - Client-server architecture
       - Request-response handling
       - Error management
       
    Features:
    - Multi-threaded server operation
    - Real-time calculation processing
    - Dynamic base conversion
    - Matrix operation handling
    - Equation solving and plotting
    
    Integration:
    - Manages communication between UI and models
    - Coordinates client-server operations
    - Handles user input validation
    - Manages error states and recovery
    """
    
    def __init__(self, root):
        """Initialize the controller with all required components.
        
        Sets up the following:
        1. Server initialization in separate thread
        2. Client connection establishment
        3. Model instantiation
        4. View creation and configuration
        5. Event binding for all UI elements
        
        Args:
            root: The root tkinter window for the application
            
        Components Initialized:
        - MathServer: Handles computation requests
        - MathClient: Manages server communication
        - CalculatorModel: Processes calculations
        - SolverModel: Handles equation solving
        - PlotterModel: Manages plotting
        - MatrixModel: Processes matrix operations
        - CalculatorView: Manages UI elements
        """
        self.server = MathServer(host='localhost', port=12345)
        self.server_thread = threading.Thread(target=self.server.run)  # Start server in new thread
        self.server_thread.daemon = True
        self.server_thread.start()
        
        self.math_client = MathClient(host='localhost', port=12345)
        self.calc_model = CalculatorModel()
        self.solver_model = SolverModel()
        self.plotter_model = PlotterModel()
        self.matrix_model = MatrixModel()
        self.view = CalculatorView(root)
        
        self.view.calc_nav_button.configure(command=self.show_calculator)
        self.view.solver_nav_button.configure(command=self.show_solver)
        self.view.matrix_nav_button.configure(command=self.show_matrix)
        
        for text, button in self.view.calc_buttons.items():  # Loop over all calculator buttons
            if text == '=':  # If button is equals
                button.configure(command=self.calculate)
            elif text == 'CE':  # If button is clear entry
                button.configure(command=self.clear_entry)
            elif text == '⌫':  # If button is backspace
                button.configure(command=self.delete_last)
            elif text in ['BIN', 'OCT', 'DEC', 'HEX']:  # If button is a base selector
                button.configure(command=lambda b=text: self.set_base(b))
            else:  # All other buttons (digits/operators)
                button.configure(command=lambda t=text: self.append_to_entry(t))
        
        self.view.solve_button.configure(command=self.solve)
        self.view.plot_button.configure(command=self.plot)
        
        self.view.add_matrices_btn.configure(command=self.add_matrices)
        self.view.subtract_matrices_btn.configure(command=self.subtract_matrices)
        self.view.multiply_matrices_btn.configure(command=self.multiply_matrices)
        
        self.show_calculator()
        
        self.current_base = 'DEC'  # Default base is decimal
        
    def append_to_entry(self, char):
        """Append a character to the calculator entry field.
        
        Validates the input character against the current number base
        and only allows valid digits and operators.
        
        Args:
            char: The character to append
            
        Validation:
        - Checks against current base's valid digits
        - Always allows operators and special characters
        - Maintains base-specific input restrictions
        """
        # Special function buttons should always be enabled
        special_buttons = ['CE', '⌫', '=']
        operators = ['+', '-', '*', '/', '(', ')']
        
        # Only allow digits valid for current base and special characters
        if (char in self.calc_model.get_available_digits(self.view.current_base) or  # If char is valid for base
            char in operators or  # Or if char is an operator
            char in special_buttons):  # Or if char is a special button
            self.view.calc_entry.insert(tk.END, char)

    def clear_entry(self):
        """Clear the calculator entry field.
        
        Resets the calculator display and shows the current base.
        """
        self.view.calc_entry.delete(0, tk.END)
        self.view.set_calc_display(f"Base: {self.view.current_base}")

    def delete_last(self):
        """Delete the last character from the calculator entry.
        
        Provides backspace functionality for the calculator display.
        """
        current = self.view.get_calc_entry()
        if current:
            self.view.calc_entry.delete(0, tk.END)
            self.view.calc_entry.insert(0, current[:-1])

    def set_base(self, base):
        """Set the calculator's number base and update the display.
        
        Changes the current number base and attempts to convert
        the current expression to the new base.
        
        Args:
            base: Target number base (BIN, OCT, DEC, HEX)
            
        Process:
        1. Update UI button states for new base
        2. Convert current expression to new base
        3. Update display with converted value
        4. Handle conversion errors
        """
        # Update view's base and button states
        self.view._update_button_states(base)
        
        # Try to convert current expression to new base
        current_expr = self.view.get_calc_entry()
        if current_expr:
            try:
                # Send request to server to convert the expression
                result = self.math_client.send_calculation(current_expr, base)
                if not result.startswith("Error"):
                    # Extract just the result part after the base indicator
                    value = result.split(": ")[1]
                    self.view.calc_entry.delete(0, tk.END)
                    self.view.calc_entry.insert(0, value)
            except Exception as e:
                self.clear_entry()
                self.view.set_calc_display(f"Error: {str(e)}")

    def get_available_digits(self) -> list:
        """Get the list of valid digits for the current base.
        
        Returns:
            list: Valid digits for the current number base
        """
        return self.calc_model.get_available_digits(self.current_base)
        
    def get_operators(self) -> list:
        """Get the list of available mathematical operators.
        
        Returns:
            list: Valid mathematical operators
        """
        return self.calc_model.get_operators()
        
    def get_max_digits(self) -> int:
        """Get the maximum number of digits allowed for current base.
        
        Returns:
            int: Maximum number of digits allowed
        """
        return self.calc_model.get_max_digits(self.current_base)
        
    def evaluate(self, expression: str) -> str:
        """Evaluate a mathematical expression in the current base.
        
        Performs validation and evaluation of the expression while
        maintaining the current number base context.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            str: Result of the evaluation in the current base
            
        Raises:
            ValueError: If expression is invalid or evaluation fails
            
        Process:
        1. Validate expression format
        2. Check for base-specific constraints
        3. Perform evaluation
        4. Convert result to current base
        """
        try:
            # First validate the expression
            self.calc_model.validate_expression(expression, self.current_base)
            
            # Then evaluate it
            result = self.calc_model.evaluate_expression(expression, self.current_base)
            return result
            
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {str(e)}")
            
    def serialize_calculation(self, expr: str, result: str) -> Dict[str, Any]:
        """Serialize a calculation for storage or transmission.
        
        Args:
            expr: The mathematical expression
            result: The calculation result
            
        Returns:
            Dict[str, Any]: Serialized calculation data
        """
        return self.calc_model.serialize_calculation(expr, self.current_base, result)
        
    def deserialize_calculation(self, data: Dict[str, Any]) -> tuple:
        """Deserialize a calculation from storage or transmission.
        
        Args:
            data: Serialized calculation data
            
        Returns:
            tuple: (expression, base, result)
        """
        return self.calc_model.deserialize_calculation(data)

    def calculate(self):
        """Process the current calculator expression.
        
        Sends the current expression to the server for calculation
        and updates all base displays with the result.
        
        Process:
        1. Get current expression
        2. Send to server for calculation
        3. Convert result to all bases
        4. Update all base displays
        5. Handle calculation errors
        
        Error Handling:
        - Invalid expressions
        - Base conversion errors
        - Server communication errors
        """
        expr = self.view.get_calc_entry()
        if not expr:
            return
        try:
            # Get result in current base
            result = self.math_client.send_calculation(expr, self.view.current_base)
            
            # Extract the numeric value from the result (remove "Base X: " prefix)
            value = result.split(": ")[1] if ": " in result else result
            
            # Calculate the value in all bases
            try:
                # Convert to decimal first (assuming current base)
                if self.view.current_base == 'BIN':
                    if '.' in value:
                        raise ValueError('Non-integer result cannot be represented in BIN base')
                    dec_value = int(value, 2)
                elif self.view.current_base == 'OCT':
                    if '.' in value:
                        raise ValueError('Non-integer result cannot be represented in OCT base')
                    dec_value = int(value, 8)
                elif self.view.current_base == 'HEX':
                    if '.' in value:
                        raise ValueError('Non-integer result cannot be represented in HEX base')
                    dec_value = int(value, 16)
                else:  # DEC
                    dec_value = float(value)
                
                # Now convert to all bases
                base_values = {
                    'BIN': str(bin(int(dec_value))[2:]) if dec_value.is_integer() else 'N/A',
                    'OCT': str(oct(int(dec_value))[2:]) if dec_value.is_integer() else 'N/A',
                    'DEC': str(dec_value),
                    'HEX': str(hex(int(dec_value))[2:].upper()) if dec_value.is_integer() else 'N/A'
                }
                
                # Update all displays
                self.view.set_base_displays(base_values)
                
            except ValueError as e:
                # If conversion fails, show error in all displays
                error_msg = f"Error: {str(e)}"
                self.view.set_base_displays({
                    'BIN': error_msg,
                    'OCT': error_msg,
                    'DEC': error_msg,
                    'HEX': error_msg
                })
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.view.set_base_displays({
                'BIN': error_msg,
                'OCT': error_msg,
                'DEC': error_msg,
                'HEX': error_msg
            })

    def solve(self):
        """Process and solve the current equation.
        
        Sends the equation to the server for solving and displays
        the step-by-step solution in the solver output area.
        
        Process:
        1. Get equation from input field
        2. Send to server for solving
        3. Display solution steps
        4. Handle solving errors
        
        Features:
        - Symbolic mathematics support
        - Step-by-step solution display
        - Error handling and reporting
        """
        equation = self.view.get_solver_entry()
        if not equation:
            return
        try:
            result = self.math_client.send_solve(equation)
            self.view.set_solver_output(result)
        except Exception as e:
            self.view.set_solver_output(f"Error: {str(e)}")

    def plot(self):
        """Plot the current equation or function.
        
        Sends the equation to the server for plotting and displays
        the result or opens a plotting window.
        
        Process:
        1. Get equation from input field
        2. Send to server for plotting
        3. Display or show plot
        4. Handle plotting errors
        
        Features:
        - Function visualization
        - Multiple plot types support
        - Error handling for undefined regions
        """
        equation = self.view.get_solver_entry()
        if not equation:
            return
        try:
            result = self.math_client.send_plot(equation)
            self.view.set_solver_output(result)
        except Exception as e:
            self.view.set_solver_output(f"Error: {str(e)}")

    def show_calculator(self):
        """Switch to the calculator interface.
        
        Activates the calculator view and performs necessary cleanup
        of other interfaces.
        """
        self.view.show_calculator()
        print("Switched to Calculator")  # Debugging

    def show_solver(self):
        """Switch to the solver and plotter interface.
        
        Activates the equation solver view and performs necessary
        cleanup of other interfaces.
        """
        self.view.show_solver()
        print("Switched to Solver & Plotter")  # Debugging

    def show_matrix(self):
        """Switch to the matrix operations interface.
        
        Activates the matrix operations view and performs necessary
        cleanup of other interfaces.
        """
        self.view.show_matrix()
        print("Switched to Matrix Operations")  # Debugging

    def add_matrices(self):
        """Add two matrices together.
        
        Retrieves matrices from input fields, validates them,
        and performs matrix addition through the server.
        
        Process:
        1. Get and validate matrix inputs
        2. Send to server for addition
        3. Display result matrix
        4. Handle operation errors
        
        Validation:
        - Matrix format checking
        - Dimension compatibility
        - Content validation
        - Server response verification
        """
        try:
            matrices = self.view.get_matrix_values()
            if matrices is None:
                raise ValueError("Invalid matrix format. Use format: [1,2,3; 4,5,6; 7,8,9]")
                
            matrix1, matrix2 = matrices
            result = self.math_client.send_matrix_add(matrix1, matrix2)
            if result is None:
                raise ValueError("Server error during matrix addition")
                
            self.view.display_matrix_result(result)
            
        except Exception as e:
            self.view.show_matrix_error(str(e))

    def subtract_matrices(self):
        """Subtract two matrices.
        
        Retrieves matrices from input fields, validates them,
        and performs matrix subtraction through the server.
        
        Process:
        1. Get and validate matrix inputs
        2. Send to server for subtraction
        3. Display result matrix
        4. Handle operation errors
        
        Validation:
        - Matrix format checking
        - Dimension compatibility
        - Content validation
        - Server response verification
        """
        try:
            matrices = self.view.get_matrix_values()
            if matrices is None:
                raise ValueError("Invalid matrix format. Use format: [1,2,3; 4,5,6; 7,8,9]")
                
            matrix1, matrix2 = matrices
            result = self.math_client.send_matrix_subtract(matrix1, matrix2)
            if result is None:
                raise ValueError("Server error during matrix subtraction")
                
            self.view.display_matrix_result(result)
            
        except Exception as e:
            self.view.show_matrix_error(str(e))

    def multiply_matrices(self):
        """Multiply two matrices.
        
        Retrieves matrices from input fields, validates them,
        and performs matrix multiplication through the server.
        
        Process:
        1. Get and validate matrix inputs
        2. Send to server for multiplication
        3. Display result matrix
        4. Handle operation errors
        
        Validation:
        - Matrix format checking
        - Dimension compatibility
        - Content validation
        - Server response verification
        """
        try:
            matrices = self.view.get_matrix_values()
            if matrices is None:
                raise ValueError("Invalid matrix format. Use format: [1,2,3; 4,5,6; 7,8,9]")
                
            matrix1, matrix2 = matrices
            result = self.math_client.send_matrix_multiply(matrix1, matrix2)
            if result is None:
                raise ValueError("Server error during matrix multiplication")
                
            self.view.display_matrix_result(result)
            
        except Exception as e:
            self.view.show_matrix_error(str(e))

    def __del__(self):
        """Clean up resources when the controller is destroyed.
        
        Performs cleanup operations:
        1. Close client connection
        2. Stop server thread
        3. Release system resources
        
        Error Handling:
        - Graceful handling of cleanup failures
        - Silent error suppression for normal shutdown
        """
        try:
            self.math_client.close()
            self.server.stop()
        except:
            pass