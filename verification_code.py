import io
import os
import random
from django.conf import settings
from PIL import Image, ImageFont, ImageDraw, ImageFilter


def get_verify_image():
    """
    创建图像并返回结果
    :return: 
    """
    code_size = (120, 30)
    # 随机获取一个字体
    fonts_location = settings.STATIC_ROOT + "/fonts/"
    fonts = os.listdir(fonts_location)
    font = ImageFont.truetype(fonts_location + random.choice(fonts), 25)
    # 创建400x50的画布
    image = Image.new("RGBA", code_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    # 绘制干扰点
    chance = min(100, max(0, 3))
    for w in range(code_size[0]):
        for h in range(code_size[1]):
            tmp = random.randint(0, 100)
            if tmp > 100 - chance:
                draw.point((w, h), fill=(0, 0, 0))

    # 产生答案
    (random_text, random_answer) = random_produce_code()
    # 将返回结果画在画布上
    draw.text((0, 0), random_text, font=font, fill="#000000")
    # 扭曲图像
    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    image = image.transform(code_size, Image.PERSPECTIVE, params)
    # 滤镜，边界加强（阈值更大）
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    # 创建一个字节流用于保存图标
    data = io.BytesIO()
    image.save(data, format="PNG")
    # 将内存数据直接返回
    data.seek(0)
    return data.getvalue(), random_answer


def random_produce_code():
    """
    随机生成验证码
    :return: 
    """
    # 随机选择运算
    operator = random.choice(["+", "-", "x"])
    # 对于乘法选较小的数
    if operator == "x":
        num1 = random.randint(0, 10)
        num2 = random.randint(0, 10)
        # 保存计算结果到session中
        code_answer = num1 * num2
    else:
        num1 = random.randint(20, 40)
        num2 = random.randint(0, 20)
        if operator == "+":
            code_answer = num1 + num2
        else:
            code_answer = num1 - num2
    return str(num1) + operator + str(num2) + "=?", code_answer
