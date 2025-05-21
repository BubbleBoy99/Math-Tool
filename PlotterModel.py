import sympy as sp  # Symbolic mathematics
import numpy as np  # Numerical computations
import matplotlib.pyplot as plt  # Plotting
from typing import Dict, List, Tuple, Any, Optional

class PlotterModel:
    """A model class for plotting mathematical functions and equations.
    
    This class serves as the visualization engine for mathematical expressions,
    providing capabilities to plot functions, equations, and their solutions.
    It integrates SymPy for symbolic mathematics and Matplotlib for high-quality
    plotting.
    
    Key Features:
    - Function and equation plotting
    - Support for various mathematical functions
    - Automatic axis scaling and grid options
    - Solution point visualization
    - Customizable plot styles
    - Error handling for undefined regions
    
    Dependencies:
    - SymPy: For symbolic mathematics
    - NumPy: For numerical computations
    - Matplotlib: For plotting
    
    Integration:
    - Works with SolverModel for visualizing solutions
    - Complements CalculatorModel for function visualization
    - Supports MatrixModel for visualizing matrix transformations
    """

    def __init__(self):
        """Initialize the plotter with supported mathematical functions and plot styles.
        
        Sets up:
        1. Mathematical Functions Dictionary:
           - Trigonometric functions (sin, cos, tan)
           - Inverse trigonometric functions (asin, acos, atan)
           - Reciprocal functions (cot, sec, csc)
           - Logarithmic and exponential functions (log, ln, exp)
           - Other functions (sqrt, abs)
           
        2. Plot Style Configurations:
           - Default style for function curves
           - Special style for solution points
           - Grid style for background
           - Axis style for coordinate system
           
        3. Plot Parameters:
           - Figure size for consistent display
           - Number of plot points for smooth curves
           - Value limits to handle infinities
        """
        self.functions = {
            'sin': sp.sin,  # SymPy sine
            'cos': sp.cos,  # SymPy cosine
            'tan': sp.tan,  # SymPy tangent
            'cot': lambda x: 1/sp.tan(x),  # Cotangent as 1/tan
            'sec': lambda x: 1/sp.cos(x),  # Secant as 1/cos
            'csc': lambda x: 1/sp.sin(x),  # Cosecant as 1/sin
            'log': sp.log,  # SymPy logarithm
            'ln': sp.log,   # Natural logarithm (alias)
            'exp': sp.exp,  # Exponential
            'sqrt': sp.sqrt,  # Square root
            'abs': abs,  # Absolute value
            'asin': sp.asin,  # Inverse sine
            'acos': sp.acos,  # Inverse cosine
            'atan': sp.atan   # Inverse tangent
        }
        self._plot_styles = {
            'default': {'color': 'blue', 'linewidth': 1.5},
            'solution': {'color': 'red', 'marker': 'o', 'markersize': 8},
            'grid': {'alpha': 0.3, 'linestyle': '--'},
            'axis': {'color': 'black', 'linestyle': '-', 'alpha': 0.3}
        }
        self._figure_size = (10, 6)
        self._plot_points = 1000
        self._value_limit = 1e6  # Limit for y values to avoid plotting huge numbers

    def serialize_plot(self, equation: str, message: str) -> Dict[str, str]:
        """Serialize plot information for storage or transmission.
        
        Used for:
        - Saving plot configurations
        - Transmitting plot data between components
        - Logging plot history
        
        Args:
            equation: The mathematical expression that was plotted
            message: Status or description message about the plot
            
        Returns:
            Dictionary containing:
            - type: "plot"
            - equation: Original expression
            - message: Status message
        """
        return {
            "type": "plot",
            "equation": equation,
            "message": message
        }

    def deserialize_plot(self, data: Dict[str, Any]) -> Tuple[str, str]:
        """Deserialize plot information from storage or transmission.
        
        Used for:
        - Loading saved plot configurations
        - Reconstructing plot history
        - Importing plot data
        
        Args:
            data: Dictionary containing serialized plot data
            
        Returns:
            Tuple containing:
            - Original expression string
            - Status message
            
        Raises:
            ValueError: If data format is invalid or missing required fields
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid data format: expected dictionary")
            
        if data.get("type") != "plot":
            raise ValueError("Invalid plot data: wrong type")
            
        required_fields = ["equation", "message"]
        if not all(field in data for field in required_fields):
            raise ValueError(f"Invalid plot data: missing fields {[f for f in required_fields if f not in data]}")
            
        return data["equation"], data["message"]

    def add_multiplication(self, expr: str) -> str:
        """Add implicit multiplication symbols to expression.
        
        This method handles cases where multiplication is implied but not explicitly written:
        - Between numbers and variables (2x → 2*x)
        - Between variables (xy → x*y)
        - Before functions (2sin(x) → 2*sin(x))
        - Before and after parentheses (2(x+1) → 2*(x+1))
        
        The method carefully preserves:
        - Function calls and their arguments
        - Operator precedence
        - Negative numbers
        - Decimal points
        
        Args:
            expr: Mathematical expression with implicit multiplication
            
        Returns:
            Expression with explicit multiplication symbols
            
        Raises:
            ValueError: If the expression contains invalid characters or syntax
        """
        if not expr:
            return expr
            
        result = []
        tokens = []
        i = 0
        
        # Loop to tokenize the input expression character by character
        while i < len(expr):
            # Skip whitespace
            if expr[i].isspace():
                i += 1
                continue
            # Check for functions
            found_func = False
            for func in sorted(self.functions.keys(), key=len, reverse=True):
                # Loop through all supported function names, longest first, to match at current position
                if expr[i:].startswith(func):
                    # For functions, we need to capture the entire function call including its argument
                    start_idx = i
                    i += len(func)
                    # Skip whitespace between function name and opening parenthesis
                    while i < len(expr) and expr[i].isspace():
                        i += 1
                    if i < len(expr) and expr[i] == '(':  # Check for function call
                        paren_count = 1
                        i += 1
                        while i < len(expr) and paren_count > 0:
                            # Loop to find the matching closing parenthesis for the function argument
                            if expr[i] == '(':  # Increase count for nested parenthesis
                                paren_count += 1
                            elif expr[i] == ')':  # Decrease count for closing parenthesis
                                paren_count -= 1
                            i += 1
                        # Get the entire function call as one token
                        func_call = expr[start_idx:i]
                        tokens.append(('func_call', func_call))
                        found_func = True
                        break
                    else:
                        # If there's no opening parenthesis, just add the function name
                        tokens.append(('func', func))
                        found_func = True
                        break
            if found_func:
                continue
            # Check for numbers (including decimals and negative signs)
            if expr[i].isdigit() or (expr[i] == '-' and i + 1 < len(expr) and expr[i + 1].isdigit()):
                num = expr[i]
                i += 1
                while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                    # Loop to collect all digits and decimal points for a number
                    num += expr[i]
                    i += 1
                tokens.append(('number', num))
                continue
            # Check for variables
            if expr[i].isalpha():
                var = expr[i]
                i += 1
                while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                    # Loop to collect all alphanumeric characters and underscores for a variable name
                    var += expr[i]
                    i += 1
                if var not in self.functions:
                    tokens.append(('var', var))
                continue
            # Operators and parentheses
            if expr[i] in '+-*/()^=':
                tokens.append(('op', expr[i]))
                i += 1
                continue
            raise ValueError(f"Invalid character in expression: {expr[i]}")
        
        # Process tokens to add multiplication symbols
        for i, token in enumerate(tokens):
            # Loop through all tokens to reconstruct the expression and insert '*' where needed
            curr_type, curr_val = token
            # For function calls, we need to process the arguments
            if curr_type == 'func_call':
                # Extract the function name and arguments
                func_name = curr_val[:curr_val.index('(')]
                args = curr_val[curr_val.index('(') + 1:-1]
                # Process the arguments recursively
                processed_args = self.add_multiplication(args)
                # Reconstruct the function call
                result.append(f"{func_name}({processed_args})")
            else:
                result.append(curr_val)
            # Add multiplication symbols where needed
            if i < len(tokens) - 1:
                next_type, next_val = tokens[i + 1]
                needs_mult = False
                # Check for cases where multiplication is implied between current and next token
                if curr_type == 'number' and next_type in ('var', 'func', 'func_call') or (next_type == 'op' and next_val == '('):
                    needs_mult = True
                elif curr_type == 'op' and curr_val == ')' and next_type in ('number', 'var', 'func', 'func_call'):
                    needs_mult = True
                elif curr_type == 'var' and (next_type in ('number', 'func', 'func_call') or (next_type == 'op' and next_val == '(')):
                    needs_mult = True
                elif curr_type == 'var' and next_type == 'var':
                    needs_mult = True
                if needs_mult:
                    result.append('*')
        
        return ''.join(result)

    def plot_equation(self, equation_str: str, x_range: Tuple[float, float] = (-10, 10),
                     y_range: Optional[Tuple[float, float]] = None,
                     show_grid: bool = True,
                     show_solutions: bool = True) -> str:
        """Plot the equation showing both sides of the equality.
        
        This method:
        1. Parses and validates the equation
        2. Converts to numerical functions
        3. Generates plot points
        4. Handles undefined regions
        5. Creates the visualization
        6. Adds solutions if requested
        
        Features:
        - Automatic range adjustment
        - Grid display option
        - Solution point highlighting
        - Axis display
        - Legend generation
        
        Error Handling:
        - Skips undefined points
        - Limits extreme values
        - Handles complex results
        - Manages parsing errors
        
        Args:
            equation_str: The equation to plot (must contain '=')
            x_range: Domain for plotting as (min_x, max_x)
            y_range: Optional range for y-axis as (min_y, max_y)
            show_grid: Whether to display the coordinate grid
            show_solutions: Whether to highlight intersection points
            
        Returns:
            Status message describing the plot result
            
        Raises:
            ValueError: If equation is invalid or cannot be plotted
        """
        try:
            x = sp.Symbol('x')  # Create SymPy symbol for x
            
            # Split and process equation
            if '=' not in equation_str:
                # Check if the equation contains an equals sign
                raise ValueError("Invalid equation: missing equals sign")
                
            left, right = equation_str.split('=')
            left = self.add_multiplication(left.strip())
            right = self.add_multiplication(right.strip())
            
            # Create sympy expressions
            try:
                left_expr = sp.sympify(left, locals=self.functions)
                right_expr = sp.sympify(right, locals=self.functions)
            except sp.SympifyError as e:
                # If parsing fails, raise an error
                raise ValueError(f"Error parsing equation: {e}")
            
            # Create lambda functions for numerical evaluation
            f_left = sp.lambdify(x, left_expr, modules=['numpy', {'log': np.log, 'ln': np.log}])
            f_right = sp.lambdify(x, right_expr, modules=['numpy', {'log': np.log, 'ln': np.log}])
            
            # Generate x values
            x_vals = np.linspace(x_range[0], x_range[1], self._plot_points)
            
            # Calculate y values with error handling
            y_left = []
            y_right = []
            
            for x_val in x_vals:
                # Loop through all x values to compute corresponding y values for both sides
                try:
                    y_l = float(f_left(x_val))
                    y_r = float(f_right(x_val))
                    if -self._value_limit < y_l < self._value_limit and -self._value_limit < y_r < self._value_limit:
                        # If both y values are within allowed range, append them
                        y_left.append(y_l)
                        y_right.append(y_r)
                    else:
                        # If y values are too large/small, append NaN
                        y_left.append(np.nan)
                        y_right.append(np.nan)
                except:
                    # If evaluation fails, append NaN
                    y_left.append(np.nan)
                    y_right.append(np.nan)
            
            # Create the plot
            plt.figure(figsize=self._figure_size)
            
            # Plot both sides of the equation
            plt.plot(x_vals, y_left, label=f'y = {left}', **self._plot_styles['default'])
            plt.plot(x_vals, y_right, label=f'y = {right}', **self._plot_styles['default'])
            
            # Add intersection points if requested
            if show_solutions:
                # If solution points should be shown, solve for intersections
                try:
                    solutions = sp.solve(left_expr - right_expr, x)
                    real_solutions = [sol for sol in solutions if sol.is_real]
                    
                    for sol in real_solutions:
                        # Loop through all real solutions to plot them
                        try:
                            x_val = float(sol.evalf())
                            if x_range[0] <= x_val <= x_range[1]:
                                # If solution is within x range, plot it
                                y_val = float(f_left(x_val))
                                plt.plot([x_val], [y_val], label=f'x = {x_val:.4f}', **self._plot_styles['solution'])
                        except:
                            # If plotting a solution fails, skip it
                            continue
                except Exception as e:
                    # If solving for intersections fails, print warning
                    print(f"Warning: Could not find intersection points: {e}")
            
            # Add grid if requested
            if show_grid:
                # If grid should be shown, add it to the plot
                plt.grid(True, **self._plot_styles['grid'])
            
            # Add axes
            plt.axhline(y=0, **self._plot_styles['axis'])
            plt.axvline(x=0, **self._plot_styles['axis'])
            
            # Add labels and title
            plt.legend()
            plt.title(f'Plot of {equation_str}')
            plt.xlabel('x')
            plt.ylabel('y')
            
            # Set y-range if provided, otherwise auto-adjust
            if y_range:
                # If y_range is specified, set it
                plt.ylim(y_range)
            else:
                # Otherwise, auto-adjust y-limits based on data
                y_min = np.nanmin(y_left + y_right)
                y_max = np.nanmax(y_left + y_right)
                if np.isfinite(y_min) and np.isfinite(y_max):
                    # If y_min and y_max are finite, add margin and set limits
                    margin = (y_max - y_min) * 0.1
                    plt.ylim(y_min - margin, y_max + margin)
            
            plt.show()
            return "Plot generated successfully"
            
        except Exception as e:
            # If any error occurs during plotting, return error message
            return f"Error plotting equation: {str(e)}"

    def plot_function(self, function_str: str, x_range: Tuple[float, float] = (-10, 10),
                     y_range: Optional[Tuple[float, float]] = None,
                     show_grid: bool = True) -> str:
        """Plot a single mathematical function.
        
        This is a convenience wrapper around plot_equation that:
        1. Converts the function to an equation (f(x) = y)
        2. Calls plot_equation with appropriate parameters
        3. Disables solution point display
        
        Use this method for:
        - Simple function visualization
        - Quick plotting needs
        - Function behavior analysis
        
        Args:
            function_str: Mathematical function to plot (e.g., 'sin(x)', 'x^2 + 1')
            x_range: Domain for plotting as (min_x, max_x)
            y_range: Optional range for y-axis as (min_y, max_y)
            show_grid: Whether to display the coordinate grid
            
        Returns:
            Status message describing the plot result
            
        Raises:
            ValueError: If function is invalid or cannot be plotted
        """
        return self.plot_equation(f"{function_str}=y", x_range, y_range, show_grid, False) 