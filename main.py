import arcade
import random
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # This gets the folder containing main.py
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Five Nights At Fera's"

class FerasGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)

        # 1. Camera Nodes and Names
        self.cam_nodes = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
        self.cam_names = {
            "01": "Stage", "02": "Dining Area", "03": "Left Hall",
            "04": "Right Hall", "05": "Backstage", "06": "Left Door",
            "07": "Right Door", "08": "Kitchen", "09": "Outdoors"
        }
        self.current_index = 0
        self.camera_up = False

        # 2. AI Setup
        self.bunny_location = "01"
        self.ai_timer = 0.0
        self.ai_interval = 5.0

        # 3. UI Setup
        self.ui_text = arcade.Text("", 20, 20, arcade.color.LIME_GREEN,
                                   font_size=25, anchor_x="left", anchor_y="bottom",
                                   font_name="Arial")

        self.heartbeat_text = arcade.Text("", SCREEN_WIDTH - 20, 20, arcade.color.RED,
                                          font_size=20, anchor_x="right", anchor_y="bottom",
                                          font_name="Arial")

        self.office_text = arcade.Text("OFFICE VIEW", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                       arcade.color.WHITE, 30, anchor_x="center",
                                       font_name="Arial")

        self.typing_mode = False
        self.input_buffer = ""
        self.cursor_timer = 0.0
        self.cursor_visible = True
        self.static_alpha = 100

        # Audio Setup - FIXED PATHS
        # Use os.path.join inside the resource_path call
        self.crt_hum = arcade.load_sound(resource_path(os.path.join("assets", "crt_hum.wav")))
        self.hum_player = None

    def on_draw(self):
        self.clear()

        if not self.camera_up:
            self.office_text.draw()  # Performance Fix
        else:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)

            current_cam = self.cam_nodes[self.current_index]
            cam_name = self.cam_names.get(current_cam, "Unknown")

            if self.typing_mode:
                cursor = "_" if self.cursor_visible else " "
                self.ui_text.text = f"DIAL: {self.input_buffer}{cursor}"
                self.ui_text.x, self.ui_text.y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                self.ui_text.anchor_x = "center"
            else:
                self.ui_text.text = f"{current_cam} - {cam_name}"
                self.ui_text.x, self.ui_text.y = 20, 20
                self.ui_text.anchor_x = "left"

            self.ui_text.draw()

            npc_count = 1 if self.bunny_location == current_cam else 0
            self.heartbeat_text.text = f"Heart beats in this room: {npc_count}"
            self.heartbeat_text.draw()

            # CRT Snow
            for _ in range(150):
                x, y = random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT)
                c = random.randint(150, 255)
                arcade.draw_point(x, y, [c, c, c, 180], 2)

    def on_update(self, delta_time):
        self.cursor_timer += delta_time
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0

        self.ai_timer += delta_time
        if self.ai_timer >= self.ai_interval:
            self.ai_timer = 0.0
            self.move_bunny()

        # AUDIO RAMP LOGIC
        if self.camera_up and self.hum_player:
            if self.hum_player.volume > 0.2:
                self.hum_player.volume -= delta_time * 2.0
            else:
                self.hum_player.volume = 0.2

    def move_bunny(self):
        paths = {
            "01": ["02","02", "05"],
            "02": ["03", "04", "08", "09"],
            "03": ["06"], "04": ["07"], "05": ["01"],
            "06": ["01"], "07": ["01"], "08": ["02"], "09": ["02"]
        }
        possible_moves = paths.get(self.bunny_location, ["01"])
        self.bunny_location = random.choice(possible_moves)
        print(f"AI: Bunny moved to {self.bunny_location}")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.camera_up = not self.camera_up
            self.typing_mode = False
            if self.camera_up:
                # Fix: looping -> loop (per Arcade docs)
                self.hum_player = arcade.play_sound(self.crt_hum, volume=1.0, loop=True)
            else:
                if self.hum_player:
                    arcade.stop_sound(self.hum_player)
            return

        if key == arcade.key.K and self.camera_up:
            self.typing_mode = True
            self.input_buffer = ""
            return

        if self.typing_mode:
            if key == arcade.key.ENTER:
                self.process_dial_in()
                self.typing_mode = False
            elif key == arcade.key.BACKSPACE:
                self.input_buffer = self.input_buffer[:-1]
            elif (arcade.key.KEY_0 <= key <= arcade.key.KEY_9) or (arcade.key.A <= key <= arcade.key.Z):
                self.input_buffer += chr(key).upper()
            return

        if self.camera_up:
            if key == arcade.key.RIGHT or key == arcade.key.LEFT:
                if key == arcade.key.RIGHT:
                    self.current_index = (self.current_index + 1) % len(self.cam_nodes)
                else:
                    self.current_index = (self.current_index - 1) % len(self.cam_nodes)
                # --- THE CALIBRATION KICK ---
                if self.hum_player:
                    self.hum_player.volume = 1.0

    def process_dial_in(self):
        name_map = {v.upper(): k for k, v in self.cam_names.items()}
        target = self.input_buffer.strip().upper()
        if target == "RANDOM":
            self.current_index = random.randrange(len(self.cam_nodes))
            return
        if target.isdigit() and len(target) == 1:
            target = f"0{target}"
        if target in self.cam_nodes:
            self.current_index = self.cam_nodes.index(target)
        elif target in name_map:
            self.current_index = self.cam_nodes.index(name_map[target])

def main():
    window = FerasGame()
    arcade.run()

if __name__ == "__main__":
    main()