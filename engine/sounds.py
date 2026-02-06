"""Sound effects - uses JS Web Audio API in browser, pygame.mixer natively."""
import os
import sys

_use_js = False
_cache = {}

try:
    import platform as _platform
    if hasattr(_platform, 'window'):
        _use_js = True
except Exception:
    pass

if not _use_js:
    import pygame
    _sound_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds")


def play(name):
    """Play a named sound effect."""
    if _use_js:
        try:
            import platform as _plat
            _plat.window.playGameSound(name)
        except Exception:
            pass
        return

    # Native pygame fallback
    if name not in _cache:
        path = os.path.join(_sound_dir, f"{name}.wav")
        try:
            _cache[name] = pygame.mixer.Sound(path)
        except Exception:
            _cache[name] = None
    snd = _cache[name]
    if snd:
        snd.play()
