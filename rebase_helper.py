import sys
import os

if len(sys.argv) < 2:
    sys.exit(0)

file_path = sys.argv[1]

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# If it is the rebase todo list
if "git-rebase-todo" in file_path:
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("pick") and "Initial commit, prepared by" in line:
            lines[i] = line.replace("pick", "reword", 1)
        elif line.startswith("pick") and "intial commit, prepared by" in line.lower():
            lines[i] = line.replace("pick", "reword", 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

# If it is the commit message
elif "COMMIT_EDITMSG" in file_path:
    if "prepared by" in content.lower():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("initial commit\n")
