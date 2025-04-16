import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk

def add_multiplication(s):
    result = ""
    s = s.strip()
    i = 0
    functions = {'sin', 'cos', 'tan', 'log', 'exp', 'sqrt'}
    while i < len(s):
        func_detected = False
        for func in functions:
            if s[i:i+len(func)] == func and (i == 0 or not s[i-1].isalnum()):
                result += func
                i += len(func)
                func_detected = True
                if i < len(s) and (s[i] == '(' or s[i] == 'x') and result[-1] != '*':
                    if len(result) > len(func) and result[-len(func)-1] not in '+-*/':
                        result += '*'
                break
        if not func_detected:
            result += s[i]
            if i + 1 < len(s):
                if s[i].isdigit() and (s[i + 1] == 'x' or s[i + 1] == '(' or s[i + 1:i + 4] in functions):
                    result += '*'
                elif s[i] == ')' and (s[i + 1] == '(' or s[i + 1] == 'x' or s[i + 1:i + 4] in functions):
                    result += '*'
            i += 1
    return result

def solve_equation(equation_str):
    try:
        x = sp.Symbol('x')
        left, right = equation_str.split('=')
        left_processed = add_multiplication(left)
        right_processed = add_multiplication(right)
        left_expr = sp.sympify(left_processed, evaluate=False)
        right_expr = sp.sympify(right_processed, evaluate=False)
        
        left_str = str(left_expr).replace('**', '^')
        right_str = str(right_expr).replace('**', '^')
        steps = [f"{left_str} = {right_str}"]
        
        left_expanded = sp.expand(left_expr)
        right_expanded = sp.expand(right_expr)
        if left_expanded != left_expr or right_expanded != right_expr:
            left_str = str(left_expanded).replace('**', '^')
            right_str = str(right_expanded).replace('**', '^')
            steps.append(f"Expand: {left_str} = {right_str}")
            left_expr, right_expr = left_expanded, right_expanded
        else:
            steps.append(f"Equation remains: {left_str} = {right_str}")
        
        simplified = left_expr - right_expr
        simplified_str = str(simplified).replace('**', '^')
        steps.append(f"Subtract {right_str} from both sides: {simplified_str} = 0")
        
        simplified = sp.simplify(simplified)
        simplified_str = str(simplified).replace('**', '^')
        if simplified_str != steps[-1].split('=')[0].strip():
            steps.append(f"Simplify: {simplified_str} = 0")
        
        # Solve symbolically
        solutions = sp.solve(simplified, x)
        if solutions:
            # Separate real and complex solutions
            real_sols = [sol for sol in solutions if sol.is_real]
            complex_sols = [sol for sol in solutions if not sol.is_real]
            
            if real_sols:
                exact_real = []
                approx_real = []
                for sol in real_sols:
                    # Check if solution is a simple symbolic form (including irrationals like sqrt)
                    if sol.is_number and len(str(sol)) < 20:  # Arbitrary length threshold for "simple"
                        exact_real.append(sol)
                    else:
                        # Approximate complex real expressions
                        approx = sp.N(sol, 6)
                        approx_real.append(approx)
                
                if exact_real:
                    if len(exact_real) > 1:
                        exact_str = " or ".join(f"x = {sol}" for sol in exact_real)
                        steps.append(f"Exact Real Solutions: {exact_str}")
                    else:
                        steps.append(f"Exact Real Solution: x = {exact_real[0]}")
                
                if approx_real:
                    if len(approx_real) > 1:
                        approx_str = " or ".join(f"x ≈ {sol}" for sol in approx_real)
                        steps.append(f"Approximate Real Solutions: {approx_str}")
                    else:
                        steps.append(f"Approximate Real Solution: x ≈ {approx_real[0]}")
            
            if complex_sols:
                if len(complex_sols) > 1:
                    complex_str = " or ".join(f"x = {sol}" for sol in complex_sols)
                    steps.append(f"Complex Solutions: {complex_str}")
                else:
                    steps.append(f"Complex Solution: x = {complex_sols[0]}")
            
            if not real_sols and not complex_sols:
                steps.append("No real or complex solutions identified")
        else:
            steps.append("No exact symbolic solution found")
            initial_guesses = [-1, 0, 1, 2]
            numerical_sols = []
            for guess in initial_guesses:
                try:
                    sol = sp.nsolve(simplified, x, guess, prec=6)
                    if not any(abs(float(sol) - float(existing)) < 0.001 for existing in numerical_sols):
                        numerical_sols.append(sol)
                except (ValueError, ZeroDivisionError):
                    continue
            if numerical_sols:
                steps.append("Approximate Real Solutions (numerical):")
                for i, sol in enumerate(numerical_sols):
                    steps.append(f"  Guess x = {initial_guesses[i]}: x ≈ {sol}")
            else:
                steps.append("No numerical solutions found with given guesses")
        
        return "\n".join(steps)
    except sp.SympifyError as e:
        return f"Error parsing equation: {e}"
    except Exception as e:
        return f"Error: {e}"

def plot_equation(equation_str, x_range=(-10, 10)):
    try:
        x = sp.Symbol('x')
        left, right = equation_str.split('=')
        left_processed = add_multiplication(left)
        right_processed = add_multiplication(right)
        left_expr = sp.sympify(left_processed, evaluate=False)
        right_expr = sp.sympify(right_processed, evaluate=False)
        expr = left_expr - right_expr
        
        f = sp.lambdify(x, expr, modules=['numpy', {'log': np.log, 'exp': np.exp, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'sqrt': np.sqrt}])
        x_vals = np.linspace(x_range[0], x_range[1], 1000)
        
        y_vals = []
        for val in x_vals:
            try:
                y_vals.append(f(val))
            except (ValueError, ZeroDivisionError, OverflowError):
                y_vals.append(np.nan)
        
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, label=f"{str(expr)} = 0")
        plt.axhline(0, color='black', linestyle='--', linewidth=0.5)
        plt.axvline(0, color='black', linestyle='--', linewidth=0.5)
        plt.grid(True)
        plt.legend()
        plt.title(f"Plot of {equation_str}")
        plt.xlabel('x')
        plt.ylabel('y')
        plt.show()
        return "Plot generated successfully"
    except sp.SympifyError as e:
        return f"Error parsing equation: {e}"
    except Exception as e:
        return f"Error: {e}"

# Add global variable to track current base
current_base = 'DEC'  # Default to decimal

def append_to_entry(char):
    calc_entry.insert(tk.END, char)

def clear_entry():
    global current_base
    calc_entry.delete(0, tk.END)
    calc_display.delete(1.0, tk.END)
    current_base = 'DEC'
    calc_display.insert(tk.END, f"Base: {current_base}")

def delete_last():
    current = calc_entry.get()
    if current:
        calc_entry.delete(0, tk.END)
        calc_entry.insert(0, current[:-1])

def set_base(base):
    global current_base
    current_base = base
    calc_display.delete(1.0, tk.END)
    calc_display.insert(tk.END, f"Base: {base}")
    calculate()  

def calculate():
    global current_base
    expr = calc_entry.get().strip()
    if not expr:
        return
    
    try:
        # Split expression into operands and operator
        for op in ['+', '-', '*', '/']:
            if op in expr:
                left, right = expr.split(op)
                left, right = left.strip(), right.strip()
                operator = op
                break
        else:
            left, operator, right = expr, None, None  # Single number case
        
        # Convert input based on current base
        if current_base == 'BIN':
            left_dec = int(left, 2) if left else 0
            right_dec = int(right, 2) if right else 0
        elif current_base == 'OCT':
            left_dec = int(left, 8) if left else 0
            right_dec = int(right, 8) if right else 0
        elif current_base == 'HEX':
            left_dec = int(left, 16) if left else 0
            right_dec = int(right, 16) if right else 0
        else:  # DEC
            left_dec = int(left) if left else 0
            right_dec = int(right) if right else 0
        
        # Perform operation
        if operator:
            if operator == '+':
                result = left_dec + right_dec
            elif operator == '-':
                result = left_dec - right_dec
            elif operator == '*':
                result = left_dec * right_dec
            elif operator == '/':
                result = left_dec / right_dec if right_dec != 0 else "Error: Division by zero"
        else:
            result = left_dec
        
        # Display result in current base
        if isinstance(result, (int, float)):
            if current_base == 'BIN':
                display = bin(int(result))[2:] if result >= 0 else f"-{bin(int(-result))[2:]}"
            elif current_base == 'OCT':
                display = oct(int(result))[2:] if result >= 0 else f"-{oct(int(-result))[2:]}"
            elif current_base == 'HEX':
                display = hex(int(result))[2:].upper() if result >= 0 else f"-{hex(int(-result))[2:].upper()}"
            else:  # DEC
                display = str(result)
        else:
            display = str(result)
        
        calc_display.delete(1.0, tk.END)
        calc_display.insert(tk.END, f"{current_base}: {display}")
    except ValueError as e:
        calc_display.delete(1.0, tk.END)
        calc_display.insert(tk.END, "Error: Invalid input for base")
    except sp.SympifyError:
        calc_display.delete(1.0, tk.END)
        calc_display.insert(tk.END, "Error: Invalid expression")

def on_solve():
    equation = solver_entry.get()
    if '=' in equation:
        result = solve_equation(equation)
        solver_output.delete(1.0, tk.END)
        solver_output.insert(tk.END, result)
    else:
        solver_output.delete(1.0, tk.END)
        solver_output.insert(tk.END, "Please enter an equation with '=' for solving")

def on_plot():
    equation = solver_entry.get()
    if '=' in equation:
        result = plot_equation(equation)
        solver_output.delete(1.0, tk.END)
        solver_output.insert(tk.END, result)
    else:
        solver_output.delete(1.0, tk.END)
        solver_output.insert(tk.END, "Please enter an equation with '=' for plotting")

def show_calculator():
    solver_frame.grid_remove()
    calc_frame.grid(row=1, column=0, columnspan=3, pady=10)

def show_solver():
    calc_frame.grid_remove()
    solver_frame.grid(row=1, column=0, columnspan=3, pady=10)

# Button layout 
buttons = [
    ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3), ('BIN', 2, 4),
    ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3), ('OCT', 3, 4),
    ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3), ('DEC', 4, 4),
    ('0', 5, 0), ('.', 5, 1), ('+', 5, 2), ('=', 5, 3), ('HEX', 5, 4),
    ('C', 6, 0), ('(', 6, 1), (')', 6, 2), ('⌫', 6, 3)
]

# Set up the GUI with styling
root = tk.Tk()
root.title("Math Tool")
root.configure(bg='#f0f0f0')  # Light gray background
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 900  # Match your root.geometry width
window_height = 700  # Match your root.geometry height
x_pos = (screen_width - window_width) // 2
y_pos = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

# Style configuration
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=8, background='#333333', foreground='white', borderwidth=1, relief='flat')  # Larger font and padding
style.map('TButton', background=[('active', '#555555')], foreground=[('active', 'white')])
style.configure('TLabel', font=('Helvetica', 14), background='#1a1a1a', foreground='#ffffff')  # Larger font
style.configure('TEntry', font=('Helvetica', 14), fieldbackground='#2a2a2a', foreground='white', borderwidth=1, relief='solid')  # Larger font
style.configure('TFrame', background='#1a1a1a')
root.configure(bg='#1a1a1a')

# Navigation frame
nav_frame = ttk.Frame(root, padding="15", style='TFrame')  # Increased padding
nav_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))

calc_nav_button = ttk.Button(nav_frame, text="Calculator", command=show_calculator, style='TButton')
calc_nav_button.grid(row=0, column=0, padx=10)  # Increased padx

solver_nav_button = ttk.Button(nav_frame, text="Solver & Plotter", command=show_solver, style='TButton')
solver_nav_button.grid(row=0, column=1, padx=10)  # Increased padx

# Calculator frame
calc_frame = ttk.Frame(root, padding="15", style='TFrame')
calc_frame.grid(row=1, column=0, columnspan=3, pady=15)

calc_display = tk.Text(calc_frame, height=1, width=40, font=('Helvetica', 14), bg='#2a2a2a', fg='white', borderwidth=1, relief='solid')
calc_display.grid(row=0, column=0, columnspan=5, pady=10)
calc_display.insert(tk.END, f"Base: {current_base}")

calc_entry = ttk.Entry(calc_frame, width=60, style='TEntry')
calc_entry.grid(row=1, column=0, columnspan=5, pady=10)

for (text, row, col) in buttons:
    if text == '=':
        cmd = calculate
    elif text == 'C':
        cmd = clear_entry
    elif text == '⌫':
        cmd = delete_last
    elif text in ['BIN', 'OCT', 'DEC', 'HEX']:
        cmd = lambda x=text: set_base(x)
    else:
        cmd = lambda x=text: append_to_entry(x)
    ttk.Button(calc_frame, text=text, command=cmd, width=6, style='TButton').grid(row=row, column=col, padx=5, pady=5)

# Solver/Plotter frame
solver_frame = ttk.Frame(root, padding="15", style='TFrame')  # Increased padding

solver_label = ttk.Label(solver_frame, text="Enter equation (e.g., 2sin(x) = 1):", style='TLabel')
solver_label.grid(row=0, column=0, columnspan=2, pady=10)  # Increased pady

solver_entry = ttk.Entry(solver_frame, width=60, style='TEntry')  # Wider entry
solver_entry.grid(row=1, column=0, columnspan=2, pady=10)  # Increased pady

solve_button = ttk.Button(solver_frame, text="Solve", command=on_solve, style='TButton')
solve_button.grid(row=2, column=0, pady=10)  # Increased pady

plot_button = ttk.Button(solver_frame, text="Plot", command=on_plot, style='TButton')
plot_button.grid(row=2, column=1, pady=10)  # Increased pady

solver_output = tk.Text(solver_frame, height=20, width=90, font=('Helvetica', 12), bg='#2a2a2a', fg='white', borderwidth=1, relief='solid')  # Larger text area
solver_output.grid(row=3, column=0, columnspan=2, pady=10)  # Increased pady

# Start with calculator visible
show_calculator()

root.mainloop()

# Examples
# x*log(x) = 0
# x^3 + x^2 - 5x = 1
# 2x^3 + x^2 - 1x = 1
# sin(3x) - cos(x) + tan(5x) = 0