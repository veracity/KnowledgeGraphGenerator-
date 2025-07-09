import sys
import tkinter as tk

from gui.app import NetGenApp

def main():
    root = tk.Tk()
    app = NetGenApp(root)
    app.mainloop()


if __name__ == "__main__":
    sys.exit(main())