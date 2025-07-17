import tkinter as tk
from tkinter import messagebox, simpledialog
from db import init_db, add_game, loan_game, return_game, list_games, delete_game
from api import lookup_barcode
import threading

class BoardGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Board Game Tracker")
        self.current_frame = None  # Ensure current_frame is always initialized
        self.build_gui()
        threading.Thread(target=init_db).start()  # Initialize the database in a separate thread

    def build_gui(self):
        # Create a horizontal frame for buttons, centered
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        # Center the button_frame in the window
        button_frame.grid_columnconfigure(0, weight=1)
        inner_frame = tk.Frame(button_frame)
        inner_frame.pack()
        # Add buttons to the horizontal frame, centered
        tk.Button(inner_frame, text="Add Game by Barcode", width=20, command=self.add_game).pack(side=tk.LEFT, padx=5)
        tk.Button(inner_frame, text="Bulk Upload", width=20, command=self.bulk_upload).pack(side=tk.LEFT, padx=5)
        tk.Button(inner_frame, text="Loan Game", width=20, command=self.loan_game).pack(side=tk.LEFT, padx=5)
        tk.Button(inner_frame, text="Return Game", width=20, command=self.return_game).pack(side=tk.LEFT, padx=5)
        tk.Button(inner_frame, text="List Games", width=20, command=self.list_games).pack(side=tk.LEFT, padx=5)
        tk.Button(inner_frame, text="Delete Game", width=20, command=self.delete_game).pack(side=tk.LEFT, padx=5)
        tk.Button(inner_frame, text="Exit", width=20, command=self.root.quit).pack(side=tk.LEFT, padx=5)


    def bulk_upload(self):
        def bulk_upload_thread():
            if self.current_frame:
                self.current_frame.destroy()
            bulk_frame = tk.Frame(self.root, borderwidth=2, relief="solid")
            bulk_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = bulk_frame
            tk.Label(bulk_frame, text="Bulk Upload Games", font=("Arial", 12, "bold"), pady=10).pack()
            tk.Label(bulk_frame, text="Scan Location Barcode (xx-xx):").pack()
            location_barcode_entry = tk.Entry(bulk_frame, width=30)
            location_barcode_entry.pack(pady=5)
            tk.Label(bulk_frame, text="Bookcase:").pack()
            bookcase_entry = tk.Entry(bulk_frame, width=30)
            bookcase_entry.pack(pady=5)
            tk.Label(bulk_frame, text="Shelf:").pack()
            shelf_entry = tk.Entry(bulk_frame, width=30)
            shelf_entry.pack(pady=5)

            def on_location_barcode_change(event):
                loc_barcode = location_barcode_entry.get()
                if '-' in loc_barcode:
                    parts = loc_barcode.split('-')
                    if len(parts) == 2:
                        bookcase_val = parts[0].strip()
                        shelf_val = parts[1].strip()
                        if bookcase_val and shelf_val:
                            bookcase_entry.delete(0, tk.END)
                            bookcase_entry.insert(0, bookcase_val)
                            shelf_entry.delete(0, tk.END)
                            shelf_entry.insert(0, shelf_val)
            def on_location_barcode_focus_out(event):
                loc_barcode = location_barcode_entry.get()
                if not loc_barcode:
                    return
                if '-' not in loc_barcode or len(loc_barcode.split('-')) != 2:
                    messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
                    return
                parts = loc_barcode.split('-')
                bookcase_val = parts[0].strip()
                shelf_val = parts[1].strip()
                if not (bookcase_val and shelf_val):
                    messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
            location_barcode_entry.bind('<KeyRelease>', on_location_barcode_change)
            location_barcode_entry.bind('<FocusOut>', on_location_barcode_focus_out)

            scanned_barcodes = []
            scanned_listbox = tk.Listbox(bulk_frame, width=50, height=10)
            scanned_listbox.pack(pady=10)
            tk.Label(bulk_frame, text="Scan each game barcode below:").pack()
            barcode_entry = tk.Entry(bulk_frame, width=30)
            barcode_entry.pack(pady=5)

            def process_barcode(barcode):
                barcode = barcode.strip()
                if not barcode:
                    return
                if barcode in scanned_barcodes:
                    return
                scanned_barcodes.append(barcode)
                scanned_listbox.insert(tk.END, barcode)

            def on_barcode_entry(event=None):
                barcode = barcode_entry.get()
                process_barcode(barcode)
                barcode_entry.delete(0, tk.END)

            barcode_entry.bind('<Return>', on_barcode_entry)
            barcode_entry.focus_set()

            def scan_barcode():
                barcode = simpledialog.askstring("Scan Barcode", "Scan or enter the game barcode:")
                if barcode:
                    process_barcode(barcode)

            tk.Button(bulk_frame, text="Scan Barcode", command=scan_barcode).pack(pady=2)

            def finish_bulk_upload():
                bookcase = bookcase_entry.get().strip()
                shelf = shelf_entry.get().strip()
                if not (bookcase and shelf):
                    messagebox.showerror("Error", "Bookcase and Shelf are required.")
                    return
                if not scanned_barcodes:
                    messagebox.showerror("Error", "No barcodes scanned.")
                    return
                from db import get_game_by_barcode
                added = []
                skipped = []
                for barcode in scanned_barcodes:
                    db_game = get_game_by_barcode(barcode)
                    if db_game:
                        name = db_game[0]
                        description = db_game[5]
                        image_url = db_game[6]
                    else:
                        data = lookup_barcode(barcode)
                        if not data:
                            skipped.append(barcode)
                            continue
                        name = data.get('title', 'Unknown Title')
                        description = data.get('description', None)
                        image_url = data.get('images', [None])[0]
                    add_game(name, barcode, bookcase, shelf, description, image_url)
                    added.append(barcode)
                summary = f"Added {len(added)} games."
                if skipped:
                    summary += f"\nSkipped {len(skipped)} (no data found):\n" + ", ".join(skipped)
                messagebox.showinfo("Bulk Upload Complete", summary)
                bulk_frame.destroy()

            tk.Button(bulk_frame, text="Done", command=finish_bulk_upload).pack(pady=10)
            tk.Button(bulk_frame, text="Cancel", command=bulk_frame.destroy).pack(pady=5)
        threading.Thread(target=bulk_upload_thread).start()

    def add_game(self):
        def add_game_thread():
            if self.current_frame:
                self.current_frame.destroy()
            add_game_frame = tk.Frame(self.root, borderwidth=2, relief="solid")
            add_game_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = add_game_frame
            tk.Label(add_game_frame, text="Add Game by Barcode", pady=10).pack()
            tk.Label(add_game_frame, text="Barcode:").pack()
            barcode_entry = tk.Entry(add_game_frame, width=30)
            barcode_entry.pack(pady=5)
            tk.Label(add_game_frame, text="Location Barcode (xx-xx):").pack()
            location_barcode_entry = tk.Entry(add_game_frame, width=30)
            location_barcode_entry.pack(pady=5)
            tk.Label(add_game_frame, text="Bookcase:").pack()
            bookcase_entry = tk.Entry(add_game_frame, width=30)
            bookcase_entry.pack(pady=5)
            tk.Label(add_game_frame, text="Shelf:").pack()
            shelf_entry = tk.Entry(add_game_frame, width=30)
            shelf_entry.pack(pady=5)

            def on_location_barcode_change(event):
                loc_barcode = location_barcode_entry.get()
                if '-' in loc_barcode:
                    parts = loc_barcode.split('-')
                    if len(parts) == 2:
                        bookcase_val = parts[0].strip()
                        shelf_val = parts[1].strip()
                        if bookcase_val and shelf_val:
                            bookcase_entry.delete(0, tk.END)
                            bookcase_entry.insert(0, bookcase_val)
                            shelf_entry.delete(0, tk.END)
                            shelf_entry.insert(0, shelf_val)
            def on_location_barcode_focus_out(event):
                loc_barcode = location_barcode_entry.get()
                if not loc_barcode:
                    return
                if '-' not in loc_barcode or len(loc_barcode.split('-')) != 2:
                    messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
                    return
                parts = loc_barcode.split('-')
                bookcase_val = parts[0].strip()
                shelf_val = parts[1].strip()
                if not (bookcase_val and shelf_val):
                    messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
            location_barcode_entry.bind('<KeyRelease>', on_location_barcode_change)
            location_barcode_entry.bind('<FocusOut>', on_location_barcode_focus_out)
            from db import get_game_by_barcode
            def submit_game():
                barcode = barcode_entry.get()
                bookcase = bookcase_entry.get()
                shelf = shelf_entry.get()
                if not barcode:
                    messagebox.showerror("Error", "Barcode is required.")
                    return
                # Try to get game info from DB first
                db_game = get_game_by_barcode(barcode)
                if db_game:
                    name = db_game[0]
                    description = db_game[5]
                    image_url = db_game[6]
                else:
                    data = lookup_barcode(barcode)
                    if not data:
                        messagebox.showerror("Error", "No data found for that barcode.")
                        return
                    name = data.get('title', 'Unknown Title')
                    description = data.get('description', None)
                    image_url = data.get('images', [None])[0]
                add_game(name, barcode, bookcase, shelf, description, image_url)
                messagebox.showinfo("Success", f"Game '{name}' added.")
                add_game_frame.destroy()

            tk.Button(add_game_frame, text="Submit", command=submit_game).pack(pady=10)
            tk.Button(add_game_frame, text="Cancel", command=add_game_frame.destroy).pack(pady=5)
        threading.Thread(target=add_game_thread).start()

    def delete_game(self):
        def delete_game_thread():
            if self.current_frame:
                self.current_frame.destroy()
            games = list_games()
            if not games:
                messagebox.showinfo("No Games", "No games available to delete.")
                return
            list_win = tk.Frame(self.root, borderwidth=2, relief="solid")
            list_win.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = list_win
            tk.Label(list_win, text="Select a game to delete or scan a barcode:", pady=10).pack()
            listbox = tk.Listbox(list_win, width=50, height=15)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to, *_ = game
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
            tk.Button(list_win, text="Delete Selected Game", command=confirm_delete).pack(pady=5)
            tk.Button(list_win, text="Scan Barcode", command=scan_barcode).pack(pady=5)
            tk.Button(list_win, text="Cancel", command=list_win.destroy).pack(pady=5)
        threading.Thread(target=delete_game_thread).start()

    def loan_game(self):
        def loan_game_thread():
            if self.current_frame:
                self.current_frame.destroy()
            loan_game_frame = tk.Frame(self.root, borderwidth=2, relief="solid")
            loan_game_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = loan_game_frame
            tk.Label(loan_game_frame, text="Loan Game", pady=10).pack()
            games = list_games()
            # Filter out games that are currently loaned out
            available_games = [game for game in games if not game[4]]  # loaned_to is at index 4
            if not available_games:
                messagebox.showinfo("No Games", "No games available to loan.")
                loan_game_frame.destroy()
                return
            tk.Label(loan_game_frame, text="Select a game to loan or scan a barcode:", pady=10).pack()
            listbox = tk.Listbox(loan_game_frame, width=50, height=15)
            for game in available_games:
                name, barcode, bookcase, shelf, loaned_to, *_ = game
                location = f"{bookcase}, Shelf {shelf}"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}")
            listbox.pack(pady=10)
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
                    selected_game = available_games[selected_index[0]]
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
            tk.Button(loan_game_frame, text="Loan Selected Game", command=confirm_loan).pack(pady=5)
            tk.Button(loan_game_frame, text="Scan Barcode", command=scan_barcode).pack(pady=5)
            tk.Button(loan_game_frame, text="Cancel", command=loan_game_frame.destroy).pack(pady=5)
        threading.Thread(target=loan_game_thread).start()

    def return_game(self):
        def return_game_thread():
            if self.current_frame:
                self.current_frame.destroy()
            return_game_frame = tk.Frame(self.root, borderwidth=2, relief="solid")
            return_game_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = return_game_frame
            tk.Label(return_game_frame, text="Return Game", pady=10).pack()
            from db import list_loaned_games, update_game_location
            games = list_loaned_games()
            if not games:
                messagebox.showinfo("No Games", "No games are currently loaned out.")
                return_game_frame.destroy()
                return
            tk.Label(return_game_frame, text="Select a loaned game to return or scan a barcode:", pady=10).pack()
            listbox = tk.Listbox(return_game_frame, width=50, height=15)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to, *_ = game
                location = f"{bookcase}, Shelf {shelf} (Loaned to {loaned_to})"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}")
            listbox.pack(pady=10)
            # Location barcode and change widgets (inline)
            location_frame = tk.Frame(return_game_frame)
            location_frame.pack(pady=5)
            tk.Label(location_frame, text="Location Barcode (xx-xx):").grid(row=0, column=0, padx=5)
            location_barcode_entry = tk.Entry(location_frame, width=20)
            location_barcode_entry.grid(row=0, column=1, padx=5)
            bookcase_label = tk.Label(location_frame, text="Bookcase:")
            bookcase_label.grid(row=0, column=2, padx=5)
            bookcase_entry = tk.Entry(location_frame, width=10)
            bookcase_entry.grid(row=0, column=3, padx=5)
            shelf_label = tk.Label(location_frame, text="Shelf:")
            shelf_label.grid(row=0, column=4, padx=5)
            shelf_entry = tk.Entry(location_frame, width=10)
            shelf_entry.grid(row=0, column=5, padx=5)

            def on_location_barcode_change(event):
                loc_barcode = location_barcode_entry.get()
                if '-' in loc_barcode:
                    parts = loc_barcode.split('-')
                    if len(parts) == 2:
                        bookcase_val = parts[0].strip()
                        shelf_val = parts[1].strip()
                        if bookcase_val and shelf_val:
                            bookcase_entry.delete(0, tk.END)
                            bookcase_entry.insert(0, bookcase_val)
                            shelf_entry.delete(0, tk.END)
                            shelf_entry.insert(0, shelf_val)
            def on_location_barcode_focus_out(event):
                loc_barcode = location_barcode_entry.get()
                if not loc_barcode:
                    return
                if '-' not in loc_barcode or len(loc_barcode.split('-')) != 2:
                    messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
                    return
                parts = loc_barcode.split('-')
                bookcase_val = parts[0].strip()
                shelf_val = parts[1].strip()
                if not (bookcase_val and shelf_val):
                    messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
            location_barcode_entry.bind('<KeyRelease>', on_location_barcode_change)
            location_barcode_entry.bind('<FocusOut>', on_location_barcode_focus_out)

            def fill_location_fields(event):
                selected_index = listbox.curselection()
                if selected_index:
                    selected_game = games[selected_index[0]]
                    bookcase_entry.delete(0, tk.END)
                    bookcase_entry.insert(0, selected_game[2])
                    shelf_entry.delete(0, tk.END)
                    shelf_entry.insert(0, selected_game[3])
                    # Optionally, clear location barcode field
                    location_barcode_entry.delete(0, tk.END)
            listbox.bind("<<ListboxSelect>>", fill_location_fields)
            def confirm_return():
                selected_index = listbox.curselection()
                if selected_index:
                    selected_game = games[selected_index[0]]
                    barcode = selected_game[1]
                    new_bookcase = bookcase_entry.get() or selected_game[2]
                    new_shelf = shelf_entry.get() or selected_game[3]
                    # Update location if changed
                    if new_bookcase != selected_game[2] or new_shelf != selected_game[3]:
                        try:
                            update_game_location(barcode, new_bookcase, new_shelf)
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to update location: {e}")
                            return
                    return_game(barcode)  # Return using the barcode
                    messagebox.showinfo("Success", f"Game '{selected_game[0]}' returned to {new_bookcase}, Shelf {new_shelf}.")
                    return_game_frame.destroy()
                else:
                    messagebox.showerror("Error", "No game selected.")
            def scan_barcode():
                barcode = simpledialog.askstring("Scan Barcode", "Scan or enter the barcode:")
                if not barcode:
                    messagebox.showerror("Error", "Barcode is required.")
                    return
                # Find the game by barcode
                selected_game = next((g for g in games if g[1] == barcode), None)
                if not selected_game:
                    messagebox.showerror("Error", "Barcode not found among loaned games.")
                    return
                new_bookcase = bookcase_entry.get() or selected_game[2]
                new_shelf = shelf_entry.get() or selected_game[3]
                if new_bookcase != selected_game[2] or new_shelf != selected_game[3]:
                    try:
                        update_game_location(barcode, new_bookcase, new_shelf)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to update location: {e}")
                        return
                return_game(barcode)
                messagebox.showinfo("Success", f"Game returned to {new_bookcase}, Shelf {new_shelf}.")
                return_game_frame.destroy()
            tk.Button(return_game_frame, text="Return Selected Game", command=confirm_return).pack(pady=5)
            tk.Button(return_game_frame, text="Scan Barcode", command=scan_barcode).pack(pady=5)
            tk.Button(return_game_frame, text="Cancel", command=return_game_frame.destroy).pack(pady=5)
        threading.Thread(target=return_game_thread).start()

    def list_games(self):
        def list_games_thread():
            if self.current_frame:
                self.current_frame.destroy()
            games = list_games()
            if not games:
                messagebox.showinfo("No Games", "No games available.")
                return
            list_win = tk.Frame(self.root, borderwidth=2, relief="solid")
            list_win.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = list_win
            tk.Label(list_win, text="Game List", font=("Arial", 12, "bold"), pady=10).pack()
            left_frame = tk.Frame(list_win, borderwidth=2, relief="solid")
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
            right_frame = tk.Frame(list_win, borderwidth=2, relief="solid")
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            tk.Label(left_frame, text="Select a game:", font=("Arial", 10)).pack(pady=5)
            listbox = tk.Listbox(left_frame, width=30, height=15)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to, description, image_url = game
                location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode})")
            listbox.pack(padx=10, pady=10)

            def delete_selected_game():
                selected_index = listbox.curselection()
                if not selected_index:
                    messagebox.showerror("Error", "No game selected.")
                    return
                selected_game = games[selected_index[0]]
                confirm = messagebox.askyesno("Delete Game", f"Are you sure you want to delete '{selected_game[0]}'?")
                if confirm:
                    delete_game(selected_game[1])
                    messagebox.showinfo("Success", f"Game '{selected_game[0]}' deleted.")
                    list_win.destroy()
                    self.list_games()  # Refresh the list

            tk.Button(left_frame, text="Delete Selected Game", command=delete_selected_game, fg="red").pack(pady=5)

            tk.Label(right_frame, text="Game Details", font=("Arial", 12, "bold")).pack(pady=5)
            title_label = tk.Label(right_frame, text="Title: ", anchor="w")
            title_label.pack(fill=tk.X, padx=5, pady=2)
            barcode_label = tk.Label(right_frame, text="Barcode: ", anchor="w")
            barcode_label.pack(fill=tk.X, padx=5, pady=2)
            description_text = tk.Text(right_frame, wrap=tk.WORD, height=6, width=60)
            description_text.pack(fill=tk.X, padx=5, pady=2)
            location_label = tk.Label(right_frame, text="Location: ", anchor="w")
            location_label.pack(fill=tk.X, padx=5, pady=2)
            image_canvas = tk.Canvas(right_frame, width=200, height=200)
            image_canvas.pack(padx=5, pady=2)
            import requests
            from PIL import Image, ImageTk
            import io
            def show_details(event):
                selected_index = listbox.curselection()
                if selected_index:
                    selected_game = games[selected_index[0]]
                    name, barcode, bookcase, shelf, loaned_to, description, image_url = selected_game
                    location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                    # Use DB info first, fallback to API if missing or image fails
                    desc = description if description else "No description available."
                    img_url = image_url if image_url else None
                    image_loaded = False
                    image_canvas.delete("all")
                    if img_url:
                        try:
                            response = requests.get(img_url)
                            if response.status_code == 200:
                                img_data = response.content
                                pil_image = Image.open(io.BytesIO(img_data))
                                pil_image = pil_image.resize((200, 200))
                                image_obj = ImageTk.PhotoImage(pil_image)
                                image_canvas.create_image(100, 100, image=image_obj)
                                image_canvas.image = image_obj  # Keep reference
                                image_loaded = True
                        except Exception:
                            image_loaded = False
                    if not image_loaded:
                        # Try API if DB image failed
                        data = lookup_barcode(barcode)
                        img_url_api = data.get("images", [None])[0] if data else None
                        desc = data.get("description", desc) if data else desc
                        if img_url_api:
                            try:
                                response = requests.get(img_url_api)
                                if response.status_code == 200:
                                    img_data = response.content
                                    pil_image = Image.open(io.BytesIO(img_data))
                                    pil_image = pil_image.resize((200, 200))
                                    image_obj = ImageTk.PhotoImage(pil_image)
                                    image_canvas.create_image(100, 100, image=image_obj)
                                    image_canvas.image = image_obj
                                else:
                                    image_canvas.create_text(100, 100, text="No image available.")
                            except Exception:
                                image_canvas.create_text(100, 100, text="Image load error")
                        else:
                            image_canvas.create_text(100, 100, text="No image available.")
                    title_label.config(text=f"Title: {name}")
                    barcode_label.config(text=f"Barcode: {barcode}")
                    description_text.config(state=tk.NORMAL)
                    description_text.delete(1.0, tk.END)
                    description_text.insert(tk.END, desc)
                    description_text.config(state=tk.DISABLED)
                    location_label.config(text=f"Location: {location}")
            listbox.bind("<<ListboxSelect>>", show_details)
            tk.Button(list_win, text="Close", command=list_win.destroy).pack(pady=5)
        threading.Thread(target=list_games_thread).start()
