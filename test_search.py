import urllib.request
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

query = "trinity"
results = []
try:
    # 1. Exact Match
    url = f"https://pypi.org/pypi/{urllib.parse.quote(query)}/json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=3) as resp:
        info = json.loads(resp.read())["info"]
        results.append({
            "name": info.get("name"),
            "desc": info.get("summary", ""),
            "category": "Exact Match"
        })
except Exception:
    pass

# 2. Top Packages Fuzzy Search
try:
    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    # To be fast, we just search in the raw string maybe? No, json.loads is super fast for 120kb
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())
        
    matches = [r["project"] for r in data["rows"] if query in r["project"].lower()]
    
    # Filter out exact match if it was already appended
    if results and results[0]["name"].lower() in [m.lower() for m in matches]:
        matches = [m for m in matches if m.lower() != results[0]["name"].lower()]
        
    matches = matches[:5]
    
    def fetch_desc(name):
        try:
            u = f"https://pypi.org/pypi/{urllib.parse.quote(name)}/json"
            q = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(q, timeout=2) as r:
                return {"name": name, "desc": json.loads(r.read())["info"].get("summary", ""), "category": "Related"}
        except:
            return {"name": name, "desc": "Top PyPI Package", "category": "Related"}

    if matches:
        with ThreadPoolExecutor(max_workers=5) as ex:
            for res in ex.map(fetch_desc, matches):
                results.append(res)
                
except Exception as e:
    print(f"Error fetching top list: {e}")

print(json.dumps(results, indent=2))
