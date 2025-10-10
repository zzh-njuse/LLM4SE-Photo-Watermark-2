# src/gui/toolbar.py
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QFileDialog, 
                             QLabel, QComboBox)
from PyQt5.QtCore import Qt

class Toolbar(QWidget):
    """
    顶部工具栏，包含常用操作按钮
    """
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f0f0f0; border-bottom: 1px solid #cccccc;")
        self.init_ui()
    
    def init_ui(self):
        """初始化工具栏UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # 删除添加图片和添加文件夹按钮
        
        # 添加分隔符
        layout.addStretch()
        # 添加分隔符
        layout.addStretch()
        
        # 应用水印按钮
        self.apply_btn = QPushButton("应用水印")
        self.apply_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 6px 12px;")
        self.apply_btn.clicked.connect(self.apply_watermark)
        layout.addWidget(self.apply_btn)
        
        # 导出按钮
        export_btn = QPushButton("导出图片")
        export_btn.setStyleSheet("background-color: #E91E63; color: white; padding: 6px 12px;")
        export_btn.clicked.connect(self.export_images)
        layout.addWidget(export_btn)
    
    def export_images(self):
        """导出图片功能实现"""
        # 检查是否有主窗口引用
        if not hasattr(self, 'main_window'):
            return
        
        # 获取预览面板和设置面板
        preview_panel = getattr(self.main_window, 'preview_panel', None)
        settings_panel = getattr(self.main_window, 'settings_panel', None)
        
        if not preview_panel or not settings_panel:
            return
        
        # 仅导出当前图片
        if not preview_panel.current_image_path:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "导出失败", "没有选中的图片可供导出")
            return
        image_paths = [preview_panel.current_image_path]
        
        # 显示导出设置对话框
        from src.gui.export_dialog import ExportDialog
        # 获取当前设置面板中的默认格式
        default_format = "PNG"
        if hasattr(settings_panel, 'format_combo'):
            default_format = settings_panel.format_combo.currentText()
            
        export_dialog = ExportDialog(self, default_format=default_format)
        if export_dialog.exec_() != ExportDialog.Accepted:
            return  # 用户取消了导出
        
        # 获取导出设置
        export_settings = export_dialog.get_settings()
        output_format = export_settings['format'].lower()
        naming_rule = export_settings['naming_rule']
        prefix = export_settings['prefix']
        suffix = export_settings['suffix']
        
        # 选择输出文件夹
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import os
        
        # 首先获取默认路径（使用第一张图片的目录或当前目录）
        default_dir = os.getcwd()
        if image_paths:
            default_dir = os.path.dirname(image_paths[0])
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出文件夹", default_dir)
        if not output_dir:
            return
        
        # 确保输出文件夹不是原始图片所在的文件夹（更严格的检查）
        # 对于批量导出，检查所有图片的目录
        if image_paths:
            original_dirs = set(os.path.dirname(img_path) for img_path in image_paths)
            if output_dir in original_dirs:
                # 对于命名规则为"original"的情况，强制不允许导出到原文件夹
                if naming_rule == "original":
                    QMessageBox.warning(self, "导出位置不允许", 
                                      "使用'保留原文件名'时，不能导出到原始图片所在的文件夹，以防止覆盖原文件。")
                    return
                # 对于其他命名规则，显示警告
                else:
                    reply = QMessageBox.question(self, "确认导出", 
                                               "您正在导出到原始图片所在的文件夹，这可能会覆盖文件。确定继续吗？",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply != QMessageBox.Yes:
                        return
        
        try:
            # 获取水印设置
            watermark_settings = self._get_watermark_settings(settings_panel)
            
            # 更新水印设置中的格式
            watermark_settings['format'] = export_settings['format']
            
            # 导入必要的模块
            from src.core.image_processor import ImageProcessor
            from src.core.file_handler import FileHandler
            
            # 导出每张图片
            success_count = 0
            for image_path in image_paths:
                try:
                    print(f"处理图片 {success_count+1}/{len(image_paths)}: {image_path}")
                    # 加载图片
                    image = ImageProcessor.load_image(image_path)
                    if not image:
                        print(f"无法加载图片: {image_path}")
                        continue
                    
                    # 应用水印
                    watermarked_image = self._apply_watermark(image, watermark_settings, settings_panel)
                    
                    # 生成输出文件名
                    output_path = FileHandler.generate_output_filename(
                        image_path, output_dir, naming_rule, prefix, suffix)
                    
                    # 获取质量设置和尺寸调整设置
                    quality = export_settings.get('quality', 90)
                    resize_type = export_settings.get('resize_type', 'original')
                    width = export_settings.get('width')
                    height = export_settings.get('height')
                    percent = export_settings.get('percent')
                    
                    # 调整图片尺寸
                    print(f"调整图片尺寸: type={resize_type}, width={width}, height={height}, percent={percent}")
                    watermarked_image = ImageProcessor.resize_image_by_settings(
                        watermarked_image, 
                        resize_type=resize_type, 
                        width=width, 
                        height=height, 
                        percent=percent
                    )
                    
                    # 保存图片（包括质量设置和格式处理）
                    success = ImageProcessor.save_image(
                        watermarked_image, output_path, output_format.upper(), quality)
                    
                    if success:
                        success_count += 1
                        print(f"成功保存: {output_path}")
                    else:
                        print(f"保存图片失败: {output_path}")
                        
                except Exception as e:
                    # 分离错误信息和图片路径，避免编码错误
                    print(f"处理图片时出错: {str(e)}")
                    print(f"异常类型: {type(e).__name__}")
                    print(f"图片路径: {image_path}")
            
            # 显示导出结果
            if success_count > 0:
                QMessageBox.information(self, "导出成功", 
                                      f"成功导出 {success_count}/{len(image_paths)} 张图片\n到文件夹: {output_dir}")
            else:
                QMessageBox.warning(self, "导出失败", "未能成功导出任何图片")
                
        except Exception as e:
            QMessageBox.warning(self, "导出失败", f"导出图片时发生错误:\n{str(e)}")
            print(f"导出过程异常: {type(e).__name__}: {str(e)}")
    
    def apply_watermark(self):
        """应用水印到预览面板"""
        # 检查是否有主窗口引用
        if not hasattr(self, 'main_window'):
            return
        
        # 获取预览面板和设置面板
        preview_panel = getattr(self.main_window, 'preview_panel', None)
        settings_panel = getattr(self.main_window, 'settings_panel', None)
        
        if not preview_panel or not settings_panel:
            return
        
        # 先应用当前设置
        if hasattr(settings_panel, 'apply_settings'):
            settings_panel.apply_settings()
            print("已保存当前设置")
        else:
            print("设置面板没有apply_settings方法")
        
        # 触发预览面板更新水印预览
        print("触发应用水印，更新预览")
        if hasattr(preview_panel, 'update_watermark_preview'):
            preview_panel.update_watermark_preview()
    
    def _get_watermark_settings(self, settings_panel):
        """从设置面板获取水印设置，优先使用已应用的设置"""
        # 使用设置面板的get_applied_settings方法，确保使用已应用的设置
        if hasattr(settings_panel, 'get_applied_settings'):
            return settings_panel.get_applied_settings()
        
        # 如果没有get_applied_settings方法，回退到使用_get_current_settings
        elif hasattr(settings_panel, '_get_current_settings'):
            return settings_panel._get_current_settings()
        
        # 最后的回退方案
        return {
            'text': "我的图片",
            'size': 30,
            'opacity': 0.5,
            'rotation': 0,
            'color': '#FFFFFF',
            'font': '微软雅黑',
            'h_position': 0.5,
            'v_position': 0.5,
            'style': 'single',
            'spacing': 50,
            'format': 'PNG',
            'quality': 90
        }
    
    def _apply_watermark(self, image, settings, settings_panel):
        """应用水印到图片上"""
        import traceback
        print("=== 开始应用水印 ===")
        
        # 尝试调用设置面板中可能存在的apply_watermark方法
        if hasattr(settings_panel, 'apply_watermark'):
            try:
                print("尝试使用设置面板的apply_watermark方法")
                return settings_panel.apply_watermark(image, settings)
            except UnicodeEncodeError as e:
                print(f"设置面板的apply_watermark方法出现编码错误(UnicodeEncodeError): {e}")
                print("检测到中文字符编码问题，直接使用本地水印实现")
                # 直接跳过，使用本地实现
            except Exception as e:
                print(f"设置面板的apply_watermark方法失败: {type(e).__name__}: {e}")
                # 记录但继续使用本地实现
        
        # 如果设置面板没有提供方法，则使用默认实现
        try:
            from PIL import Image, ImageDraw, ImageFont
            import os
            import sys
            
            # 创建图像副本
            watermarked = image.copy()
            draw = ImageDraw.Draw(watermarked)
            
            # 获取水印文本和设置，确保安全处理
            text = settings.get('text', '')
            # 确保文本是安全的字符串，防止编码问题
            try:
                safe_text = str(text) if text else ''
                print(f"水印文本: {repr(safe_text)}")
                # 验证文本是否能被正确编码
                test_encode = safe_text.encode('utf-8').decode('utf-8')
                print(f"文本UTF-8验证成功")
            except Exception as e:
                print(f"文本处理失败: {type(e).__name__}: {e}")
                # 使用安全的默认文本
                safe_text = "Watermark"
                print(f"使用默认文本: {safe_text}")
            
            font_size = settings.get('size', 30)
            opacity = int(settings.get('opacity', 0.5) * 255)  # 转换为0-255范围
            rotation = settings.get('rotation', 0)
            color_str = settings.get('color', '#FFFFFF')
            style = settings.get('style', 'single')
            spacing = settings.get('spacing', 20)
            
            # 新增：获取字体样式和效果设置
            bold = settings.get('bold', False)
            italic = settings.get('italic', False)
            shadow = settings.get('shadow', False)
            stroke = settings.get('stroke', False)
            stroke_width = settings.get('stroke_width', 2)
            stroke_color_str = settings.get('stroke_color', '#000000')
            
            print(f"水印设置: 字体大小={font_size}, 不透明度={opacity}, 旋转={rotation}, 样式={style}")
            print(f"文本效果设置: 粗体={bold}, 斜体={italic}, 阴影={shadow}, 描边={stroke}, 描边宽度={stroke_width}")
            
            # 将十六进制颜色转换为RGBA元组，添加错误处理
            try:
                # 移除#号（如果有）
                color_str = str(color_str).lstrip('#')
                # 转换为RGB
                r = int(color_str[0:2], 16)
                g = int(color_str[2:4], 16)
                b = int(color_str[4:6], 16)
                # 创建RGBA颜色
                color = (r, g, b, opacity)
                print(f"颜色转换成功: {color}")
            except Exception as e:
                print(f"颜色转换失败: {type(e).__name__}: {e}")
                # 默认使用白色半透明
                color = (255, 255, 255, 128)
                print(f"使用默认颜色: {color}")
            
            # 解析描边颜色
            try:
                stroke_color_str = stroke_color_str.lstrip('#')
                sr = int(stroke_color_str[0:2], 16)
                sg = int(stroke_color_str[2:4], 16)
                sb = int(stroke_color_str[4:6], 16)
                stroke_color = (sr, sg, sb, opacity)
                print(f"描边颜色转换成功: {stroke_color}")
            except Exception as e:
                print(f"描边颜色转换错误: {e}")
                stroke_color = (0, 0, 0, opacity)
            
            # 尝试加载字体，如果失败使用默认字体
            font = None
            font_options = []
            
            # 根据bold和italic属性构建字体选项列表
            if bold and italic:
                # 粗斜体
                font_options = [f"{settings.get('font', 'Arial')}:bold:italic", f"{settings.get('font', 'Arial')}-BoldItalic"]
            elif bold:
                # 粗体
                font_options = [f"{settings.get('font', 'Arial')}:bold", f"{settings.get('font', 'Arial')}-Bold"]
            elif italic:
                # 斜体
                font_options = [f"{settings.get('font', 'Arial')}:italic", f"{settings.get('font', 'Arial')}-Italic"]
            
            # 添加基本字体作为后备选项
            font_names = font_options + [settings.get('font', '微软雅黑'), 'Microsoft YaHei', 'SimHei', 'Arial']
            font_paths = ['C:/Windows/Fonts/msyh.ttf', 'C:/Windows/Fonts/simhei.ttf']  # Windows常见中文字体路径，优先微软雅黑
                
            # 先尝试字体路径
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        print(f"成功加载字体文件: {font_path}")
                        break
                except Exception as e:
                    print(f"加载字体文件失败 {font_path}: {type(e).__name__}: {e}")
            
            # 如果没有找到字体文件，尝试字体名称
            if font is None:
                for font_name in font_names:
                    try:
                        # 尝试直接加载字体名称
                        font = ImageFont.truetype(font_name, font_size)
                        print(f"成功加载字体名称: {font_name}")
                        # 测试是否能正确渲染文本
                        try:
                            temp_img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
                            temp_draw = ImageDraw.Draw(temp_img)
                            test_char = safe_text[:1] if safe_text else 'A'
                            temp_draw.text((0, 0), test_char, font=font, fill=color)
                            print(f"字体渲染测试成功")
                            break
                        except Exception as render_e:
                            print(f"字体渲染测试失败: {type(render_e).__name__}: {render_e}")
                            font = None
                            continue
                    except Exception as e:
                        print(f"加载字体名称失败 {font_name}: {type(e).__name__}: {e}")
                        # 尝试添加.ttf后缀
                        try:
                            ttf_name = f"{font_name}.ttf"
                            font = ImageFont.truetype(ttf_name, font_size)
                            print(f"成功加载字体文件: {ttf_name}")
                            break
                        except Exception as e2:
                            print(f"加载ttf字体失败 {ttf_name}: {type(e2).__name__}: {e2}")
            # 如果所有字体都加载失败，使用默认字体
            if font is None:
                try:
                    font = ImageFont.load_default()
                    print("使用默认字体")
                except Exception as e:
                    print(f"加载默认字体失败: {type(e).__name__}: {e}")
                    font = None  # 允许font为None，让绘制函数处理
            
            # 根据不同的水印样式应用
            try:
                if style == "single":
                    # 单个水印
                    print("应用单个水印")
                    self._apply_single_watermark(draw, watermarked.size, safe_text, font, color, opacity, 
                                                settings.get('h_position', 0.5), settings.get('v_position', 0.5), rotation,
                                                shadow=shadow, stroke=stroke, stroke_width=stroke_width, stroke_color=stroke_color)
                else:
                    print(f"使用单个水印")
                    self._apply_single_watermark(draw, watermarked.size, safe_text, font, color, opacity, 
                                                settings.get('h_position', 0.5), settings.get('v_position', 0.5), rotation,
                                                shadow=shadow, stroke=stroke, stroke_width=stroke_width, stroke_color=stroke_color)
            except Exception as e:
                print(f"应用水印样式失败: {type(e).__name__}: {e}")
                traceback.print_exc()
                # 尝试最简单的备用方案：在图片角落添加文本
                try:
                    print("尝试备用水印方案")
                    if font:
                        draw.text((10, 10), safe_text, font=font, fill=color)
                    else:
                        draw.text((10, 10), safe_text, fill=color)
                    print("备用水印方案应用成功")
                except Exception as e2:
                    print(f"备用水印方案也失败: {type(e2).__name__}: {e2}")
            
            print("=== 水印应用完成 ===")
            return watermarked
        except Exception as e:
            print(f"整个水印应用过程失败: {type(e).__name__}: {e}")
            traceback.print_exc()
            # 如果整个过程失败，返回原始图像的副本
            return image.copy()
    
    def _draw_text_with_effects(self, draw, position, text, font, fill, shadow=False, stroke=False, stroke_width=2, stroke_fill=(0,0,0,255)):
        """
        绘制带有效果的文本
        
        Args:
            draw: ImageDraw对象
            position: 文本位置 (x, y)
            text: 要绘制的文本
            font: ImageFont对象
            fill: 文本颜色 (RGBA元组)
            shadow: 是否添加阴影
            stroke: 是否添加描边
            stroke_width: 描边宽度
            stroke_fill: 描边颜色 (RGBA元组)
        """
        x, y = position
        
        print(f"绘制文本效果: 阴影={shadow}, 描边={stroke}, 描边宽度={stroke_width}")
        
        # 绘制阴影
        if shadow:
            shadow_color = (0, 0, 0, int(fill[3] * 0.5))  # 半透明黑色阴影
            # 绘制阴影（右下方偏移）
            draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
        
        # 绘制描边 - 使用更有效的方法
        if stroke:
            # 对于较新版本的PIL，可以使用stroke_width参数
            try:
                # 尝试使用PIL的描边功能（如果可用）
                draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
                print("使用PIL内置描边功能")
                return  # 已经绘制了文本和描边，直接返回
            except TypeError:
                # 如果stroke_width参数不可用，使用传统方法
                print("使用传统描边方法")
                # 简化的描边实现，只绘制必要的像素
                for offset in range(1, stroke_width + 1):
                    # 四个主要方向
                    draw.text((x - offset, y), text, font=font, fill=stroke_fill)
                    draw.text((x + offset, y), text, font=font, fill=stroke_fill)
                    draw.text((x, y - offset), text, font=font, fill=stroke_fill)
                    draw.text((x, y + offset), text, font=font, fill=stroke_fill)
                    
                    # 四个对角线方向（仅对宽度>1有效）
                    if offset > 1:
                        draw.text((x - offset, y - offset), text, font=font, fill=stroke_fill)
                        draw.text((x + offset, y - offset), text, font=font, fill=stroke_fill)
                        draw.text((x - offset, y + offset), text, font=font, fill=stroke_fill)
                        draw.text((x + offset, y + offset), text, font=font, fill=stroke_fill)
        
        # 绘制主文本
        draw.text((x, y), text, font=font, fill=fill)
        print("主文本绘制完成")
        
    def _apply_single_watermark(self, draw, image_size, text, font, color, opacity, h_position, v_position, rotation, shadow=False, stroke=False, stroke_width=2, stroke_color=(0,0,0,255)):
        """
        应用单个水印
        """
        from PIL import Image, ImageDraw, ImageFont
        import traceback
        
        # 创建临时图像来绘制文字
        temp_img = Image.new('RGBA', image_size, (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 确保文本是安全的字符串
        safe_text = str(text) if text else ''
        print(f"应用水印文本: {repr(safe_text)}, 位置: ({h_position}, {v_position}), 旋转: {rotation}")
        print(f"应用文本效果: 阴影={shadow}, 描边={stroke}, 描边宽度={stroke_width}")
        
        # 获取文本尺寸
        text_width, text_height = 100, 30  # 默认大小
        try:
            # 优先使用textbbox，这是较新版本PIL推荐的方式
            # 安全地计算文本边界框
            try:
                bbox = temp_draw.textbbox((0, 0), safe_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                print(f"文本尺寸计算成功: {text_width}x{text_height}")
            except Exception as e:
                print(f"文本边界框计算失败: {type(e).__name__}: {e}")
                # 如果失败，尝试使用textsize（旧版本PIL）
                try:
                    text_width, text_height = temp_draw.textsize(safe_text, font=font)
                    print(f"使用textsize计算成功: {text_width}x{text_height}")
                except Exception as e2:
                    print(f"文本尺寸计算失败，使用默认值: {type(e2).__name__}: {e2}")
        except Exception as e:
            print(f"获取文本尺寸出错: {type(e).__name__}: {e}")
        
        # 计算水印位置
        x = max(0, int((image_size[0] - text_width) * h_position))
        y = max(0, int((image_size[1] - text_height) * v_position))
        print(f"计算水印位置: ({x}, {y})")
        
        # 如果需要旋转
        if rotation != 0:
            try:
                # 创建足够大的文本图像以容纳旋转后的文本
                max_dim = max(text_width, text_height)
                padding = 20
                text_img = Image.new('RGBA', (max_dim + padding, max_dim + padding), (255, 255, 255, 0))
                text_draw = ImageDraw.Draw(text_img)
                
                # 绘制文本到中心位置
                center_x = (text_img.width - text_width) // 2
                center_y = (text_img.height - text_height) // 2
                print(f"绘制旋转文本到临时图像中心: ({center_x}, {center_y})")
                
                # 使用_draw_text_with_effects方法绘制带效果的文本
                try:
                    self._draw_text_with_effects(text_draw, (center_x, center_y), safe_text, font, color, 
                                               shadow=shadow, stroke=stroke, stroke_width=stroke_width, 
                                               stroke_fill=stroke_color)
                except Exception as e:
                    print(f"绘制旋转文本失败: {type(e).__name__}: {e}")
                    # 降级方案：尝试不带字体绘制
                    try:
                        text_draw.text((center_x, center_y), safe_text, fill=color)
                        print("降级到无字体绘制成功")
                    except Exception as e2:
                        print(f"无字体绘制也失败: {type(e2).__name__}: {e2}")
                
                # 旋转文本图像
                rotated = text_img.rotate(rotation, expand=True)
                
                # 计算旋转后的位置
                rot_x = x - (rotated.width - text_width) // 2
                rot_y = y - (rotated.height - text_height) // 2
                
                # 确保位置有效
                rot_x = max(0, rot_x)
                rot_y = max(0, rot_y)
                print(f"旋转后位置: ({rot_x}, {rot_y})")
                
                # 粘贴旋转后的文本
                temp_img.paste(rotated, (rot_x, rot_y), rotated)
            except Exception as e:
                print(f"旋转水印处理失败: {type(e).__name__}: {e}")
                traceback.print_exc()
                # 降级到不旋转直接绘制
                try:
                    print(f"降级到不旋转绘制，应用文本效果")
                    self._draw_text_with_effects(temp_draw, (x, y), safe_text, font, color, 
                                               shadow=shadow, stroke=stroke, stroke_width=stroke_width, 
                                               stroke_fill=stroke_color)
                    print("降级到不旋转绘制成功")
                except Exception as e2:
                    print(f"降级绘制失败: {type(e2).__name__}: {e2}")
        else:
            # 直接绘制文本，使用_draw_text_with_effects方法
            try:
                print(f"直接绘制文本到位置: ({x}, {y})，应用文本效果")
                self._draw_text_with_effects(temp_draw, (x, y), safe_text, font, color, 
                                           shadow=shadow, stroke=stroke, stroke_width=stroke_width, 
                                           stroke_fill=stroke_color)
            except Exception as e:
                print(f"直接绘制文本失败: {type(e).__name__}: {e}")
                # 降级方案：尝试不带字体绘制
                try:
                    temp_draw.text((x, y), safe_text, fill=color)
                    print("降级到无字体绘制成功")
                except Exception as e2:
                    print(f"无字体绘制也失败: {type(e2).__name__}: {e2}")
        
        # 将临时图像合并到原图
        try:
            draw.bitmap((0, 0), temp_img, fill=None)
        except Exception as e:
            print(f"bitmap方法失败: {type(e).__name__}: {e}")
            # 如果bitmap方法失败，尝试其他方法
            try:
                draw.bitmap((0, 0), temp_img)
                print("降级bitmap方法成功")
            except Exception as e2:
                print(f"降级bitmap方法也失败: {type(e2).__name__}: {e2}")
                # 最后尝试直接在原图上绘制文本作为备用
                try:
                    draw.text((x, y), safe_text, font=font, fill=color)
                    print("备用方案：直接在原图绘制成功")
                except Exception as e3:
                    print(f"备用方案也失败: {type(e3).__name__}: {e3}")