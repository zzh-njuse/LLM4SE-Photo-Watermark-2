# src/core/file_handler.py
import os
from typing import List, Tuple, Optional
from PIL import Image

class FileHandler:
    """
    文件处理器类，负责图片的导入、导出和文件操作相关功能
    """
    
    # 支持的图片格式
    SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif']
    
    @staticmethod
    def is_supported_image(file_path: str) -> bool:
        """
        检查文件是否为支持的图片格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为支持的图片格式
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in FileHandler.SUPPORTED_IMAGE_FORMATS
    
    @staticmethod
    def get_images_from_folder(folder_path: str) -> List[str]:
        """
        从文件夹中获取所有支持的图片文件路径
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            List[str]: 图片文件路径列表
        """
        image_paths = []
        
        if not os.path.isdir(folder_path):
            return image_paths
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if FileHandler.is_supported_image(file_path):
                    image_paths.append(file_path)
        
        return image_paths
    
    @staticmethod
    def save_image(image: Image.Image, output_path: str, format: Optional[str] = None, quality: int = 95) -> bool:
        """
        保存图片到指定路径
        
        Args:
            image: PIL Image对象
            output_path: 输出文件路径
            format: 输出格式，如'PNG', 'JPEG'等，若为None则根据文件扩展名确定
            quality: 图片质量，仅对JPEG等有损压缩格式有效
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保路径为字符串类型
            output_path_str = str(output_path)
            print(f"保存图片到: {output_path_str}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path_str)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 直接保存 - 测试显示这种方式在Windows上可以处理中文路径
            if format:
                image.save(output_path_str, format=format, quality=quality)
            else:
                # 对于JPEG格式，设置质量参数
                ext = os.path.splitext(output_path_str)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    image.save(output_path_str, quality=quality)
                else:
                    image.save(output_path_str)
            
            print(f"保存成功")
            return True
        except Exception as e:
            print(f"保存图片失败: {e}")
            print(f"异常类型: {type(e).__name__}")
            # 尝试降级方案：使用临时文件名然后重命名
            try:
                temp_path = os.path.join(os.path.dirname(output_path_str), "temp_img_" + str(os.getpid()) + ".tmp")
                print(f"尝试临时文件方案: {temp_path}")
                
                if format:
                    image.save(temp_path, format=format, quality=quality)
                else:
                    image.save(temp_path)
                
                # 使用os.rename重命名（Windows API可能更好地处理Unicode）
                if os.path.exists(temp_path):
                    os.rename(temp_path, output_path_str)
                    print(f"临时文件方案成功，已重命名到: {output_path_str}")
                    return True
                else:
                    print("临时文件不存在")
                    return False
            except Exception as e2:
                print(f"临时文件方案也失败: {e2}")
                return False
    
    @staticmethod
    def generate_output_filename(original_path: str, output_dir: str, suffix: str = "_watermark") -> str:
        """
        根据原文件名生成输出文件名
        
        Args:
            original_path: 原始文件路径
            output_dir: 输出目录
            suffix: 添加到文件名的后缀
            
        Returns:
            str: 输出文件的完整路径
        """
        try:
            # 确保所有路径参数都是字符串类型
            original_path_str = str(original_path)
            output_dir_str = str(output_dir)
            suffix_str = str(suffix)
            
            # 安全地获取文件名部分
            base_name = os.path.basename(original_path_str)
            base_name_without_ext, ext = os.path.splitext(base_name)
            
            # 生成新文件名
            new_name = f"{base_name_without_ext}{suffix_str}{ext}"
            
            # 确保路径分隔符正确
            output_path = os.path.join(output_dir_str, new_name)
            print(f"生成输出文件名: {output_path}")
            
            return output_path
        except Exception as e:
            print(f"生成输出文件名时出错: {e}")
            # 如果出错，使用安全的回退方案
            safe_name = "output_image" + str(hash(original_path))[:8] + ".png"
            return os.path.join(str(output_dir), safe_name)