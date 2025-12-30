import pygame

class SceneManager:
    def __init__(self, app):
        self.app = app
        self.scene = None

        self._next_scene = None
        self._next_kwargs = {}

        # Fade transition
        self.fade_enabled = True
        self._fade_alpha = 0
        self._fade_state = "idle"   # idle | out | in
        self._fade_speed = 520      # alpha per second

        # overlay surface (reused)
        self._fade_surf = pygame.Surface((self.app.w, self.app.h)).convert()
        self._fade_surf.fill((0, 0, 0))

    def set_scene(self, scene, **kwargs):
        # ✅ nếu chưa có scene hoặc tắt fade -> vào thẳng
        if self.scene is None or not self.fade_enabled:
            self.scene = scene
            self.scene.on_enter(**kwargs)
            return

        # ✅ CHỐT CHỐNG TREO:
        # nếu đang fade (out/in) thì KHÔNG cho gọi set_scene tiếp
        # tránh reset alpha về 0 liên tục (kẹt Loading)
        if self._fade_state != "idle":
            return

        # có scene -> fade out rồi swap
        self._next_scene = scene
        self._next_kwargs = kwargs
        self._fade_state = "out"
        self._fade_alpha = 0

    def _swap_now(self):
        if self.scene:
            try:
                self.scene.on_exit()
            except Exception:
                pass

        self.scene = self._next_scene
        self._next_scene = None

        if self.scene:
            self.scene.on_enter(**self._next_kwargs)
        self._next_kwargs = {}

        self._fade_state = "in"
        self._fade_alpha = 255

    def handle_event(self, event):
        if self.scene:
            self.scene.handle_event(event)

    def update(self, dt):
        # update current scene
        if self.scene:
            self.scene.update(dt)

        # fade logic
        if not self.fade_enabled:
            return

        if self._fade_state == "out":
            self._fade_alpha += int(self._fade_speed * dt)
            if self._fade_alpha >= 255:
                self._fade_alpha = 255
                self._swap_now()

        elif self._fade_state == "in":
            self._fade_alpha -= int(self._fade_speed * dt)
            if self._fade_alpha <= 0:
                self._fade_alpha = 0
                self._fade_state = "idle"

    def draw(self, screen):
        if self.scene:
            self.scene.draw(screen)

        # draw fade overlay on top
        if self.fade_enabled and self._fade_state != "idle":
            self._fade_surf.set_alpha(self._fade_alpha)
            screen.blit(self._fade_surf, (0, 0))

    def replace_scene(self, scene):
        """
        Swap scene immediately WITHOUT calling on_enter (Pause -> Resume).
        Keeps current gameplay state.
        """
        self.scene = scene
        self._fade_state = "idle"
        self._fade_alpha = 0
        self._next_scene = None
        self._next_kwargs = {}
