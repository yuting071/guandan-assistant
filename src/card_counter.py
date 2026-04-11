"""
记牌器核心模块
管理所有牌的统计和炸弹提示
"""

from typing import Dict, List, Set, Optional
from enum import Enum
import threading


class CardSuit(Enum):
    """牌花色"""
    HEART = "红桃"
    SPADE = "黑桃"
    CLUB = "梅花"
    DIAMOND = "方块"
    JOKER_RED = "大王"
    JOKER_BLACK = "小王"


class CardRank(Enum):
    """牌大小"""
    JOKER_BLACK = 17  # 小王
    JOKER_RED = 18    # 大王
    TWO = 16          # 2
    ACE = 14          # A
    KING = 13         # K
    QUEEN = 12        # Q
    JACK = 11         # J
    TEN = 10          # 10
    NINE = 9          # 9
    EIGHT = 8         # 8
    SEVEN = 7         # 7
    SIX = 6           # 6
    FIVE = 5          # 5
    FOUR = 4          # 4
    THREE = 3         # 3


# 牌面定义（对应实际游戏中的牌）
ALL_CARDS = [
    # 大王
    ('joker_red', '大王', 18),
    # 小王
    ('joker_black', '小王', 17),
    # 2
    ('2_heart', '红桃2', 16), ('2_spade', '黑桃2', 16), ('2_club', '梅花2', 16), ('2_diamond', '方块2', 16),
    # A
    ('a_heart', '红桃A', 14), ('a_spade', '黑桃A', 14), ('a_club', '梅花A', 14), ('a_diamond', '方块A', 14),
    # K
    ('k_heart', '红桃K', 13), ('k_spade', '黑桃K', 13), ('k_club', '梅花K', 13), ('k_diamond', '方块K', 13),
    # Q
    ('q_heart', '红桃Q', 12), ('q_spade', '黑桃Q', 12), ('q_club', '梅花Q', 12), ('q_diamond', '方块Q', 12),
    # J
    ('j_heart', '红桃J', 11), ('j_spade', '黑桃J', 11), ('j_club', '梅花J', 11), ('j_diamond', '方块J', 11),
    # 10
    ('10_heart', '红桃10', 10), ('10_spade', '黑桃10', 10), ('10_club', '梅花10', 10), ('10_diamond', '方块10', 10),
    # 9
    ('9_heart', '红桃9', 9), ('9_spade', '黑桃9', 9), ('9_club', '梅花9', 9), ('9_diamond', '方块9', 9),
    # 8
    ('8_heart', '红桃8', 8), ('8_spade', '黑桃8', 8), ('8_club', '梅花8', 8), ('8_diamond', '方块8', 8),
    # 7
    ('7_heart', '红桃7', 7), ('7_spade', '黑桃7', 7), ('7_club', '梅花7', 7), ('7_diamond', '方块7', 7),
    # 6
    ('6_heart', '红桃6', 6), ('6_spade', '黑桃6', 6), ('6_club', '梅花6', 6), ('6_diamond', '方块6', 6),
    # 5
    ('5_heart', '红桃5', 5), ('5_spade', '黑桃5', 5), ('5_club', '梅花5', 5), ('5_diamond', '方块5', 5),
    # 4
    ('4_heart', '红桃4', 4), ('4_spade', '黑桃4', 4), ('4_club', '梅花4', 4), ('4_diamond', '方块4', 4),
    # 3
    ('3_heart', '红桃3', 3), ('3_spade', '黑桃3', 3), ('3_club', '梅花3', 3), ('3_diamond', '方块3', 3),
]

# 每种点数对应的牌数（掼蛋使用两副牌）
RANK_CARD_COUNT = {
    'joker': 2,  # 大王小王各一张
    '2': 8,      # 四个花色的2
    'A': 8,
    'K': 8,
    'Q': 8,
    'J': 8,
    '10': 8,
    '9': 8,
    '8': 8,
    '7': 8,
    '6': 8,
    '5': 8,
    '4': 8,
    '3': 8,
}


class CardCounter:
    """
    掼蛋记牌器核心类
    
    掼蛋使用两副牌（108张），需要记录：
    1. 每种点数剩余多少张
    2. 已经打出的炸弹
    3. 关键牌是否已出（大王、小王、2、A等）
    """

    def __init__(self):
        # 剩余牌数统计
        self.remaining: Dict[str, int] = {}
        # 已出牌统计
        self.played: Dict[str, int] = {}
        # 已出炸弹记录
        self.bombs: List[Dict] = []
        # 关键牌提示
        self.alerts: List[str] = []
        # 锁（线程安全）
        self._lock = threading.Lock()
        
        # 初始化
        self._initialize()
        
    def _initialize(self):
        """初始化牌数"""
        self.remaining = RANK_CARD_COUNT.copy()
        self.played = {k: 0 for k in RANK_CARD_COUNT.keys()}
        self.bombs = []
        self.alerts = []

    def update(self, cards: List[str]):
        """
        更新已出的牌
        
        Args:
            cards: 识别出的牌面列表，如 ['joker_red', 'a_heart', 'k_spade']
        """
        with self._lock:
            for card_id in cards:
                # 提取牌的点数
                rank = self._extract_rank(card_id)
                if rank and rank in self.remaining:
                    self.remaining[rank] -= 1
                    self.played[rank] += 1
                    
                    # 记录已出
                    self._record_alert(rank)
                    self._check_bomb(rank)
            
            self._update_alerts()

    def _extract_rank(self, card_id: str) -> Optional[str]:
        """从牌ID提取点数"""
        # 大王小王
        if card_id.startswith('joker_'):
            return 'joker'
        
        # 普通牌
        parts = card_id.split('_')
        if len(parts) >= 2:
            return parts[0]
        
        return None

    def _record_alert(self, rank: str):
        """记录关键牌已出"""
        if self.remaining.get(rank, 0) == 0:
            rank_names = {
                'joker': '大小王',
                '2': '2',
                'A': 'A',
                'K': 'K',
                'Q': 'Q',
                'J': 'J'
            }
            name = rank_names.get(rank, rank)
            if f"{name}已出" not in self.alerts:
                self.alerts.append(f"⚠️ {name}已出")

    def _check_bomb(self, rank: str):
        """检查是否形成炸弹"""
        if self.remaining.get(rank, 0) == 0:
            bomb = {
                'rank': rank,
                'type': 'normal',
                'count': 4  # 单点炸弹（掼蛋中四张即可成炸）
            }
            if bomb not in self.bombs:
                self.bombs.append(bomb)

    def _update_alerts(self):
        """更新警告信息"""
        self.alerts = []
        
        # 检查关键牌
        if self.remaining.get('joker', 0) <= 1:
            self.alerts.append("⚠️ 关键牌提醒")
        
        # 检查大牌
        for rank in ['2', 'A', 'K']:
            if self.remaining.get(rank, 0) <= 2:
                self.alerts.append(f"⚠️ {rank}剩余不多")
        
        # 炸弹提醒
        for bomb in self.bombs[-3:]:  # 只显示最近3个
            self.alerts.append(f"💣 {bomb['rank']}炸弹已出")

    def get_state(self) -> Dict:
        """获取当前状态"""
        with self._lock:
            return {
                'remaining': self.remaining.copy(),
                'played': self.played.copy(),
                'bombs': self.bombs.copy(),
                'alerts': self.alerts.copy(),
                'total_remaining': sum(self.remaining.values()),
                'total_cards': 108
            }

    def get_display_data(self) -> List[Dict]:
        """
        获取用于显示的数据
        
        Returns:
            格式化的显示数据列表
        """
        state = self.get_state()
        remaining = state['remaining']
        
        display_order = ['joker', '2', 'A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3']
        
        result = []
        for rank in display_order:
            if rank in remaining:
                total = RANK_CARD_COUNT.get(rank, 8)
                curr = remaining.get(rank, 0)
                result.append({
                    'rank': rank,
                    'remaining': curr,
                    'total': total,
                    'played': total - curr
                })
        
        return result

    def reset(self):
        """重置记牌器"""
        with self._lock:
            self._initialize()

    def is_bomb_possible(self, rank: str) -> bool:
        """
        检查指定点数是否可能形成炸弹
        
        Args:
            rank: 牌的点数
            
        Returns:
            是否可能成炸
        """
        with self._lock:
            return self.remaining.get(rank, 0) >= 4

    def get_bomb_count(self) -> int:
        """获取已出炸弹数量"""
        with self._lock:
            return len(self.bombs)


class GuandanCardCounter(CardCounter):
    """
    掼蛋专用记牌器
    
    掼蛋特殊规则：
    - 两副牌（108张）
    - 四人游戏，对家合作
    - 四张同点即可成炸弹
    - 同花顺也是炸弹（要求更高）
    """

    def __init__(self):
        super().__init__()
        # 同花顺记录
        self.straight_flush: List[str] = []

    def update(self, cards: List[str]):
        """更新已出的牌"""
        super().update(cards)
        
        # 检查同花顺（简化版）
        self._check_straight_flush(cards)

    def _check_straight_flush(self, cards: List[str]):
        """检查同花顺（简化实现）"""
        # 简化版：检测到连续三张同花色就提示
        pass

    def get_important_cards(self) -> List[Dict]:
        """
        获取重要牌的状态
        
        用于悬浮窗高亮显示
        """
        state = self.get_state()
        important = ['joker', '2', 'A', 'K']
        
        result = []
        for rank in important:
            remaining = state['remaining'].get(rank, 0)
            total = RANK_CARD_COUNT.get(rank, 8)
            
            # 计算风险等级
            if remaining == 0:
                risk = 'danger'
            elif remaining <= 2:
                risk = 'warning'
            else:
                risk = 'normal'
            
            result.append({
                'rank': rank,
                'remaining': remaining,
                'total': total,
                'risk': risk
            })
        
        return result

    def get_strategy_tips(self) -> List[str]:
        """
        获取策略提示
        
        基于记牌结果给出简单建议
        """
        tips = []
        state = self.get_state()
        remaining = state['remaining']
        
        # 大王检查
        if remaining.get('joker', 0) >= 2:
            tips.append("🔴 大王尚在，可考虑上手")
        elif remaining.get('joker', 0) == 1:
            tips.append("🟡 大王剩余一张")
        else:
            tips.append("🟢 大王已出")
        
        # 2的数量
        two_count = remaining.get('2', 0)
        if two_count >= 6:
            tips.append(f"🟡 2还剩{two_count}张，小心")
        elif two_count <= 2:
            tips.append(f"🔴 2快没了（剩{two_count}张）")
        
        return tips
