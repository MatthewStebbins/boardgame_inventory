import tkinter as tk
from tkinter import messagebox

def validate_location_barcode(barcode):
    """Validate and parse a location barcode in the format xx-xx."""
    if not barcode or '-' not in barcode:
        messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
        return None, None
    parts = barcode.split('-')
    if len(parts) != 2:
        messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
        return None, None
    bookcase_val = parts[0].strip()
    shelf_val = parts[1].strip()
    if not (bookcase_val and shelf_val):
        messagebox.showerror("Error", "Invalid location barcode format. Use xx-xx.")
        return None, None
    return bookcase_val, shelf_val

def show_info(title, message):
    messagebox.showinfo(title, message)

def show_error(title, message):
    messagebox.showerror(title, message)

def confirm_action(title, message):
    return messagebox.askyesno(title, message)

def update_entry(entry, value):
    entry.delete(0, tk.END)
    entry.insert(0, value)
