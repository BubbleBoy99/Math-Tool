import tkinter as tk
from View import CalculatorView
from Client import MathClientController

def main():
    root = tk.Tk()
    root.title("Scientific Calculator")
    view = CalculatorView(root)
    client = MathClientController(view, host='127.0.0.1', port=12345)
    client.update_server_status()  # Show server status on startup
    root.mainloop()

if __name__ == "__main__":
    main() 

# Examples
# 1+(5-3*9)+6*9
# 01+110+0011+10101
# 6/9+3*4-(8-5+4*7)
# x*log(x) = 0
# x^3 + x^2 - 5x = 1
# 2x^3 + x^2 - 1x = 1
# sin(3x) - cos(x) = 0
# [1,2,3;4,5,6]*[1,2;3,4;5,6]