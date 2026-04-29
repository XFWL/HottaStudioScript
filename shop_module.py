import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import os
import time
import pyautogui
import threading

class ShopModule:
    def __init__(self, main_app, notebook):
        self.main_app = main_app
        self.shop_log_text = None
        self.create_ui(notebook)
    
    def create_ui(self, notebook):
        self.shop_tab = ttk.Frame(notebook)
        notebook.add(self.shop_tab, text="店长特供")
        
        content_frame = ttk.Frame(self.shop_tab)
        content_frame.pack(anchor=tk.NW)
        
        ttk.Label(content_frame, text="分辨率:", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        self.resolution_var = tk.StringVar(value="1080")
        resolution_frame = ttk.Frame(content_frame)
        resolution_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Radiobutton(resolution_frame, text="1929x1080（窗口）", value="1080", variable=self.resolution_var).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(resolution_frame, text="2560x1600（全屏）", value="2k", variable=self.resolution_var).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(content_frame, text="第一步操作: 识别 店长特供 图片，执行F键操作", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        step1_frame = ttk.Frame(content_frame)
        step1_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(step1_frame, text="图像名:").pack(side=tk.LEFT, padx=5)
        self.image_path = tk.StringVar(value="image1.png")
        ttk.Entry(step1_frame, textvariable=self.image_path, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(step1_frame, text="F键次数:").pack(side=tk.LEFT, padx=5)
        self.action_count = tk.IntVar(value=2)
        ttk.Entry(step1_frame, textvariable=self.action_count, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(content_frame, text="第二步操作: 识别 开始营业 图片执行点击操作", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        step2_frame = ttk.Frame(content_frame)
        step2_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(step2_frame, text="图像名:").pack(side=tk.LEFT, padx=5)
        self.image2_path = tk.StringVar(value="image2.png")
        ttk.Entry(step2_frame, textvariable=self.image2_path, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(step2_frame, text="点击次数:").pack(side=tk.LEFT, padx=5)
        self.click_count = tk.IntVar(value=2)
        ttk.Entry(step2_frame, textvariable=self.click_count, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(content_frame, text="第三步操作: 识别 锤子 图片，执行持续点击操作", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        step3_frame = ttk.Frame(content_frame)
        step3_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(step3_frame, text="图像名:").pack(side=tk.LEFT, padx=5)
        self.image3_path = tk.StringVar(value="image3.png")
        ttk.Entry(step3_frame, textvariable=self.image3_path, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(step3_frame, text="黑屏动态时间和开始时间延迟(秒):").pack(side=tk.LEFT, padx=5)
        self.delay_time = tk.IntVar(value=4)
        ttk.Entry(step3_frame, textvariable=self.delay_time, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(step3_frame, text="持续时间(秒):").pack(side=tk.LEFT, padx=5)
        self.hold_time = tk.IntVar(value=44)
        ttk.Entry(step3_frame, textvariable=self.hold_time, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(content_frame, text="第四步操作: 识别 领取 图片，执行点击操作", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        step4_frame = ttk.Frame(content_frame)
        step4_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(step4_frame, text="图像名:").pack(side=tk.LEFT, padx=5)
        self.image4_path = tk.StringVar(value="image4.png")
        ttk.Entry(step4_frame, textvariable=self.image4_path, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(step4_frame, text="点击次数:").pack(side=tk.LEFT, padx=5)
        self.click4_count = tk.IntVar(value=2)
        ttk.Entry(step4_frame, textvariable=self.click4_count, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(step4_frame, text="延迟(秒):").pack(side=tk.LEFT, padx=5)
        self.step4_delay = tk.IntVar(value=1)
        ttk.Entry(step4_frame, textvariable=self.step4_delay, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(content_frame, text="循环设置:", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        loop_frame = ttk.Frame(content_frame)
        loop_frame.pack(anchor=tk.NW, pady=3, padx=20)
        self.loop_var = tk.StringVar(value="once")
        ttk.Radiobutton(loop_frame, text="执行一次", value="once", variable=self.loop_var).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(loop_frame, text="指定次数", value="custom", variable=self.loop_var).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(loop_frame, text="一直执行", value="infinite", variable=self.loop_var).pack(side=tk.LEFT, padx=10)
        
        loop_count_frame = ttk.Frame(content_frame)
        loop_count_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(loop_count_frame, text="循环次数:").pack(side=tk.LEFT, padx=5)
        self.loop_count = tk.IntVar(value=1)
        ttk.Entry(loop_count_frame, textvariable=self.loop_count, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(content_frame, text="执行选项:", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        self.execution_var = tk.StringVar(value="all")
        execution_frame = ttk.Frame(content_frame)
        execution_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Radiobutton(execution_frame, text="单独测试第一步操作", value="step1", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(execution_frame, text="单独测试第二步操作", value="step2", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(execution_frame, text="单独测试第三步操作", value="step3", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(execution_frame, text="单独测试第四步操作", value="step4", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(execution_frame, text="执行所有步骤", value="all", variable=self.execution_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(content_frame, text="重试功能:", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        backup_frame = ttk.Frame(content_frame)
        backup_frame.pack(anchor=tk.NW, pady=3, padx=20)
        self.backup_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_frame, text="启动重试功能，在错误时重试当前操作", variable=self.backup_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(backup_frame, text="重试次数:").pack(side=tk.LEFT, padx=5)
        self.backup_count = tk.IntVar(value=2)
        ttk.Entry(backup_frame, textvariable=self.backup_count, width=5).pack(side=tk.LEFT, padx=5)
        
        button_frame = ttk.Frame(self.shop_tab)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="开始执行", command=self.start_execution).pack(side=tk.LEFT, padx=10)
        ttk.Label(button_frame, text="取消热键: F12", font=("Arial", 10, "italic"), foreground="#0066cc").pack(side=tk.LEFT, padx=10)
        
        log_frame = ttk.Frame(self.shop_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(log_frame, text="日志输出:", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)
        
        self.shop_log_text = tk.Text(log_frame, height=8, width=80, font=("SimHei", 9))
        self.shop_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        self.shop_log_text.config(state=tk.DISABLED)
    
    def shop_log(self, message):
        if self.shop_log_text:
            self.shop_log_text.config(state=tk.NORMAL)
            timestamp = time.strftime("%H:%M:%S")
            self.shop_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.shop_log_text.see(tk.END)
            self.shop_log_text.config(state=tk.DISABLED)
    
    def smooth_move_click(self, x, y, duration=0.5):
        pyautogui.moveTo(x, y, duration=duration)
        pyautogui.click(x, y)
    
    def start_execution(self):
        self.main_app.cancelled = False
        
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        execution_type = self.execution_var.get()
        
        thread = threading.Thread(target=self.execute_operations, args=(window, execution_type))
        thread.start()
    
    def execute_operations(self, window, execution_type):
        window.activate()
        time.sleep(0.5)
        
        if execution_type == "step1":
            self.step1(window)
        elif execution_type == "step2":
            self.step2(window)
        elif execution_type == "step3":
            self.step3(window)
        elif execution_type == "step4":
            self.step4(window)
        elif execution_type == "all":
            loop_mode = self.loop_var.get()
            if loop_mode == "once":
                self.execute_all_steps(window)
            elif loop_mode == "custom":
                count = self.loop_count.get()
                for i in range(count):
                    if self.main_app.cancelled:
                        break
                    self.shop_log(f"=== 第 {i+1}/{count} 轮 ===")
                    self.execute_all_steps(window)
            elif loop_mode == "infinite":
                count = 1
                while not self.main_app.cancelled:
                    self.shop_log(f"=== 第 {count} 轮 ===")
                    self.execute_all_steps(window)
                    count += 1
    
    def execute_all_steps(self, window):
        if self.main_app.cancelled:
            return
        
        self.step1(window)
        if self.main_app.cancelled:
            return
        
        self.step2(window)
        if self.main_app.cancelled:
            return
        
        self.step3(window)
        if self.main_app.cancelled:
            return
        
        self.step4(window)
    
    def find_image_on_screen(self, window, image_path, threshold=0.8):
        screenshot = self.main_app.capture_window(window)
        if screenshot is None:
            return None
        
        resolution = self.resolution_var.get()
        if resolution == "1080":
            folder = "1080"
        else:
            folder = "2k"
        
        template_path = os.path.join("images", folder, image_path)
        if not os.path.exists(template_path):
            self.shop_log(f"模板图片不存在: {template_path}")
            return None
        
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            self.shop_log(f"无法读取模板图片: {template_path}")
            return None
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        
        return None
    
    def step1(self, window):
        self.shop_log("=== 开始第一步操作 ===")
        
        image_path = self.image_path.get()
        action_count = self.action_count.get()
        
        pos = self.find_image_on_screen(window, image_path)
        if pos:
            self.shop_log(f"找到目标图片: {image_path}")
            for i in range(action_count):
                if self.main_app.cancelled:
                    break
                pyautogui.press('f')
                time.sleep(0.5)
                self.shop_log(f"执行F键操作 {i+1}/{action_count}")
        else:
            self.shop_log(f"未找到目标图片: {image_path}")
            if self.backup_enabled.get():
                self.shop_log("重试功能已启用，尝试重试")
                for i in range(self.backup_count.get()):
                    if self.main_app.cancelled:
                        break
                    time.sleep(2)
                    pos = self.find_image_on_screen(window, image_path)
                    if pos:
                        for j in range(action_count):
                            if self.main_app.cancelled:
                                break
                            pyautogui.press('f')
                            time.sleep(0.5)
                            self.shop_log(f"重试执行F键操作 {j+1}/{action_count}")
                        return
            self.main_app.cancelled = True
            self.shop_log("取消后续操作")
            messagebox.showerror("错误", f"第一步操作失败：未找到目标图片 {image_path}")
    
    def step2(self, window):
        self.shop_log("=== 开始第二步操作 ===")
        
        image_path = self.image2_path.get()
        click_count = self.click_count.get()
        
        pos = self.find_image_on_screen(window, image_path)
        if pos:
            self.shop_log(f"找到目标图片: {image_path}")
            window_left, window_top = window.left, window.top
            for i in range(click_count):
                if self.main_app.cancelled:
                    break
                self.smooth_move_click(window_left + pos[0], window_top + pos[1])
                time.sleep(0.5)
                self.shop_log(f"执行点击操作 {i+1}/{click_count}")
        else:
            self.shop_log(f"未找到目标图片: {image_path}")
            if self.backup_enabled.get():
                self.shop_log("重试功能已启用，尝试重试")
                for i in range(self.backup_count.get()):
                    if self.main_app.cancelled:
                        break
                    time.sleep(2)
                    pos = self.find_image_on_screen(window, image_path)
                    if pos:
                        window_left, window_top = window.left, window.top
                        for j in range(click_count):
                            if self.main_app.cancelled:
                                break
                            self.smooth_move_click(window_left + pos[0], window_top + pos[1])
                            time.sleep(0.5)
                            self.shop_log(f"重试执行点击操作 {j+1}/{click_count}")
                        return
            self.main_app.cancelled = True
            self.shop_log("取消后续操作")
            messagebox.showerror("错误", f"第二步操作失败：未找到目标图片 {image_path}")
    
    def step3(self, window):
        self.shop_log("=== 开始第三步操作 ===")
        
        image_path = self.image3_path.get()
        delay_time = self.delay_time.get()
        hold_time = self.hold_time.get()
        
        pos = self.find_image_on_screen(window, image_path)
        if pos:
            self.shop_log(f"找到目标图片: {image_path}")
            window_left, window_top = window.left, window.top
            time.sleep(delay_time)
            
            end_time = time.time() + hold_time
            while time.time() < end_time and not self.main_app.cancelled:
                self.smooth_move_click(window_left + pos[0], window_top + pos[1], duration=0.2)
                time.sleep(0.1)
            
            self.shop_log(f"持续点击操作完成，时长: {hold_time}秒")
        else:
            self.shop_log(f"未找到目标图片: {image_path}")
            if self.backup_enabled.get():
                self.shop_log("重试功能已启用，尝试重试")
                for i in range(self.backup_count.get()):
                    if self.main_app.cancelled:
                        break
                    time.sleep(2)
                    pos = self.find_image_on_screen(window, image_path)
                    if pos:
                        window_left, window_top = window.left, window.top
                        time.sleep(delay_time)
                        
                        end_time = time.time() + hold_time
                        while time.time() < end_time and not self.main_app.cancelled:
                            self.smooth_move_click(window_left + pos[0], window_top + pos[1], duration=0.2)
                            time.sleep(0.1)
                        
                        self.shop_log(f"重试持续点击操作完成，时长: {hold_time}秒")
                        return
            self.main_app.cancelled = True
            self.shop_log("取消后续操作")
            messagebox.showerror("错误", f"第三步操作失败：未找到目标图片 {image_path}")
    
    def step4(self, window):
        self.shop_log("=== 开始第四步操作 ===")
        
        image_path = self.image4_path.get()
        click_count = self.click4_count.get()
        delay = self.step4_delay.get()
        
        pos = self.find_image_on_screen(window, image_path)
        if pos:
            self.shop_log(f"找到目标图片: {image_path}")
            window_left, window_top = window.left, window.top
            for i in range(click_count):
                if self.main_app.cancelled:
                    break
                self.smooth_move_click(window_left + pos[0], window_top + pos[1])
                time.sleep(delay)
                self.shop_log(f"执行点击操作 {i+1}/{click_count}")
        else:
            self.shop_log(f"未找到目标图片: {image_path}")
            if self.backup_enabled.get():
                self.shop_log("重试功能已启用，尝试重试")
                for i in range(self.backup_count.get()):
                    if self.main_app.cancelled:
                        break
                    time.sleep(2)
                    pos = self.find_image_on_screen(window, image_path)
                    if pos:
                        window_left, window_top = window.left, window.top
                        for j in range(click_count):
                            if self.main_app.cancelled:
                                break
                            self.smooth_move_click(window_left + pos[0], window_top + pos[1])
                            time.sleep(delay)
                            self.shop_log(f"重试执行点击操作 {j+1}/{click_count}")
                        return
            self.main_app.cancelled = True
            self.shop_log("取消后续操作")
            messagebox.showerror("错误", f"第四步操作失败：未找到目标图片 {image_path}")