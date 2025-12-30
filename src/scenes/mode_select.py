import pygame
from src.core.scene import Scene
from src.ui.button import Button
from src.scenes.map_select import MapSelectScene

class ModeSelectScene(Scene):
    def on_enter(self, **kwargs):
        self.h1 = self.app.assets.font(None, 46)
        self.btn_font = self.app.assets.font(None, 26)
        cx = self.app.w // 2
        y0 = 320
        theme = self.app.theme

        self.buttons = [
            Button((cx-220, y0,     440, 64), "1 PLAYER", lambda: self._pick(1), self.btn_font, theme),
            Button((cx-220, y0+90,  440, 64), "2 PLAYERS",lambda: self._pick(2), self.btn_font, theme),
            Button((cx-220, y0+190, 440, 56), "BACK", self.app.back, self.btn_font, theme),
        ]

    def _pick(self, mode: int):
        self.app.runtime["mode"] = mode
        self.app.scenes.set_scene(MapSelectScene(self.app))

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, screen):
        screen.fill((6, 22, 44))
        t = self.h1.render("Select Mode", True, self.app.theme["text"])
        screen.blit(t, t.get_rect(center=(self.app.w//2, 220)))
        for b in self.buttons:
            b.draw(screen)
