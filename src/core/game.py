import pygame

from src.core.settings import Settings
from src.core.assets import Assets
from src.core.scene_manager import SceneManager
from src.core.save import SaveManager

from src.scenes.boot import BootScene
from src.scenes.menu import MenuScene
from src.scenes.mode_select import ModeSelectScene
from src.scenes.map_select import MapSelectScene


class GameApp:
    def __init__(self):
        # ================= INIT =================
        pygame.init()

        try:
            pygame.mixer.init()
        except Exception as e:
            print("[WARN] Mixer init failed:", e)

        pygame.display.set_caption(Settings.TITLE)

        self.width = Settings.WIDTH
        self.height = Settings.HEIGHT

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )
        self.clock = pygame.time.Clock()
        self.running = True

        # ================= CORE SYSTEMS =================
        self.assets = Assets()

        self.save = SaveManager()
        self.save.load()

        # Runtime data (dùng xuyên scene)
        self.runtime = {
            "mode": 1,
            "map": None
        }

        # ================= THEME =================
        self.theme = {
            "btn": (70, 150, 210, 150),
            "btn_top": (160, 210, 245, 120),
            "btn_hover": (90, 170, 230, 170),
            "btn_disabled": (120, 120, 120, 120),

            "text": (240, 245, 250),
            "muted": (180, 200, 210),

            "stroke": (190, 225, 255, 160),
            "shadow": (0, 0, 0, 100),
        }

        # ================= SOUND (BẮT BUỘC) =================
        self.sound_on = True
        self.music_volume = 1.0

        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            pass

        # ================= SCENE MANAGER =================
        self.scenes = SceneManager(self)
        self.scenes.set_scene(BootScene(self))

    # ==================================================
    # SOUND CONTROL  ⭐⭐ QUAN TRỌNG ⭐⭐
    # ==================================================
    def set_sound(self, on: bool):
        self.sound_on = on
        try:
            pygame.mixer.music.set_volume(
                self.music_volume if on else 0.0
            )
        except Exception:
            pass

    def toggle_sound(self):
        self.set_sound(not self.sound_on)

    # ==================================================
    # BACK NAVIGATION
    # ==================================================
    def back(self):
        if not self.scenes.scene:
            self.quit()
            return

        scene_name = self.scenes.scene.__class__.__name__

        if scene_name == "GameScene":
            self.scenes.set_scene(MapSelectScene(self))
        elif scene_name == "MapSelectScene":
            self.scenes.set_scene(ModeSelectScene(self))
        elif scene_name == "ModeSelectScene":
            self.scenes.set_scene(MenuScene(self))
        else:
            self.quit()

    # ==================================================
    # QUIT GAME
    # ==================================================
    def quit(self):
        self.running = False

    # ==================================================
    # MAIN LOOP
    # ==================================================
    def run(self):
        while self.running:
            dt = self.clock.tick(Settings.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.scenes.handle_event(event)

            self.scenes.update(dt)
            self.scenes.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
