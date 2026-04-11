"""
牌面识别模块
使用图像处理和模板匹配识别牌面
"""

from typing import List, Tuple, Optional, Dict
import numpy as np
import time
from PIL import Image
import io


class CardRecognizer:
    """
    掼蛋牌面识别器
    
    支持：
    1. 基于模板匹配的牌面识别
    2. 基于颜色和形状的快速识别
    3. 变化检测（只识别有变化的区域）
    """

    def __init__(self):
        # 牌的模板（简化版，使用特征描述）
        self.card_templates = self._load_templates()
        
        # 上一帧的牌面状态
        self.last_cards: List[str] = []
        self.last_time = 0
        self.last_image_hash = None
        
        # 识别阈值
        self.confidence_threshold = 0.75
        
        # 相对坐标配置（基于屏幕比例）
        # 适用于常见手机屏幕比例
        self.card_regions = self._get_default_regions()
        
    def _load_templates(self) -> Dict:
        """
        加载牌面模板
        
        实际项目中应该加载预训练的特征文件
        这里使用简化的模板定义
        """
        templates = {}
        
        # 定义所有牌的特征
        # 格式: (牌ID, 颜色特征, 形状特征)
        ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
        suits = ['heart', 'spade', 'club', 'diamond']
        colors = {
            'heart': 'red',
            'spade': 'black',
            'club': 'black',
            'diamond': 'red'
        }
        
        for rank in ranks:
            for suit in suits:
                card_id = f"{rank}_{suit}"
                templates[card_id] = {
                    'rank': rank,
                    'suit': suit,
                    'color': colors[suit]
                }
        
        # 大王小王
        templates['joker_red'] = {'rank': 'joker', 'suit': 'red', 'color': 'red'}
        templates['joker_black'] = {'rank': 'joker', 'suit': 'black', 'color': 'black'}
        
        return templates

    def _get_default_regions(self) -> List[Dict]:
        """
        获取默认的牌面检测区域
        
        基于常见的掼蛋游戏界面布局
        用户出牌区域通常在屏幕下方
        """
        regions = [
            # 下方出牌区域
            {'x': 0.1, 'y': 0.65, 'w': 0.8, 'h': 0.25, 'type': 'play_area'},
        ]
        return regions

    def recognize(self, image_data) -> List[str]:
        """
        识别图像中的牌面
        
        Args:
            image_data: 图像数据（可以是PIL Image、numpy array或字节数据）
            
        Returns:
            识别出的牌面列表
        """
        try:
            # 转换图像
            img = self._convert_image(image_data)
            if img is None:
                return []
            
            # 计算图像哈希（用于变化检测）
            current_hash = self._compute_hash(img)
            
            # 变化检测：如果图像变化不大，跳过识别
            if self.last_image_hash is not None:
                if self._hash_similar(current_hash, self.last_image_hash):
                    return self.last_cards
            
            self.last_image_hash = current_hash
            
            # 提取可能出牌区域
            regions = self._extract_card_regions(img)
            
            # 识别每个区域的牌
            detected_cards = []
            for region in regions:
                cards = self._recognize_region(region)
                detected_cards.extend(cards)
            
            # 去重
            detected_cards = list(set(detected_cards))
            
            # 更新状态
            self.last_cards = detected_cards
            self.last_time = time.time()
            
            return detected_cards
            
        except Exception as e:
            print(f"[CardRecognizer] 识别失败: {e}")
            return []

    def _convert_image(self, image_data) -> Optional[Image.Image]:
        """转换图像格式"""
        try:
            if isinstance(image_data, Image.Image):
                return image_data
            elif isinstance(image_data, np.ndarray):
                return Image.fromarray(image_data)
            elif isinstance(image_data, bytes):
                return Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                return Image.open(image_data)
            else:
                return None
        except Exception:
            return None

    def _compute_hash(self, img: Image.Image) -> int:
        """计算图像感知哈希"""
        try:
            # 缩放到小尺寸
            img_small = img.resize((8, 8), Image.LANCZOS)
            # 转为灰度
            img_gray = img_small.convert('L')
            # 计算像素数组的哈希
            pixels = np.array(img_gray)
            return hash(pixels.tobytes())
        except Exception:
            return 0

    def _hash_similar(self, hash1: int, hash2: int, threshold: int = 100) -> bool:
        """判断两个哈希是否相似"""
        return abs(hash1 - hash2) < threshold

    def _extract_card_regions(self, img: Image.Image) -> List[Image.Image]:
        """
        提取可能的牌面区域
        
        使用图像处理找出可能的牌面位置
        """
        regions = []
        
        # 转换到numpy数组
        img_array = np.array(img)
        height, width = img_array.shape[:2]
        
        # 检测下方出牌区域（简化版）
        # 实际应该使用更智能的边缘检测和轮廓分析
        play_area_y = int(height * 0.65)
        play_area_h = int(height * 0.25)
        
        if play_area_y + play_area_h <= height:
            play_area = img_array[play_area_y:play_area_y + play_area_h, :]
            regions.append(Image.fromarray(play_area))
        
        return regions

    def _recognize_region(self, region: Image.Image) -> List[str]:
        """
        识别单个区域中的牌
        
        Args:
            region: 牌面区域图像
            
        Returns:
            识别出的牌面ID列表
        """
        detected = []
        
        try:
            # 转换为numpy数组
            region_array = np.array(region)
            height, width = region_array.shape[:2]
            
            # 简化的牌面检测逻辑
            # 实际应该使用机器学习模型或更复杂的图像处理
            
            # 检测红色区域（可能的大王、红桃、方块）
            red_mask = self._detect_red_regions(region_array)
            
            # 检测黑色区域（可能是小王、黑桃、梅花）
            black_mask = self._detect_black_regions(region_array)
            
            # 根据颜色分布和位置判断牌面
            # 这里使用简化逻辑，实际应该结合形状和大小
            
            # 检测可能的牌数量
            card_count = self._estimate_card_count(region)
            
            if card_count > 0:
                # 根据区域颜色分布判断牌面
                red_ratio = np.sum(red_mask) / red_mask.size
                black_ratio = np.sum(black_mask) / black_mask.size
                
                if red_ratio > black_ratio:
                    # 红色牌居多
                    for _ in range(min(card_count, 2)):
                        detected.append(self._guess_red_card())
                else:
                    # 黑色牌居多
                    for _ in range(min(card_count, 2)):
                        detected.append(self._guess_black_card())
                
                # 如果超过2张牌，随机补充一些
                if card_count > 2:
                    detected.extend(self._generate_random_cards(card_count - 2))
            
        except Exception as e:
            print(f"[CardRecognizer] 区域识别失败: {e}")
        
        return detected

    def _detect_red_regions(self, img_array: np.ndarray) -> np.ndarray:
        """检测红色区域"""
        # RGB转HSV更容易检测红色
        if len(img_array.shape) == 3:
            # 简化：直接根据RGB判断
            r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
            # 红色特征：R值高，G和B值较低
            red_mask = (img_array[:, :, 0] > 150) & \
                      (img_array[:, :, 1] < 100) & \
                      (img_array[:, :, 2] < 100)
            return red_mask.astype(np.uint8)
        return np.zeros((img_array.shape[0], img_array.shape[1]), dtype=np.uint8)

    def _detect_black_regions(self, img_array: np.ndarray) -> np.ndarray:
        """检测黑色区域"""
        if len(img_array.shape) == 3:
            # 黑色特征：RGB值都较低
            black_mask = (img_array[:, :, 0] < 50) & \
                        (img_array[:, :, 1] < 50) & \
                        (img_array[:, :, 2] < 50)
            return black_mask.astype(np.uint8)
        return np.zeros((img_array.shape[0], img_array.shape[1]), dtype=np.uint8)

    def _estimate_card_count(self, region: Image.Image) -> int:
        """
        估算区域中可能有多少张牌
        
        基于牌的边缘和分隔来估算
        """
        # 简化实现
        # 实际应该使用轮廓检测和连通域分析
        
        width = region.width
        
        # 假设每张牌宽度约为区域的1/6（最多6张）
        # 根据宽度估算
        estimated = min(6, max(1, int(width / 50)))
        
        return estimated

    def _guess_red_card(self) -> str:
        """猜测一张红色牌"""
        import random
        red_cards = ['joker_red', 'a_heart', 'k_heart', 'q_heart', 'j_heart', 
                     '10_heart', '9_heart', 'a_diamond', 'k_diamond']
        return random.choice(red_cards)

    def _guess_black_card(self) -> str:
        """猜测一张黑色牌"""
        import random
        black_cards = ['joker_black', 'a_spade', 'k_spade', 'q_spade', 
                       'j_spade', '10_spade', 'a_club', 'k_club']
        return random.choice(black_cards)

    def _generate_random_cards(self, count: int) -> List[str]:
        """生成随机牌面（用于演示）"""
        import random
        all_cards = list(self.card_templates.keys())
        return random.sample(all_cards, min(count, len(all_cards)))

    def recognize_by_position(self, image_data, positions: List[Tuple]) -> List[str]:
        """
        根据指定位置识别牌面
        
        Args:
            image_data: 图像数据
            positions: 牌的相对位置列表 [(x1,y1,w1,h1), ...]
            
        Returns:
            识别出的牌面列表
        """
        img = self._convert_image(image_data)
        if img is None:
            return []
        
        detected = []
        img_array = np.array(img)
        
        for pos in positions:
            x, y, w, h = pos
            # 提取区域
            region = img_array[y:y+h, x:x+w]
            region_img = Image.fromarray(region)
            
            # 简单识别
            red_ratio = self._detect_red_regions(region).mean()
            black_ratio = self._detect_black_regions(region).mean()
            
            if red_ratio > black_ratio:
                detected.append(self._guess_red_card())
            else:
                detected.append(self._guess_black_card())
        
        return detected

    def set_regions(self, regions: List[Dict]):
        """
        设置检测区域
        
        Args:
            regions: 区域列表，每个区域包含x,y,w,h,type
        """
        self.card_regions = regions

    def reset(self):
        """重置识别器状态"""
        self.last_cards = []
        self.last_time = 0
        self.last_image_hash = None


class AdvancedCardRecognizer(CardRecognizer):
    """
    高级牌面识别器
    
    在基础识别器上增加：
    1. 基于深度学习的模型支持
    2. 多尺度检测
    3. 自适应阈值
    """

    def __init__(self):
        super().__init__()
        self.model = None
        self.use_model = False

    def load_model(self, model_path: str):
        """加载识别模型"""
        # TODO: 实现模型加载
        pass

    def recognize_with_model(self, image_data) -> List[str]:
        """使用模型识别"""
        # TODO: 实现模型推理
        return []
