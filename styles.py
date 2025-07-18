# styles.py
"""
Style constants and custom widgets for Board Game Inventory UI
"""

import tkinter as tk

# Color palette
PRIMARY = "#4F6D7A"      # Button, accent
ACCENT = "#C0D6DF"      # Button hover, accent
BG = "#F7F9FB"          # Background
CARD = "#FFFFFF"        # Card/dialog background
DANGER = "#E57373"      # Delete/danger
TEXT = "#222"
BTN_TEXT = "#fff"
BORDER = "#E0E4EA"

class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text:str="", radius=18, btnforeground=BTN_TEXT, btnbackground=PRIMARY, clicked=None, font=("Segoe UI", 11, "bold"), *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg=self.master["bg"], highlightthickness=0, bd=0)
        self.btnbackground = btnbackground
        self.clicked = clicked
        self.radius = radius
        self.rect = self.round_rectangle(0, 0, 0, 0, tags="button", radius=radius, fill=btnbackground)
        self.text = self.create_text(0, 0, text=text, tags="button", fill=btnforeground, font=font, justify="center")
        self.tag_bind("button", "<ButtonPress>", self.border)
        self.tag_bind("button", "<ButtonRelease>", self.border)
        self.bind("<Configure>", self.resize)
        text_rect = self.bbox(self.text)
        if int(self["width"]) < text_rect[2]-text_rect[0]:
            self["width"] = (text_rect[2]-text_rect[0]) + 18
        if int(self["height"]) < text_rect[3]-text_rect[1]:
            self["height"] = (text_rect[3]-text_rect[1]) + 18
    def round_rectangle(self, x1, y1, x2, y2, radius=18, update=False, **kwargs):
        points = [x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1]
        if not update:
            return self.create_polygon(points, **kwargs, smooth=True)
        else:
            self.coords(self.rect, points)
    def resize(self, event):
        text_bbox = self.bbox(self.text)
        radius = min(self.radius, event.width//2, event.height//2)
        width, height = event.width, event.height
        if event.width < text_bbox[2]-text_bbox[0]:
            width = text_bbox[2]-text_bbox[0] + 30
        if event.height < text_bbox[3]-text_bbox[1]:
            height = text_bbox[3]-text_bbox[1] + 30
        self.round_rectangle(5, 5, width-5, height-5, radius, update=True)
        bbox = self.bbox(self.rect)
        x = ((bbox[2]-bbox[0])/2) - ((text_bbox[2]-text_bbox[0])/2)
        y = ((bbox[3]-bbox[1])/2) - ((text_bbox[3]-text_bbox[1])/2)
        self.moveto(self.text, x, y)
    def border(self, event):
        if event.type == "4":
            self.itemconfig(self.rect, fill="#d2d6d3")
            if self.clicked is not None:
                self.clicked()
        else:
            self.itemconfig(self.rect, fill=self.btnbackground)
