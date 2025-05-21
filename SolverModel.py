import sympy as sp  # Symbolic mathematics
import numpy as np  # Numerical computations
import matplotlib.pyplot as plt  # Plotting
import re  # Regular expressions
from typing import Dict, List, Tuple, Any, Optional

class SolverModel:
    """A model class for solving mathematical equations and plotting functions.
    
    This class serves as the advanced mathematical engine for equation solving and function plotting.
    It leverages SymPy for symbolic mathematics and matplotlib for visualization. The solver supports
    a wide range of mathematical operations including trigonometric, logarithmic, and exponential
    functions.
    
    Key Features:
    - Symbolic equation solving with step-by-step solutions
    - Support for complex mathematical functions
    - Implicit multiplication handling
    - Real and complex number solutions
    - Solution verification
    - Function plotting capabilities
    - Serialization for storage and transmission
    
    Dependencies:
    - SymPy: For symbolic mathematics
    - NumPy: For numerical computations
    - Matplotlib: For function plotting
    """

    def __init__(self):
        """Initialize the solver with supported mathematical functions and plotting styles.
        
        Sets up:
        1. Mathematical Functions Dictionary:
           - Basic trigonometric functions (sin, cos, tan)
           - Inverse trigonometric functions (asin, acos, atan)
           - Reciprocal trigonometric functions (cot, sec, csc)
           - Logarithmic and exponential functions (log, ln, exp)
           - Other functions (sqrt, abs)
           
        2. Plot Style Configurations:
           - Default style for function plots
           - Special style for solution points
           - Grid style for plot backgrounds
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
            'grid': {'alpha': 0.3, 'linestyle': '--'}
        }

    def serialize_solution(self, equation: str, steps: List[str]) -> Dict[str, Any]:
        """Serialize a solution for storage or transmission.
        
        Used for:
        - Saving solution history
        - Transmitting solutions between components
        - Exporting solutions to other formats
        
        Args:
            equation: The original equation that was solved
            steps: List of solution steps with explanations
            
        Returns:
            Dictionary containing:
            - type: "solution"
            - equation: Original equation string
            - steps: List of solution steps
        """
        # Ensure steps is a list
        if isinstance(steps, str):
            steps = steps.split('\n')
        elif not isinstance(steps, list):
            steps = [str(steps)]
            
        return {
            "type": "solution",
            "equation": equation,
            "steps": steps
        }

    def deserialize_solution(self, data: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Deserialize a solution from storage or transmission.
        
        Used for:
        - Loading saved solutions
        - Reconstructing solution history
        - Importing solutions from other sources
        
        Args:
            data: Dictionary containing serialized solution data
            
        Returns:
            Tuple containing:
            - Original equation string
            - List of solution steps
            
        Raises:
            ValueError: If data format is invalid or missing required fields
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid data format: expected dictionary")
            
        if data.get("type") != "solution":
            raise ValueError("Invalid solution data: wrong type")
            
        required_fields = ["equation", "steps"]
        if not all(field in data for field in required_fields):
            raise ValueError(f"Invalid solution data: missing fields {[f for f in required_fields if f not in data]}")
            
        if not isinstance(data["steps"], list):
            raise ValueError("Invalid solution data: steps must be a list")
            
        return data["equation"], data["steps"]

    def serialize_plot(self, equation: str, message: str) -> Dict[str, str]:
        """Serialize plot information for storage or transmission.
        
        Used for:
        - Saving plot configurations
        - Transmitting plot data between components
        - Documenting plot history
        
        Args:
            equation: The equation or function that was plotted
            message: Status or description message about the plot
            
        Returns:
            Dictionary containing plot metadata and configuration
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
            Tuple of (equation, message) describing the plot
            
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
        - Before parentheses (2(x+1) → 2*(x+1))
        - After parentheses ((x+1)2 → (x+1)*2)
        - Before functions (2sin(x) → 2*sin(x))
        
        The method carefully preserves function calls and their arguments while
        adding multiplication symbols where needed.
        
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

    def format_expression(self, expr) -> str:
        """Format a SymPy expression to use ^ for powers and look more like handwritten math.
        
        This method improves readability of mathematical expressions by:
        - Converting ** to ^ for exponents
        - Preserving function names and parentheses
        - Maintaining operator precedence
        
        Args:
            expr: SymPy expression to format
            
        Returns:
            Formatted string representation that's more readable
        """
        # Convert the expression to string
        expr_str = str(expr)
        
        # Replace ** with ^
        expr_str = expr_str.replace('**', '^')
        
        return expr_str

    def solve_equation(self, equation_str: str) -> str:
        """Solve an equation and provide step-by-step solution.
        
        This is the main solving method that:
        1. Parses and validates the equation
        2. Converts to standard form
        3. Applies algebraic transformations
        4. Finds solutions (real and complex)
        5. Verifies solutions
        6. Provides numerical approximations
        
        The solution process includes:
        - Equation rearrangement
        - Expression expansion
        - Factoring when possible
        - Finding real and complex solutions
        - Solution verification
        - Numerical approximations
        
        Special handling for:
        - Trigonometric equations
        - Logarithmic equations
        - Polynomial equations
        - Systems with multiple solutions
        
        Args:
            equation_str: String representation of the equation (e.g., "x^2 + 2x = 5")
            
        Returns:
            List of strings containing the step-by-step solution process
            
        Raises:
            ValueError: For invalid equations or when solutions cannot be found
        """
        print(f"[TRACE] SolverModel.solve_equation called with: {equation_str}")
        try:
            x = sp.Symbol('x')
            
            # First, validate the equation format
            if '=' not in equation_str:
                # Check if the equation contains an equals sign
                raise ValueError("Invalid equation: missing equals sign")
            
            # Split and process both sides
            left, right = equation_str.split('=')
            left = self.add_multiplication(left.strip())
            right = self.add_multiplication(right.strip())
            
            # Debug output
            print(f"Processed left side: {left}")
            print(f"Processed right side: {right}")
            
            try:
                # Create a dictionary of local variables for sympy
                locals_dict = {**self.functions, 'x': x}
                
                # Loop through all function names to replace standalone names with actual functions
                for func_name, func in self.functions.items():
                    left = re.sub(r'\b' + func_name + r'\b(?!\()', str(func), left)
                    right = re.sub(r'\b' + func_name + r'\b(?!\()', str(func), right)
                
                # Convert the expressions to SymPy objects
                left_expr = sp.parse_expr(left, local_dict=locals_dict, transformations='all')
                right_expr = sp.parse_expr(right, local_dict=locals_dict, transformations='all')
            except Exception as e:
                raise ValueError(f"Error parsing equation: {e}\nProcessed equation: {left} = {right}")
            
            # Start building solution steps
            steps = []
            
            # Section: Problem Statement
            steps.append("─" * 40)
            steps.append("PROBLEM")
            steps.append("─" * 40)
            steps.append(f"Solve the equation:")
            steps.append(f"{equation_str}")
            steps.append("")
            
            # Section: Solution Steps
            steps.append("─" * 40)
            steps.append("SOLUTION STEPS")
            steps.append("─" * 40)
            
            # Move everything to left side
            equation = left_expr - right_expr
            steps.append("1. Rearrange to standard form:")
            steps.append(f"   {self.format_expression(equation)} = 0")
            steps.append("")
            
            step_number = 2
            
            # Expand if possible
            expanded = sp.expand(equation)
            if expanded != equation:
                # If the expanded form is different, add an expansion step
                steps.append(f"{step_number}. Expand the expression:")
                steps.append(f"   {self.format_expression(expanded)} = 0")
                steps.append("")
                equation = expanded
                step_number += 1
            
            # Try to factor if it's a polynomial
            try:
                factored = sp.factor(equation)
                if factored != equation:
                    # If factoring is possible, add a factoring step
                    steps.append(f"{step_number}. Factor the expression:")
                    steps.append(f"   {self.format_expression(factored)} = 0")
                    steps.append("")
                    equation = factored
                    step_number += 1
            except Exception:
                # If factoring fails, continue with unfactored form
                pass
            
            # Solve the equation
            try:
                solutions = sp.solve(equation, x)
                
                if not solutions:
                    # If no solutions are found, note it and return
                    steps.append("No solutions found")
                    print(f"[TRACE] SolverModel.solve_equation returning: {steps}")
                    return steps
                
                # Separate real and complex solutions
                real_sols = []
                complex_sols = []
                
                for sol in solutions:
                    # Loop through all solutions to classify as real or complex
                    try:
                        if sol.is_real:
                            # If the solution is real, add to real_sols
                            real_sols.append(sol)
                        else:
                            # Otherwise, add to complex_sols
                            complex_sols.append(sol)
                    except:
                        # If we can't determine if it's real, try to evaluate it
                        try:
                            float_val = complex(sol.evalf())
                            if abs(float_val.imag) < 1e-10:
                                # If imaginary part is negligible, treat as real
                                real_sols.append(sol)
                            else:
                                # Otherwise, treat as complex
                                complex_sols.append(sol)
                        except:
                            # If we can't evaluate it, assume it's complex
                            complex_sols.append(sol)
                
                # Section: Solutions
                steps.append("─" * 40)
                steps.append("SOLUTIONS")
                steps.append("─" * 40)
                
                # Process real solutions
                if real_sols:
                    if len(real_sols) == 1:
                        # If there is one real solution, note it
                        steps.append("Found 1 real solution:")
                    else:
                        # Otherwise, note the number of real solutions
                        steps.append(f"Found {len(real_sols)} real solutions:")
                    steps.append("")
                    
                    for i, sol in enumerate(real_sols, 1):
                        # Loop through all real solutions to display and approximate
                        try:
                            simple_sol = sp.simplify(sol)
                            steps.append(f"x{i} = {self.format_expression(simple_sol)}")
                            
                            # Always show numerical approximation for real solutions
                            approx = sp.N(simple_sol, 10)
                            steps.append(f"   ≈ {approx}")
                        except Exception as e:
                            steps.append(f"Error simplifying solution {i}: {e}")
                        steps.append("")
                
                # Process complex solutions
                if complex_sols:
                    if len(complex_sols) == 1:
                        # If there is one complex solution, note it
                        steps.append("Found 1 complex solution:")
                    else:
                        # Otherwise, note the number of complex solutions
                        steps.append(f"Found {len(complex_sols)} complex solutions:")
                    steps.append("")
                    
                    for i, sol in enumerate(complex_sols, 1):
                        # Loop through all complex solutions to display and approximate
                        try:
                            # Try to simplify the solution
                            simple_sol = sp.simplify(sol)
                            steps.append(f"x{i} = {self.format_expression(simple_sol)}")
                            
                            # Add numerical approximation for complex solutions
                            approx = sp.N(simple_sol, 10)
                            steps.append(f"   ≈ {approx}")
                            steps.append("")
                        except Exception as e:
                            steps.append(f"Error simplifying complex solution {i}: {e}")
                            steps.append("")
                
                # Section: Verification
                steps.append("─" * 40)
                steps.append("VERIFICATION")
                steps.append("─" * 40)
                
                all_verified = True
                for i, sol in enumerate(solutions, 1):
                    # Loop through all solutions to verify them
                    try:
                        verification = equation.subs(x, sol)
                        if abs(complex(verification.evalf())) < 1e-10:
                            # If the solution satisfies the equation, mark as verified
                            steps.append(f"✓ x = {self.format_expression(sol)} is verified")
                        else:
                            # Otherwise, mark as possibly inexact
                            steps.append(f"⚠ x = {self.format_expression(sol)} may not be exact")
                            all_verified = False
                    except Exception:
                        # If verification fails, note it
                        steps.append(f"⚠ Could not verify x = {self.format_expression(sol)}")
                        all_verified = False
                
                if all_verified:
                    steps.append("")
                    steps.append("All solutions have been verified.")
                
            except Exception as e:
                steps.append(f"Error solving equation: {e}")
                # Try numerical solving as a fallback
                try:
                    nsolve_results = []
                    for guess in [-10, -1, 0, 1, 10]:
                        # Loop through a set of initial guesses for numerical solving
                        try:
                            sol = sp.nsolve(equation, x, guess, verify=False)
                            if not any(abs(complex(s - sol)) < 1e-10 for s in nsolve_results):
                                # If the solution is not already in the list, add it
                                nsolve_results.append(sol)
                        except:
                            # If nsolve fails for this guess, skip it
                            continue
                    
                    if nsolve_results:
                        steps.append("")
                        steps.append("─" * 40)
                        steps.append("NUMERICAL SOLUTIONS")
                        steps.append("─" * 40)
                        for i, sol in enumerate(nsolve_results, 1):
                            # Loop through all numerical solutions to display them
                            steps.append(f"x{i} ≈ {sol}")
                except:
                    # If numerical solving fails, note it
                    steps.append("Could not find numerical solutions")
            
            print(f"[TRACE] SolverModel.solve_equation returning: {steps}")
            return steps
            
        except Exception as e:
            print(f"[TRACE] SolverModel.solve_equation exception: {e}")
            raise