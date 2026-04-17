"""
掼蛋实时助手 - 最小测试版
用于验证APK基础功能
"""
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.config import Config

# 设置中文字体
Config.set('kivy', 'default_font', ['DroidSansFallback', 'NotoSansCJK', 'Roboto'])


class GuandanTestApp(App):
    """测试应用"""
    
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title = Label(
            text='掼蛋实时助手 v1.0',
            font_size='24sp',
            size_hint_y=0.3
        )
        
        # 状态
        status = Label(
            text='APK基础功能测试成功！\n\n如果看到此界面，说明Kivy环境正常。\n\n点击下方按钮退出。',
            font_size='16sp',
            size_hint_y=0.5
        )
        
        # 退出按钮
        btn = Button(
            text='退出',
            size_hint_y=0.2
        )
        btn.bind(on_press=self.stop)
        
        layout.add_widget(title)
        layout.add_widget(status)
        layout.add_widget(btn)
        
        return layout


if __name__ == '__main__':
    GuandanTestApp().run()
