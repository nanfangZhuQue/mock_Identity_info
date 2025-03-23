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
import random
import io
import base64
import binascii
import requests  # 添加requests库用于获取在线图片
import pygame  # 添加pygame库用于MP3播放
from logo import logo_data
from button_icons import get_copy_icon, get_clear_icon  # 导入按钮图标
from area_code_map import area_code_map  # 导入地区码映射
from area_code_map import city_license_map  # 导入车牌字母映射
from province_code_map import province_code_map  # 导入省份代码映射

class MockDataGenerator:
    def _get_fallback_city_list(self, province):
        """获取备用城市列表"""
        # 首先尝试从 area_code_map 获取
        if province in area_code_map:
            return sorted(list(area_code_map[province].keys()))
        
        # 然后尝试从 city_license_map 获取
        if province in city_license_map:
            return sorted(list(city_license_map[province].keys()))
        
        # 最后检查特别行政区
        if province in self.cities:
            return sorted(self.cities[province])
        
        return []
    
    def _get_default_districts(self):
        """获取默认区县列表"""
        return [
            "市辖区", "新城区", "老城区", "城关区",
            "高新区", "开发区", "工业区", "经济开发区"
        ]
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("朱雀-身份证信息生成器")
        self.window.geometry("900x600")  # 增加窗口尺寸以适应新增内容
        self.window.resizable(False, False)
        
        # 初始化数据存储
        self.data = []
        
        # 初始化图片变量
        self.image = None
        self.photo = None
        self.marquee_text = "警告：本程序为南方朱雀出品！仅为内部测试人员工具模拟使用，任何人不能恶意违规或商业使用！！！最终解释权为南方朱雀！\t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t \t"
        self.marquee_position = 0
        self.marquee_running = True
        
        # 初始化音频播放相关变量
        try:
            pygame.mixer.init(frequency=44100)  # 初始化pygame混音器，指定采样率
        except Exception as e:
            print(f"初始化音频播放器失败: {str(e)}")
            
        # 获取音乐文件路径，支持PyInstaller打包环境
        try:
            # 检查是否在PyInstaller打包环境中运行
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # 在打包环境中，使用_MEIPASS作为基础路径
                base_path = getattr(sys, '_MEIPASS')
                print(f"运行在PyInstaller打包环境中，基础路径: {base_path}")
                self.music_file = os.path.join(base_path, "test_music.mp3")
            else:
                # 在开发环境中，使用脚本所在目录
                self.music_file = os.path.join(os.path.dirname(__file__), "test_music.mp3")
            
            print(f"音乐文件路径: {self.music_file}")
            # 检查文件是否存在
            if not os.path.exists(self.music_file):
                print(f"警告: 音乐文件不存在: {self.music_file}")
        except Exception as e:
            print(f"设置音乐文件路径时出错: {str(e)}")
            # 设置一个默认值，避免后续代码出错
            self.music_file = "test_music.mp3"
            
        self.is_playing = False
        self.music_paused = False
        
        # 初始化所有数据变量
        self.provinces = [
            "北京市", "上海市", "天津市", "重庆市",  # 直辖市
            "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省", "江苏省", "浙江省", "安徽省", 
            "福建省", "江西省", "山东省", "河南省", "湖北省", "湖南省", "广东省", "海南省", 
            "四川省", "贵州省", "云南省", "陕西省", "甘肃省", "青海省", "台湾省",
            "内蒙古自治区", "广西壮族自治区", "西藏自治区", "宁夏回族自治区", "新疆维吾尔自治区", 
            "香港特别行政区", "澳门特别行政区"  # 特别行政区
        ]
        
        # 初始化界面变量
        self.province_var = tk.StringVar(value=self.provinces[0])  # 默认选择第一个省份
        self.city_var = tk.StringVar()
        self.district_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="男")
        self.birth_date_var = tk.StringVar(value=datetime.now().strftime("%Y/%m/%d"))
        
        # 初始化城市和区县数据结构
        self.cities = {}
        self.districts = {}
        
        # 修改执行顺序：先初始化数据，再创建UI
        self.init_region_data()
        self.setup_ui()
        self.load_fixed_image()
    
    def init_region_data(self):
        """初始化省市区数据"""
        
        # 初始化城市和区县数据结构
        self.cities = {}
        self.districts = {}
        
        try:
            # 从area_code_map获取标准的省市区数据
            missing_provinces = []
            empty_districts = []
            data_errors = []

            for province in self.provinces:
                try:
                    if province in area_code_map:
                        # 获取并排序城市列表
                        self.cities[province] = sorted(list(area_code_map[province].keys()))
                        
                        # 处理每个城市的区县数据
                        for city in self.cities[province]:
                            try:
                                districts = area_code_map[province][city]
                                if districts:
                                    self.districts[city] = sorted(list(districts.keys()))
                                    if not self.districts[city]:  # 如果区县列表为空
                                        empty_districts.append(f"{province}{city}")
                                        # 使用默认区县
                                        self.districts[city] = self._get_default_districts()
                                else:
                                    empty_districts.append(f"{province}{city}")
                                    # 使用默认区县
                                    self.districts[city] = self._get_default_districts()
                            except Exception as city_error:
                                data_errors.append(f"{province}{city}: {str(city_error)}")
                                # 使用默认区县
                                self.districts[city] = self._get_default_districts()
                    # 检查是否在city_license_map中存在
                    elif province in city_license_map:
                        # 从city_license_map获取城市列表
                        self.cities[province] = sorted(list(city_license_map[province].keys()))
                        # 这些城市没有区县数据，将在UI中使用默认区县
                        for city in self.cities[province]:
                            self.districts[city] = self._get_default_districts()
                    else:
                        if province not in ["香港特别行政区", "澳门特别行政区"]:
                            missing_provinces.append(province)
                        # 为特别行政区添加默认数据
                        if province in ["香港特别行政区", "澳门特别行政区"]:
                            if province == "香港特别行政区":
                                self.cities[province] = ["香港岛", "九龙", "新界"]
                            else:  # 澳门
                                self.cities[province] = ["澳门半岛", "氹仔岛", "路环岛"]
                            
                            # 为特别行政区的城市添加默认区县
                            for city in self.cities[province]:
                                self.districts[city] = self._get_default_districts()
                            
                except Exception as province_error:
                    data_errors.append(f"{province}: {str(province_error)}")
            
            # 确保北京市的区县数据正确加载
            if "北京市" in self.cities:
                for city in self.cities["北京市"]:
                    if city not in self.districts or not self.districts[city]:
                        self.districts[city] = self._get_default_districts()
            
            # 构建警告消息
            # 错误统计和分析
            error_stats = {
                "missing": {"count": len(missing_provinces), "items": missing_provinces, "icon": "🚫"},
                "incomplete": {"count": len(empty_districts), "items": empty_districts, "icon": "⚠️"},
                "error": {"count": len(data_errors), "items": data_errors, "icon": "❌"}
            }
            
            warning_parts = []
            error_details = []
            suggestions = []
            total_issues = sum(stat["count"] for stat in error_stats.values())

            # 构建错误摘要
            for error_type, stats in error_stats.items():
                if stats["count"] > 0:
                    if error_type == "missing":
                        warning_parts.append(f"{stats['icon']} 数据缺失（{stats['count']}）")
                        error_details.append(
                            "【数据完全缺失】\n" +
                            "\n".join(f"▫️ {item}" for item in stats["items"]) +
                            "\n\n影响：这些地区将无法选择和使用"
                        )
                        suggestions.append("• 优先使用其他可用地区")
                    elif error_type == "incomplete":
                        warning_parts.append(f"{stats['icon']} 数据不完整（{stats['count']}）")
                        error_details.append(
                            "【区县数据缺失】\n" +
                            "\n".join(f"▫️ {item}" for item in stats["items"]) +
                            "\n\n影响：这些地区将使用默认区县数据"
                        )
                        suggestions.append("• 手动选择正确的区县信息")
                    else:  # error
                        warning_parts.append(f"{stats['icon']} 数据异常（{stats['count']}）")
                        error_details.append(
                            "【数据加载异常】\n" +
                            "\n".join(f"▫️ {item}" for item in stats["items"]) +
                            "\n\n影响：这些错误可能导致数据不准确"
                        )
                        suggestions.append("• 检查数据文件完整性")
            
            if warning_parts:
                # 构建数据状态摘要
                summary = " | ".join(warning_parts)
                total_regions = len(self.provinces)
                # 统计受影响的地区数量
                affected_provinces = set()
                for item in error_stats["missing"]["items"]:
                    province_name = item.split(':')[0].strip()
                    affected_provinces.add(province_name)
                affected_regions = len(affected_provinces)
                
                # 构建图形化统计信息
                stats_bar = "数据完整性: " + "█" * (20 - affected_regions) + "░" * affected_regions
                stats_info = (
                    f"总计地区: {total_regions} | 受影响: {affected_regions} | "
                    f"完整率: {((total_regions - affected_regions) / total_regions * 100):.1f}%"
                )
                
                # 构建详细错误报告
                detail_msg = (
                    f"数据加载状态分析\n{'-' * 50}\n\n"
                    f"{stats_bar}\n{stats_info}\n\n"
                    f"发现问题 ({total_issues}项):\n{summary}\n\n"
                    f"{'-' * 50}\n"
                    f"{''.join(error_details)}\n"
                    f"{'-' * 50}\n\n"
                    "📋 解决建议:\n" + "\n".join(suggestions) + "\n\n"
                    "🔍 补充说明:\n"
                    "• 数据缺失地区将被禁用\n"
                    "• 不完整数据将使用默认值\n"
                    "• 特别行政区使用独立数据源\n"
                )
                
                # 如果有严重错误，显示警告对话框
                if error_stats["missing"]["count"] > 0 or error_stats["error"]["count"] > 0:
                    self.window.after(1000, lambda: messagebox.showwarning(
                        "数据加载警告", 
                        f"数据加载过程中发现以下问题:\n\n{summary}\n\n"
                        "点击'详情'查看完整报告。",
                        detail=detail_msg
                    ))
                
                # 更新状态栏
                self.status_label.config(text=f"数据加载状态: {summary}")
                
        except Exception as e:
            error_msg = f"初始化地区数据时出错: {str(e)}"
            print(error_msg)
            messagebox.showerror("数据初始化错误", 
                f"初始化地区数据时发生错误:\n{str(e)}\n\n"
                "程序将使用有限的功能继续运行。")
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建顶部轮播文字框架
        marquee_frame = ttk.Frame(self.window, height=30)
        marquee_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        
        # 创建一个Canvas作为轮播文字的容器，以隔离滚动效果
        self.marquee_canvas = tk.Canvas(marquee_frame, height=30, bd=0, highlightthickness=0, bg=self.window.cget('bg'))
        self.marquee_canvas.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        
        # 在Canvas上创建轮播文字标签
        self.marquee_label = tk.Label(self.marquee_canvas, text=self.marquee_text, font=("Arial", 12, "bold"), fg="red", bg=self.window.cget('bg'))
        self.marquee_canvas.create_window(0, 15, window=self.marquee_label, anchor='w')
        
        # 启动轮播文字线程
        self.start_marquee()
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=1, column=0, sticky='nsew')
        
        # 创建图片显示框架
        image_frame = ttk.LabelFrame(self.window, text="图片展示", padding="10")
        image_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)
        image_frame.grid_rowconfigure(0, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)
        
        # 创建图片标签
        self.image_label = tk.Label(image_frame, bg='white')
        self.image_label.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # 添加图片信息标签
        self.image_info_label = ttk.Label(image_frame, text="正在加载图片...", font=("Arial", 10))
        self.image_info_label.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        # 创建商务合作标签
        self.cooperation_label = tk.Label(image_frame, text="商务合作 敬请联系", font=("Arial", 12, "bold"), fg="#1976D2", bg="white")
        self.cooperation_label.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        
        # 创建选择区域框架
        selection_frame = ttk.LabelFrame(main_frame, text="信息选择", padding="10")
        selection_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=10)
        
        # 省市区选择
        # 省份选择
        ttk.Label(selection_frame, text="省份:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        province_combo = ttk.Combobox(selection_frame, textvariable=self.province_var, values=self.provinces, state="readonly", width=10)
        province_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # 城市选择
        ttk.Label(selection_frame, text="城市:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.city_combo = ttk.Combobox(selection_frame, textvariable=self.city_var, state="readonly", width=10)
        self.city_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # 区县选择
        ttk.Label(selection_frame, text="区县:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.district_combo = ttk.Combobox(selection_frame, textvariable=self.district_var, state="readonly", width=10)
        self.district_combo.grid(row=0, column=5, padx=5, pady=5)
        
        # 性别选择
        ttk.Label(selection_frame, text="性别:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        gender_frame = ttk.Frame(selection_frame)
        gender_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(gender_frame, text="男", variable=self.gender_var, value="男").pack(side=tk.LEFT)
        ttk.Radiobutton(gender_frame, text="女", variable=self.gender_var, value="女").pack(side=tk.LEFT)
        
        # 出生日期选择
        ttk.Label(selection_frame, text="出生日期:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        date_frame = ttk.Frame(selection_frame)
        date_frame.grid(row=1, column=3, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # 添加日期输入框
        date_entry = ttk.Entry(date_frame, textvariable=self.birth_date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        # 添加事件绑定
        province_combo.bind("<<ComboboxSelected>>", self.on_province_selected)
        self.city_combo.bind("<<ComboboxSelected>>", self.on_city_selected)
        
        # 创建状态栏
        status_frame = ttk.Frame(self.window)
        status_frame.grid(row=2, column=0, columnspan=2, sticky='ew')
        self.status_label = ttk.Label(status_frame, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 初始化省份选择
        self.update_city_list()
        
        # 添加生成按钮
        self.add_generate_button(main_frame)
    
    def on_province_selected(self, event=None):
        """当省份选择改变时更新城市列表"""
        province = self.province_var.get()
        print(f"选择省份: {province}")
        self.update_city_list()
        
    def on_city_selected(self, event=None):
        """当城市选择改变时更新区县列表"""
        city = self.city_var.get()
        print(f"选择城市: {city}")
        self.update_district_list()
        
    def update_city_list(self):
        """更新城市下拉列表"""
        province = self.province_var.get()
        
        # 清空当前城市和区县选择
        self.city_var.set("")
        self.district_var.set("")
        
        # 获取城市列表
        if province in self.cities and self.cities[province]:
            city_list = self.cities[province]
        else:
            # 使用备用城市列表
            city_list = self._get_fallback_city_list(province)
            
        # 更新城市下拉列表
        self.city_combo['values'] = city_list
        
        # 如果有城市，默认选择第一个
        if city_list:
            self.city_var.set(city_list[0])
            self.update_district_list()
            
    def update_district_list(self):
        """更新区县下拉列表"""
        province = self.province_var.get()
        city = self.city_var.get()
        
        # 清空当前区县选择
        self.district_var.set("")
        
        # 获取区县列表
        if city in self.districts and self.districts[city]:
            district_list = self.districts[city]
            print(f"获取区县列表: {province}{city} -> {len(district_list)}个区县")
        else:
            # 使用默认区县列表
            district_list = self._get_default_districts()
            print(f"警告: {province}{city} 没有区县数据，使用默认区县列表")
            
        # 更新区县下拉列表
        self.district_combo['values'] = district_list
        
        # 如果有区县，默认选择第一个
        if district_list:
            self.district_var.set(district_list[0])
            print(f"默认选择区县: {district_list[0]}")
            
            # 检查是否可以获取区域代码
            if province in area_code_map and city in area_code_map[province] and district_list[0] in area_code_map[province][city]:
                full_code = area_code_map[province][city][district_list[0]]
                area_code = full_code[:6]
                print(f"区域代码检查: {province}{city}{district_list[0]} -> {area_code}")
            else:
                print(f"区域代码检查: 无法获取 {province}{city}{district_list[0]} 的区域代码")
    
    def start_marquee(self):
        """启动文字轮播效果"""
        if not self.marquee_running:
            return
            
        # 更新轮播位置
        self.marquee_position = (self.marquee_position + 1) % len(self.marquee_text)
        rotated_text = self.marquee_text[self.marquee_position:] + self.marquee_text[:self.marquee_position]
        self.marquee_label.config(text=rotated_text)
        
        # 获取标签的实际宽度
        self.marquee_label.update_idletasks()
        label_width = self.marquee_label.winfo_width()
        canvas_width = self.marquee_canvas.winfo_width()
        
        # 确保Canvas宽度足够
        if canvas_width > 0:
            # 设置Canvas的滚动区域
            self.marquee_canvas.config(scrollregion=(0, 0, label_width, 30))
        
        # 每500毫秒更新一次，降低滚动速度
        self.window.after(500, self.start_marquee)
    
    def handle_image_error(self, error_msg):
        """统一处理图片加载错误"""
        print(error_msg)
        self.image_label.config(text="无法显示图片")
        self.image_info_label.config(text=error_msg)
        self.create_fallback_image()

    def load_fixed_image(self):
        """加载固定图片"""
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
                
                # 获取预览区域大小
                preview_width = self.image_label.winfo_width()
                preview_height = self.image_label.winfo_height()
                
                # 如果预览区域尚未渲染完成，使用默认大小
                if preview_width <= 1 or preview_height <= 1:
                    preview_width = 300
                    preview_height = 300
                
                # 计算缩放比例
                width_ratio = preview_width / self.image.width
                height_ratio = preview_height / self.image.height
                scale_ratio = min(width_ratio, height_ratio)
                
                # 计算新的尺寸，保持宽高比
                new_width = int(self.image.width * scale_ratio)
                new_height = int(self.image.height * scale_ratio)
                
                # 调整图片大小，保持宽高比
                self.image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 转换为PhotoImage
                self.photo = ImageTk.PhotoImage(self.image)
                
                # 在标签中显示图片
                self.image_label.config(image=self.photo)
                self.image_info_label.config(text="")
                # 添加商务合作文字
                self.cooperation_label.config(text="商务合作 敬请联系", font=("Arial", 12, "bold"), fg="#1976D2")
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
            print(f"创建备用图片失败: {str(e)}")
            self.image_label.config(text="无法显示图片")

    
    def generate_id_card(self):
        """生成身份证号码"""
        import random
        
        # 获取选择的省市区
        province = self.province_var.get()
        city = self.city_var.get()
        district = self.district_var.get()
        
        # 获取区域代码
        area_code = ""
        try:
            # 调试信息
            debug_info = f"尝试获取区域代码: 省={province}, 市={city}, 区={district}"
            print(debug_info)
            
            # 确保使用正确的区域代码
            if province in area_code_map and city in area_code_map[province] and district in area_code_map[province][city]:
                # 只取前6位作为区域代码
                full_code = area_code_map[province][city][district]
                area_code = full_code[:6]  # 取前6位作为身份证区域代码
                self.status_label.config(text=f"成功获取 {province}{city}{district} 的区域代码: {area_code}")
                print(f"成功: 使用精确区域代码 {area_code}")
            else:
                # 尝试查找该省份下任意城市和区县的代码作为备用
                if province in area_code_map:
                    # 获取该省份下第一个城市
                    first_city = list(area_code_map[province].keys())[0]
                    # 获取该城市下第一个区县
                    first_district = list(area_code_map[province][first_city].keys())[0]
                    # 获取区域代码
                    full_code = area_code_map[province][first_city][first_district]
                    area_code = full_code[:6]  # 取前6位作为身份证区域代码
                    self.status_label.config(text=f"警告: 无法获取 {province}{city}{district} 的精确区域代码，使用 {province}{first_city}{first_district} 的代码: {area_code}")
                    print(f"警告: 使用备用区域代码 {area_code} (来自 {province}{first_city}{first_district})")
                # 使用省份代码映射表获取省级代码
                elif province in province_code_map:
                    # 使用省份代码前缀
                    area_code = province_code_map[province][:6]  # 确保只取前6位
                    self.status_label.config(text=f"警告: 无法获取 {province}{city}{district} 的精确区域代码，使用省级代码: {area_code}")
                    print(f"警告: 使用省级代码 {area_code} (来自 province_code_map)")
                else:
                    # 使用默认区域代码
                    area_code = "110101"  # 北京市东城区
                    self.status_label.config(text=f"警告: 无法获取 {province} 的区域代码，使用默认代码")
                    print(f"错误: 无法找到省份 {province} 的任何区域代码，使用默认代码 110101")
        except Exception as e:
            # 尝试使用省份代码映射表
            if province in province_code_map:
                area_code = province_code_map[province][:6]  # 确保只取前6位
                self.status_label.config(text=f"警告: 发生错误，使用省级代码: {area_code}")
                print(f"异常处理: {str(e)}，使用省级代码 {area_code}")
            else:
                area_code = "110101"  # 北京市东城区
                self.status_label.config(text=f"错误: {str(e)}，使用默认区域代码")
                print(f"异常: {str(e)}，使用默认区域代码 110101")
        
        # 获取出生日期 - 修正为正确格式
        birth_date_str = self.birth_date_var.get()
        try:
            # 将日期字符串转换为日期对象
            birth_date = datetime.strptime(birth_date_str, "%Y/%m/%d")
            # 转换为身份证格式 YYYYMMDD
            birth_date = birth_date.strftime("%Y%m%d")
        except:
            # 使用当前日期
            birth_date = datetime.now().strftime("%Y%m%d")
            
        # 生成顺序码 (3位)
        gender = self.gender_var.get()
        if gender == "男":
            # 男性使用奇数
            sequence = str(random.randint(1, 499) * 2 + 1).zfill(3)
        else:
            # 女性使用偶数
            sequence = str(random.randint(0, 499) * 2).zfill(3)
            
        # 组合前17位
        id_without_check = f"{area_code}{birth_date}{sequence}"
        
        # 计算校验码
        check_code = self.calculate_check_code(id_without_check)
        
        # 返回完整的18位身份证号
        return f"{id_without_check}{check_code}"
        
    def calculate_check_code(self, id17):
        """计算身份证校验码"""
        # 加权因子
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        
        # 校验码对应值
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        # 根据前17位计算校验码
        sum = 0
        for i in range(17):
            sum += int(id17[i]) * factors[i]
            
        # 返回校验码
        return check_codes[sum % 11]
    
    def generate_data(self):
        """生成模拟数据"""
        # 创建Faker实例
        fake = Faker('zh_CN')
        
        # 生成身份证号
        id_card = self.generate_id_card()
        
        # 生成姓名
        name = fake.name()
        
        # 获取选择的省市区
        province = self.province_var.get()
        city = self.city_var.get()
        district = self.district_var.get()
        
        # 生成地址
        address = f"{province}{city}{district}" + fake.street_address()
        
        # 生成手机号
        phone = fake.phone_number()
        
        # 返回生成的数据
        return {
            "姓名": name,
            "性别": self.gender_var.get(),
            "身份证号": id_card,
            "出生日期": self.birth_date_var.get(),
            "地址": address,
            "手机号": phone
        }
    
    def add_generate_button(self, main_frame):
        """添加生成按钮"""
        # 创建数据量设置区域
        count_frame = ttk.Frame(main_frame)
        count_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        ttk.Label(count_frame, text="生成数据条数:").pack(side=tk.LEFT, padx=5)
        self.count_var = tk.StringVar(value="1")
        count_entry = ttk.Entry(count_frame, textvariable=self.count_var, width=10)
        count_entry.pack(side=tk.LEFT, padx=5)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        # 添加生成按钮，使用蓝色主题
        generate_button = tk.Button(button_frame, text="生成数据", command=self.on_generate,
                                  bg='#2196F3', fg='white', activebackground='#1976D2')
        generate_button.pack(side=tk.LEFT, padx=5)
        
        # 添加随机生成按钮，使用绿色主题
        random_generate_button = tk.Button(button_frame, text="随机生成", command=self.on_random_generate,
                                         bg='#4CAF50', fg='white', activebackground='#388E3C')
        random_generate_button.pack(side=tk.LEFT, padx=5)
        
        # 添加复制按钮
        copy_button = tk.Button(button_frame, text="复制", command=self.on_copy,
                               bg='#9C27B0', fg='white', activebackground='#7B1FA2')
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # 添加清空按钮
        clear_button = tk.Button(button_frame, text="清除", command=self.on_clear,
                                bg='#9E9E9E', fg='white', activebackground='#757575')
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 添加一键导出按钮，使用橙色主题
        export_all_button = tk.Button(button_frame, text="一键导出", command=self.on_export_all,
                                     bg='#FF9800', fg='white', activebackground='#F57C00')
        export_all_button.pack(side=tk.LEFT, padx=5)
        
        # 添加音乐播放按钮，放在一键导出按钮右侧
        self.play_button = tk.Button(button_frame, text="播放音乐", command=self.toggle_music,
                                   bg='#03A9F4', fg='white', activebackground='#0288D1')
        self.play_button.pack(side=tk.LEFT, padx=5)
    
    def on_generate(self):
        """生成按钮点击事件"""
        try:
            # 获取生成数量
            try:
                count = int(self.count_var.get())
                if count <= 0:
                    messagebox.showerror("错误", "请输入大于0的数值")
                    return
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
                return
                
            # 清空之前的数据
            self.data = []
            
            # 生成指定数量的数据
            for i in range(count):
                # 生成数据
                data = self.generate_data()
                
                # 添加到数据列表
                self.data.append(data)
            
            # 更新结果显示
            self.update_result_display()
            
            # 更新状态栏
            self.status_label.config(text=f"成功生成 {count} 条数据")
        except Exception as e:
            messagebox.showerror("生成错误", f"生成数据时出错: {str(e)}")
            self.status_label.config(text=f"错误: {str(e)}")
    
    def on_copy(self):
        """复制按钮点击事件"""
        if not self.data:
            messagebox.showinfo("提示", "没有数据可复制")
            return
            
        try:
            # 格式化所有数据为文本
            all_data_text = []
            for i, data in enumerate(self.data):
                # 添加数据序号
                data_text = f"===== 数据 {i+1} =====\n"
                # 添加数据内容
                data_text += "\n".join([f"{k}: {v}" for k, v in data.items()])
                all_data_text.append(data_text)
            
            # 将所有数据合并为一个文本，每条数据之间用空行分隔
            text = "\n\n".join(all_data_text)
            
            # 复制到剪贴板
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            
            # 更新状态栏
            self.status_label.config(text=f"已复制 {len(self.data)} 条数据到剪贴板")
        except Exception as e:
            messagebox.showerror("复制错误", f"复制数据时出错: {str(e)}")
    
    def on_clear(self):
        """清空按钮点击事件"""
        # 清空数据
        self.data = []
        
        # 更新结果显示
        self.update_result_display()
        
        # 更新状态栏
        self.status_label.config(text="数据已清空")
    
    def update_result_display(self):
        """更新结果显示"""
        # 如果没有创建结果显示区域，则创建
        if not hasattr(self, 'result_frame'):
            self.create_result_display()
            
        # 清空当前显示
        for widget in self.result_text.get_children():
            self.result_text.delete(widget)
            
        # 添加新数据
        for i, data in enumerate(self.data):
            self.result_text.insert("", "end", text=str(i+1), values=(
                data["姓名"],
                data["性别"],
                data["身份证号"],
                data["出生日期"],
                data["地址"],
                data["手机号"]
            ))
    
    def create_result_display(self):
        """创建结果显示区域"""
        # 创建结果框架
        self.result_frame = ttk.LabelFrame(self.window, text="生成结果", padding="10")
        self.result_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # 创建自定义样式用于表头加粗
        style = ttk.Style()
        style.configure("Bold.Treeview.Heading", font=("Arial", 9, "bold"))
        
        # 创建Treeview用于显示结果
        columns = ("姓名", "性别", "身份证号", "出生日期", "地址", "手机号")
        self.result_text = ttk.Treeview(self.result_frame, columns=columns, show="headings", style="Bold.Treeview")
        
        # 设置列标题
        for col in columns:
            # 设置标题和样式
            self.result_text.heading(col, text=col, anchor='center')
            self.result_text.tag_configure('row', font=('Arial', 9))
            
            # 根据内容类型设置列宽
            if col in ["姓名", "性别"]:
                self.result_text.column(col, width=80)
            elif col == "身份证号":
                self.result_text.column(col, width=150)
            elif col == "出生日期":
                self.result_text.column(col, width=100)
            elif col == "地址":
                self.result_text.column(col, width=250)
            else:
                self.result_text.column(col, width=120)
        
        # 创建滚动条框架
        scroll_frame = ttk.Frame(self.result_frame)
        scroll_frame.pack(side="right", fill="y")
        
        # 添加垂直滚动条
        y_scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=self.result_text.yview)
        y_scrollbar.pack(side="top", fill="y", expand=True)
        
        # 添加水平滚动条
        x_scrollbar = ttk.Scrollbar(self.result_frame, orient="horizontal", command=self.result_text.xview)
        x_scrollbar.pack(side="bottom", fill="x")
        
        # 配置Treeview的滚动条
        self.result_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # 放置Treeview控件
        self.result_text.pack(side="left", fill="both", expand=True)

    def run(self):
        """运行应用程序"""
        self.window.mainloop()

    def on_random_generate(self):
        """随机生成按钮点击事件"""
        try:
            # 获取生成数量
            try:
                count = int(self.count_var.get())
                if count <= 0:
                    messagebox.showerror("错误", "请输入大于0的数值")
                    return
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
                return
                
            # 清空之前的数据
            self.data = []
            
            # 使用Faker生成随机数据
            fake = Faker('zh_CN')
            
            # 生成指定数量的随机数据
            for i in range(count):
                # 生成随机数据
                data = {
                    "姓名": fake.name(),
                    "性别": random.choice(["男", "女"]),
                    "身份证号": self.generate_id_card(),
                    "出生日期": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y/%m/%d"),
                    "地址": fake.address(),
                    "手机号": fake.phone_number()
                }
                
                # 添加到数据列表
                self.data.append(data)
            
            # 更新结果显示
            self.update_result_display()
            
            # 更新状态栏
            self.status_label.config(text=f"成功生成 {count} 条随机数据")
        except Exception as e:
            messagebox.showerror("生成错误", f"生成随机数据时出错: {str(e)}")
            self.status_label.config(text=f"错误: {str(e)}")
    
    def on_export_all(self):
        """一键导出按钮点击事件"""
        if not self.data:
            messagebox.showinfo("提示", "没有数据可导出")
            return
            
        try:
            # 创建DataFrame
            df = pd.DataFrame(self.data)
            
            # 选择保存位置
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"身份证信息_{timestamp}.xlsx"
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
        except Exception as e:
            messagebox.showerror("导出错误", f"导出数据时出错: {str(e)}")
            self.status_label.config(text=f"错误: {str(e)}")
            
    def toggle_music(self):
        """播放/暂停背景音乐"""
        try:
            if not self.is_playing and not self.music_paused:
                # 尝试使用不同的方式加载音乐
                try:
                    # 首先尝试使用pygame的方式播放
                    pygame.mixer.quit()  # 先关闭之前的mixer
                    pygame.mixer.init(frequency=44100)  # 重新初始化，指定采样率
                    pygame.mixer.music.load(self.music_file)
                    pygame.mixer.music.play(-1)  # -1表示循环播放
                    self.is_playing = True
                except Exception as pygame_error:
                    # 如果pygame播放失败，尝试使用系统默认播放器播放
                    self.status_label.config(text=f"尝试使用系统播放器播放音乐...")
                    # 使用系统命令播放音乐文件
                    import subprocess
                    import threading
                    def play_with_system():
                        try:
                            if os.name == 'nt':  # Windows
                                os.startfile(self.music_file)
                            else:  # macOS 或 Linux
                                subprocess.call(['xdg-open', self.music_file])
                        except Exception as sys_error:
                            print(f"系统播放失败: {str(sys_error)}")
                    
                    # 在新线程中启动系统播放器
                    threading.Thread(target=play_with_system, daemon=True).start()
                    self.is_playing = True
                
                self.play_button.config(text="停止")
                self.status_label.config(text="正在播放背景音乐")
            else:
                # 停止播放
                try:
                    pygame.mixer.music.stop()
                except:
                    pass  # 忽略pygame停止错误
                
                self.is_playing = False
                self.music_paused = False
                self.play_button.config(text="播放音乐")
                self.status_label.config(text="背景音乐已停止")
        except Exception as e:
            messagebox.showerror("音乐播放错误", f"播放音乐时出错: {str(e)}")
            self.status_label.config(text=f"音乐播放错误: {str(e)}")

# 创建并运行应用程序
if __name__ == "__main__":
    app = MockDataGenerator()
    app.run()
