"""
主界面窗口
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock


class MainWindow(Screen):
    """
    掼蛋助手主界面
    
    功能：
    1. 显示应用状态
    2. 控制悬浮窗显示/隐藏
    3. 控制截屏监控开始/停止
    4. 查看记牌统计
    5. 设置参数
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.monitoring_active = False
        self.float_visible = False

    def on_enter(self):
        """进入界面时"""
        self.build_ui()

    def build_ui(self):
        """构建UI"""
        # 清除现有子元素
        self.clear_widgets()
        
        # 主布局
        main_layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15
        )
        
        # 标题
        title = Label(
            text='[b]掼蛋实时助手[/b]',
            markup=True,
            font_size='24sp',
            size_hint_y=None,
            height=60,
            halign='center'
        )
        main_layout.add_widget(title)
        
        # 状态显示
        self.status_label = Label(
            text='状态：就绪',
            font_size='16sp',
            size_hint_y=None,
            height=40,
            color=(0.3, 0.7, 0.3, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # 控制按钮区域
        controls = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=200,
            spacing=10
        )
        
        # 悬浮窗开关
        float_control = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50
        )
        float_control.add_widget(Label(text='悬浮窗', size_hint_x=0.4))
        self.float_switch = Switch(size_hint_x=0.6)
        self.float_switch.bind(active=self.on_float_switch)
        float_control.add_widget(self.float_switch)
        controls.add_widget(float_control)
        
        # 监控开关
        monitor_control = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50
        )
        monitor_control.add_widget(Label(text='截屏监控', size_hint_x=0.4))
        self.monitor_switch = Switch(size_hint_x=0.6)
        self.monitor_switch.bind(active=self.on_monitor_switch)
        monitor_control.add_widget(self.monitor_switch)
        controls.add_widget(monitor_control)
        
        # 截屏间隔设置
        interval_control = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50
        )
        interval_control.add_widget(Label(text='截屏间隔', size_hint_x=0.4))
        self.interval_slider = Slider(
            min=0.5,
            max=5.0,
            value=1.0,
            step=0.5,
            size_hint_x=0.4
        )
        self.interval_slider.bind(value=self.on_interval_change)
        interval_control.add_widget(self.interval_slider)
        self.interval_label = Label(text='1.0秒', size_hint_x=0.2)
        interval_control.add_widget(self.interval_label)
        controls.add_widget(interval_control)
        
        main_layout.add_widget(controls)
        
        # 按钮区域
        buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        start_btn = Button(
            text='开始记牌',
            background_color=(0.2, 0.6, 0.2, 1)
        )
        start_btn.bind(on_press=self.start_counting)
        buttons.add_widget(start_btn)
        
        reset_btn = Button(
            text='重置',
            background_color=(0.8, 0.4, 0.2, 1)
        )
        reset_btn.bind(on_press=self.reset_counter)
        buttons.add_widget(reset_btn)
        
        help_btn = Button(
            text='帮助',
            background_color=(0.3, 0.3, 0.8, 1)
        )
        help_btn.bind(on_press=self.show_help)
        buttons.add_widget(help_btn)
        
        main_layout.add_widget(buttons)
        
        # 记牌统计显示
        stats_label = Label(
            text='[b]记牌统计[/b]',
            markup=True,
            font_size='18sp',
            size_hint_y=None,
            height=40,
            halign='left'
        )
        main_layout.add_widget(stats_label)
        
        # 统计文本区域
        self.stats_text = Label(
            text=self._get_initial_stats(),
            font_size='14sp',
            halign='left',
            valign='top',
            text_size=(Window.width - 40, 200)
        )
        main_layout.add_widget(self.stats_text)
        
        # 添加到主界面
        self.add_widget(main_layout)

    def _get_initial_stats(self) -> str:
        """获取初始统计文本"""
        return """大王: 2/2 | 小王: 2/2
A: 8/8 | K: 8/8 | Q: 8/8
J: 8/8 | 10: 8/8 | 9: 8/8
8: 8/8 | 7: 8/8 | 6: 8/8
5: 8/8 | 4: 8/8 | 3: 8/8

已出炸弹: 0"""

    def on_float_switch(self, instance, value):
        """悬浮窗开关回调"""
        self.float_visible = value
        app = self.get_app()
        if hasattr(app, 'toggle_float_window'):
            app.toggle_float_window(value)
        
        self.status_label.text = f'悬浮窗: {"显示" if value else "隐藏"}'

    def on_monitor_switch(self, instance, value):
        """监控开关回调"""
        self.monitoring_active = value
        app = self.get_app()
        
        if value:
            if hasattr(app, 'start_monitoring'):
                app.start_monitoring()
            self.status_label.text = '状态：监控中...'
            self.status_label.color = (0.2, 0.8, 0.2, 1)
        else:
            if hasattr(app, 'stop_monitoring'):
                app.stop_monitoring()
            self.status_label.text = '状态：已停止'
            self.status_label.color = (0.8, 0.6, 0.2, 1)

    def on_interval_change(self, instance, value):
        """截屏间隔变化回调"""
        self.interval_label.text = f'{value:.1f}秒'
        app = self.get_app()
        if hasattr(app, 'screen_capture') and app.screen_capture:
            app.screen_capture.set_interval(value)

    def start_counting(self, instance):
        """开始记牌"""
        self.monitor_switch.active = True
        self.on_monitor_switch(None, True)

    def reset_counter(self, instance):
        """重置记牌器"""
        app = self.get_app()
        if hasattr(app, 'get_card_counter'):
            counter = app.get_card_counter()
            counter.reset()
            self.update_stats(counter.get_display_data())
        
        self.stats_label.text = self._get_initial_stats()

    def update_stats(self, display_data):
        """更新统计显示"""
        lines = []
        for item in display_data:
            rank = item['rank']
            remaining = item['remaining']
            total = item['total']
            lines.append(f"{rank}: {remaining}/{total}")
        
        self.stats_text.text = '\n'.join(lines)

    def show_help(self, instance):
        """显示帮助"""
        help_text = """
[b]掼蛋实时助手 使用说明[/b]

1. [b]悬浮窗[/b]：打开后会在屏幕右侧显示记牌器
2. [b]截屏监控[/b]：开启后自动识别出牌并更新统计
3. [b]截屏间隔[/b]：设置检测屏幕变化的频率

[b]使用步骤[/b]：
1. 首次使用需要授权悬浮窗权限
2. 开启悬浮窗显示
3. 开始游戏后开启截屏监控
4. 助手会自动识别并记录已出的牌

[b]注意事项[/b]：
- 截屏监控会影响少量性能
- 建议根据手机性能调整截屏间隔
- 识别准确度受屏幕亮度和环境影响
        """
        
        popup = Popup(
            title='帮助',
            content=Label(
                text=help_text,
                markup=True,
                valign='top',
                text_size=(400, 500)
            ),
            size_hint=(0.9, 0.8),
            auto_dismiss=True
        )
        popup.open()

    def get_app(self):
        """获取App实例"""
        from kivy.app import App
        return App.get_running_app()
