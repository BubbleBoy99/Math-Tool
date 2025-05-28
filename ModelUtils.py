# ModelUtils.py
# Shared utilities for PlotterModel and SolverModel

import sympy as sp
import numpy as np
import math  # Added import for math.factorial
from typing import Dict, Any, Tuple
import logging
import os
import re

# Shared function dictionary
FUNCTIONS = {
    'sin': sp.sin,
    'cos': sp.cos,
    'tan': sp.tan,
    'cot': lambda x: 1/sp.tan(x),
    'sec': lambda x: 1/sp.cos(x),
    'csc': lambda x: 1/sp.sin(x),
    'log': sp.log,
    'ln': sp.log,
    'exp': sp.exp,
    'sqrt': sp.sqrt,
    'abs': abs,
    'asin': sp.asin,
    'acos': sp.acos,
    'atan': sp.atan,
    'pow': lambda x, y: x ** y,  # Added for power function
    'fact': lambda n: math.factorial(n)  # Added for factorial; requires math import
}

def add_multiplication(expr: str, functions=FUNCTIONS) -> str:
    """Add implicit multiplication symbols to expression (shared logic)."""
    if not expr:
        return expr
    expr = expr.replace('^', '**')  # Allow user to use ^ for exponentiation
    result = []
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue
        found_func = False
        for func in sorted(functions.keys(), key=len, reverse=True):
            if expr[i:].startswith(func):
                start_idx = i
                i += len(func)
                while i < len(expr) and expr[i].isspace():
                    i += 1
                if i < len(expr) and expr[i] == '(':  # function call
                    paren_count = 1
                    i += 1
                    while i < len(expr) and paren_count > 0:
                        if expr[i] == '(': paren_count += 1
                        elif expr[i] == ')': paren_count -= 1
                        i += 1
                    func_call = expr[start_idx:i]
                    tokens.append(('func_call', func_call))
                    found_func = True
                    break
                else:
                    tokens.append(('func', func))
                    found_func = True
                    break
        if found_func:
            continue
        if expr[i].isdigit() or (expr[i] == '-' and i + 1 < len(expr) and expr[i + 1].isdigit()):
            num = expr[i]
            i += 1
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                num += expr[i]
                i += 1
            tokens.append(('number', num))
            continue
        if expr[i].isalpha():
            var = expr[i]
            i += 1
            while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                var += expr[i]
                i += 1
            if var not in functions:
                tokens.append(('var', var))
            continue
        if expr[i] in '+-*/()^=':
            tokens.append(('op', expr[i]))
            i += 1
            continue
        raise ValueError(f"Invalid character in expression: {expr[i]}")
    for i, token in enumerate(tokens):
        curr_type, curr_val = token
        if curr_type == 'func_call':
            func_name = curr_val[:curr_val.index('(')]
            args = curr_val[curr_val.index('(') + 1:-1]
            processed_args = add_multiplication(args, functions)
            result.append(f"{func_name}({processed_args})")
        else:
            result.append(curr_val)
        if i < len(tokens) - 1:
            next_type, next_val = tokens[i + 1]
            needs_mult = False
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

def format_expression(expr) -> str:
    """Format a SymPy expression as a readable string for display."""
    return str(expr)

def serialize_plot(equation: str, message: str) -> Dict[str, str]:
    return {
        "type": "plot",
        "equation": equation,
        "message": message
    }

def deserialize_plot(data: Dict[str, Any]) -> Tuple[str, str]:
    if not isinstance(data, dict):
        raise ValueError("Invalid data format: expected dictionary")
    if data.get("type") != "plot":
        raise ValueError("Invalid plot data: wrong type")
    required_fields = ["equation", "message"]
    if not all(field in data for field in required_fields):
        raise ValueError(f"Invalid plot data: missing fields {[f for f in required_fields if f not in data]}")
    return data["equation"], data["message"]

def validate_input(input_type: str, value, **kwargs):
    """
    Unified validation function for different input types.
    input_type: 'expression', 'matrix', or 'symbolic_expression'
    value: the string or object to validate
    kwargs: additional context (e.g., base for expressions, variable for symbolic)
    Raises ValueError if validation fails.
    """
    if input_type == 'expression':
        expr = value
        base = kwargs.get('base', 'DEC')
        base_configs = kwargs.get('base_configs')
        get_max_digits = kwargs.get('get_max_digits')
        if not isinstance(expr, str):
            raise ValueError("Expression must be a string")
        if not expr or expr.isspace():
            raise ValueError("Expression cannot be empty")
        if base not in base_configs:
            raise ValueError(f"Invalid base: {base}. Must be one of {list(base_configs.keys())}")
        valid_digits = base_configs[base]['valid_digits']
        
        tokens = re.findall(r'([0-9A-Fa-f]+|[\+\-\*\/\(\)]|\s+)', expr)
        tokens = [t for t in tokens if not t.isspace()]
        if not tokens:
            raise ValueError("Expression contains no valid tokens")
        prev_token_type = None
        paren_count = 0
        operator_count = 0
        number_count = 0
        for token in tokens:
            if token in '+-*/':
                operator_count += 1
                if prev_token_type in [None, 'operator', 'open_paren']:
                    if token not in '+-' or prev_token_type == 'operator':
                        raise ValueError(f"Invalid operator placement: '{token}' after {prev_token_type}")
                prev_token_type = 'operator'
            elif token == '(':  # Parenthesis
                if prev_token_type == 'number':
                    raise ValueError("Missing operator before parenthesis")
                paren_count += 1
                prev_token_type = 'open_paren'
            elif token == ')':
                if prev_token_type in [None, 'operator', 'open_paren']:
                    raise ValueError("Invalid closing parenthesis placement - no expression inside parentheses")
                paren_count -= 1
                if paren_count < 0:
                    raise ValueError("Unmatched closing parenthesis")
                prev_token_type = 'close_paren'
            else:
                if not all(d in valid_digits for d in token.upper()):
                    invalid_digits = [d for d in token.upper() if d not in valid_digits]
                    raise ValueError(f"Invalid digit(s) {invalid_digits} for {base} number: {token}")
                if len(token) > get_max_digits(base):
                    raise ValueError(f"Number {token} exceeds maximum length of {get_max_digits(base)} digits for {base}")
                if prev_token_type == 'close_paren':
                    raise ValueError("Missing operator after parenthesis")
                prev_token_type = 'number'
                number_count += 1
                            
        if paren_count > 0:
            raise ValueError(f"Unclosed parenthesis: missing {paren_count} closing parenthesis")
        if prev_token_type == 'operator':
            raise ValueError("Expression cannot end with an operator")
        if number_count == 0:
            raise ValueError("Expression must contain at least one number")
        if operator_count >= number_count:
            raise ValueError("Too many operators for the number of operands")
    elif input_type == 'matrix':
        matrix = value
        if not matrix:
            raise ValueError("Matrix cannot be empty")
        if not all(isinstance(row, list) for row in matrix):
            raise ValueError("Matrix must be a list of lists")
        row_length = len(matrix[0])
        if not all(len(row) == row_length for row in matrix):
            raise ValueError("All rows must have the same length")
    elif input_type == 'symbolic_expression':
        expr = value
        variable = kwargs.get('variable', 'x')
        if not isinstance(expr, str):
            raise ValueError("Symbolic expression must be a string")
        if not expr or expr.isspace():
            raise ValueError("Symbolic expression cannot be empty")
        try:
            if '=' in expr:
                left, right = expr.split('=', 1)
                left = add_multiplication(left.strip())
                right = add_multiplication(right.strip())
                parsed = sp.Eq(sp.sympify(left, locals=FUNCTIONS), sp.sympify(right, locals=FUNCTIONS))
            else:
                expr = add_multiplication(expr.strip())
                parsed = sp.sympify(expr, locals=FUNCTIONS)
        except Exception as e:
            raise ValueError(f"Invalid symbolic expression: {e}")
        # Optionally check for variable presence
        if variable:
            symbols = [str(s) for s in parsed.free_symbols]
            if variable not in symbols:
                raise ValueError(f"Symbolic expression must contain the variable '{variable}'")
    else:
        raise ValueError(f"Unknown input_type for validation: {input_type}")

def log_server_event(event_type: str, message: str):
    logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'logs', 'server.log'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.log(logging.INFO, f'{event_type}: {message}')

def handle_model_request(controller, model_name: str, instructions: dict):
    """
    Centralized handler for all model requests.
    - controller: the Controller instance (with model attributes)
    - model_name: 'calculator', 'matrix', 'solver', 'plotter'
    - instructions: dict with operation and data
    """
    log_server_event('Request Received', f'Model: {model_name}, Instructions: {instructions}')
    if model_name == "calculator":
        expr = instructions.get("expr")
        base = instructions.get("base", "DEC")
        validate_input('expression', expr, base=base, base_configs=controller.calc_model.base_configs, get_max_digits=controller.calc_model.get_max_digits)
        result = controller.calc_model.evaluate_expression(expr, base)
        log_server_event('Request Processed', f'Result for {model_name}: {result}')
        return result
    elif model_name == "matrix":
        op = instructions.get("operation")
        m1 = instructions.get("matrix1")
        m2 = instructions.get("matrix2")
        # Parse matrix input strings to lists
        m1_parsed = controller.matrix_model.parse_matrix_input(m1) if isinstance(m1, str) else m1
        m2_parsed = controller.matrix_model.parse_matrix_input(m2) if isinstance(m2, str) else m2
        validate_input('matrix', m1_parsed)
        validate_input('matrix', m2_parsed)
        if op == "add":
            result = controller.matrix_model.add_matrices(m1_parsed, m2_parsed)
        elif op == "subtract":
            result = controller.matrix_model.subtract_matrices(m1_parsed, m2_parsed)
        elif op == "multiply":
            result = controller.matrix_model.multiply_matrices(m1_parsed, m2_parsed)
        else:
            raise ValueError("Unknown matrix operation")
        log_server_event('Request Processed', f'Result for {model_name}: Success')
        return result
    elif model_name == "solver":
        eq = instructions.get("equation")
        validate_input('symbolic_expression', eq, variable='x')
        result = controller.solver_model.solve_equation(eq)
        log_server_event('Request Processed', f'Result for {model_name}: Success')
        return result
    elif model_name == "plotter":
        eq = instructions.get("equation")
        validate_input('symbolic_expression', eq, variable='x')
        result = controller.plotter_model.plot_equation(eq)
        log_server_event('Request Processed', f'Result for {model_name}: Success')
        return result
    else:
        log_server_event('Error', f'Unknown model: {model_name}')
        raise ValueError(f"Unknown model: {model_name}") 