import numpy as np
from typing import List, Tuple, Dict, Any, Union
import sympy as sp
from sympy import Matrix, Symbol, sympify
from ModelUtils import validate_input, FUNCTIONS

class MatrixModel:
    """A model class for matrix operations and symbolic matrix manipulation.
    
    This class serves as the matrix computation engine, supporting both numeric and symbolic
    matrix operations. It integrates SymPy for symbolic computations and provides a robust
    interface for matrix manipulation, validation, and formatting.
    
    Key Features:
    - Support for both numeric and symbolic matrices
    - Basic matrix operations (addition, subtraction, multiplication)
    - Matrix parsing from text input
    - Symbolic variable management
    - Result simplification and formatting
    - Serialization for storage and transmission
    
    Dependencies:
    - NumPy: For numerical computations
    - SymPy: For symbolic mathematics
    
    Integration:
    - Works alongside SolverModel for equation systems
    - Complements CalculatorModel for advanced mathematical operations
    """
    
    def __init__(self):
        """Initialize the matrix model with symbolic variable management.
        
        Sets up:
        1. Symbol Dictionary:
           - Stores SymPy Symbol objects for variables
           - Pre-initializes common variable names (x, y, z, etc.)
           
        2. Common Variables:
           - Single letters (a-z) for basic variables
           - Common mathematical symbols (m, n, p, etc.)
        """
        # Dictionary to store symbolic variables
        self.symbols = {}
        # Common variable names that might be used
        common_vars = ['x', 'y', 'z', 'a', 'b', 'c', 'd', 'm', 'n', 'p', 'q', 'r', 's', 't']
        for var in common_vars:
            # Loop through all common variable names to create SymPy symbols
            self.symbols[var] = sp.Symbol(var)  # Create SymPy Symbol for each variable
    
    def get_or_create_symbol(self, name: str) -> sp.Symbol:
        """Get an existing symbol or create a new one.
        
        Used for:
        - Managing symbolic variables consistently
        - Avoiding duplicate symbol creation
        - Ensuring symbol reuse across operations
        
        Args:
            name: Name of the symbol to retrieve or create
            
        Returns:
            SymPy Symbol object that can be used in expressions
        """
        if name not in self.symbols:
            # If the symbol does not exist, create a new SymPy Symbol
            self.symbols[name] = sp.Symbol(name)  # Create new SymPy Symbol if not present
        return self.symbols[name]
    
    def parse_element(self, element: str):
        try:
            return sp.sympify(element, locals=FUNCTIONS)
        except Exception:
            return element  # fallback: return as string if cannot parse
    
    def parse_matrix_input(self, matrix_text: str) -> List[List[Any]]:
        """Parse a matrix from text input, supporting both numeric and symbolic elements.
        
        Input Format:
        - Matrix enclosed in square brackets []
        - Rows separated by semicolons ;
        - Elements within rows separated by commas ,
        - Example: [1,2,3; 4,5,6; 7,8,9]
        
        Features:
        - Whitespace tolerance
        - Support for symbolic expressions
        - Automatic type conversion
        - Comprehensive error checking
        
        Args:
            matrix_text: String containing the matrix in specified format
            
        Returns:
            List of lists representing the matrix with appropriate types
            
        Raises:
            ValueError: If the input format is invalid or parsing fails
        """
        if not isinstance(matrix_text, str):
            raise ValueError("Matrix input must be a string")
            
        # Remove whitespace and check basic format
        matrix_text = matrix_text.strip()
        if not (matrix_text.startswith('[') and matrix_text.endswith(']')):
            raise ValueError("Matrix must be enclosed in square brackets []")
            
        # Remove brackets and split into rows
        content = matrix_text[1:-1].strip()
        if not content:
            raise ValueError("Matrix cannot be empty")
            
        # Split into rows and parse
        rows = [row.strip() for row in content.split(';')]
        matrix = []
        
        for row in rows:
            # Loop through each row string to parse its elements
            try:
                elements = [self.parse_element(x.strip()) for x in row.split(',')]
                matrix.append(elements)
            except ValueError as e:
                # If parsing an element fails, raise a detailed error for this row
                raise ValueError(f"Invalid row '{row}': {str(e)}")
            except Exception as e:
                # If any other error occurs, raise a detailed error for this row
                raise ValueError(f"Error parsing row '{row}': {str(e)}")
        
        # Validate matrix structure
        if not matrix:
            # If the matrix is empty after parsing, raise an error
            raise ValueError("Matrix cannot be empty")
            
        row_length = len(matrix[0])
        if not all(len(row) == row_length for row in matrix):
            # If any row has a different number of elements, raise an error
            raise ValueError("All rows must have the same number of elements")
            
        # Convert all elements to SymPy format
        return matrix  # Elements are already parsed as SymPy objects
    def validate_matrix(self, matrix):
        # Check if the input is a list of lists
        if not isinstance(matrix, list) or not all(isinstance(row, list) for row in matrix):
            raise ValueError("Invalid matrix format")
        
        # Check if all rows have the same length
        row_lengths = [len(row) for row in matrix]
        if len(set(row_lengths)) > 1:
            raise ValueError("All rows must have the same length")
        
        return True
    def to_sympy_matrix(self, matrix: List[List[Any]]) -> sp.Matrix:
        """Convert a matrix to SymPy Matrix format for symbolic operations.
        
        Used for:
        - Preparing matrices for symbolic computations
        - Ensuring consistent type handling
        - Enabling advanced matrix operations
        
        Args:
            matrix: List of lists representing the matrix
            
        Returns:
            SymPy Matrix object ready for symbolic computation
        """
        return sp.Matrix(matrix)  # Convert list of lists to SymPy Matrix
    
    def ensure_native_types(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """Convert matrix elements to native Python types while preserving symbolic expressions.
        
        Conversion Rules:
        - Numbers → float
        - Symbolic expressions → preserved as strings
        - None values → 0.0
        - NumPy types → float
        - Strings → float if possible, otherwise preserved
        
        Args:
            matrix: Input matrix with any type of elements
            
        Returns:
            Matrix with elements as native Python types or symbolic expressions
        """
        result = []
        for row in matrix:
            # Loop through each row in the matrix to convert elements to native types
            native_row = []
            for element in row:
                # Loop through each element in the row to convert it
                try:
                    # Handle None
                    if element is None:
                        native_row.append(0.0)
                        continue
                    # Handle SymPy types - preserve symbolic expressions
                    if isinstance(element, (sp.Basic, sp.Expr, sp.Symbol)):
                        try:
                            # Try to evaluate to a number if possible
                            value = element.evalf()  # Evaluate symbolic expression to a number if possible
                            if value.is_number:
                                # If the symbolic value is a number, convert to float
                                native_row.append(float(value))
                            else:
                                # Keep as symbolic expression if it can't be evaluated
                                native_row.append(str(element))
                        except:
                            # If evaluation fails, keep as string representation
                            native_row.append(str(element))
                        continue
                    # Handle numpy types
                    if hasattr(element, 'item'):
                        native_row.append(float(element.item()))  # Convert numpy types to float
                        continue
                    # Handle strings that might be symbolic expressions
                    if isinstance(element, str):
                        try:
                            float_val = float(element)
                            native_row.append(float_val)
                        except ValueError:
                            # If it can't be converted to float, keep as string
                            native_row.append(element)
                        continue
                    # Handle other numeric types
                    native_row.append(float(element))
                except (ValueError, TypeError, AttributeError) as e:
                    # If conversion fails, print warning and keep as string
                    print(f"Warning: Could not convert element {element} to float: {e}")
                    native_row.append(str(element))
            result.append(native_row)
        return result
    
    def add_matrices(self, matrix1: List[List[Any]], matrix2: List[List[Any]]) -> List[List[Any]]:
        print(f"[TRACE] MatrixModel.add_matrices called with:\nmatrix1={matrix1}\nmatrix2={matrix2}")
        # Validate inputs
        self.validate_matrix(matrix1)
        self.validate_matrix(matrix2)
        if len(matrix1) != len(matrix2) or len(matrix1[0]) != len(matrix2[0]):
            raise ValueError("Matrices must have the same dimensions for addition")
        m1 = self.to_sympy_matrix(matrix1)  # Convert to SymPy Matrix
        m2 = self.to_sympy_matrix(matrix2)  # Convert to SymPy Matrix
        result = m1 + m2  # SymPy matrix addition
        result_list = result.tolist()  # Convert SymPy Matrix to list of lists
        simplified = self.simplify_result(result_list)
        final_result = self.ensure_native_types(simplified)
        print(f"[TRACE] MatrixModel.add_matrices result: {final_result}")
        return final_result
    
    def subtract_matrices(self, matrix1: List[List[Any]], matrix2: List[List[Any]]) -> List[List[Any]]:
        print(f"[TRACE] MatrixModel.subtract_matrices called with:\nmatrix1={matrix1}\nmatrix2={matrix2}")
        self.validate_matrix(matrix1)
        self.validate_matrix(matrix2)
        if len(matrix1) != len(matrix2) or len(matrix1[0]) != len(matrix2[0]):
            raise ValueError("Matrices must have the same dimensions for subtraction")
        m1 = self.to_sympy_matrix(matrix1)  # Convert to SymPy Matrix
        m2 = self.to_sympy_matrix(matrix2)  # Convert to SymPy Matrix
        result = m1 - m2  # SymPy matrix subtraction
        result_list = result.tolist()  # Convert SymPy Matrix to list of lists
        simplified = self.simplify_result(result_list)
        final_result = self.ensure_native_types(simplified)
        print(f"[TRACE] MatrixModel.subtract_matrices result: {final_result}")
        return final_result
    
    def multiply_matrices(self, matrix1: List[List[Any]], matrix2: List[List[Any]]) -> List[List[Any]]:
        print(f"[TRACE] MatrixModel.multiply_matrices called with:\nmatrix1={matrix1}\nmatrix2={matrix2}")
        self.validate_matrix(matrix1)
        self.validate_matrix(matrix2)
        if len(matrix1[0]) != len(matrix2):
            raise ValueError("Number of columns in first matrix must equal number of rows in second matrix")
        m1 = self.to_sympy_matrix(matrix1)  # Convert to SymPy Matrix
        m2 = self.to_sympy_matrix(matrix2)  # Convert to SymPy Matrix
        result = m1 * m2  # SymPy matrix multiplication
        result_list = result.tolist()  # Convert SymPy Matrix to list of lists
        simplified = self.simplify_result(result_list)
        final_result = self.ensure_native_types(simplified)
        print(f"[TRACE] MatrixModel.multiply_matrices result: {final_result}")
        return final_result
    
    def serialize_matrix_result(self, result: List[List[Any]]) -> Dict[str, Any]:
        """Serialize a matrix result for storage or transmission.
        
        Output Format:
        - matrix: Raw matrix data
        - formatted: Human-readable string representation
        - dimensions: Row and column counts
        
        Features:
        - Handles both numeric and symbolic elements
        - Provides formatted output for display
        - Includes matrix dimensions
        - Error handling with fallback values
        
        Args:
            result: Matrix to serialize
            
        Returns:
            Dictionary containing serialized matrix data
        """
        try:
            # Convert to native types while preserving symbolic expressions
            processed_matrix = self.ensure_native_types(result)  # Convert to native types
            
            # Create dimensions
            dimensions = {
                "rows": len(processed_matrix),
                "cols": len(processed_matrix[0]) if processed_matrix else 0
            }
            
            # Format the matrix for display
            formatted = "\n".join([
                "  ".join(f"{val:.2f}" if isinstance(val, (int, float)) 
                        else str(val) for val in row)
                for row in processed_matrix
            ])  # Format matrix for display
            
            return {
                "matrix": processed_matrix,
                "formatted": formatted,
                "dimensions": dimensions
            }
            
        except Exception as e:
            print(f"Error in matrix serialization: {e}")
            return {
                "matrix": [[0.0]],
                "formatted": "Error processing matrix",
                "dimensions": {"rows": 1, "cols": 1}
            }
    
    def format_matrix(self, matrix: List[List[Any]], precision: int = 2) -> str:
        """Format a matrix for display with proper alignment and spacing.
        
        Features:
        - Right-aligned columns
        - Consistent spacing
        - Configurable numeric precision
        - Special handling for symbolic expressions
        - Column width optimization
        
        Args:
            matrix: Matrix to format
            precision: Number of decimal places for numeric values
            
        Returns:
            Formatted string representation of the matrix
        """
        # Convert numeric values to formatted strings and keep symbolic elements as is
        formatted_rows = []
        for row in matrix:
            # Loop through each row to format its values
            formatted_row = []
            for val in row:
                # Loop through each value in the row to format it
                if isinstance(val, (int, float)):
                    formatted_row.append(f"{val:.{precision}f}")  # Format float with precision
                elif isinstance(val, (sp.Basic, sp.Expr, sp.Symbol)):
                    # For symbolic expressions, use sympy's string representation
                    try:
                        simplified = sp.simplify(val)  # Simplify symbolic expression
                        formatted_row.append(str(simplified))
                    except:
                        formatted_row.append(str(val))
                else:
                    formatted_row.append(str(val))
            formatted_rows.append(formatted_row)
        
        # Get the maximum width needed for each column
        col_widths = []
        for col in range(len(formatted_rows[0])):
            # Loop through each column index to determine max width
            col_vals = [row[col] for row in formatted_rows]
            col_widths.append(max(len(val) for val in col_vals))
        
        # Build the string representation
        lines = []
        for row in formatted_rows:
            # Format each value in the row with proper width
            formatted_row = [val.rjust(width) for val, width in zip(row, col_widths)]
            lines.append("  ".join(formatted_row))
        
        return "\n".join(lines)
    
    def serialize_operation(self, operation: str, matrix1: List[List[float]], 
                          matrix2: List[List[float]], result: List[List[float]]) -> Dict[str, Any]:
        """Serialize a matrix operation for storage or transmission.
        
        Includes:
        - Operation type
        - Input matrices
        - Result matrix
        - Formatted output for display
        
        Args:
            operation: Name of the operation performed
            matrix1: First input matrix
            matrix2: Second input matrix
            result: Result matrix
            
        Returns:
            Dictionary containing complete operation data
        """
        return {
            "type": "matrix_operation",
            "operation": operation,
            "matrix1": matrix1,
            "matrix2": matrix2,
            "result": result,
            "formatted_output": (
                f"Matrix 1:\n{self.format_matrix(matrix1)}\n\n"
                f"Matrix 2:\n{self.format_matrix(matrix2)}\n\n"
                f"Result ({operation}):\n{self.format_matrix(result)}"
            )
        }
    
    def simplify_result(self, result: List[List[Any]]) -> List[List[Any]]:
        """Simplify the symbolic expressions in the result matrix.
        
        Process:
        - Attempts to simplify each symbolic element
        - Preserves numeric values
        - Handles failed simplifications gracefully
        - Maintains matrix structure
        
        Args:
            result: Matrix containing symbolic expressions
            
        Returns:
            Matrix with simplified expressions where possible
        """
        simplified = []
        for row in result:
            # Loop through each row in the result matrix to simplify elements
            simplified_row = []
            for element in row:
                # Loop through each element in the row to simplify if symbolic
                if isinstance(element, (sp.Basic, sp.Expr, sp.Symbol)):
                    try:
                        # Try to simplify the expression
                        simplified_row.append(sp.simplify(element))  # Simplify symbolic element
                    except Exception:
                        # If simplification fails, keep original
                        simplified_row.append(element)
                else:
                    simplified_row.append(element)
            simplified.append(simplified_row)
        return simplified 