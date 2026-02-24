import arcade
import random
import os
import sys
import time


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Five Nights At Fera's"

STATIC_MIN = 0.2   # resting transparency
STATIC_MAX = 1.0   # shock peak on cam change
STATIC_FADE = 1.5  # how fast it fades back down (per second)


class FerasGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)

        # Camera setup
        self.cam_nodes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
        self.cam_names = {
            "01": "Stage", "02": "Dining Area", "03": "Left Hall",
            "04": "Right Hall", "05": "Backstage", "06": "Left Door",
            "07": "Right Door", "08": "Kitchen", "09": "Jay's curtain", "10": "Outdoors",
            "11": "Cleaning Closet", "12": "????"
        }

        self.ai_levels = {"Fera": 2, "Jason": 0, "May": 2, "Jay": 0}
        self.locations = {
            "Fera": "01",
            "Jason": "01",
            "May": "01",
            "Jay": "09"
        }

        self.current_index = 0
        self.camera_up = False
        self.game_over = False
        self.won = False
        self.null_triggered = False

        self.ai_timer = 0.0
        self.ai_interval = 5.0

        self.ui_text = arcade.Text("", 20, 20, arcade.color.LIME_GREEN, font_size=25, font_name="Arial")
        self.heartbeat_text = arcade.Text("", SCREEN_WIDTH - 20, 20, arcade.color.RED, font_size=20, anchor_x="right",
                                          font_name="Arial")
        self.power_text = arcade.Text("", 20, 60, arcade.color.LIME_GREEN, font_size=18, font_name="Arial")
        self.clock_text = arcade.Text("", 20, 90, arcade.color.LIME_GREEN, font_size=18, font_name="Arial")
        self.center_text = arcade.Text("", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.WHITE, 50,
                                       anchor_x="center", anchor_y="center", font_name="Arial", multiline=True,
                                       width=SCREEN_WIDTH, align="center")

        self.typing_mode = False
        self.input_buffer = ""
        self.cursor_timer = 0.0
        self.cursor_visible = True

        # Sounds
        self.crt_hum = arcade.load_sound(resource_path(os.path.join("assets", "crt_hum.wav")))
        self.hum_player = None

        self.power = 100.0
        self.game_hour = 6
        self.game_timer = 0.0

        # Static effect state
        self.static_timer = 0.0
        self.glitch_offset = 0
        self.glitch_y = 0
        self.glitch_height = 0

        # Static opacity: 0.0 - 1.0, starts at resting level
        self.static_alpha = STATIC_MIN

    def shock_static(self):
        """ Call this whenever cams change — slams static to full then it fades back """
        self.static_alpha = STATIC_MAX

    def check_null_spawn(self):
        if random.randint(1, 420) == 1:
            self.trigger_null_crash()

    def trigger_null_crash(self):
        self.null_triggered = True
        print("CRITICAL ERROR: NULL INTERCEPTED CAMERA FEED.")
        if self.hum_player:
            arcade.stop_sound(self.hum_player)
        arcade.schedule(lambda dt: sys.exit(), 2.0)

    def draw_static(self):
        """
        Heavy CRT static effect, scaled by self.static_alpha (0.2 resting, 1.0 on shock).
        - Full horizontal scanline bars of noise
        - A random glitch band that shifts sideways like a VHS tape
        - Dark vignette on the edges
        - Occasional full-screen white flash
        """
        a = self.static_alpha  # shorthand, 0.0 - 1.0

        # SCANLINE NOISE BARS
        bar_height = 3
        for y in range(0, SCREEN_HEIGHT, bar_height):
            c = random.randint(80, 220)
            alpha = int(random.randint(120, 220) * a)
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, y, y + bar_height, (c, c, c, alpha))

        # GLITCH BAND
        if self.glitch_height > 0:
            band_top = self.glitch_y + self.glitch_height
            arcade.draw_lrbt_rectangle_filled(
                self.glitch_offset, SCREEN_WIDTH + self.glitch_offset,
                self.glitch_y, band_top,
                (200, 200, 200, int(180 * a))
            )
            core_c = random.randint(200, 255)
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH,
                self.glitch_y + self.glitch_height // 3,
                band_top - self.glitch_height // 3,
                (core_c, core_c, core_c, int(230 * a))
            )

        # VIGNETTE — always at full strength regardless of static alpha
        edge = 80
        arcade.draw_lrbt_rectangle_filled(0, edge, 0, SCREEN_HEIGHT, (0, 0, 0, 160))
        arcade.draw_lrbt_rectangle_filled(SCREEN_WIDTH - edge, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 160))
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, edge, (0, 0, 0, 160))
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT - edge, SCREEN_HEIGHT, (0, 0, 0, 160))

        # RARE FULL-SCREEN FLASH — only really visible during shock
        if random.randint(1, 60) == 1:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                                              (255, 255, 255, int(random.randint(30, 80) * a)))

    def on_draw(self):
        self.clear()

        if self.null_triggered:
            return

        if self.won:
            self.center_text.text = "SHIFT COMPLETE\nYOU SURVIVED"
            self.center_text.draw()
            return

        if not self.camera_up:
            arcade.Text("OFFICE VIEW", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                        arcade.color.GRAY, 30, anchor_x="center").draw()
        else:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)

            current_cam = self.cam_nodes[self.current_index]
            cam_name = self.cam_names.get(current_cam, "Unknown")

            self.draw_static()

            if self.typing_mode:
                cursor = "_" if self.cursor_visible else " "
                self.ui_text.text = f"DIAL: {self.input_buffer}{cursor}"
                self.ui_text.x, self.ui_text.y, self.ui_text.anchor_x = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "center"
            else:
                self.ui_text.text = f"{current_cam} - {cam_name}"
                self.ui_text.x, self.ui_text.y, self.ui_text.anchor_x = 20, 20, "left"

            self.ui_text.draw()

            npc_count = sum(1 for loc in self.locations.values() if loc == current_cam)
            self.heartbeat_text.text = f"Heart beats in this room: {npc_count}"
            self.heartbeat_text.draw()

            self.power_text.text = f"POWER: {int(self.power)}%"
            display_hour = 12 if self.game_hour % 12 == 0 else self.game_hour % 12
            am_pm = "AM" if self.game_hour < 12 else "PM"
            self.clock_text.text = f"TIME: {display_hour:02}:{int(self.game_timer):02} {am_pm}"

            self.power_text.draw()
            self.clock_text.draw()

    def on_update(self, delta_time):
        if self.won or self.game_over or self.null_triggered:
            return

        # Fade static alpha back down to resting level
        if self.static_alpha > STATIC_MIN:
            self.static_alpha -= STATIC_FADE * delta_time
            if self.static_alpha < STATIC_MIN:
                self.static_alpha = STATIC_MIN

        # Update glitch band every ~0.1s
        self.static_timer += delta_time
        if self.static_timer >= 0.1:
            self.static_timer = 0.0
            self.glitch_y = random.randint(0, SCREEN_HEIGHT - 60)
            self.glitch_height = random.randint(0, 80)
            self.glitch_offset = random.randint(-40, 40)

        self.cursor_timer += delta_time
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0

        self.ai_timer += delta_time
        if self.ai_timer >= self.ai_interval:
            self.ai_timer = 0.0
            for name, level in self.ai_levels.items():
                if level > 0 and random.randint(1, 20) <= level:
                    self.move_character(name)

        if self.camera_up and self.hum_player:
            if self.hum_player.volume > 0.2:
                self.hum_player.volume -= delta_time * 2.0

        self.game_timer += delta_time
        if self.game_timer >= 60.0:
            self.game_timer = 0.0
            self.game_hour += 1

        current_am_pm = "AM" if self.game_hour < 12 else "PM"
        if self.game_hour == 12 and current_am_pm == "PM":
            self.won = True
            if self.hum_player:
                arcade.stop_sound(self.hum_player)

        if self.camera_up:
            self.power -= delta_time * 0.2
            if self.power <= 0:
                self.power = 0
                self.camera_up = False
                if self.hum_player:
                    arcade.stop_sound(self.hum_player)
        else:
            if self.power < 100:
                self.power += delta_time * 0.0166

    def move_character(self, name):
        paths = {
            "01": ["02", "05"], "02": ["03", "04", "08", "09", "10"],
            "03": ["06"], "04": ["07"], "05": ["01"],
            "06": ["01"], "07": ["01"], "08": ["02"], "10": ["02"]
        }
        current_loc = self.locations[name]
        possible_moves = paths.get(current_loc, ["01"])
        self.locations[name] = random.choice(possible_moves)
        print(f"DEBUG: {name} moved to {self.locations[name]}")

    def on_key_press(self, key, modifiers):
        required_mods = arcade.key.MOD_CTRL | arcade.key.MOD_ALT | arcade.key.MOD_SHIFT
        if key == arcade.key.W and (modifiers & required_mods) == required_mods:
            self.game_hour = 12
            return

        if self.won: return

        if key == arcade.key.SPACE:
            if not self.camera_up and self.power > 0:
                self.camera_up = True
                self.shock_static()  # shock on camera open
                self.hum_player = arcade.play_sound(self.crt_hum, volume=1.0, loop=True)
            else:
                self.camera_up = False
                if self.hum_player:
                    arcade.stop_sound(self.hum_player)
            self.typing_mode = False
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

                self.shock_static()  # VHMmmm effect on every cam change
                self.check_null_spawn()

                if self.hum_player:
                    self.hum_player.volume = 1.0

    def process_dial_in(self):
        name_map = {v.upper(): k for k, v in self.cam_names.items()}
        target = self.input_buffer.strip().upper()

        if target == "RANDOM":
            self.current_index = random.randrange(len(self.cam_nodes))
            self.shock_static()  # shock on dial-in too
            self.check_null_spawn()
        elif target in self.cam_nodes or target in name_map:
            final_code = target if target in self.cam_nodes else name_map[target]
            self.current_index = self.cam_nodes.index(final_code)
            self.shock_static()  # shock on dial-in too
            self.check_null_spawn()


def main():
    game = FerasGame()
    arcade.run()


if __name__ == "__main__":
    main()