# -*- coding: utf-8 -*-
"""
从 Arduino_GFX 的 Arduino_ST7701_RGBPanel.h 提取 st7701_type1_init_operations
（ESP32-4848S040 面板实际使用的序列），转换为 ESPHome st7701s init_sequence YAML。

操作码枚举 (Arduino_DataBus.h)：
  BEGIN_WRITE=0, WRITE_COMMAND_8=1, WRITE_COMMAND_16=2, WRITE_DATA_8=3,
  WRITE_DATA_16=4, WRITE_BYTES=5, WRITE_C8_D8=6, WRITE_C8_D16=7,
  WRITE_C16_D16=8, END_WRITE=9, DELAY=10
"""
import re
from pathlib import Path

# 改成你本机厂商 Arduino_GFX 库里 Arduino_ST7701_RGBPanel.h 的实际路径
SRC = Path(r"此处改成厂商Arduino_GFX库中Arduino_ST7701_RGBPanel.h的完整路径")
OUT = Path(__file__).resolve().parent.parent / "st7701_full_init.yaml"

text = SRC.read_text(encoding="utf-8", errors="ignore")
start = text.index("st7701_type1_init_operations")
end = text.index("st7701_type2_init_operations")
body = text[start:end]

# 提取所有 token（宏名/数字），先剔除行注释
clean = re.sub(r"//[^\n]*", "", body)
tokens = []
for m in re.finditer(r"(WRITE_[A-Z_0-9]+|0x[0-9A-Fa-f]+|\d+)", clean):
    tokens.append(m.group(1))

OP = {
    "BEGIN_WRITE": 0, "WRITE_COMMAND_8": 1, "WRITE_COMMAND_16": 2,
    "WRITE_DATA_8": 3, "WRITE_DATA_16": 4, "WRITE_BYTES": 5,
    "WRITE_C8_D8": 6, "WRITE_C8_D16": 7, "WRITE_C16_D16": 8,
    "END_WRITE": 9, "DELAY": 10,
}

def num(tok):
    return int(tok, 16) if tok.lower().startswith("0x") else int(tok)

seq = []
i = 0
while i < len(tokens):
    t = tokens[i]
    if t.startswith("//"):
        i += 1
        continue
    if t not in OP:
        i += 1
        continue
    op = OP[t]
    if op == 1:  # WRITE_COMMAND_8 cmd
        cmd = num(tokens[i + 1])
        seq.append([cmd])
        i += 2
    elif op == 2:  # WRITE_COMMAND_16 cmd16
        seq.append([num(tokens[i + 1])])
        i += 2
    elif op == 5:  # WRITE_BYTES n d1..dn
        n = num(tokens[i + 1])
        data = [num(tokens[i + 2 + k]) for k in range(n)]
        if seq and seq[-1] and len(seq[-1]) == 1:
            seq[-1].extend(data)  # 合并到前一条命令
        else:
            seq.append(data)
        i += 2 + n
    elif op == 6:  # WRITE_C8_D8: cmd + 1 字节数据
        seq.append([num(tokens[i + 1]), num(tokens[i + 2])])
        i += 3
    elif op == 7:  # WRITE_C8_D16: cmd + 2 字节数据
        seq.append([num(tokens[i + 1]), num(tokens[i + 2]), num(tokens[i + 3])])
        i += 4
    elif op == 10:  # DELAY ms
        seq.append(num(tokens[i + 1]))
        i += 2
    else:
        i += 1

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("# ST7701 full init sequence extracted from vendor Arduino_GFX (type1)\n")
    f.write("# Usage: if the screen stays blank, replace the whole display.init_sequence\n")
    f.write("#        in esp32-panel.yaml with the content of this file.\n")
    f.write("init_sequence:\n")
    for item in seq:
        if isinstance(item, list):
            f.write("- [" + ", ".join(f"0x{x:02X}" for x in item) + "]\n")
        else:
            f.write(f"- {item}\n")

print(f"converted {len(seq)} entries -> {OUT}")
