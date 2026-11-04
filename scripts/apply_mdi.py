# -*- coding: utf-8 -*-
"""把 esp32-panel.yaml 中的 <mdi:name> 标记替换为 MDI 真实字符(从 css 解析)"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YAML = ROOT / "esp32-panel.yaml"
CSS = ROOT / "fonts" / "materialdesignicons.css"

css = CSS.read_text(encoding="utf-8", errors="ignore")
mapping = {}
for m in re.finditer(r"\.mdi-([\w-]+)::before\s*\{\s*content:\s*\"\\F([0-9A-Fa-f]{4,5})\"", css):
    name, cp = m.group(1), m.group(2)
    code = int(cp, 16)
    if code < 0x10000:
        code |= 0xF0000
    mapping[name] = chr(code)

s = YAML.read_text(encoding="utf-8")
n = 0

def repl(m):
    global n
    name = m.group(1)
    if name not in mapping:
        raise SystemExit(f"[error] css 中未找到图标: {name}")
    n += 1
    return mapping[name]

s = re.sub(r"<mdi:([\w-]+)>", repl, s)
YAML.write_text(s, encoding="utf-8")
with open(ROOT / "scripts" / "mdi_result.txt", "w", encoding="utf-8") as f:
    f.write(f"resolved {n} mdi icons\n")
print(f"resolved {n} mdi icons")
