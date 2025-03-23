import os
import sys
import pandas as pd
from faker import Faker
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
import io
import base64
import binascii
import requests  # 添加requests库用于获取在线图片
from logo import logo_data

class MockDataGenerator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("朱雀-司机信息生成器")
        self.window.geometry("900x500")  # 增加窗口尺寸以适应新增内容
        self.window.resizable(False, False)
        
        # 初始化数据存储
        self.data = []
        
        # 初始化图片变量
        self.image = None
        self.photo = None
        self.marquee_text = "南方朱雀出品！           谁能把一首恋歌唱的依然动听！                 授人以鱼不如授人以渔！"
        self.marquee_position = 0
        self.marquee_running = True
        
        self.setup_ui()
        
        # 加载固定图片
        self.load_fixed_image()
        
    def setup_ui(self):
        # 创建顶部轮播文字框架
        marquee_frame = ttk.Frame(self.window, height=30)
        marquee_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        
        # 创建轮播文字标签
        self.marquee_label = ttk.Label(marquee_frame, text=self.marquee_text, font=("Arial", 12, "bold"))
        self.marquee_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 启动轮播文字线程
        self.start_marquee()
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=1, column=0, sticky='nsew')
        
        # 创建图片显示框架
        image_frame = ttk.LabelFrame(self.window, text="图片展示", padding="10")
        image_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)
        
        # 创建图片标签
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(expand=True, fill=tk.BOTH, pady=10)
        
        # 添加图片信息标签
        self.image_info_label = ttk.Label(image_frame, text="正在加载图片...", font=("Arial", 10))
        self.image_info_label.pack(pady=5)
        
        # 数据量设置区域
        ttk.Label(main_frame, text="生成数据条数:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.count_var = tk.StringVar(value="100")
        count_entry = ttk.Entry(main_frame, textvariable=self.count_var, width=10)
        count_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 生成按钮
        generate_btn = ttk.Button(main_frame, text="生成数据", command=self.generate_data)
        generate_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # 导出按钮
        self.export_btn = ttk.Button(main_frame, text="立即导出", command=self.export_data, state=tk.DISABLED)
        self.export_btn.grid(row=0, column=3, padx=10, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=1, column=0, columnspan=3, pady=10)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="数据预览", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=10)
        
        # 创建带滚动条的文本框
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(expand=True, fill=tk.BOTH)
        
        # 添加垂直滚动条
        scrollbar = ttk.Scrollbar(preview_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本框并关联滚动条
        self.preview_text = tk.Text(preview_container, height=10, width=50, yscrollcommand=scrollbar.set)
        self.preview_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.config(command=self.preview_text.yview)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
    def generate_data(self):
        try:
            count = int(self.count_var.get())
            if count <= 0:
                messagebox.showerror("错误", "请输入大于0的数值")
                return
                
            self.status_label.config(text="正在生成数据...")
            self.progress_var.set(0)
            self.preview_text.delete(1.0, tk.END)
            self.window.update()
            
            fake = Faker(locale="zh_CN")
            self.data = []
            
            for i in range(count):
                car = fake.license_plate().replace("-", "")
                self.data.append({
                    "车牌号码": car,
                    "司机姓名": fake.name(),
                    "身份证号": fake.ssn(),
                    "手机号码": fake.phone_number()
                })
                
                # 更新进度条和预览
                progress = (i + 1) / count * 100
                self.progress_var.set(progress)
                
                # 显示所有生成的数据，不再限制只显示前5条
                preview = f"数据 {i+1}:\n"
                for key, value in self.data[-1].items():
                    preview += f"{key}: {value}\n"
                preview += "\n"
                self.preview_text.insert(tk.END, preview)
                
                self.window.update()
            
            # 启用导出按钮
            self.export_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"已生成 {count} 条数据，可以点击【立即导出】按钮导出")
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"生成数据时发生错误: {str(e)}")
            
        self.progress_var.set(0)
        
    def export_data(self):
        if not self.data:
            messagebox.showerror("错误", "没有可导出的数据")
            return
            
        # 创建DataFrame
        df = pd.DataFrame(self.data)
        
        # 选择保存位置
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"司机信息_{timestamp}.xlsx"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")],
            initialfile=default_filename
        )
        
        if file_path:
            df.to_excel(file_path, index=False)
            self.status_label.config(text=f"数据已成功保存到: {os.path.basename(file_path)}")
            messagebox.showinfo("成功", "数据导出完成！")
        else:
            self.status_label.config(text="取消导出")
    
    def run(self):
        self.window.mainloop()
        self.marquee_running = False
    
    def start_marquee(self):
        """启动文字轮播"""
        self.update_marquee()
    
    def update_marquee(self):
        """更新轮播文字位置"""
        if not self.marquee_running:
            return
            
        # 更新文字位置
        self.marquee_position = (self.marquee_position + 1) % len(self.marquee_text)
        display_text = self.marquee_text[self.marquee_position:] + self.marquee_text[:self.marquee_position]
        self.marquee_label.config(text=display_text)
        
        # 设置下一次更新
        self.window.after(100, self.update_marquee)
    
    def handle_image_error(self, error_msg):
        """统一处理图片加载错误"""
        print(error_msg)
        self.image_label.config(text="无法显示图片")
        self.image_info_label.config(text=error_msg)
        self.create_fallback_image()
    
    def update_image(self):
        try:
            if self.image:
                self.photo = ImageTk.PhotoImage(self.image)
                self.image_label.config(image=self.photo)
                self.image_info_label.config(text="图片加载成功")
        except Exception as e:
            self.handle_image_error(f"更新图片失败: {str(e)}")
    
    def load_fixed_image(self):
        try:
            # 从在线URL加载图片
            image_url = "https://picturedata.oss-cn-beijing.aliyuncs.com/news/2025-03-13/9a94685baa4d482c8a967c9ac292f958.png"
            self.image_info_label.config(text=f"正在从 {image_url} 加载图片...")
            self.window.update()
            
            # 使用requests获取图片数据
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # 将响应内容转换为字节流
                image_data = response.content
                temp_file = io.BytesIO(image_data)
                
                # 加载图片
                self.image = Image.open(temp_file)
                
                # 调整图片大小
                self.image = self.image.resize((300, 300), Image.Resampling.LANCZOS)
                
                # 转换为PhotoImage
                self.photo = ImageTk.PhotoImage(self.image)
                
                # 在标签中显示图片
                self.image_label.config(image=self.photo)
                self.image_info_label.config(text="")
            else:
                raise Exception(f"获取图片失败，HTTP状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.handle_image_error(f"网络请求错误: {str(e)}")
            self.create_fallback_image()
        except Exception as e:
            self.handle_image_error(f"加载图片失败: {str(e)}")
            self.create_fallback_image()
    
    def create_fallback_image(self):
        """创建一个简单的替代图片"""
        try:
            # 创建一个蓝色背景的图片
            img = Image.new('RGB', (300, 300), color='blue')
            # 转换为PhotoImage
            self.photo = ImageTk.PhotoImage(img)
            # 在标签中显示图片
            self.image_label.config(image=self.photo)
            print("已创建替代图片")
        except Exception as e:
            print(f"创建替代图片失败: {str(e)}")
            self.image_label.config(text="无法显示图片")

# 主程序入口
if __name__ == "__main__":
    app = MockDataGenerator()
    app.run()
