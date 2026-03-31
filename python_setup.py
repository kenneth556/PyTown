import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import tempfile
import threading
import os
import sys

# Windows constants for hidden consoles
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

PYTHON_VERSIONS = {
    "Python 3.12": "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe",
    "Python 3.11": "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe",
    "Python 3.10": "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
}

def is_python_installed():
    try:
        # Check system python (not the bundled one from pyinstaller)
        result = subprocess.run(["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_python_version():
    try:
        result = subprocess.run(["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "NIL"

class PythonInstallerApp:
    def __init__(self, root, on_complete):
        self.root = root
        self.on_complete = on_complete
        self.root.title("PyTown - System Check")
        self.root.geometry("450x260")
        self.root.resizable(False, False)
        
        # Basic Windows utility style
        self.root.configure(bg="#F0F0F0")
        
        # Load custom app icon if present correctly with PyInstaller support
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
        
        
        try:
            self.style = ttk.Style()
            self.style.theme_use('vista')
        except tk.TclError:
            pass # Fallback
            
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#F0F0F0", padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        lbl_title = tk.Label(main_frame, text="Python Environment Missing", font=("Segoe UI", 12, "bold"), fg="#D4B830", bg="#F0F0F0")
        lbl_title.pack(anchor="w", pady=(0, 5))

        lbl_desc = tk.Label(main_frame, text="PyTown requires Python installed on your system to function.\nPlease select a version to download and install.", font=("Segoe UI", 9), bg="#F0F0F0", justify="left")
        lbl_desc.pack(anchor="w", pady=(0, 15))

        self.version_var = tk.StringVar(value="Python 3.12")
        self.combo_versions = ttk.Combobox(main_frame, textvariable=self.version_var, values=list(PYTHON_VERSIONS.keys()), state="readonly", font=("Segoe UI", 9))
        self.combo_versions.pack(fill=tk.X, pady=(0, 15))

        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 5))

        self.lbl_status = tk.Label(main_frame, text="Ready", font=("Segoe UI", 8), bg="#F0F0F0", fg="#666666")
        self.lbl_status.pack(anchor="w")

        bottom_frame = tk.Frame(main_frame, bg="#F0F0F0")
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_install = ttk.Button(bottom_frame, text="Download & Install", command=self.start_installation)
        self.btn_install.pack(side=tk.RIGHT)

    def update_status(self, message, pct=None):
        self.lbl_status.config(text=message)
        if pct is not None:
            self.progress["value"] = pct
        self.root.update_idletasks()

    def start_installation(self):
        self.btn_install.config(state=tk.DISABLED)
        self.combo_versions.config(state=tk.DISABLED)
        version = self.version_var.get()
        url = PYTHON_VERSIONS[version]
        
        thread = threading.Thread(target=self.download_and_install, args=(url, version), daemon=True)
        thread.start()

    def download_and_install(self, url, version):
        try:
            self.update_status(f"Downloading {version}...", 0)
            
            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, "python_installer.exe")
            
            def report(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    pct = min(100, int(downloaded * 100 / total_size))
                    self.root.after(0, self.update_status, f"Downloading {version}... {pct}%", pct)
            
            urllib.request.urlretrieve(url, installer_path, reporthook=report)
            
            self.root.after(0, self.update_status, "Installing Python silently (this may take a minute)..", 100)
            self.root.after(0, lambda: self.progress.config(mode="indeterminate"))
            self.root.after(0, self.progress.start)
            
            # Run silent install
            try:
                subprocess.run(
                    [installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"],
                    check=True,
                    creationflags=CREATE_NO_WINDOW
                )
            except subprocess.CalledProcessError:
                self.root.after(0, lambda: messagebox.showerror("Error", "Python installation failed. It might require Administrator privileges. Try closing and running as Admin."))
                self.reset_ui()
                return
                
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.update_status, "Installation Complete", 100)
            
            # Validate installation
            if is_python_installed():
                self.root.after(0, lambda: messagebox.showinfo("Success", f"{version} was installed successfully!"))
                self.root.after(0, self.finish)
            else:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "Python was installed, but might not be in PATH yet. You may need to restart the application or computer."))
                self.root.after(0, self.finish)
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.reset_ui()

    def reset_ui(self):
        self.root.after(0, self.progress.stop)
        self.root.after(0, lambda: self.progress.config(mode="determinate", value=0))
        self.root.after(0, lambda: self.btn_install.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.combo_versions.config(state="readonly"))
        self.root.after(0, self.update_status, "Ready", 0)

    def finish(self):
        self.root.destroy()
        self.on_complete()

def check_and_install(on_complete):
    if is_python_installed():
        on_complete()
    else:
        root = tk.Tk()
        app = PythonInstallerApp(root, on_complete)
        root.mainloop()
