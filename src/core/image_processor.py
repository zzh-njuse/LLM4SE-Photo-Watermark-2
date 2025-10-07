# src/core/image_processor.py
from PIL import Image
from typing import Optional, Tuple

class ImageProcessor:
    """
    图像处理器类，负责图像处理相关功能
    """
    # 添加PIL引用，便于其他模块访问
    PIL = Image
    
    @staticmethod
    def load_image(file_path: str) -> Optional[Image.Image]:
        """
        加载图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            Optional[Image.Image]: 加载的图像对象，加载失败返回None
        """
        try:
            # 确保路径为字符串类型
            file_path_str = str(file_path)
            print(f"尝试加载图片: {file_path_str}")
            
            # 直接加载 - 简化实现
            img = Image.open(file_path_str)
            return img
        except Exception as e:
            print(f"加载图片失败: {e}")
            return None
    
    @staticmethod
    def create_thumbnail(image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        创建缩略图
        
        Args:
            image: 原始图像
            size: 缩略图尺寸 (width, height)
            
        Returns:
            Image.Image: 缩略图
        """
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.LANCZOS)
        return thumbnail
    
    @staticmethod
    def resize_image(image: Image.Image, size: Tuple[int, int], keep_aspect_ratio: bool = True) -> Image.Image:
        """
        调整图像大小
        
        Args:
            image: 原始图像
            size: 目标尺寸 (width, height)
            keep_aspect_ratio: 是否保持长宽比
            
        Returns:
            Image.Image: 调整大小后的图像
        """
        if keep_aspect_ratio:
            return image.resize(size, Image.LANCZOS, box=None, reducing_gap=3.0)
        else:
            # 使用thumbnail方法保持长宽比
            resized = image.copy()
            resized.thumbnail(size, Image.LANCZOS)
            return resized
    
    @staticmethod
    def convert_to_rgb(image: Image.Image) -> Image.Image:
        """
        将图像转换为RGB模式(用于保存为JPEG等不支持透明通道的格式)
        
        Args:
            image: 原始图像
            
        Returns:
            Image.Image: RGB模式图像
        """
        if image.mode == 'RGBA':
            # 创建白色背景
            background = Image.new('RGB', image.size, (255, 255, 255))
            # 粘贴图像，使用alpha通道作为掩码
            background.paste(image, mask=image.split()[3])
            return background
        return image.convert('RGB')