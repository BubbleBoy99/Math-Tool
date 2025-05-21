import tkinter as tk  # Tkinter for GUI
from tkinter import ttk  # Themed Tkinter widgets
from MatrixModel import MatrixModel

class CalculatorView:
    """A comprehensive graphical user interface for a mathematical application.
    
    This class implements a modern, multi-functional calculator interface with three main components:
    1. Basic Calculator: Supports arithmetic operations in multiple number bases (BIN, OCT, DEC, HEX)
    2. Equation Solver & Plotter: Handles equation solving and function visualization
    3. Matrix Operations: Provides interface for matrix arithmetic and transformations
    
    Key Features:
    - Dark theme with consistent styling across all components
    - Responsive layout that adapts to window size
    - Real-time base conversion display
    - Interactive equation solving with step-by-step solutions
    - Visual function plotting capabilities
    - Matrix operations with flexible input formats
    
    Design Principles:
    - Modular component organization
    - Consistent styling and theming
    - Clear visual hierarchy
    - Intuitive user interaction
    - Comprehensive error handling and feedback
    
    Integration Points:
    - Uses MatrixModel for matrix input parsing and validation
    - Interfaces with calculator model for arithmetic operations
    - Connects with solver model for equation processing
    - Communicates with plotting system for visualization
    """
    
    def __init__(self, root):
        """Initialize the calculator view with all its components.
        
        This method sets up the main window and initializes all UI components:
        1. Window configuration (size, position, theme)
        2. Style definitions for all widgets
        3. Layout containers and frames
        4. Navigation components
        5. Individual calculator interfaces
        
        Args:
            root: The root Tkinter window
            
        Components Created:
        - Main container with responsive grid layout
        - Navigation bar with section buttons
        - Calculator interface with number pad
        - Solver interface with input and output areas
        - Matrix interface with operation controls
        
        Style Configuration:
        - Dark theme with consistent colors
        - Modern button and input styling
        - Responsive grid-based layout
        - Proper spacing and padding
        """
        self.root = root
        self.root.title("Your Math Tool")
        self.matrix_model = MatrixModel()
        screen_width = root.winfo_screenwidth()  # Get screen width
        screen_height = root.winfo_screenheight()  # Get screen height
        window_width = int(screen_width * 0.6)  # 60% of screen width
        window_height = int(screen_height * 0.8)  # 80% of screen height
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.root.configure(bg='#1a1a1a')
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use 'clam' theme for modern look
        
        # Normal button style
        self.style.configure('TButton', 
                           font=('Helvetica', 12, 'bold'), 
                           padding=8, 
                           background='#333333', 
                           foreground='white',
                           borderwidth=1,
                           relief='flat')
        
        # Button states mapping (hover, disabled, etc.)
        self.style.map('TButton',
                      background=[('active', '#555555'),
                                ('disabled', '#1a1a1a')],
                      foreground=[('active', 'white'),
                                ('disabled', '#666666')])
                                
        # Other styles remain the same
        self.style.configure('TLabel', 
                           font=('Helvetica', 14),
                           background='#1a1a1a',
                           foreground='#ffffff')
        self.style.configure('TEntry',
                           font=('Helvetica', 14),
                           fieldbackground='#2a2a2a',
                           foreground='white',
                           borderwidth=1,
                           relief='solid')
        self.style.configure('TFrame',
                           background='#1a1a1a')
        
        # Create outer container for centering
        self.outer_container = ttk.Frame(root, style='TFrame')
        self.outer_container.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Configure grid weights for centering
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        
        # Create main container with padding
        self.main_container = ttk.Frame(self.outer_container, padding=20, style='TFrame')
        self.main_container.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Configure outer container grid weights for centering
        self.outer_container.grid_columnconfigure(0, weight=1)  # Left margin
        self.outer_container.grid_columnconfigure(1, weight=2)  # Content
        self.outer_container.grid_columnconfigure(2, weight=1)  # Right margin
        self.outer_container.grid_rowconfigure(0, weight=1)     # Top margin
        self.outer_container.grid_rowconfigure(1, weight=2)     # Content
        self.outer_container.grid_rowconfigure(2, weight=1)     # Bottom margin
        
        # Create navigation frame
        self.nav_frame = ttk.Frame(self.main_container, style='TFrame')
        self.nav_frame.grid(row=0, column=0, pady=(0, 20))
        
        # Center the navigation buttons
        self.nav_frame.grid_columnconfigure(0, weight=1)  # Space before buttons
        self.nav_frame.grid_columnconfigure(4, weight=1)  # Space after buttons
        
        self.calc_nav_button = ttk.Button(self.nav_frame, text="Calculator", style='TButton')
        self.calc_nav_button.grid(row=0, column=1, padx=5)
        
        self.solver_nav_button = ttk.Button(self.nav_frame, text="Solver & Plotter", style='TButton')
        self.solver_nav_button.grid(row=0, column=2, padx=5)

        self.matrix_nav_button = ttk.Button(self.nav_frame, text="Matrix Operations", style='TButton')
        self.matrix_nav_button.grid(row=0, column=3, padx=5)
        
        # Create calculator frame
        self.calc_frame = ttk.Frame(self.main_container, style='TFrame')
        self.calc_frame.grid(row=1, column=0)
        
        # Create solver frame
        self.solver_frame = ttk.Frame(self.main_container, style='TFrame')
        self.solver_frame.grid(row=1, column=0)

        # Create matrix frame
        self.matrix_frame = ttk.Frame(self.main_container, style='TFrame')
        self.matrix_frame.grid(row=1, column=0)
        
        # Configure main container grid weights
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Initialize calculator components
        self._init_calculator()
        
        # Initialize solver components
        self._init_solver()

        # Initialize matrix components
        self._init_matrix()
        
        # Set default base
        self.current_base = 'DEC'
        
    def _init_calculator(self):
        """Initialize the basic calculator interface.
        
        Sets up the calculator component with the following features:
        1. Main display field for calculations
        2. Base conversion display area (BIN, OCT, DEC, HEX)
        3. Number pad with base-specific digits
        4. Operation buttons for arithmetic
        
        Layout Organization:
        - Top: Main display field
        - Middle: Base conversion displays
        - Bottom: Interactive keypad
        
        Button Configuration:
        - Number buttons (0-9, A-F)
        - Operation buttons (+, -, *, /, etc.)
        - Control buttons (CE, backspace)
        - Base selection buttons
        
        State Management:
        - Tracks current number base
        - Updates button states based on base
        - Maintains conversion displays
        """
        # Entry field for calculations
        self.calc_entry = ttk.Entry(self.calc_frame, justify='left', style='TEntry')
        self.calc_entry.grid(row=0, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=5)
        
        # Create frame for base displays
        self.base_display_frame = ttk.Frame(self.calc_frame, style='TFrame')
        self.base_display_frame.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid for base displays
        self.base_display_frame.grid_columnconfigure(1, weight=1)  # Make value column expandable
        
        # Create labels for each base
        bases = [
            ('BIN', 'Binary:'),
            ('OCT', 'Octal:'),
            ('DEC', 'Decimal:'),
            ('HEX', 'Hexadecimal:')
        ]
        
        self.base_displays = {}
        for idx, (base_code, base_name) in enumerate(bases):  # Loop over all base display labels
            # Base name label
            name_label = ttk.Label(self.base_display_frame, text=base_name, style='TLabel', width=12)
            name_label.grid(row=idx, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            
            # Base value label
            value_label = ttk.Label(self.base_display_frame, text="0", style='TLabel')
            value_label.grid(row=idx, column=1, sticky=tk.W, pady=2)
            
            self.base_displays[base_code] = value_label
        
        # Calculator buttons
        self.calc_buttons = {}
        
        # Base selection buttons (now row 3)
        base_buttons = ['BIN', 'OCT', 'DEC', 'HEX']
        for i, base in enumerate(base_buttons):  # Loop over base selection buttons
            btn = ttk.Button(self.calc_frame, text=base, style='TButton')
            btn.grid(row=3, column=i, padx=2, pady=2)
            self.calc_buttons[base] = btn
        
        # First part of hex letters A-C (row 4)
        hex_letters_top = ['A', 'B', 'C']
        for i, letter in enumerate(hex_letters_top):  # Loop over first part of hex letters
            btn = ttk.Button(self.calc_frame, text=letter, style='TButton')
            btn.grid(row=4, column=i, padx=2, pady=2)
            self.calc_buttons[letter] = btn
            btn.state(['disabled'])  # Initially disabled (DEC mode)
            
        # Second part of hex letters D-F (row 5)
        hex_letters_bottom = ['D', 'E', 'F']
        for i, letter in enumerate(hex_letters_bottom):  # Loop over second part of hex letters
            btn = ttk.Button(self.calc_frame, text=letter, style='TButton')
            btn.grid(row=5, column=i, padx=2, pady=2)
            self.calc_buttons[letter] = btn
            btn.state(['disabled'])  # Initially disabled (DEC mode)
        
        # Number pad and operators with clear separation
        # Numbers on the left (columns 0-2)
        number_layout = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', ' ', ' ']
        ]
        
        # Operators on the right (columns 3-5)
        operator_layout = [
            ['/', '(', ')'],
            ['*', '⌫', 'CE'],
            ['-', ' ', ' '],
            ['+', ' ', '=']
        ]
        
        # Place numbers
        for row, numbers in enumerate(number_layout, 6):  # Loop over number pad rows
            for col, text in enumerate(numbers):  # Loop over numbers in row
                if text != ' ':  # If not a blank space
                    btn = ttk.Button(self.calc_frame, text=text, style='TButton')
                    btn.grid(row=row, column=col, padx=2, pady=2)
                    self.calc_buttons[text] = btn
        
        # Place operators
        for row, operators in enumerate(operator_layout, 6):  # Loop over operator pad rows
            for col, text in enumerate(operators):  # Loop over operators in row
                if text != ' ':  # If not a blank space
                    btn = ttk.Button(self.calc_frame, text=text, style='TButton')
                    btn.grid(row=row, column=col+3, padx=2, pady=2)  # Offset by 3 columns
                    self.calc_buttons[text] = btn
        
        # Initially disable buttons based on decimal base
        self._update_button_states('DEC')
        
    def _init_solver(self):
        """Initialize the equation solver and plotter interface.
        
        Sets up the solver component with the following features:
        1. Equation input field with label
        2. Control buttons for solving and plotting
        3. Output area for solutions and plots
        
        Layout Organization:
        - Top: Equation input with label
        - Middle: Action buttons
        - Bottom: Solution/plot display area
        
        Features:
        - Support for symbolic mathematics
        - Step-by-step solution display
        - Function plotting capabilities
        - Error feedback display
        
        Display Configuration:
        - Monospace font for clear output
        - Scrollable solution area
        - Dark theme consistency
        - Proper spacing for readability
        """
        # Entry field for equations with label
        entry_frame = ttk.Frame(self.solver_frame, style='TFrame')
        entry_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Center the entry components
        entry_frame.grid_columnconfigure(0, weight=1)  # Space before
        entry_frame.grid_columnconfigure(3, weight=1)  # Space after
        
        equation_label = ttk.Label(entry_frame, text="Enter equation:", style='TLabel')
        equation_label.grid(row=0, column=1, padx=(0, 10), sticky=tk.E)
        
        self.solver_entry = ttk.Entry(entry_frame, justify='left', style='TEntry', width=60)
        self.solver_entry.grid(row=0, column=2, sticky=tk.EW)
        
        # Buttons frame
        button_frame = ttk.Frame(self.solver_frame, style='TFrame')
        button_frame.grid(row=1, column=0, pady=10)
        
        # Center the buttons
        button_frame.grid_columnconfigure(0, weight=1)  # Space before
        button_frame.grid_columnconfigure(3, weight=1)  # Space after
        
        self.solve_button = ttk.Button(button_frame, text="Solve", style='TButton', width=15)
        self.solve_button.grid(row=0, column=1, padx=10)
        
        self.plot_button = ttk.Button(button_frame, text="Plot", style='TButton', width=15)
        self.plot_button.grid(row=0, column=2, padx=10)
        
        # Output area with centered label
        output_frame = ttk.Frame(self.solver_frame, style='TFrame')
        output_frame.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), pady=10)
        
        # Center the output components
        output_frame.grid_columnconfigure(0, weight=1)  # Space before
        output_frame.grid_columnconfigure(3, weight=1)  # Space after
        
        output_label = ttk.Label(output_frame, text="Solution:", style='TLabel')
        output_label.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # Output text area with dark theme and monospace font
        self.solver_output = tk.Text(output_frame,
                                   height=25,
                                   width=80,
                                   font=('Consolas', 12),
                                   bg='#2a2a2a',
                                   fg='white',
                                   insertbackground='white',
                                   relief='solid',
                                   borderwidth=1,
                                   wrap=tk.WORD)
        
        self.solver_output.grid(row=1, column=1, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Configure solver frame grid weights
        self.solver_frame.grid_columnconfigure(0, weight=1)
        self.solver_frame.grid_rowconfigure(2, weight=1)
        
    def _init_matrix(self):
        """Initialize the matrix operations interface.
        
        Sets up the matrix component with the following features:
        1. Input areas for two matrices
        2. Operation buttons (add, subtract, multiply)
        3. Result display area
        4. Error feedback section
        
        Layout Organization:
        - Top: Instructions and input format guide
        - Middle: Matrix input areas (A and B)
        - Controls: Operation buttons
        - Bottom: Result display and error messages
        
        Input Features:
        - Flexible matrix input format
        - Real-time validation
        - Support for symbolic entries
        - Error highlighting
        
        Operation Support:
        - Matrix addition
        - Matrix subtraction
        - Matrix multiplication
        - Dimension validation
        """
        # Main container for matrix operations
        matrix_container = ttk.Frame(self.matrix_frame, style='TFrame')
        matrix_container.grid(row=0, column=0, padx=20, pady=20, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Instructions label
        instructions = ("Enter matrices in the format: [1,2,3; 4,5,6; 7,8,9]\n"
                       "Use commas (,) to separate elements and semicolons (;) to separate rows")
        instructions_label = ttk.Label(matrix_container, text=instructions, style='TLabel', wraplength=400)
        instructions_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Matrix A input
        matrix_a_label = ttk.Label(matrix_container, text="Matrix A:", style='TLabel')
        matrix_a_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.matrix_a_input = tk.Text(matrix_container, height=5, width=40, bg='#2a2a2a', fg='white')
        self.matrix_a_input.grid(row=2, column=0, padx=10, pady=(0, 20))

        # Matrix B input
        matrix_b_label = ttk.Label(matrix_container, text="Matrix B:", style='TLabel')
        matrix_b_label.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        self.matrix_b_input = tk.Text(matrix_container, height=5, width=40, bg='#2a2a2a', fg='white')
        self.matrix_b_input.grid(row=2, column=1, padx=10, pady=(0, 20))

        # Buttons frame
        button_frame = ttk.Frame(matrix_container, style='TFrame')
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.add_matrices_btn = ttk.Button(button_frame, text="Add Matrices", style='TButton', width=20)
        self.add_matrices_btn.grid(row=0, column=0, padx=10)
        
        self.subtract_matrices_btn = ttk.Button(button_frame, text="Subtract Matrices", style='TButton', width=20)
        self.subtract_matrices_btn.grid(row=0, column=1, padx=10)

        self.multiply_matrices_btn = ttk.Button(button_frame, text="Multiply Matrices", style='TButton', width=20)
        self.multiply_matrices_btn.grid(row=0, column=2, padx=10)

        # Result display
        result_label = ttk.Label(matrix_container, text="Result:", style='TLabel')
        result_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(20, 5))
        
        self.matrix_result_display = tk.Text(matrix_container, height=5, width=80, bg='#2a2a2a', fg='white')
        self.matrix_result_display.grid(row=5, column=0, columnspan=2, pady=(0, 20))
        self.matrix_result_display.config(state='disabled')  # Make it read-only

        # Error display
        self.matrix_error_label = ttk.Label(matrix_container, text="", style='TLabel', foreground='red')
        self.matrix_error_label.grid(row=6, column=0, columnspan=2, pady=(0, 10))

        # Configure grid weights
        matrix_container.grid_columnconfigure(0, weight=1)
        matrix_container.grid_columnconfigure(1, weight=1)
        
    def _update_button_states(self, base):
        """Update calculator button states based on selected number base.
        
        Enables/disables number buttons based on the selected base:
        - BIN: 0-1
        - OCT: 0-7
        - DEC: 0-9
        - HEX: 0-9, A-F
        
        Args:
            base: Selected number base (BIN, OCT, DEC, HEX)
            
        Button Management:
        - Enables valid digits for current base
        - Disables invalid digits
        - Maintains operation buttons enabled
        - Updates current base tracking
        """
        # Define available digits for each base
        base_digits = {
            'BIN': ['0', '1'],
            'OCT': ['0', '1', '2', '3', '4', '5', '6', '7'],
            'DEC': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            'HEX': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        }
        
        # Special buttons that should always be enabled
        special_buttons = ['CE', '⌫', '=', '+', '-', '*', '/', '(', ')']
        
        # Enable/disable number buttons based on base
        for digit in '0123456789ABCDEF':  # Loop over all possible digit buttons
            if digit in self.calc_buttons:  # If button exists for this digit
                if digit in base_digits[base] or digit in special_buttons:  # If digit is valid for base or special
                    self.calc_buttons[digit].state(['!disabled'])
                else:  # Otherwise disable
                    self.calc_buttons[digit].state(['disabled'])
        
        # Ensure special buttons are always enabled
        for special in special_buttons:  # Loop over all special buttons
            if special in self.calc_buttons:  # If button exists for this special
                self.calc_buttons[special].state(['!disabled'])
        
        # Update current base
        self.current_base = base
        for base_code, value_label in self.base_displays.items():  # Loop over all base displays
            value_label.config(text=f"{base_code}: 0")
        
    def show_calculator(self):
        """Show the calculator interface and hide other components.
        
        Process:
        1. Hide solver and matrix interfaces
        2. Clear all displays and inputs
        3. Reset base conversion displays
        4. Show calculator frame
        
        Cleanup Operations:
        - Clear solver input/output
        - Reset matrix inputs/results
        - Clear calculator display
        - Reset base displays to 0
        """
        # Clean up solver
        self.solver_frame.grid_remove()
        self.solver_entry.delete(0, tk.END)
        self.solver_output.delete(1.0, tk.END)
        
        # Clean up matrix
        self.matrix_frame.grid_remove()
        self.matrix_result_display.delete(1.0, tk.END)
        if hasattr(self, 'matrix_a_entries'):
            for row in self.matrix_a_entries:
                for entry in row:
                    entry.delete(0, tk.END)
        if hasattr(self, 'matrix_b_entries'):
            for row in self.matrix_b_entries:
                for entry in row:
                    entry.delete(0, tk.END)
        
        # Clean up calculator
        self.calc_entry.delete(0, tk.END)
        self.set_base_displays({
            'BIN': 'Binary: 0',
            'OCT': 'Octal: 0',
            'DEC': 'Decimal: 0',
            'HEX': 'Hexadecimal: 0'
        })
        
        # Show calculator frame
        self.calc_frame.grid()
        
    def show_solver(self):
        """Show the solver interface and hide other components.
        
        Process:
        1. Hide calculator and matrix interfaces
        2. Clear any existing content
        3. Reset solver interface state
        4. Show solver frame
        
        Cleanup Operations:
        - Clear calculator display and memory
        - Reset solver input field
        - Clear solution output area
        - Reset matrix interface if active
        """
        # Clean up calculator
        self.calc_frame.grid_remove()
        self.calc_entry.delete(0, tk.END)
        
        # Clean up matrix
        self.matrix_frame.grid_remove()
        self.matrix_result_display.delete(1.0, tk.END)
        if hasattr(self, 'matrix_a_entries'):
            for row in self.matrix_a_entries:
                for entry in row:
                    entry.delete(0, tk.END)
        if hasattr(self, 'matrix_b_entries'):
            for row in self.matrix_b_entries:
                for entry in row:
                    entry.delete(0, tk.END)
        
        # Clean up solver
        self.solver_entry.delete(0, tk.END)
        self.solver_output.delete(1.0, tk.END)
        
        # Show solver frame
        self.solver_frame.grid()
        
    def show_matrix(self):
        """Show the matrix interface and hide other components.
        
        Process:
        1. Hide calculator and solver interfaces
        2. Clear any existing matrix inputs
        3. Reset result display
        4. Clear error messages
        5. Show matrix frame
        
        Cleanup Operations:
        - Clear calculator display
        - Reset solver fields
        - Clear matrix inputs
        - Reset error states
        """
        # Clean up calculator
        self.calc_frame.grid_remove()
        self.calc_entry.delete(0, tk.END)
        
        # Clean up solver
        self.solver_frame.grid_remove()
        self.solver_entry.delete(0, tk.END)
        self.solver_output.delete(1.0, tk.END)
        
        # Clean up matrix
        if hasattr(self, 'matrix_result_display'):
            self.matrix_result_display.config(state='normal')
            self.matrix_result_display.delete(1.0, tk.END)
            self.matrix_result_display.config(state='disabled')
            
        if hasattr(self, 'matrix_a_input'):
            self.matrix_a_input.delete(1.0, tk.END)
            
        if hasattr(self, 'matrix_b_input'):
            self.matrix_b_input.delete(1.0, tk.END)
            
        if hasattr(self, 'matrix_error_label'):
            self.matrix_error_label.config(text="")
        
        # Show matrix frame
        self.matrix_frame.grid()
        
    def show_custom_matrix_input(self):
        """Show the custom matrix input interface."""
        self.custom_matrix_frame.grid()
        
    def hide_custom_matrix_input(self):
        """Hide the custom matrix input interface and clear its contents."""
        self.custom_matrix_frame.grid_remove()
        self.matrix_a_custom.delete(1.0, tk.END)
        self.matrix_b_custom.delete(1.0, tk.END)
        
    def get_custom_matrix_input(self) -> tuple:
        """Get the custom matrix input values.
        
        Returns:
            tuple: (matrix_a_text, matrix_b_text) containing the raw text input for both matrices
        """
        matrix_a_text = self.matrix_a_custom.get(1.0, tk.END).strip()
        matrix_b_text = self.matrix_b_custom.get(1.0, tk.END).strip()
        return matrix_a_text, matrix_b_text
        
    def get_calc_entry(self) -> str:
        """Get the current calculator display text.
        
        Returns:
            str: Current calculator entry text
        """
        return self.calc_entry.get()
        
    def get_solver_entry(self) -> str:
        """Get the current equation from the solver entry field.
        
        Returns:
            str: The current equation text
        """
        return self.solver_entry.get()
        
    def set_base_displays(self, values: dict):
        """Update all base conversion displays.
        
        Updates the display values for all number bases
        (BIN, OCT, DEC, HEX) simultaneously.
        
        Args:
            values: Dictionary with base codes as keys (BIN, OCT, DEC, HEX)
                   and their display values
        """
        for base_code, value in values.items():
            if base_code in self.base_displays:
                self.base_displays[base_code].config(text=value)
    
    def set_calc_display(self, text: str):
        """Set the calculator main display text.
        
        Args:
            text: Text to display in calculator entry
        """
        self.calc_entry.delete(0, tk.END)
        self.calc_entry.insert(0, text)
        
    def set_solver_output(self, text: str):
        """Set the solver output text with proper formatting.
        
        Args:
            text: The solution text to display, either as a string or list of lines
            
        Format Features:
        - Adds spacing around section headers
        - Properly indents solution steps
        - Maintains consistent formatting
        - Handles both string and list inputs
        """
        self.solver_output.delete(1.0, tk.END)
        
        # If text is a string (from older code), split it into lines
        if isinstance(text, str):
            lines = text.split('\n')
        else:
            lines = text
            
        # Insert each line with proper formatting
        for line in lines:
            # Add extra newline before section headers
            if line.startswith('─' * 40):
                self.solver_output.insert(tk.END, '\n')
            
            # Insert the line
            self.solver_output.insert(tk.END, line + '\n')
            
            # Add extra spacing after section headers and between solutions
            if line.startswith('─' * 40) or line.strip() == '':
                self.solver_output.insert(tk.END, '\n')

    def get_matrix_dimensions(self) -> tuple:
        """Get the dimensions for both matrices from the input fields.
        
        Returns:
            tuple: ((rows_a, cols_a), (rows_b, cols_b)) containing dimensions for both matrices
        """
        try:
            matrix_a_dims = (int(self.matrix_a_rows.get()), int(self.matrix_a_cols.get()))
            matrix_b_dims = (int(self.matrix_b_rows.get()), int(self.matrix_b_cols.get()))
            return matrix_a_dims, matrix_b_dims
        except ValueError:
            return None
            
    def create_matrix_entries(self, matrix_a_dims: tuple, matrix_b_dims: tuple):
        """Create entry widgets for both matrices based on given dimensions."""
        # Clear existing entries
        for widget in self.matrix_a_frame.winfo_children():
            widget.destroy()
        for widget in self.matrix_b_frame.winfo_children():
            widget.destroy()
        
        self.matrix_a_entries = []
        self.matrix_b_entries = []
        
        # Create Matrix A entries
        rows_a, cols_a = matrix_a_dims
        for i in range(rows_a):
            row_entries = []
            for j in range(cols_a):
                entry = ttk.Entry(self.matrix_a_frame, width=8)
                entry.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.matrix_a_entries.append(row_entries)
        
        # Create Matrix B entries
        rows_b, cols_b = matrix_b_dims
        for i in range(rows_b):
            row_entries = []
            for j in range(cols_b):
                entry = ttk.Entry(self.matrix_b_frame, width=8)
                entry.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.matrix_b_entries.append(row_entries)
                
    def get_matrix_values(self) -> tuple:
        """Get and validate the values from both matrix inputs.
        
        Process:
        1. Retrieve raw text from both matrix inputs
        2. Validate input format
        3. Parse matrix structure
        4. Check matrix dimensions
        
        Returns:
            tuple: (matrix_a, matrix_b) where each matrix is a string in the format [a,b,c; d,e,f],
                  or None if the input is invalid
                  
        Error Handling:
        - Empty input validation
        - Format validation
        - Dimension checking
        - Numeric content validation
        """
        try:
            # Get raw text from both inputs
            matrix_a_text = self.matrix_a_input.get("1.0", tk.END).strip()
            matrix_b_text = self.matrix_b_input.get("1.0", tk.END).strip()
            
            # Check if inputs are empty
            if not matrix_a_text or not matrix_b_text:
                raise ValueError("Please enter both matrices")
            
            # Parse both matrices to ensure they're in the correct format
            matrix_a = self.parse_matrix_input(matrix_a_text)
            matrix_b = self.parse_matrix_input(matrix_b_text)
            
            return matrix_a, matrix_b
            
        except ValueError as e:
            self.show_matrix_error(str(e))
            return None

    def format_matrix_input(self, text: str) -> str:
        """Format raw matrix input text into standardized format.
        
        Converts various input formats into the standard [a,b,c; d,e,f] format.
        Handles multiple input styles:
        - Space-separated values
        - Comma-separated values
        - Mixed format
        - Multi-line input
        
        Args:
            text: Raw matrix input text
            
        Returns:
            str: Formatted matrix text in [a,b,c; d,e,f] format
            
        Raises:
            ValueError: If input format is invalid or inconsistent
        """
        # Split into rows (assuming rows are separated by newlines)
        rows = [row.strip() for row in text.split('\n') if row.strip()]
        
        if not rows:
            raise ValueError("Matrix cannot be empty")
        
        # Process each row: split by whitespace or commas and join with commas
        processed_rows = []
        first_row_length = None
        
        for i, row in enumerate(rows):
            # Split by both whitespace and commas
            elements = [elem.strip() for elem in row.replace(',', ' ').split() if elem.strip()]
            
            # Validate row length
            if first_row_length is None:
                first_row_length = len(elements)
            elif len(elements) != first_row_length:
                raise ValueError(f"Row {i+1} has different number of elements than first row")
                
            if not elements:
                raise ValueError(f"Row {i+1} is empty")
                
            processed_rows.append(','.join(elements))
        
        # Join rows with semicolons and wrap in brackets
        return '[' + '; '.join(processed_rows) + ']'

    def parse_matrix_input(self, matrix_text: str) -> str:
        """Parse and validate a matrix from text input.
        
        Validates and standardizes matrix input format.
        Supports:
        - Numeric values
        - Symbolic elements
        - Mixed content
        - Various delimiters
        
        Args:
            matrix_text: String containing the matrix in specified format
            
        Returns:
            str: The matrix text in correct format [a,b,c; d,e,f; g,h,i]
            
        Raises:
            ValueError: If the input format is invalid
        """
        try:
            # If the input is already in the correct format, return it
            if matrix_text.startswith('[') and matrix_text.endswith(']'):
                # Validate that it can be parsed
                self.matrix_model.parse_matrix_input(matrix_text)
                return matrix_text
                
            # Otherwise, format it
            return self.format_matrix_input(matrix_text)
        except ValueError as e:
            raise ValueError(str(e))

    def display_matrix_result(self, result: dict):
        """Display the matrix operation result.
        
        Handles various result formats and provides proper formatting
        for display in the result area.
        
        Args:
            result: Dictionary containing the matrix result information
                   or error message
                   
        Display Features:
        - Formatted matrix output
        - Error message handling
        - Clear visual presentation
        - Read-only result area
        """
        self.matrix_result_display.config(state='normal')  # Enable editing temporarily
        
        if not result:
            self.matrix_result_display.delete(1.0, tk.END)
            self.matrix_result_display.insert(tk.END, "Invalid operation or matrices")
            self.matrix_result_display.config(state='disabled')
            return
            
        try:
            # If result is a dictionary with formatted output, use it directly
            if isinstance(result, dict) and 'formatted' in result:
                formatted_output = result['formatted']
            # If result is a list (matrix), format it
            elif isinstance(result, list):
                formatted_output = self.matrix_model.format_matrix(result)
            else:
                formatted_output = str(result)
            
            # Display the formatted matrix
            self.matrix_result_display.delete(1.0, tk.END)
            self.matrix_result_display.insert(tk.END, formatted_output)
            
        except Exception as e:
            self.matrix_result_display.delete(1.0, tk.END)
            self.matrix_result_display.insert(tk.END, f"Error formatting result: {str(e)}")
            
        self.matrix_result_display.config(state='disabled')  # Make read-only again
        
    def show_matrix_error(self, message: str):
        """Display an error message in the matrix interface.
        
        Shows error both in the result area and dedicated error label
        for maximum visibility.
        
        Args:
            message: Error message to display
            
        Display Locations:
        - Main result area (with error prefix)
        - Dedicated error label
        - Proper error styling
        """
        self.matrix_result_display.config(state='normal')  # Enable editing temporarily
        self.matrix_result_display.delete(1.0, tk.END)
        self.matrix_result_display.insert(tk.END, f"Error: {message}")
        self.matrix_result_display.config(state='disabled')  # Make read-only again
        
        # Also update the error label
        self.matrix_error_label.config(text=message)