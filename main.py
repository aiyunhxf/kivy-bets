# ===================== 防盗激活模块（安卓全屏·机器码100%读取·终极修复版） =====================
import hashlib
import json
import os
import uuid
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock

# 字体注册（兼容Windows+安卓，解决中文乱码）
try:
    if platform == "win":
        LabelBase.register(name='SimHei', fn_regular=r'C:\Windows\Fonts\msyh.ttc')
    else:
        LabelBase.register(name='SimHei', fn_regular='DroidSansFallback')
except:
    pass

SECRET_KEY = "20260505_UNLOCK"
ACT_FILE = "act.json"

# ===================== 【核心修复】安卓10+ 机器码100%读取方案 =====================
def get_device_code():
    try:
        if platform == "android":
            # 方案1：读取安卓系统安全ID（唯一、不会被封禁）
            from android import android
            secure_id = android.provider.Settings.Secure.getString(
                android.content.Context().getContentResolver(),
                android.provider.Settings.Secure.ANDROID_ID
            )
            if secure_id and secure_id.strip():
                return hashlib.md5(secure_id.strip().encode()).hexdigest().upper()
            
            # 方案2：读取蓝牙MAC地址（备用兜底）
            bluetooth_mac = android.bluetooth.BluetoothAdapter.getDefaultAdapter().getAddress()
            if bluetooth_mac and bluetooth_mac.strip() and bluetooth_mac != "02:00:00:00:00:00":
                return hashlib.md5(bluetooth_mac.strip().encode()).hexdigest().upper()
            
            # 方案3：读取WIFI MAC地址（最终兜底）
            wifi_mac = android.net.wifi.WifiInfo.getMacAddress()
            return hashlib.md5(wifi_mac.strip().encode()).hexdigest().upper()
        else:
            # 电脑端不变
            return hashlib.md5(str(uuid.getnode()).encode()).hexdigest().upper()
    except Exception as e:
        print("读取机器码异常:", e)
        return "00000000000000000000000000000000"

def make_key(code):
    raw = code.strip() + SECRET_KEY
    return hashlib.md5(raw.encode()).hexdigest()[:16].upper()

def is_activated():
    if not os.path.exists(ACT_FILE):
        return False
    try:
        with open(ACT_FILE, encoding="utf-8") as f:
            dt = json.load(f)
        dc = get_device_code()
        return dt.get("device_code") == dc and dt.get("key") == make_key(dc)
    except:
        return False

def save_activation(key):
    dc = get_device_code()
    if key.strip().upper() == make_key(dc):
        with open(ACT_FILE, "w", encoding="utf-8") as f:
            json.dump({"device_code": dc, "key": key}, f)
        return True
    return False

# ===================== 【核心修复】安卓全屏激活界面（不再小窗口） =====================
class ActivateUI(BoxLayout):
    def __init__(self, main_app,** kwargs):
        super().__init__(**kwargs)
               
        # ========== 修复1：删除强制小窗口，安卓自动全屏 ==========
        if platform == "android":
            Window.fullscreen = True  # 安卓全屏
            Window.orientation = 'portrait'
        else:
            Window.size = (360, 640)  # 电脑端保留小窗口
        
        self.main = main_app
        self.dc = ""
        self.orientation = "vertical"
        self.padding = 60
        self.spacing = 30

        # 上下占位，内容垂直居中
        self.add_widget(Label(size_hint_y=1))

        # 机器码行
        line1 = BoxLayout(size_hint_y=None, height=60, spacing=15)
        line1.add_widget(Label(text="机器码：", font_size=22, font_name='SimHei', size_hint_x=None, width=80))
        self.code_input = TextInput(text="正在读取...", readonly=True, font_size=20, font_name='SimHei', halign="center")
        line1.add_widget(self.code_input)
        btn_copy = Button(text="复制", font_size=20, font_name='SimHei', size_hint_x=None, width=80, background_color=(0.2,0.7,0.3,1))
        btn_copy.bind(on_press=lambda x: Clipboard.copy(self.dc))
        line1.add_widget(btn_copy)
        self.add_widget(line1)

        # 激活码行
        line2 = BoxLayout(size_hint_y=None, height=60, spacing=15)
        line2.add_widget(Label(text="激活码：", font_size=22, font_name='SimHei', size_hint_x=None, width=80))
        self.key_input = TextInput(hint_text="请输入16位激活码", font_size=20, font_name='SimHei', halign="center")
        line2.add_widget(self.key_input)
        btn_act = Button(text="激活", font_size=20, font_name='SimHei', size_hint_x=None, width=80, background_color=(0.1,0.6,0.9,1))
        btn_act.bind(on_press=self.do_activate)
        line2.add_widget(btn_act)
        self.add_widget(line2)

        self.add_widget(Label(size_hint_y=1))

        # 自动读取机器码
        Clock.schedule_once(self.auto_load_device_code, 0.2)

    def auto_load_device_code(self, dt):
        self.dc = get_device_code()
        self.code_input.text = self.dc

    def do_activate(self, x):
        if save_activation(self.key_input.text.strip()):
            self.main.load_main_ui()
        else:
            self.key_input.text = ""
            self.key_input.hint_text = "激活码错误，请核对！"
# ===================== 防盗模块结束 =====================

# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.config import Config
from kivy.uix.popup import Popup
import re
import json
import os
import sys
from datetime import datetime
import uuid

# ==================== 字体资源路径处理 ====================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# ==================== 注册中文字体 ====================
try:
    font_path = resource_path("msyh.ttf")
    if os.path.exists(font_path):
        LabelBase.register(name='SimHei', fn_regular=font_path)
    else:
        import platform
        if platform.system() == 'Windows':
            LabelBase.register(name='SimHei', fn_regular=r'C:\Windows\Fonts\msyh.ttc')
        else:
            LabelBase.register(name='SimHei', fn_regular='DroidSansFallback')
except:
    LabelBase.register(name='SimHei', fn_regular='DroidSansFallback')

Config.set('graphics', 'multisamples', '0')
Config.set('kivy', 'text_backend', 'sdl2')

# ==================== 开奖号码配置 ====================
CURRENT_DRAW_NUMBERS = {
    "normal": [19, 24, 17, 34, 40, 39, 42],
    "special": 49
}

try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    print("警告：未安装 openpyxl，导出功能不可用。请运行 'pip install openpyxl' 安装。")

Config.set('graphics', 'width', 360)
Config.set('graphics', 'height', 640)
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'orientation', 'portrait')

COLOR_HEADER_BG = get_color_from_hex("#FFF9CC")
COLOR_NORMAL_BG = (1,1,1,1)
COLOR_NEGATIVE = get_color_from_hex("#FFE6F6")
COLOR_BTN_BG = get_color_from_hex("#cceeff")
COLOR_TEXT = (0,0,0,1)
COLOR_BORDER = (0.2,0.2,0.2,1)

BACKWATER_RATE = 0.04
ROW_H = dp(27)
DATA_FILE_XINAO = "bets_data_xinao.json"
DATA_FILE_LAOAO = "bets_data_laoao.json"
DATA_FILE_HK = "bets_data_hk.json"
ZODIAC_CONFIG_FILE = "zodiac_config.json"
AWARD_FILE_PREFIX = "award_numbers_"

ODDS = {
    "特码": 47,
    "特码大小": 1.9, "特码单双": 1.9,
    "特码合数大小": 1.9, "特码合数单双": 1.9,
    "特天肖": 1.9, "特地肖": 1.9,
    "特前肖": 1.9, "特后肖": 1.9,
    "特家肖": 1.9, "特野肖": 1.9,
    "特码尾数大小": 1.9,
    "总和单双": 1.9, "总和大小": 1.9,
    "红波": 2.7, "蓝波": 2.8, "绿波": 2.8,
    "六肖": 1.9, "六中": 1.9,
    "五不中": 2, "六不中": 2.5, "七不中": 3, "八不中": 3.5, "九不中": 4.2, "十不中": 5.2,
    "二连肖": 4, "二连肖马": 3.5,
    "三连肖": 10, "三连肖马": 8.5,
    "四连肖": 30, "四连肖马": 25,
    "五连肖": 100, "五连肖马": 85,
    "平特": 2, "平特马": 1.75,
    "平特0尾": 2, "平特1-9尾": 1.75,
    "二全中": 60, "三全中": 600,
}

# ==================== 用户指定对照表 ====================
ANIMALS = {
    "马": [1,13,25,37,49],
    "蛇": [2,14,26,38],
    "龙": [3,15,27,39],
    "兔": [4,16,28,40],
    "虎": [5,17,29,41],
    "牛": [6,18,30,42],
    "鼠": [7,19,31,43],
    "猪": [8,20,32,44],
    "狗": [9,21,33,45],
    "鸡": [10,22,34,46],
    "猴": [11,23,35,47],
    "羊": [12,24,36,48]
}

RED_BALL = [1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46]
BLUE_BALL = [3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48]
GREEN_BALL = [5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49]

TAIL_NUMBERS = {
    0: [10,20,30,40],
    1: [1,11,21,31,41],
    2: [2,12,22,32,42],
    3: [3,13,23,33,43],
    4: [4,14,24,34,44],
    5: [5,15,25,35,45],
    6: [6,16,26,36,46],
    7: [7,17,27,37,47],
    8: [8,18,28,38,48],
    9: [9,19,29,39,49]
}

TIAN_XIAO = ["牛","兔","龙","马","猴","猪"]
DI_XIAO   = ["鼠","虎","蛇","羊","鸡","狗"]
QIAN_XIAO = ["鼠","牛","虎","兔","龙","蛇"]
HOU_XIAO  = ["马","羊","猴","鸡","狗","猪"]
JIA_XIAO  = ["牛","马","羊","鸡","狗","猪"]
YE_XIAO   = ["鼠","虎","龙","蛇","兔","猴"]

sx = [(animal, len(nums)) for animal, nums in ANIMALS.items()]
bs = [("红波", len(RED_BALL)), ("蓝波", len(BLUE_BALL)), ("绿波", len(GREEN_BALL))]
wx = [("金",10),("木",16),("水",16),("火",9),("土",5)]
ANIMAL_NUM_COUNT = {name: cnt for name, cnt in sx}

# 内置生肖号码对照表
ANIMAL_NUM_MAP = {
    "马": ["01", "13", "25", "37", "49"],
    "蛇": ["02", "14", "26", "38"],
    "龙": ["03", "15", "27", "39"],
    "兔": ["04", "16", "28", "40"],
    "虎": ["05", "17", "29", "41"],
    "牛": ["06", "18", "30", "42"],
    "鼠": ["07", "19", "31", "43"],
    "猪": ["08", "20", "32", "44"],
    "狗": ["09", "21", "33", "45"],
    "鸡": ["10", "22", "34", "46"],
    "猴": ["11", "23", "35", "47"],
    "羊": ["12", "24", "36", "48"]
}

# ==================== 辅助函数 ====================
def extract_real_numbers(s):
    nums = re.findall(r'[0-9]+', s)
    res = []
    for n in nums:
        if len(n) == 1:
            if 1 <= int(n) <= 9:
                res.append(f"{int(n):02d}")
        elif len(n) == 2:
            if 1 <= int(n) <= 49:
                res.append(n)
        elif len(n) > 2:
            i = 0
            while i < len(n):
                if i+1 < len(n):
                    two = n[i:i+2]
                    if 1 <= int(two) <= 49:
                        res.append(two)
                        i += 2
                        continue
                one = n[i:i+1]
                if 1 <= int(one) <= 9:
                    res.append(f"{int(one):02d}")
                i += 1
    return res

def get_animal_by_number(num):
    if isinstance(num, str):
        num = int(num)
    for animal, numbers in ANIMALS.items():
        if num in numbers:
            return animal
    return None

def get_color_by_number(num):
    if isinstance(num, str):
        num = int(num)
    if num in RED_BALL:
        return "红波"
    elif num in BLUE_BALL:
        return "蓝波"
    elif num in GREEN_BALL:
        return "绿波"
    return None

def is_he_draw(play_type, special_num):
    he_plays = ["特码大小", "特码单双", "特码合数大小", "特码合数单双",
                "特天肖", "特地肖", "特前肖", "特后肖", "特家肖", "特野肖",
                "特码尾数大小", "六肖", "六中"]
    return special_num == 49 and play_type in he_plays

EXTENDED_KEYWORDS = {
    "特码": ["特码", "特马", "主码", "特别号", "特", "正码", "尾码", "特别"],
    "特码大小": ["特大", "特小", "大小", "大", "小", "特码大", "特码小", "大细", "大细码"],
    "特码单双": ["特单", "特双", "单双", "单", "双", "特码单", "特码双", "单数", "双数"],
    "特码合数大小": ["合大", "合小", "合数大", "合数小", "总和大", "总和小", "合大小"],
    "特码合数单双": ["合单", "合双", "合数单", "合数双", "总和单", "总和双"],
    "特天肖": ["天肖", "天", "特天", "天堂"],
    "特地肖": ["地肖", "地", "特地", "地府"],
    "特前肖": ["前肖", "前", "上半场"],
    "特后肖": ["后肖", "后", "下半场"],
    "特家肖": ["家肖", "家", "家禽", "家畜"],
    "特野肖": ["野肖", "野", "野兽"],
    "特码尾数大小": ["尾大", "尾小", "大尾", "小尾", "尾数大", "尾数小", "尾大小"],
    "总和单双": ["总单", "总双", "总分单", "总分双", "总和单", "总和双"],
    "总和大小": ["总大", "总小", "总分大", "总分小", "总和大", "总和小"],
    "红波": ["红波", "红", "波色", "颜色", "三色"],
    "蓝波": ["蓝波", "篮波", "蓝"],
    "绿波": ["绿波", "绿"],
    "六肖": ["六肖", "生肖", "肖", "选肖", "六个生肖", "六肖中"],
    "六中": ["六中"],
    "五不中": ["五不中", "五中", "不钟"],
    "六不中": ["六不中", "六中"],
    "七不中": ["七不中", "七中"],
    "八不中": ["八不中", "八中"],
    "九不中": ["九不中", "九中"],
    "十不中": ["十不中", "十中"],
    "二连肖": ["二连肖", "二连", "2连肖"],
    "三连肖": ["三连肖", "三连", "3连肖"],
    "四连肖": ["四连肖", "四连", "4连肖"],
    "五连肖": ["五连肖", "五连", "5连肖"],
    "平特": ["平特", "平特肖", "特肖", "平特鼠", "平特牛", "平特虎", "平特兔", "平特龙", "平特蛇", "平特马", "平特羊", "平特猴", "平特鸡", "平特狗", "平特猪"],
    "平特尾": ["尾", "0尾", "1尾", "2尾", "3尾", "4尾", "5尾", "6尾", "7尾", "8尾", "9尾", "平特尾", "尾数", "尾号", "尾码"],
    "二全中": ["二全中", "二全", "全中", "连码", "中两码"],
    "三全中": ["三全中", "三全", "中三码"],
}

def identify_play_type_extended(content):
    original_result = identify_play_type_original(content)
    if original_result[0] is not None:
        return original_result
    cleaned = re.sub(r'[\\/.,!$￥\s]', '', content)
    for play_type, keywords in EXTENDED_KEYWORDS.items():
        for kw in keywords:
            if kw in cleaned:
                if play_type in ["二连肖", "三连肖", "四连肖", "五连肖"]:
                    parts = re.split(r'[，,、\s]+', content)
                    all_combos = []
                    for part in parts:
                        animals_in_part = [a for a in ANIMALS.keys() if a in part]
                        if animals_in_part:
                            all_combos.append(animals_in_part)
                    if all_combos:
                        has_horse = any("马" in combo for combo in all_combos)
                        return play_type, {"combos": all_combos, "has_horse": has_horse}
                    else:
                        animals = [a for a in ANIMALS.keys() if a in cleaned]
                        if animals:
                            has_horse = "马" in animals
                            return play_type, {"animals": animals, "has_horse": has_horse}
                elif play_type == "平特":
                    parts = re.split(r'[，,、\s]+', content)
                    all_combos = []
                    for part in parts:
                        animals_in_part = [a for a in ANIMALS.keys() if a in part]
                        if animals_in_part:
                            all_combos.append(animals_in_part)
                    if all_combos:
                        return play_type, {"combos": all_combos, "is_horse": any("马" in combo for combo in all_combos)}
                    else:
                        for animal in ANIMALS.keys():
                            if animal in cleaned:
                                return play_type, {"animal": animal, "is_horse": (animal == "马")}
                        return play_type, None
                elif play_type == "平特尾":
                    match = re.search(r'(\d)尾', cleaned)
                    if match:
                        return play_type, {"tail": match.group(1)}
                    return play_type, None
                else:
                    return play_type, None
    return None, None

identify_play_type_original = None

def identify_play_type(content):
    global identify_play_type_original
    if identify_play_type_original is None:
        import sys
        identify_play_type_original = sys.modules[__name__].__dict__.get('_identify_play_type_orig')
        if identify_play_type_original is None:
            def orig(content):
                content_clean = content.replace(" ", "").replace("，", "").replace(",", "")
                if "特码" in content_clean and not any(x in content_clean for x in ["大小","单双","合数","尾数","天肖","地肖","前肖","后肖","家肖","野肖"]):
                    return "特码", None
                if "特码大小" in content_clean or (("特" in content_clean) and ("大小" in content_clean)):
                    return "特码大小", None
                if "特码单双" in content_clean or (("特" in content_clean) and ("单双" in content_clean)):
                    return "特码单双", None
                if "特码合数大小" in content_clean or "特合大" in content_clean or "特合小" in content_clean:
                    return "特码合数大小", None
                if "特码合数单双" in content_clean or "特合单" in content_clean or "特合双" in content_clean:
                    return "特码合数单双", None
                if "特天肖" in content_clean:
                    return "特天肖", None
                if "特地肖" in content_clean:
                    return "特地肖", None
                if "特前肖" in content_clean:
                    return "特前肖", None
                if "特后肖" in content_clean:
                    return "特后肖", None
                if "特家肖" in content_clean:
                    return "特家肖", None
                if "特野肖" in content_clean:
                    return "特野肖", None
                if "特码尾数大小" in content_clean or "特大尾" in content_clean or "特小尾" in content_clean:
                    return "特码尾数大小", None
                if "总和单双" in content_clean:
                    return "总和单双", None
                if "总和大小" in content_clean:
                    return "总和大小", None
                if "红波" in content_clean:
                    return "红波", None
                if "蓝波" in content_clean or "篮波" in content_clean:
                    return "蓝波", None
                if "绿波" in content_clean:
                    return "绿波", None
                if "六肖" in content_clean:
                    return "六肖", None
                if "六中" in content_clean:
                    return "六中", None
                for i in range(5,11):
                    if f"{i}不中" in content_clean:
                        return f"{i}不中", None
                if "二连肖" in content_clean:
                    animals = [a for a in ANIMALS.keys() if a in content_clean]
                    if "马" in animals:
                        return "二连肖", {"animals": animals, "has_horse": True}
                    else:
                        return "二连肖", {"animals": animals, "has_horse": False}
                if "三连肖" in content_clean:
                    animals = [a for a in ANIMALS.keys() if a in content_clean]
                    if "马" in animals:
                        return "三连肖", {"animals": animals, "has_horse": True}
                    else:
                        return "三连肖", {"animals": animals, "has_horse": False}
                if "四连肖" in content_clean:
                    animals = [a for a in ANIMALS.keys() if a in content_clean]
                    if "马" in animals:
                        return "四连肖", {"animals": animals, "has_horse": True}
                    else:
                        return "四连肖", {"animals": animals, "has_horse": False}
                if "五连肖" in content_clean:
                    animals = [a for a in ANIMALS.keys() if a in content_clean]
                    if "马" in animals:
                        return "五连肖", {"animals": animals, "has_horse": True}
                    else:
                        return "五连肖", {"animals": animals, "has_horse": False}
                if "平特" in content_clean:
                    for animal in ANIMALS.keys():
                        if animal in content_clean:
                            if animal == "马":
                                return "平特", {"animal": "马", "is_horse": True}
                            else:
                                return "平特", {"animal": animal, "is_horse": False}
                    return "平特", None
                if "平特尾" in content_clean:
                    match = re.search(r'(\d+)尾', content_clean)
                    if match:
                        tail = match.group(1)
                        return "平特尾", {"tail": tail}
                    return "平特尾", None
                if "二全中" in content_clean:
                    return "二全中", None
                if "三全中" in content_clean:
                    return "三全中", None
                return None, None
            identify_play_type_original = orig
    result = identify_play_type_original(content)
    if result[0] is not None:
        return result
    return identify_play_type_extended(content)

def calc_win_amount(play_type, bet_amount, extra, draw_numbers):
    special = draw_numbers["special"]
    normals = draw_numbers["normal"]
    special_str = f"{special:02d}"

    if is_he_draw(play_type, special):
        return 0.0

    bet_type = extra.get("bet_type", "")
    play_tag = ""

    if bet_type == "特码":
        play_tag = "number"
    elif bet_type == "各号":
        play_tag = "gehao"
    elif bet_type == "各肖":
        play_tag = "gexiao"
    elif bet_type == "平特":
        play_tag = "pingte"
    else:
        play_tag = extra.get("play_tag", "")

    numbers = extra.get("numbers", [])
    animals = extra.get("animals", [])
    draw_an = get_animal_by_number(special)

    total_win = 0.0

    if play_tag == "number":
        if numbers:
            total_count = len(numbers)
            per_unit = bet_amount / total_count
            hit_count = 1 if special_str in numbers else 0
            total_win += per_unit * hit_count * 47

    elif play_tag == "gehao":
        if animals:
            pack_nums = []
            for an in animals:
                pack_nums.extend(ANIMAL_NUM_MAP.get(an, []))
            if pack_nums:
                total_pack = len(pack_nums)
                per_pack = bet_amount / total_pack
                if special_str in pack_nums:
                    total_win += per_pack * 47

    elif play_tag == "gexiao":
        if animals:
            if draw_an in animals:
                per_ani = bet_amount / len(animals)
                if draw_an == "马":
                    total_win += per_ani * 9
                else:
                    total_win += per_ani * 11

    elif play_tag == "pingte":
        if animals:
            if draw_an in animals:
                per_ani = bet_amount / len(animals)
                if draw_an == "马":
                    total_win += per_ani * 1.75
                else:
                    total_win += per_ani * 2

    if play_type == "特码":
        total_win += bet_amount * 47

    if play_type == "特码大小":
        if 1 <= special <= 24 or 25 <= special <= 48:
            total_win += bet_amount * ODDS["特码大小"]

    if play_type == "特码单双":
        total_win += bet_amount * ODDS["特码单双"]

    if play_type == "特码合数大小":
        if special != 49:
            digit_sum = sum(int(d) for d in str(special))
            if 7 <= digit_sum <= 12 or 1 <= digit_sum <= 6:
                total_win += bet_amount * ODDS["特码合数大小"]

    if play_type == "特码合数单双":
        if special != 49:
            digit_sum = sum(int(d) for d in str(special))
            total_win += bet_amount * ODDS["特码合数单双"]

    if play_type == "特天肖":
        animal = get_animal_by_number(special)
        if animal in TIAN_XIAO:
            total_win += bet_amount * ODDS["特天肖"]

    if play_type == "特地肖":
        animal = get_animal_by_number(special)
        if animal in DI_XIAO:
            total_win += bet_amount * ODDS["特地肖"]

    if play_type == "特前肖":
        animal = get_animal_by_number(special)
        if animal in QIAN_XIAO:
            total_win += bet_amount * ODDS["特前肖"]

    if play_type == "特后肖":
        animal = get_animal_by_number(special)
        if animal in HOU_XIAO:
            total_win += bet_amount * ODDS["特后肖"]

    if play_type == "特家肖":
        animal = get_animal_by_number(special)
        if animal in JIA_XIAO:
            total_win += bet_amount * ODDS["特家肖"]

    if play_type == "特野肖":
        animal = get_animal_by_number(special)
        if animal in YE_XIAO:
            total_win += bet_amount * ODDS["特野肖"]

    if play_type == "特码尾数大小":
        tail = special % 10
        if 5 <= tail <= 9 or 0 <= tail <= 4:
            total_win += bet_amount * ODDS["特码尾数大小"]

    if play_type == "总和单双":
        total_sum = sum(normals) + special
        total_win += bet_amount * ODDS["总和单双"]

    if play_type == "总和大小":
        total_sum = sum(normals) + special
        total_win += bet_amount * ODDS["总和大小"]

    if play_type in ["红波", "蓝波", "绿波"]:
        color = get_color_by_number(special)
        if color == play_type:
            total_win += bet_amount * ODDS[play_type]

    if play_type in ["六肖", "六中"]:
        animals_in_text = extra.get("animals", [])
        if animals_in_text:
            animal = get_animal_by_number(special)
            if animal in animals_in_text:
                total_win += bet_amount * ODDS[play_type]

    if play_type in ["五不中", "六不中", "七不中", "八不中", "九不中", "十不中"]:
        chosen_numbers = extra.get("numbers", [])
        if chosen_numbers:
            chosen_int = [int(n) for n in chosen_numbers]
            hit = any(num in all_numbers for num in chosen_int)
            if not hit:
                total_win += bet_amount * ODDS["五不中"]

    if play_type in ["二连肖", "三连肖", "四连肖", "五连肖"]:
        combos = extra.get("combos", []) if extra else []
        if combos:
            total_combos = len(combos)
        else:
            animals = extra.get("animals", []) if extra else []
            total_combos = 1 if animals else 0
        if total_combos == 0:
            pass
        else:
            unit_amount = bet_amount / total_combos
            draw_animals = set()
            for num in all_numbers:
                a = get_animal_by_number(num)
                if a:
                    draw_animals.add(a)
            win_combos = 0
            if combos:
                for combo in combos:
                    if set(combo).issubset(draw_animals):
                        win_combos += 1
            else:
                animals = extra.get("animals", [])
                if animals and set(animals).issubset(draw_animals):
                    win_combos = 1
            if win_combos > 0:
                key = play_type
                if extra.get("has_horse", False):
                    key += "马"
                total_win += win_combos * unit_amount * ODDS[key]

    if play_type == "平特":
        combos = extra.get("combos", []) if extra else []
        total_combos = 0
        if combos:
            total_combos = len(combos)
        else:
            animal = extra.get("animal")
            if animal:
                total_combos = 1
        if total_combos == 0:
            pass
        else:
            unit_amount = bet_amount / total_combos
            draw_animals_set = set()
            for num in all_numbers:
                a = get_animal_by_number(num)
                if a:
                    draw_animals_set.add(a)
            win_count = 0
            if combos:
                for combo in combos:
                    for animal in combo:
                        if animal in draw_animals_set:
                            win_count += 1
                            break
            else:
                animal = extra.get("animal")
                if animal and animal in draw_animals_set:
                    win_count = 1
            if win_count > 0:
                if extra.get("is_horse", False):
                    odds = ODDS["平特马"]
                else:
                    odds = ODDS["平特"]
                total_win += win_count * unit_amount * odds

    if play_type == "平特尾":
        tails = extra.get("tails", []) if extra else []
        if not tails:
            tail_single = extra.get("tail")
            if tail_single is not None:
                tails = [tail_single]
        if tails:
            total_combos = len(tails)
            unit_amount = bet_amount / total_combos
            for tail in tails:
                tail_int = int(tail)
                if any(num % 10 == tail_int for num in all_numbers):
                    if tail_int == 0:
                        total_win += unit_amount * ODDS["平特0尾"]
                    else:
                        total_win += unit_amount * ODDS["平特1-9尾"]

    if play_type in ["二全中", "三全中"]:
        numbers_val = extra.get("numbers", [])
        if len(numbers_val) >= 2:
            nums = [int(n) for n in numbers_val]
            if play_type == "二全中":
                from math import comb
                total_combos = comb(len(nums), 2)
                if total_combos == 0:
                    pass
                else:
                    unit_amount = bet_amount / total_combos
                    win_combos = 0
                    for i in range(len(nums)):
                        for j in range(i+1, len(nums)):
                            if nums[i] in normals and nums[j] in normals:
                                win_combos += 1
                    total_win += win_combos * unit_amount * ODDS["二全中"]
            elif play_type == "三全中":
                if len(nums) >= 3:
                    from math import comb
                    total_combos = comb(len(nums), 3)
                    if total_combos == 0:
                        pass
                    else:
                        unit_amount = bet_amount / total_combos
                        win_combos = 0
                        for i in range(len(nums)):
                            for j in range(i+1, len(nums)):
                                for k in range(j+1, len(nums)):
                                    if nums[i] in normals and nums[j] in normals and nums[k] in normals:
                                        win_combos += 1
                        total_win += win_combos * unit_amount * ODDS["三全中"]

    return round(total_win, 2)

def convert_chinese_number(s):
    s = s.replace("一百","100").replace("两百","200").replace("三百","300")
    s = s.replace("四百","400").replace("五百","500").replace("六百","600")
    s = s.replace("七百","700").replace("八百","800").replace("九百","900")
    s = s.replace("二十","20").replace("三十","30").replace("四十","40")
    s = s.replace("五十","50").replace("六十","60").replace("七十","70")
    s = s.replace("八十","80").replace("九十","90").replace("十","10")
    s = s.replace("一","1").replace("二","2").replace("三","3")
    s = s.replace("四","4").replace("五","5").replace("六","6")
    s = s.replace("七","7").replace("八","8").replace("九","9")
    return s

def correct_typos(s):
    replacements = {"免":"兔","候":"猴","诸":"猪"}
    for wrong,right in replacements.items():
        s = s.replace(wrong,right)
    return s

def filter_region(text):
    region_keywords = ["新澳","老澳","香港","澳门","新门"]
    for kw in region_keywords:
        text = text.replace(kw, " ")
    return text

def detect_region(text):
    if re.search(r'(旧|老|老澳|老澳兑奖|老澳奖)', text):
        return "老澳"
    elif re.search(r'(香|港|香港|香港兑奖|香港奖|港奖)', text):
        return "香港"
    else:
        return "新澳"

def clean_text(text):
    text = filter_region(text)
    text = convert_chinese_number(text)
    text = correct_typos(text)
    text = re.sub(r'[（(]\s*共\s*[０-９\d]+\s*码\s*[）)]', '', text)
    text = re.sub(r'共\s*[０-９\d]+\s*码', '', text)
    text = re.sub(r'[\[〖［【].*?[\]〗］]', '', text)
    text = re.sub(r'[^\u4e00-\u9fa5\d\.\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_amount(seg):
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:米|元|块|斤|币|井|毛|两|#)\s*$', seg)
    if m:
        return float(m.group(1))
    m = re.search(r'(?<![0-9])(\d+(?:\.\d+)?)\s*$', seg)
    if m:
        return float(m.group(1))
    nums = re.findall(r'\d+(?:\.\d+)?', seg)
    if nums:
        return float(nums[-1])
    return 0.0

def identify_outer_play(seg):
    patterns = [
        ("特码大小", ["特码大小","特大","特小","特码大","特码小"]),
        ("特码单双", ["特码单双","特单","特双","特码单","特码双","包单","包双","包单双""平码单","平码双"]),
        ("特码合数大小", ["特码合数大小","合大","合小","合数大","合数小"]),
        ("特码合数单双", ["特码合数单双","合单","合双","合数单","合数双"]),
        ("特天肖", ["特天肖","天肖"]),
        ("特地肖", ["特地肖","地肖"]),
        ("特前肖", ["特前肖","前肖"]),
        ("特后肖", ["特后肖","后肖"]),
        ("特家肖", ["特家肖","家肖"]),
        ("特野肖", ["特野肖","野肖"]),
        ("特码尾数大小", ["特码尾数大小","尾大","尾小","大尾","小尾"]),
        ("总和单双", ["总和单双","总单","总双"]),
        ("总和大小", ["总和大小","总大","总小"]),
        ("红波", ["红波","红"]),
        ("蓝波", ["蓝波","篮波","蓝","篮"]),
        ("绿波", ["绿波","绿"]),
        ("六肖", ["六肖","六中","6中"]),
        ("六中", ["六中","6中"]),
        ("五不中", ["五不中"]),
        ("六不中", ["六不中"]),
        ("七不中", ["七不中"]),
        ("八不中", ["八不中"]),
        ("九不中", ["九不中"]),
        ("十不中", ["十不中"]),
        ("二连肖", ["二连肖","二连","2连肖","2连"]),
        ("三连肖", ["三连肖","三连","3连肖","3连"]),
        ("四连肖", ["四连肖","四连","4连肖","4连"]),
        ("五连肖", ["五连肖","五连","5连肖","5连","5友"]),
        ("平特", ["平特","平特肖"]),
        ("平特尾", ["平特尾","尾"]),
        ("二全中", ["二全中","二全"]),
        ("三全中", ["三全中","三全"]),
    ]
    for play_type, keywords in patterns:
        for kw in keywords:
            if kw in seg:
                info = {}
                if play_type in ["二连肖","三连肖","四连肖","五连肖","平特"]:
                    parts = re.split(r'[，,、\s]+', seg)
                    all_combos = []
                    for part in parts:
                        animals_in_part = [a for a in ANIMALS.keys() if a in part]
                        if animals_in_part:
                            all_combos.append(animals_in_part)
                    if all_combos:
                        if play_type == "平特" and len(all_combos) == 1 and len(all_combos[0]) > 1:
                            if not re.search(r'[，,、\s]', seg):
                                all_combos = [[a] for a in all_combos[0]]
                        info["combos"] = all_combos
                        info["has_horse"] = any("马" in combo for combo in all_combos)
                    else:
                        animals = [a for a in ANIMALS.keys() if a in seg]
                        if animals:
                            info["animals"] = list(set(animals))
                            info["has_horse"] = "马" in animals
                if play_type == "平特尾":
                    tails = re.findall(r'(?<![0-9])(\d)尾', seg)
                    if tails:
                        info["tails"] = list(set(tails))
                    else:
                        m = re.search(r'(?<![0-9])(\d)尾', seg)
                        if m:
                            info["tail"] = m.group(1)
                return play_type, info
    return None, None

def calc_outer_bet(play_type, info, base_amount, seg):
    single_plays = [
        "特码大小","特码单双","特码合数大小","特码合数单双",
        "特天肖","特地肖","特前肖","特后肖","特家肖","特野肖",
        "特码尾数大小","总和单双","总和大小",
        "五不中","六不中","七不中","八不中","九不中","十不中",
        "二全中","三全中",
        "六肖","六中"
    ]
    if play_type in single_plays:
        return base_amount

    if play_type in ["二连肖","三连肖","四连肖","五连肖"]:
        combos = info.get("combos", [])
        if combos:
            return len(combos) * base_amount
        else:
            animals = info.get("animals", [])
            return len(animals) * base_amount if animals else base_amount

    if play_type in ["红波","蓝波","绿波"]:
        if any(k in seg for k in ["各号","各码","各数","各"]):
            if "红" in seg and "蓝" in seg:
                return (len(RED_BALL) + len(BLUE_BALL)) * base_amount
            elif "红" in seg and "绿" in seg:
                return (len(RED_BALL) + len(GREEN_BALL)) * base_amount
            elif "蓝" in seg and "绿" in seg:
                return (len(BLUE_BALL) + len(GREEN_BALL)) * base_amount
            elif play_type == "红波":
                return len(RED_BALL) * base_amount
            elif play_type == "蓝波":
                return len(BLUE_BALL) * base_amount
            else:
                return len(GREEN_BALL) * base_amount
        else:
            return base_amount

    if play_type == "平特":
        if "各号" in seg or "各码" in seg or "各数" in seg:
            animals = info.get("animals", [])
            total_nums = sum(len(ANIMALS.get(a, [])) for a in animals)
            return total_nums * base_amount
        else:
            combos = info.get("combos", [])
            if combos:
                return len(combos) * base_amount
            else:
                animals = info.get("animals", [])
                return len(animals) * base_amount if animals else base_amount

    if play_type == "平特尾":
        if "各号" in seg or "各码" in seg or "各数" in seg:
            if "tails" in info:
                tails = info["tails"]
                total_nums = sum(len(TAIL_NUMBERS.get(int(t), [])) for t in tails)
                return total_nums * base_amount
            else:
                tail = info.get("tail")
                if tail is not None:
                    tail_int = int(tail)
                    return len(TAIL_NUMBERS.get(tail_int, [])) * base_amount
        else:
            return base_amount

    return base_amount

def calc_special_bet(seg, base_amount):
    has_animal = any(a in seg for a in ANIMALS.keys())
    temp_seg = seg
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:米|元|块|斤|币|井|毛|两|闷|#)?$', temp_seg)
    if match:
        temp_seg = temp_seg[:match.start()].strip()
    temp_seg = re.sub(r'\d+(?:米|元|块|斤|币|毛|两|#)', '', temp_seg)
    all_numbers = []
    for m in re.finditer(r'\d+', temp_seg):
        num_str = m.group()
        if len(num_str) > 2:
            continue
        try:
            n = int(num_str)
            if 1 <= n <= 49:
                all_numbers.append(f"{n:02d}")
        except:
            continue

    if not has_animal:
        keywords_a = ["各号","各码","各数","各","买","斤","米","#","元","块","个"]
        if any(kw in seg for kw in keywords_a):
            cnt = len(all_numbers)
            if cnt > 0:
                return cnt * base_amount, all_numbers
    if has_animal:
        keywords_b = ["各号","各码","号各","号码各","每个号","各数"]
        if any(kw in seg for kw in keywords_b):
            animals = []
            for one_sx in ANIMALS.keys():
                cnt = seg.count(one_sx)
                animals.extend([one_sx] * cnt)
            total_nums = sum(len(ANIMALS.get(a, [])) for a in animals)
            return total_nums * base_amount, None
        keywords_c = ["各肖","生肖","肖"]
        if any(kw in seg for kw in keywords_c):
            animals = []
            for one_sx in ANIMALS.keys():
                cnt = seg.count(one_sx)
                animals.extend([one_sx] * cnt)
            return len(animals) * base_amount, None
        else:
            animals = []
            for one_sx in ANIMALS.keys():
                cnt = seg.count(one_sx)
                animals.extend([one_sx] * cnt)
            if animals:
                return len(animals) * base_amount, None
    if all_numbers and base_amount > 0:
        return len(all_numbers) * base_amount, all_numbers
    return base_amount, None

def parse_segment(seg):
    
    seg = seg.strip()
    if not seg:
        return 0, 0, 0.0, None, None
    seg = clean_text(seg)

    if re.search(r'^(共|合计|总共|总计|总)\D*\d+', seg):
        return 0, 0, 0.0, None, None

    base_amount = extract_amount(seg)
    if base_amount <= 0:
        return 0, 0, 0.0, None, None
    play_type, info = identify_outer_play(seg)
    if play_type:
        bet = calc_outer_bet(play_type, info, base_amount, seg)
        count = int(bet / base_amount) if base_amount > 0 else 0
        if info is None:
            info = {}
        if 'numbers' not in info:
            numbers = []
            temp_seg = seg
            match = re.search(r'(\d+(?:\.\d+)?)\s*(?:米|元|块|斤|币|井|毛|两|#)?$', temp_seg)
            if match:
                temp_seg = temp_seg[:match.start()].strip()
            for m in re.finditer(r'\d+', temp_seg):
                num_str = m.group()
                if len(num_str) > 2:
                    continue
                try:
                    n = int(num_str)
                    if 1 <= n <= 49:
                        numbers.append(f"{n:02d}")
                except:
                    continue
            if numbers:
                info['numbers'] = numbers
        
        return count, base_amount, bet, play_type, info
    else:
        bet, numbers = calc_special_bet(seg, base_amount)
        bet = bet if bet > 0 else base_amount
        count = int(bet / base_amount) if base_amount > 0 else 0
        extra = {}
        if numbers:
            extra['numbers'] = numbers
        animals = [a for a in ANIMALS.keys() if a in seg]
        if animals:
            extra['animals'] = animals
        
        return count, base_amount, bet, None, extra

def extract_bet_units(text):
    text = convert_chinese_number(text)
    text = re.sub(r'[。，,、；！.]', ' ', text)
    text = text.replace('/', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    if re.search(r'\d', text):
        return [text]
    return []

def get_mode_number(play_type):
    if play_type is None:
        return "1"
    mode_map = {
        "特码": "1",
        "特码大小": "2",
        "特码单双": "3",
        "平码单双": "3",
        "特码合数大小": "4",
        "特码合数单双": "5",
        "特天肖": "6", "特地肖": "6",
        "特前肖": "7", "特后肖": "7",
        "特家肖": "8", "特野肖": "8",
        "特码尾数大小": "9",
        "总和单双": "10", "总和大小": "11",
        "红波": "12", "蓝波": "12", "绿波": "12",
        "六肖": "13", "六中": "13",
        "五不中": "14", "六不中": "14", "七不中": "14", "八不中": "14", "九不中": "14", "十不中": "14",
        "二连肖": "15", "三连肖": "15", "四连肖": "15", "五连肖": "15",
        "平特": "16",
        "平特尾": "17",
        "二全中": "18", "三全中": "18"
    }
    return mode_map.get(play_type, "1")

def parse_total_amount(text):
    if not text:
        return 0.0, []

    region_lvl = detect_region(text)

    def expand_tails(s):
        s = re.sub(r'(\d+(?:\.\d+)+)\.?尾', lambda m: ' '.join([f"{n}尾" for n in m.group(1).split('.')]), s)
        s = re.sub(r'(\d+(?:[,，、]\d+)+)尾', lambda m: ' '.join([f"{n}尾" for n in re.split(r'[,，、]', m.group(1))]), s)
        s = re.sub(r'(\d+(?:\s+\d+)+)\s*尾', lambda m: ' '.join([f"{n}尾" for n in m.group(1).split()]), s)
        return s

    text = expand_tails(text)
    text = text.replace('篮波', '蓝波')
    text = re.sub(r'[，,、]', ' ', text)
    text = re.sub(r'[/\\]+', ' ', text)
    text = re.sub(r'(\d)\.([斤米元块毛两])', r'\1\2', text)
    text = re.sub(r'(\d)\.(\d)', r'\1 \2', text)
    text = re.sub(r'([米元块斤])\s*(\d)', r'\1\n\2', text)

    def process_slash(match):
        left = match.group(1)
        right = match.group(2)
        if re.match(r'^\d+$', left) and re.match(r'^\d+$', right):
            return left + ' ' + right
        else:
            return left + '\n' + right
    text = re.sub(r'([^/\s]+)/([^/\s]+)', process_slash, text)
    raw_text = text.replace('/', '\n')

    raw_text = convert_chinese_number(raw_text)
    raw_text = re.sub(r'[。！]', ' ', raw_text)

    def is_valid_line(line):
        if not re.search(r'\d', line):
            return False
        if re.fullmatch(r'[\d\.\s]+', line):
            return True
        return True

    lines = [line.strip() for line in raw_text.splitlines() if line.strip() and is_valid_line(line.strip())]

    animal_names = '|'.join(ANIMALS.keys())
    play_words = [
        '平特', '二连肖', '二连', '三连肖', '三连', '四连肖', '四连', '五连肖', '五连', '五友',
        '六肖', '六中', '五不中', '六不中', '七不中', '八不中', '九不中', '十不中',
        '红波', '蓝波', '绿波', '平特尾', '特码'
    ]
    play_re = re.compile('|'.join(re.escape(w) for w in play_words))

    expanded_lines = []
    for line in lines:
        if play_re.search(line):
            expanded_lines.append(line)
            continue
        single_animal = re.fullmatch(rf'({animal_names})肖?\s*(\d+)', line)
        if single_animal:
            animal = single_animal.group(1)
            amt = single_animal.group(2)
            expanded_lines.append(f"{animal}肖{amt}")
        else:
            expanded_lines.append(line)
    lines = expanded_lines

    if not lines:
        units = [text] if re.search(r'\d', text) else []
    else:
        def has_amount_or_keyword(line):
            if re.search(r'(\d+)\s*(?:米|元|块|斤|币|井|毛|两|#)$', line):
                return True
            if re.search(r'(?:各号|各数|各码|各肖|每个\s*号|每个|各|个|买)', line):
                return True
            if re.search(r'(鼠|牛|虎|兔|龙|蛇|马|羊|猴|鸡|狗|猪)肖', line):
                return True
            keywords = '|'.join([
                '平特', '二连肖', '三连肖', '四连肖', '五连肖', '五友', '六肖', '六中',
                '五不中', '六不中', '七不中', '八不中', '九不中', '十不中',
                '特码大小', '特码单双', '特码合数大小', '特码合数单双',
                '特天肖', '特地肖', '特前肖', '特后肖', '特家肖', '特野肖',
                '特码尾数大小', '总和单双', '总和大小', '红波', '蓝波', '绿波',
                '平特尾', '二全中', '三全中', '特码'
            ])
            if re.search(keywords, line) and re.search(r'\d+\s*$', line):
                return True
            return False

        merged = []
        i = 0
        while i < len(lines):
            current = lines[i]
            if not has_amount_or_keyword(current) and i+1 < len(lines):
                lines[i+1] = current + ' ' + lines[i+1]
                i += 1
                continue
            merged.append(current)
            i += 1

        final_units = []
        keywords_pattern = r'(?:各号|各码|各数|各肖|每个\s*号|每个|各|个|买)'
        amount_unit = r'\s*(\d+)\s*(?:米|元|块|斤|币|井|毛|两|#|新澳)?'
        for line in merged:
            matches = list(re.finditer(keywords_pattern + amount_unit, line))
            if matches:
                prev = 0
                for m in matches:
                    unit = line[prev:m.end()].strip()
                    if unit:
                        unit = re.sub(r'^[，,、\s]+', '', unit)
                        final_units.append(unit)
                    prev = m.end()
                tail = line[prev:].strip()
                if tail:
                    final_units[-1] += ' ' + tail
            else:
                final_units.append(line)
        units = [u for u in final_units if u]

    split_keywords = [
        '平特', '二连肖', '三连肖', '四连肖', '五连肖', '五友', '六肖', '六中',
        '五不中', '六不中', '七不中', '八不中', '九不中', '十不中',
        '特码大小', '特码单双', '特码合数大小', '特码合数单双',
        '特天肖', '特地肖', '特前肖', '特后肖', '特家肖', '特野肖',
        '特码尾数大小', '总和单双', '总和大小', '红波', '蓝波', '绿波',
        '平特尾', '二全中', '三全中', '特码'
    ]
    new_units = []
    for unit in units:
        found = []
        for kw in split_keywords:
            for match in re.finditer(re.escape(kw), unit):
                found.append((match.start(), kw))
        if not found:
            new_units.append(unit)
            continue
        found.sort(key=lambda x: x[0])
        if len(found) == 1:
            new_units.append(unit)
            continue

        last_valid = -1
        for i, (pos, kw) in enumerate(found):
            if i == len(found) - 1:
                sub_unit = unit[pos:].strip()
            else:
                next_pos = found[i+1][0]
                sub_unit = unit[pos:next_pos].strip()
            if sub_unit and re.search(r'\d', sub_unit):
                if not re.search(r'(\d+)\s*(?:米|元|块|斤|币|井|毛|两|#)\s*$', sub_unit):
                    m = re.search(r'(\d+)\s*(?:米|元|块|斤|币|井|毛|两|#)?', unit[pos+len(kw):])
                    if m and m.group(1):
                        sub_unit += ' ' + m.group(1)
                new_units.append(sub_unit)
                last_valid = i
        if last_valid == -1:
            new_units.append(unit)
    units = new_units

    total_bet = 0.0
    details = []
    print("\n===== 粘贴的完整内容 =====")
    print(text)
    print("==================================================")
    print("\n===== 开始逐句解析 =====")
    for i, unit in enumerate(units, 1):
        count, price, bet, pt, info = parse_segment(unit)
        if bet == 0:
            print(f"【句{i}】：{unit}")
            print(f"  无法解析（金额为0）")
            continue
        mode_num = get_mode_number(pt)
        region = detect_region(unit)
        if pt:
            print(f"【句{i}】：{unit}")
            print(f"模式{mode_num}：{count} × {price} = {bet:.2f}  [区域:{region}]")
        else:
            print(f"【句{i}】：{unit}")
            print(f"模式1：{count} × {price} = {bet:.2f}  [区域:{region}]")
        total_bet += bet
        details.append((bet, pt, info, region))
    print("==================================================")
    print(f"合计：{int(total_bet)}")

    return total_bet, details

# ==================== GUI界面组件 ====================
class Cell(BoxLayout):
    def __init__(self, text='', bold=False, bg=COLOR_NORMAL_BG, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = ROW_H
        with self.canvas.before:
            Color(*bg)
            self.bg = Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BORDER)
            self.line = Line(width=1)
        self.lbl = Label(text=text, bold=bold, font_name='SimHei', font_size=28,
                        color=COLOR_TEXT, halign='center', valign='middle',
                        max_lines=2, text_size=(self.width, None))
        self.add_widget(self.lbl)
        self.bind(pos=self.update, size=self.update)
        self.bind(size=self._update_text_size)
    def _update_text_size(self,*args):
        self.lbl.text_size = (self.width, None)
    def update(self,*args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.line.rectangle = (self.x, self.y, self.width, self.height)
    def set_text(self,s):
        self.lbl.text = str(s)
    def set_bg(self,color):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*color)
            self.bg = Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BORDER)
            self.line = Line(width=1)

class EditCell(BoxLayout):
    def __init__(self, row, table, value=0.0, manual=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = ROW_H
        self.row = row
        self.table = table
        self.value = value
        self.manual_edited = manual
        with self.canvas.before:
            Color(*COLOR_NORMAL_BG)
            self.bg = Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BORDER)
            self.line = Line(width=1)

        self.ti = TextInput(
            text=f"{value:.2f}",
            halign='center',
            font_name='SimHei',
            font_size=28,
            foreground_color=COLOR_TEXT,
            background_color=COLOR_NORMAL_BG,
            padding=(dp(8), dp(4)),
            cursor_color=COLOR_TEXT
        )
        self.ti.bind(text=self.on_change)
        self.add_widget(self.ti)
        self.bind(pos=self.update, size=self.update)
        self.update_bg_by_value()

    def update(self,*args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.line.rectangle = (self.x, self.y, self.width, self.height)

    def set_bg(self,color):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*color)
            self.bg = Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BORDER)
            self.line = Line(width=1)

    def update_bg_by_value(self):
        if self.manual_edited:
            self.set_bg(COLOR_NEGATIVE)
        else:
            if self.value < 0:
                self.set_bg(COLOR_NEGATIVE)
            else:
                self.set_bg(COLOR_NORMAL_BG)

    def on_change(self, instance, value):
        try:
            new_val = float(value) if value.strip() else 0.0
        except:
            new_val = 0.0
        self.manual_edited = True
        self.value = new_val
        self.update_bg_by_value()
        if 0 <= self.row < len(self.table.row_list):
            if self is self.table.row_list[self.row][1]:
                self.table.row_data[self.row]['order_money'] = new_val
                self.table.calc_row(self.row)
                self.table.save_data()
            elif self is self.table.row_list[self.row][2]:
                self.table.row_data[self.row]['win_money'] = new_val
                self.table.calc_row(self.row)
                self.table.save_data()
            if self.table.on_data_changed:
                self.table.on_data_changed()

class BetTable(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 6
        self.spacing = 0
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.row_list = []
        self.row_data = []
        self.selected = None
        self.on_data_changed = None
        self.load_data()

    def select_row(self, index):
        if self.selected is not None:
            old_row = self.row_list[self.selected]
            for i,cell in enumerate(old_row):
                if i==0:
                    cell.set_bg(COLOR_HEADER_BG)
                else:
                    cell.set_bg(COLOR_NORMAL_BG)
        self.selected = index
        if self.selected is not None:
            new_row = self.row_list[self.selected]
            for cell in new_row:
                cell.set_bg((0.9,0.9,0.2,1))

    def add_row(self, order_money=0.0, win_money=0.0, xinao_list=None, laoao_list=None, hk_list=None):
        idx = len(self.row_list)
        row_id = str(uuid.uuid4())
        row = []
        sn_cell = Cell(text=str(idx+1), bg=COLOR_HEADER_BG)
        sn_cell.size_hint_x = None
        sn_cell.width = dp(40)
        sn_cell.index = idx
        sn_cell.bind(on_touch_up=lambda instance, touch: self.select_row(instance.index) if instance.collide_point(*touch.pos) else None)
        self.add_widget(sn_cell)
        row.append(sn_cell)
        bet_cell = EditCell(idx, self, order_money, manual=False)
        self.add_widget(bet_cell)
        row.append(bet_cell)
        win_cell = EditCell(idx, self, win_money, manual=False)
        self.add_widget(win_cell)
        row.append(win_cell)
        profit_cell = Cell(text="0.00", bg=COLOR_NORMAL_BG)
        self.add_widget(profit_cell)
        row.append(profit_cell)
        back_cell = Cell(text="0.00", bg=COLOR_NORMAL_BG)
        self.add_widget(back_cell)
        row.append(back_cell)
        total_cell = Cell(text="0.00", bg=COLOR_NORMAL_BG)
        self.add_widget(total_cell)
        row.append(total_cell)
        self.row_list.append(row)
        self.row_data.append({
            'row_id': row_id,
            'order_money': order_money,
            'win_money': win_money,
            'xinao': xinao_list if xinao_list is not None else [],
            'laoao': laoao_list if laoao_list is not None else [],
            'hk': hk_list if hk_list is not None else [],
            'xinao_key': '',
            'laoao_key': '',
            'hk_key': ''
        })
        self.calc_row(idx)
        self.save_data()
        if self.on_data_changed:
            self.on_data_changed()

    def insert_row_at(self, index, order_money=0.0, win_money=0.0, xinao_list=None, laoao_list=None, hk_list=None):
        row_id = str(uuid.uuid4())
        row = []
        sn_cell = Cell(text="?", bg=COLOR_HEADER_BG)
        sn_cell.size_hint_x = None
        sn_cell.width = dp(40)
        sn_cell.index = index
        sn_cell.bind(on_touch_up=lambda instance, touch: self.select_row(instance.index) if instance.collide_point(*touch.pos) else None)
        self.add_widget(sn_cell)
        row.append(sn_cell)
        bet_cell = EditCell(index, self, order_money, manual=False)
        self.add_widget(bet_cell)
        row.append(bet_cell)
        win_cell = EditCell(index, self, win_money, manual=False)
        self.add_widget(win_cell)
        row.append(win_cell)
        profit_cell = Cell(text="0.00", bg=COLOR_NORMAL_BG)
        self.add_widget(profit_cell)
        row.append(profit_cell)
        back_cell = Cell(text="0.00", bg=COLOR_NORMAL_BG)
        self.add_widget(back_cell)
        row.append(back_cell)
        total_cell = Cell(text="0.00", bg=COLOR_NORMAL_BG)
        self.add_widget(total_cell)
        row.append(total_cell)
        self.row_list.insert(index, row)
        self.row_data.insert(index, {
            'row_id': row_id,
            'order_money': order_money,
            'win_money': win_money,
            'xinao': xinao_list if xinao_list is not None else [],
            'laoao': laoao_list if laoao_list is not None else [],
            'hk': hk_list if hk_list is not None else [],
            'xinao_key': '',
            'laoao_key': '',
            'hk_key': ''
        })
        for i,r in enumerate(self.row_list):
            r[0].set_text(str(i+1))
            r[0].index = i
            r[1].row = i
            r[2].row = i
        for i in range(index, len(self.row_list)):
            self.calc_row(i)
        self.save_data()
        if self.on_data_changed:
            self.on_data_changed()

    def insert_empty_row(self):
        if self.selected is not None:
            pos = self.selected + 1
        else:
            pos = len(self.row_list)
        self.insert_row_at(pos, 0.0, 0.0, [], [], [])

    def clear_all(self):
        for row in self.row_list:
            for cell in row:
                self.remove_widget(cell)
        self.row_list.clear()
        self.row_data.clear()
        self.selected = None
        self.save_data()
        if self.on_data_changed:
            self.on_data_changed()

    def calc_row(self, idx):
        order = self.row_data[idx]['order_money']
        win = self.row_data[idx]['win_money']
        profit = win - order
        back = order * BACKWATER_RATE
        total = profit + back

        self.row_list[idx][1].value = order
        self.row_list[idx][1].update_bg_by_value()
        self.row_list[idx][2].value = win
        self.row_list[idx][2].ti.text = f"{win:.2f}"
        if win > 0:
            self.row_list[idx][2].set_bg(COLOR_NEGATIVE)
        else:
            self.row_list[idx][2].set_bg(COLOR_NORMAL_BG)

        self.row_list[idx][3].set_text(f"{profit:.2f}")
        self.row_list[idx][3].set_bg(COLOR_NEGATIVE if profit < 0 else COLOR_NORMAL_BG)
        self.row_list[idx][4].set_text(f"{back:.2f}")
        self.row_list[idx][4].set_bg(COLOR_NEGATIVE if back < 0 else COLOR_NORMAL_BG)
        self.row_list[idx][5].set_text(f"{total:.2f}")
        self.row_list[idx][5].set_bg(COLOR_NEGATIVE if total < 0 else COLOR_NORMAL_BG)

        if win > 0:
            for cell in self.row_list[idx][1:]:
                if isinstance(cell, Cell):
                    cell.set_bg(COLOR_NEGATIVE)
                elif isinstance(cell, EditCell):
                    cell.set_bg(COLOR_NEGATIVE)
        else:
            for cell in self.row_list[idx][1:]:
                if isinstance(cell, Cell):
                    cell.set_bg(COLOR_NORMAL_BG)
                elif isinstance(cell, EditCell):
                    cell.set_bg(COLOR_NORMAL_BG)

        if self.on_data_changed:
            self.on_data_changed()

    def paste_smart(self):
        txt = Clipboard.paste().strip()
        if not txt:
            self._show_popup("提示", "剪贴板为空")
            return

        def on_confirm(final_text):
            try:
                total_bet, details = parse_total_amount(final_text)
            except Exception as e:
                self._show_popup("解析错误", f"无法解析粘贴内容：{e}")
                return

            if total_bet > 0:
                xinao_list = []
                laoao_list = []
                hk_list = []
                gehao_keywords = ["各号", "个号", "个码", "各码", "各数", "每个号", "每个", "买"]
                has_gehao_in_text = any(kw in final_text for kw in gehao_keywords)

                for bet, pt, extra, region in details:
                    has_num = len(extra.get("numbers", [])) > 0
                    has_ani = len(extra.get("animals", [])) > 0
                    if has_num:
                        bet_type = "各数"
                        main_mode = "各数"
                    elif has_ani:
                        if has_gehao_in_text:
                            bet_type = "各号"
                            main_mode = "各号"
                        else:
                            bet_type = "各肖"
                            main_mode = "各肖"
                    else:
                        bet_type = "各号"
                        main_mode = "各号"
                    extra["bet_type"] = bet_type
                    extra["main_mode"] = main_mode
                    extra["sub_modes"] = [bet_type]
                    unit = {'amount': bet, 'play_type': pt, 'extra': extra}
                    if region == '新澳':
                        xinao_list.append(unit)
                    elif region == '老澳':
                        laoao_list.append(unit)
                    else:
                        hk_list.append(unit)

                if self.selected is not None:
                    self.insert_row_at(self.selected+1, total_bet, 0.0, xinao_list, laoao_list, hk_list)
                    self.selected = None
                else:
                    self.add_row(total_bet, 0.0, xinao_list, laoao_list, hk_list)
            else:
                self._show_popup("提示", "未识别到有效投注")

        popup = PastePreviewPopup(txt, on_confirm)
        popup.open()

    def delete_selected(self):
        if self.selected is not None and 0 <= self.selected < len(self.row_list):
            for cell in self.row_list[self.selected]:
                self.remove_widget(cell)
            del self.row_list[self.selected]
            del self.row_data[self.selected]
            for i,row in enumerate(self.row_list):
                row[0].set_text(str(i+1))
                row[0].index = i
                row[1].row = i
                row[2].row = i
            self.selected = None
            self.save_data()
            if self.on_data_changed:
                self.on_data_changed()

    def save_data(self):
        xinao_all = []
        laoao_all = []
        hk_all = []
        for rd in self.row_data:
            row_info = {
                'row_id': rd['row_id'],
                'order_money': rd['order_money'],
                'win_money': rd['win_money'],
                'xinao_key': rd.get('xinao_key', ''),
                'laoao_key': rd.get('laoao_key', ''),
                'hk_key': rd.get('hk_key', '')
            }
            for unit in rd['xinao']:
                xinao_all.append({**row_info, 'unit': unit})
            for unit in rd['laoao']:
                laoao_all.append({**row_info, 'unit': unit})
            for unit in rd['hk']:
                hk_all.append({**row_info, 'unit': unit})
        try:
            with open(DATA_FILE_XINAO, 'w', encoding='utf-8') as f:
                json.dump(xinao_all, f, ensure_ascii=False, indent=2)
            with open(DATA_FILE_LAOAO, 'w', encoding='utf-8') as f:
                json.dump(laoao_all, f, ensure_ascii=False, indent=2)
            with open(DATA_FILE_HK, 'w', encoding='utf-8') as f:
                json.dump(hk_all, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("保存失败:", e)

    def load_data(self):
        def load_file(filepath):
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    return []
            return []

        xinao_data = load_file(DATA_FILE_XINAO)
        laoao_data = load_file(DATA_FILE_LAOAO)
        hk_data = load_file(DATA_FILE_HK)
        if not (xinao_data or laoao_data or hk_data):
            return

        rows_dict = {}
        for item in xinao_data:
            rid = item['row_id']
            if rid not in rows_dict:
                rows_dict[rid] = {
                    'row_id': rid,
                    'order_money': item['order_money'],
                    'win_money': item['win_money'],
                    'xinao': [],
                    'laoao': [],
                    'hk': [],
                    'xinao_key': item.get('xinao_key', ''),
                    'laoao_key': item.get('laoao_key', ''),
                    'hk_key': item.get('hk_key', '')
                }
            rows_dict[rid]['xinao'].append(item['unit'])
        for item in laoao_data:
            rid = item['row_id']
            if rid not in rows_dict:
                rows_dict[rid] = {
                    'row_id': rid,
                    'order_money': item['order_money'],
                    'win_money': item['win_money'],
                    'xinao': [],
                    'laoao': [],
                    'hk': [],
                    'xinao_key': item.get('xinao_key', ''),
                    'laoao_key': item.get('laoao_key', ''),
                    'hk_key': item.get('hk_key', '')
                }
            rows_dict[rid]['laoao'].append(item['unit'])
        for item in hk_data:
            rid = item['row_id']
            if rid not in rows_dict:
                rows_dict[rid] = {
                    'row_id': rid,
                    'order_money': item['order_money'],
                    'win_money': item['win_money'],
                    'xinao': [],
                    'laoao': [],
                    'hk': [],
                    'xinao_key': item.get('xinao_key', ''),
                    'laoao_key': item.get('laoao_key', ''),
                    'hk_key': item.get('hk_key', '')
                }
            rows_dict[rid]['hk'].append(item['unit'])

        ordered_row_ids = []
        for item in xinao_data + laoao_data + hk_data:
            if item['row_id'] not in ordered_row_ids:
                ordered_row_ids.append(item['row_id'])
        for rid in ordered_row_ids:
            rd = rows_dict[rid]
            self.add_row(
                order_money=rd['order_money'],
                win_money=rd['win_money'],
                xinao_list=rd['xinao'],
                laoao_list=rd['laoao'],
                hk_list=rd['hk']
            )
            self.row_data[-1]['row_id'] = rid
            self.row_data[-1]['xinao_key'] = rd.get('xinao_key', '')
            self.row_data[-1]['laoao_key'] = rd.get('laoao_key', '')
            self.row_data[-1]['hk_key'] = rd.get('hk_key', '')
        if self.on_data_changed:
            self.on_data_changed()

    def export_to_excel(self):
        if not OPENPYXL_AVAILABLE:
            self._show_popup("错误", "请安装 openpyxl")
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "投注记录"
        headers = ["序号","下单金额","中码金额","盈亏(不含回水)","回水","总盈亏(含回水)"]
        ws.append(headers)
        for row in self.row_data:
            ws.append([self.row_list[self.row_data.index(row)][0].lbl.text,
                       row['order_money'], row['win_money'],
                       row['win_money'] - row['order_money'],
                       row['order_money'] * BACKWATER_RATE,
                       (row['win_money'] - row['order_money']) + row['order_money'] * BACKWATER_RATE])
        totals = ["总计",
                  sum(r['order_money'] for r in self.row_data),
                  sum(r['win_money'] for r in self.row_data),
                  sum(r['win_money'] - r['order_money'] for r in self.row_data),
                  sum(r['order_money'] * BACKWATER_RATE for r in self.row_data),
                  sum((r['win_money'] - r['order_money']) + r['order_money'] * BACKWATER_RATE for r in self.row_data)]
        ws.append(totals)
        fn = f"投注记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb.save(fn)
        self._show_popup("导出成功", f"已保存：{fn}")

    def _show_popup(self, title, msg):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        layout.add_widget(Label(text=title, font_name='SimHei', font_size=24, bold=True, size_hint_y=None, height=30))
        layout.add_widget(Label(text=msg, font_name='SimHei', font_size=20, size_hint_y=None, height=40))
        btn = Button(text='确定', font_name='SimHei', size_hint_y=None, height=40, background_color=COLOR_BTN_BG)
        layout.add_widget(btn)
        popup = Popup(title='', content=layout, size_hint=(0.7, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()

class FixedHeaderTable(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 0
        self.total_row = GridLayout(cols=6, spacing=0, size_hint_y=None, height=ROW_H)
        sn_cell = Cell(text="总计", bold=True, bg=COLOR_HEADER_BG)
        sn_cell.size_hint_x = None
        sn_cell.width = dp(40)
        self.total_row.add_widget(sn_cell)
        self.total_cells = []
        for _ in range(5):
            c = Cell(text="0.00", bold=True, bg=COLOR_HEADER_BG)
            self.total_cells.append(c)
            self.total_row.add_widget(c)
        self.add_widget(self.total_row)
        self.header = GridLayout(cols=6, spacing=0, size_hint_y=None, height=ROW_H)
        headers = ["序号","下单金额","中码金额","盈亏(不含回水)","回水","总盈亏(含回水)"]
        h0 = Cell(text=headers[0], bold=True, bg=COLOR_HEADER_BG)
        h0.size_hint_x = None
        h0.width = dp(40)
        self.header.add_widget(h0)
        for h in headers[1:]:
            self.header.add_widget(Cell(text=h, bold=True, bg=COLOR_HEADER_BG))
        self.add_widget(self.header)
        self.scroll = ScrollView()
        self.table = BetTable()
        self.table.on_data_changed = self.update_total_display
        self.scroll.add_widget(self.table)
        self.add_widget(self.scroll)
        self.update_total_display()

    def update_total_display(self):
        if not self.table.row_data:
            t = [0.0]*5
        else:
            t = [
                sum(r['order_money'] for r in self.table.row_data),
                sum(r['win_money'] for r in self.table.row_data),
                sum(r['win_money'] - r['order_money'] for r in self.table.row_data),
                sum(r['order_money'] * BACKWATER_RATE for r in self.table.row_data),
                sum((r['win_money'] - r['order_money']) + r['order_money'] * BACKWATER_RATE for r in self.table.row_data)
            ]
        for i in range(5):
            self.total_cells[i].set_text(f"{t[i]:.2f}")
            self.total_cells[i].set_bg(COLOR_NEGATIVE if t[i]<0 else COLOR_HEADER_BG)

    def paste_smart(self):
        self.table.paste_smart()

    def delete_selected(self):
        self.table.delete_selected()

    def insert_empty_row(self):
        self.table.insert_empty_row()

    def clear_all(self):
        self.table.clear_all()

    def export_to_excel(self):
        self.table.export_to_excel()

class ZodiacConfigWindow(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.95, 0.9)
        self.auto_dismiss = False

        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        with main_layout.canvas.before:
            Color(1,1,1,1)
            self.rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        title_label = Label(text='生肖号码设置', font_name='SimHei', font_size=36,
                            color=(0,0,0,1), bold=True, size_hint_y=None, height=40)
        main_layout.add_widget(title_label)
        main_layout.add_widget(Label(text='生肖对应号码 (01-49)', size_hint_y=None, height=30,
                                     font_name='SimHei', color=(0,0,0,1)))

        scroll = ScrollView()
        self.content_grid = GridLayout(cols=2, spacing=5, size_hint_y=None)
        self.content_grid.bind(minimum_height=self.content_grid.setter('height'))

        self.zodiacs = list(ANIMALS.keys())
        self.spinner_dict = {}
        self.num_options = [f"{i:02d}" for i in range(1,50)]

        try:
            with open(ZODIAC_CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
        except:
            self.config_data = {animal: [f"{n:02d}" for n in numbers] for animal, numbers in ANIMALS.items()}

        for zodiac in self.zodiacs:
            lbl = Label(text=zodiac, size_hint_y=None, height=40,
                        font_name='SimHei', bold=True, color=(0,0,0,1))
            self.content_grid.add_widget(lbl)

            spinner_box = BoxLayout(orientation='horizontal', spacing=1, size_hint_x=0.9,
                                    size_hint_y=None, height=40, padding=(-160,0))
            spinners = []
            for i in range(5):
                sp = Spinner(
                    text='--',
                    values=self.num_options,
                    size_hint=(None,1),
                    width=80,
                    font_name='SimHei',
                    font_size=32,
                    halign='center',
                    background_normal='',
                    background_color=(1,1,1,1),
                    color=(0,0,0,1),
                    sync_height=True
                )
                if zodiac in self.config_data and i < len(self.config_data[zodiac]):
                    val = self.config_data[zodiac][i]
                    if val in self.num_options:
                        sp.text = val
                spinners.append(sp)
                spinner_box.add_widget(sp)
            self.spinner_dict[zodiac] = spinners
            self.content_grid.add_widget(spinner_box)

        scroll.add_widget(self.content_grid)
        main_layout.add_widget(scroll)

        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        btn_save = Button(text='保存设置', font_name='SimHei', background_color=COLOR_BTN_BG)
        btn_save.bind(on_press=self.save_config)
        btn_close = Button(text='关闭', font_name='SimHei', background_color=(0.9,0.9,0.9,1))
        btn_close.bind(on_press=self.dismiss)
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_close)
        main_layout.add_widget(btn_layout)

        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def save_config(self, *args):
        new_config = {}
        for zodiac, spinners in self.spinner_dict.items():
            nums = [sp.text for sp in spinners if sp.text != '--']
            if nums:
                new_config[zodiac] = nums
        try:
            with open(ZODIAC_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=2)
            global ANIMALS, sx, ANIMAL_NUM_COUNT
            ANIMALS = {k: [int(n) for n in v] for k, v in new_config.items()}
            sx = [(animal, len(nums)) for animal, nums in ANIMALS.items()]
            ANIMAL_NUM_COUNT = {name: cnt for name, cnt in sx}
            self.show_popup('成功', '生肖号码配置已保存')
        except Exception as e:
            self.show_popup('错误', f'保存失败：{str(e)}')

    def show_popup(self, title, msg):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        layout.add_widget(Label(text=title, font_name='SimHei', font_size=24,
                                color=(0,0,0,1), bold=True, size_hint_y=None, height=30))
        layout.add_widget(Label(text=msg, font_name='SimHei', font_size=20,
                                color=(0,0,0,1), size_hint_y=None, height=40))
        btn = Button(text='确定', font_name='SimHei', size_hint_y=None, height=40,
                     background_color=COLOR_BTN_BG)
        layout.add_widget(btn)
        popup = Popup(title='', content=layout, size_hint=(0.6, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()

class DrawAwardController(BoxLayout):
    def __init__(self, bet_table, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(36)
        self.spacing = dp(4)
        self.bet_table = bet_table

        btn_size = (dp(100), dp(36))

        self.btn_xinao = Button(
            text='新澳兑奖', font_name='SimHei', font_size=32,
            color=COLOR_TEXT, background_normal='', background_down='',
            background_color=COLOR_BTN_BG, size_hint=(None, None), size=btn_size
        )
        self.btn_xinao.bind(on_press=lambda x: self.do_award('新澳'))
        self.add_widget(self.btn_xinao)

        self.btn_laoao = Button(
            text='老澳兑奖', font_name='SimHei', font_size=32,
            color=COLOR_TEXT, background_normal='', background_down='',
            background_color=COLOR_BTN_BG, size_hint=(None, None), size=btn_size
        )
        self.btn_laoao.bind(on_press=lambda x: self.do_award('老澳'))
        self.add_widget(self.btn_laoao)

        self.btn_hk = Button(
            text='香港兑奖', font_name='SimHei', font_size=32,
            color=COLOR_TEXT, background_normal='', background_down='',
            background_color=COLOR_BTN_BG, size_hint=(None, None), size=btn_size
        )
        self.btn_hk.bind(on_press=lambda x: self.do_award('香港'))
        self.add_widget(self.btn_hk)

    def _get_award_file(self, region):
        return AWARD_FILE_PREFIX + region + ".txt"

    def _load_award_numbers(self, region):
        filepath = self._get_award_file(region)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except:
                return ""
        return ""

    def _save_award_numbers(self, region, text):
        filepath = self._get_award_file(region)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(f"保存开奖号码失败：{e}")

    def open_zodiac_config(self, instance):
        ZodiacConfigWindow().open()

    def parse_draw_numbers(self, raw_text):
        nums = re.findall(r'\b(0?[1-9]|[1-4][0-9]|49)\b', raw_text)
        if not nums:
            return None, None, None, None
        int_nums = []
        seen = set()
        for n in nums:
            num = int(n)
            if 1 <= num <= 49 and num not in seen:
                seen.add(num)
                int_nums.append(num)
        if len(int_nums) < 7:
            return None, None, None, None
        normals = int_nums[:6]
        special = int_nums[6]

        animals = re.findall(r'[鼠牛虎兔龙蛇马羊猴鸡狗猪]', raw_text)
        if len(animals) >= 7:
            normals_animals = animals[:6]
            special_animal = animals[6]
        else:
            normals_animals = [get_animal_by_number(n) for n in normals]
            special_animal = get_animal_by_number(special)
        return normals, special, normals_animals, special_animal

    def _print_draw_info(self, region, normals, special, normals_animals, special_animal):
        all_numbers = normals + [special]
        print(f"\n===== 开始 {region} 兑奖 =====")
        print(f"\n本次开奖号码（原始）：平码 {normals}  特码 {special}")
        normals_str = [f"{n:02d}" for n in normals]
        special_str = f"{special:02d}"
        print(f"标准化两位：平码 {normals_str}  特码 {special_str}")
        print(f"平码生肖：{normals_animals}")
        print(f"特码生肖：{special_animal}")
        print(f"七个号码总和：{sum(all_numbers)}")
        print("==================================================")

    def do_award(self, target_region):
        def on_confirm(final_text):
            self._save_award_numbers(target_region, final_text)
            normals, special, normals_animals, special_animal = self.parse_draw_numbers(final_text)
            if normals is None:
                self.show_popup("错误", "开奖号码格式不正确，需要至少7个1-49的数字")
                return
            draw_numbers = {
                "normal": normals,
                "special": special,
                "normals_animals": normals_animals,
                "special_animal": special_animal
            }
            self._print_draw_info(target_region, normals, special, normals_animals, special_animal)
            self.update_award_for_region(target_region, draw_numbers)

        popup = AwardPreviewPopup(target_region, on_confirm)
        popup.open()

    def update_award_for_region(self, region, draw_numbers):
        draw_key = f"{draw_numbers['normal']}-{draw_numbers['special']}"
        all_numbers = draw_numbers['normal'] + [draw_numbers['special']]
        normals_animals = draw_numbers['normals_animals']
        special_animal = draw_numbers['special_animal']
        all_animals = normals_animals + [special_animal]
        special_color = get_color_by_number(draw_numbers['special'])

        total_bets = 0
        hit_bets = 0
        total_win_amount = 0.0
        details_lines = []

        for idx, row_data in enumerate(self.bet_table.row_data):
            if region == '新澳':
                bet_list = row_data['xinao']
                last_key = row_data.get('xinao_key', '')
            elif region == '老澳':
                bet_list = row_data['laoao']
                last_key = row_data.get('laoao_key', '')
            else:
                bet_list = row_data['hk']
                last_key = row_data.get('hk_key', '')

            if draw_key == last_key:
                continue

            row_win_add = 0.0
            print(f"\n--- 处理第 {idx+1} 行 (订单金额: {row_data['order_money']:.2f}) ---")
            for i, unit in enumerate(bet_list, 1):
                amt = unit['amount']
                pt = unit['play_type']
                extra = unit['extra']
                total_bets += 1

                bet_desc = []
                if extra:
                    if 'numbers' in extra and extra['numbers']:
                        bet_desc.append(f"号码:{','.join(extra['numbers'])}")
                    if 'animals' in extra and extra['animals']:
                        bet_desc.append(f"生肖:{','.join(extra['animals'])}")
                    if 'combos' in extra and extra['combos']:
                        combo_str = ';'.join([','.join(c) for c in extra['combos']])
                        bet_desc.append(f"组合:{combo_str}")
                    if 'tail' in extra:
                        bet_desc.append(f"尾数:{extra['tail']}")
                if not bet_desc:
                    bet_desc.append("无明细")
                bet_info = " | ".join(bet_desc)

                win = calc_win_amount(pt, amt, extra, draw_numbers)

                odds = ODDS.get(pt, 0)
                if pt in ["二连肖","三连肖","四连肖","五连肖"] and extra and extra.get('has_horse'):
                    odds = ODDS.get(pt + "马", 0)
                elif pt == "平特" and extra and extra.get('is_horse'):
                    odds = ODDS.get("平特马", 0)
                elif pt == "平特尾":
                    tail = extra.get('tail', '')
                    odds = ODDS.get("平特0尾" if tail == '0' else "平特1-9尾", 0)

                hit_desc = self._get_hit_desc(pt, extra, draw_numbers, all_animals, special_animal)

                if win > 0:
                    hit_bets += 1
                    total_win_amount += win
                    row_win_add += win
                    print(f"  【中奖】玩法:{pt if pt else '直接投注'} | {bet_info} | 命中:{hit_desc} | 赔率:{odds} | 中奖:{win:.2f}")
                else:
                    print(f"  【未中奖】玩法:{pt if pt else '直接投注'} | {bet_info} | 开奖:{hit_desc} | 未中奖")

                if win > 0:
                    details_lines.append(
                        f"【中奖】玩法:{pt if pt else '直接投注'} | {bet_info} | "
                        f"命中:{hit_desc} | 赔率:{odds} | 下注:{amt:.2f} → 中奖:{win:.2f}"
                    )
                else:
                    details_lines.append(
                        f"【未中奖】玩法:{pt if pt else '直接投注'} | {bet_info} | "
                        f"开奖:{hit_desc} | 未命中"
                    )

            if row_win_add > 0:
                row_data['win_money'] += row_win_add
                self.bet_table.row_list[idx][2].value = row_data['win_money']
                self.bet_table.row_list[idx][2].manual_edited = True
                self.bet_table.calc_row(idx)

            if region == '新澳':
                row_data['xinao_key'] = draw_key
            elif region == '老澳':
                row_data['laoao_key'] = draw_key
            else:
                row_data['hk_key'] = draw_key
            self.bet_table.save_data()

        print("\n==================================================")
        if total_bets == 0:
            print("暂无中奖数据")
        elif hit_bets == 0:
            print("暂无中奖数据")
        else:
            print(f"本区兑奖汇总：总注数 {total_bets}，中奖注数 {hit_bets}，累计中奖金额 {total_win_amount:.2f}")
            print(f"已自动累加写入表格「中码金额」列")
        print("==================================================\n")

        self._show_detailed_award_result(
            region, draw_numbers, all_animals, special_color,
            total_bets, hit_bets, total_win_amount, details_lines
        )

        if self.bet_table.on_data_changed:
            self.bet_table.on_data_changed()

    def _get_hit_desc(self, play_type, extra, draw_numbers, all_animals, special_animal):
        special = draw_numbers['special']
        normals = draw_numbers['normal']
        all_numbers = normals + [special]
        if play_type == "特码":
            return f"特码 {special}"
        if play_type == "特码大小":
            return f"特码 {special} ({'大' if special>24 else '小'})"
        if play_type == "特码单双":
            return f"特码 {special} ({'单' if special%2 else '双'})"
        if play_type == "特码合数大小":
            ds = sum(int(d) for d in str(special))
            return f"特码 {special} 合数 {'大' if 7<=ds<=12 else '小'}"
        if play_type == "特码合数单双":
            ds = sum(int(d) for d in str(special))
            return f"特码 {special} 合数 {'单' if ds%2 else '双'}"
        if play_type in ["特天肖","特地肖","特前肖","特后肖","特家肖","特野肖"]:
            return f"特码生肖 {special_animal}"
        if play_type == "特码尾数大小":
            tail = special % 10
            return f"特码尾数 {tail} ({'大' if tail>=5 else '小'})"
        if play_type in ["总和单双","总和大小"]:
            total = sum(all_numbers)
            if play_type == "总和单双":
                return f"总和 {total} ({'单' if total%2 else '双'})"
            else:
                return f"总和 {total} ({'大' if total>=175 else '小'})"
        if play_type in ["红波","蓝波","绿波"]:
            color = get_color_by_number(special)
            return f"特码波色 {color}"
        if play_type in ["六肖","六中"]:
            return f"特码生肖 {special_animal}"
        if play_type in ["五不中","六不中","七不中","八不中","九不中","十不中"]:
            chosen = extra.get('numbers', [])
            if chosen:
                return f"自选号码 {','.join(chosen)} 全部未开出"
            return "自选号码全部未开出"
        if play_type in ["二连肖","三连肖","四连肖","五连肖"]:
            combos = extra.get('combos', [])
            if combos:
                return f"连肖组合 {','.join([','.join(c) for c in combos])}"
            animals = extra.get('animals', [])
            if animals:
                return f"连肖 {','.join(animals)}"
        if play_type == "平特":
            animal = extra.get('animal', '')
            if animal:
                return f"平特 {animal}"
            combos = extra.get('combos', [])
            if combos:
                return f"平特组合 {','.join([','.join(c) for c in combos])}"
        if play_type == "平特尾":
            tail = extra.get('tail', '')
            return f"平特尾 {tail}尾"
        if play_type == "二全中":
            nums = extra.get('numbers', [])
            if len(nums) >= 2:
                return f"二全中号码 {nums[0]},{nums[1]}"
        if play_type == "三全中":
            nums = extra.get('numbers', [])
            if len(nums) >= 3:
                return f"三全中号码 {nums[0]},{nums[1]},{nums[2]}"
        return "直接投注"

    def _show_detailed_award_result(self, region, draw_numbers, all_animals, special_color,
                                    total_bets, hit_bets, total_win, details_lines):
        normals = draw_numbers['normal']
        special = draw_numbers['special']
        now = datetime.now()
        period = now.strftime("%Y%m%d%H%M%S")
        hour = now.hour
        if 23 <= hour or hour < 5:
            shichen = "子时"
        elif 5 <= hour < 7:
            shichen = "卯时"
        elif 7 <= hour < 9:
            shichen = "辰时"
        elif 9 <= hour < 11:
            shichen = "巳时"
        elif 11 <= hour < 13:
            shichen = "午时"
        elif 13 <= hour < 15:
            shichen = "未时"
        elif 15 <= hour < 17:
            shichen = "申时"
        elif 17 <= hour < 19:
            shichen = "酉时"
        elif 19 <= hour < 21:
            shichen = "戌时"
        else:
            shichen = "亥时"

        draw_info = f"平码：{', '.join(map(str, normals))}\n"
        draw_info += f"平码生肖：{', '.join(all_animals[:6])}\n"
        draw_info += f"特码：{special}  生肖：{all_animals[6]}  波色：{special_color}\n"
        draw_info += f"七个号码总和：{sum(normals) + special}"

        if details_lines:
            bet_details = "\n".join(details_lines)
        else:
            bet_details = "无投注记录"

        if total_bets == 0:
            summary = "本次兑奖：全区无投注记录"
        elif hit_bets == 0:
            summary = "本次兑奖：全区无中奖记录"
        else:
            summary = f"总注数：{total_bets}，中奖注数：{hit_bets}，累计中奖金额：{total_win:.2f}\n中奖金额已自动累加入表格「中码金额」列。"

        content_text = (
            f"===== {region} 兑奖结果 =====\n"
            f"期数：{period}  时辰：{shichen}\n\n"
            f"【开奖详情】\n{draw_info}\n\n"
            f"【下单明细】\n{bet_details}\n\n"
            f"【汇总】\n{summary}"
        )

        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        title_label = Label(
            text='兑奖详细信息',
            font_name='SimHei',
            font_size=28,
            bold=True,
            color=(1,1,1,1),
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title_label)
        
        scroll = ScrollView(size_hint=(1, 0.8))
        content_label = Label(
            text=content_text,
            font_name='SimHei',
            font_size=20,
            color=(1,1,1,1),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        content_label.bind(texture_size=lambda inst, sz: setattr(inst, 'height', sz[1]))
        scroll.add_widget(content_label)
        layout.add_widget(scroll)
        btn_ok = Button(text='确定', font_name='SimHei', size_hint_y=None, height=40, background_color=COLOR_BTN_BG)
        layout.add_widget(btn_ok)
        popup = Popup(title='', content=layout, size_hint=(0.9, 0.8))
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def show_popup(self, title, msg):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        layout.add_widget(Label(text=title, font_name='SimHei', font_size=24,
                                color=(1,1,1,1), bold=True, size_hint_y=None, height=30))
        layout.add_widget(Label(text=msg, font_name='SimHei', font_size=20,
                                color=(1,1,1,1), size_hint_y=None, height=40))
        btn = Button(text='确定', font_name='SimHei', size_hint_y=None, height=40,
                     background_color=COLOR_BTN_BG)
        layout.add_widget(btn)
        popup = Popup(title='', content=layout, size_hint=(0.7, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()

class PastePreviewPopup(Popup):
    def __init__(self, content, on_confirm, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.7, None)
        self.auto_dismiss = False
        self.on_confirm = on_confirm

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        title_label = Label(
            text='粘贴内容预览',
            font_name='SimHei',
            font_size=28,
            bold=True,
            color=(0.4,0.7,1,1),
            size_hint_x=None,
            width=180
        )
        self.stats_label = Label(
            text='',
            font_name='SimHei',
            font_size=26,
            color=(0.4,0.7,1,1),
            size_hint_x=1,
            halign='right'
        )
        header.add_widget(title_label)
        header.add_widget(self.stats_label)
        layout.add_widget(header)

        self.content_label = Label(
            text=content,
            font_name='SimHei',
            font_size=26,
            color=(1,1,1,1),
            size_hint_y=None,
            text_size=(Window.width * 0.7 - 40, None),
            halign='left',
            valign='top',
            padding=(5,20)
        )
        self.content_label.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1]))
        layout.add_widget(self.content_label)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_cancel = Button(text='取消', font_name='SimHei', font_size=20)
        btn_cancel.bind(on_press=self.dismiss)
        btn_ok = Button(text='确认', font_name='SimHei', font_size=20)
        btn_ok.bind(on_press=self.do_confirm)
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)
        layout.add_widget(btn_layout)

        self.content = layout

        def update_height(*_):
            self.height = layout.minimum_height + 20
        layout.bind(minimum_height=update_height)
        self.content_label.bind(texture_size=update_height)

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: update_height(), 0.1)

        self._update_stats()

    def _update_stats(self):
        text = self.content_label.text
        lines = len(text.splitlines())
        chars = len(text)
        self.stats_label.text = f"{lines}行 · {chars}字"

    def do_confirm(self, *args):
        self.dismiss()
        if self.on_confirm:
            self.on_confirm(self.content_label.text)

class AwardPreviewPopup(Popup):
    def __init__(self, region, on_confirm, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.7, None)
        self.auto_dismiss = False
        self.on_confirm = on_confirm
        self.region = region

        clipboard_text = Clipboard.paste().strip()
        self.initial_text = clipboard_text

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        title_label = Label(
            text=f'{region}兑奖预览',
            font_name='SimHei',
            font_size=28,
            bold=True,
            color=(0.4,0.7,1,1),
            size_hint_x=None,
            width=180
        )
        self.stats_label = Label(
            text='',
            font_name='SimHei',
            font_size=26,
            color=(0.4,0.7,1,1),
            size_hint_x=1,
            halign='right'
        )
        header.add_widget(title_label)
        header.add_widget(self.stats_label)
        layout.add_widget(header)

        self.content_input = TextInput(
            text=self.initial_text,
            font_name='SimHei',
            font_size=26,
            foreground_color=(0,0,0,1),
            background_color=(0.95,0.95,0.95,1),
            size_hint_y=None,
            height=200,
            multiline=True,
            padding=(10,10)
        )
        self.content_input.bind(text=self._update_stats)
        layout.add_widget(self.content_input)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_cancel = Button(text='取消', font_name='SimHei', font_size=20)
        btn_cancel.bind(on_press=self.dismiss)
        btn_ok = Button(text='确认', font_name='SimHei', font_size=20)
        btn_ok.bind(on_press=self.do_confirm)
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)
        layout.add_widget(btn_layout)

        self.content = layout

        def update_height(*_):
            inp_h = self.content_input.minimum_height
            final_h = min(inp_h, Window.height * 0.6)
            self.content_input.height = final_h
            self.height = layout.minimum_height + 20
        layout.bind(minimum_height=update_height)
        self.content_input.bind(minimum_height=update_height)

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: (self._update_stats(), update_height()), 0.1)

    def _update_stats(self, *args):
        text = self.content_input.text
        lines = len(text.splitlines())
        chars = len(text)
        self.stats_label.text = f"{lines}行 · {chars}字"

    def do_confirm(self, *args):
        self.dismiss()
        if self.on_confirm:
            self.on_confirm(self.content_input.text)

# ==================== 澳门统计页面（新表格样式） ====================
SECONDARY_LOSS_FACTOR = 1.0
TOTAL_SHARES = 48

# 自定义合并单元格（总亏损/次级亏损）
class MergedLossCell(BoxLayout):
    def __init__(self, loss, secondary, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.size_hint_y = None
        self.height = ROW_H   
        with self.canvas.before:
            Color(*COLOR_NORMAL_BG)
            self.bg = Rectangle(pos=self.pos, size=self.size)
            Color(*COLOR_BORDER)
            self.line = Line(width=1)
        self.bind(pos=self.update, size=self.update)

        # 上行：总亏损（红色背景）
        loss_bg = COLOR_NEGATIVE if loss > 0 else COLOR_NORMAL_BG
        self.loss_label = Label(
            text=f"{loss:.2f}",
            font_name='SimHei',
            font_size=28,
            color=(1,0,0,1) if loss > 0 else COLOR_TEXT,
            halign='center',
            valign='middle',
            size_hint_y=0.5
        )
        with self.loss_label.canvas.before:
            Color(*loss_bg)
            self.loss_bg_rect = Rectangle(pos=self.loss_label.pos, size=self.loss_label.size)
        self.loss_label.bind(pos=self.update_loss_bg, size=self.update_loss_bg)

        # 下行：次级亏损
        sec_bg = COLOR_NEGATIVE if secondary > 0 else COLOR_NORMAL_BG
        self.sec_label = Label(
            text=f"{secondary:.2f}",
            font_name='SimHei',
            font_size=28,
            color=COLOR_TEXT,
            halign='center',
            valign='middle',
            size_hint_y=0.5
        )
        with self.sec_label.canvas.before:
            Color(*sec_bg)
            self.sec_bg_rect = Rectangle(pos=self.sec_label.pos, size=self.sec_label.size)
        self.sec_label.bind(pos=self.update_sec_bg, size=self.update_sec_bg)

        self.add_widget(self.loss_label)
        self.add_widget(self.sec_label)

    def update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.line.rectangle = (self.x, self.y, self.width, self.height)
        # 更新子控件背景
        self.update_loss_bg()
        self.update_sec_bg()

    def update_loss_bg(self, *args):
        self.loss_bg_rect.pos = self.loss_label.pos
        self.loss_bg_rect.size = self.loss_label.size

    def update_sec_bg(self, *args):
        self.sec_bg_rect.pos = self.sec_label.pos
        self.sec_bg_rect.size = self.sec_label.size

class MacaoStatsPage(BoxLayout):
    def __init__(self, bet_table, **kwargs):
        super().__init__(orientation='vertical', padding=dp(8), spacing=dp(6), **kwargs)
        self.bet_table = bet_table
        self.included_rows = {}
        self.history = []
        self.stats = {}   # 格式: {"01": {"animal":"马","bet":0,"win":0,"count":0}, ...}

        # 红色标题栏
        title_bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        with title_bar.canvas.before:
            Color(1, 0.2, 0.2, 1)
            self.title_rect = Rectangle(pos=title_bar.pos, size=title_bar.size)
        title_bar.bind(pos=self._update_title_rect, size=self._update_title_rect)

        btn_one_key = Button(text='一键打单', font_name='SimHei', font_size=30,
                             color=(1,1,1,1), background_color=(1,1,1,0.3),
                             size_hint=(None,None), size=(dp(100), dp(36)))
        btn_reset = Button(text='重置', font_name='SimHei', font_size=30,
                           color=(1,1,1,1), background_color=(1,1,1,0.3),
                           size_hint=(None,None), size=(dp(80), dp(36)))
        btn_reset.bind(on_press=lambda x: self.reset_stats())
        title_label = Label(text='澳门统计', font_name='SimHei', font_size=34,
                            color=(1,1,1,1), bold=True, size_hint_x=1, halign='center')
        title_bar.add_widget(btn_one_key)
        title_bar.add_widget(title_label)
        title_bar.add_widget(btn_reset)
        self.add_widget(title_bar)

        # 功能按钮
        func_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        btn_parse = Button(text='解析添加', font_name='SimHei', font_size=32,
                           background_color=COLOR_BTN_BG, color=COLOR_TEXT)
        btn_parse.bind(on_press=lambda x: self.parse_and_add())
        btn_undo = Button(text='撤销上次', font_name='SimHei', font_size=32,
                          background_color=COLOR_BTN_BG, color=COLOR_TEXT)
        btn_undo.bind(on_press=lambda x: self.undo_last())
        btn_export = Button(text='一键导出', font_name='SimHei', font_size=32,
                            background_color=COLOR_BTN_BG, color=COLOR_TEXT)
        btn_export.bind(on_press=lambda x: self.export_to_excel())
        func_bar.add_widget(btn_parse)
        func_bar.add_widget(btn_undo)
        func_bar.add_widget(btn_export)
        self.add_widget(func_bar)

        # 提示文本
        self.hint_label = Label(
            text='总投注/48 = ?\n? × 2 = ?\n? × 2.5 = ?\n总合计：?',
            font_name='SimHei', font_size=26, color=COLOR_TEXT,
            size_hint_y=None, height=dp(80), halign='left', valign='middle',
            padding=(10, 0)
        )
        self.add_widget(self.hint_label)

        # 汇总栏
        summary_bar = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(4))
        self.lbl_total_bet = Label(text='总投注：0', font_name='SimHei', font_size=28, color=COLOR_TEXT)
        self.lbl_total_count = Label(text='总个数：0', font_name='SimHei', font_size=28, color=COLOR_TEXT)
        self.lbl_max_loss = Label(text='最大亏损：0', font_name='SimHei', font_size=28, color=COLOR_TEXT)
        summary_bar.add_widget(self.lbl_total_bet)
        summary_bar.add_widget(self.lbl_total_count)
        summary_bar.add_widget(self.lbl_max_loss)
        self.add_widget(summary_bar)

        # 表格容器
        self.table_container = BoxLayout(orientation='vertical', spacing=0)
        self.add_widget(self.table_container)

    def _update_title_rect(self, *args):
        self.title_rect.pos = args[0].pos
        self.title_rect.size = args[0].size

    def parse_and_add(self):
        if not self.bet_table or not self.bet_table.row_data:
            return
        new_ids = []
        for row_data in self.bet_table.row_data:
            row_id = row_data['row_id']
            if row_id not in self.included_rows:
                if row_data.get('xinao'):
                    new_ids.append(row_id)
                    self.included_rows[row_id] = {
                        'order_money': row_data['order_money'],
                        'win_money': row_data['win_money'],
                        'xinao_units': row_data['xinao']
                    }
        if new_ids:
            self.history.append(new_ids)
            self.refresh_ui()
        else:
            self._show_popup('提示', '没有新的特码投注数据')

    def undo_last(self):
        if not self.history:
            self._show_popup('提示', '没有可撤销的操作')
            return
        last_ids = self.history.pop()
        for rid in last_ids:
            if rid in self.included_rows:
                del self.included_rows[rid]
        self.refresh_ui()

    def reset_stats(self):
        self.included_rows.clear()
        self.history.clear()
        self.refresh_ui()

    def refresh_ui(self):
        self.stats = self._calc_stats()
        self._update_hint()
        self._update_summary()
        self._build_table()

    def _calc_stats(self):
        num_stats = {f"{n:02d}": {'animal': get_animal_by_number(n), 'bet': 0.0, 'win': 0.0, 'rows': set()} for n in range(1,50)}

        for row_id, row_info in self.included_rows.items():
            row_order = row_info['order_money']
            row_win = row_info['win_money']
            row_num_bet = {}

            for unit in row_info['xinao_units']:
                pt = unit.get('play_type')
                extra = unit.get('extra', {})
                bet_type = extra.get('bet_type', '')

                if pt != '特码' and bet_type not in ('各数', '各号'):
                    continue

                amount = unit.get('amount', 0)
                if amount <= 0:
                    continue

                if bet_type == '各号' and extra.get('animals'):
                    animals = extra['animals']
                    all_nums = []
                    for an in animals:
                        if an in ANIMALS:
                            all_nums.extend([f"{n:02d}" for n in ANIMALS[an]])
                    if not all_nums:
                        continue
                    per_num = amount / len(all_nums)
                    for num in all_nums:
                        row_num_bet[num] = row_num_bet.get(num, 0.0) + per_num
                else:
                    numbers = extra.get('numbers', [])
                    if not numbers:
                        continue
                    per_num = amount / len(numbers)
                    for num in numbers:
                        if 1 <= int(num) <= 49:
                            row_num_bet[num] = row_num_bet.get(num, 0.0) + per_num

            total_row_bet = sum(row_num_bet.values())
            if total_row_bet > 0:
                for num, bet in row_num_bet.items():
                    num_stats[num]['bet'] += bet
                    num_stats[num]['rows'].add(row_id)  # 用row_info作为唯一标识
                    if row_order > 0:
                        proportion = bet / total_row_bet
                        num_stats[num]['win'] += row_win * proportion

        final_stats = {}
        for num, data in num_stats.items():
            if data['bet'] == 0.0:
                continue
            loss = data['bet'] - data['win']
            final_stats[num] = {
                'animal': data['animal'],
                'bet': data['bet'],
                'win': data['win'],
                'loss': loss,
                'secondary_loss': loss * SECONDARY_LOSS_FACTOR,
                'count': len(data['rows']),
                'last_number': int(num)
            }
        return final_stats

    def _update_hint(self):
        total_bet = sum(s['bet'] for s in self.stats.values())
        base = total_bet / TOTAL_SHARES if total_bet > 0 else 0
        double_val = base * 2
        coeff_val = base * 2.5
        total_bet_all = sum(row['order_money'] for row in self.included_rows.values())
        self.hint_label.text = (
            f"总投注/{TOTAL_SHARES} = {base:.2f}\n"
            f"{base:.2f} × 2 = {double_val:.2f}\n"
            f"{base:.2f} × 2.5 = {coeff_val:.2f}\n"
            f"总合计：{total_bet_all:.2f}"
        )

    def _update_summary(self):
        if not self.stats:
            self.lbl_total_bet.text = '总投注：0.00'
            self.lbl_total_count.text = '总个数：0'
            self.lbl_max_loss.text = '最大亏损：0.00'
            return
        total_bet = sum(s['bet'] for s in self.stats.values())
        total_count = len(self.stats)
        max_loss = max(s['loss'] for s in self.stats.values())
        self.lbl_total_bet.text = f"总投注：{total_bet:.2f}"
        self.lbl_total_count.text = f"总个数：{total_count}"
        self.lbl_max_loss.text = f"最大亏损：{max_loss:.2f}"

    def _build_table(self):
        self.table_container.clear_widgets()

        if not self.stats:
            return

        # 表头：序号生肖号码、总亏损/次级亏损、累计中奖金额、投注期数
        header_grid = GridLayout(cols=4, spacing=0, size_hint_y=None, height=ROW_H)
        headers = ['序号生肖号码', '总亏损/次级亏损', '累计中奖金额', '投注期数']
        for i, h in enumerate(headers):
            c = Cell(text=h, bold=True, bg=COLOR_HEADER_BG)
            if i == 0:
                c.size_hint_x = None
                c.width = dp(100)
            header_grid.add_widget(c)
        self.table_container.add_widget(header_grid)

        # 数据行
        scroll = ScrollView()
        grid = GridLayout(cols=4, spacing=0, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        sorted_nums = sorted(self.stats.keys(), key=lambda x: int(x))
        idx = 1
        for num in sorted_nums:
            s = self.stats[num]
            animal = s['animal']
            display_text = f"{idx}.{animal}{s['last_number']}" if animal else f"{idx}.{s['last_number']}"

            # 第一列
            first_cell = Cell(text=display_text, bg=COLOR_NORMAL_BG)
            first_cell.size_hint_x = None
            first_cell.width = dp(100)
            grid.add_widget(first_cell)

            # 第二列：合并单元格
            merged = MergedLossCell(s['loss'], s['secondary_loss'])
            grid.add_widget(merged)

            # 第三列：累计中奖金额
            grid.add_widget(Cell(text=f"{s['win']:.2f}", bg=COLOR_NORMAL_BG))

            # 第四列：投注期数
            grid.add_widget(Cell(text=str(s['count']), bg=COLOR_NORMAL_BG))

            idx += 1

        scroll.add_widget(grid)
        self.table_container.add_widget(scroll)

    def export_to_excel(self):
        if not OPENPYXL_AVAILABLE:
            self._show_popup('错误', '请安装 openpyxl 库')
            return
        wb = Workbook()
        ws = wb.active
        ws.title = '澳门统计'
        headers = ['序号生肖号码', '总亏损/次级亏损', '累计中奖金额', '投注期数']
        ws.append(headers)
        sorted_nums = sorted(self.stats.keys(), key=lambda x: int(x))
        idx = 1
        for num in sorted_nums:
            s = self.stats[num]
            animal = s['animal']
            display_text = f"{idx}.{animal}{s['last_number']}" if animal else f"{idx}.{s['last_number']}"
            # 第二列用换行符合并
            loss_sec = f"{s['loss']:.2f}\n{s['secondary_loss']:.2f}"
            ws.append([display_text, loss_sec, s['win'], s['count']])
            idx += 1
        filename = f"澳门统计_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb.save(filename)
        self._show_popup('导出成功', f'已保存：{filename}')

    def _show_popup(self, title, msg):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        layout.add_widget(Label(text=title, font_name='SimHei', font_size=24, color=(0,0,0,1), bold=True, size_hint_y=None, height=30))
        layout.add_widget(Label(text=msg, font_name='SimHei', font_size=20, color=(0,0,0,1), size_hint_y=None, height=40))
        btn = Button(text='确定', font_name='SimHei', size_hint_y=None, height=40, background_color=COLOR_BTN_BG)
        layout.add_widget(btn)
        popup = Popup(title='', content=layout, size_hint=(0.7, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()

# ==================== 主应用 ====================
class MainApp(App):
    def build(self):
        # ================== 防盗判断（我加的） ==================
        if not is_activated():
            return ActivateUI(self)
        # ======================================================

        Window.clearcolor = (1,1,1,1)
        Window.size = (360, 640)
        root = BoxLayout(orientation='vertical', spacing=0)

        original_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        bar1 = BoxLayout(spacing=dp(4), size_hint_y=None, height=dp(36))
        btn_paste = Button(text="一键粘贴", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                           background_normal='', background_down='',
                           background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_paste.bind(on_press=lambda x: self.table_container.paste_smart())
        btn_del = Button(text="删除选中", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                         background_normal='', background_down='',
                         background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_del.bind(on_press=lambda x: self.table_container.delete_selected())
        btn_export = Button(text="导出表格", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                            background_normal='', background_down='',
                            background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_export.bind(on_press=lambda x: self.table_container.export_to_excel())
        bar1.add_widget(btn_paste)
        bar1.add_widget(btn_del)
        bar1.add_widget(btn_export)

        self.table_container = FixedHeaderTable()
        self.draw_ctl = DrawAwardController(self.table_container.table)

        bar2 = BoxLayout(spacing=dp(4), size_hint_y=None, height=dp(36))
        btn_insert = Button(text="插入单行", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                            background_normal='', background_down='',
                            background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_insert.bind(on_press=lambda x: self.table_container.insert_empty_row())
        btn_clear = Button(text="清除表格", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                           background_normal='', background_down='',
                           background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_clear.bind(on_press=lambda x: self.table_container.clear_all())
        btn_zodiac_bar2 = Button(text="生肖号码", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                           background_normal='', background_down='',
                           background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_zodiac_bar2.bind(on_press=lambda x: ZodiacConfigWindow().open())

        bar2.add_widget(btn_insert)
        bar2.add_widget(btn_clear)
        bar2.add_widget(btn_zodiac_bar2)
        spacer = Label(size_hint_x=1)
        bar2.add_widget(spacer)

        original_layout.add_widget(bar1)
        original_layout.add_widget(self.draw_ctl)
        original_layout.add_widget(bar2)
        original_layout.add_widget(self.table_container)

        self.macao_page = MacaoStatsPage(bet_table=self.table_container.table)

        self.content_area = BoxLayout(orientation='vertical')
        self.content_area.add_widget(original_layout)
        self.current_page = 'record'

        nav_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6), padding=[dp(10), dp(6)])
        with nav_bar.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.nav_rect = Rectangle(pos=nav_bar.pos, size=nav_bar.size)
        nav_bar.bind(pos=self._update_nav_rect, size=self._update_nav_rect)

        def make_nav_btn(text, page):
            btn = Button(text=text, font_name='SimHei', font_size=28,
                         background_normal='', background_down='',
                         background_color=(0.9,0.9,0.9,1),
                         color=(0.2,0.2,0.2,1))
            btn.bind(on_press=lambda x: self.switch_page(page))
            return btn

        btn_macao = make_nav_btn('澳门', 'macao')
        btn_hk = make_nav_btn('香港', 'hk')
        btn_record = make_nav_btn('记录', 'record')
        btn_my = make_nav_btn('我的', 'my')

        nav_bar.add_widget(btn_macao)
        nav_bar.add_widget(btn_hk)
        nav_bar.add_widget(btn_record)
        nav_bar.add_widget(btn_my)

        root.add_widget(self.content_area)
        root.add_widget(nav_bar)

        self.original_layout = original_layout
        self.root_widget = root  # 我加的
        return root

    # ================== 激活后加载主界面（我加的） ==================
    def load_main_ui(self):
        self.root.clear_widgets()
        self.root.add_widget(self.build_original())

    def build_original(self):
        Window.clearcolor = (1,1,1,1)
        Window.size = (360, 640)
        root = BoxLayout(orientation='vertical', spacing=0)

        original_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        bar1 = BoxLayout(spacing=dp(4), size_hint_y=None, height=dp(36))
        btn_paste = Button(text="一键粘贴", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                           background_normal='', background_down='',
                           background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_paste.bind(on_press=lambda x: self.table_container.paste_smart())
        btn_del = Button(text="删除选中", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                         background_normal='', background_down='',
                         background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_del.bind(on_press=lambda x: self.table_container.delete_selected())
        btn_export = Button(text="导出表格", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                            background_normal='', background_down='',
                            background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_export.bind(on_press=lambda x: self.table_container.export_to_excel())
        bar1.add_widget(btn_paste)
        bar1.add_widget(btn_del)
        bar1.add_widget(btn_export)

        self.table_container = FixedHeaderTable()
        self.draw_ctl = DrawAwardController(self.table_container.table)

        bar2 = BoxLayout(spacing=dp(4), size_hint_y=None, height=dp(36))
        btn_insert = Button(text="插入单行", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                            background_normal='', background_down='',
                            background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_insert.bind(on_press=lambda x: self.table_container.insert_empty_row())
        btn_clear = Button(text="清除表格", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                           background_normal='', background_down='',
                           background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_clear.bind(on_press=lambda x: self.table_container.clear_all())
        btn_zodiac_bar2 = Button(text="生肖号码", font_name='SimHei', font_size=32, color=COLOR_TEXT,
                           background_normal='', background_down='',
                           background_color=COLOR_BTN_BG, size_hint=(None,None), size=(dp(100),dp(36)))
        btn_zodiac_bar2.bind(on_press=lambda x: ZodiacConfigWindow().open())

        bar2.add_widget(btn_insert)
        bar2.add_widget(btn_clear)
        bar2.add_widget(btn_zodiac_bar2)
        spacer = Label(size_hint_x=1)
        bar2.add_widget(spacer)

        original_layout.add_widget(bar1)
        original_layout.add_widget(self.draw_ctl)
        original_layout.add_widget(bar2)
        original_layout.add_widget(self.table_container)

        self.macao_page = MacaoStatsPage(bet_table=self.table_container.table)

        self.content_area = BoxLayout(orientation='vertical')
        self.content_area.add_widget(original_layout)
        self.current_page = 'record'

        nav_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6), padding=[dp(10), dp(6)])
        with nav_bar.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.nav_rect = Rectangle(pos=nav_bar.pos, size=nav_bar.size)
        nav_bar.bind(pos=self._update_nav_rect, size=self._update_nav_rect)

        def make_nav_btn(text, page):
            btn = Button(text=text, font_name='SimHei', font_size=28,
                         background_normal='', background_down='',
                         background_color=(0.9,0.9,0.9,1),
                         color=(0.2,0.2,0.2,1))
            btn.bind(on_press=lambda x: self.switch_page(page))
            return btn

        btn_macao = make_nav_btn('澳门', 'macao')
        btn_hk = make_nav_btn('香港', 'hk')
        btn_record = make_nav_btn('记录', 'record')
        btn_my = make_nav_btn('我的', 'my')

        nav_bar.add_widget(btn_macao)
        nav_bar.add_widget(btn_hk)
        nav_bar.add_widget(btn_record)
        nav_bar.add_widget(btn_my)

        root.add_widget(self.content_area)
        root.add_widget(nav_bar)

        self.original_layout = original_layout
        return root
    # =================================================================

    def _update_nav_rect(self, *args):
        self.nav_rect.pos = args[0].pos
        self.nav_rect.size = args[0].size

    def switch_page(self, page):
        if page == self.current_page:
            return
        self.content_area.clear_widgets()
        if page == 'macao':
            self.content_area.add_widget(self.macao_page)
            self.current_page = 'macao'
        else:
            self.content_area.add_widget(self.original_layout)
            self.current_page = 'record'

    def on_stop(self):
        self.table_container.table.save_data()

if __name__ == "__main__":
    MainApp().run()
