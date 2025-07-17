
import tkinter as tk
from ui import BoardGameApp

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Board Game Tracker")
    root.wm_minsize(width=1200, height=700)  # Set minimum window size
    app = BoardGameApp(root)
    root.mainloop()
