# 掼蛋助手 Android图标和资源
# 
# 图标要求：
# - icon.png: 应用图标 (推荐尺寸 512x512 或 256x256)
# - presplash.png: 启动画面 (推荐尺寸 1080x1920)
#
# 可以使用以下Python脚本生成简单图标：

"""
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    # 创建512x512的图标
    img = Image.new('RGB', (512, 512), color='#2E7D32')
    draw = ImageDraw.Draw(img)
    
    # 画一个扑克牌形状
    # 背景圆角矩形
    draw.rounded_rectangle([50, 50, 462, 462], radius=40, fill='#FFFFFF')
    
    # 绘制文字 "掼"
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 200)
    except:
        font = ImageFont.load_default()
    
    # 绘制红色"掼"字
    draw.text((160, 130), '掼', fill='#E53935', font=font)
    draw.text((160, 280), '蛋', fill='#1565C0', font=font)
    
    img.save('res/drawable/icon.png')
    print("图标已生成: res/drawable/icon.png")

def create_presplash():
    # 创建启动画面
    img = Image.new('RGB', (1080, 1920), color='#1B5E20')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 120)
    except:
        font = ImageFont.load_default()
    
    # 居中文字
    text = '掼蛋记牌器'
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (1080 - text_width) // 2
    
    draw.text((x, 800), text, fill='#FFFFFF', font=font)
    
    img.save('res/drawable/presplash.png')
    print("启动画面已生成: res/drawable/presplash.png")

if __name__ == '__main__':
    create_icon()
    create_presplash()
"""

# 或者使用在线图标生成器：
# 1. https://icon.kitchen/
# 2. https://appicon.co/
# 3. https://iconifier.net/

# 将生成的图标放入 res/drawable/ 目录
