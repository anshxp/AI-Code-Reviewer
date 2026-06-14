"""Beautiful Tkinter UI for the Visual Beginner Code Reviewer with Gemini AI."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageDraw
import io
import threading
import os

from .analyzer import CodeAnalyzer, Issue
from .explanations import get_explanation
from .examples import BROKEN_EXAMPLE, DEFAULT_EXAMPLE
from .simulator import CodeSimulator
from .gemini_service import GeminiService
from .prompt_generator import generate_prompt_for_issue


class CodeMentorApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("✨ Visual Beginner Code Reviewer - Powered by Gemini AI")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 750)
        
        # Store references
        self.analyzer = CodeAnalyzer()
        self.simulator = CodeSimulator()
        self.gemini = GeminiService()
        self.issues: list[Issue] = []
        self.current_image_data: bytes | None = None
        self.current_photo_image: tk.PhotoImage | None = None
        
        # Configure style
        self._configure_style()
        self._build_layout()
        self.load_example(DEFAULT_EXAMPLE)

    def run(self) -> None:
        self.root.mainloop()

    def _configure_style(self) -> None:
        """Configure modern dark theme with gradients."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Color palette - Modern dark mode with vibrant accents
        bg_dark = "#0f1419"
        bg_card = "#1a1f2e"
        bg_input = "#0d1117"
        accent_blue = "#3b82f6"
        accent_purple = "#8b5cf6"
        accent_green = "#10b981"
        accent_red = "#ef4444"
        text_primary = "#f8fafc"
        text_secondary = "#cbd5e1"
        text_muted = "#94a3b8"
        
        # Frame styles
        style.configure("TFrame", background=bg_dark)
        style.configure("Card.TFrame", background=bg_card, relief="flat")
        style.configure("Dark.TFrame", background=bg_dark)
        
        # Label styles
        style.configure("TLabel", background=bg_dark, foreground=text_primary, font=("Segoe UI", 11))
        style.configure("Title.TLabel", font=("Segoe UI", 28, "bold"), foreground=text_primary, background=bg_dark)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12), foreground=text_secondary, background=bg_dark)
        style.configure("Muted.TLabel", font=("Segoe UI", 9), foreground=text_muted, background=bg_dark)
        style.configure("Card.TLabel", background=bg_card, foreground=text_primary, font=("Segoe UI", 10))
        
        # Button styles - More polished
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=12,
            relief="flat"
        )
        style.map(
            "Primary.TButton",
            background=[("active", accent_blue), ("pressed", accent_purple)],
        )
        
        style.configure(
            "Success.TButton",
            font=("Segoe UI", 10),
            padding=8,
            relief="flat"
        )
        style.map(
            "Success.TButton",
            background=[("active", accent_green)],
        )
        
        # Treeview
        style.configure(
            "Treeview",
            background=bg_input,
            foreground=text_primary,
            fieldbackground=bg_input,
            font=("Segoe UI", 10),
            rowheight=32,
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        """Build the main UI layout."""
        self.root.configure(bg="#0f1419")
        
        # ============ HEADER ============
        header = ttk.Frame(self.root, style="Dark.TFrame")
        header.pack(fill="x", padx=0, pady=0)
        
        header_inner = ttk.Frame(header, style="Dark.TFrame", padding=(24, 20, 24, 16))
        header_inner.pack(fill="x")
        
        # Title with emoji
        title = ttk.Label(
            header_inner,
            text="✨ Visual Code Reviewer",
            style="Title.TLabel"
        )
        title.pack(anchor="w")
        
        # Subtitle
        subtitle = ttk.Label(
            header_inner,
            text="Learn Python with AI-powered visual error explanations",
            style="Subtitle.TLabel"
        )
        subtitle.pack(anchor="w", pady=(4, 0))
        
        # ============ CONTROLS ============
        controls = ttk.Frame(self.root, style="Dark.TFrame", padding=(24, 12, 24, 12))
        controls.pack(fill="x")
        
        btn_frame = ttk.Frame(controls, style="Dark.TFrame")
        btn_frame.pack(fill="x")
        
        ttk.Button(
            btn_frame,
            text="🔍 Analyze Code",
            style="Primary.TButton",
            command=self.analyze_code
        ).pack(side="left", padx=(0, 8))
        
        ttk.Button(
            btn_frame,
            text="▶️ Run Code",
            style="Primary.TButton",
            command=self.run_code
        ).pack(side="left", padx=(0, 8))
        
        ttk.Button(
            btn_frame,
            text="📝 Default Example",
            style="Success.TButton",
            command=lambda: self.load_example(DEFAULT_EXAMPLE)
        ).pack(side="left", padx=(0, 8))
        
        ttk.Button(
            btn_frame,
            text="⚠️ Broken Example",
            style="Success.TButton",
            command=lambda: self.load_example(BROKEN_EXAMPLE)
        ).pack(side="left", padx=(0, 8))
        
        ttk.Button(
            btn_frame,
            text="🗑️ Clear All",
            style="Success.TButton",
            command=self.clear_editor
        ).pack(side="left")
        
        # API Key indicator
        api_status = "🔑 Gemini Ready" if self.gemini.api_key else "⚠️ No API Key"
        status_label = ttk.Label(
            controls,
            text=api_status,
            style="Muted.TLabel"
        )
        status_label.pack(anchor="e", pady=(8, 0))
        
        # ============ MAIN CONTENT ============
        main = ttk.Frame(self.root, style="Dark.TFrame", padding=(24, 12, 24, 20))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)
        
        # ---- LEFT SIDE: EDITOR ----
        editor_card = ttk.Frame(main, style="Card.TFrame", padding=16)
        editor_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        editor_card.columnconfigure(0, weight=1)
        editor_card.rowconfigure(1, weight=1)
        
        editor_label = ttk.Label(
            editor_card,
            text="💻 Code Editor",
            style="Subtitle.TLabel"
        )
        editor_label.grid(row=0, column=0, sticky="w", pady=(0, 12))
        
        self.code_text = tk.Text(
            editor_card,
            wrap="none",
            undo=True,
            bg="#0d1117",
            fg="#f8fafc",
            insertbackground="#3b82f6",
            selectbackground="#3b82f6",
            selectforeground="#f8fafc",
            relief="flat",
            font=("Fira Code", 12),
            padx=14,
            pady=12,
            height=28,
            bd=0,
            highlightthickness=0,
        )
        self.code_text.grid(row=1, column=0, sticky="nsew")
        
        code_scroll = ttk.Scrollbar(editor_card, orient="vertical", command=self.code_text.yview)
        code_scroll.grid(row=1, column=1, sticky="ns", padx=(8, 0))
        self.code_text.configure(yscrollcommand=code_scroll.set)
        
        # ---- RIGHT SIDE ----
        right = ttk.Frame(main, style="Dark.TFrame")
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=0)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        
        # Issues card
        issues_card = ttk.Frame(right, style="Card.TFrame", padding=12)
        issues_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        issues_card.columnconfigure(0, weight=1)
        
        issues_label = ttk.Label(
            issues_card,
            text="🐛 Detected Issues",
            style="Subtitle.TLabel"
        )
        issues_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        self.issue_list = tk.Listbox(
            issues_card,
            height=8,
            bg="#0d1117",
            fg="#f8fafc",
            selectbackground="#3b82f6",
            selectforeground="#f8fafc",
            relief="flat",
            activestyle="none",
            font=("Segoe UI", 10),
            bd=0,
            highlightthickness=0,
        )
        self.issue_list.grid(row=1, column=0, sticky="ew")
        self.issue_list.bind("<<ListboxSelect>>", self._show_issue_details)
        
        # Notebook (tabs)
        notebook = ttk.Notebook(right)
        notebook.grid(row=1, column=0, sticky="nsew")
        
        explanation_tab = ttk.Frame(notebook, padding=12)
        visualization_tab = ttk.Frame(notebook, padding=12)
        output_tab = ttk.Frame(notebook, padding=12)
        variables_tab = ttk.Frame(notebook, padding=12)
        
        notebook.add(explanation_tab, text="📖 Explanation")
        notebook.add(visualization_tab, text="🎨 Visualization")
        notebook.add(output_tab, text="📤 Output")
        notebook.add(variables_tab, text="📊 Variables")
        
        # Explanation tab
        self.explanation_text = tk.Text(
            explanation_tab,
            wrap="word",
            bg="#0d1117",
            fg="#f8fafc",
            relief="flat",
            font=("Segoe UI", 10),
            padx=12,
            pady=12,
            bd=0,
            highlightthickness=0,
        )
        self.explanation_text.pack(fill="both", expand=True)
        
        # Visualization tab
        viz_controls = ttk.Frame(visualization_tab, style="Card.TFrame", padding=8)
        viz_controls.pack(fill="x", pady=(0, 12))
        
        ttk.Button(
            viz_controls,
            text="✨ Generate with Gemini AI",
            style="Primary.TButton",
            command=self._generate_visualization
        ).pack(side="left", padx=(0, 8))
        
        ttk.Label(
            viz_controls,
            text="Creates AI-powered visualizations",
            style="Muted.TLabel"
        ).pack(side="left")
        
        self.visualization_text = tk.Text(
            visualization_tab,
            wrap="word",
            bg="#0d1117",
            fg="#10b981",
            relief="flat",
            font=("Courier New", 9),
            padx=12,
            pady=12,
            bd=0,
            highlightthickness=0,
        )
        self.visualization_text.pack(fill="both", expand=True)
        
        # Output tab
        self.output_text = tk.Text(
            output_tab,
            wrap="word",
            bg="#0d1117",
            fg="#f8fafc",
            relief="flat",
            font=("Courier New", 10),
            padx=12,
            pady=12,
            bd=0,
            highlightthickness=0,
        )
        self.output_text.pack(fill="both", expand=True)
        
        # Variables tab
        self.variables_tree = ttk.Treeview(
            variables_tab,
            columns=("name", "value"),
            show="headings",
            height=12
        )
        self.variables_tree.heading("name", text="Variable")
        self.variables_tree.heading("value", text="Value")
        self.variables_tree.column("name", width=120)
        self.variables_tree.column("value", width=200)
        self.variables_tree.pack(fill="both", expand=True)
        
        # ============ FOOTER ============
        footer = ttk.Frame(self.root, style="Dark.TFrame", padding=(24, 8, 24, 12))
        footer.pack(fill="x")
        
        self.status_var = tk.StringVar(value="Ready to analyze your code")
        status = ttk.Label(
            footer,
            textvariable=self.status_var,
            style="Muted.TLabel"
        )
        status.pack(anchor="w")

    def load_example(self, code: str) -> None:
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", code.strip() + "\n")
        self.status_var.set("Example loaded • Ready to analyze")

    def clear_editor(self) -> None:
        self.code_text.delete("1.0", tk.END)
        self.issue_list.delete(0, tk.END)
        self.explanation_text.delete("1.0", tk.END)
        self.visualization_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.variables_tree.delete(*self.variables_tree.get_children())
        self.status_var.set("Editor cleared")

    def analyze_code(self) -> None:
        source = self.code_text.get("1.0", tk.END)
        if not source.strip():
            self.status_var.set("Please write some code first")
            return
        
        self.issues = self.analyzer.analyze(source)
        self.issue_list.delete(0, tk.END)

        if not self.issues:
            self.issue_list.insert(tk.END, "✅ No issues found!")
            explanation = get_explanation("no_issues")
            self._render_explanation(
                "✨ " + explanation.title,
                explanation.description,
                explanation.fix
            )
            self.status_var.set("Analysis complete • Great code! No issues found")
            return

        for issue in self.issues:
            icon = "🔴" if issue.severity == "high" else "🟡"
            self.issue_list.insert(tk.END, f"{icon} Line {issue.line}: {issue.title}")

        self.issue_list.selection_set(0)
        self._show_issue_details()
        self.status_var.set(f"Analysis complete • {len(self.issues)} issue(s) found")

    def run_code(self) -> None:
        source = self.code_text.get("1.0", tk.END)
        if not source.strip():
            self.status_var.set("Please write some code first")
            return
        
        result = self.simulator.run(source)
        self.output_text.delete("1.0", tk.END)
        self.variables_tree.delete(*self.variables_tree.get_children())

        if result.output:
            self.output_text.insert(tk.END, result.output + "\n")
        if result.error:
            self.output_text.insert(tk.END, f"\n❌ Error: {result.error}\n")
            self.status_var.set(f"Execution failed • {result.error}")
        else:
            self.status_var.set("Execution successful ✅")

        for name, value in sorted(result.variables.items()):
            self.variables_tree.insert("", tk.END, values=(name, value))

        if result.steps and result.steps:
            self.output_text.insert(tk.END, "\n\n📊 Execution steps:\n")
            for step in result.steps[:20]:
                self.output_text.insert(tk.END, step + "\n")

    def _show_issue_details(self, event: object | None = None) -> None:
        selection = self.issue_list.curselection()
        if not selection or not self.issues:
            return

        index = selection[0]
        if index >= len(self.issues):
            return

        issue = self.issues[index]
        explanation = get_explanation(issue.kind)
        self._render_explanation(
            f"💡 {issue.title} (Line {issue.line})",
            f"{issue.message}\n\n{explanation.description}",
            f"{issue.fix}\n\n💡 Key concept: {explanation.fix}"
        )
        
        # Auto-generate visualization
        self._generate_visualization_thread(issue)

    def _render_explanation(self, title: str, body: str, fix: str) -> None:
        self.explanation_text.delete("1.0", tk.END)
        text = f"{title}\n\n{'─' * 50}\n\n{body}\n\n{'─' * 50}\n\nHow to fix:\n{fix}\n"
        self.explanation_text.insert(tk.END, text)

    def _generate_visualization(self) -> None:
        selection = self.issue_list.curselection()
        if not selection or not self.issues:
            self.status_var.set("Please select an issue first")
            return

        index = selection[0]
        if index >= len(self.issues):
            return

        issue = self.issues[index]
        self.status_var.set("🤖 Generating visualization with Gemini AI...")
        self.root.update()
        
        thread = threading.Thread(target=self._generate_visualization_thread, args=(issue,))
        thread.daemon = True
        thread.start()

    def _generate_visualization_thread(self, issue: Issue) -> None:
        try:
            # Get Gemini explanation
            explanation_result = self.gemini.generate_explanation(
                issue.title,
                issue.message,
                issue.fix
            )
            
            self.visualization_text.delete("1.0", tk.END)
            
            if explanation_result.success:
                self.visualization_text.insert(tk.END, explanation_result.text)
                self.status_var.set("✨ Visualization generated successfully!")
            else:
                error_msg = explanation_result.error or "Unknown error"
                self.visualization_text.insert(tk.END, f"❌ Error: {error_msg}\n\nMake sure to set GEMINI_API_KEY environment variable:\n\nexport GEMINI_API_KEY='your-key-here'")
                self.status_var.set(f"Visualization failed: {error_msg}")
        except Exception as e:
            self.visualization_text.delete("1.0", tk.END)
            self.visualization_text.insert(tk.END, f"❌ Error: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
