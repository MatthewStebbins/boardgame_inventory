import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import threading
import os
from db import init_db, add_game, loan_game, return_game, list_games, delete_game, get_game_by_barcode, list_loaned_games, update_game_location
from api import lookup_barcode
from util import validate_location_barcode, update_entry, show_error, show_info

class BoardGameApp:
    """
    Main application class for the Board Game Inventory Tracker GUI.
    Handles all user interactions and database operations.
    """
    def bulk_upload(self):
        """Open the bulk upload dialog for adding multiple games."""
        def bulk_upload_thread():
            """Threaded function for bulk upload dialog."""
            if self.current_frame:
                self.current_frame.destroy()
            bulk_frame = tk.Frame(self.root, borderwidth=2, relief="groove", bg="#f7f7fa")
            bulk_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = bulk_frame
            tk.Label(bulk_frame, text="Bulk Upload Games", font=("Segoe UI", 15, "bold"), pady=12, bg="#f7f7fa").pack()
            form = tk.Frame(bulk_frame, bg="#f7f7fa")
            form.pack(pady=8)
            tk.Label(form, text="Scan Location Barcode (xx-xx):", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=0, column=0, sticky="e", pady=4, padx=4)
            location_barcode_entry = tk.Entry(form, width=24, font=("Segoe UI", 10))
            location_barcode_entry.grid(row=0, column=1, pady=4, padx=4)
            tk.Label(form, text="Bookcase:", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=1, column=0, sticky="e", pady=4, padx=4)
            bookcase_entry = tk.Entry(form, width=24, font=("Segoe UI", 10))
            bookcase_entry.grid(row=1, column=1, pady=4, padx=4)
            tk.Label(form, text="Shelf:", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=2, column=0, sticky="e", pady=4, padx=4)
            shelf_entry = tk.Entry(form, width=24, font=("Segoe UI", 10))
            shelf_entry.grid(row=2, column=1, pady=4, padx=4)

            def on_location_barcode_change(event):
                """Update bookcase/shelf fields when location barcode changes."""
                loc_barcode = location_barcode_entry.get()
                bookcase_val, shelf_val = validate_location_barcode(loc_barcode)
                if bookcase_val and shelf_val:
                    update_entry(bookcase_entry, bookcase_val)
                    update_entry(shelf_entry, shelf_val)
            def on_location_barcode_focus_out(event):
                """Validate location barcode on focus out."""
                loc_barcode = location_barcode_entry.get()
                validate_location_barcode(loc_barcode)
            location_barcode_entry.bind('<KeyRelease>', on_location_barcode_change)
            location_barcode_entry.bind('<FocusOut>', on_location_barcode_focus_out)

            scanned_barcodes = []
            tk.Label(bulk_frame, text="Scanned Barcodes:", font=("Segoe UI", 10, "bold"), bg="#f7f7fa").pack(pady=(8, 2))
            scanned_listbox = tk.Listbox(bulk_frame, width=40, height=7, font=("Segoe UI", 10), bg="#fff", relief="solid", bd=1)
            scanned_listbox.pack(pady=2)
            tk.Label(bulk_frame, text="Scan each game barcode below:", font=("Segoe UI", 10), bg="#f7f7fa").pack(pady=(8, 2))
            barcode_entry = tk.Entry(bulk_frame, width=24, font=("Segoe UI", 10))
            barcode_entry.pack(pady=4)

            def process_barcode(barcode):
                barcode = barcode.strip()
                if not barcode or barcode in scanned_barcodes:
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

            scan_btn = tk.Button(bulk_frame, text="Scan Barcode", command=scan_barcode, font=("Segoe UI", 10), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=8, pady=4)
            scan_btn.pack(pady=2)

            from util import show_error, show_info
            def finish_bulk_upload():
                bookcase = bookcase_entry.get().strip()
                shelf = shelf_entry.get().strip()
                if not (bookcase and shelf):
                    show_error("Error", "Bookcase and Shelf are required.")
                    return
                if not scanned_barcodes:
                    show_error("Error", "No barcodes scanned.")
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
                show_info("Bulk Upload Complete", summary)
                bulk_frame.destroy()

            btns = tk.Frame(bulk_frame, bg="#f7f7fa")
            btns.pack(pady=12)
            tk.Button(btns, text="Done", command=finish_bulk_upload, font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
            tk.Button(btns, text="Cancel", command=bulk_frame.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        threading.Thread(target=bulk_upload_thread).start()
    def __init__(self, root):
        """Initialize the main application window and database."""
        self.root = root
        self.root.title("Board Game Tracker")
        self.current_frame = None  # Ensure current_frame is always initialized
        self.button_frame = None
        self.content_frame = None
        self.build_gui()
        threading.Thread(target=init_db).start()  # Initialize the database in a separate thread

    def build_gui(self):
        """Build the main GUI layout and buttons."""
        # Import styles and widgets
        from styles import PRIMARY, ACCENT, BG, CARD, DANGER, TEXT, BTN_TEXT, BORDER, RoundedButton

        self.button_frame = tk.Frame(self.root, bg=BG)
        self.button_frame.pack(pady=18, fill=tk.X)
        self.button_frame.grid_columnconfigure(0, weight=1)
        inner_frame = tk.Frame(self.button_frame, bg=BG)
        inner_frame.pack(fill=tk.X)
        btns = [
            ("Add Game by Barcode", self.add_game, PRIMARY),
            ("Bulk Upload", self.bulk_upload, PRIMARY),
            ("Loan Game", self.loan_game, PRIMARY),
            ("Return Game", self.return_game, PRIMARY),
            ("List Games", self.list_games, PRIMARY),
            ("Delete Game", self.delete_game, DANGER),
            ("Export CSV/Excel", self.export_games, ACCENT),
            ("Import CSV/Excel", self.import_games, ACCENT),
            ("Exit", self.root.quit, BORDER)
        ]
        self.button_widgets = []
        def make_callback(c):
            return lambda: c()
        for idx, (text, cmd, color) in enumerate(btns):
            btn = RoundedButton(inner_frame, text=text, btnbackground=color, btnforeground=BTN_TEXT if color != BORDER else TEXT, clicked=make_callback(cmd), width=150, height=44)
            btn.grid(row=0, column=idx, padx=7, pady=2, sticky="ew")
            inner_frame.grid_columnconfigure(idx, weight=1)
            self.button_widgets.append(btn)

        def update_button_layout(event):
            total_width = inner_frame.winfo_width()
            btn_width = 164  # 150 + 2*7 padding
            max_per_row = max(1, total_width // btn_width)
            for i, btn in enumerate(self.button_widgets):
                row = i // max_per_row
                col = i % max_per_row
                btn.grid(row=row, column=col, padx=7, pady=6, sticky="ew")
                inner_frame.grid_columnconfigure(col, weight=1)
        inner_frame.bind('<Configure>', update_button_layout)

        # Content frame for dialogs
        self.content_frame = tk.Frame(self.root, bg=BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def export_games(self):
        """Open the export dialog for saving games to CSV or Excel."""
        import pandas as pd
        from tkinter import filedialog
        if self.current_frame:
            self.current_frame.destroy()
        export_frame = tk.Frame(self.content_frame, borderwidth=2, relief="groove", bg="#f7f7fa")
        export_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
        self.current_frame = export_frame
        tk.Label(export_frame, text="Export Games", font=("Segoe UI", 15, "bold"), pady=12, bg="#f7f7fa").pack()
        tk.Label(export_frame, text="Export your games to a CSV or Excel file.", font=("Segoe UI", 10), bg="#f7f7fa").pack(pady=(0, 12))

        def do_export(fmt):
            try:
                games = list_games()
                if not games:
                    messagebox.showinfo("No Games", "No games to export.")
                    return
                columns = ["name", "barcode", "bookcase", "shelf", "loaned_to", "description", "image_url"]
                df = pd.DataFrame(games, columns=columns)
                if fmt == "csv":
                    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
                    if not file_path:
                        return
                    df.to_csv(file_path, index=False)
                else:
                    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
                    if not file_path:
                        return
                    df.to_excel(file_path, index=False)
                messagebox.showinfo("Export Complete", f"Games exported to {os.path.basename(file_path)}.")
                export_frame.destroy()
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")

        btns = tk.Frame(export_frame, bg="#f7f7fa")
        btns.pack(pady=12)
        tk.Button(btns, text="Export as CSV", command=lambda: do_export("csv"), font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        tk.Button(btns, text="Export as Excel", command=lambda: do_export("excel"), font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        tk.Button(btns, text="Cancel", command=export_frame.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)

    def import_games(self):
        """Open the import dialog for loading games from CSV or Excel."""
        import pandas as pd
        from tkinter import filedialog
        if self.current_frame:
            self.current_frame.destroy()
        import_frame = tk.Frame(self.content_frame, borderwidth=2, relief="groove", bg="#f7f7fa")
        import_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
        self.current_frame = import_frame
        tk.Label(import_frame, text="Import Games", font=("Segoe UI", 15, "bold"), pady=12, bg="#f7f7fa").pack()
        tk.Label(import_frame, text="Import games from a CSV or Excel file. You can choose to overwrite the database or add to it.", font=("Segoe UI", 10), bg="#f7f7fa").pack(pady=(0, 12))

        def do_import(fmt):
            try:
                if fmt == "csv":
                    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
                    if not file_path:
                        return
                    df = pd.read_csv(file_path)
                else:
                    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
                    if not file_path:
                        return
                    df = pd.read_excel(file_path)
                required_cols = {"name", "barcode", "bookcase", "shelf"}
                if not required_cols.issubset(df.columns):
                    messagebox.showerror("Import Error", f"File must contain columns: {', '.join(required_cols)}")
                    return
                # Prompt user: Overwrite or Add
                overwrite = messagebox.askyesno("Import Option", "Do you want to overwrite the entire database with this import? (Yes = Overwrite, No = Add)")
                from db import get_game_by_barcode
                if overwrite:
                    # Clear the games table
                    import sqlite3
                    try:
                        conn = sqlite3.connect('games.db')
                        c = conn.cursor()
                        c.execute('DELETE FROM games')
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        messagebox.showerror("Database Error", f"Failed to clear database: {e}")
                        return
                added, skipped = 0, 0
                for _, row in df.iterrows():
                    barcode = str(row.get("barcode", "")).strip()
                    if not barcode:
                        continue
                    if not overwrite and get_game_by_barcode(barcode):
                        skipped += 1
                        continue
                    name = str(row.get("name", "Unknown Title"))
                    bookcase = str(row.get("bookcase", ""))
                    shelf = str(row.get("shelf", ""))
                    description = str(row.get("description", "")) if "description" in df.columns else None
                    image_url = str(row.get("image_url", "")) if "image_url" in df.columns else None
                    add_game(name, barcode, bookcase, shelf, description, image_url)
                    added += 1
                if overwrite:
                    messagebox.showinfo("Import Complete", f"Database overwritten. Imported {added} games.")
                else:
                    messagebox.showinfo("Import Complete", f"Added {added} games. Skipped {skipped} (already exist).")
                import_frame.destroy()
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import: {e}")

        btns = tk.Frame(import_frame, bg="#f7f7fa")
        btns.pack(pady=12)
        tk.Button(btns, text="Import from CSV", command=lambda: do_import("csv"), font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        tk.Button(btns, text="Import from Excel", command=lambda: do_import("excel"), font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        tk.Button(btns, text="Cancel", command=import_frame.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
    def list_games(self):
        """Open the dialog to list all games in the inventory."""
        def list_games_thread():
            if self.current_frame:
                self.current_frame.destroy()
            games = list_games()
            list_win = tk.Frame(self.content_frame, borderwidth=2, relief="groove", bg="#f7f7fa")
            list_win.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
            self.current_frame = list_win
            tk.Label(list_win, text="Game List", font=("Segoe UI", 16, "bold"), pady=16, bg="#f7f7fa").pack()
            if not games:
                tk.Label(list_win, text="No games available.", font=("Segoe UI", 12), bg="#f7f7fa", fg="#E57373").pack(pady=24)
                close_btn = tk.Button(list_win, text="Close", command=list_win.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=8, pady=4)
                close_btn.pack(pady=(0, 12), side=tk.BOTTOM)
                return
            content_frame = tk.Frame(list_win, bg="#f7f7fa")
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            left_frame = tk.Frame(content_frame, borderwidth=1, relief="ridge", bg="#fff")
            left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16), pady=0)
            right_frame = tk.Frame(content_frame, borderwidth=1, relief="ridge", bg="#fff")
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)

            tk.Label(left_frame, text="Select a game:", font=("Segoe UI", 11, "bold"), bg="#f7f7fa").pack(pady=(8, 4))
            listbox_frame = tk.Frame(left_frame, bg="#f7f7fa")
            listbox_frame.pack(padx=8, pady=(0, 8))
            listbox = tk.Listbox(listbox_frame, width=32, height=18, font=("Segoe UI", 10), activestyle="dotbox", selectbackground="#0078d7", selectforeground="#fff")
            scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
            listbox.config(yscrollcommand=scrollbar.set)
            listbox.grid(row=0, column=0, sticky="nsew")
            scrollbar.grid(row=0, column=1, sticky="ns")
            listbox_frame.grid_rowconfigure(0, weight=1)
            listbox_frame.grid_columnconfigure(0, weight=1)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to, description, image_url = game
                location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode})")

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
                    self.current_frame = None
                    self.list_games()  # Refresh the list

            button_frame = tk.Frame(left_frame, bg="#f7f7fa")
            button_frame.pack(pady=(0, 8))
            from tkinter import ttk
            ttk.Button(button_frame, text="Delete Selected Game", command=delete_selected_game, style='Rounded.TButton').pack(fill=tk.X, pady=2)

            tk.Label(right_frame, text="Game Details", font=("Segoe UI", 13, "bold"), bg="#f7f7fa").pack(pady=(8, 4))
            details_inner = tk.Frame(right_frame, bg="#f7f7fa")
            details_inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
            title_label = tk.Label(details_inner, text="Title: ", anchor="w", font=("Segoe UI", 11), bg="#f7f7fa")
            title_label.pack(fill=tk.X, padx=2, pady=2)
            barcode_label = tk.Label(details_inner, text="Barcode: ", anchor="w", font=("Segoe UI", 10), bg="#f7f7fa")
            barcode_label.pack(fill=tk.X, padx=2, pady=2)
            description_label = tk.Label(details_inner, text="Description:", anchor="w", font=("Segoe UI", 10, "bold"), bg="#f7f7fa")
            description_label.pack(fill=tk.X, padx=2, pady=(8, 2))
            description_text = tk.Text(details_inner, wrap=tk.WORD, height=6, width=60, font=("Segoe UI", 10), bg="#f7f7fa", relief="solid", bd=1)
            description_text.pack(fill=tk.X, padx=2, pady=2)
            location_label = tk.Label(details_inner, text="Location: ", anchor="w", font=("Segoe UI", 10), bg="#f7f7fa")
            location_label.pack(fill=tk.X, padx=2, pady=2)
            image_canvas = tk.Canvas(details_inner, width=200, height=200, bg="#fff", bd=1, relief="solid", highlightthickness=0)
            image_canvas.pack(padx=2, pady=8)

            import requests
            from PIL import Image, ImageTk
            import io
            def show_details(event):
                selected_index = listbox.curselection()
                if selected_index:
                    selected_game = games[selected_index[0]]
                    name, barcode, bookcase, shelf, loaned_to, description, image_url = selected_game
                    location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                    desc = description if description else "No description available."
                    img_url = image_url if image_url else None
                    image_loaded = False
                    image_canvas.delete("all")
                    data = None
                    if img_url:
                        try:
                            response = requests.get(img_url)
                            if response.status_code == 200:
                                img_data = response.content
                                pil_image = Image.open(io.BytesIO(img_data))
                                pil_image = pil_image.resize((200, 200))
                                image_obj = ImageTk.PhotoImage(pil_image)
                                image_canvas.create_image(100, 100, image=image_obj)
                                image_canvas.image = image_obj
                                image_loaded = True
                        except Exception:
                            image_loaded = False
                    if not image_loaded:
                        data = lookup_barcode(barcode)
                    images = data.get("images") if data else None
                    if images and isinstance(images, list):
                        img_url_api = images[0]
                    else:
                        img_url_api = None
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
                                    image_canvas.create_text(100, 100, text="No image available.", font=("Segoe UI", 10))
                            except Exception:
                                image_canvas.create_text(100, 100, text="Image load error", font=("Segoe UI", 10))
                        else:
                            image_canvas.create_text(100, 100, text="No image available.", font=("Segoe UI", 10))
                    title_label.config(text=f"Title: {name}")
                    barcode_label.config(text=f"Barcode: {barcode}")
                    description_text.config(state=tk.NORMAL)
                    description_text.delete(1.0, tk.END)
                    description_text.insert(tk.END, desc)
                    description_text.config(state=tk.DISABLED)
                    location_label.config(text=f"Location: {location}")
            listbox.bind("<<ListboxSelect>>", show_details)

            close_btn = tk.Button(list_win, text="Close", command=list_win.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=8, pady=4)
            close_btn.pack(pady=(0, 12), side=tk.BOTTOM)
        threading.Thread(target=list_games_thread).start()

    def add_game(self):
        """Open the dialog to add a new game by barcode."""
        def add_game_thread():
            if self.current_frame:
                self.current_frame.destroy()
            add_game_frame = tk.Frame(self.root, borderwidth=2, relief="groove", bg="#f7f7fa")
            add_game_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = add_game_frame
            tk.Label(add_game_frame, text="Add Game by Barcode", font=("Segoe UI", 15, "bold"), pady=12, bg="#f7f7fa").pack()
            form = tk.Frame(add_game_frame, bg="#f7f7fa")
            form.pack(pady=8)
            tk.Label(form, text="Barcode:", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=0, column=0, sticky="e", pady=4, padx=4)
            barcode_entry = tk.Entry(form, width=24, font=("Segoe UI", 10))
            barcode_entry.grid(row=0, column=1, pady=4, padx=4)
            tk.Label(form, text="Location Barcode (xx-xx):", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=1, column=0, sticky="e", pady=4, padx=4)
            location_barcode_entry = tk.Entry(form, width=24, font=("Segoe UI", 10))
            location_barcode_entry.grid(row=1, column=1, pady=4, padx=4)
            tk.Label(form, text="Bookcase:", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=2, column=0, sticky="e", pady=4, padx=4)
            bookcase_entry = tk.Entry(form, width=24, font=("Segoe UI", 10))
            bookcase_entry.grid(row=2, column=1, pady=4, padx=4)
            tk.Label(form, text="Shelf:", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=3, column=0, sticky="e", pady=4, padx=4)
            shelf_entry = tk.Entry(form, width=24, font=("Segoe UI", 10))
            shelf_entry.grid(row=3, column=1, pady=4, padx=4)

            from util import validate_location_barcode, update_entry, show_error, show_info
            def on_location_barcode_change(event):
                loc_barcode = location_barcode_entry.get()
                bookcase_val, shelf_val = validate_location_barcode(loc_barcode)
                if bookcase_val and shelf_val:
                    update_entry(bookcase_entry, bookcase_val)
                    update_entry(shelf_entry, shelf_val)
            def on_location_barcode_focus_out(event):
                loc_barcode = location_barcode_entry.get()
                validate_location_barcode(loc_barcode)
            location_barcode_entry.bind('<KeyRelease>', on_location_barcode_change)
            location_barcode_entry.bind('<FocusOut>', on_location_barcode_focus_out)
            from db import get_game_by_barcode
            def submit_game():
                barcode = barcode_entry.get()
                bookcase = bookcase_entry.get()
                shelf = shelf_entry.get()
                if not barcode:
                    show_error("Error", "Barcode is required.")
                    return
                db_game = get_game_by_barcode(barcode)
                if db_game:
                    name = db_game[0]
                    description = db_game[5]
                    image_url = db_game[6]
                else:
                    data = lookup_barcode(barcode)
                    if not data:
                        show_error("Error", "No data found for that barcode.")
                        return
                    name = data.get('title', 'Unknown Title')
                    description = data.get('description', None)
                    images = data.get('images')
                    if images and isinstance(images, list):
                        image_url = images[0]
                    else:
                        image_url = None
                add_game(name, barcode, bookcase, shelf, description, image_url)
                show_info("Success", f"Game '{name}' added.")
                add_game_frame.destroy()

            btns = tk.Frame(add_game_frame, bg="#f7f7fa")
            btns.pack(pady=12)
            tk.Button(btns, text="Submit", command=submit_game, font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
            tk.Button(btns, text="Cancel", command=add_game_frame.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        threading.Thread(target=add_game_thread).start()

    def delete_game(self):
        """Open the dialog to delete a game from the inventory."""
        def delete_game_thread():
            if self.current_frame:
                self.current_frame.destroy()
            games = list_games()
            list_win = tk.Frame(self.root, borderwidth=2, relief="groove", bg="#f7f7fa")
            list_win.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = list_win
            tk.Label(list_win, text="Delete Game", font=("Segoe UI", 15, "bold"), pady=12, bg="#f7f7fa").pack()
            if not games:
                tk.Label(list_win, text="No games available to delete.", font=("Segoe UI", 12), bg="#f7f7fa", fg="#E57373").pack(pady=24)
                close_btn = tk.Button(list_win, text="Close", command=list_win.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=8, pady=4)
                close_btn.pack(pady=(0, 12), side=tk.BOTTOM)
                return
            listbox = tk.Listbox(list_win, width=40, height=15, font=("Segoe UI", 10), bg="#fff", relief="solid", bd=1)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to, *_ = game
                location = f"{bookcase}, Shelf {shelf}" if not loaned_to else f"Loaned to {loaned_to}"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}")
            listbox.pack(padx=12, pady=8)
            def confirm_delete():
                selected_index = listbox.curselection()
                if selected_index:
                    selected_game = games[selected_index[0]]
                    delete_game(selected_game[1])
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
            btns = tk.Frame(list_win, bg="#f7f7fa")
            btns.pack(pady=10)
            tk.Button(btns, text="Delete Selected Game", command=confirm_delete, font=("Segoe UI", 10, "bold"), bg="#e81123", fg="#fff", activebackground="#c50f1f", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
            tk.Button(btns, text="Scan Barcode", command=scan_barcode, font=("Segoe UI", 10), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
            tk.Button(btns, text="Cancel", command=list_win.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        threading.Thread(target=delete_game_thread).start()

    def loan_game(self):
        """Open the dialog to loan a game to someone."""
        def loan_game_thread():
            if self.current_frame:
                self.current_frame.destroy()
            loan_game_frame = tk.Frame(self.root, borderwidth=2, relief="groove", bg="#f7f7fa")
            loan_game_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = loan_game_frame
            tk.Label(loan_game_frame, text="Loan Game", font=("Segoe UI", 15, "bold"), pady=12, bg="#f7f7fa").pack()
            games = list_games()
            available_games = [game for game in games if not game[4]]
            if not available_games:
                tk.Label(loan_game_frame, text="No games to loan.", font=("Segoe UI", 12), bg="#f7f7fa", fg="#E57373").pack(pady=24)
                close_btn = tk.Button(loan_game_frame, text="Close", command=loan_game_frame.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=8, pady=4)
                close_btn.pack(pady=(0, 12), side=tk.BOTTOM)
                return
            listbox = tk.Listbox(loan_game_frame, width=40, height=12, font=("Segoe UI", 10), bg="#fff", relief="solid", bd=1)
            for game in available_games:
                name, barcode, bookcase, shelf, loaned_to, *_ = game
                location = f"{bookcase}, Shelf {shelf}"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}")
            listbox.pack(padx=12, pady=8)
            form = tk.Frame(loan_game_frame, bg="#f7f7fa")
            form.pack(pady=4)
            tk.Label(form, text="Borrower's Name:", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=0, column=0, sticky="e", pady=4, padx=4)
            borrower_entry = tk.Entry(form, width=24, font=("Segoe UI", 10))
            borrower_entry.grid(row=0, column=1, pady=4, padx=4)
            def confirm_loan():
                selected_index = listbox.curselection()
                borrower = borrower_entry.get()
                if not borrower:
                    messagebox.showerror("Error", "Borrower's name is required.")
                    return
                if selected_index:
                    selected_game = available_games[selected_index[0]]
                    loan_game(selected_game[1], borrower)
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
            btns = tk.Frame(loan_game_frame, bg="#f7f7fa")
            btns.pack(pady=10)
            tk.Button(btns, text="Loan Selected Game", command=confirm_loan, font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
            tk.Button(btns, text="Scan Barcode", command=scan_barcode, font=("Segoe UI", 10), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
            tk.Button(btns, text="Cancel", command=loan_game_frame.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        threading.Thread(target=loan_game_thread).start()

    def return_game(self):
        """Open the dialog to mark a game as returned."""
        def return_game_thread():
            if self.current_frame:
                self.current_frame.destroy()
            return_game_frame = tk.Frame(self.root, borderwidth=2, relief="groove", bg="#f7f7fa")
            return_game_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_frame = return_game_frame
            tk.Label(return_game_frame, text="Return Game", font=("Segoe UI", 15, "bold"), pady=12, bg="#f7f7fa").pack()
            from db import list_loaned_games, update_game_location
            games = list_loaned_games()
            if not games:
                tk.Label(return_game_frame, text="No games  Loaned out.", font=("Segoe UI", 12), bg="#f7f7fa", fg="#E57373").pack(pady=24)
                close_btn = tk.Button(return_game_frame, text="Close", command=return_game_frame.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=8, pady=4)
                close_btn.pack(pady=(0, 12), side=tk.BOTTOM)
                return
            listbox = tk.Listbox(return_game_frame, width=40, height=12, font=("Segoe UI", 10), bg="#fff", relief="solid", bd=1)
            for game in games:
                name, barcode, bookcase, shelf, loaned_to, *_ = game
                location = f"{bookcase}, Shelf {shelf} (Loaned to {loaned_to})"
                listbox.insert(tk.END, f"{name} (Barcode: {barcode}) — Location: {location}")
            listbox.pack(padx=12, pady=8)
            location_frame = tk.Frame(return_game_frame, bg="#f7f7fa")
            location_frame.pack(pady=4)
            tk.Label(location_frame, text="Location Barcode (xx-xx):", font=("Segoe UI", 10), bg="#f7f7fa").grid(row=0, column=0, padx=5)
            location_barcode_entry = tk.Entry(location_frame, width=16, font=("Segoe UI", 10))
            location_barcode_entry.grid(row=0, column=1, padx=5)
            bookcase_label = tk.Label(location_frame, text="Bookcase:", font=("Segoe UI", 10), bg="#f7f7fa")
            bookcase_label.grid(row=0, column=2, padx=5)
            bookcase_entry = tk.Entry(location_frame, width=8, font=("Segoe UI", 10))
            bookcase_entry.grid(row=0, column=3, padx=5)
            shelf_label = tk.Label(location_frame, text="Shelf:", font=("Segoe UI", 10), bg="#f7f7fa")
            shelf_label.grid(row=0, column=4, padx=5)
            shelf_entry = tk.Entry(location_frame, width=8, font=("Segoe UI", 10))
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
                    location_barcode_entry.delete(0, tk.END)
            listbox.bind("<<ListboxSelect>>", fill_location_fields)
            def confirm_return():
                selected_index = listbox.curselection()
                if selected_index:
                    selected_game = games[selected_index[0]]
                    barcode = selected_game[1]
                    new_bookcase = bookcase_entry.get() or selected_game[2]
                    new_shelf = shelf_entry.get() or selected_game[3]
                    if new_bookcase != selected_game[2] or new_shelf != selected_game[3]:
                        try:
                            update_game_location(barcode, new_bookcase, new_shelf)
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to update location: {e}")
                            return
                    return_game(barcode)
                    messagebox.showinfo("Success", f"Game '{selected_game[0]}' returned to {new_bookcase}, Shelf {new_shelf}.")
                    return_game_frame.destroy()
                else:
                    messagebox.showerror("Error", "No game selected.")
            def scan_barcode():
                barcode = simpledialog.askstring("Scan Barcode", "Scan or enter the barcode:")
                if not barcode:
                    messagebox.showerror("Error", "Barcode is required.")
                    return
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
            btns = tk.Frame(return_game_frame, bg="#f7f7fa")
            btns.pack(pady=10)
            tk.Button(btns, text="Return Selected Game", command=confirm_return, font=("Segoe UI", 10, "bold"), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
            tk.Button(btns, text="Scan Barcode", command=scan_barcode, font=("Segoe UI", 10), bg="#0078d7", fg="#fff", activebackground="#005fa3", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
            tk.Button(btns, text="Cancel", command=return_game_frame.destroy, font=("Segoe UI", 10), bg="#e1e1e1", relief="flat", padx=10, pady=6).pack(side=tk.LEFT, padx=8)
        threading.Thread(target=return_game_thread).start()