import arcade

# 常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Sheet Animation Example"


# 角色类
class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # 加载 sprite sheet
        self.textures = arcade.load_spritesheet(
            "map_assets/cute_rpg_word_VXAce/characters/!Character_RM_001.png",  # 替换为你的 sprite sheet 路径
            sprite_width=48,  # 每个帧的宽度
            sprite_height=48,  # 每个帧的高度
            columns=12,  # sprite sheet 中的列数
            count=48  # 总帧数
        )
        self.highLight = [0, 3, 6, 9]
        self.moveForward = {"down":0, "left":12, "right":24, "up":36}
        self.moveState = "down"
        # 设置初始帧
        self.current_frame = 0
        self.speed = 5
        self.set_texture(self.current_frame)

    def update_animation(self, delta_time: float = 1 / 60):
        # 更新帧
        self.current_frame += 1
        isMove = self.change_x !=0 or self.change_y !=0
        self.set_texture(self.get_frame_index(self.moveState) + self.current_frame%3 if isMove else 1)

    def get_frame_index(self, direction, highlight=0):
        return self.moveForward[direction] + self.highLight[highlight]

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

    def move_left(self):
        self.moveState = "left"
        self.set_texture(self.get_frame_index("left"))
        self.change_x = -self.speed

    def move_right(self):
        self.moveState = "right"
        self.change_x = self.speed

    def move_up(self):
        self.moveState = "up"
        self.change_y = self.speed

    def move_down(self):
        self.moveState = "down"
        self.change_y = -self.speed

    def stop(self):
        self.change_x = 0
        self.change_y = 0


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player = None

    def setup(self):
        self.player = Player()
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2

    def on_draw(self):
        arcade.start_render()
        self.player.draw()

    def update(self, delta_time):
        self.player.update_animation(delta_time)


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()