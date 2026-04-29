import tkinter as tk
from tkinter import ttk, messagebox
import pygetwindow as gw
import pyautogui
# 禁用 PyAutoGUI 的 fail-safe，避免鼠标移动到角落报错
pyautogui.FAILSAFE = False
import cv2
import numpy as np
import os
import time
import keyboard
import ctypes
import os
import sys

# 检查是否以管理员权限运行
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 如果不是管理员权限，显示警告
if not is_admin():
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showwarning("权限警告", "建议以管理员权限运行此脚本，否则可能无法正常操作游戏窗口。")
    root.destroy()

class ImageRecognitionAutomation:
    def __init__(self, root):
        self.root = root
        self.root.title("异环小工具")
        self.root.geometry("800x950")  # 增加高度以显示所有内容
        
        # 设置整体颜色方案和磨砂玻璃效果
        self.root.configure(bg="#f0f0f0")  # 浅灰色背景
        
        # 实现半透明效果
        try:
            # 对于Windows系统
            from ctypes import windll, byref, sizeof, c_int
            
            # 获取窗口句柄
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            
            # 设置窗口属性为透明
            windll.shcore.SetProcessDpiAwareness(1)
            # 设置窗口为半透明
            windll.user32.SetWindowLongW(hwnd, -20, windll.user32.GetWindowLongW(hwnd, -20) | 0x80000)
            # 设置透明度（值越小越透明，范围0-255）
            windll.user32.SetLayeredWindowAttributes(hwnd, 0, 150, 0x2)
        except:
            # 非Windows系统或无法实现半透明效果时，使用替代方案
            # 尝试使用Tkinter的透明度设置
            try:
                self.root.attributes('-alpha', 0.6)
            except:
                pass
        
        # 取消标志
        self.cancelled = False
        
        # 当前轮次的日志计数
        self.current_round_log_count = 0
        self.current_round = 0
        
        # 设置热键监听
        self.setup_hotkeys()
        
        # 创建自定义样式
        style = ttk.Style()
        style.configure("Main.TFrame", background="#f0f0f0")
        style.configure("Title.TLabel", font=("SimHei", 12, "bold"), background="#f0f0f0", foreground="#333333")
        style.configure("Subtitle.TLabel", font=("SimHei", 10, "bold"), background="#f0f0f0", foreground="#555555")
        style.configure("TButton", font=("SimHei", 10, "bold"), padding=8, background="#4CAF50", foreground="black")
        style.configure("Hotkey.TLabel", font=("Arial", 10, "italic"), background="#f0f0f0", foreground="#0066cc")
        style.configure("Log.TLabel", font=("SimHei", 10), background="#f0f0f0", foreground="#333333")
        style.configure("Status.TLabel", font=("SimHei", 10), background="#f0f0f0", foreground="#0066cc")
        
        # 主框架 - 顶格显示，内容添加左边距
        main_frame = ttk.Frame(root, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)  # 增加左边距
        
        # 窗口选择 - 放在标签页外面
        ttk.Label(main_frame, text="选择目标窗口:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        window_frame = ttk.Frame(main_frame, style="Main.TFrame")
        window_frame.pack(anchor=tk.NW, pady=3)  # 具体设置缩进20像素
        self.window_var = tk.StringVar()
        self.window_combobox = ttk.Combobox(window_frame, textvariable=self.window_var, width=40)
        self.window_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Button(window_frame, text="刷新", command=self.refresh_windows).pack(side=tk.LEFT, padx=5)
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 第一个标签页：店长特供
        shop_tab = ttk.Frame(notebook, style="Main.TFrame")
        notebook.add(shop_tab, text="店长特供")
        
        # 内容框架 - 顶格显示
        content_frame = ttk.Frame(shop_tab, style="Main.TFrame")
        content_frame.pack(anchor=tk.NW)  # 顶格显示
        
        # 分辨率选择
        ttk.Label(content_frame, text="分辨率:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        self.resolution_var = tk.StringVar(value="1080")
        resolution_frame = ttk.Frame(content_frame, style="Main.TFrame")
        resolution_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        ttk.Radiobutton(resolution_frame, text="1929x1080（窗口）", value="1080", variable=self.resolution_var).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(resolution_frame, text="2560x1600（全屏）", value="2k", variable=self.resolution_var).pack(side=tk.LEFT, padx=10)
        
        # 第一步操作
        ttk.Label(content_frame, text="第一步操作: 识别 店长特供 图片，执行F键操作", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        step1_frame = ttk.Frame(content_frame, style="Main.TFrame")
        step1_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        ttk.Label(step1_frame, text="图像名:").pack(side=tk.LEFT, padx=5)
        self.image_path = tk.StringVar(value="image1.png")
        ttk.Entry(step1_frame, textvariable=self.image_path, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(step1_frame, text="F键次数:").pack(side=tk.LEFT, padx=5)
        self.action_count = tk.IntVar(value=2)
        ttk.Entry(step1_frame, textvariable=self.action_count, width=5).pack(side=tk.LEFT, padx=5)
        
        # 第二步操作
        ttk.Label(content_frame, text="第二步操作: 识别 开始营业 图片执行点击操作", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        step2_frame = ttk.Frame(content_frame, style="Main.TFrame")
        step2_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        ttk.Label(step2_frame, text="图像名:").pack(side=tk.LEFT, padx=5)
        self.image2_path = tk.StringVar(value="image2.png")
        ttk.Entry(step2_frame, textvariable=self.image2_path, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(step2_frame, text="点击次数:").pack(side=tk.LEFT, padx=5)
        self.click_count = tk.IntVar(value=2)
        ttk.Entry(step2_frame, textvariable=self.click_count, width=5).pack(side=tk.LEFT, padx=5)
        
        # 第三步操作
        ttk.Label(content_frame, text="第三步操作: 识别 锤子 图片，执行持续点击操作", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        step3_frame = ttk.Frame(content_frame, style="Main.TFrame")
        step3_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        ttk.Label(step3_frame, text="图像名:").pack(side=tk.LEFT, padx=5)
        self.image3_path = tk.StringVar(value="image3.png")
        ttk.Entry(step3_frame, textvariable=self.image3_path, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(step3_frame, text="黑屏动态时间和开始时间延迟(秒):").pack(side=tk.LEFT, padx=5)
        self.delay_time = tk.IntVar(value=4)
        ttk.Entry(step3_frame, textvariable=self.delay_time, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(step3_frame, text="持续时间(秒):").pack(side=tk.LEFT, padx=5)
        self.hold_time = tk.IntVar(value=44)
        ttk.Entry(step3_frame, textvariable=self.hold_time, width=5).pack(side=tk.LEFT, padx=5)
        
        # 第四步操作
        ttk.Label(content_frame, text="第四步操作: 识别 领取 图片，执行点击操作", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        step4_frame = ttk.Frame(content_frame, style="Main.TFrame")
        step4_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        ttk.Label(step4_frame, text="图像名:").pack(side=tk.LEFT, padx=5)
        self.image4_path = tk.StringVar(value="image4.png")
        ttk.Entry(step4_frame, textvariable=self.image4_path, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(step4_frame, text="点击次数:").pack(side=tk.LEFT, padx=5)
        self.click4_count = tk.IntVar(value=2)
        ttk.Entry(step4_frame, textvariable=self.click4_count, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(step4_frame, text="延迟(秒):").pack(side=tk.LEFT, padx=5)
        self.step4_delay = tk.IntVar(value=1)
        ttk.Entry(step4_frame, textvariable=self.step4_delay, width=5).pack(side=tk.LEFT, padx=5)
        
        # 循环设置
        ttk.Label(content_frame, text="循环设置:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        loop_frame = ttk.Frame(content_frame, style="Main.TFrame")
        loop_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        self.loop_var = tk.StringVar(value="once")
        ttk.Radiobutton(loop_frame, text="执行一次", value="once", variable=self.loop_var).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(loop_frame, text="指定次数", value="custom", variable=self.loop_var).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(loop_frame, text="一直执行", value="infinite", variable=self.loop_var).pack(side=tk.LEFT, padx=10)
        
        # 循环次数输入
        loop_count_frame = ttk.Frame(content_frame, style="Main.TFrame")
        loop_count_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        ttk.Label(loop_count_frame, text="循环次数:").pack(side=tk.LEFT, padx=5)
        self.loop_count = tk.IntVar(value=1)
        ttk.Entry(loop_count_frame, textvariable=self.loop_count, width=5).pack(side=tk.LEFT, padx=5)
        
        # 执行选项
        ttk.Label(content_frame, text="执行选项:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        self.execution_var = tk.StringVar(value="all")
        execution_frame = ttk.Frame(content_frame, style="Main.TFrame")
        execution_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        ttk.Radiobutton(execution_frame, text="单独测试第一步操作", value="step1", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(execution_frame, text="单独测试第二步操作", value="step2", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(execution_frame, text="单独测试第三步操作", value="step3", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(execution_frame, text="单独测试第四步操作", value="step4", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(execution_frame, text="执行所有步骤", value="all", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        
        # 重试功能设置
        ttk.Label(content_frame, text="重试功能:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        backup_frame = ttk.Frame(content_frame, style="Main.TFrame")
        backup_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        self.backup_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_frame, text="启动重试功能，在错误时重试当前操作", variable=self.backup_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(backup_frame, text="重试次数:").pack(side=tk.LEFT, padx=5)
        self.backup_count = tk.IntVar(value=2)
        ttk.Entry(backup_frame, textvariable=self.backup_count, width=5).pack(side=tk.LEFT, padx=5)
        
        # 按钮和提示区域
        button_frame = ttk.Frame(shop_tab, style="Main.TFrame")
        button_frame.pack(pady=5)  # 进一步减小间距
        
        # 开始按钮
        ttk.Button(button_frame, text="开始执行", command=self.start_execution).pack(side=tk.LEFT, padx=10)
        
        # F12取消热键提示 - 放在开始按钮旁边
        ttk.Label(button_frame, text="取消热键: F12", style="Hotkey.TLabel").pack(side=tk.LEFT, padx=10)
        
        # 第二个标签页：钓鱼
        fishing_tab = ttk.Frame(notebook, style="Main.TFrame")
        notebook.add(fishing_tab, text="钓鱼")
        
        # 钓鱼功能内容框架
        fishing_content_frame = ttk.Frame(fishing_tab, style="Main.TFrame")
        fishing_content_frame.pack(anchor=tk.NW, padx=20, pady=10)
        
        # 第一组HSV参数设置 - 鱼
        ttk.Label(fishing_content_frame, text="【鱼】HSV 参数设置:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)
        
        # 鱼 - 低阈值设置
        fish_low_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        fish_low_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(fish_low_frame, text="低阈值 (H, S, V):").pack(side=tk.LEFT, padx=5)
        self.fish_h_low = tk.IntVar(value=83)
        self.fish_s_low = tk.IntVar(value=195)
        self.fish_v_low = tk.IntVar(value=184)
        ttk.Entry(fish_low_frame, textvariable=self.fish_h_low, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(fish_low_frame, textvariable=self.fish_s_low, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(fish_low_frame, textvariable=self.fish_v_low, width=5).pack(side=tk.LEFT, padx=2)
        
        # 鱼 - 高阈值设置
        fish_high_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        fish_high_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(fish_high_frame, text="高阈值 (H, S, V):").pack(side=tk.LEFT, padx=5)
        self.fish_h_high = tk.IntVar(value=85)
        self.fish_s_high = tk.IntVar(value=206)
        self.fish_v_high = tk.IntVar(value=226)
        ttk.Entry(fish_high_frame, textvariable=self.fish_h_high, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(fish_high_frame, textvariable=self.fish_s_high, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(fish_high_frame, textvariable=self.fish_v_high, width=5).pack(side=tk.LEFT, padx=2)
        
        # 第二组HSV参数设置 - 鱼竿
        ttk.Label(fishing_content_frame, text="【鱼竿】HSV 参数设置:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)
        
        # 鱼竿 - 低阈值设置
        rod_low_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        rod_low_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(rod_low_frame, text="低阈值 (H, S, V):").pack(side=tk.LEFT, padx=5)
        self.rod_h_low = tk.IntVar(value=26)
        self.rod_s_low = tk.IntVar(value=73)
        self.rod_v_low = tk.IntVar(value=253)
        ttk.Entry(rod_low_frame, textvariable=self.rod_h_low, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(rod_low_frame, textvariable=self.rod_s_low, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(rod_low_frame, textvariable=self.rod_v_low, width=5).pack(side=tk.LEFT, padx=2)
        
        # 鱼竿 - 高阈值设置
        rod_high_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        rod_high_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(rod_high_frame, text="高阈值 (H, S, V):").pack(side=tk.LEFT, padx=5)
        self.rod_h_high = tk.IntVar(value=29)
        self.rod_s_high = tk.IntVar(value=110)
        self.rod_v_high = tk.IntVar(value=254)
        ttk.Entry(rod_high_frame, textvariable=self.rod_h_high, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(rod_high_frame, textvariable=self.rod_s_high, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(rod_high_frame, textvariable=self.rod_v_high, width=5).pack(side=tk.LEFT, padx=2)
        
        # 截图区域设置
        ttk.Label(fishing_content_frame, text="识别匹配设置以及测试功能按钮", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)
        
        # 变量定义
        self.key_press_time_per_5px = tk.IntVar(value=23)
        self.phase_drop_line_enabled = tk.BooleanVar(value=True)
        self.phase_fishing_enabled = tk.BooleanVar(value=True)
        self.phase_cleanup_enabled = tk.BooleanVar(value=True)
        self.auto_fishing_loop = tk.BooleanVar(value=False)
        self.auto_fishing_loop_count = tk.IntVar(value=0)
        self.phase_drop_line_delay = tk.DoubleVar(value=0)
        self.phase_drop_line_interval = tk.IntVar(value=1)
        self.phase_drop_line_timeout = tk.IntVar(value=10)
        self.phase_fishing_delay = tk.DoubleVar(value=0.25)
        self.phase_cleanup_delay = tk.DoubleVar(value=1)
        
        # 检测区域设置（从左上角开始的高度百分比）
        detect_area_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        detect_area_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(detect_area_frame, text="检测区域高度（从窗口顶部开始）:").pack(side=tk.LEFT, padx=5)
        self.detect_area_percent = tk.IntVar(value=15)
        ttk.Entry(detect_area_frame, textvariable=self.detect_area_percent, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(detect_area_frame, text="%").pack(side=tk.LEFT, padx=2)
        ttk.Button(detect_area_frame, text="测试获取当前指定窗口的HSV匹配区域参考图片", command=self.test_capture_region).pack(side=tk.LEFT, padx=10)
        
        # 测试获取鱼和鱼竿的HSV匹配图片按钮
        test_fish_rod_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        test_fish_rod_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Button(test_fish_rod_frame, text="测试获取鱼和鱼竿的HSV匹配图片", command=self.test_fish_rod_capture).pack(anchor=tk.NW)
        
        # 获取图片HSV按钮
        get_hsv_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        get_hsv_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Button(get_hsv_frame, text="点击获取指定图片的HSV", command=self.get_image_hsv).pack(anchor=tk.NW)
        
        # 钓鱼各阶段设置
        ttk.Label(fishing_content_frame, text="钓鱼各阶段设置:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)
        
        # 下杆阶段设置
        drop_line_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        drop_line_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(drop_line_frame, text="下杆阶段:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(drop_line_frame, text="是否在循环中启用", variable=self.phase_drop_line_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(drop_line_frame, text="启动延迟").pack(side=tk.LEFT, padx=5)
        ttk.Entry(drop_line_frame, textvariable=self.phase_drop_line_delay, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="执行间隔").pack(side=tk.LEFT, padx=5)
        ttk.Entry(drop_line_frame, textvariable=self.phase_drop_line_interval, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="超时").pack(side=tk.LEFT, padx=5)
        ttk.Entry(drop_line_frame, textvariable=self.phase_drop_line_timeout, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Button(drop_line_frame, text="单独执行", command=self.run_phase_drop_line).pack(side=tk.LEFT, padx=10)
        
        # 钓鱼阶段设置
        fishing_phase_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        fishing_phase_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(fishing_phase_frame, text="钓鱼阶段:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(fishing_phase_frame, text="是否在循环中启用", variable=self.phase_fishing_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(fishing_phase_frame, text="启动延迟").pack(side=tk.LEFT, padx=5)
        ttk.Entry(fishing_phase_frame, textvariable=self.phase_fishing_delay, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(fishing_phase_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Label(fishing_phase_frame, text="按键时间设置每5px增加").pack(side=tk.LEFT, padx=5)
        ttk.Entry(fishing_phase_frame, textvariable=self.key_press_time_per_5px, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(fishing_phase_frame, text="ms").pack(side=tk.LEFT, padx=2)
        ttk.Button(fishing_phase_frame, text="单独执行", command=self.run_phase_fishing).pack(side=tk.LEFT, padx=10)
        
        # 收尾阶段设置
        cleanup_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        cleanup_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(cleanup_frame, text="收尾阶段:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(cleanup_frame, text="是否在循环中启用", variable=self.phase_cleanup_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(cleanup_frame, text="启动延迟").pack(side=tk.LEFT, padx=5)
        ttk.Entry(cleanup_frame, textvariable=self.phase_cleanup_delay, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(cleanup_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Button(cleanup_frame, text="单独执行", command=self.run_phase_cleanup).pack(side=tk.LEFT, padx=10)
        
        # 自动钓鱼循环设置
        auto_loop_frame = ttk.Frame(fishing_content_frame, style="Main.TFrame")
        auto_loop_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Checkbutton(auto_loop_frame, text="自动钓鱼循环执行", variable=self.auto_fishing_loop).pack(side=tk.LEFT, padx=5)
        ttk.Label(auto_loop_frame, text="循环次数").pack(side=tk.LEFT, padx=5)
        self.auto_fishing_loop_count = tk.IntVar(value=0)
        ttk.Entry(auto_loop_frame, textvariable=self.auto_fishing_loop_count, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(auto_loop_frame, text="次（0=无限，不勾选默认执行一次）").pack(side=tk.LEFT, padx=2)
        
        # 按钮区域
        fishing_button_frame = ttk.Frame(fishing_tab, style="Main.TFrame")
        fishing_button_frame.pack(pady=10)
        ttk.Button(fishing_button_frame, text="开始执行", command=self.start_fishing_execution).pack(side=tk.LEFT, padx=10)
        ttk.Label(fishing_button_frame, text="取消热键: F12", style="Hotkey.TLabel").pack(side=tk.LEFT, padx=10)
        
        # 钓鱼标签页的日志显示区域
        ttk.Label(fishing_tab, text="执行日志:", style="Log.TLabel").pack(anchor=tk.NW, pady=5)
        fishing_log_frame = ttk.Frame(fishing_tab, style="Main.TFrame")
        fishing_log_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=True, pady=5)
        
        self.fishing_log_text = tk.Text(fishing_log_frame, height=15, width=80, wrap=tk.WORD)
        self.fishing_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        fishing_scrollbar = ttk.Scrollbar(fishing_log_frame, orient=tk.VERTICAL, command=self.fishing_log_text.yview)
        fishing_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fishing_log_text.config(yscrollcommand=fishing_scrollbar.set)
        
        # 店长特供标签页的状态标签和日志显示区域
        # 状态标签 - 移除就绪显示
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(shop_tab, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(pady=0)  # 最小间距
        
        # 日志显示区域
        ttk.Label(shop_tab, text="执行日志:", style="Log.TLabel").pack(anchor=tk.NW, pady=0)  # 最小间距
        log_frame = ttk.Frame(shop_tab, style="Main.TFrame")
        log_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=True, pady=1)  # 最小间距
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=10, width=80, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 刷新窗口列表
        self.refresh_windows()
    
    def log(self, message):
        """添加日志信息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)  # 滚动到最新日志
    
    def refresh_windows(self):
        """刷新窗口列表"""
        try:
            windows = gw.getAllTitles()
            # 过滤空标题
            windows = [window for window in windows if window]
            self.window_combobox['values'] = windows
            if windows:
                self.window_combobox.current(0)
        except Exception as e:
            messagebox.showerror("错误", f"获取窗口列表失败: {str(e)}")
    
    def find_window(self, window_title):
        """根据标题查找窗口"""
        try:
            # 尝试使用pygetwindow查找
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                return windows[0]
            
            # 如果没找到，尝试获取所有窗口并模糊匹配
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if window_title.lower() in window.title.lower():
                    return window
            
            return None
        except Exception as e:
            print(f"查找窗口失败: {str(e)}")
            return None
    
    def capture_window(self, window):
        """捕获窗口截图"""
        try:
            # 获取窗口位置和大小
            left, top, width, height = window.left, window.top, window.width, window.height
            
            # 确保坐标有效
            if left < 0:
                left = 0
            if top < 0:
                top = 0
            if width <= 0 or height <= 0:
                return None
            
            # 捕获窗口区域
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # 转换为OpenCV格式
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screenshot
        except Exception as e:
            return None
    
    def load_template(self, template_path):
        """加载模板图像"""
        try:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise Exception(f"无法加载图像: {template_path}")
            return template
        except Exception as e:
            messagebox.showerror("错误", f"加载模板失败: {str(e)}")
            return None
    
    def find_template(self, screenshot, template):
        """在截图中查找模板"""
        try:
            # 打印截图和模板信息
            print(f"截图形状: {screenshot.shape}")
            print(f"模板形状: {template.shape}")
            
            # 确保模板大小小于截图
            if template.shape[0] > screenshot.shape[0] or template.shape[1] > screenshot.shape[1]:
                print("模板大小大于截图，无法匹配")
                return False
            
            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            # 设置阈值
            threshold = 0.7  # 降低阈值以提高匹配成功率
            
            # 找到最大匹配值
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(f"最大匹配值: {max_val}")
            print(f"匹配阈值: {threshold}")
            
            # 如果找到匹配
            if max_val >= threshold:
                print(f"找到匹配，位置: {max_loc}")
                return True
            else:
                print("未找到匹配")
                return False
        except Exception as e:
            print(f"模板匹配失败: {str(e)}")
            return False
    
    def perform_action(self, count):
        """执行F键操作"""
        try:
            # 确保键盘操作在游戏中生效
            pyautogui.FAILSAFE = False
            
            # 尝试使用更底层的方法发送按键
            import keyboard
            
            for i in range(count):
                # 检查是否取消
                if self.cancelled:
                    
                    return False
                # 按下F键
                keyboard.press('f')
                time.sleep(0.1)  # 保持按下状态
                # 释放F键
                keyboard.release('f')
                time.sleep(0.5)  # 间隔0.5秒
            
            return True
        except ImportError:
            # 如果keyboard模块不可用，回退到pyautogui
            try:
                for i in range(count):
                    # 检查是否取消
                    if self.cancelled:
                        
                        return False
                    # 按下F键
                    pyautogui.keyDown('f')
                    time.sleep(0.1)  # 保持按下状态
                    # 释放F键
                    pyautogui.keyUp('f')
                    time.sleep(0.5)  # 间隔0.5秒
                return True
            except Exception as e:
                print(f"执行操作失败: {str(e)}")
                return False
        except Exception as e:
            print(f"执行操作失败: {str(e)}")
            return False
    
    def find_template_with_position(self, screenshot, template):
        """在截图中查找模板并返回位置"""
        try:
            # 打印截图和模板信息
            print(f"截图形状: {screenshot.shape}")
            print(f"模板形状: {template.shape}")
            
            # 确保模板大小小于截图
            if template.shape[0] > screenshot.shape[0] or template.shape[1] > screenshot.shape[1]:
                print("模板大小大于截图，无法匹配")
                return False, None
            
            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            # 设置阈值
            threshold = 0.7  # 降低阈值以提高匹配成功率
            
            # 找到最大匹配值
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(f"最大匹配值: {max_val}")
            print(f"匹配阈值: {threshold}")
            
            # 如果找到匹配
            if max_val >= threshold:
                # 计算模板中心位置
                center_x = max_loc[0] + template.shape[1] // 2
                center_y = max_loc[1] + template.shape[0] // 2
                print(f"找到匹配，中心位置: ({center_x}, {center_y})")
                return True, (center_x, center_y)
            else:
                print("未找到匹配")
                return False, None
        except Exception as e:
            print(f"模板匹配失败: {str(e)}")
            return False, None
    
    def perform_mouse_click(self, window, position, count):
        """执行鼠标点击操作"""
        try:
            # 激活窗口
            window.activate()
            time.sleep(0.3)  # 等待窗口激活
            
            # 获取窗口位置
            window_left, window_top = window.left, window.top
            
            # 计算实际点击位置
            click_x = window_left + position[0]
            click_y = window_top + position[1]
            
            print(f"执行鼠标点击，位置: ({click_x}, {click_y})")
            
            # 执行点击操作
            for i in range(count):
                # 检查是否取消
                if self.cancelled:
                    
                    return False
                
                # 模拟鼠标平滑移动，默认300ms，动态波动30毫秒
                import random
                duration = 0.3 + random.uniform(-0.03, 0.03)  # 300ms ± 30ms
                pyautogui.moveTo(click_x, click_y, duration=duration)
                
                # 执行点击
                pyautogui.click()
                time.sleep(0.5)  # 间隔0.5秒
            
            return True
        except Exception as e:
            print(f"执行鼠标点击失败: {str(e)}")
            return False
    
    def setup_hotkeys(self):
        """设置热键监听 - F12是全局唯一的取消判定"""
        # 绑定F12热键用于取消操作（全局唯一）
        keyboard.add_hotkey('f12', self.cancel_operation)
    
    def cancel_operation(self):
        """取消当前操作 - F12全局唯一取消判定"""
        # F12是全局唯一的取消判定，直接设置标志
        self.cancelled = True
        self.log("F12全局取消触发")
        messagebox.showinfo("操作取消", "操作已取消")
    
    def perform_hold_click(self, window, position, duration):
        """执行重复左键点击操作，持续指定时间"""
        try:
            # 激活窗口
            window.activate()
            time.sleep(0.3)  # 等待窗口激活
            
            # 检查是否取消
            if self.cancelled:
                
                return False
            
            # 获取窗口位置
            window_left, window_top = window.left, window.top
            
            # 计算实际点击位置
            click_x = window_left + position[0]
            click_y = window_top + position[1]
            
            print(f"执行重复左键点击，位置: ({click_x}, {click_y})，持续时间: {duration}秒")
            
            # 模拟鼠标平滑移动到目标位置，默认300ms，动态波动30毫秒
            import random
            move_duration = 0.3 + random.uniform(-0.03, 0.03)  # 300ms ± 30ms
            pyautogui.moveTo(click_x, click_y, duration=move_duration)
            
            # 执行重复点击操作
            start_time = time.time()
            end_time = start_time + duration
            
            while time.time() < end_time:
                # 检查是否取消
                if self.cancelled:
                    
                    return False
                
                # 执行点击
                pyautogui.click()
                time.sleep(0.1)  # 控制点击频率，避免过快
            
            return True
        except Exception as e:
            print(f"执行重复点击失败: {str(e)}")
            return False
    
    def start_execution(self):
        """开始执行识别和操作"""
        try:
            # 重置取消标志
            self.cancelled = False
            
            # 获取参数
            window_title = self.window_var.get()
            image1_name = self.image_path.get()
            image2_name = self.image2_path.get()
            image3_name = self.image3_path.get()
            image4_name = self.image4_path.get()
            resolution = self.resolution_var.get()
            action_count = self.action_count.get()
            click_count = self.click_count.get()
            delay_time = self.delay_time.get()
            hold_time = self.hold_time.get()
            click4_count = self.click4_count.get()
            execution_option = self.execution_var.get()
            loop_option = self.loop_var.get()
            loop_count = self.loop_count.get()
            
            # 验证参数
            if not window_title:
                messagebox.showerror("错误", "请选择目标窗口")
                self.log("错误: 请选择目标窗口")
                return
            
            # 验证分辨率文件夹是否存在
            if not os.path.exists(resolution):
                messagebox.showerror("错误", f"分辨率文件夹 '{resolution}' 不存在")
                self.log(f"错误: 分辨率文件夹 '{resolution}' 不存在")
                return
            
            # 验证循环次数
            if loop_option == "custom" and loop_count <= 0:
                messagebox.showerror("错误", "循环次数必须大于0")
                self.log("错误: 循环次数必须大于0")
                return
            
            # 开始执行
            self.log("开始执行操作")
            self.log(f"目标窗口: {window_title}")
            self.log(f"分辨率: {resolution}")
            self.log(f"执行选项: {execution_option}")
            self.log(f"循环模式: {loop_option}")
            if loop_option == "custom":
                self.log(f"循环次数: {loop_count}")
            
            # 查找窗口
            window = self.find_window(window_title)
            if not window:
                messagebox.showerror("错误", f"找不到窗口: {window_title}")
                self.log(f"错误: 找不到窗口: {window_title}")
                self.status_var.set("")
                return
            
            self.log(f"找到窗口: {window_title}")
            
            # 激活窗口
            window.activate()
            time.sleep(0.3)  # 等待窗口激活
            
            # 检查是否取消
            if self.cancelled:
                self.log("操作已取消")
                self.status_var.set("已取消")
                return
            
            # 执行循环
            current_loop = 0
            max_loops = loop_count if loop_option == "custom" else 1
            
            while True:
                # 检查是否取消
                if self.cancelled:
                    
                    self.log("操作已取消")
                    self.status_var.set("已取消")
                    return
                
                # 检查循环次数
                if loop_option != "infinite" and current_loop >= max_loops:
                    break
                
                current_loop += 1
                print(f"执行第 {current_loop} 轮操作")
                self.log(f"开始第 {current_loop} 轮操作")
                
                # 更新状态
                self.status_var.set(f"执行中... (第 {current_loop} 轮)")
                self.root.update()
                
                # 执行第一步：F键操作
                if execution_option in ["step1", "all"]:
                    self.log("执行第一步操作")
                    # 构建图像1路径
                    template1_path = f"{resolution}/{image1_name}"
                    
                    # 验证图像1文件是否存在
                    if not os.path.exists(template1_path):
                        messagebox.showerror("错误", f"图像文件 '{template1_path}' 不存在")
                        self.log(f"错误: 图像文件 '{template1_path}' 不存在")
                        self.status_var.set("")
                        return
                    
                    self.log(f"加载图像: {template1_path}")
                    # 加载模板1
                    template1 = self.load_template(template1_path)
                    if template1 is None:
                        self.log("错误: 无法加载模板1")
                        self.status_var.set("")
                        return
                    
                    # 保底功能
                    backup_enabled = self.backup_enabled.get()
                    backup_count = self.backup_count.get()
                    total_attempts = 1 + (backup_count if backup_enabled else 0)
                    
                    for attempt in range(total_attempts):
                        # 检查是否取消
                        if self.cancelled:
                            
                            self.log("操作已取消")
                            self.status_var.set("已取消")
                            return
                        
                        if attempt > 0:
                            self.log(f"执行第 {attempt} 次重试尝试")
                            # 重试尝试前等待，每0.1秒检查一次取消状态，确保能够立刻取消
                            retry_wait_steps = 10  # 1秒 / 0.1秒 = 10次
                            for i in range(retry_wait_steps):
                                if self.cancelled:
                                    
                                    self.log("操作已取消")
                                    self.status_var.set("已取消")
                                    return
                                time.sleep(0.1)
                        
                        # 捕获窗口截图
                        self.log("捕获窗口截图")
                        screenshot = self.capture_window(window)
                        if screenshot is None:
                            self.log("错误: 无法捕获窗口截图")
                            continue
                        
                        # 查找模板1
                        self.log("查找模板1")
                        found1 = self.find_template(screenshot, template1)
                        if found1:
                            # 再次激活窗口，确保在执行操作时窗口在前台
                            window.activate()
                            time.sleep(0.3)  # 等待窗口激活
                            
                            # 执行F键操作
                            self.log(f"识别到图像1，执行F键操作 {action_count} 次")
                            success = self.perform_action(action_count)
                            if success:
                                self.log("F键操作执行完成")
                                break
                            else:
                                self.log("执行F键操作失败")
                                continue
                        else:
                            self.log("未识别到图像1")
                            continue
                    else:
                        # 所有尝试都失败
                        messagebox.showerror("错误", "重试尝试失败: 未识别到图像1")
                        self.log("错误: 重试尝试失败 - 未识别到图像1")
                        self.status_var.set("")
                        return
                
                # 执行第二步：鼠标点击操作
                if execution_option in ["step2", "all"]:
                    self.log("执行第二步操作")
                    # 构建图像2路径
                    template2_path = f"{resolution}/{image2_name}"
                    
                    # 验证图像2文件是否存在
                    if not os.path.exists(template2_path):
                        messagebox.showerror("错误", f"图像文件 '{template2_path}' 不存在")
                        self.log(f"错误: 图像文件 '{template2_path}' 不存在")
                        self.status_var.set("")
                        return
                    
                    self.log(f"加载图像: {template2_path}")
                    # 加载模板2
                    template2 = self.load_template(template2_path)
                    if template2 is None:
                        self.log("错误: 无法加载模板2")
                        self.status_var.set("")
                        return
                    
                    # 保底功能
                    backup_enabled = self.backup_enabled.get()
                    backup_count = self.backup_count.get()
                    total_attempts = 1 + (backup_count if backup_enabled else 0)
                    
                    for attempt in range(total_attempts):
                        # 检查是否取消
                        if self.cancelled:
                            
                            self.log("操作已取消")
                            self.status_var.set("已取消")
                            return
                        
                        if attempt > 0:
                            self.log(f"执行第 {attempt} 次重试尝试")
                            # 重试尝试前等待，每0.1秒检查一次取消状态，确保能够立刻取消
                            retry_wait_steps = 10  # 1秒 / 0.1秒 = 10次
                            for i in range(retry_wait_steps):
                                if self.cancelled:
                                    
                                    self.log("操作已取消")
                                    self.status_var.set("已取消")
                                    return
                                time.sleep(0.1)
                        
                        # 捕获窗口截图
                        self.log("捕获窗口截图")
                        screenshot = self.capture_window(window)
                        if screenshot is None:
                            self.log("错误: 无法捕获窗口截图")
                            continue
                        
                        # 查找模板2并获取位置
                        self.log("查找模板2")
                        found2, position = self.find_template_with_position(screenshot, template2)
                        if found2 and position:
                            # 执行鼠标点击操作
                            self.log(f"识别到图像2，执行鼠标点击 {click_count} 次")
                            success = self.perform_mouse_click(window, position, click_count)
                            if success:
                                self.log("鼠标点击操作执行完成")
                                break
                            else:
                                self.log("执行鼠标点击操作失败")
                                continue
                        else:
                            self.log("未识别到图像2")
                            continue
                    else:
                        # 所有尝试都失败
                        messagebox.showerror("错误", "重试尝试失败: 未识别到图像2")
                        self.log("错误: 重试尝试失败 - 未识别到图像2")
                        self.status_var.set("")
                        return
                
                # 执行第三步：持续左键点击操作
                if execution_option in ["step3", "all"]:
                    self.log("执行第三步操作")
                    # 构建图像3路径
                    template3_path = f"{resolution}/{image3_name}"
                    
                    # 验证图像3文件是否存在
                    if not os.path.exists(template3_path):
                        messagebox.showerror("错误", f"图像文件 '{template3_path}' 不存在")
                        self.log(f"错误: 图像文件 '{template3_path}' 不存在")
                        self.status_var.set("")
                        return
                    
                    self.log(f"加载图像: {template3_path}")
                    # 加载模板3
                    template3 = self.load_template(template3_path)
                    if template3 is None:
                        self.log("错误: 无法加载模板3")
                        self.status_var.set("")
                        return
                    
                    # 保底功能
                    backup_enabled = self.backup_enabled.get()
                    backup_count = self.backup_count.get()
                    total_attempts = 1 + (backup_count if backup_enabled else 0)
                    
                    for attempt in range(total_attempts):
                        # 检查是否取消
                        if self.cancelled:
                            
                            self.log("操作已取消")
                            self.status_var.set("已取消")
                            return
                        
                        if attempt > 0:
                            self.log(f"执行第 {attempt} 次重试尝试")
                            # 重试尝试前等待，每0.1秒检查一次取消状态，确保能够立刻取消
                            retry_wait_steps = 10  # 1秒 / 0.1秒 = 10次
                            for i in range(retry_wait_steps):
                                if self.cancelled:
                                    
                                    self.log("操作已取消")
                                    self.status_var.set("已取消")
                                    return
                                time.sleep(0.1)
                        
                        # 执行延迟，每0.1秒检查一次取消状态，确保能够立刻取消
                        if delay_time > 0:
                            self.log(f"执行延迟 {delay_time} 秒")
                            delay_steps = delay_time * 10  # 每0.1秒检查一次
                            for i in range(delay_steps):
                                if self.cancelled:
                                    
                                    self.log("操作已取消")
                                    self.status_var.set("已取消")
                                    return
                                time.sleep(0.1)
                        
                        # 捕获窗口截图
                        self.log("捕获窗口截图")
                        screenshot = self.capture_window(window)
                        if screenshot is None:
                            self.log("错误: 无法捕获窗口截图")
                            continue
                        
                        # 查找模板3并获取位置
                        self.log("查找模板3")
                        found3, position = self.find_template_with_position(screenshot, template3)
                        if found3 and position:
                            # 执行持续左键点击操作
                            self.log(f"识别到图像3，执行持续左键点击 {hold_time} 秒")
                            success = self.perform_hold_click(window, position, hold_time)
                            if success:
                                self.log("持续左键点击操作执行完成")
                                break
                            else:
                                self.log("执行持续左键点击操作失败")
                                continue
                        else:
                            self.log("未识别到图像3")
                            continue
                    else:
                        # 所有尝试都失败
                        messagebox.showerror("错误", "重试尝试失败: 未识别到图像3")
                        self.log("错误: 重试尝试失败 - 未识别到图像3")
                        self.status_var.set("")
                        return
                
                # 执行第四步：鼠标左键点击操作
                if execution_option in ["step4", "all"]:
                    self.log("执行第四步操作")
                    # 构建图像4路径
                    template4_path = f"{resolution}/{image4_name}"
                    
                    # 验证图像4文件是否存在
                    if not os.path.exists(template4_path):
                        messagebox.showerror("错误", f"图像文件 '{template4_path}' 不存在")
                        self.log(f"错误: 图像文件 '{template4_path}' 不存在")
                        self.status_var.set("")
                        return
                    
                    self.log(f"加载图像: {template4_path}")
                    # 加载模板4
                    template4 = self.load_template(template4_path)
                    if template4 is None:
                        self.log("错误: 无法加载模板4")
                        self.status_var.set("")
                        return
                    
                    # 保底功能
                    backup_enabled = self.backup_enabled.get()
                    backup_count = self.backup_count.get()
                    total_attempts = 1 + (backup_count if backup_enabled else 0)
                    
                    for attempt in range(total_attempts):
                        # 检查是否取消
                        if self.cancelled:
                            
                            self.log("操作已取消")
                            self.status_var.set("已取消")
                            return
                        
                        if attempt > 0:
                            self.log(f"执行第 {attempt} 次重试尝试")
                            # 重试尝试前等待，每0.1秒检查一次取消状态，确保能够立刻取消
                            retry_wait_steps = 10  # 1秒 / 0.1秒 = 10次
                            for i in range(retry_wait_steps):
                                if self.cancelled:
                                    
                                    self.log("操作已取消")
                                    self.status_var.set("已取消")
                                    return
                                time.sleep(0.1)
                        
                        # 捕获窗口截图
                        self.log("捕获窗口截图")
                        screenshot = self.capture_window(window)
                        if screenshot is None:
                            self.log("错误: 无法捕获窗口截图")
                            continue
                        
                        # 查找模板4并获取位置
                        self.log("查找模板4")
                        found4, position = self.find_template_with_position(screenshot, template4)
                        if found4 and position:
                            # 执行延迟，每0.1秒检查一次取消状态，确保能够立刻取消
                            step4_delay = self.step4_delay.get()
                            if step4_delay > 0:
                                self.log(f"执行延迟 {step4_delay} 秒")
                                delay_steps = step4_delay * 10  # 每0.1秒检查一次
                                for i in range(delay_steps):
                                    if self.cancelled:
                                        
                                        self.log("操作已取消")
                                        self.status_var.set("已取消")
                                        return
                                    time.sleep(0.1)
                            # 执行鼠标点击操作
                            self.log(f"识别到图像4，执行鼠标点击 {click4_count} 次")
                            success = self.perform_mouse_click(window, position, click4_count)
                            if success:
                                self.log("鼠标点击操作执行完成")
                                break
                            else:
                                self.log("执行鼠标点击操作失败")
                                continue
                        else:
                            self.log("未识别到图像4")
                            continue
                    else:
                        # 所有尝试都失败
                        messagebox.showerror("错误", "重试尝试失败: 未识别到图像4")
                        self.log("错误: 重试尝试失败 - 未识别到图像4")
                        self.status_var.set("")
                        return
                

                
                # 如果是循环执行，添加间隔
                if loop_option != "once":
                    self.log("等待下一轮操作...")
                    time.sleep(1)  # 间隔1秒
            
            # 更新状态
            self.status_var.set("操作完成")
            self.log("操作完成")
            
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中发生错误: {str(e)}")
            self.log(f"错误: 执行过程中发生错误: {str(e)}")
            self.status_var.set("")

    def fishing_log(self, message):
        """添加钓鱼功能日志信息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.fishing_log_text.insert(tk.END, log_message)
        self.fishing_log_text.see(tk.END)  # 滚动到最新日志
        
        # 只记录日志计数，避免内存溢出
        self.current_round_log_count += 1
    
    def fishing_log_separator(self):
        """添加日志分隔符"""
        separator = "-------------------------------------------------------\n"
        self.fishing_log_text.insert(tk.END, separator)
        self.fishing_log_text.see(tk.END)
    
    def end_round(self):
        """结束当前轮次，输出本轮总结"""
        if self.current_round > 0:
            self.fishing_log_separator()
            self.fishing_log(f"第 {self.current_round} 轮完成，共 {self.current_round_log_count} 条日志")
            self.fishing_log_separator()
        
        # 重置当前轮次计数
        self.current_round_log_count = 0
    
    def detect_hsv_and_capture(self, screenshot, h_low, s_low, v_low, h_high, s_high, v_high, radius, name, detect_percent=10, generate_image=True):
        """检测HSV颜色并截取目标区域 - 只检测窗口顶部指定百分比区域
        返回: (成功与否, 截图路径, 中心坐标(x,y), 边界(min_x, min_y, max_x, max_y))
        """
        # 转换为HSV颜色空间
        hsv_image = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # 定义HSV范围
        lower_hsv = np.array([h_low, s_low, v_low])
        upper_hsv = np.array([h_high, s_high, v_high])
        
        # 创建掩码
        mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
        
        # 找到非零像素坐标
        coords = np.column_stack(np.where(mask > 0))
        
        # 只检测窗口顶部指定百分比的区域
        img_height = hsv_image.shape[0]
        top_region_threshold = int(img_height * detect_percent / 100)
        
        # 过滤出在上半部分10%区域内的坐标
        coords_in_top_region = coords[coords[:, 0] < top_region_threshold]
        
        if len(coords_in_top_region) == 0:
            return False, None, None, None
        
        # 计算所有匹配点的边界框
        y_coords = coords_in_top_region[:, 0]
        x_coords = coords_in_top_region[:, 1]
        
        min_x, max_x = int(np.min(x_coords)), int(np.max(x_coords))
        min_y, max_y = int(np.min(y_coords)), int(np.max(y_coords))
        
        # 计算中心坐标
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        if not generate_image:
            return True, None, (center_x, center_y), (min_x, min_y, max_x, max_y)
        
        # 计算截图区域（包含所有匹配点的边界框）
        img_height, img_width = screenshot.shape[:2]
        
        # 确保截图区域在图像范围内
        x1 = max(0, min_x)
        y1 = max(0, min_y)
        x2 = min(img_width, max_x + 1)
        y2 = min(img_height, max_y + 1)
        
        # 截取区域
        cropped_image = screenshot[y1:y2, x1:x2]
        
        # 保存截图
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "fishing_screenshots"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{name}_{timestamp}.png"
        
        cv2.imwrite(output_path, cropped_image)
        
        return True, output_path, (center_x, center_y), (min_x, min_y, max_x, max_y)
    
    def phase_drop_line(self, window, fish_hsv, rod_hsv, detect_percent, interval, timeout, delay):
        """下杆阶段：每隔interval秒点击F键，直到检测到HSV或超时"""
        self.fishing_log("=== 开始下杆阶段 ===")
        self.fishing_log(f"启动延迟: {delay}秒, 执行间隔: {interval}秒, 超时: {timeout}秒")
        
        if delay > 0:
            self.fishing_log(f"等待延迟 {delay} 秒...")
            time.sleep(delay)
        
        start_time = time.time()
        # 初始化last_f_click_time为start_time - interval，这样第一次就会立即点击
        last_f_click_time = start_time - interval
        
        while not self.cancelled:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                self.fishing_log("下杆等待上钩超时，终止循环")
                messagebox.showwarning("超时", "下杆等待上钩超时")
                self.cancelled = True  # 设置取消标志，终止整个循环
                return "timeout"
            
            current_time = time.time()
            if current_time - last_f_click_time >= interval:
                keyboard.press_and_release('f')
                last_f_click_time = current_time
                self.fishing_log(f"点击F键 (已等待{int(elapsed)}秒)")
            
            # 添加错误处理，避免 Windows 错误
            try:
                window.activate()
                time.sleep(0.02)
                screenshot = self.capture_window(window)
            except Exception as e:
                self.fishing_log(f"窗口操作错误: {str(e)}，继续尝试...")
                time.sleep(0.1)
                continue
            
            if screenshot is None:
                continue
            
            fish_success, _, _, _ = self.detect_hsv_and_capture(screenshot, 
                fish_hsv[0], fish_hsv[1], fish_hsv[2],
                fish_hsv[3], fish_hsv[4], fish_hsv[5],
                50, "鱼", detect_percent, False)
            
            rod_success, _, _, _ = self.detect_hsv_and_capture(screenshot, 
                rod_hsv[0], rod_hsv[1], rod_hsv[2],
                rod_hsv[3], rod_hsv[4], rod_hsv[5],
                50, "鱼竿", detect_percent, False)
            
            if fish_success and rod_success:
                self.fishing_log("检测到鱼和鱼竿，下杆完成")
                return "success"
        
        return "cancelled"
    
    def phase_fishing(self, window, fish_hsv, rod_hsv, detect_percent, key_press_time_per_5px, delay):
        """钓鱼阶段：持续匹配HSV并执行钓鱼操作，直到匹配不到HSV或超时"""
        self.fishing_log("=== 开始钓鱼阶段 ===")
        self.fishing_log(f"启动延迟: {delay}秒")
        
        if delay > 0:
            self.fishing_log(f"等待延迟 {delay}秒...")
            time.sleep(delay)
        
        start_time = time.time()
        timeout_triggered = False
        
        while not self.cancelled:
            # 检查是否超时
            elapsed_time = time.time() - start_time
            if elapsed_time > 10 and not timeout_triggered:
                timeout_triggered = True
                self.fishing_log(f"钓鱼阶段已持续{elapsed_time:.1f}秒，将触发收尾延迟")
            
            # 添加错误处理，避免 Windows 错误
            try:
                window.activate()
                time.sleep(0.02)
                screenshot = self.capture_window(window)
            except Exception as e:
                self.fishing_log(f"窗口操作错误: {str(e)}，继续尝试...")
                time.sleep(0.1)
                continue
            
            if screenshot is None:
                continue
            
            fish_success, fish_path, fish_center, fish_bounds = self.detect_hsv_and_capture(screenshot, 
                fish_hsv[0], fish_hsv[1], fish_hsv[2],
                fish_hsv[3], fish_hsv[4], fish_hsv[5],
                50, "鱼", detect_percent, False)
            
            rod_success, rod_path, rod_center, rod_bounds = self.detect_hsv_and_capture(screenshot, 
                rod_hsv[0], rod_hsv[1], rod_hsv[2],
                rod_hsv[3], rod_hsv[4], rod_hsv[5],
                50, "鱼竿", detect_percent, False)
            
            if not fish_success or not rod_success:
                if not fish_success and not rod_success:
                    self.fishing_log("鱼和鱼竿均未找到，钓鱼完成")
                elif not fish_success:
                    self.fishing_log("鱼未找到，钓鱼完成")
                else:
                    self.fishing_log("鱼竿未找到，钓鱼完成")
                return ("timeout" if timeout_triggered else "finished", timeout_triggered)
            
            if fish_center and rod_center and fish_bounds:
                fish_min_x, fish_min_y, fish_max_x, fish_max_y = fish_bounds
                rod_x = rod_center[0]
                fish_center_x = (fish_min_x + fish_max_x) // 2
                fish_width = fish_max_x - fish_min_x
                offset = rod_x - fish_center_x
                
                # 输出详细调试信息
                self.fishing_log(f"鱼:[{fish_min_x}-{fish_max_x}] (宽:{fish_width}px), 中心:{fish_center_x} | 鱼竿:{rod_x} | 偏移:{offset}")
                
                # 降低阈值：鱼宽度的1/6，最小8px
                threshold = max(8, fish_width // 6)
                
                if abs(offset) > threshold:
                    distance = abs(offset)
                    press_time = distance * 0.006  # 每1px按6ms，更快
                    press_time = max(press_time, 0.04)  # 最小0.04秒
                    press_time = min(press_time, 0.25)  # 最大0.25秒
                    
                    # 确认方向：鱼竿在鱼中心左边(offset<0)，按D向右
                    if offset < 0:
                        keyboard.press('d')
                        time.sleep(press_time)
                        keyboard.release('d')
                        self.fishing_log(f"按D向右 (鱼中心左{abs(offset)}px, 阈值:{threshold}px, 按{press_time:.3f}s)")
                    else:
                        keyboard.press('a')
                        time.sleep(press_time)
                        keyboard.release('a')
                        self.fishing_log(f"按A向左 (鱼中心右{abs(offset)}px, 阈值:{threshold}px, 按{press_time:.3f}s)")
                    
                    # 减少等待时间，更快响应
                    time.sleep(0.08)
                else:
                    # 在阈值内，不移动，稍等
                    time.sleep(0.04)
        
        return "cancelled", timeout_triggered
    
    def phase_cleanup(self, window, fish_hsv, rod_hsv, detect_percent, delay, timeout_triggered=False):
        """收尾阶段：进行一次HSV匹配，匹配不到则点击窗口中间位置，支持重试"""
        self.fishing_log("=== 开始收尾阶段 ===")
        
        # 如果是超时触发的，延迟5秒
        if timeout_triggered:
            self.fishing_log("钓鱼超时触发，延迟5秒...")
            time.sleep(5)
        
        self.fishing_log(f"启动延迟: {delay}秒")
        
        if delay > 0:
            self.fishing_log(f"等待延迟 {delay} 秒...")
            time.sleep(delay)
        
        max_retry = 3
        retry_count = 0
        
        while retry_count < max_retry and not self.cancelled:
            # 添加错误处理，避免 Windows 错误
            try:
                window.activate()
                time.sleep(0.02)
                screenshot = self.capture_window(window)
            except Exception as e:
                self.fishing_log(f"窗口操作错误: {str(e)}，继续尝试...")
                time.sleep(0.1)
                if retry_count < max_retry - 1:
                    retry_count += 1
                continue
            
            if screenshot is None:
                self.fishing_log("无法捕获窗口截图")
                if retry_count < max_retry - 1:
                    retry_count += 1
                    self.fishing_log(f"1秒后重试 ({retry_count}/{max_retry})...")
                    time.sleep(1)
                    continue
                return
            
            fish_success, _, _, _ = self.detect_hsv_and_capture(screenshot, 
                fish_hsv[0], fish_hsv[1], fish_hsv[2],
                fish_hsv[3], fish_hsv[4], fish_hsv[5],
                50, "鱼", detect_percent, False)
            
            rod_success, _, _, _ = self.detect_hsv_and_capture(screenshot, 
                rod_hsv[0], rod_hsv[1], rod_hsv[2],
                rod_hsv[3], rod_hsv[4], rod_hsv[5],
                50, "鱼竿", detect_percent, False)
            
            if not fish_success and not rod_success:
                self.fishing_log("未检测到鱼和鱼竿，点击窗口中心位置")
                pyautogui.click(window.left + window.width // 2, window.top + window.height // 2)
                return
            elif not fish_success:
                self.fishing_log("未检测到鱼，点击窗口中心位置")
                pyautogui.click(window.left + window.width // 2, window.top + window.height // 2)
                return
            elif not rod_success:
                self.fishing_log("未检测到鱼竿，点击窗口中心位置")
                pyautogui.click(window.left + window.width // 2, window.top + window.height // 2)
                return
            else:
                self.fishing_log("鱼和鱼竿仍存在")
                if retry_count < max_retry - 1:
                    retry_count += 1
                    self.fishing_log(f"1秒后重试 ({retry_count}/{max_retry})...")
                    time.sleep(1)
                else:
                    self.fishing_log(f"已重试{max_retry}次，完成收尾")
                    return
    
    def start_fishing_execution(self):
        """开始执行钓鱼功能 - 支持三阶段和自动循环"""
        try:
            self.cancelled = False
            
            window_title = self.window_var.get()
            if not window_title:
                messagebox.showerror("错误", "请选择目标窗口")
                self.fishing_log("错误: 请选择目标窗口")
                return
            
            window = self.find_window(window_title)
            if not window:
                messagebox.showerror("错误", f"找不到窗口: {window_title}")
                self.fishing_log(f"错误: 找不到窗口: {window_title}")
                return
            
            fish_hsv = [self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
                        self.fish_h_high.get(), self.fish_s_high.get(), self.fish_v_high.get()]
            rod_hsv = [self.rod_h_low.get(), self.rod_s_low.get(), self.rod_v_low.get(),
                       self.rod_h_high.get(), self.rod_s_high.get(), self.rod_v_high.get()]
            detect_percent = self.detect_area_percent.get()
            key_press_time_per_5px = self.key_press_time_per_5px.get()
            phase_drop_line_enabled = self.phase_drop_line_enabled.get()
            phase_fishing_enabled = self.phase_fishing_enabled.get()
            phase_cleanup_enabled = self.phase_cleanup_enabled.get()
            auto_loop = self.auto_fishing_loop.get()
            loop_count = self.auto_fishing_loop_count.get()
            drop_line_delay = self.phase_drop_line_delay.get()
            fishing_delay = self.phase_fishing_delay.get()
            cleanup_delay = self.phase_cleanup_delay.get()
            
            self.fishing_log("开始执行钓鱼功能")
            self.fishing_log(f"目标窗口: {window_title}")
            self.fishing_log(f"【鱼】HSV: {fish_hsv[:3]} - {fish_hsv[3:]}")
            self.fishing_log(f"【鱼竿】HSV: {rod_hsv[:3]} - {rod_hsv[3:]}")
            self.fishing_log(f"检测区域高度: {detect_percent}%")
            
            if auto_loop:
                self.fishing_log(f"自动钓鱼循环: {'无限' if loop_count == 0 else str(loop_count) + '次'}")
            else:
                self.fishing_log("单次执行模式")
            
            total_loops = 0
            while not self.cancelled:
                if auto_loop and loop_count > 0 and total_loops >= loop_count:
                    self.fishing_log(f"达到循环次数 {loop_count}，停止")
                    break
                
                total_loops += 1
                self.current_round = total_loops
                self.current_round_log_count = 0
                self.fishing_log_separator()
                self.fishing_log(f"=== 第 {total_loops} 轮 ===")
                
                if phase_drop_line_enabled:
                    drop_interval = self.phase_drop_line_interval.get()
                    drop_timeout = self.phase_drop_line_timeout.get()
                    result = self.phase_drop_line(window, fish_hsv, rod_hsv, detect_percent, drop_interval, drop_timeout, drop_line_delay)
                    if result == "cancelled":
                        self.end_round()
                        break
                
                if self.cancelled:
                    self.end_round()
                    break
                
                if phase_fishing_enabled:
                    result, timeout_triggered = self.phase_fishing(window, fish_hsv, rod_hsv, detect_percent, key_press_time_per_5px, fishing_delay)
                    if result == "cancelled":
                        self.end_round()
                        break
                
                if self.cancelled:
                    self.end_round()
                    break
                
                if phase_cleanup_enabled:
                    self.phase_cleanup(window, fish_hsv, rod_hsv, detect_percent, cleanup_delay, timeout_triggered)
                
                # 结束当前轮次
                self.end_round()
                
                if not auto_loop:
                    break
            
            if self.cancelled:
                self.fishing_log("操作已取消")
            else:
                self.fishing_log(f"钓鱼结束，共执行 {total_loops} 轮")
            
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中发生错误: {str(e)}")
            self.fishing_log(f"错误: 执行过程中发生错误: {str(e)}")
    
    def run_phase_drop_line(self):
        """单独执行下杆阶段"""
        try:
            self.cancelled = False
            self.current_round = 1
            self.current_round_log_count = 0
            
            window_title = self.window_var.get()
            if not window_title:
                messagebox.showerror("错误", "请选择目标窗口")
                return
            window = self.find_window(window_title)
            if not window:
                messagebox.showerror("错误", f"找不到窗口: {window_title}")
                return
            
            fish_hsv = [self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
                        self.fish_h_high.get(), self.fish_s_high.get(), self.fish_v_high.get()]
            rod_hsv = [self.rod_h_low.get(), self.rod_s_low.get(), self.rod_v_low.get(),
                       self.rod_h_high.get(), self.rod_s_high.get(), self.rod_v_high.get()]
            detect_percent = self.detect_area_percent.get()
            drop_interval = self.phase_drop_line_interval.get()
            drop_timeout = self.phase_drop_line_timeout.get()
            delay = self.phase_drop_line_delay.get()
            
            self.fishing_log_separator()
            self.fishing_log("=== 单独执行下杆阶段 ===")
            self.phase_drop_line(window, fish_hsv, rod_hsv, detect_percent, drop_interval, drop_timeout, delay)
            self.end_round()
        except Exception as e:
            messagebox.showerror("错误", str(e))
    
    def run_phase_fishing(self):
        """单独执行钓鱼阶段"""
        try:
            self.cancelled = False
            self.current_round = 1
            self.current_round_log_count = 0
            
            window_title = self.window_var.get()
            if not window_title:
                messagebox.showerror("错误", "请选择目标窗口")
                return
            window = self.find_window(window_title)
            if not window:
                messagebox.showerror("错误", f"找不到窗口: {window_title}")
                return
            
            fish_hsv = [self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
                        self.fish_h_high.get(), self.fish_s_high.get(), self.fish_v_high.get()]
            rod_hsv = [self.rod_h_low.get(), self.rod_s_low.get(), self.rod_v_low.get(),
                       self.rod_h_high.get(), self.rod_s_high.get(), self.rod_v_high.get()]
            detect_percent = self.detect_area_percent.get()
            key_press_time_per_5px = self.key_press_time_per_5px.get()
            delay = self.phase_fishing_delay.get()
            
            self.fishing_log_separator()
            self.fishing_log("=== 单独执行钓鱼阶段 ===")
            self.phase_fishing(window, fish_hsv, rod_hsv, detect_percent, key_press_time_per_5px, delay)
            self.end_round()
        except Exception as e:
            messagebox.showerror("错误", str(e))
    
    def run_phase_cleanup(self):
        """单独执行收尾阶段"""
        try:
            self.cancelled = False
            self.current_round = 1
            self.current_round_log_count = 0
            
            window_title = self.window_var.get()
            if not window_title:
                messagebox.showerror("错误", "请选择目标窗口")
                return
            window = self.find_window(window_title)
            if not window:
                messagebox.showerror("错误", f"找不到窗口: {window_title}")
                return
            
            fish_hsv = [self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
                        self.fish_h_high.get(), self.fish_s_high.get(), self.fish_v_high.get()]
            rod_hsv = [self.rod_h_low.get(), self.rod_s_low.get(), self.rod_v_low.get(),
                       self.rod_h_high.get(), self.rod_s_high.get(), self.rod_v_high.get()]
            detect_percent = self.detect_area_percent.get()
            delay = self.phase_cleanup_delay.get()
            
            self.fishing_log_separator()
            self.fishing_log("=== 单独执行收尾阶段 ===")
            self.phase_cleanup(window, fish_hsv, rod_hsv, detect_percent, delay)
            self.end_round()
        except Exception as e:
            messagebox.showerror("错误", str(e))
    
    def test_capture_region(self):
        """测试获取截图区域 - 捕获指定百分比区域的截图"""
        try:
            self.current_round = 1
            self.current_round_log_count = 0
            
            # 保存当前取消状态，测试函数不受F12影响
            saved_cancelled = self.cancelled
            self.cancelled = False
            
            window_title = self.window_var.get()
            
            if not window_title:
                messagebox.showerror("错误", "请选择目标窗口")
                self.fishing_log("错误: 请选择目标窗口")
                self.cancelled = saved_cancelled
                return
            
            self.fishing_log_separator()
            self.fishing_log("=== 测试获取截图区域 ===")
            self.fishing_log(f"目标窗口: {window_title}")
            
            # 查找窗口
            window = self.find_window(window_title)
            if not window:
                messagebox.showerror("错误", f"找不到窗口: {window_title}")
                self.fishing_log(f"错误: 找不到窗口: {window_title}")
                self.cancelled = saved_cancelled
                return
            
            self.fishing_log(f"找到窗口: {window_title}")
            
            # 激活窗口
            window.activate()
            time.sleep(0.3)
            
            # 捕获窗口截图
            self.fishing_log("捕获窗口截图")
            screenshot = self.capture_window(window)
            if screenshot is None:
                messagebox.showerror("错误", "无法捕获窗口截图")
                self.fishing_log("错误: 无法捕获窗口截图")
                self.cancelled = saved_cancelled
                return
            
            # 获取检测区域百分比
            detect_percent = self.detect_area_percent.get()
            
            # 计算检测区域（从左上角开始，取窗口高度的指定百分比）
            img_height, img_width = screenshot.shape[:2]
            detect_height = int(img_height * detect_percent / 100)
            start_x, start_y = 0, 0
            end_x, end_y = img_width, detect_height
            
            # 截取检测区域
            detect_region = screenshot[start_y:end_y, start_x:end_x]
            
            # 保存检测区域截图
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "fishing_screenshots"
            os.makedirs(output_dir, exist_ok=True)
            detect_screenshot_path = f"{output_dir}/detect_area_{timestamp}.png"
            cv2.imwrite(detect_screenshot_path, detect_region)
            self.fishing_log(f"检测区域截图已保存: {detect_screenshot_path}")
            self.fishing_log(f"区域尺寸: {img_width}x{detect_height}px (窗口高度的{detect_percent}%)")
            
            messagebox.showinfo("成功", f"截图区域已保存!\n路径: {detect_screenshot_path}\n尺寸: {img_width}x{detect_height}px")
            
            self.end_round()
            
        except Exception as e:
            messagebox.showerror("错误", f"测试获取截图区域时发生错误: {str(e)}")
            self.fishing_log(f"错误: 测试获取截图区域时发生错误: {str(e)}")
    
    def test_fish_rod_capture(self):
        """测试获取鱼和鱼竿的HSV匹配图片"""
        try:
            self.current_round = 1
            self.current_round_log_count = 0
            
            # 保存当前取消状态，测试函数不受F12影响
            saved_cancelled = self.cancelled
            self.cancelled = False
            
            window_title = self.window_var.get()
            
            if not window_title:
                messagebox.showerror("错误", "请选择目标窗口")
                self.fishing_log("错误: 请选择目标窗口")
                self.cancelled = saved_cancelled
                return
            
            self.fishing_log_separator()
            self.fishing_log("=== 测试获取鱼和鱼竿的HSV匹配图片 ===")
            self.fishing_log(f"目标窗口: {window_title}")
            
            # 查找窗口
            window = self.find_window(window_title)
            if not window:
                messagebox.showerror("错误", f"找不到窗口: {window_title}")
                self.fishing_log(f"错误: 找不到窗口: {window_title}")
                self.cancelled = saved_cancelled
                return
            
            self.fishing_log(f"找到窗口: {window_title}")
            
            # 激活窗口
            window.activate()
            time.sleep(0.3)
            
            # 捕获窗口截图
            self.fishing_log("捕获窗口截图")
            screenshot = self.capture_window(window)
            if screenshot is None:
                messagebox.showerror("错误", "无法捕获窗口截图")
                self.fishing_log("错误: 无法捕获窗口截图")
                self.cancelled = saved_cancelled
                return
            
            # 获取参数
            detect_percent = self.detect_area_percent.get()
            radius = 50
            
            # 获取鱼的HSV参数
            fish_h_low = self.fish_h_low.get()
            fish_s_low = self.fish_s_low.get()
            fish_v_low = self.fish_v_low.get()
            fish_h_high = self.fish_h_high.get()
            fish_s_high = self.fish_s_high.get()
            fish_v_high = self.fish_v_high.get()
            
            # 获取鱼竿的HSV参数
            rod_h_low = self.rod_h_low.get()
            rod_s_low = self.rod_s_low.get()
            rod_v_low = self.rod_v_low.get()
            rod_h_high = self.rod_h_high.get()
            rod_s_high = self.rod_s_high.get()
            rod_v_high = self.rod_v_high.get()
            
            self.fishing_log(f"检测区域高度: {detect_percent}%")
            self.fishing_log(f"【鱼】HSV范围: ({fish_h_low}, {fish_s_low}, {fish_v_low}) - ({fish_h_high}, {fish_s_high}, {fish_v_high})")
            self.fishing_log(f"【鱼竿】HSV范围: ({rod_h_low}, {rod_s_low}, {rod_v_low}) - ({rod_h_high}, {rod_s_high}, {rod_v_high})")
            
            # 检测并捕获鱼的图片
            self.fishing_log("开始检测【鱼】的HSV颜色")
            fish_success, fish_path, fish_center, fish_bounds = self.detect_hsv_and_capture(screenshot, 
                fish_h_low, fish_s_low, fish_v_low, 
                fish_h_high, fish_s_high, fish_v_high, 
                radius, "鱼", detect_percent, True)
            
            # 检测并捕获鱼竿的图片
            self.fishing_log("开始检测【鱼竿】的HSV颜色")
            rod_success, rod_path, rod_center, rod_bounds = self.detect_hsv_and_capture(screenshot, 
                rod_h_low, rod_s_low, rod_v_low, 
                rod_h_high, rod_s_high, rod_v_high, 
                radius, "鱼竿", detect_percent, True)
            
            # 显示结果
            if fish_success and rod_success:
                self.fishing_log("两组HSV颜色检测完成!")
                messagebox.showinfo("成功", f"两组HSV颜色检测完成!\n【鱼】截图已保存: {fish_path}\n【鱼竿】截图已保存: {rod_path}")
            elif fish_success:
                messagebox.showinfo("部分成功", f"【鱼】检测成功，截图已保存: {fish_path}\n【鱼竿】未找到匹配区域")
            elif rod_success:
                messagebox.showinfo("部分成功", f"【鱼竿】检测成功，截图已保存: {rod_path}\n【鱼】未找到匹配区域")
            else:
                messagebox.showinfo("结果", "两组HSV颜色均未找到匹配区域")
            
            self.end_round()
            self.cancelled = saved_cancelled
            
        except Exception as e:
            self.cancelled = saved_cancelled
            messagebox.showerror("错误", f"测试获取鱼和鱼竿的HSV匹配图片时发生错误: {str(e)}")
            self.fishing_log(f"错误: 测试获取鱼和鱼竿的HSV匹配图片时发生错误: {str(e)}")
    
    def get_image_hsv(self):
        """获取图片的HSV值并显示在日志上"""
        try:
            from tkinter import filedialog
            
            self.current_round = 1
            self.current_round_log_count = 0
            
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择图片",
                filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("所有文件", "*.*")]
            )
            
            if not file_path:
                self.fishing_log("用户取消选择图片")
                return
            
            self.fishing_log_separator()
            self.fishing_log("=== 获取图片HSV ===")
            self.fishing_log(f"选择的图片: {file_path}")
            
            # 读取图片
            image = cv2.imread(file_path)
            if image is None:
                messagebox.showerror("错误", "无法读取图片，请检查文件路径是否正确")
                self.fishing_log("错误: 无法读取图片")
                return
            
            # 获取图片尺寸
            height, width = image.shape[:2]
            self.fishing_log(f"图片尺寸: {width}x{height}")
            
            # 转换为HSV颜色空间
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 计算HSV各通道的统计信息
            h_channel = hsv_image[:, :, 0]
            s_channel = hsv_image[:, :, 1]
            v_channel = hsv_image[:, :, 2]
            
            h_mean = np.mean(h_channel)
            s_mean = np.mean(s_channel)
            v_mean = np.mean(v_channel)
            
            h_min, h_max = np.min(h_channel), np.max(h_channel)
            s_min, s_max = np.min(s_channel), np.max(s_channel)
            v_min, v_max = np.min(v_channel), np.max(v_channel)
            
            self.fishing_log("=" * 50)
            self.fishing_log("HSV 统计信息:")
            self.fishing_log(f"  H (色相): 均值={h_mean:.1f}, 范围=[{h_min}, {h_max}]")
            self.fishing_log(f"  S (饱和度): 均值={s_mean:.1f}, 范围=[{s_min}, {s_max}]")
            self.fishing_log(f"  V (明度): 均值={v_mean:.1f}, 范围=[{v_min}, {v_max}]")
            self.fishing_log("=" * 50)
            
            # 计算推荐的低阈值和高阈值（使用均值附近的标准差范围）
            h_std = np.std(h_channel)
            s_std = np.std(s_channel)
            v_std = np.std(v_channel)
            
            recommended_low_h = max(0, int(h_mean - h_std))
            recommended_high_h = min(179, int(h_mean + h_std))
            recommended_low_s = max(0, int(s_mean - s_std))
            recommended_high_s = min(255, int(s_mean + s_std))
            recommended_low_v = max(0, int(v_mean - v_std))
            recommended_high_v = min(255, int(v_mean + v_std))
            
            self.fishing_log("推荐的低阈值: ({}, {}, {})".format(
                recommended_low_h, recommended_low_s, recommended_low_v))
            self.fishing_log("推荐的高阈值: ({}, {}, {})".format(
                recommended_high_h, recommended_high_s, recommended_high_v))
            self.fishing_log("=" * 50)
            
            messagebox.showinfo("HSV 获取成功", 
                f"图片: {file_path}\n\n"
                f"推荐阈值设置:\n"
                f"低阈值: ({recommended_low_h}, {recommended_low_s}, {recommended_low_v})\n"
                f"高阈值: ({recommended_high_h}, {recommended_high_s}, {recommended_high_v})")
            
            self.end_round()
            
        except Exception as e:
            messagebox.showerror("错误", f"获取HSV时发生错误: {str(e)}")
            self.fishing_log(f"错误: 获取HSV时发生错误: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRecognitionAutomation(root)
    root.mainloop()