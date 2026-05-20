import re
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from frames.base import PageFrame
from ui_constants import BORDER_COLOR, CARD_BG, ICON_UPLOAD, SOFT_CARD_BG
from utils.pdf_parser import preview_text


class ResumeScanFrame(PageFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.grid_rowconfigure(2, weight=1)

        self.create_upload_section()
        self.create_file_preview()
        self.create_text_preview()
        self.register_drop_target()

    def create_upload_section(self):
        self.upload_section = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.upload_section.grid(row=0, column=0, sticky="ew", padx=28, pady=(8, 18))
        self.upload_section.grid_columnconfigure(1, weight=1)

        upload_icon = ctk.CTkLabel(
            self.upload_section,
            text=ICON_UPLOAD,
            width=58,
            height=58,
            corner_radius=14,
            fg_color=("#dbeafe", "#1e3a8a"),
            text_color=("#1d4ed8", "#bfdbfe"),
            font=ctk.CTkFont(size=25, weight="bold"),
        )
        upload_icon.grid(row=0, column=0, padx=(22, 16), pady=22)

        title = ctk.CTkLabel(
            self.upload_section,
            text="Resume Scan",
            font=ctk.CTkFont(size=21, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=1, sticky="sw", pady=(20, 0))

        drop_text = "Drag and drop a PDF here, or choose a file."
        if not self.controller.drop_enabled:
            drop_text = "Choose a PDF file. Drag-and-drop is available when tkinterdnd2 is installed."

        self.drop_label = ctk.CTkLabel(
            self.upload_section,
            text=drop_text,
            font=ctk.CTkFont(size=14),
            text_color=("#64748b", "#94a3b8"),
            anchor="w",
        )
        self.drop_label.grid(row=1, column=1, sticky="nw", pady=(2, 20))

        upload_button = ctk.CTkButton(
            self.upload_section,
            text="Upload PDF",
            command=self.controller.choose_resume,
            width=142,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
        )
        upload_button.grid(row=0, column=2, rowspan=2, padx=(8, 10), pady=20)

        clear_button = ctk.CTkButton(
            self.upload_section,
            text="Clear",
            command=self.controller.clear_results,
            width=92,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#e2e8f0", "#334155"),
            hover_color=("#cbd5e1", "#475569"),
            text_color=("#0f172a", "#f8fafc"),
        )
        clear_button.grid(row=0, column=3, rowspan=2, padx=(0, 22), pady=20)

    def create_file_preview(self):
        self.preview_card = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.preview_card.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 18))
        self.preview_card.grid_columnconfigure(0, weight=1)
        self.preview_card.grid_columnconfigure(1, weight=1)
        self.preview_card.grid_columnconfigure(2, weight=1)

        self.file_name_value = self.create_metric(self.preview_card, 0, "Selected File", "No file selected")
        self.file_size_value = self.create_metric(self.preview_card, 1, "File Size", "-")
        self.best_match_value = self.create_metric(self.preview_card, 2, "Best Match", "Waiting")

    def create_metric(self, parent, column, label, value):
        card = ctk.CTkFrame(parent, corner_radius=14, fg_color=SOFT_CARD_BG)
        card.grid(row=0, column=column, sticky="nsew", padx=12, pady=12)
        card.grid_columnconfigure(0, weight=1)

        label_widget = ctk.CTkLabel(
            card,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#64748b", "#94a3b8"),
            anchor="w",
        )
        label_widget.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))

        value_widget = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
            wraplength=250,
        )
        value_widget.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))
        return value_widget

    def create_text_preview(self):
        preview_frame = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=CARD_BG,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        preview_frame.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 24))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        label = ctk.CTkLabel(
            preview_frame,
            text="Extracted Text Preview",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        label.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))

        self.text_preview = ctk.CTkTextbox(
            preview_frame,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=13),
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.text_preview.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.text_preview.tag_config("found_skill", foreground="#16a34a")
        self.text_preview.tag_config("missing_skill", foreground="#dc2626")
        self.text_preview.insert("end", "Upload a resume to preview extracted text here.")
        self.text_preview.configure(state="disabled")

    def register_drop_target(self):
        if not self.controller.drop_enabled:
            return

        try:
            from tkinterdnd2 import DND_FILES

            self.upload_section.drop_target_register(DND_FILES)
            self.upload_section.dnd_bind("<<Drop>>", self.handle_drop)
        except Exception:
            self.controller.drop_enabled = False

    def handle_drop(self, event):
        files = self.tk.splitlist(event.data)
        if not files:
            return

        file_path = files[0]
        if not file_path.lower().endswith(".pdf"):
            messagebox.showerror("Invalid file", "Please drop a PDF resume file.")
            return

        self.controller.analyze_resume(file_path)

    def refresh(self):
        info = self.controller.current_file_info
        self.file_name_value.configure(text=self.controller.current_file)
        self.file_size_value.configure(text=info["size"] if info else "-")
        self.best_match_value.configure(text=self.controller.best_role or "Waiting")
        self.render_text_preview()

    def render_text_preview(self):
        self.text_preview.configure(state="normal")
        self.text_preview.delete("1.0", "end")

        if not self.controller.extracted_text:
            self.text_preview.insert("end", "Upload a resume to preview extracted text here.")
            self.text_preview.configure(state="disabled")
            return

        found_skills = sorted({skill for item in self.controller.analysis_results for skill in item["found"]})
        missing_skills = sorted({skill for item in self.controller.analysis_results for skill in item["missing"]})
        preview = preview_text(self.controller.extracted_text, 300)

        if missing_skills:
            self.text_preview.insert("end", "Missing skills: ", "missing_skill")
            self.text_preview.insert("end", ", ".join(missing_skills) + "\n\n", "missing_skill")

        self.text_preview.insert("end", preview)
        self.highlight_found_skills(found_skills)
        self.text_preview.configure(state="disabled")

    def highlight_found_skills(self, skills):
        content = self.text_preview.get("1.0", "end-1c")
        for skill in skills:
            pattern = re.compile(re.escape(skill), re.IGNORECASE)
            for match in pattern.finditer(content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_preview.tag_add("found_skill", start, end)
