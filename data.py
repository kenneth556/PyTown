import urllib.request
import urllib.parse
import re

local_packages = [
    {"name": "numpy", "desc": "Numerical computing", "category": "Data"},
    {"name": "pandas", "desc": "Data analysis", "category": "Data"},
    {"name": "requests", "desc": "HTTP requests", "category": "Web"},
    {"name": "selenium", "desc": "Web automation", "category": "Automation"},
    {"name": "pyautogui", "desc": "Automation", "category": "Automation"},
    {"name": "tkinter", "desc": "GUI toolkit", "category": "GUI"},
    {"name": "pyaudio", "desc": "Audio handling", "category": "Audio"},
]

PRESETS = {
    "Data Science Pack": [
        {"name": "numpy", "desc": "Numerical computing", "category": "Data Science"},
        {"name": "pandas", "desc": "Data analysis", "category": "Data Science"},
        {"name": "matplotlib", "desc": "Plotting library", "category": "Data Science"},
        {"name": "seaborn", "desc": "Statistical data visualization", "category": "Data Science"},
        {"name": "scikit-learn", "desc": "Machine learning", "category": "Data Science"},
    ],
    "Automation Pack": [
        {"name": "selenium", "desc": "Web automation", "category": "Automation"},
        {"name": "pyautogui", "desc": "GUI automation", "category": "Automation"},
        {"name": "keyboard", "desc": "Hook and simulate keyboard events", "category": "Automation"},
        {"name": "mouse", "desc": "Hook and simulate mouse events", "category": "Automation"},
        {"name": "schedule", "desc": "Job scheduling", "category": "Automation"},
    ],
    "Web Dev Pack": [
        {"name": "flask", "desc": "Lightweight web framework", "category": "Web Dev"},
        {"name": "django", "desc": "Full-stack web framework", "category": "Web Dev"},
        {"name": "requests", "desc": "HTTP library", "category": "Web Dev"},
        {"name": "fastapi", "desc": "Modern async web framework", "category": "Web Dev"},
        {"name": "uvicorn", "desc": "ASGI web server", "category": "Web Dev"},
    ],
    "Audio & Media Pack": [
        {"name": "pyaudio", "desc": "Audio processing", "category": "Audio & Media"},
        {"name": "sounddevice", "desc": "Play and record sound", "category": "Audio & Media"},
        {"name": "moviepy", "desc": "Video editing", "category": "Audio & Media"},
        {"name": "pydub", "desc": "Audio manipulation", "category": "Audio & Media"},
        {"name": "librosa", "desc": "Music and audio analysis", "category": "Audio & Media"},
    ],
    "GUI Dev Pack": [
        {"name": "tkinter", "desc": "Standard GUI toolkit", "category": "GUI Dev"},
        {"name": "customtkinter", "desc": "Modern UI for tkinter", "category": "GUI Dev"},
        {"name": "pyqt5", "desc": "Qt toolkit bindings", "category": "GUI Dev"},
        {"name": "kivy", "desc": "Multitouch UI framework", "category": "GUI Dev"},
    ],
    "AI Extended": [
        {"name": "torch", "desc": "PyTorch deep learning", "category": "AI Extended"},
        {"name": "torchvision", "desc": "Image datasets and models", "category": "AI Extended"},
        {"name": "torchaudio", "desc": "Audio datasets and models", "category": "AI Extended"},
        {"name": "tensorflow", "desc": "Google ML framework", "category": "AI Extended"},
        {"name": "keras", "desc": "Deep learning API", "category": "AI Extended"},
        {"name": "numpy", "desc": "Numerical computing", "category": "AI Extended"},
        {"name": "pandas", "desc": "Data analysis", "category": "AI Extended"},
        {"name": "matplotlib", "desc": "Plotting library", "category": "AI Extended"},
        {"name": "seaborn", "desc": "Statistical data visualization", "category": "AI Extended"},
        {"name": "transformers", "desc": "HuggingFace models", "category": "AI Extended"},
        {"name": "datasets", "desc": "HuggingFace datasets", "category": "AI Extended"},
        {"name": "tokenizers", "desc": "Fast text tokenization", "category": "AI Extended"},
        {"name": "scikit-learn", "desc": "Machine learning", "category": "AI Extended"},
        {"name": "tqdm", "desc": "Fast, extensible progress meter", "category": "AI Extended"},
        {"name": "jupyter", "desc": "Interactive computing suite", "category": "AI Extended"},
        {"name": "ipykernel", "desc": "IPython kernel for Jupyter", "category": "AI Extended"},
    ],
    "AI": [
        {"name": "torch", "desc": "PyTorch deep learning", "category": "AI"},
        {"name": "torchvision", "desc": "Image datasets and models", "category": "AI"},
        {"name": "torchaudio", "desc": "Audio datasets and models", "category": "AI"},
        {"name": "transformers", "desc": "HuggingFace models", "category": "AI"},
        {"name": "datasets", "desc": "HuggingFace datasets", "category": "AI"},
        {"name": "numpy", "desc": "Numerical computing", "category": "AI"},
        {"name": "pandas", "desc": "Data analysis", "category": "AI"},
        {"name": "matplotlib", "desc": "Plotting library", "category": "AI"},
        {"name": "scikit-learn", "desc": "Machine learning", "category": "AI"},
        {"name": "tqdm", "desc": "Fast, extensible progress meter", "category": "AI"},
        {"name": "jupyter", "desc": "Interactive computing suite", "category": "AI"},
        {"name": "ipykernel", "desc": "IPython kernel for Jupyter", "category": "AI"},
    ]
}

import json
import urllib.error
from concurrent.futures import ThreadPoolExecutor

def search_online(query):
    query = query.strip().lower()
    if not query:
        return []
        
    results = []
    has_network = False
    
    # 1. Exact Match via PyPI JSON API
    try:
        url = f"https://pypi.org/pypi/{urllib.parse.quote(query)}/json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 PyTown/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            info = json.loads(resp.read())["info"]
            results.append({
                "name": info.get("name", query),
                "desc": info.get("summary", "No description"),
                "category": "Exact Match"
            })
            has_network = True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            has_network = True
    except Exception:
        pass
        
    # 2. Fuzzy Search using Top Packages Index (Bypasses PyPI Cloudflare)
    try:
        url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 PyTown/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            has_network = True
            
        matches = [r["project"] for r in data.get("rows", []) if query in r["project"].lower()]
        
        exact_name = results[0]["name"].lower() if results else ""
        matches = [m for m in matches if m.lower() != exact_name]
        matches = matches[:8] # Max 8 related packages
        
        def fetch_desc(name):
            try:
                u = f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json"
                q = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 PyTown/1.0'})
                with urllib.request.urlopen(q, timeout=2) as r:
                    summary = json.loads(r.read())["info"].get("summary")
                    return {
                        "name": name, 
                        "desc": summary if summary else "Top PyPI Package", 
                        "category": "Related"
                    }
            except Exception:
                return {"name": name, "desc": "Top PyPI Package", "category": "Related"}
                
        if matches:
            with ThreadPoolExecutor(max_workers=8) as ex:
                for res in ex.map(fetch_desc, matches):
                    results.append(res)
                    
    except Exception:
        pass
        
    if not has_network and not results:
        return None  # Triggers the Offline warning in ui.py
        
    return results
