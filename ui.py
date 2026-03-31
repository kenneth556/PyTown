import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import data
import installer
import python_setup
import threading

class PyTownApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyTown - Python Library Installer")
        self.root.geometry("800x600")
        self.root.configure(bg="#F0F0F0")
        
        # Load custom app icon if present correctly with PyInstaller support
        import os
        import sys
        if hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(__file__)
            
        icon_path = os.path.join(base_dir, "icon.png")
        if os.path.exists(icon_path):
            try:
                self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
            except Exception:
                pass
                
        # Win 10 utility style
        try:
            self.style = ttk.Style()
            self.style.theme_use('vista')
        except tk.TclError:
            pass
            
        # Color hints
        self.python_yellow = "#FFD43B"
        self.python_blue = "#306998"
        self.accent_blue = "#3182CE"
        
        self.style.configure("TButton", padding=5)
        self.style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"))
        
        # State
        self.search_var = tk.StringVar()
        self.library_vars = {} # name -> BooleanVar
        self.current_installer_state = None
        
        self.build_ui()
        self.populate_list(data.local_packages)

    def build_ui(self):
        # 1. Top Frame (Search & Presets)
        top_frame = tk.Frame(self.root, bg="#F0F0F0", padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        
        lbl_search = tk.Label(top_frame, text="Search:", bg="#F0F0F0", font=("Segoe UI", 10))
        lbl_search.pack(side=tk.LEFT, padx=(0, 5))
        
        entry_search = ttk.Entry(top_frame, textvariable=self.search_var, width=30, font=("Segoe UI", 10))
        entry_search.pack(side=tk.LEFT)
        entry_search.bind("<Return>", self.handle_search)
        
        # NEW PYTHON VERSION STYLE (FROM POLISHED UI)
        version = python_setup.get_python_version()
        py_frame = tk.Frame(top_frame, bg="#EBF8FF", padx=10, pady=5)
        py_frame.pack(side=tk.RIGHT, padx=5)
        lbl_py_version = tk.Label(py_frame, text=f"Python: {version}", bg="#EBF8FF", font=("Segoe UI", 9, "bold"), fg=self.accent_blue)
        lbl_py_version.pack()
        
        # Presets Combobox
        preset_names = list(data.PRESETS.keys())
        self.preset_var = tk.StringVar(value="Select a Preset")
        preset_combo = ttk.Combobox(top_frame, textvariable=self.preset_var, values=preset_names, state="readonly", width=18, font=("Segoe UI", 9))
        preset_combo.pack(side=tk.RIGHT, padx=(5, 10))
        
        # When user selects a preset from combo:
        preset_combo.bind("<<ComboboxSelected>>", lambda e: self.select_preset(data.PRESETS[self.preset_var.get()]))
        
        lbl_presets = tk.Label(top_frame, text="Presets :", bg="#F0F0F0", font=("Segoe UI", 9, "italic"))
        lbl_presets.pack(side=tk.RIGHT, padx=2)

        # 2. Main Middle Frame (List of packages)
        mid_frame = tk.LabelFrame(self.root, text="Available Libraries", bg="#F0F0F0", padx=10, pady=10, font=("Segoe UI", 9, "bold"))
        mid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas + Scrollbar for the package list
        self.canvas = tk.Canvas(mid_frame, bg="#FFFFFF", highlightthickness=1, highlightbackground="#CCCCCC")
        self.scrollbar = ttk.Scrollbar(mid_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="#FFFFFF")
        
        # Configure canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_reqwidth())
        # We need to update canvas window width when canvas resizes
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mousewheel binding
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # 3. Actions Frame
        action_frame = tk.Frame(self.root, bg="#F0F0F0", padx=10, pady=5)
        action_frame.pack(fill=tk.X)
        
        self.btn_install = tk.Button(action_frame, text="Install Selected", bg=self.python_yellow, fg="#000000", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5, command=self.install_selected)
        self.btn_install.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.btn_cancel = tk.Button(action_frame, text="Cancel", bg="#FF5C5C", fg="#FFFFFF", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=5, command=self.cancel_installation, state=tk.DISABLED)
        self.btn_cancel.pack(side=tk.RIGHT, padx=(5, 5))
        
        btn_clear = ttk.Button(action_frame, text="Clear Selection", command=self.clear_selection)
        btn_clear.pack(side=tk.RIGHT, padx=5)
        
        btn_reqs = ttk.Button(action_frame, text="Install requirements.txt", command=self.install_requirements)
        btn_reqs.pack(side=tk.LEFT)

        # 4. Console Frame (Bottom)
        console_frame = tk.LabelFrame(self.root, text="Installation Console", bg="#F0F0F0", padx=10, pady=10, font=("Segoe UI", 9, "bold"))
        console_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=(5, 10))
        
        self.text_console = tk.Text(console_frame, height=8, bg="#1E1E1E", fg="#CCCCCC", font=("Consolas", 9), state=tk.DISABLED)
        console_scroll = ttk.Scrollbar(console_frame, command=self.text_console.yview)
        self.text_console.configure(yscrollcommand=console_scroll.set)
        
        self.text_console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def populate_list(self, libraries, message=None):
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        if message:
            lbl_msg = tk.Label(self.scrollable_frame, text=message, font=("Segoe UI", 10, "italic"), bg="#FFFFFF", fg="#666666", pady=20)
            lbl_msg.pack(fill=tk.X)
            return
            
        for lib in libraries:
            if lib["name"] not in self.library_vars:
                self.library_vars[lib["name"]] = tk.BooleanVar(value=False)
                
            var = self.library_vars[lib["name"]]
            
            # Row frame
            row = tk.Frame(self.scrollable_frame, bg="#FFFFFF", pady=5)
            row.pack(fill=tk.X, expand=True)
            
            # Change background on hover
            row.bind("<Enter>", lambda e, r=row: self.on_hover(r, True))
            row.bind("<Leave>", lambda e, r=row: self.on_hover(r, False))
            
            cb = tk.Checkbutton(row, variable=var, bg="#FFFFFF", activebackground="#F5F5F5", cursor="hand2")
            cb.pack(side=tk.LEFT, padx=(5, 10))
            
            # Bind checkbutton hover to the row too
            cb.bind("<Enter>", lambda e, r=row: self.on_hover(r, True))
            cb.bind("<Leave>", lambda e, r=row: self.on_hover(r, False))
            
            lbl_name = tk.Label(row, text=lib["name"], font=("Segoe UI", 10, "bold"), bg="#FFFFFF", width=20, anchor="w")
            lbl_name.pack(side=tk.LEFT)
            
            desc_text = f"({lib.get('desc', '')})" if lib.get('desc') else ""
            lbl_desc = tk.Label(row, text=desc_text, font=("Segoe UI", 9), bg="#FFFFFF", fg="#333333", anchor="w")
            lbl_desc.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Add subtle separator
            sep = ttk.Separator(self.scrollable_frame, orient="horizontal")
            sep.pack(fill=tk.X)

    def on_hover(self, row_frame, hovering):
        color = "#F5F8FA" if hovering else "#FFFFFF"
        row_frame.configure(bg=color)
        for child in row_frame.winfo_children():
            # Dont change the Checkbutton background since it renders weird
            if not isinstance(child, tk.Checkbutton):
                child.configure(bg=color)

    def handle_search(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            self.populate_list(data.local_packages)
            return
            
        # Searching state
        self.populate_list([], message="Searching online...")
        
        def bg_search():
            results = data.search_online(query)
            
            if results is None:
                self.root.after(0, lambda: self.populate_list(data.local_packages))
                self.root.after(0, lambda: messagebox.showwarning("Offline", "Could not connect to PyPI. Showing local packages only."))
            elif len(results) == 0:
                self.root.after(0, lambda: self.populate_list([], message="No packages found 😕"))
            else:
                self.root.after(0, lambda: self.populate_list(results))
                
        threading.Thread(target=bg_search, daemon=True).start()

    def select_preset(self, preset_libs):
        self.clear_selection()
        self.populate_list(preset_libs)
        for lib in preset_libs:
            if lib["name"] in self.library_vars:
                self.library_vars[lib["name"]].set(True)

    def clear_selection(self):
        for var in self.library_vars.values():
            var.set(False)

    def log_to_console(self, text):
        def _log():
            self.text_console.config(state=tk.NORMAL)
            self.text_console.insert(tk.END, text)
            self.text_console.see(tk.END)
            self.text_console.config(state=tk.DISABLED)
        # Schedule on main thread
        self.root.after(0, _log)

    def freeze_ui(self, frozen):
        install_state = tk.DISABLED if frozen else tk.NORMAL
        cancel_state = tk.NORMAL if frozen else tk.DISABLED
        
        self.btn_install.config(state=install_state)
        self.btn_cancel.config(state=cancel_state)

    def cancel_installation(self):
        if self.current_installer_state:
            self.current_installer_state.cancel()

    def install_selected(self):
        selected = [pkg for pkg, var in self.library_vars.items() if var.get()]
        if not selected:
            messagebox.showinfo("Info", "Please select at least one package to install.")
            return
            
        self.log_to_console("\n--- Starting Installation ---\n")
        self.freeze_ui(True)
        
        def on_complete(success_pkgs, failed_pkgs):
            self.current_installer_state = None
            self.root.after(0, lambda: self.freeze_ui(False))
            
            msg = []
            if success_pkgs:
                msg.append("✅ Successful:\n" + ", ".join(success_pkgs))
            if failed_pkgs:
                msg.append("❌ Failed:\n" + ", ".join(failed_pkgs))
                
            final_text = "\n\n".join(msg) if msg else "No packages were processed."
            
            if failed_pkgs:
                self.root.after(0, lambda: messagebox.showwarning("Installation Report", final_text))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Installation Report", final_text))
            
        self.current_installer_state = installer.install_packages(selected, self.log_to_console, on_complete)

    def install_requirements(self):
        path = filedialog.askopenfilename(
            title="Select requirements.txt",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if not path:
            return
            
        self.log_to_console(f"\n--- Installing requirements from {path} ---\n")
        self.freeze_ui(True)
        
        def on_complete(success):
            self.root.after(0, lambda: self.freeze_ui(False))
            if success:
                self.root.after(0, lambda: messagebox.showinfo("Done", "Requirements installed successfully!"))
            else:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "Requirements installation failed or was cancelled. Check console."))
            
        def req_runner():
            self.log_to_console(f"Running pip install -r {path}...\n")
            self.current_installer_state = installer.InstallerState()
            success = False
            try:
                import subprocess, os
                self.current_installer_state.process = subprocess.Popen(
                    ["python", "-m", "pip", "install", "-r", path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=installer.CREATE_NO_WINDOW
                )
                for line in iter(self.current_installer_state.process.stdout.readline, ''):
                    self.log_to_console(line)
                self.current_installer_state.process.stdout.close()
                self.current_installer_state.process.wait()
                
                if self.current_installer_state.cancel_requested:
                    self.log_to_console("\n⚠️ Requirements installation cancelled by user.\n\n")
                elif self.current_installer_state.process.returncode == 0:
                    self.log_to_console("✔ Installed requirements.txt successfully.\n\n")
                    success = True
                else:
                    self.log_to_console(f"❌ Failed to install (Return code: {self.current_installer_state.process.returncode})\n\n")
            except Exception as e:
                self.log_to_console(f"❌ Error: {str(e)}\n\n")
            finally:
                self.current_installer_state = None
                on_complete(success)
                
        threading.Thread(target=req_runner, daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PyTownApp()
    app.run()
