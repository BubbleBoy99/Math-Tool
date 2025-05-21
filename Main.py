import tkinter as tk
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Controller import Controller

def main():
    root = tk.Tk()
    root.title("Scientific Calculator")
    app = Controller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
#4760
#4564
#4581

# Examples
# 1+(5-3*9)+6*9
# 01+110+0011+10101
# 6/9+3*4-(8-5+4*7)
# x*log(x) = 0
# x^3 + x^2 - 5x = 1
# 2x^3 + x^2 - 1x = 1
# sin(3x) - cos(x) = 0
# [1,2,3;4,5,6]*[1,2;3,4;5,6]