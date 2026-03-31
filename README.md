<div align="center">
  <img src="icon.png" width="128" height="128" alt="PyTown Logo">
  
  # PyTown

  **The Ultimate Desktop Graphical Python Library Installer**
</div>

---

**PyTown** is a lightweight, zero-dependency, modern Windows desktop application that bridges the gap between running Python code and managing complex `pip` installations. Instead of wrestling with command-line terminals, PyTown lets you search, select, and install Python libraries with a single click.

## ✨ Features

- **🚀 Ultra-Fast Package Search:** Bypasses aggressive PyPI bot-blocks by employing a custom hybrid search engine. Instantly fuzzy-searches the top 15,000 Python packages in milliseconds.
- **📦 Curated Presets:** Install entire technology stacks (e.g., Data Science, Web Development, Automation) completely automatically with built-in presets.
- **🛡️ Real-Time Process Control:** PyTown intercepts `pip`'s output, rendering the installation logs natively. You can safely `Cancel` a jammed installation midway.
- **🐍 Automatic Python Detection:** Actively scans the local system's environment variables to verify the active Python version dynamically upon launch.
- **✅ Detailed Reporting:** Clearly separates successful installs from failures so you never assume a broken package is ready to be imported.

## 🛠️ Running Locally (Development)

PyTown is built entirely on Python's built-in standard libraries (Tkinter, urllib, subprocess, threading). **No virtual environments or external dependencies are required** to test or edit the code!

1. Clone or download this repository.
2. Run the application entry point:
```bash
python main.py
```

## 📜 License

MIT License. Do whatever you want with the code!
