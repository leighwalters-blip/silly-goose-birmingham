"""On-screen touch controls for mobile play."""
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


# Button layout
_BTN_RADIUS = 32
_BTN_ALPHA = 90
_BTN_PRESSED_ALPHA = 150
_MARGIN = 20

# Button positions (x, y)
_BUTTONS = {
    "left":  (_MARGIN + _BTN_RADIUS, SCREEN_HEIGHT - _MARGIN - _BTN_RADIUS),
    "right": (_MARGIN + _BTN_RADIUS * 3 + 20, SCREEN_HEIGHT - _MARGIN - _BTN_RADIUS),
    "jump":  (SCREEN_WIDTH - _MARGIN - _BTN_RADIUS, SCREEN_HEIGHT - _MARGIN - _BTN_RADIUS),
    "hit":   (SCREEN_WIDTH - _MARGIN - _BTN_RADIUS * 3 - 20, SCREEN_HEIGHT - _MARGIN - _BTN_RADIUS),
    "enter": (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100),
}

# Colors
_BTN_COLOR = (255, 255, 255)
_ARROW_COLOR = (40, 40, 40)
_LABEL_COLOR = (40, 40, 40)


class TouchControls:
    """Draws virtual buttons and tracks touch state."""

    def __init__(self):
        self.pressed = set()       # currently held buttons
        self.just_pressed = set()  # pressed this frame
        self.active_touches = {}   # finger_id -> button_name
        self._font = None
        self._touched = False      # has user ever touched the screen
        self.show_enter = False    # set by game to control which buttons show

    def _get_font(self):
        if self._font is None:
            pygame.font.init()
            self._font = pygame.font.SysFont("Arial", 18, bold=True)
        return self._font

    def _hit_test(self, x, y):
        """Return which button (if any) is at screen position x, y."""
        for name, (bx, by) in _BUTTONS.items():
            # Skip buttons not currently shown
            if name == "enter" and not self.show_enter:
                continue
            if name != "enter" and self.show_enter:
                continue
            radius = 50 if name == "enter" else _BTN_RADIUS
            dx = x - bx
            dy = y - by
            if dx * dx + dy * dy <= (radius + 10) ** 2:
                return name
        # On menu screens, any tap anywhere counts as enter
        if self.show_enter:
            return "enter"
        return None

    def update(self, events):
        """Process touch/mouse events and return button states."""
        self.just_pressed.clear()

        for event in events:
            # Mouse events (also how Pygbag delivers single touches)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._touched = True
                btn = self._hit_test(event.pos[0], event.pos[1])
                if btn:
                    if btn not in self.pressed:
                        self.just_pressed.add(btn)
                    self.pressed.add(btn)
                    self.active_touches["mouse"] = btn

            elif event.type == pygame.MOUSEBUTTONUP:
                old_btn = self.active_touches.pop("mouse", None)
                if old_btn:
                    self.pressed.discard(old_btn)

            elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                # Drag between buttons
                btn = self._hit_test(event.pos[0], event.pos[1])
                old_btn = self.active_touches.get("mouse")
                if btn != old_btn:
                    if old_btn:
                        self.pressed.discard(old_btn)
                    if btn:
                        if btn not in self.pressed:
                            self.just_pressed.add(btn)
                        self.pressed.add(btn)
                    self.active_touches["mouse"] = btn

            # Multi-touch finger events
            elif event.type == pygame.FINGERDOWN:
                self._touched = True
                sx = event.x * SCREEN_WIDTH
                sy = event.y * SCREEN_HEIGHT
                btn = self._hit_test(sx, sy)
                if btn:
                    if btn not in self.pressed:
                        self.just_pressed.add(btn)
                    self.pressed.add(btn)
                    self.active_touches[event.finger_id] = btn

            elif event.type == pygame.FINGERUP:
                old_btn = self.active_touches.pop(event.finger_id, None)
                if old_btn:
                    # Only release if no other finger is on same button
                    if old_btn not in self.active_touches.values():
                        self.pressed.discard(old_btn)

            elif event.type == pygame.FINGERMOTION:
                sx = event.x * SCREEN_WIDTH
                sy = event.y * SCREEN_HEIGHT
                btn = self._hit_test(sx, sy)
                old_btn = self.active_touches.get(event.finger_id)
                if btn != old_btn:
                    if old_btn:
                        if old_btn not in [v for k, v in self.active_touches.items()
                                           if k != event.finger_id]:
                            self.pressed.discard(old_btn)
                    if btn:
                        if btn not in self.pressed:
                            self.just_pressed.add(btn)
                        self.pressed.add(btn)
                    self.active_touches[event.finger_id] = btn

    def draw(self, surface, show_enter=False):
        """Draw touch buttons. START always shows on menus; game buttons after first touch."""
        self.show_enter = show_enter

        for name, (bx, by) in _BUTTONS.items():
            # Only show enter button on menu/gameover screens
            if name == "enter" and not show_enter:
                continue
            # Hide dpad/action buttons on menu screens
            if name != "enter" and show_enter:
                continue
            # Game buttons only appear after user has touched the screen
            if name != "enter" and not self._touched:
                continue

            is_pressed = name in self.pressed
            alpha = _BTN_PRESSED_ALPHA if is_pressed else _BTN_ALPHA
            radius = _BTN_RADIUS if name != "enter" else 50  # bigger START button

            # Draw button circle
            sz = radius * 2 + 4
            btn_surf = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.circle(btn_surf, (*_BTN_COLOR, alpha),
                               (radius + 2, radius + 2), radius)
            pygame.draw.circle(btn_surf, (*_BTN_COLOR, min(255, alpha + 60)),
                               (radius + 2, radius + 2), radius, 2)
            surface.blit(btn_surf, (bx - radius - 2, by - radius - 2))

            # Draw icon/label
            cx, cy = bx, by
            if name == "left":
                pts = [(cx + 8, cy - 10), (cx - 8, cy), (cx + 8, cy + 10)]
                pygame.draw.polygon(surface, _ARROW_COLOR, pts)
            elif name == "right":
                pts = [(cx - 8, cy - 10), (cx + 8, cy), (cx - 8, cy + 10)]
                pygame.draw.polygon(surface, _ARROW_COLOR, pts)
            elif name == "jump":
                pts = [(cx - 10, cy + 6), (cx, cy - 10), (cx + 10, cy + 6)]
                pygame.draw.polygon(surface, _ARROW_COLOR, pts)
            elif name == "hit":
                font = self._get_font()
                label = font.render("HIT", True, _ARROW_COLOR)
                rect = label.get_rect(center=(cx, cy))
                surface.blit(label, rect)
            elif name == "enter":
                font = self._get_font()
                label = font.render("TAP TO START", True, _ARROW_COLOR)
                rect = label.get_rect(center=(cx, cy))
                surface.blit(label, rect)
