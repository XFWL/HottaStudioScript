import tkinter as tk
from tkinter import ttk, messagebox
import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
import os
import time
import keyboard
import ctypes
import sys

pyautogui.FAILSAFE = False

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
        
        self.refresh_windows()
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        from shop_module import ShopModule
        from fishing_module import FishingModule
        
        self.shop_module = ShopModule(self, self.notebook)
        self.fishing_module = FishingModule(self, self.notebook)
    
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

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()