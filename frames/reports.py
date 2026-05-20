import customtkinter as ctk

from frames.base import PageFrame
from ui_constants import BORDER_COLOR, CARD_BG, SOFT_CARD_BG
from utils.history import load_history


class ReportsFrame(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.grid_rowconfigure(1, weight=1)
        self.create_summary_cards()
        self.create_history_table()

    def create_summary_cards(self):
        self.summary = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.summary.grid(row=0, column=0, sticky="ew", padx=28, pady=(8, 18))
        self.summary.grid_columnconfigure(0, weight=1)
        self.summary.grid_columnconfigure(1, weight=1)
        self.summary.grid_columnconfigure(2, weight=1)
        self.summary.grid_columnconfigure(3, weight=1)

        self.best_role_value = self.create_metric(0, "Best Role", "Waiting")
        self.best_score_value = self.create_metric(1, "Best Score", "0%")
        self.history_count_value = self.create_metric(2, "Saved Reports", "0")
        self.skills_found_value = self.create_metric(3, "Skills Found", "0")

    def create_metric(self, column, title, value):
        card = ctk.CTkFrame(self.summary, corner_radius=14, fg_color=SOFT_CARD_BG)
        card.grid(row=0, column=column, sticky="nsew", padx=10, pady=12)
        card.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#64748b", "#94a3b8"),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 4))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
            wraplength=190,
        )
        value_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 16))
        return value_label

    def create_history_table(self):
        self.table = ctk.CTkScrollableFrame(
            self,
            corner_radius=16,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            label_text="Analysis History",
            label_font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.table.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        self.table.grid_columnconfigure(0, weight=2)
        self.table.grid_columnconfigure(1, weight=1)
        self.table.grid_columnconfigure(2, weight=1)
        self.table.grid_columnconfigure(3, weight=1)

    def refresh(self):
        self.controller.history = load_history()
        found_total = sum(len(result["found"]) for result in self.controller.analysis_results)
        self.best_role_value.configure(text=self.controller.best_role or "Waiting")
        self.best_score_value.configure(text=f"{self.controller.best_score}%")
        self.history_count_value.configure(text=str(len(self.controller.history)))
        self.skills_found_value.configure(text=str(found_total))
        self.render_history()

    def clear_table(self):
        for widget in self.table.winfo_children():
            widget.destroy()

    def render_history(self):
        self.clear_table()
        headers = ["Filename", "Date", "Best Role", "Score"]

        for column, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.table,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#64748b", "#94a3b8"),
                anchor="w",
            )
            label.grid(row=0, column=column, sticky="ew", padx=12, pady=(8, 10))

        if not self.controller.history:
            empty = ctk.CTkLabel(
                self.table,
                text="No analyzed resumes saved yet.",
                font=ctk.CTkFont(size=14),
                text_color=("#64748b", "#94a3b8"),
            )
            empty.grid(row=1, column=0, columnspan=4, pady=34)
            return

        for row, item in enumerate(self.controller.history, start=1):
            values = [
                item.get("filename", "-"),
                item.get("date", "-"),
                item.get("best_role", "-"),
                f"{item.get('score', 0)}%",
            ]
            for column, value in enumerate(values):
                cell = ctk.CTkLabel(
                    self.table,
                    text=value,
                    font=ctk.CTkFont(size=13, weight="bold" if column == 3 else "normal"),
                    anchor="w",
                    text_color=("#0f172a", "#e2e8f0") if column != 3 else ("#2563eb", "#60a5fa"),
                    fg_color=SOFT_CARD_BG,
                    corner_radius=8,
                )
                cell.grid(row=row, column=column, sticky="ew", padx=6, pady=5, ipady=9)
