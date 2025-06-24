import tkinter as tk
from receitai_app import ReceitAIApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ReceitAIApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing) # Ensures that the connection with the DataBase is closed
    root.mainloop()
