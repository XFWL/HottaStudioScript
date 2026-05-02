import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import os
import sys
import time
import keyboard
import pyautogui
import threading

def get_resource_path(relative_path):
    """获取资源文件的绝对路径 - 支持开发环境和打包后"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FishingModule:
    def __init__(self, main_app, notebook):
        self.main_app = main_app
        self.fishing_log_text = None
        self.create_ui(notebook)
    
    def create_ui(self, notebook):
        self.fishing_tab = ttk.Frame(notebook)
        notebook.add(self.fishing_tab, text="钓鱼")

        fishing_content_frame = ttk.Frame(self.fishing_tab)
        fishing_content_frame.pack(anchor=tk.NW, padx=20, pady=10)

        ttk.Label(fishing_content_frame, text="【鱼】HSV 参数设置:", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)

        fish_low_frame = ttk.Frame(fishing_content_frame)
        fish_low_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(fish_low_frame, text="低阈值 (H, S, V):").pack(side=tk.LEFT, padx=5)
        self.fish_h_low = tk.IntVar(value=83)
        self.fish_s_low = tk.IntVar(value=195)
        self.fish_v_low = tk.IntVar(value=184)
        ttk.Entry(fish_low_frame, textvariable=self.fish_h_low, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(fish_low_frame, textvariable=self.fish_s_low, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(fish_low_frame, textvariable=self.fish_v_low, width=5).pack(side=tk.LEFT, padx=2)

        fish_high_frame = ttk.Frame(fishing_content_frame)
        fish_high_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(fish_high_frame, text="高阈值 (H, S, V):").pack(side=tk.LEFT, padx=5)
        self.fish_h_high = tk.IntVar(value=85)
        self.fish_s_high = tk.IntVar(value=206)
        self.fish_v_high = tk.IntVar(value=226)
        ttk.Entry(fish_high_frame, textvariable=self.fish_h_high, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(fish_high_frame, textvariable=self.fish_s_high, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(fish_high_frame, textvariable=self.fish_v_high, width=5).pack(side=tk.LEFT, padx=2)

        ttk.Label(fishing_content_frame, text="【鱼竿】HSV 参数设置:", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)

        rod_low_frame = ttk.Frame(fishing_content_frame)
        rod_low_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(rod_low_frame, text="低阈值 (H, S, V):").pack(side=tk.LEFT, padx=5)
        self.rod_h_low = tk.IntVar(value=26)
        self.rod_s_low = tk.IntVar(value=73)
        self.rod_v_low = tk.IntVar(value=253)
        ttk.Entry(rod_low_frame, textvariable=self.rod_h_low, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(rod_low_frame, textvariable=self.rod_s_low, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(rod_low_frame, textvariable=self.rod_v_low, width=5).pack(side=tk.LEFT, padx=2)

        rod_high_frame = ttk.Frame(fishing_content_frame)
        rod_high_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(rod_high_frame, text="高阈值 (H, S, V):").pack(side=tk.LEFT, padx=5)
        self.rod_h_high = tk.IntVar(value=29)
        self.rod_s_high = tk.IntVar(value=110)
        self.rod_v_high = tk.IntVar(value=254)
        ttk.Entry(rod_high_frame, textvariable=self.rod_h_high, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(rod_high_frame, textvariable=self.rod_s_high, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Entry(rod_high_frame, textvariable=self.rod_v_high, width=5).pack(side=tk.LEFT, padx=2)

        ttk.Label(fishing_content_frame, text="钓鱼阶段设置", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)

        self.key_press_time_per_px = tk.IntVar(value=4)
        self.phase_drop_line_enabled = tk.BooleanVar(value=True)
        self.phase_fishing_enabled = tk.BooleanVar(value=True)
        self.phase_cleanup_enabled = tk.BooleanVar(value=True)
        self.auto_fishing_loop = tk.BooleanVar(value=False)
        self.auto_fishing_loop_count = tk.IntVar(value=0)
        self.phase_drop_line_delay = tk.DoubleVar(value=0)
        self.phase_drop_line_interval = tk.IntVar(value=0.75)
        self.phase_drop_line_timeout = tk.IntVar(value=10)
        self.phase_fishing_delay = tk.DoubleVar(value=0.25)
        self.phase_cleanup_delay = tk.DoubleVar(value=1)
        self.buy_bait_enabled = tk.BooleanVar(value=False)

        self.sell_catch_enabled = tk.BooleanVar(value=False)

        drop_line_frame = ttk.Frame(fishing_content_frame)
        drop_line_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(drop_line_frame, text="下杆阶段:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(drop_line_frame, text="是否在循环中启用", variable=self.phase_drop_line_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(drop_line_frame, text="启动延迟").pack(side=tk.LEFT, padx=5)
        ttk.Entry(drop_line_frame, textvariable=self.phase_drop_line_delay, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="检测间隔").pack(side=tk.LEFT, padx=5)
        ttk.Entry(drop_line_frame, textvariable=self.phase_drop_line_interval, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="超时时间").pack(side=tk.LEFT, padx=5)
        ttk.Entry(drop_line_frame, textvariable=self.phase_drop_line_timeout, width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(drop_line_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Button(drop_line_frame, text="单独执行", command=self.execute_drop_line_alone).pack(side=tk.LEFT, padx=10)

        fishing_phase_frame = ttk.Frame(fishing_content_frame)
        fishing_phase_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(fishing_phase_frame, text="钓鱼阶段:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(fishing_phase_frame, text="是否在循环中启用", variable=self.phase_fishing_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(fishing_phase_frame, text="启动延迟").pack(side=tk.LEFT, padx=5)
        ttk.Entry(fishing_phase_frame, textvariable=self.phase_fishing_delay, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(fishing_phase_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Label(fishing_phase_frame, text="按键时间设置每1px增加").pack(side=tk.LEFT, padx=5)
        ttk.Entry(fishing_phase_frame, textvariable=self.key_press_time_per_px, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(fishing_phase_frame, text="ms").pack(side=tk.LEFT, padx=2)
        ttk.Button(fishing_phase_frame, text="单独执行", command=self.execute_fishing_alone).pack(side=tk.LEFT, padx=10)

        timeout_info_frame = ttk.Frame(fishing_content_frame)
        timeout_info_frame.pack(anchor=tk.NW, pady=3, padx=(85, 38))
        ttk.Label(timeout_info_frame, text="超时设置(循环时):", foreground="#888888").pack(side=tk.LEFT, padx=5)
        ttk.Label(timeout_info_frame, text="超时时间", foreground="#888888").pack(side=tk.LEFT, padx=5)
        ttk.Label(timeout_info_frame, text="11", width=4, foreground="#888888", font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        ttk.Label(timeout_info_frame, text="秒", foreground="#888888").pack(side=tk.LEFT, padx=2)
        ttk.Label(timeout_info_frame, text="超时后收尾阶段设置启动延迟为", foreground="#888888").pack(side=tk.LEFT, padx=5)
        ttk.Label(timeout_info_frame, text="5", width=4, foreground="#888888", font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        ttk.Label(timeout_info_frame, text="秒", foreground="#888888").pack(side=tk.LEFT, padx=2)

        cleanup_frame = ttk.Frame(fishing_content_frame)
        cleanup_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(cleanup_frame, text="收尾阶段:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(cleanup_frame, text="是否在循环中启用", variable=self.phase_cleanup_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(cleanup_frame, text="启动延迟").pack(side=tk.LEFT, padx=5)
        ttk.Entry(cleanup_frame, textvariable=self.phase_cleanup_delay, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(cleanup_frame, text="秒").pack(side=tk.LEFT, padx=2)
        ttk.Button(cleanup_frame, text="单独执行", command=self.execute_cleanup_alone).pack(side=tk.LEFT, padx=10)

        # 出售渔获
        sell_catch_frame = ttk.Frame(fishing_content_frame)
        sell_catch_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(sell_catch_frame, text="出售渔获:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(sell_catch_frame, text="是否在循环中启用", variable=self.sell_catch_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(sell_catch_frame, text="触发条件: 钓鱼").pack(side=tk.LEFT, padx=5)
        self.sell_catch_interval = tk.IntVar(value=99)
        ttk.Entry(sell_catch_frame, textvariable=self.sell_catch_interval, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(sell_catch_frame, text="次 后出售一次渔获").pack(side=tk.LEFT, padx=2)
        ttk.Button(sell_catch_frame, text="单独执行", command=self.execute_sell_catch_alone).pack(side=tk.LEFT, padx=10)

        # 补充鱼饵
        buy_bait_frame = ttk.Frame(fishing_content_frame)
        buy_bait_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(buy_bait_frame, text="补充鱼饵:").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(buy_bait_frame, text="是否在循环中启用", variable=self.buy_bait_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Label(buy_bait_frame, text="触发条件: 钓鱼").pack(side=tk.LEFT, padx=5)
        self.buy_bait_interval = tk.IntVar(value=99)
        ttk.Entry(buy_bait_frame, textvariable=self.buy_bait_interval, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(buy_bait_frame, text="次 后购买一次99个鱼饵").pack(side=tk.LEFT, padx=2)
        self.buy_bait_test_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(buy_bait_frame, text="测试（只购买1个鱼饵）", variable=self.buy_bait_test_mode).pack(side=tk.LEFT, padx=10)
        ttk.Button(buy_bait_frame, text="单独执行", command=self.execute_buy_bait_alone).pack(side=tk.LEFT, padx=10)

        auto_loop_frame = ttk.Frame(fishing_content_frame)
        auto_loop_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Checkbutton(auto_loop_frame, text="自动循环钓鱼", variable=self.auto_fishing_loop).pack(side=tk.LEFT, padx=5)
        ttk.Entry(auto_loop_frame, textvariable=self.auto_fishing_loop_count, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(auto_loop_frame, text="循环次数(0为无限，不勾选默认循环1遍)").pack(side=tk.LEFT, padx=5)

        ttk.Label(fishing_content_frame, text="其他设置", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)

        detect_area_frame = ttk.Frame(fishing_content_frame)
        detect_area_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Label(detect_area_frame, text="检测区域高度（从窗口顶部开始）:").pack(side=tk.LEFT, padx=5)
        self.detect_area_percent = tk.IntVar(value=15)
        ttk.Entry(detect_area_frame, textvariable=self.detect_area_percent, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(detect_area_frame, text="%").pack(side=tk.LEFT, padx=2)
        ttk.Button(detect_area_frame, text="测试获取当前指定窗口的HSV匹配区域参考图片", command=self.test_capture_region).pack(side=tk.LEFT, padx=10)

        test_fish_rod_frame = ttk.Frame(fishing_content_frame)
        test_fish_rod_frame.pack(anchor=tk.NW, pady=3, padx=20)
        ttk.Button(test_fish_rod_frame, text="测试获取鱼和鱼竿的HSV匹配图片", command=self.test_fish_rod_capture).pack(anchor=tk.NW)
        ttk.Button(test_fish_rod_frame, text="获取指定图片的HSV", command=self.get_image_hsv).pack(anchor=tk.NW, pady=2)

        button_frame = ttk.Frame(self.fishing_tab)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="开始执行钓鱼", command=self.start_fishing).pack(side=tk.LEFT, padx=10)
        ttk.Label(button_frame, text="取消热键: F12", font=("Arial", 10, "italic"), foreground="#0066cc").pack(side=tk.LEFT, padx=10)

        log_frame = ttk.Frame(self.fishing_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        ttk.Label(log_frame, text="日志输出:", font=("SimHei", 10, "bold"), background="#f0f0f0").pack(anchor=tk.NW, pady=3)

        self.fishing_log_text = tk.Text(log_frame, height=8, width=80, font=("SimHei", 9))
        self.fishing_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        self.fishing_log_text.config(state=tk.DISABLED)
    
    def fishing_log(self, message):
        if self.fishing_log_text:
            self.fishing_log_text.config(state=tk.NORMAL)
            timestamp = time.strftime("%H:%M:%S")
            self.fishing_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.fishing_log_text.see(tk.END)
            self.fishing_log_text.config(state=tk.DISABLED)
    
    def detect_hsv_and_capture(self, screenshot, h_low, s_low, v_low, h_high, s_high, v_high, radius, name, detect_percent=10, generate_image=True):
        hsv_image = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        lower_hsv = np.array([h_low, s_low, v_low])
        upper_hsv = np.array([h_high, s_high, v_high])
        
        mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
        
        coords = np.column_stack(np.where(mask > 0))
        
        img_height = hsv_image.shape[0]
        top_region_threshold = int(img_height * detect_percent / 100)
        
        coords_in_top_region = coords[coords[:, 0] < top_region_threshold]
        
        if len(coords_in_top_region) == 0:
            return False, None, None, None
        
        y_coords = coords_in_top_region[:, 0]
        x_coords = coords_in_top_region[:, 1]
        
        min_x, max_x = int(np.min(x_coords)), int(np.max(x_coords))
        min_y, max_y = int(np.min(y_coords)), int(np.max(y_coords))
        
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        if not generate_image:
            return True, None, (center_x, center_y), (min_x, min_y, max_x, max_y)
        
        img_height, img_width = screenshot.shape[:2]
        
        x1 = max(0, min_x)
        y1 = max(0, min_y)
        x2 = min(img_width, max_x + 1)
        y2 = min(img_height, max_y + 1)
        
        cropped_image = screenshot[y1:y2, x1:x2]
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = "images/fishing_screenshots"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{name}_{timestamp}.png"
        
        cv2.imwrite(output_path, cropped_image)
        
        return True, output_path, (center_x, center_y), (min_x, min_y, max_x, max_y)
    
    def phase_drop_line(self, window, fish_hsv, detect_percent, delay, interval, timeout):
        self.fishing_log("=== 开始下杆阶段 ===")
        
        if delay > 0:
            self.fishing_log(f"等待延迟 {delay}秒...")
            time.sleep(delay)
        
        start_time = time.time()
        last_log_time = start_time - 1
        
        while not self.main_app.cancelled:
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > timeout:
                self.fishing_log(f"下杆阶段超时({timeout}秒)，退出")
                return "timeout"
            
            if current_time - last_log_time >= 1:
                self.fishing_log(f"下杆阶段进行中，已等待 {int(elapsed_time)}秒")
                last_log_time = current_time
            
            window.activate()
            time.sleep(0.02)
            
            screenshot = self.main_app.capture_window(window)
            if screenshot is None:
                time.sleep(interval)
                continue
            
            success, _, _, _ = self.detect_hsv_and_capture(screenshot, fish_hsv[0], fish_hsv[1], fish_hsv[2], fish_hsv[3], fish_hsv[4], fish_hsv[5], 50, "fish", detect_percent, False)
            
            if success:
                self.fishing_log("检测到鱼，下杆成功")
                return "success"
            
            pyautogui.press('f')
            time.sleep(interval)
        
        return "cancelled"
    
    def phase_fishing(self, window, fish_hsv, rod_hsv, detect_percent, key_press_time_per_px, delay):
        self.fishing_log("=== 开始钓鱼阶段 ===")
        self.fishing_log(f"启动延迟: {delay}秒")
        
        if delay > 0:
            self.fishing_log(f"等待延迟 {delay}秒...")
            time.sleep(delay)
        
        start_time = time.time()
        timeout_triggered = False
        current_key = None
        last_log_time = start_time
        first_detection = True
        
        while not self.main_app.cancelled:
            elapsed_time = time.time() - start_time
            if elapsed_time > 10 and not timeout_triggered:
                timeout_triggered = True
                self.fishing_log(f"钓鱼阶段已持续{elapsed_time:.1f}秒，将触发收尾延迟")
            
            try:
                window.activate()
                time.sleep(0.02)
                screenshot = self.main_app.capture_window(window)
                
                if screenshot is None:
                    time.sleep(0.02)
                    continue
                
                fish_success, fish_path, fish_center, fish_bounds = self.detect_hsv_and_capture(
                    screenshot, fish_hsv[0], fish_hsv[1], fish_hsv[2],
                    fish_hsv[3], fish_hsv[4], fish_hsv[5],
                    50, "fish", detect_percent, False)
                
                rod_success, rod_path, rod_center, rod_bounds = self.detect_hsv_and_capture(
                    screenshot, rod_hsv[0], rod_hsv[1], rod_hsv[2],
                    rod_hsv[3], rod_hsv[4], rod_hsv[5],
                    50, "rod", detect_percent, False)
                
                if not fish_success or not rod_success:
                    if current_key:
                        keyboard.release(current_key)
                        current_key = None
                    if not fish_success and not rod_success:
                        self.fishing_log("鱼和鱼竿均未找到")
                    elif not fish_success:
                        self.fishing_log("鱼未找到")
                    else:
                        self.fishing_log("鱼竿未找到")
                    
                    if first_detection:
                        self.fishing_log("钓鱼阶段失败：首次检测未找到目标")
                        return (None, timeout_triggered)
                    else:
                        self.fishing_log("钓鱼阶段结束")
                        return ("finished", timeout_triggered)
                
                first_detection = False
                
                if fish_center and rod_center and fish_bounds:
                    fish_min_x, fish_min_y, fish_max_x, fish_max_y = fish_bounds
                    rod_x = rod_center[0]
                    fish_center_x = (fish_min_x + fish_max_x) // 2
                    fish_width = fish_max_x - fish_min_x
                    offset = rod_x - fish_center_x
                    
                    threshold = max(8, fish_width // 6)
                    
                    action = ""
                    position_status = ""
                    
                    if abs(offset) <= threshold:
                        if current_key:
                            keyboard.release(current_key)
                            action = f"释放{current_key.upper()}键"
                            current_key = None
                        else:
                            action = "无操作"
                        position_status = f"位置已到达，偏移:{offset}px"
                        time.sleep(0.04)
                    else:
                        if offset < 0:
                            target_key = 'd'
                        else:
                            target_key = 'a'
                        
                        if current_key != target_key:
                            if current_key:
                                keyboard.release(current_key)
                                action = f"释放{current_key.upper()}键 → 切换方向 → 按住{target_key.upper()}键"
                            else:
                                action = f"按住{target_key.upper()}键"
                            keyboard.press(target_key)
                            current_key = target_key
                        else:
                            action = f"保持按住{target_key.upper()}键"
                        position_status = f"位置偏移:{offset}px"
                        time.sleep(0.04)
                    
                    if time.time() - last_log_time >= 1:
                        self.fishing_log(f"【鱼中心:{fish_center_x}】|【鱼竿中心:{rod_x}】|【{action}】|【{position_status}】")
                        last_log_time = time.time()
                        
            except Exception as e:
                if current_key:
                    keyboard.release(current_key)
                    current_key = None
                self.fishing_log(f"钓鱼阶段错误: {str(e)}")
                self.fishing_log("钓鱼阶段异常，终止操作")
                return (None, timeout_triggered)
        
        if current_key:
            keyboard.release(current_key)
            current_key = None
        return ("cancelled", timeout_triggered)
    
    def phase_cleanup(self, window, fish_hsv, detect_percent, delay, timeout_triggered=False):
        self.fishing_log("=== 开始收尾阶段 ===")
        
        if timeout_triggered:
            self.fishing_log("钓鱼超时，延迟5秒执行收尾")
            time.sleep(5)
        elif delay > 0:
            self.fishing_log(f"启动延迟 {delay} 秒")
            time.sleep(delay)
        
        max_retry = 3
        retry_count = 0
        
        while retry_count < max_retry and not self.main_app.cancelled:
            try:
                window.activate()
                time.sleep(0.02)
                screenshot = self.main_app.capture_window(window)
                
                if screenshot is None:
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                success, _, fish_center, _ = self.detect_hsv_and_capture(screenshot, fish_hsv[0], fish_hsv[1], fish_hsv[2], fish_hsv[3], fish_hsv[4], fish_hsv[5], 50, "fish", detect_percent, False)
                
                if fish_center:
                    self.fishing_log(f"检测到鱼，重试 {retry_count + 1}/{max_retry}")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                self.fishing_log("未检测到鱼，点击窗口中心")
                window_left, window_top = window.left, window.top
                window_width, window_height = window.width, window.height
                pyautogui.click(window_left + window_width // 2, window_top + window_height // 2)
                time.sleep(0.5)
                return "success"
                
            except Exception as e:
                self.fishing_log(f"收尾阶段错误: {str(e)}")
                retry_count += 1
                time.sleep(1)
        
        self.fishing_log(f"收尾阶段失败，重试次数已达上限({max_retry}次)")
        return "failed"
    
    def start_fishing(self):
        self.main_app.cancelled = False
        
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        thread = threading.Thread(target=self.execute_fishing_cycle, args=(window,))
        thread.start()
    
    def execute_fishing_cycle(self, window):
        fish_hsv = [
            self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
            self.fish_h_high.get(), self.fish_s_high.get(), self.fish_v_high.get()
        ]
        
        rod_hsv = [
            self.rod_h_low.get(), self.rod_s_low.get(), self.rod_v_low.get(),
            self.rod_h_high.get(), self.rod_s_high.get(), self.rod_v_high.get()
        ]
        
        detect_percent = self.detect_area_percent.get()
        
        is_auto_loop = self.auto_fishing_loop.get()
        loop_count = self.auto_fishing_loop_count.get()
        
        buy_bait_enabled = self.buy_bait_enabled.get()
        buy_bait_interval = self.buy_bait_interval.get()
        
        sell_catch_enabled = self.sell_catch_enabled.get()
        sell_catch_interval = self.sell_catch_interval.get()
        
        if is_auto_loop:
            if loop_count == 0:
                loop_count = float('inf')
        else:
            loop_count = 1
        
        current_loop = 0
        fishing_count_since_buy = 0
        fishing_count_since_sell = 0
        
        while not self.main_app.cancelled:
            if current_loop > 0:
                self.fishing_log("------------------------------------------------------")
            current_loop += 1
            self.fishing_log(f"=== 钓鱼循环 第 {current_loop} 轮 ===")
            
            timeout_triggered = False
            
            # 下杆阶段
            if self.phase_drop_line_enabled.get():
                result = self.phase_drop_line(
                    window, fish_hsv, detect_percent,
                    self.phase_drop_line_delay.get(),
                    self.phase_drop_line_interval.get(),
                    self.phase_drop_line_timeout.get()
                )
                if result == "timeout":
                    self.fishing_log("下杆阶段超时，终止操作")
                    self.main_app.root.after(0, lambda: messagebox.showerror("错误", "下杆阶段超时"))
                    break
                elif result != "success":
                    self.fishing_log("下杆阶段失败，终止操作")
                    self.main_app.root.after(0, lambda: messagebox.showerror("错误", "下杆阶段失败：未找到目标"))
                    break
            
            # 钓鱼阶段
            if self.phase_fishing_enabled.get():
                result, timeout_triggered = self.phase_fishing(
                    window, fish_hsv, rod_hsv, detect_percent,
                    self.key_press_time_per_px.get(),
                    self.phase_fishing_delay.get()
                )
                if result == "cancelled":
                    self.fishing_log("钓鱼阶段被取消")
                    break
                elif result is None:
                    self.fishing_log("钓鱼阶段失败，终止操作")
                    self.main_app.root.after(0, lambda: messagebox.showerror("错误", "钓鱼阶段失败"))
                    break
            
            # 收尾阶段
            if self.phase_cleanup_enabled.get():
                result = self.phase_cleanup(
                    window, fish_hsv, detect_percent,
                    self.phase_cleanup_delay.get(),
                    timeout_triggered
                )
            
            # 出售渔获
            fishing_count_since_sell += 1
            if sell_catch_enabled and fishing_count_since_sell >= sell_catch_interval:
                self.fishing_log(f"已完成 {fishing_count_since_sell} 次钓鱼，开始出售渔获")
                if self.sell_catch(window):
                    self.fishing_log("出售渔获完成，重置计数")
                    fishing_count_since_sell = 0
                else:
                    self.fishing_log("出售渔获失败，终止操作")
                    self.main_app.root.after(0, lambda: messagebox.showerror("错误", "出售渔获失败"))
                    fishing_count_since_sell = 0
                    break
            
            # 补充鱼饵
            fishing_count_since_buy += 1
            if buy_bait_enabled and fishing_count_since_buy >= buy_bait_interval:
                self.fishing_log(f"已完成 {fishing_count_since_buy} 次钓鱼，开始补充鱼饵")
                if self.buy_bait(window):
                    self.fishing_log("补充鱼饵完成，重置计数")
                    fishing_count_since_buy = 0
                else:
                    self.fishing_log("补充鱼饵失败，终止操作")
                    self.main_app.root.after(0, lambda: messagebox.showerror("错误", "补充鱼饵失败"))
                    fishing_count_since_buy = 0
                    break
            
            if loop_count != float('inf') and current_loop >= loop_count:
                break
        
        self.fishing_log("钓鱼执行结束")
        
        # 如果是F12取消导致的结束，弹出提示
        if self.main_app.cancelled:
            messagebox.showinfo("操作取消", "钓鱼操作已取消")
    
    def execute_buy_bait_alone(self):
        self.main_app.cancelled = False
        
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        def thread_func():
            result = self.buy_bait(window)
            if not result:
                self.main_app.root.after(0, lambda: messagebox.showerror("错误", "补充鱼饵失败"))
        
        thread = threading.Thread(target=thread_func)
        thread.start()
    
    def execute_drop_line_alone(self):
        self.main_app.cancelled = False
        
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        def thread_func():
            fish_hsv = [
                self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
                self.fish_h_high.get(), self.fish_h_high.get(), self.fish_v_high.get()
            ]
            
            result = self.phase_drop_line(
                window, fish_hsv, self.detect_area_percent.get(),
                self.phase_drop_line_delay.get(),
                self.phase_drop_line_interval.get(),
                self.phase_drop_line_timeout.get()
            )
            
            self.fishing_log("------------------------------------------------------")
            
            if result == "timeout":
                self.main_app.root.after(0, lambda: messagebox.showerror("错误", "下杆阶段超时"))
            elif result != "success":
                self.main_app.root.after(0, lambda: messagebox.showerror("错误", "下杆阶段失败：未找到目标"))
        
        thread = threading.Thread(target=thread_func)
        thread.start()
    
    def execute_fishing_alone(self):
        self.main_app.cancelled = False
        
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        fish_hsv = [
            self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
            self.fish_h_high.get(), self.fish_s_high.get(), self.fish_v_high.get()
        ]
        
        rod_hsv = [
            self.rod_h_low.get(), self.rod_s_low.get(), self.rod_v_low.get(),
            self.rod_h_high.get(), self.rod_h_high.get(), self.rod_v_high.get()
        ]
        
        def thread_func():
            result, timeout_triggered = self.phase_fishing(
                window, fish_hsv, rod_hsv, self.detect_area_percent.get(),
                self.key_press_time_per_px.get(),
                self.phase_fishing_delay.get()
            )
            
            self.fishing_log("------------------------------------------------------")
            
            if result == "cancelled":
                pass
            elif result is None:
                self.main_app.root.after(0, lambda: messagebox.showerror("错误", "钓鱼阶段失败"))
        
        thread = threading.Thread(target=thread_func)
        thread.start()
    
    def execute_cleanup_alone(self):
        self.main_app.cancelled = False
        
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        def thread_func():
            fish_hsv = [
                self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
                self.fish_h_high.get(), self.fish_h_high.get(), self.fish_v_high.get()
            ]
            
            self.phase_cleanup(
                window, fish_hsv, self.detect_area_percent.get(),
                self.phase_cleanup_delay.get()
            )
            
            self.fishing_log("------------------------------------------------------")
        
        thread = threading.Thread(target=thread_func)
        thread.start()
    
    def test_capture_region(self):
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        window.activate()
        time.sleep(0.3)
        
        screenshot = self.main_app.capture_window(window)
        if screenshot is None:
            messagebox.showerror("错误", "无法捕获窗口截图")
            return
        
        detect_percent = self.detect_area_percent.get()
        img_height = screenshot.shape[0]
        top_region_height = int(img_height * detect_percent / 100)
        
        cropped_region = screenshot[:top_region_height, :]
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = "images/fishing_screenshots"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/match_region_{timestamp}.png"
        
        cv2.imwrite(output_path, cropped_region)
        
        messagebox.showinfo("成功", f"检测区域截图已保存: {output_path}")
        self.fishing_log(f"检测区域截图已保存: {output_path}")
    
    def get_image_hsv(self):
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        
        if not file_path:
            return

        # 使用 numpy 读取支持中文路径
        image = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            messagebox.showerror("错误", "无法读取图片文件")
            return
        
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        h_min = int(np.min(hsv_image[:, :, 0]))
        h_max = int(np.max(hsv_image[:, :, 0]))
        s_min = int(np.min(hsv_image[:, :, 1]))
        s_max = int(np.max(hsv_image[:, :, 1]))
        v_min = int(np.min(hsv_image[:, :, 2]))
        v_max = int(np.max(hsv_image[:, :, 2]))
        
        result = f"HSV范围:\nH: {h_min} - {h_max}\nS: {s_min} - {s_max}\nV: {v_min} - {v_max}"
        messagebox.showinfo("HSV分析结果", result)
        self.fishing_log(f"图片HSV分析完成: {file_path}\n{result}")
    
    def test_fish_rod_capture(self):
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        window.activate()
        time.sleep(0.3)
        
        screenshot = self.main_app.capture_window(window)
        if screenshot is None:
            messagebox.showerror("错误", "无法捕获窗口截图")
            return
        
        detect_percent = self.detect_area_percent.get()
        
        fish_hsv_low = (self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get())
        fish_hsv_high = (self.fish_h_high.get(), self.fish_s_high.get(), self.fish_v_high.get())
        
        rod_hsv_low = (self.rod_h_low.get(), self.rod_s_low.get(), self.rod_v_low.get())
        rod_hsv_high = (self.rod_h_high.get(), self.rod_s_high.get(), self.rod_v_high.get())
        
        success_fish, fish_path, fish_center, fish_bounds = self.detect_hsv_and_capture(screenshot, fish_hsv_low[0], fish_hsv_low[1], fish_hsv_low[2], fish_hsv_high[0], fish_hsv_high[1], fish_hsv_high[2], 50, "fish", detect_percent)
        success_rod, rod_path, rod_center, rod_bounds = self.detect_hsv_and_capture(screenshot, rod_hsv_low[0], rod_hsv_low[1], rod_hsv_low[2], rod_hsv_high[0], rod_hsv_high[1], rod_hsv_high[2], 50, "rod", detect_percent)
        
        if success_fish:
            self.fishing_log(f"【fish】匹配成功，截图已保存: {fish_path}")
        else:
            self.fishing_log("【fish】未找到匹配区域")
        
        if success_rod:
            self.fishing_log(f"【rod】匹配成功，截图已保存: {rod_path}")
        else:
            self.fishing_log("【rod】未找到匹配区域")
        
        if success_fish and success_rod:
            messagebox.showinfo("成功", f"两组HSV颜色检测完成!\n【fish】截图已保存: {fish_path}\n【rod】截图已保存: {rod_path}")
        elif success_fish:
            messagebox.showinfo("部分成功", f"【fish】检测成功，截图已保存: {fish_path}\n【rod】未找到匹配区域")
        elif success_rod:
            messagebox.showinfo("部分成功", f"【rod】检测成功，截图已保存: {rod_path}\n【fish】未找到匹配区域")
        else:
            messagebox.showinfo("结果", "两组HSV颜色均未找到匹配区域")
    
    def find_fishing_template(self, screenshot, template_name, threshold=0.8):
        template_path = get_resource_path(os.path.join("images", "fishing_templates", template_name))
        if not os.path.exists(template_path):
            self.fishing_log(f"模板图片不存在: {template_path}")
            return None
        
        # 使用 numpy 读取支持中文路径
        template = cv2.imdecode(np.fromfile(template_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if template is None:
            self.fishing_log(f"无法读取模板图片: {template_path}")
            self.fishing_log(f"文件是否存在: {os.path.exists(template_path)}")
            self.fishing_log(f"文件大小: {os.path.getsize(template_path) if os.path.exists(template_path) else 'N/A'}")
            return None
        
        # 获取当前窗口分辨率
        current_width, current_height = screenshot.shape[1], screenshot.shape[0]
        
        # 定义基准分辨率（模板图片的原始分辨率）
        base_width, base_height = 1920, 1080
        
        # 计算缩放比例
        scale_x = current_width / base_width
        scale_y = current_height / base_height
        
        # 缩放模板（按比例缩放）
        if scale_x != 1.0 or scale_y != 1.0:
            original_h, original_w = template.shape[:2]
            new_w = int(original_w * scale_x)
            new_h = int(original_h * scale_y)
            if new_w > 0 and new_h > 0:
                template = cv2.resize(template, (new_w, new_h), interpolation=cv2.INTER_AREA)
                self.fishing_log(f"模板 {template_name} 已缩放: {scale_x:.2f}x{scale_y:.2f}")
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        
        return None
    
    def buy_bait(self, window):
        saved_pos1 = None
        try:
            if self.main_app.cancelled:
                return False
            
            self.fishing_log("=== 开始补充鱼饵 ===")
            
            window.activate()
            
            # 1. 单击R键
            pyautogui.press('r')
            self.fishing_log("按下R键")
            time.sleep(1)
            
            if self.main_app.cancelled:
                return False
            
            # 2. 识别image2-1-1.png并点击（最多重试4次）
            pos1 = None
            retry_count = 0
            while retry_count < 4 and not self.main_app.cancelled:
                screenshot = self.main_app.capture_window(window)
                if screenshot is None:
                    self.fishing_log("无法获取窗口截图")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                pos1 = self.find_fishing_template(screenshot, "image2-1-1.png")
                if pos1:
                    self.fishing_log(f"找到image2-1-1.png，点击位置: {pos1}")
                    window_left, window_top = window.left, window.top
                    pyautogui.moveTo(window_left + pos1[0], window_top + pos1[1], duration=0.3)
                    pyautogui.click(window_left + pos1[0], window_top + pos1[1])
                    break
                else:
                    self.fishing_log(f"未找到image2-1-1.png，结束补充鱼饵 (第{retry_count + 1}/4次)")
                    retry_count += 1
                    time.sleep(1)
            
            if pos1 is None:
                self.fishing_log("未找到image2-1-1.png，达到重试上限")
                return False
            
            time.sleep(1)
            
            if self.main_app.cancelled:
                return False
            
            # 3. 识别image2-1-2.png并保存坐标（最多重试4次）
            pos2 = None
            retry_count = 0
            while retry_count < 4 and not self.main_app.cancelled:
                screenshot = self.main_app.capture_window(window)
                if screenshot is None:
                    self.fishing_log("无法获取窗口截图")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                pos2 = self.find_fishing_template(screenshot, "image2-1-2.png")
                if pos2:
                    # 保存坐标时向上移动100px
                    saved_pos1 = (pos2[0], pos2[1] - 100)
                    self.fishing_log(f"找到image2-1-2.png，原始位置: {pos2}，保存位置（上移100px）: {saved_pos1}")
                    window_left, window_top = window.left, window.top
                    pyautogui.moveTo(window_left + pos2[0], window_top + pos2[1], duration=0.3)
                    # 测试模式：只移动不点击；默认模式：移动并点击
                    if not self.buy_bait_test_mode.get():
                        pyautogui.click(window_left + pos2[0], window_top + pos2[1])
                        self.fishing_log("点击image2-1-2.png位置")
                    else:
                        self.fishing_log("测试模式：仅移动，不点击image2-1-2.png")
                    break
                else:
                    self.fishing_log(f"未找到image2-1-2.png，结束补充鱼饵 (第{retry_count + 1}/4次)")
                    retry_count += 1
                    time.sleep(1)
            
            if pos2 is None:
                self.fishing_log("未找到image2-1-2.png，达到重试上限")
                return False
            
            time.sleep(1)
            
            if self.main_app.cancelled:
                return False
            
            # 4. 识别image2-2.png并点击（最多重试4次）
            pos3 = None
            retry_count = 0
            while retry_count < 4 and not self.main_app.cancelled:
                screenshot = self.main_app.capture_window(window)
                if screenshot is None:
                    self.fishing_log("无法获取窗口截图")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                pos3 = self.find_fishing_template(screenshot, "image2-2.png")
                if pos3:
                    self.fishing_log(f"找到image2-2.png，点击位置: {pos3}")
                    window_left, window_top = window.left, window.top
                    pyautogui.moveTo(window_left + pos3[0], window_top + pos3[1], duration=0.3)
                    pyautogui.click(window_left + pos3[0], window_top + pos3[1])
                    break
                else:
                    self.fishing_log(f"未找到image2-2.png，结束补充鱼饵 (第{retry_count + 1}/4次)")
                    retry_count += 1
                    time.sleep(1)
            
            if pos3 is None:
                self.fishing_log("未找到image2-2.png，达到重试上限")
                return False
            
            time.sleep(1)
            
            if self.main_app.cancelled:
                return False
            
            # 5. 识别image2-3.png并点击（失败则跳过）
            screenshot = self.main_app.capture_window(window)
            if screenshot is not None:
                pos4 = self.find_fishing_template(screenshot, "image2-3.png")
                if pos4:
                    self.fishing_log(f"找到image2-3.png，点击位置: {pos4}")
                    window_left, window_top = window.left, window.top
                    pyautogui.moveTo(window_left + pos4[0], window_top + pos4[1], duration=0.3)
                    pyautogui.click(window_left + pos4[0], window_top + pos4[1])
                else:
                    self.fishing_log("未找到image2-3.png，跳过当前流程")
            
            # 6. ESC并识别image2-4.png，最多重试4次
            retry_count = 0
            while retry_count < 4 and not self.main_app.cancelled:
                time.sleep(1)
                pyautogui.press('esc')
                self.fishing_log(f"按下ESC键 (重试第{retry_count + 1}次)")
                time.sleep(1)
                
                screenshot = self.main_app.capture_window(window)
                if screenshot is None:
                    self.fishing_log("无法获取窗口截图")
                    retry_count += 1
                    continue
                
                pos5 = self.find_fishing_template(screenshot, "image2-4.png")
                if pos5:
                    self.fishing_log("找到image2-4.png，补充鱼饵完成")
                    return True
                else:
                    self.fishing_log("未找到image2-4.png，使用保存的坐标点击")
                    if saved_pos1:
                        window_left, window_top = window.left, window.top
                        pyautogui.moveTo(window_left + saved_pos1[0], window_top + saved_pos1[1], duration=0.3)
                        pyautogui.click(window_left + saved_pos1[0], window_top + saved_pos1[1])
                        self.fishing_log("点击完成")
                    retry_count += 1
            
            self.fishing_log("补充鱼饵失败")
            return False
        finally:
            saved_pos1 = None
            self.fishing_log("已清除image2-1-2.png坐标")

    def sell_catch(self, window):
        saved_pos1 = None
        try:
            if self.main_app.cancelled:
                return False
            
            self.fishing_log("=== 开始出售渔获 ===")
            
            window.activate()
            
            # 1. 单击Q键
            pyautogui.press('q')
            self.fishing_log("按下Q键")
            time.sleep(1)
            
            if self.main_app.cancelled:
                return False
            
            # 2. 识别image1-1.png并点击，保存坐标（最多重试4次）
            pos1 = None
            retry_count = 0
            while retry_count < 4 and not self.main_app.cancelled:
                screenshot = self.main_app.capture_window(window)
                if screenshot is None:
                    self.fishing_log("无法获取窗口截图")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                pos1 = self.find_fishing_template(screenshot, "image1-1.png")
                if pos1:
                    saved_pos1 = pos1
                    self.fishing_log(f"找到image1-1.png，保存坐标: {saved_pos1}")
                    window_left, window_top = window.left, window.top
                    pyautogui.moveTo(window_left + pos1[0], window_top + pos1[1], duration=0.3)
                    pyautogui.click(window_left + pos1[0], window_top + pos1[1])
                    break
                else:
                    self.fishing_log(f"未找到image1-1.png，重试出售渔获 (第{retry_count + 1}/4次)")
                    retry_count += 1
                    time.sleep(1)
            
            if pos1 is None:
                self.fishing_log("未找到image1-1.png，达到重试上限")
                return False
            
            time.sleep(1)
            
            if self.main_app.cancelled:
                return False
            
            # 3. 识别image1-2.png并点击（最多重试4次）
            pos2 = None
            retry_count = 0
            while retry_count < 4 and not self.main_app.cancelled:
                screenshot = self.main_app.capture_window(window)
                if screenshot is None:
                    self.fishing_log("无法获取窗口截图")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                pos2 = self.find_fishing_template(screenshot, "image1-2.png")
                if pos2:
                    self.fishing_log(f"找到image1-2.png，点击位置: {pos2}")
                    window_left, window_top = window.left, window.top
                    pyautogui.moveTo(window_left + pos2[0], window_top + pos2[1], duration=0.3)
                    pyautogui.click(window_left + pos2[0], window_top + pos2[1])
                    break
                else:
                    self.fishing_log(f"未找到image1-2.png，重试出售渔获 (第{retry_count + 1}/4次)")
                    retry_count += 1
                    time.sleep(1)
            
            if pos2 is None:
                self.fishing_log("未找到image1-2.png，达到重试上限")
                return False
            
            time.sleep(1)
            
            if self.main_app.cancelled:
                return False
            
            # 4. 识别image1-3.png并点击（最多重试4次）
            pos3 = None
            retry_count = 0
            while retry_count < 4 and not self.main_app.cancelled:
                screenshot = self.main_app.capture_window(window)
                if screenshot is None:
                    self.fishing_log("无法获取窗口截图")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                pos3 = self.find_fishing_template(screenshot, "image1-3.png")
                if pos3:
                    self.fishing_log(f"找到image1-3.png，点击位置: {pos3}")
                    window_left, window_top = window.left, window.top
                    pyautogui.moveTo(window_left + pos3[0], window_top + pos3[1], duration=0.3)
                    pyautogui.click(window_left + pos3[0], window_top + pos3[1])
                    break
                else:
                    self.fishing_log(f"未找到image1-3.png，重试出售渔获 (第{retry_count + 1}/4次)")
                    retry_count += 1
                    time.sleep(1)
            
            if pos3 is None:
                self.fishing_log("未找到image1-3.png，达到重试上限")
                return False
            
            time.sleep(1)
            
            # 5. ESC并识别image1-4.png，最多重试4次
            retry_count = 0
            while retry_count < 4 and not self.main_app.cancelled:
                time.sleep(1)
                pyautogui.press('esc')
                self.fishing_log(f"按下ESC键 (重试第{retry_count + 1}次)")
                time.sleep(1)
                
                screenshot = self.main_app.capture_window(window)
                if screenshot is None:
                    self.fishing_log("无法获取窗口截图")
                    retry_count += 1
                    continue
                
                pos4 = self.find_fishing_template(screenshot, "image1-4.png")
                if pos4:
                    self.fishing_log("找到image1-4.png，出售渔获完成")
                    return True
                else:
                    self.fishing_log("未找到image1-4.png，继续重试")
                    retry_count += 1
            
            self.fishing_log("出售渔获失败，终止操作")
            return False
        finally:
            saved_pos1 = None
            self.fishing_log("已清除image1-1.png坐标")

    def execute_sell_catch_alone(self):
        self.main_app.cancelled = False
        
        window_title = self.main_app.window_var.get()
        if not window_title:
            messagebox.showerror("错误", "请先选择目标窗口")
            return
        
        window = self.main_app.find_window(window_title)
        if not window:
            messagebox.showerror("错误", f"找不到窗口: {window_title}")
            return
        
        def thread_func():
            result = self.sell_catch(window)
            if not result:
                self.main_app.root.after(0, lambda: messagebox.showerror("错误", "出售渔获失败"))
        
        thread = threading.Thread(target=thread_func)
        thread.start()

    def get_settings(self):
        """获取当前设置"""
        return {
            'fish_hsv': [self.fish_h_low.get(), self.fish_s_low.get(), self.fish_v_low.get(),
                        self.fish_h_high.get(), self.fish_s_high.get(), self.fish_v_high.get()],
            'rod_hsv': [self.rod_h_low.get(), self.rod_s_low.get(), self.rod_v_low.get(),
                       self.rod_h_high.get(), self.rod_s_high.get(), self.rod_v_high.get()],
            'key_press_time_per_px': self.key_press_time_per_px.get(),
            'phase_drop_line_enabled': self.phase_drop_line_enabled.get(),
            'phase_fishing_enabled': self.phase_fishing_enabled.get(),
            'phase_cleanup_enabled': self.phase_cleanup_enabled.get(),
            'auto_fishing_loop': self.auto_fishing_loop.get(),
            'auto_fishing_loop_count': self.auto_fishing_loop_count.get(),
            'phase_drop_line_delay': self.phase_drop_line_delay.get(),
            'phase_drop_line_interval': self.phase_drop_line_interval.get(),
            'phase_drop_line_timeout': self.phase_drop_line_timeout.get(),
            'phase_fishing_delay': self.phase_fishing_delay.get(),
            'phase_cleanup_delay': self.phase_cleanup_delay.get(),
            'buy_bait_enabled': self.buy_bait_enabled.get(),
            'buy_bait_interval': self.buy_bait_interval.get(),
            'buy_bait_test_mode': self.buy_bait_test_mode.get(),
            'sell_catch_enabled': self.sell_catch_enabled.get(),
            'sell_catch_interval': self.sell_catch_interval.get(),
            'detect_area_percent': self.detect_area_percent.get(),
        }

    def load_settings(self, settings):
        """加载设置"""
        if not settings:
            return
        if 'fish_hsv' in settings:
            hsv = settings['fish_hsv']
            self.fish_h_low.set(hsv[0])
            self.fish_s_low.set(hsv[1])
            self.fish_v_low.set(hsv[2])
            self.fish_h_high.set(hsv[3])
            self.fish_s_high.set(hsv[4])
            self.fish_v_high.set(hsv[5])
        if 'rod_hsv' in settings:
            hsv = settings['rod_hsv']
            self.rod_h_low.set(hsv[0])
            self.rod_s_low.set(hsv[1])
            self.rod_v_low.set(hsv[2])
            self.rod_h_high.set(hsv[3])
            self.rod_s_high.set(hsv[4])
            self.rod_h_high.set(hsv[5])
        self.key_press_time_per_px.set(settings.get('key_press_time_per_px', 4))
        self.phase_drop_line_enabled.set(settings.get('phase_drop_line_enabled', True))
        self.phase_fishing_enabled.set(settings.get('phase_fishing_enabled', True))
        self.phase_cleanup_enabled.set(settings.get('phase_cleanup_enabled', True))
        self.auto_fishing_loop.set(settings.get('auto_fishing_loop', False))
        self.auto_fishing_loop_count.set(settings.get('auto_fishing_loop_count', 0))
        self.phase_drop_line_delay.set(settings.get('phase_drop_line_delay', 0))
        self.phase_drop_line_interval.set(settings.get('phase_drop_line_interval', 0.75))
        self.phase_drop_line_timeout.set(settings.get('phase_drop_line_timeout', 10))
        self.phase_fishing_delay.set(settings.get('phase_fishing_delay', 0.25))
        self.phase_cleanup_delay.set(settings.get('phase_cleanup_delay', 1))
        self.buy_bait_enabled.set(settings.get('buy_bait_enabled', False))
        self.buy_bait_interval.set(settings.get('buy_bait_interval', 99))
        self.buy_bait_test_mode.set(settings.get('buy_bait_test_mode', False))
        self.sell_catch_enabled.set(settings.get('sell_catch_enabled', False))
        self.sell_catch_interval.set(settings.get('sell_catch_interval', 99))
        self.detect_area_percent.set(settings.get('detect_area_percent', 15))