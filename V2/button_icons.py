import base64
import io
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import ttk

# 创建彩色图标的函数
def create_colored_icon(text, bg_color, text_color='white', size=(20, 20)):
    """创建一个彩色图标
    
    Args:
        text: 图标中显示的文本
        bg_color: 背景颜色
        text_color: 文本颜色
        size: 图标大小
        
    Returns:
        PhotoImage对象
    """
    # 创建一个新图像
    img = Image.new('RGBA', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()
    
    # 计算文本位置使其居中
    # 使用font.getbbox代替过时的draw.textsize
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # 绘制文本
    draw.text(position, text, fill=text_color, font=font)
    
    # 转换为PhotoImage
    photo_image = tk.PhotoImage(data=image_to_data(img))
    return photo_image

def image_to_data(img):
    """将PIL图像转换为base64编码的数据"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue())

# 预定义的图标
def get_copy_icon():
    """获取复制按钮的图标"""
    return create_colored_icon('复制', '#4CAF50', size=(40, 20))  # 绿色背景

def get_clear_icon():
    """获取清除按钮的图标"""
    return create_colored_icon('清除', '#F44336', size=(40, 20))  # 红色背景