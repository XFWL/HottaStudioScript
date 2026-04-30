import tkinter as tk
from tkinter import ttk, messagebox
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
import os
import json
import time
import keyboard
import ctypes
import sys

pyautogui.FAILSAFE = False

def get_resource_path(relative_path):
    """获取资源文件的绝对路径 - 支持开发环境和打包后"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("权限警告", "建议以管理员权限运行此脚本，否则可能无法正常操作游戏窗口。")
    root.destroy()

class ConfigManager:
    """配置管理器 - 处理设置的保存和加载"""
    CONFIG_DIR = "config"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
    
    @staticmethod
    def ensure_config_dir():
        if not os.path.exists(ConfigManager.CONFIG_DIR):
            os.makedirs(ConfigManager.CONFIG_DIR)
    
    @staticmethod
    def save_settings(settings):
        try:
            ConfigManager.ensure_config_dir()
            with open(ConfigManager.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False
    
    @staticmethod
    def load_settings():
        try:
            if os.path.exists(ConfigManager.CONFIG_FILE):
                with open(ConfigManager.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载设置失败: {e}")
        return None

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("异环小工具")
        self.root.geometry("900x950")
        
        self.root.configure(bg="#f0f0f0")
        
        try:
            from ctypes import windll, byref, sizeof, c_int
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            windll.shcore.SetProcessDpiAwareness(1)
            windll.user32.SetWindowLongW(hwnd, -20, windll.user32.GetWindowLongW(hwnd, -20) | 0x80000)
            windll.user32.SetLayeredWindowAttributes(hwnd, 0, 150, 0x2)
        except:
            try:
                self.root.attributes('-alpha', 0.6)
            except:
                pass
        
        self.cancelled = False
        self.current_round_log_count = 0
        self.current_round = 0
        
        self.setup_hotkeys()
        
        style = ttk.Style()
        style.configure("Main.TFrame", background="#f0f0f0")
        style.configure("Title.TLabel", font=("SimHei", 12, "bold"), background="#f0f0f0", foreground="#333333")
        style.configure("Subtitle.TLabel", font=("SimHei", 10, "bold"), background="#f0f0f0", foreground="#555555")
        style.configure("TButton", font=("SimHei", 10, "bold"), padding=8, background="#4CAF50", foreground="black")
        style.configure("Hotkey.TLabel", font=("Arial", 10, "italic"), background="#f0f0f0", foreground="#0066cc")
        style.configure("Log.TLabel", font=("SimHei", 10), background="#f0f0f0", foreground="#333333")
        style.configure("Status.TLabel", font=("SimHei", 10), background="#f0f0f0", foreground="#0066cc")
        
        main_frame = ttk.Frame(root, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(main_frame, text="选择目标窗口:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)
        window_frame = ttk.Frame(main_frame, style="Main.TFrame")
        window_frame.pack(anchor=tk.NW, pady=3)
        self.window_var = tk.StringVar()
        self.window_combobox = ttk.Combobox(window_frame, textvariable=self.window_var, width=40)
        self.window_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Button(window_frame, text="刷新", command=self.refresh_windows).pack(side=tk.LEFT, padx=5)
        ttk.Button(window_frame, text="保存设置", command=self.save_all_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(window_frame, text="加载设置", command=self.load_all_settings).pack(side=tk.LEFT, padx=5)
        
        self.refresh_windows()
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        from shop_module import ShopModule
        from fishing_module import FishingModule
        
        self.shop_module = ShopModule(self, self.notebook)
        self.fishing_module = FishingModule(self, self.notebook)
        
        self.load_all_settings()
    
    def setup_hotkeys(self):
        keyboard.add_hotkey('f12', self.cancel_operation)
    
    def cancel_operation(self):
        self.cancelled = True
        self.log("操作已取消")
    
    def refresh_windows(self):
        try:
            windows = gw.getAllTitles()
            valid_windows = [w for w in windows if w.strip()]
            self.window_combobox['values'] = valid_windows
        except Exception as e:
            messagebox.showerror("错误", f"获取窗口列表失败: {str(e)}")
    
    def find_window(self, title):
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                return windows[0]
            return None
        except Exception as e:
            self.log(f"查找窗口失败: {str(e)}")
            return None
    
    def capture_window(self, window):
        try:
            left, top, right, bottom = window.left, window.top, window.right, window.bottom
            screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screenshot
        except Exception as e:
            self.log(f"截图失败: {str(e)}")
            return None
    
    def log(self, message):
        pass
    
    def end_round(self):
        self.current_round_log_count = 0
    
    def save_all_settings(self):
        settings = {}
        if hasattr(self, 'shop_module'):
            settings['shop'] = self.shop_module.get_settings()
        if hasattr(self, 'fishing_module'):
            settings['fishing'] = self.fishing_module.get_settings()
        
        if ConfigManager.save_settings(settings):
            messagebox.showinfo("提示", "设置已保存")
        else:
            messagebox.showerror("错误", "保存设置失败")
    
    def load_all_settings(self):
        settings = ConfigManager.load_settings()
        if settings:
            if hasattr(self, 'shop_module'):
                self.shop_module.load_settings(settings.get('shop', {}))
            if hasattr(self, 'fishing_module'):
                self.fishing_module.load_settings(settings.get('fishing', {}))
        else:
            print("未找到保存的设置或加载失败，使用默认设置")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()