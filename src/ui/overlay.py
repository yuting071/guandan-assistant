"""
悬浮窗覆盖层UI
用于Kivy桌面调试或模拟显示
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty, StringProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import platform


class CardCounterOverlay(BoxLayout):
    """
    记牌器悬浮窗UI组件
    
    用于：
    1. 桌面调试模式下的悬浮窗显示
    2. 非Android平台的替代显示
    """

    def __init__(self, card_counter=None, **kwargs):
        super().__init__(**kwargs)
        
        self.card_counter = card_counter
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.width = 180
        self.height = 300
        
        # 位置
        self.pos_hint = {'right': 0.95, 'center_y': 0.4}
        
        # 背景
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 0.85)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[10, 10, 10, 10]
            )
        
        # 构建UI
        self.build_ui()

    def build_ui(self):
        """构建悬浮窗UI"""
        # 标题
        title = Label(
            text='[b]掼蛋记牌器[/b]',
            markup=True,
            font_size='14sp',
            size_hint_y=None,
            height=30,
            color=(1, 0.9, 0.5, 1)
        )
        self.add_widget(title)
        
        # 分隔线
        divider = Label(
            text='',
            size_hint_y=None,
            height=2
        )
        with divider.canvas.after:
            Color(0.5, 0.5, 0.5, 0.8)
            Rectangle(pos=divider.pos, size=(150, 1))
        self.add_widget(divider)
        
        # 重要牌显示
        self.important_label = Label(
            text='大王:2  小王:2',
            font_size='11sp',
            size_hint_y=None,
            height=25,
            color=(1, 0.8, 0.5, 1)
        )
        self.add_widget(self.important_label)
        
        # 分隔线
        divider2 = Label(text='', size_hint_y=None, height=2)
        self.add_widget(divider2)
        
        # 牌面列表（可滚动）
        scroll = ScrollView(
            size_hint_y=1,
            do_scroll_x=False,
            bar_color=(0.6, 0.6, 0.6, 0.5),
            bar_inactive_color=(0.4, 0.4, 0.4, 0.3)
        )
        
        self.cards_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=5,
            spacing=2
        )
        self.cards_container.bind(
            minimum_height=self.cards_container.setter('height')
        )
        
        scroll.add_widget(self.cards_container)
        self.add_widget(scroll)
        
        # 分隔线
        divider3 = Label(text='', size_hint_y=None, height=2)
        self.add_widget(divider3)
        
        # 警告区域
        self.alert_label = Label(
            text='',
            font_size='10sp',
            size_hint_y=None,
            height=50,
            color=(1, 0.5, 0.5, 1),
            valign='top'
        )
        self.add_widget(self.alert_label)
        
        # 初始化显示
        self._update_initial_display()

    def _update_initial_display(self):
        """更新初始显示"""
        # 清空牌面容器
        self.cards_container.clear_widgets()
        
        # 初始化牌面显示
        ranks = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3']
        for rank in ranks:
            card_label = Label(
                text=f'{rank}:8/8',
                font_size='11sp',
                size_hint_y=None,
                height=18,
                halign='left',
                color=(0.9, 0.9, 0.9, 1)
            )
            self.cards_container.add_widget(card_label)

    def update_display(self, state: dict):
        """
        更新显示内容
        
        Args:
            state: 记牌器状态字典
        """
        if not state:
            return
            
        remaining = state.get('remaining', {})
        alerts = state.get('alerts', [])
        
        # 更新重要牌
        joker_count = remaining.get('joker', 2)
        # 假设2的数量为 remaining.get('2', 8)
        two_count = remaining.get('2', 8)
        ace_count = remaining.get('A', 8)
        
        important_text = f'大王:{joker_count}  小王:{joker_count}\n2:{two_count}  A:{ace_count}'
        self.important_label.text = important_text
        
        # 更新牌面列表
        self.cards_container.clear_widgets()
        
        rank_order = ['joker', '2', 'A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3']
        
        for rank in rank_order:
            if rank in remaining:
                curr = remaining.get(rank, 0)
                total = 8 if rank != 'joker' else 2
                
                # 根据剩余量设置颜色
                if curr == 0:
                    color = (0.6, 0.6, 0.6, 1)  # 灰色
                elif curr <= 2:
                    color = (1, 0.5, 0.5, 1)  # 红色警告
                else:
                    color = (0.9, 0.9, 0.9, 1)  # 白色
                
                display_name = '王' if rank == 'joker' else rank
                card_label = Label(
                    text=f'{display_name}:{curr}/{total}',
                    font_size='11sp',
                    size_hint_y=None,
                    height=18,
                    halign='left',
                    color=color
                )
                self.cards_container.add_widget(card_label)
        
        # 更新警告
        if alerts:
            self.alert_label.text = '\n'.join(alerts[:3])  # 最多显示3条
        else:
            self.alert_label.text = ''


class SimpleOverlay(BoxLayout):
    """
    简化版悬浮窗
    
    占用更小空间，只显示关键信息
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.width = 120
        self.height = 80
        self.pos_hint = {'right': 0.98, 'top': 0.95}
        
        # 背景
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[8, 8, 8, 8]
            )
        
        self.build_ui()

    def build_ui(self):
        """构建简化UI"""
        # 标题
        title = Label(
            text='[b]记牌[/b]',
            markup=True,
            font_size='12sp',
            size_hint_y=None,
            height=25,
            color=(1, 0.9, 0.5, 1)
        )
        self.add_widget(title)
        
        # 剩余牌数
        self.remain_label = Label(
            text='剩余: 108',
            font_size='11sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.remain_label)
        
        # 炸弹提示
        self.bomb_label = Label(
            text='炸弹: 0',
            font_size='11sp',
            color=(1, 0.7, 0.3, 1)
        )
        self.add_widget(self.bomb_label)

    def update(self, total_remaining: int, bomb_count: int):
        """更新显示"""
        self.remain_label.text = f'剩余: {total_remaining}'
        self.bomb_label.text = f'炸弹: {bomb_count}'


# 用于测试的独立窗口
if __name__ == '__main__':
    from kivy.app import App
    from kivy.core.window import Window
    
    class TestApp(App):
        def build(self):
            Window.add_widget(CardCounterOverlay())
            return BoxLayout()  # 空布局
    
    TestApp().run()
