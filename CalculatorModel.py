import re  # Regular expressions for parsing
from typing import Dict, Union, Tuple, List, Any
from functools import lru_cache  # For caching function results

class CalculatorModel:
    """A model class for handling mathematical calculations in different number bases.
    
    This class serves as the core calculation engine for the calculator application.
    It supports operations in binary (BIN), octal (OCT), decimal (DEC), and hexadecimal (HEX)
    number systems. The model handles validation, conversion between bases, and mathematical
    operations while enforcing base-specific constraints.
    
    Key Features:
    - Supports basic arithmetic operations (+, -, *, /)
    - Handles parentheses for operation precedence
    - Validates input based on number base constraints
    - Converts between different number bases
    - Enforces maximum digit limits for each base
    """
    
    def __init__(self):
        """Initialize calculator with base-specific configurations.
        
        Sets up the configuration dictionary for each supported number base (BIN, OCT, DEC, HEX).
        Each base configuration includes:
        - valid_digits: String of allowed digits for the base
        - base_int: Integer representation of the base (2, 8, 10, 16)
        - available_digits: List of valid digits for UI/input validation
        - max_display_digits: Maximum number of digits allowed for display
        
        Display Limits (64-bit):
        - BIN: 64 digits (range: -2^63 to 2^63-1)
        - OCT: 22 digits (⌈64/3⌉ digits for equivalent range)
        - DEC: 20 digits (log10(2^64) ≈ 19.3, rounded up)
        - HEX: 16 digits (⌈64/4⌉ digits for equivalent range)
        """
        self.base_configs = {
            'BIN': {
                'valid_digits': '01',
                'base_int': 2,
                'available_digits': ['0', '1'],
                'max_display_digits': 64
            },
            'OCT': {
                'valid_digits': '01234567',
                'base_int': 8,
                'available_digits': ['0', '1', '2', '3', '4', '5', '6', '7'],
                'max_display_digits': 22
            },
            'DEC': {
                'valid_digits': '0123456789',
                'base_int': 10,
                'available_digits': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                'max_display_digits': 20
            },
            'HEX': {
                'valid_digits': '0123456789ABCDEF',
                'base_int': 16,
                'available_digits': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                                   'A', 'B', 'C', 'D', 'E', 'F'],
                'max_display_digits': 16
            }
        }
        self.operators = ['+', '-', '*', '/', '(', ')']

    def get_available_digits(self, base: str) -> List[str]:
        """Get the list of available digits for a given base.
        
        This method is typically used by the UI layer to:
        - Configure number input buttons
        - Validate user input
        - Display available digit options
        
        Args:
            base: The number base (BIN, OCT, DEC, HEX)
            
        Returns:
            List of valid digits for the base
            
        Raises:
            ValueError: If the base is invalid
        """
        if base not in self.base_configs:
            raise ValueError(f"Invalid base: {base}. Must be one of {list(self.base_configs.keys())}")
        return self.base_configs[base]['available_digits']

    def get_operators(self) -> List[str]:
        """Get the list of available operators.
        
        Used by the UI layer to:
        - Configure operator buttons
        - Validate operator input
        - Display available operations
        
        Returns:
            List of valid operators ['+', '-', '*', '/', '(', ')']
        """
        return self.operators

    def get_max_digits(self, base: str) -> int:
        """Get the maximum number of digits allowed for display in a given base.
        
        Used to enforce display limitations and prevent overflow conditions.
        Maximum digits per base (64-bit support):
        - BIN: 64 digits (range: -2^63 to 2^63-1)
        - OCT: 22 digits (equivalent to 64 binary digits)
        - DEC: 20 digits (supports full 64-bit range)
        - HEX: 16 digits (equivalent to 64 binary digits)
        
        Args:
            base: The number base (BIN, OCT, DEC, HEX)
            
        Returns:
            Maximum number of digits for the base
            
        Raises:
            ValueError: If the base is invalid
        """
        if base not in self.base_configs:
            raise ValueError(f"Invalid base: {base}. Must be one of {list(self.base_configs.keys())}")
        return self.base_configs[base]['max_display_digits']

    def serialize_calculation(self, expr: str, base: str, result: str) -> Dict[str, str]:
        """Serialize a calculation for storage or transmission.
        
        Used for:
        - Saving calculation history
        - Transmitting calculations between components
        
        Args:
            expr: The mathematical expression
            base: The number base used
            result: The calculated result
            
        Returns:
            Dictionary containing the calculation details
        """
        return {
            "type": "calculation",
            "expr": expr,
            "base": base,
            "result": result
        }

    def deserialize_calculation(self, data: Dict[str, Any]) -> Tuple[str, str, str]:
        """Deserialize a calculation from storage or transmission.
        
        Used for:
        - Loading saved calculations
        - Reconstructing calculations from history
        - Processing received calculation data
        
        Args:
            data: Dictionary containing calculation data
            
        Returns:
            Tuple of (expression, base, result)
            
        Raises:
            ValueError: If the data format is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid data format: expected dictionary")
            
        if data.get("type") != "calculation":
            raise ValueError("Invalid calculation data: wrong type")
            
        required_fields = ["expr", "base", "result"]
        if not all(field in data for field in required_fields):
            raise ValueError(f"Invalid calculation data: missing fields {[f for f in required_fields if f not in data]}")
            
        return data["expr"], data["base"], data["result"]

    def validate_expression(self, expr: str, base: str) -> None:
        """Validate that the expression is valid for the given base.
        
        Performs comprehensive validation including:
        - Digit validity for the specified base
        - Operator placement and combinations
        - Parentheses matching and placement
        - Expression structure and completeness
        - Number length limits
        
        Args:
            expr: The mathematical expression to validate
            base: The number base to validate against
            
        Raises:
            ValueError: With detailed error message if validation fails
        """
        if not isinstance(expr, str):
            raise ValueError("Expression must be a string")
            
        if not expr or expr.isspace():
            raise ValueError("Expression cannot be empty")
        
        if base not in self.base_configs:
            raise ValueError(f"Invalid base: {base}. Must be one of {list(self.base_configs.keys())}")
        
        valid_digits = self.base_configs[base]['valid_digits']
        
        # Split expression into tokens using regex
        tokens = re.findall(r'([0-9A-Fa-f]+|[\+\-\*\/\(\)]|\s+)', expr)  # re.findall for tokenizing
        tokens = [t for t in tokens if not t.isspace()]
        
        if not tokens:
            raise ValueError("Expression contains no valid tokens")
        
        # Validate each token and check for invalid combinations
        prev_token_type = None  # Can be 'number', 'operator', 'open_paren', 'close_paren'
        paren_count = 0
        operator_count = 0
        number_count = 0
        
        for token in tokens:
            # Loop through each token in the expression to validate its type and placement
            if token in '+-*/':
                operator_count += 1
                if prev_token_type in [None, 'operator', 'open_paren']:
                    # Check for invalid operator placement (e.g., two operators in a row)
                    if token not in '+-' or prev_token_type == 'operator':  # Allow unary + and -
                        raise ValueError(f"Invalid operator placement: '{token}' after {prev_token_type}")
                prev_token_type = 'operator'
            elif token == '(':  # Parenthesis
                if prev_token_type == 'number':
                    # Check for missing operator before parenthesis
                    raise ValueError("Missing operator before parenthesis")
                paren_count += 1
                prev_token_type = 'open_paren'
            elif token == ')':
                if prev_token_type in [None, 'operator', 'open_paren']:
                    # Check for invalid closing parenthesis placement
                    raise ValueError("Invalid closing parenthesis placement - no expression inside parentheses")
                paren_count -= 1
                if paren_count < 0:
                    # Check for unmatched closing parenthesis
                    raise ValueError("Unmatched closing parenthesis")
                prev_token_type = 'close_paren'
            else:
                # Validate number for the current base
                if not all(d in valid_digits for d in token.upper()):
                    # Check for invalid digits in the number
                    invalid_digits = [d for d in token.upper() if d not in valid_digits]
                    raise ValueError(f"Invalid digit(s) {invalid_digits} for {base} number: {token}")
                # Check number length
                if len(token) > self.get_max_digits(base):
                    raise ValueError(f"Number {token} exceeds maximum length of {self.get_max_digits(base)} digits for {base}")
                if prev_token_type == 'close_paren':
                    # Check for missing operator after parenthesis
                    raise ValueError("Missing operator after parenthesis")
                prev_token_type = 'number'
                number_count += 1
        
        if paren_count > 0:
            # Check for unclosed parenthesis
            raise ValueError(f"Unclosed parenthesis: missing {paren_count} closing parenthesis")
        
        if prev_token_type == 'operator':
            # Check if expression ends with an operator
            raise ValueError("Expression cannot end with an operator")
            
        if number_count == 0:
            # Check if there is at least one number in the expression
            raise ValueError("Expression must contain at least one number")
            
        if operator_count >= number_count:
            # Check for too many operators compared to operands
            raise ValueError("Too many operators for the number of operands")

    @lru_cache(maxsize=128)  # Cache results for performance
    def to_decimal(self, number_str: str, base: str) -> int:
        """Convert a number from given base to decimal.
        
        Uses Python's built-in base conversion with additional validation.
        Results are cached to improve performance for repeated conversions.
        
        Args:
            number_str: The number to convert as a string
            base: Source base of the number
            
        Returns:
            Decimal (base-10) integer representation
            
        Raises:
            ValueError: If the number is invalid for the given base
        """
        if not isinstance(number_str, str):
            raise ValueError("Number must be a string")
            
        if not number_str:
            raise ValueError("Empty number string")
            
        # Handle negative numbers
        is_negative = number_str.startswith('-')
        if is_negative:
            number_str = number_str[1:]
            
        # Validate the number string
        if base not in self.base_configs:
            raise ValueError(f"Invalid base: {base}. Must be one of {list(self.base_configs.keys())}")
            
        valid_digits = self.base_configs[base]['valid_digits']
        if not all(d in valid_digits for d in number_str.upper()):
            invalid_digits = [d for d in number_str.upper() if d not in valid_digits]
            raise ValueError(f"Invalid digit(s) {invalid_digits} for {base} number: {number_str}")
            
        # Convert based on the base
        try:
            if base == 'DEC':
                result = float(number_str)  # Convert string to float
            else:
                base_int = self.base_configs[base]['base_int']
                number_str = number_str.upper()
                result = int(number_str, base_int)  # Convert string to int with base
            return -result if is_negative else result
            
        except ValueError:
            raise ValueError(f"Invalid {base} number: '{number_str}'")

    @lru_cache(maxsize=128)  # Cache results for performance
    def from_decimal(self, number: Union[int, float], base: str) -> str:
        """Convert a decimal number to the given base.
        
        Uses Python's built-in conversion functions (hex, oct, bin)
        with additional formatting and validation. Results are cached
        for performance optimization.
        
        Args:
            number: Decimal integer or float to convert
            base: Target base for conversion
            
        Returns:
            String representation in target base
            
        Raises:
            ValueError: If number exceeds display limits for target base
        """
        if not isinstance(number, (int, float)):
            raise ValueError("Number must be an integer or float")
            
        if base not in self.base_configs:
            raise ValueError(f"Invalid base: {base}. Must be one of {list(self.base_configs.keys())}")
            
        if number == 0:
            return '0'
            
        is_negative = number < 0
        if is_negative:
            number = -number
            
        # For float, skip digit limit check (since it's not representable in non-DEC bases)
        if isinstance(number, int):
            max_value = (self.base_configs[base]['base_int'] ** self.base_configs[base]['max_display_digits']) - 1
            if number > max_value:
                raise ValueError(f"Number too large for {base} representation with {self.get_max_digits(base)} digits")
        
        try:
            if base == 'DEC':
                result = str(-number if is_negative else number)
            elif isinstance(number, float):
                # For non-DEC bases, return float as string (not representable)
                result = f"{'-' if is_negative else ''}{number} (non-integer, cannot represent in {base})"
            elif base == 'HEX':
                result = hex(number)[2:].upper()  # Convert int to hex string
                result = f"-{result}" if is_negative else result
            elif base == 'OCT':
                result = oct(number)[2:]  # Convert int to octal string
                result = f"-{result}" if is_negative else result
            elif base == 'BIN':
                result = bin(number)[2:]  # Convert int to binary string
                result = f"-{result}" if is_negative else result
            return result
        except Exception as e:
            raise ValueError(f"Error converting to {base}: {str(e)}")

    @lru_cache(maxsize=128)  # Cache results for performance
    def convert_to_decimal(self, expr: str, base: str) -> str:
        """Convert all numbers in an expression to decimal.
        
        Handles complex expressions by:
        - Preserving operators and parentheses
        - Converting only the numeric portions
        - Maintaining unary operators
        - Caching results for performance
        
        Args:
            expr: Expression containing numbers in source base
            base: Source base of the numbers
            
        Returns:
            Expression with all numbers converted to decimal
            
        Raises:
            ValueError: If any number in the expression is invalid
        """
        if base == 'DEC':
            return expr
            
        # First, validate the expression
        self.validate_expression(expr, base)
        
        # Handle unary operators and tokenize the expression
        expr = re.sub(r'^\s*-\s*', '-', expr)  # Handle unary minus at start
        expr = re.sub(r'^\s*\+\s*', '', expr)  # Remove unary plus at start
        expr = re.sub(r'\(\s*-\s*', '(-', expr)  # Handle unary minus after open paren
        expr = re.sub(r'\(\s*\+\s*', '(', expr)  # Remove unary plus after open paren
        
        # Split into tokens preserving operators and parentheses
        tokens = re.findall(r'(-?[0-9A-Fa-f]+|[\+\-\*\/\(\)])', expr)
        
        dec_expr = []
        for token in tokens:
            # Loop through each token in the expression to convert numbers to decimal
            if token in '+-*/()':
                dec_expr.append(token)
            else:
                # Convert number to decimal
                try:
                    dec_num = self.to_decimal(token, base)
                    dec_expr.append(str(dec_num))
                except ValueError as e:
                    raise ValueError(f"Error converting '{token}': {str(e)}")
                
        return ''.join(dec_expr)

    def evaluate_expression(self, expr: str, base: str) -> str:
        """Evaluate a mathematical expression in the given base.
        
        This is the main calculation method that:
        1. Converts the expression to decimal
        2. Evaluates the decimal expression
        3. Converts the result back to the target base
        
        Security note: Uses restricted eval() for mathematical operations only.
        
        Args:
            expr: The mathematical expression to evaluate
            base: The number base for input and output
            
        Returns:
            The result in the specified base
            
        Raises:
            ValueError: For invalid expressions or results that can't be represented
        """
        print(f"[TRACE] CalculatorModel.evaluate_expression called with: expr={expr}, base={base}")
        # First convert the expression to decimal
        dec_expr = self.convert_to_decimal(expr, base)
        print(f"[TRACE] Decimal expression: {dec_expr}")
        try:
            # Replace multiple unary minuses with a single one
            dec_expr = re.sub(r'-{2,}', '-', dec_expr)
            # Replace unary plus followed by minus with just minus
            dec_expr = re.sub(r'\+-', '-', dec_expr)
            # Evaluate the decimal expression
            result = eval(dec_expr, {"__builtins__": {}}, {})  # Restricted eval for safety
            print(f"[TRACE] Evaluation result: {result}")
            if not isinstance(result, (int, float)):
                # Check if the result is a numeric type
                raise ValueError("Expression resulted in a non-numeric value")
            # Convert the result back to the target base
            final_result = self.from_decimal(result, base)
            print(f"[TRACE] Final result in base {base}: {final_result}")
            return final_result
        except ZeroDivisionError:
            # Handle division by zero
            raise ValueError("Division by zero")
        except Exception as e:
            # Handle any other evaluation error
            raise ValueError(f"Error evaluating expression: {str(e)}") 