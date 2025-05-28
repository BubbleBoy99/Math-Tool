import sympy as sp  # Symbolic mathematics
import numpy as np  # Numerical computations
import matplotlib.pyplot as plt  # Plotting
import re  # Regular expressions
from typing import Dict, List, Tuple, Any, Optional
from ModelUtils import add_multiplication, serialize_plot, deserialize_plot, FUNCTIONS, format_expression

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
        self.functions = FUNCTIONS
        self._plot_styles = {
            'default': {'color': 'blue', 'linewidth': 1.5},
            'solution': {'color': 'red', 'marker': 'o', 'markersize': 8},
            'grid': {'alpha': 0.3, 'linestyle': '--'}
        }


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
            left = add_multiplication(left.strip())
            right = add_multiplication(right.strip())
            
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
            steps.append(f"   {format_expression(equation)} = 0")
            steps.append("")
            
            step_number = 2
            
            # Expand if possible
            expanded = sp.expand(equation)
            if expanded != equation:
                # If the expanded form is different, add an expansion step
                steps.append(f"{step_number}. Expand the expression:")
                steps.append(f"   {format_expression(expanded)} = 0")
                steps.append("")
                equation = expanded
                step_number += 1
            
            # Try to factor if it's a polynomial
            try:
                factored = sp.factor(equation)
                if factored != equation:
                    # If factoring is possible, add a factoring step
                    steps.append(f"{step_number}. Factor the expression:")
                    steps.append(f"   {format_expression(factored)} = 0")
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
                            steps.append(f"x{i} = {format_expression(simple_sol)}")
                            
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
                            steps.append(f"x{i} = {format_expression(simple_sol)}")
                            
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
                            steps.append(f"✓ x = {format_expression(sol)} is verified")
                        else:
                            # Otherwise, mark as possibly inexact
                            steps.append(f"⚠ x = {format_expression(sol)} may not be exact")
                            all_verified = False
                    except Exception:
                        # If verification fails, note it
                        steps.append(f"⚠ Could not verify x = {format_expression(sol)}")
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