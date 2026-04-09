import os

replacements = {
    "#F97316": "#0F172A",
    "#EA580C": "#020617",
    "bg-orange-600": "bg-slate-900",
    "bg-orange-500": "bg-slate-800",
    "bg-orange-400": "bg-slate-700",
    "text-orange-600": "text-slate-900",
    "text-orange-500": "text-slate-800",
    "text-orange-400": "text-slate-700",
    "from-orange-500": "from-slate-700",
    "from-orange-400": "from-slate-700",
    "to-red-500": "to-slate-900",
    "to-orange-600": "to-slate-900",
    "border-orange-500": "border-slate-800",
    "ring-orange-500": "ring-slate-800",
    "styles.css?v=6": "styles.css?v=7"
}

target_dirs = ["templates", "static/css"]

for d in target_dirs:
    for root, _, files in os.walk(d):
        for file in files:
            if file.endswith(".html") or file.endswith(".css"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content
                for old, new in replacements.items():
                    new_content = new_content.replace(old, new)
                
                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Updated {path}")
