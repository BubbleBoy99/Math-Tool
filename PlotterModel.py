import sympy as sp  # Symbolic mathematics
import numpy as np  # Numerical computations
import matplotlib.pyplot as plt  # Plotting
from typing import Dict, List, Tuple, Any, Optional
from ModelUtils import add_multiplication, serialize_plot, deserialize_plot, FUNCTIONS

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
        self.functions = FUNCTIONS
        self._plot_styles = {
            'default': {'color': 'blue', 'linewidth': 1.5},
            'solution': {'color': 'red', 'marker': 'o', 'markersize': 8},
            'grid': {'alpha': 0.3, 'linestyle': '--'},
            'axis': {'color': 'black', 'linestyle': '-', 'alpha': 0.3}
        }
        self._figure_size = (10, 6)
        self._plot_points = 1000
        self._value_limit = 1e6  # Limit for y values to avoid plotting huge numbers


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
            left = add_multiplication(left.strip())
            right = add_multiplication(right.strip())
            
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