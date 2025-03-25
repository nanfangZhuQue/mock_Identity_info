import base64
import io
from PIL import Image

# 使用logo.py中的base64编码数据
from logo import logo_data

def create_icon():
    try:
        # 解码base64数据
        image_data = base64.b64decode(logo_data)
        image = Image.open(io.BytesIO(image_data))
        
        # 创建不同尺寸的图标
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)]
        icon_images = []
        
        for size in sizes:
            resized_img = image.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized_img)
        
        # 保存为.ico文件
        icon_path = '3.13.ico'
        icon_images[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in icon_images], 
                          append_images=icon_images[1:])
        
        print(f"图标已创建: {icon_path}")
        return icon_path
    except Exception as e:
        print(f"创建图标时出错: {str(e)}")
        return None

if __name__ == "__main__":
    create_icon()