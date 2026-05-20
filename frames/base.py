import customtkinter as ctk

from ui_constants import APP_BG


class PageFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, fg_color=APP_BG)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)

    def refresh(self):
        pass
