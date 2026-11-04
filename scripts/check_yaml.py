# -*- coding: utf-8 -*-
import re
from pathlib import Path

s = Path(__file__).parent.parent / "esp32-panel.yaml".read_text(encoding="utf-8")
pua = [hex(ord(c)) for c in s if "\uE000" <= c <= "\uF8FF" or 0xF0000 <= ord(c) <= 0xFFFFF]
tags = re.findall(r"<mdi:[^>]+>", s)
print("剩余私用区字符:", len(pua))
print("剩余 mdi 标记:", len(tags))
print("剩余无效 on_click:", s.count("return nullptr"))
print("lbl_signal_set 出现:", s.count("lbl_signal_set"))
print("icon text 样例:", re.findall(r'text: "([^"]{1,4})"', s)[:6])
