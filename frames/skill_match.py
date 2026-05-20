import customtkinter as ctk

from frames.base import PageFrame
from ui_constants import BORDER_COLOR, CARD_BG, ICON_CHECK, ICON_CIRCLE, ICON_RESUME, SOFT_CARD_BG


class SkillMatchFrame(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.grid_rowconfigure(1, weight=1)
        self.create_best_match_card()
        self.create_cards_container()

    def create_best_match_card(self):
        self.best_match = ctk.CTkFrame(
            self,
            corner_radius=18,
            fg_color=("#dbeafe", "#172554"),
            border_width=1,
            border_color=("#bfdbfe", "#1d4ed8"),
        )
        self.best_match.grid(row=0, column=0, sticky="ew", padx=28, pady=(8, 18))
        self.best_match.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            self.best_match,
            text="Best Match",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1d4ed8", "#93c5fd"),
            anchor="w",
        )
        label.grid(row=0, column=0, sticky="w", padx=22, pady=(20, 0))

        self.best_role_value = ctk.CTkLabel(
            self.best_match,
            text="Waiting for resume",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        )
        self.best_role_value.grid(row=1, column=0, sticky="w", padx=22, pady=(2, 22))

        self.best_score_value = ctk.CTkLabel(
            self.best_match,
            text="0%",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color=("#1d4ed8", "#60a5fa"),
            anchor="e",
        )
        self.best_score_value.grid(row=0, column=1, rowspan=2, sticky="e", padx=24, pady=18)

    def create_cards_container(self):
        self.cards_container = ctk.CTkScrollableFrame(
            self,
            corner_radius=16,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER_COLOR,
            label_text="Role Match Progress",
            label_font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.cards_container.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 24))
        self.cards_container.grid_columnconfigure(0, weight=1)

    def refresh(self):
        self.best_role_value.configure(text=self.controller.best_role or "Waiting for resume")
        self.best_score_value.configure(text=f"{self.controller.best_score}%")
        self.render_results()

    def clear_cards(self):
        for widget in self.cards_container.winfo_children():
            widget.destroy()

    def render_results(self):
        self.clear_cards()

        if not self.controller.analysis_results:
            self.show_empty_state()
            return

        results = sorted(self.controller.analysis_results, key=lambda item: item["score"], reverse=True)
        for index, result in enumerate(results):
            self.create_result_card(index, result)

    def show_empty_state(self):
        empty = ctk.CTkFrame(self.cards_container, corner_radius=14, fg_color=SOFT_CARD_BG)
        empty.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        empty.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(empty, text="No analysis yet", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, pady=(28, 6))

        text = ctk.CTkLabel(
            empty,
            text="Upload a PDF resume from Resume Scan to generate progress bars.",
            font=ctk.CTkFont(size=14),
            text_color=("#64748b", "#94a3b8"),
        )
        text.grid(row=1, column=0, pady=(0, 28))

    def create_result_card(self, index, result):
        score = result["score"]
        score_color = self.controller.get_score_color(score)

        card = ctk.CTkFrame(
            self.cards_container,
            corner_radius=14,
            fg_color=SOFT_CARD_BG,
            border_width=1,
            border_color=("#e2e8f0", "#334155"),
        )
        card.grid(row=index, column=0, sticky="ew", padx=12, pady=(12, 4))
        card.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        top_row.grid_columnconfigure(0, weight=1)

        role_label = ctk.CTkLabel(
            top_row,
            text=f"{ICON_RESUME} {result['role']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        role_label.grid(row=0, column=0, sticky="w")

        score_badge = ctk.CTkLabel(
            top_row,
            text=f"{score}% match",
            width=104,
            height=30,
            corner_radius=15,
            fg_color=score_color,
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        score_badge.grid(row=0, column=1, sticky="e")

        progress = ctk.CTkProgressBar(card, height=14, corner_radius=8, progress_color=score_color)
        progress.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))
        progress.set(score / 100)

        details = ctk.CTkFrame(card, fg_color="transparent")
        details.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))
        details.grid_columnconfigure(0, weight=1, uniform="skills")
        details.grid_columnconfigure(1, weight=1, uniform="skills")

        self.create_skill_section(details, 0, f"{ICON_CHECK} Found Skills", result["found"], "#16a34a")
        self.create_skill_section(details, 1, f"{ICON_CIRCLE} Missing Skills", result["missing"], "#dc2626")

    def create_skill_section(self, parent, column, title, skills, color):
        section = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
        section.grid(row=0, column=column, sticky="nsew", padx=(0, 8) if column == 0 else (8, 0))
        section.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=color,
            anchor="w",
        )
        label.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 8))

        skills_text = ", ".join(skills) if skills else "None"
        skills_label = ctk.CTkLabel(
            section,
            text=skills_text,
            font=ctk.CTkFont(size=13),
            text_color=("#475569", "#cbd5e1"),
            anchor="nw",
            justify="left",
            wraplength=330,
        )
        skills_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))
