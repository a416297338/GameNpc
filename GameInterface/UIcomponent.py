import arcade
import time
from PIL import Image, ImageDraw, ImageFont


class DialogueBox:
    def __init__(self, image_path, font_size=14):
        self.texture = arcade.load_texture(image_path)
        self.text = None
        self.end_time = 0
        self.font_size = font_size
        self.down_flag = False
        self.text_texture = None

    def setup(self):
        # 创建一个文本纹理,只需要创建一次
        self.text_texture = self.create_text_texture("Hello, Arcade!", 24, arcade.color.WHITE)

    def create_text_texture(self, text, color, font_size, max_width=200):
        # 使用 PIL 创建一个图像
        font = ImageFont.truetype("msyh.ttc", font_size)

        # 分割文本为多行
        lines = []
        current_line = ""

        for char in text:
            test_line = current_line + char
            test_width, _ = font.getsize(test_line)

            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        # 计算文本的总高度
        text_height = font.getsize(text)[1] * len(lines)

        # 创建图像
        image = Image.new("RGBA", (max_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 绘制每一行文本
        y = 0
        for line in lines:
            draw.text((0, y), line, font=font, fill=color)
            y += font.getsize(line)[1]

        # 将 PIL 图像转换为 arcade 纹理
        texture = arcade.Texture(text)
        texture.image = image
        return texture

    def set_text(self, text, duration_time=100, down_flag=False):
        if self.text != text:
            self.text_texture = self.create_text_texture(text, arcade.color.BLACK, 14)
        self.text = text
        self.end_time = time.time() + duration_time
        self.down_flag = down_flag

    def draw(self, center_x, center_y):
        # 绘制对话框
        center_x += 48
        center_y += 48
        now_time = time.time()
        if self.texture and now_time < self.end_time:
            width = 300
            height = 200
            arcade.draw_texture_rectangle(center_x, center_y, width, height, self.texture)
            # 创建文本对象
            text_x = center_x
            text_y = center_y - self.text_texture.height // 2 + 30
            arcade.draw_texture_rectangle(text_x, text_y,
                                          self.text_texture.width, self.text_texture.height,
                                          self.text_texture)
