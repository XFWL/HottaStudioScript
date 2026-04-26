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
        self.root.title("异环店长特供")
        self.root.geometry("800x750")  # 加宽宽度，保持高度
        
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
        
        # 内容框架 - 顶格显示
        content_frame = ttk.Frame(main_frame, style="Main.TFrame")
        content_frame.pack(anchor=tk.NW)  # 顶格显示
        
        # 窗口选择
        ttk.Label(content_frame, text="选择目标窗口:", style="Subtitle.TLabel").pack(anchor=tk.NW, pady=3)  # 标题顶格
        window_frame = ttk.Frame(content_frame, style="Main.TFrame")
        window_frame.pack(anchor=tk.NW, pady=3, padx=20)  # 具体设置缩进20像素
        self.window_var = tk.StringVar()
        self.window_combobox = ttk.Combobox(window_frame, textvariable=self.window_var, width=40)
        self.window_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Button(window_frame, text="刷新", command=self.refresh_windows).pack(side=tk.LEFT, padx=5)
        
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
        self.hold_time = tk.IntVar(value=42)
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
        button_frame = ttk.Frame(main_frame, style="Main.TFrame")
        button_frame.pack(pady=5)  # 进一步减小间距
        
        # 开始按钮
        ttk.Button(button_frame, text="开始执行", command=self.start_execution).pack(side=tk.LEFT, padx=10)
        
        # F12取消热键提示 - 放在开始按钮旁边
        ttk.Label(button_frame, text="取消热键: F12", style="Hotkey.TLabel").pack(side=tk.LEFT, padx=10)
        
        # 状态标签 - 移除就绪显示
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(pady=0)  # 最小间距
        
        # 日志显示区域
        ttk.Label(main_frame, text="执行日志:", style="Log.TLabel").pack(anchor=tk.NW, pady=0)  # 最小间距
        log_frame = ttk.Frame(main_frame, style="Main.TFrame")
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
            # 激活窗口
            window.activate()
            time.sleep(0.5)  # 等待窗口激活
            
            # 获取窗口位置和大小
            left, top, width, height = window.left, window.top, window.width, window.height
            
            # 打印窗口信息用于调试
            print(f"窗口信息: left={left}, top={top}, width={width}, height={height}")
            
            # 确保坐标有效
            if left < 0:
                left = 0
            if top < 0:
                top = 0
            if width <= 0 or height <= 0:
                print("窗口大小无效")
                return None
            
            # 对于1920x1080窗口，尝试捕获整个屏幕
            if width == 1920 and height == 1080:
                print("检测到1920x1080窗口，尝试捕获整个屏幕")
                screenshot = pyautogui.screenshot()
            else:
                # 捕获窗口区域
                print(f"捕获窗口区域: ({left}, {top}, {width}, {height})")
                screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            # 转换为OpenCV格式
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screenshot
        except Exception as e:
            print(f"捕获窗口失败: {str(e)}")
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
                    print("操作已取消")
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
                        print("操作已取消")
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
                    print("操作已取消")
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
        """设置热键监听"""
        # 绑定F12热键用于取消操作
        keyboard.add_hotkey('f12', self.cancel_operation)
        print("已设置F12为取消热键")
    
    def cancel_operation(self):
        """取消当前操作"""
        print("收到取消指令，正在停止操作...")
        self.log("收到取消指令，正在停止操作...")
        self.cancelled = True
        messagebox.showinfo("取消", "操作已取消（需要管理员启动）")
    
    def perform_hold_click(self, window, position, duration):
        """执行重复左键点击操作，持续指定时间"""
        try:
            # 激活窗口
            window.activate()
            time.sleep(0.3)  # 等待窗口激活
            
            # 检查是否取消
            if self.cancelled:
                print("操作已取消")
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
                    print("操作已取消")
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
            
            # 默认操作：获取窗口后执行鼠标左键点击一次
            self.log("执行默认操作：获取窗口后执行鼠标左键点击")
            
            # 激活窗口
            window.activate()
            time.sleep(0.3)  # 等待窗口激活
            
            # 检查是否取消
            if self.cancelled:
                print("操作已取消")
                self.log("操作已取消")
                self.status_var.set("已取消")
                return
            
            # 获取窗口中心位置
            left, top, width, height = window.left, window.top, window.width, window.height
            center_x = left + width // 2
            center_y = top + height // 2
            
            self.log(f"获取窗口中心位置: ({center_x}, {center_y})")
            
            # 执行鼠标左键点击一次
            self.log("执行鼠标左键点击 1 次")
            
            # 检查是否取消
            if self.cancelled:
                print("操作已取消")
                self.log("操作已取消")
                self.status_var.set("已取消")
                return
            
            # 模拟鼠标平滑移动，默认300ms，动态波动30毫秒
            import random
            duration = 0.3 + random.uniform(-0.03, 0.03)  # 300ms ± 30ms
            pyautogui.moveTo(center_x, center_y, duration=duration)
            
            # 执行点击
            pyautogui.click()
            time.sleep(0.1)  # 点击间隔
            
            self.log("默认操作执行完成")
            
            # 执行循环
            current_loop = 0
            max_loops = loop_count if loop_option == "custom" else 1
            
            while True:
                # 检查是否取消
                if self.cancelled:
                    print("操作已取消")
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
                            print("操作已取消")
                            self.log("操作已取消")
                            self.status_var.set("已取消")
                            return
                        
                        if attempt > 0:
                            self.log(f"执行第 {attempt} 次重试尝试")
                            # 重试尝试前等待，每0.1秒检查一次取消状态，确保能够立刻取消
                            retry_wait_steps = 10  # 1秒 / 0.1秒 = 10次
                            for i in range(retry_wait_steps):
                                if self.cancelled:
                                    print("操作已取消")
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
                            print("操作已取消")
                            self.log("操作已取消")
                            self.status_var.set("已取消")
                            return
                        
                        if attempt > 0:
                            self.log(f"执行第 {attempt} 次重试尝试")
                            # 重试尝试前等待，每0.1秒检查一次取消状态，确保能够立刻取消
                            retry_wait_steps = 10  # 1秒 / 0.1秒 = 10次
                            for i in range(retry_wait_steps):
                                if self.cancelled:
                                    print("操作已取消")
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
                            print("操作已取消")
                            self.log("操作已取消")
                            self.status_var.set("已取消")
                            return
                        
                        if attempt > 0:
                            self.log(f"执行第 {attempt} 次重试尝试")
                            # 重试尝试前等待，每0.1秒检查一次取消状态，确保能够立刻取消
                            retry_wait_steps = 10  # 1秒 / 0.1秒 = 10次
                            for i in range(retry_wait_steps):
                                if self.cancelled:
                                    print("操作已取消")
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
                                    print("操作已取消")
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
                            print("操作已取消")
                            self.log("操作已取消")
                            self.status_var.set("已取消")
                            return
                        
                        if attempt > 0:
                            self.log(f"执行第 {attempt} 次重试尝试")
                            # 重试尝试前等待，每0.1秒检查一次取消状态，确保能够立刻取消
                            retry_wait_steps = 10  # 1秒 / 0.1秒 = 10次
                            for i in range(retry_wait_steps):
                                if self.cancelled:
                                    print("操作已取消")
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
                                        print("操作已取消")
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

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRecognitionAutomation(root)
    root.mainloop()