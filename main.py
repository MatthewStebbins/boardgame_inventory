import tkinter as tk
from tkinter import messagebox, simpledialog
from db import init_db, add_game, loan_game, return_game, list_games, delete_game
from api import lookup_barcode
import threading

class BoardGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Board Game Tracker")
        self.build_gui()
        threading.Thread(target=init_db).start()  # Initialize the database in a separate thread

    def build_gui(self):
        # Create a horizontal frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)  # Pack at the top of the window

        # Add buttons to the horizontal frame
        tk.Button(button_frame, text="Add Game by Barcode", width=20, command=self.add_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Loan Game", width=20, command=self.loan_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Return Game", width=20, command=self.return_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="List Games", width=20, command=self.list_games).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Game", width=20, command=self.delete_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Exit", width=20, command=self.root.quit).pack(side=tk.LEFT, padx=5)

    def add_game(self):
        def add_game_thread():
            # Create a frame for adding a game
            add_game_frame = tk.Frame(self.root, borderwidth=2, relief="solid")
            add_game_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame in the main application

            tk.Label(add_game_frame, text="Add Game by Barcode", pady=10).pack()

            # Barcode input
            tk.Label(add_game_frame, text="Barcode:").pack()
            barcode_entry = tk.Entry(add_game_frame, width=30)
            barcode_entry.pack(pady=5)

            # Bookcase input
            tk.Label(add_game_frame, text="Bookcase:").pack()
            bookcase_entry = tk.Entry(add_game_frame, width=30)
            bookcase_entry.pack(pady=5)

            # Shelf input
            tk.Label(add_game_frame, text="Shelf:").pack()
            shelf_entry = tk.Entry(add_game_frame, width=30)
            shelf_entry.pack(pady=5)

            def submit_game():
                barcode = barcode_entry.get()
                bookcase = bookcase_entry.get()
                shelf = shelf_entry.get()

                if not barcode:
                    messagebox.showerror("Error", "Barcode is required.")
                    return

                data = lookup_barcode(barcode)
                if data:
                    name = data.get('title', 'Unknown Title')
                    add_game(name, barcode, bookcase, shelf)
                    messagebox.showinfo("Success", f"Game '{name}' added.")
                    add_game_frame.destroy()
                else:
                    messagebox.showerror("Error", "No data found for that barcode.")

            # Submit button
            tk.Button(add_game_frame, text="Submit", command=submit_game).pack(pady=10)

            # Cancel button
            tk.Button(add_game_frame, text="Cancel", command=add_game_frame.destroy).pack(pady=5)

        threading.Thread(target=add_game_thread).start()

    def delete_game(self):
        def delete_game_thread():
            games = list_games()
            if not games:
                messagebox.showinfo("No Games", "No games available to delete.")
                return

            # Create a selection dialog within the main window
            list_win = tk.Frame(self.root, borderwidth=2, relief="solid")
            list_win.place(relx=0.5, rely=0.5, anchor="center")  # Center the window in the main application
            tk.Label(list_win, text="Select a game to delete or scan a barcode:", pady=10).pack()

            # Listbox for game selection
            listbox = tk.Listbox(list_win, width=50, height=15)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to = game
                location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}")
            listbox.pack(pady=10)

            def confirm_delete():
                selected_index = listbox.curselection()
                if selected_index:
                    selected_game = games[selected_index[0]]
                    delete_game(selected_game[1])  # Delete using the barcode
                    messagebox.showinfo("Success", f"Game '{selected_game[0]}' deleted.")
                    list_win.destroy()
                else:
                    messagebox.showerror("Error", "No game selected.")

            def scan_barcode():
                barcode = simpledialog.askstring("Scan Barcode", "Scan or enter the barcode:")
                if not barcode:
                    return
                delete_game(barcode)
                messagebox.showinfo("Success", "Game deleted.")
                list_win.destroy()

            # Buttons for confirmation or scanning
            tk.Button(list_win, text="Delete Selected Game", command=confirm_delete).pack(pady=5)
            tk.Button(list_win, text="Scan Barcode", command=scan_barcode).pack(pady=5)
            tk.Button(list_win, text="Cancel", command=list_win.destroy).pack(pady=5)

        threading.Thread(target=delete_game_thread).start()

    def loan_game(self):
        def loan_game_thread():
            # Create a frame for loaning a game
            loan_game_frame = tk.Frame(self.root, borderwidth=2, relief="solid")
            loan_game_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame in the main application

            tk.Label(loan_game_frame, text="Loan Game", pady=10).pack()

            # List of games
            games = list_games()
            if not games:
                messagebox.showinfo("No Games", "No games available to loan.")
                loan_game_frame.destroy()
                return

            tk.Label(loan_game_frame, text="Select a game to loan or scan a barcode:", pady=10).pack()

            # Listbox for game selection
            listbox = tk.Listbox(loan_game_frame, width=50, height=15)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to = game
                location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}")
            listbox.pack(pady=10)

            # Borrower input
            tk.Label(loan_game_frame, text="Borrower's Name:").pack()
            borrower_entry = tk.Entry(loan_game_frame, width=30)
            borrower_entry.pack(pady=5)

            def confirm_loan():
                selected_index = listbox.curselection()
                borrower = borrower_entry.get()
                if not borrower:
                    messagebox.showerror("Error", "Borrower's name is required.")
                    return

                if selected_index:
                    selected_game = games[selected_index[0]]
                    loan_game(selected_game[1], borrower)  # Loan using the barcode
                    messagebox.showinfo("Success", f"Game '{selected_game[0]}' loaned to {borrower}.")
                    loan_game_frame.destroy()
                else:
                    messagebox.showerror("Error", "No game selected.")

            def scan_barcode():
                barcode = simpledialog.askstring("Scan Barcode", "Scan or enter the barcode:")
                borrower = borrower_entry.get()
                if not barcode or not borrower:
                    messagebox.showerror("Error", "Both barcode and borrower's name are required.")
                    return
                loan_game(barcode, borrower)
                messagebox.showinfo("Success", "Game loaned.")
                loan_game_frame.destroy()

            # Buttons for confirmation or scanning
            tk.Button(loan_game_frame, text="Loan Selected Game", command=confirm_loan).pack(pady=5)
            tk.Button(loan_game_frame, text="Scan Barcode", command=scan_barcode).pack(pady=5)
            tk.Button(loan_game_frame, text="Cancel", command=loan_game_frame.destroy).pack(pady=5)

        threading.Thread(target=loan_game_thread).start()

    def return_game(self):
        def return_game_thread():
            # Create a frame for returning a game
            return_game_frame = tk.Frame(self.root, borderwidth=2, relief="solid")
            return_game_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame in the main application

            tk.Label(return_game_frame, text="Return Game", pady=10).pack()

            # List of games
            games = list_games()
            if not games:
                messagebox.showinfo("No Games", "No games available to return.")
                return_game_frame.destroy()
                return

            tk.Label(return_game_frame, text="Select a game to return or scan a barcode:", pady=10).pack()

            # Listbox for game selection
            listbox = tk.Listbox(return_game_frame, width=50, height=15)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to = game
                location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}")
            listbox.pack(pady=10)

            def confirm_return():
                selected_index = listbox.curselection()
                if selected_index:
                    selected_game = games[selected_index[0]]
                    return_game(selected_game[1])  # Return using the barcode
                    messagebox.showinfo("Success", f"Game '{selected_game[0]}' returned.")
                    return_game_frame.destroy()
                else:
                    messagebox.showerror("Error", "No game selected.")

            def scan_barcode():
                barcode = simpledialog.askstring("Scan Barcode", "Scan or enter the barcode:")
                if not barcode:
                    messagebox.showerror("Error", "Barcode is required.")
                    return
                return_game(barcode)
                messagebox.showinfo("Success", "Game returned.")
                return_game_frame.destroy()

            # Buttons for confirmation or scanning
            tk.Button(return_game_frame, text="Return Selected Game", command=confirm_return).pack(pady=5)
            tk.Button(return_game_frame, text="Scan Barcode", command=scan_barcode).pack(pady=5)
            tk.Button(return_game_frame, text="Cancel", command=return_game_frame.destroy).pack(pady=5)

        threading.Thread(target=return_game_thread).start()

    def list_games(self):
        def list_games_thread():
            games = list_games()
            list_win = tk.Frame(self.root, borderwidth=2, relief="solid")
            list_win.place(relx=0.5, rely=0.5, anchor="center")  # Center the window in the main application
            tk.Label(list_win, text="Game List", pady=10).pack()
            text = tk.Text(list_win, wrap="word", width=80, height=20)
            text.pack(padx=10, pady=10)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to = game
                location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                text.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}\n")
            text.config(state=tk.DISABLED)
            tk.Button(list_win, text="Close", command=list_win.destroy).pack(pady=5)

        threading.Thread(target=list_games_thread).start()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Board Game Tracker")
    root.wm_minsize(width=800, height=600)  # Set minimum window size
    app = BoardGameApp(root)
    root.mainloop()
