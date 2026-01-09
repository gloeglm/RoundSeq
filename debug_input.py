"""Debug script to check Kivy input providers."""
import os

# Print environment
print("=== Environment ===")
print(f"User: {os.getuid()}")
print(f"Groups: {os.getgroups()}")

# Check device permissions
print("\n=== Input Devices ===")
for i in range(10):
    dev = f"/dev/input/event{i}"
    if os.path.exists(dev):
        readable = os.access(dev, os.R_OK)
        print(f"{dev}: readable={readable}")

# Now start Kivy
print("\n=== Starting Kivy ===")
from kivy.config import Config
print(f"Input config: {Config.items('input')}")

from kivy.base import EventLoop
EventLoop.ensure_window()

print(f"\n=== Input Providers ===")
for provider in EventLoop.input_providers:
    print(f"  {provider}")

print("\n=== Running App ===")
from kivy.app import App
from kivy.uix.label import Label


class DebugApp(App):
    def build(self):
        from kivy.core.window import Window
        print(f"Window size: {Window.size}")
        self.label = Label(text='Touch anywhere\nWaiting...', font_size=40)

        # Bind to window touch events directly
        Window.bind(on_touch_down=self.window_touch)
        return self.label

    def window_touch(self, window, touch):
        msg = 'WINDOW TOUCH: x={:.0f} y={:.0f}'.format(touch.x, touch.y)
        print(msg)
        self.label.text = msg
        return False  # Don't consume, let it propagate

    def on_touch_down(self, touch):
        msg = 'APP TOUCH: x={:.0f} y={:.0f}'.format(touch.x, touch.y)
        print(msg)
        self.label.text = msg
        return True


DebugApp().run()
