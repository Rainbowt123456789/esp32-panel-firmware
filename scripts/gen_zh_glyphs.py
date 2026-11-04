# -*- coding: utf-8 -*-
"""
生成 ESPHome LVGL 中文字体所需的 glyphs 列表。
输出:
  fonts/zh_glyphs.yaml   : GB2312 一级常用汉字(3755) + ASCII + 常用全角符号
  fonts/mdi_glyphs.yaml  : 智能面板用 MDI 图标字符(从 css 解析准确码点)
"""
import re
import sys
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"


def gb2312_level1():
    """GB2312 一级字库: 区 16-55 (0xB0-0xD7), 位 1-94 (0xA1-0xFE)，共 3755 字。"""
    chars = []
    for area in range(0xB0, 0xD8):
        for pos in range(0xA1, 0xFF):
            try:
                ch = bytes([area, pos]).decode("gb2312")
            except UnicodeDecodeError:
                continue
            if ch and not ch.isspace():
                chars.append(ch)
    return chars


def build_zh_list():
    result = []
    # 1) ASCII 可见字符 (数字/字母/英文标点) —— 含空格 0x20 (LVGL 缺空格会显示方框)
    for cp in range(0x20, 0x7F):
        result.append(chr(cp))
    # 2) GB2312 符号区常用全角标点 (区 1-8, 0xA1A1-0xA8FE)
    for area in range(0xA1, 0xA9):
        for pos in range(0xA1, 0xFF):
            try:
                ch = bytes([area, pos]).decode("gb2312")
            except UnicodeDecodeError:
                continue
            if ch and not ch.isspace():
                result.append(ch)
    # 3) GB2312 一级常用汉字
    result.extend(gb2312_level1())
    # 4) 常用补充符号（GB2312 未覆盖但面板常用）—— 含全角空格 U+3000
    extra = "℃℉°·—…℃㎡³≤≥×÷±￥＄　"
    for ch in extra:
        if ch not in result:
            result.append(ch)
    # 去重保序
    seen = set()
    uniq = []
    for ch in result:
        if ch not in seen:
            seen.add(ch)
            uniq.append(ch)
    return uniq


def build_mdi_list(css_path):
    """从 css 解析码点。返回 {name: char}"""
    css = css_path.read_text(encoding="utf-8", errors="ignore")
    mapping = {}
    # css 使用标准伪元素双冒号 ::before，content 为 "\FXXXX"(4位) 或 "\FXXXXX"(5位)
    for m in re.finditer(r"\.mdi-([\w-]+)::before\s*\{\s*content:\s*\"\\F([0-9A-Fa-f]{4,5})\"", css):
        name, cp = m.group(1), m.group(2)
        code = int(cp, 16)
        if code < 0x10000:  # 4 位格式需并入私用区
            code |= 0xF0000
        mapping[name] = chr(code)
    wanted = [
        "home",          # 首页
        "lightbulb",     # 灯光
        "lightbulb-on",  # 灯光-开
        "toggle-switch", # 开关
        "toggle-switch-off",
        "palette",       # 场景
        "cog",           # 设置
        "wifi",          # WiFi
        "wifi-off",      # WiFi 断开
        "thermometer",   # 温度
        "water-percent", # 湿度
        "clock-outline", # 时钟
        "calendar",      # 日历
        "power",         # 电源/占位
        "power-cycle",   # 重启
        "brightness-4",  # 背光
        "information-outline", # 信息
        "cloud",         # 云/天气
        "weather-partly-cloudy",
        "weather-sunny",
        "weather-rainy",
        "weather-night", # 夜晚
        "fan",           # 风扇
        "air-conditioner",
        "blinds",        # 窗帘
        "door",          # 门锁
        "cctv",          # 监控
        "music-note",    # 音乐
        "lock",          # 锁屏
        "arrow-left",    # 返回
        "chevron-right", # 占位/更多
        "weather-windy", # 空气质量
        "water",         # 水质
        "flash",         # 电费
        "package",       # 包裹
        "bell",          # 通知
        "home-variant",  # 家庭名
    ]
    out = {}
    missing = []
    for name in wanted:
        if name in mapping:
            out[name] = mapping[name]
        else:
            missing.append(name)
    if missing:
        print("[warn] css 中未找到图标:", ", ".join(missing))
    return out


def yaml_esc(ch):
    """YAML 双引号字符串转义"""
    if ch == '"':
        return '\\"'
    if ch == "\\":
        return "\\\\"
    if ord(ch) < 0x20 or ord(ch) == 0x7F:
        return f"\\u{ord(ch):04X}"
    return ch


def write_yaml_list(path, chars):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for ch in chars:
            f.write(f'- "{yaml_esc(ch)}"\n')
    print(f"{path.name}: {len(chars)} glyphs -> {path}")


def main():
    zh = build_zh_list()
    write_yaml_list(FONTS_DIR / "zh_glyphs.yaml", zh)

    css_path = FONTS_DIR / "materialdesignicons.css"
    if css_path.exists():
        mdi = build_mdi_list(css_path)
        write_yaml_list(FONTS_DIR / "mdi_glyphs.yaml", list(mdi.values()))
    else:
        print("[error] materialdesignicons.css 不存在，跳过 MDI glyphs")
        sys.exit(1)


if __name__ == "__main__":
    main()
