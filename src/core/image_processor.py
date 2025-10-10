# src/core/image_processor.py
import os
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
    
    @staticmethod
    def resize_image_by_settings(image: Image.Image, resize_type: str = "original", 
                                width: int = None, height: int = None, 
                                percent: float = None) -> Image.Image:
        """
        根据设置调整图像尺寸
        
        Args:
            image: 原始图像
            resize_type: 调整方式 (original, width, height, percent)
            width: 目标宽度
            height: 目标高度
            percent: 缩放百分比
            
        Returns:
            Image.Image: 调整大小后的图像
        """
        if resize_type == "original":
            return image.copy()
        
        original_width, original_height = image.size
        
        if resize_type == "width" and width:
            # 按宽度调整，保持长宽比
            ratio = width / original_width
            new_height = int(original_height * ratio)
            return image.resize((width, new_height), Image.LANCZOS)
        
        elif resize_type == "height" and height:
            # 按高度调整，保持长宽比
            ratio = height / original_height
            new_width = int(original_width * ratio)
            return image.resize((new_width, height), Image.LANCZOS)
        
        elif resize_type == "percent" and percent:
            # 按百分比调整
            ratio = percent / 100
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            return image.resize((new_width, new_height), Image.LANCZOS)
        
        return image.copy()
    
    @staticmethod
    def save_image(image: Image.Image, file_path: str, format: str = None, 
                  quality: int = 90) -> bool:
        """
        保存图像到文件
        
        Args:
            image: 要保存的图像
            file_path: 保存路径
            format: 图像格式 (PNG, JPEG)
            quality: 图像质量 (1-100)，仅JPEG格式有效
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保路径为字符串类型
            file_path_str = str(file_path)
            
            # 确定保存格式
            if not format:
                # 从文件扩展名推断格式
                ext = os.path.splitext(file_path_str)[1].lower()
                if ext == '.jpg' or ext == '.jpeg':
                    format = 'JPEG'
                else:
                    format = 'PNG'
            
            # 转换格式
            save_image = image.copy()
            
            # JPEG需要特殊处理
            if format.upper() == 'JPEG':
                save_image = ImageProcessor.convert_to_rgb(save_image)
                save_image.save(file_path_str, format='JPEG', quality=quality, optimize=True)
            else:
                # PNG格式
                if save_image.mode == 'RGBA':
                    save_image.save(file_path_str, format='PNG', optimize=True)
                else:
                    save_image.save(file_path_str, format='PNG', optimize=True)
            
            return True
        except Exception as e:
            print(f"保存图像失败: {e}")
            return False