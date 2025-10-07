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
        
        # 批量处理选项
        batch_label = QLabel("批量处理:")
        self.batch_combo = QComboBox()
        self.batch_combo.addItems(["当前图片", "所有图片"])
        layout.addWidget(batch_label)
        layout.addWidget(self.batch_combo)
        
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
        
        # 获取批量处理选项
        batch_mode = self.batch_combo.currentText()
        
        # 获取预览面板和设置面板
        preview_panel = getattr(self.main_window, 'preview_panel', None)
        settings_panel = getattr(self.main_window, 'settings_panel', None)
        image_list_panel = getattr(self.main_window, 'image_list_panel', None)
        
        if not preview_panel or not settings_panel:
            return
        
        # 确定要导出的图片列表
        if batch_mode == "当前图片":
            # 仅导出当前图片
            if not preview_panel.current_image_path:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "导出失败", "没有选中的图片可供导出")
                return
            image_paths = [preview_panel.current_image_path]
        else:
            # 导出所有图片
            if not image_list_panel or not image_list_panel.image_paths:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "导出失败", "图片列表为空")
                return
            image_paths = image_list_panel.image_paths.copy()
        
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
        
        # 确保输出文件夹不是原始图片所在的文件夹
        if batch_mode == "所有图片" and image_list_panel and image_paths:
            # 获取第一张图片的目录作为参考
            first_img_dir = os.path.dirname(image_paths[0])
            if output_dir == first_img_dir:
                reply = QMessageBox.question(self, "确认导出", 
                                           "您正在导出到原始图片所在的文件夹，这可能会覆盖文件。确定继续吗？",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
        
        try:
            # 获取水印设置
            watermark_settings = self._get_watermark_settings(settings_panel)
            
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
                    output_path = FileHandler.generate_output_filename(image_path, output_dir, "_watermark")
                    
                    # 根据选择的格式进行保存
                    output_format = watermark_settings['format'].lower()
                    quality = watermark_settings['quality']
                    
                    # 确保在保存前转换为RGB模式，特别是对于JPEG格式
                    if output_format in ['jpg', 'jpeg']:
                        print(f"将图片转换为RGB模式以保存为JPEG格式")
                        watermarked_image = ImageProcessor.convert_to_rgb(watermarked_image)
                    
                    # 保存图片
                    success = FileHandler.save_image(watermarked_image, output_path, output_format.upper(), quality)
                    
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
        # 优先使用已应用的设置
        if hasattr(settings_panel, 'get_applied_settings'):
            return settings_panel.get_applied_settings()
        
        # 备用方案：如果没有已应用的设置，则直接从UI组件获取
        text = getattr(settings_panel, 'watermark_text', None)
        text = text.text() if text else ""
        
        font = getattr(settings_panel, 'font_combo', None)
        font = font.currentText() if font else "Arial"
        
        size = getattr(settings_panel, 'size_slider', None)
        size = size.value() if size else 30
        
        opacity = getattr(settings_panel, 'opacity_slider', None)
        opacity = opacity.value() / 100 if opacity else 0.5  # 转换为0-1范围
        
        rotation = getattr(settings_panel, 'rotation_slider', None)
        rotation = rotation.value() if rotation else 0
        
        color_value = getattr(settings_panel, 'color_value', None)
        color = color_value.text() if color_value else "#FFFFFF"
        
        # 获取位置设置
        h_position = getattr(settings_panel, 'h_position_slider', None)
        h_position = h_position.value() / 100 if h_position else 0.5  # 转换为0-1范围
        
        v_position = getattr(settings_panel, 'v_position_slider', None)
        v_position = v_position.value() / 100 if v_position else 0.5  # 转换为0-1范围
        
        # 获取样式设置
        style = "single"
        tile_radio = getattr(settings_panel, 'tile_radio', None)
        diagonal_radio = getattr(settings_panel, 'diagonal_radio', None)
        
        if tile_radio and tile_radio.isChecked():
            style = "tile"
        elif diagonal_radio and diagonal_radio.isChecked():
            style = "diagonal"
        
        spacing = getattr(settings_panel, 'spacing_slider', None)
        spacing = spacing.value() if spacing else 20
        
        # 获取输出设置
        format_combo = getattr(settings_panel, 'format_combo', None)
        format = format_combo.currentText() if format_combo else "PNG"
        
        quality_slider = getattr(settings_panel, 'quality_slider', None)
        quality = quality_slider.value() if quality_slider else 90
        
        return {
            'text': text,
            'font': font,
            'size': size,
            'opacity': opacity,
            'rotation': rotation,
            'color': color,
            'h_position': h_position,
            'v_position': v_position,
            'style': style,
            'spacing': spacing,
            'format': format,
            'quality': quality
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
            
            print(f"水印设置: 字体大小={font_size}, 不透明度={opacity}, 旋转={rotation}, 样式={style}")
            
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
            
            # 尝试加载字体，如果失败使用默认字体
            font = None
            # 尝试多种字体加载方式，确保中文能正确显示
            try:
                # 尝试直接使用系统字体
                font_names = [settings.get('font', 'Arial'), 'SimHei', 'Microsoft YaHei', 'Arial']
                font_paths = ['C:/Windows/Fonts/simhei.ttf', 'C:/Windows/Fonts/msyh.ttf']  # Windows常见中文字体路径
                
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
            except Exception as e:
                print(f"字体加载过程异常: {type(e).__name__}: {e}")
                traceback.print_exc()
            
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
                                                settings.get('h_position', 0.5), settings.get('v_position', 0.5), rotation)
                elif style == "tile":
                    # 平铺水印
                    print("应用平铺水印")
                    self._apply_tile_watermark(draw, watermarked.size, safe_text, font, color, opacity, spacing, rotation)
                elif style == "diagonal":
                    # 对角线水印
                    print("应用对角线水印")
                    self._apply_diagonal_watermark(draw, watermarked.size, safe_text, font, color, opacity, spacing, rotation)
                else:
                    print(f"未知水印样式: {style}，使用单个水印")
                    self._apply_single_watermark(draw, watermarked.size, safe_text, font, color, opacity, 
                                                settings.get('h_position', 0.5), settings.get('v_position', 0.5), rotation)
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
    
    def _apply_single_watermark(self, draw, image_size, text, font, color, opacity, h_position, v_position, rotation):
        """应用单个水印"""
        from PIL import Image, ImageDraw, ImageFont
        import traceback
        
        # 创建临时图像来绘制文字
        temp_img = Image.new('RGBA', image_size, (255, 255, 255, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 确保文本是安全的字符串
        safe_text = str(text) if text else ''
        print(f"应用水印文本: {repr(safe_text)}, 位置: ({h_position}, {v_position}), 旋转: {rotation}")
        
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
                
                # 安全地绘制文本
                try:
                    text_draw.text((center_x, center_y), safe_text, font=font, fill=color)
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
                    temp_draw.text((x, y), safe_text, font=font, fill=color)
                    print("降级到不旋转绘制成功")
                except Exception as e2:
                    print(f"降级绘制失败: {type(e2).__name__}: {e2}")
        else:
            # 直接绘制文本
            try:
                print(f"直接绘制文本到位置: ({x}, {y})")
                temp_draw.text((x, y), safe_text, font=font, fill=color)
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
    
    def _apply_tile_watermark(self, draw, image_size, text, font, color, opacity, spacing, rotation):
        """应用平铺水印"""
        # 简化实现，创建多个单个水印
        step_x = image_size[0] // 3 + spacing
        step_y = image_size[1] // 3 + spacing
        
        for x in range(0, image_size[0], step_x):
            for y in range(0, image_size[1], step_y):
                # 计算相对位置
                h_pos = x / image_size[0]
                v_pos = y / image_size[1]
                # 应用单个水印，注意这里直接传递color参数，不需要单独传递opacity
                self._apply_single_watermark(draw, image_size, text, font, color, opacity, h_pos, v_pos, rotation)
    
    def _apply_diagonal_watermark(self, draw, image_size, text, font, color, opacity, spacing, rotation):
        """应用对角线水印"""
        # 简化实现，沿对角线创建水印
        # 调整旋转角度使其更适合对角线
        adjusted_rotation = rotation + 45
        
        # 创建足够长的对角线覆盖
        diagonal_length = int((image_size[0]**2 + image_size[1]** 2)**0.5)
        step = diagonal_length // 5 + spacing
        
        for offset in range(-diagonal_length, diagonal_length, step):
            # 计算起点和终点
            start_x = offset
            start_y = 0
            end_x = min(offset + diagonal_length, image_size[0])
            end_y = min(diagonal_length, image_size[1])
            
            # 在对角线位置应用水印
            if start_x < image_size[0] and start_y < image_size[1]:
                h_pos = min(max(start_x / image_size[0], 0), 1)
                v_pos = min(max(start_y / image_size[1], 0), 1)
                # 应用单个水印，注意这里直接传递color参数，不需要单独传递opacity
                self._apply_single_watermark(draw, image_size, text, font, color, opacity, h_pos, v_pos, adjusted_rotation)