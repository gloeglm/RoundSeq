from kivy.app import App
from kivy.uix.label import Label


class TestApp(App):
    def build(self):
        self.label = Label(text='Touch me!', font_size=50)
        return self.label

    def on_touch_down(self, touch):
        self.label.text = f'Touch: {touch.x:.0f}, {touch.y:.0f}'
        print(f'Touch: {touch.x}, {touch.y}')
        return True


if __name__ == '__main__':
    TestApp().run()
