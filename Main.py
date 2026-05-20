try:
    import customtkinter as ctk
except Exception:
    # Fallback to standard tkinter if customtkinter is not available
    import tkinter as _tk
    import tkinter.font as _tkfont

    class _CTkShim:
        Tk = _tk.Tk
        CTk = _tk.Tk
        CTkFrame = _tk.Frame
        CTkLabel = _tk.Label
        CTkButton = _tk.Button
        CTkSwitch = _tk.Checkbutton
        CTkFont = _tkfont.Font

        @staticmethod
        def set_appearance_mode(*args, **kwargs):
            return None

        @staticmethod
        def set_default_color_theme(*args, **kwargs):
            return None

    ctk = _CTkShim
from tkinter import messagebox

from frames.reports import ReportsFrame
from frames.resume_scan import ResumeScanFrame
from frames.skill_match import SkillMatchFrame
from ui_constants import (
    ACTIVE_NAV_COLOR,
    APP_BG,
    ICON_BRAND,
    ICON_CHECK,
    ICON_REPORT,
    ICON_RESUME,
    ICON_THEME,
    SIDEBAR_BG,
)
from utils.analyzer import analyze_text, get_score_color, load_roles
from utils.history import load_history, save_history_entry
from utils.pdf_parser import extract_text_from_pdf, get_file_info, is_pdf_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Help type-checkers and IDEs resolve names without requiring the package at runtime
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.job_roles = load_roles()
        self.current_file = "No resume selected"
        self.current_file_info = None
        self.extracted_text = ""
        self.analysis_results = []
        self.best_role = ""
        self.best_score = 0
        self.history = load_history()
        self.nav_buttons = {}
        self.drop_enabled = False

        self.title("AI Resume Analyzer")
        self.geometry("1180x760")
        self.minsize(1040, 680)
        self.configure(fg_color=APP_BG)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.enable_drag_and_drop()
        self.create_sidebar()
        self.create_main_shell()
        self.create_frames()
        self.show_frame("ResumeScanFrame")

    def enable_drag_and_drop(self):
        if TkinterDnD is None:
            return

        try:
            TkinterDnD._require(self)
            self.drop_enabled = True
        except Exception:
            self.drop_enabled = False

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=244, corner_radius=0, fg_color=SIDEBAR_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(5, weight=1)

        brand = ctk.CTkLabel(
            self.sidebar,
            text=f"{ICON_BRAND} ResumeAI",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1d4ed8", "#60a5fa"),
            anchor="w",
        )
        brand.grid(row=0, column=0, sticky="ew", padx=24, pady=(28, 8))

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="AI skill match dashboard",
            font=ctk.CTkFont(size=13),
            text_color=("#64748b", "#94a3b8"),
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 28))

        nav_items = [
            ("ResumeScanFrame", f"{ICON_RESUME}  Resume Scan"),
            ("SkillMatchFrame", f"{ICON_CHECK}  Skill Match"),
            ("ReportsFrame", f"{ICON_REPORT}  Reports"),
        ]

        for row, (frame_name, label) in enumerate(nav_items, start=2):
            button = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda name=frame_name: self.show_frame(name),
                height=44,
                corner_radius=10,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                hover_color=("#e8f0fe", "#1e293b"),
                text_color=("#334155", "#cbd5e1"),
            )
            button.grid(row=row, column=0, sticky="ew", padx=16, pady=4)
            self.nav_buttons[frame_name] = button

        theme_box = ctk.CTkFrame(self.sidebar, corner_radius=14, fg_color=("#f1f5f9", "#1f2937"))
        theme_box.grid(row=6, column=0, sticky="ew", padx=16, pady=(16, 24))
        theme_box.grid_columnconfigure(0, weight=1)

        theme_label = ctk.CTkLabel(
            theme_box,
            text=f"{ICON_THEME} Dark mode",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        theme_label.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        self.sidebar_theme_switch = ctk.CTkSwitch(
            theme_box,
            text="Enabled",
            command=lambda: self.toggle_theme(self.sidebar_theme_switch),
            progress_color="#2563eb",
        )
        self.sidebar_theme_switch.select()
        self.sidebar_theme_switch.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 16))

    def create_main_shell(self):
        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color=APP_BG)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(self.main, height=76, corner_radius=0, fg_color=APP_BG)
        self.header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 8))
        self.header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self.header,
            text="AI Resume Analyzer",
            font=ctk.CTkFont(size=30, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")

        user_section = ctk.CTkFrame(self.header, corner_radius=16, fg_color=("#ffffff", "#111827"))
        user_section.grid(row=0, column=1, sticky="e", padx=(16, 12))

        user_label = ctk.CTkLabel(
            user_section,
            text="BY  Analyst",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#334155", "#e2e8f0"),
        )
        user_label.grid(row=0, column=0, padx=16, pady=10)

        self.header_theme_switch = ctk.CTkSwitch(
            self.header,
            text="Dark",
            command=lambda: self.toggle_theme(self.header_theme_switch),
            progress_color="#2563eb",
        )
        self.header_theme_switch.select()
        self.header_theme_switch.grid(row=0, column=2, sticky="e")

        subtitle = ctk.CTkLabel(
            self.header,
            text="Upload, scan, compare, and track resume skill matches.",
            font=ctk.CTkFont(size=14),
            text_color=("#64748b", "#94a3b8"),
            anchor="w",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.container = ctk.CTkFrame(self.main, corner_radius=0, fg_color=APP_BG)
        self.container.grid(row=1, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

    def create_frames(self):
        self.frames = {
            "ResumeScanFrame": ResumeScanFrame(self.container, self),
            "SkillMatchFrame": SkillMatchFrame(self.container, self),
            "ReportsFrame": ReportsFrame(self.container, self),
        }

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.refresh()
        self.animate_frame_raise(frame)
        self.highlight_nav_button(frame_name)

    def animate_frame_raise(self, frame):
        frame.tkraise()
        frame.configure(fg_color=("#f8fafc", "#111827"))
        self.after(70, lambda: frame.configure(fg_color=APP_BG))

    def highlight_nav_button(self, active_frame):
        for frame_name, button in self.nav_buttons.items():
            is_active = frame_name == active_frame
            button.configure(
                state="disabled" if is_active else "normal",
                fg_color=ACTIVE_NAV_COLOR if is_active else "transparent",
                hover_color=ACTIVE_NAV_COLOR if is_active else ("#e8f0fe", "#1e293b"),
                text_color=("#1d4ed8", "#93c5fd") if is_active else ("#334155", "#cbd5e1"),
            )

    def toggle_theme(self, source_switch):
        is_dark = source_switch.get() == 1
        mode = "dark" if is_dark else "light"
        ctk.set_appearance_mode(mode)

        if is_dark:
            self.header_theme_switch.select()
            self.sidebar_theme_switch.select()
        else:
            self.header_theme_switch.deselect()
            self.sidebar_theme_switch.deselect()

    def choose_resume(self):
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.analyze_resume(file_path)

    def analyze_resume(self, file_path):
        if not is_pdf_file(file_path):
            messagebox.showerror("Invalid file", "Please upload a PDF resume file.")
            return

        file_info = get_file_info(file_path)
        text = extract_text_from_pdf(file_path)

        if not text.strip():
            messagebox.showwarning("Warning", "No readable text found in resume!")
            return

        analysis = analyze_text(text, self.job_roles)
        self.current_file = file_info["name"]
        self.current_file_info = file_info
        self.extracted_text = text
        self.analysis_results = analysis["results"]
        self.best_role = analysis["best_role"]
        self.best_score = analysis["best_score"]

        save_history_entry(
            {
                "filename": self.current_file,
                "date": file_info["date"],
                "best_role": self.best_role,
                "score": self.best_score,
                "found_skills": analysis["all_found_skills"],
            }
        )
        self.history = load_history()

        for frame in self.frames.values():
            frame.refresh()
        self.show_frame("SkillMatchFrame")

    def clear_results(self):
        self.current_file = "No resume selected"
        self.current_file_info = None
        self.extracted_text = ""
        self.analysis_results = []
        self.best_role = ""
        self.best_score = 0

        for frame in self.frames.values():
            frame.refresh()

    def get_score_color(self, score):
        return get_score_color(score)


if __name__ == "__main__":
    app = App()
    app.mainloop()
