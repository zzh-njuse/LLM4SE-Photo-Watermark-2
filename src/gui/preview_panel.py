# src/gui/preview_panel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QPushButton, QFrame, QScrollArea, QSplitter, QFileDialog)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QUrl
from src.core.image_processor import ImageProcessor
from src.core.file_handler import FileHandler
import os
from io import BytesIO

class PreviewPanel(QWidget):
    """
    中央预览面板，用于显示原图和水印效果预览
    """
    def __init__(self):
        super().__init__()
        self.current_image_path = ""
        # 启用拖放功能
        self.setAcceptDrops(True)
        self.init_ui()
    
    def init_ui(self):
        """初始化预览面板UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建带有虚线框的上传区域 - 只保留这一个虚线框
        self.upload_area = QFrame()
        # 明确设置只有外层有虚线框
        self.upload_area.setStyleSheet("border: 2px dashed #cccccc; border-radius: 8px; background: transparent;")
        # 启用上传区域的拖放功能
        self.upload_area.setAcceptDrops(True)
        
        # 创建上传区域的布局
        upload_layout = QVBoxLayout(self.upload_area)
        upload_layout.setContentsMargins(20, 20, 20, 20)
        upload_layout.setAlignment(Qt.AlignCenter)
        
        # 上部分：拖放提示 - 明确设置无边框
        top_section = QWidget()
        # 使用更明确的样式确保没有边框
        top_section.setStyleSheet("background: transparent; border: none; outline: none;")
        top_layout = QVBoxLayout(top_section)
        top_layout.setAlignment(Qt.AlignCenter)
        
        # 确保图片居中显示
        icon_label = QLabel("🖼️")
        icon_label.setStyleSheet("font-size: 48px; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        text_label = QLabel("拖放您的照片到这里")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("background: transparent; border: none;")
        
        top_layout.addWidget(icon_label)
        top_layout.addWidget(text_label)
        
        # 修改：将"或者"和"选择图片"按钮分开在两行
        # 首先是"或者"标签
        or_label = QLabel("或者")
        or_label.setStyleSheet("background: transparent; border: none;")
        or_label.setAlignment(Qt.AlignCenter)
        
        # 然后是选择按钮 - 添加点击事件连接
        select_button = QPushButton("选择图片")
        select_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px 20px; font-size: 14px; border: none;")
        select_button.clicked.connect(self.on_select_image)
        
        # 添加隐私提示 - 明确设置无边框
        privacy_label = QLabel("您的图片将在本地处理，不会上传至服务器")
        privacy_label.setStyleSheet("color: #666666; font-size: 12px; background: transparent; border: none;")
        privacy_label.setAlignment(Qt.AlignCenter)
        
        # 将所有部分添加到上传区域布局 - 直接添加而不是放在容器中
        upload_layout.addWidget(top_section)
        upload_layout.addSpacing(10)  # 添加一些间距
        upload_layout.addWidget(or_label)  # 单独的"或者"标签
        upload_layout.addSpacing(10)  # 添加一些间距
        upload_layout.addWidget(select_button, alignment=Qt.AlignCenter)  # 单独的选择按钮，居中对齐
        upload_layout.addSpacing(15)  # 添加一些间距
        upload_layout.addWidget(privacy_label)
        
        # 设置上传区域的最小高度
        self.upload_area.setMinimumHeight(300)
        
        # 将上传区域添加到主布局
        layout.addWidget(self.upload_area, 1)  # 使用1作为拉伸因子
        
        # 创建分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 创建对比预览区域容器
        preview_container = QWidget()
        preview_container.setMinimumHeight(300)  # 设置与上传区域相同的最小高度
        compare_layout = QHBoxLayout(preview_container)
        
        # 原图预览 - 设置固定大小
        original_container = QWidget()
        original_container.setStyleSheet("background: transparent; border: none;")
        original_layout = QVBoxLayout(original_container)
        
        original_title = QLabel("原图")
        original_title.setAlignment(Qt.AlignCenter)
        original_title.setStyleSheet("font-weight: bold; background: transparent; border: none;")
        
        # 设置预览标签的固定大小
        self.original_preview = QLabel("上传后显示原图")
        self.original_preview.setAlignment(Qt.AlignCenter)
        self.original_preview.setFixedSize(350, 250)  # 设置固定大小
        self.original_preview.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; border: 1px solid #dddddd;")
        self.original_preview.setScaledContents(False)  # 确保图片不会自动缩放填充整个区域
        
        original_layout.addWidget(original_title)
        original_layout.addWidget(self.original_preview, alignment=Qt.AlignCenter)  # 居中显示
        
        # 效果预览 - 设置固定大小
        effect_container = QWidget()
        effect_container.setStyleSheet("background: transparent; border: none;")
        effect_layout = QVBoxLayout(effect_container)
        
        effect_title = QLabel("水印效果预览")
        effect_title.setAlignment(Qt.AlignCenter)
        effect_title.setStyleSheet("font-weight: bold; background: transparent; border: none;")
        
        # 设置预览标签的固定大小
        self.effect_preview = QLabel("此处实时预览效果")
        self.effect_preview.setAlignment(Qt.AlignCenter)
        self.effect_preview.setFixedSize(350, 250)  # 设置固定大小
        self.effect_preview.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; border: 1px solid #dddddd;")
        self.effect_preview.setScaledContents(False)  # 确保图片不会自动缩放填充整个区域
        
        effect_layout.addWidget(effect_title)
        effect_layout.addWidget(self.effect_preview, alignment=Qt.AlignCenter)  # 居中显示
        
        # 添加到对比布局
        compare_layout.addWidget(original_container, 1)
        compare_layout.addWidget(effect_container, 1)
        
        # 将预览容器添加到主布局，使用相同的拉伸因子确保高度一致
        layout.addWidget(preview_container, 1)
    
    # 拖放事件处理方法
    def dragEnterEvent(self, event):
        """
        当拖拽进入控件时触发
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 可以在这里添加视觉反馈，如改变上传区域样式
            
    def dragMoveEvent(self, event):
        """
        当拖拽在控件上移动时触发
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """
        当在控件上释放拖拽时触发
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if FileHandler.is_supported_image(file_path):
                    self.handle_dropped_image(file_path)
                    break  # 暂时只处理第一张图片
    
    def handle_dropped_image(self, image_path):
        """
        处理拖拽的图片
        """
        self.current_image_path = image_path
        self.set_preview_image(image_path)
        
        # 使用更直接的方式通知主窗口图片已选择
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'on_image_selected'):
            self.main_window.on_image_selected(image_path)
        
        # 更新水印预览
        self.update_watermark_preview()
    
    def on_select_image(self):
        """
        处理选择图片按钮点击事件
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.tif);;所有文件 (*)", 
            options=options
        )
        
        if file_path and FileHandler.is_supported_image(file_path):
            self.current_image_path = file_path
            self.set_preview_image(file_path)
            
            # 使用更直接的方式通知主窗口图片已选择
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'on_image_selected'):
                self.main_window.on_image_selected(file_path)
            
            # 更新水印预览
            self.update_watermark_preview()
    
    def set_preview_image(self, image_path):
        """
        设置预览图片
        """
        if not os.path.exists(image_path):
            return
        
        try:
            # 使用QPixmap直接加载图片
            pixmap = QPixmap(image_path)
            
            # 使用预览标签的实际固定大小进行缩放
            # 减去一些边距以确保图片完全可见
            available_width = self.original_preview.width() - 10
            available_height = self.original_preview.height() - 10
            
            scaled_pixmap = pixmap.scaled(
                available_width, available_height, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            # 设置原图预览 - 确保在固定大小的容器内居中显示
            self.original_preview.setPixmap(scaled_pixmap)
            self.original_preview.setText("")  # 清除文本
            
            # 目前效果预览与原图相同
            self.effect_preview.setPixmap(scaled_pixmap)
            self.effect_preview.setText("")  # 清除文本
            
        except Exception as e:
            print(f"设置预览图片失败: {e}")
            self.original_preview.setText("图片加载失败")
            self.effect_preview.setText("图片加载失败")
    
    def update_preview(self):
        """
        更新预览（例如在应用水印后）
        """
        if self.current_image_path:
            self.set_preview_image(self.current_image_path)
            self.update_watermark_preview()
            
    def update_watermark_preview(self):
        """
        更新水印效果预览，使用与导出相同的设置和逻辑
        """
        print("开始更新水印预览")
        # 确保有当前图片路径
        if not hasattr(self, 'current_image_path') or not self.current_image_path:
            print("没有当前图片路径")
            return
        
        try:
            # 修复Unicode路径处理
            image_path = self.current_image_path
            # 确保路径为字符串类型
            image_path_str = str(image_path)
            print(f"处理图片路径: {image_path_str}")
            
            # 从设置面板获取所有水印设置
            settings = self._get_watermark_settings()
            
            # 尝试直接使用toolbar中的_apply_watermark方法逻辑
            from PIL import Image
            
            # 直接使用Image.open打开图片
            image = Image.open(image_path_str)
            # 确保图片是RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 应用水印
            watermarked = self._apply_watermark(image, settings)
            
            # 保存水印图片以便调试
            try:
                debug_path = 'debug_watermarked.png'
                watermarked.save(debug_path)
                print(f"调试图片已保存到: {debug_path}")
            except Exception as e:
                print(f"保存调试图片失败: {str(e)}")
            
            # 转换为QImage和QPixmap
            try:
                width, height = watermarked.size
                print(f"图片尺寸: {width}x{height}")
                # 获取原始图像数据
                data = watermarked.tobytes()
                
                # 创建QImage
                q_image = QImage(data, width, height, 3 * width, QImage.Format_RGB888)
                
                # 转换为QPixmap
                pixmap = QPixmap.fromImage(q_image)
                
                # 显示水印图片
                if hasattr(self, 'effect_preview'):
                    print("显示水印预览")
                    # 缩放并显示
                    scaled_pixmap = pixmap.scaled(
                        350, 250,  # 固定大小
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.effect_preview.setPixmap(scaled_pixmap)
                    self.effect_preview.setText("")  # 清除文本提示
                else:
                    print("没有effect_preview属性")
            except Exception as e:
                print(f"图像转换为QPixmap失败: {str(e)}")
                # 降级方案：如果转换失败，直接显示调试图片
                try:
                    from PyQt5.QtGui import QPixmap
                    from PyQt5.QtCore import Qt
                    
                    if hasattr(self, 'effect_preview'):
                        debug_pixmap = QPixmap('debug_watermarked.png')
                        scaled_pixmap = debug_pixmap.scaled(
                            350, 250, 
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.effect_preview.setPixmap(scaled_pixmap)
                        print("降级方案：直接加载调试图片")
                except Exception as inner_e:
                    print(f"降级方案也失败: {str(inner_e)}")
        
        except Exception as e:
            print(f"更新水印预览时出错: {str(e)}")
            # 使用英文错误信息避免编码问题
            if hasattr(self, 'effect_preview'):
                self.effect_preview.setText("Watermark preview error")
            import traceback
            traceback.print_exc()
            # 发生错误时至少显示原图
            if hasattr(self, 'effect_preview'):
                try:
                    from PyQt5.QtGui import QImage, QPixmap
                    from PyQt5.QtCore import Qt
                    
                    # 加载原图
                    q_image = QImage(self.current_image_path)
                    pixmap = QPixmap.fromImage(q_image)
                    scaled_pixmap = pixmap.scaled(350, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.effect_preview.setPixmap(scaled_pixmap)
                except Exception as inner_e:
                    print(f"显示原图失败: {str(inner_e)}")
                    self.effect_preview.setText("无法加载图片")
    
    def _get_watermark_settings(self):
        """
        从设置面板获取所有水印设置
        现在使用已应用的设置，而不是直接从UI组件获取值
        """
        # 尝试从设置面板获取已应用的设置
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'settings_panel'):
            try:
                panel = self.main_window.settings_panel
                # 使用已应用的设置
                if hasattr(panel, 'get_applied_settings'):
                    return panel.get_applied_settings()
            except Exception as e:
                print(f"获取已应用设置失败: {str(e)}")
        
        # 默认设置作为备用
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
    
    def _apply_watermark(self, image, settings):
        """
        应用水印到图片上，使用与toolbar.py相同的逻辑
        """
        import traceback
        print("=== 开始应用水印(预览) ===")
        
        # 尝试调用设置面板中可能存在的apply_watermark方法
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'settings_panel'):
            panel = self.main_window.settings_panel
            if hasattr(panel, 'apply_watermark'):
                try:
                    print("尝试使用设置面板的apply_watermark方法")
                    return panel.apply_watermark(image, settings)
                except UnicodeEncodeError as e:
                    print(f"设置面板的apply_watermark方法出现编码错误(UnicodeEncodeError): {e}")
                    print("检测到中文字符编码问题，直接使用本地面板的水印实现")
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
            
            # 获取字体大小并根据预览窗口比例调整，确保与导出结果一致
            base_font_size = settings.get('size', 30)
            
            # 计算预览窗口与实际图片的比例关系，调整字体大小以保持视觉一致性
            try:
                # 获取原始图片尺寸
                orig_width, orig_height = image.size
                # 预览窗口固定大小
                preview_width, preview_height = 350, 250
                
                # 计算缩放比例
                scale_factor = min(preview_width / orig_width, preview_height / orig_height)
                # 根据比例调整字体大小
                font_size = int(base_font_size * scale_factor)
                # 确保字体大小至少可读
                font_size = max(5, font_size)
                print(f"调整字体大小: 原始={base_font_size}, 比例={scale_factor:.2f}, 调整后={font_size}")
            except Exception as e:
                print(f"计算字体缩放比例失败: {e}，使用原始大小")
                font_size = base_font_size
            
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
            
            print("=== 水印应用完成(预览) ===")
            return watermarked
        except Exception as e:
            print(f"整个水印应用过程失败: {type(e).__name__}: {e}")
            traceback.print_exc()
            # 如果整个过程失败，返回原始图像的副本
            return image.copy()
    
    def _apply_single_watermark(self, draw, image_size, text, font, color, opacity, h_position, v_position, rotation):
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
        """
        应用平铺水印
        """
        # 简化实现，创建多个单个水印
        step_x = image_size[0] // 3 + spacing
        step_y = image_size[1] // 3 + spacing
        
        for x in range(0, image_size[0], step_x):
            for y in range(0, image_size[1], step_y):
                # 计算相对位置
                h_pos = x / image_size[0]
                v_pos = y / image_size[1]
                # 应用单个水印
                self._apply_single_watermark(draw, image_size, text, font, color, opacity, h_pos, v_pos, rotation)
    
    def _apply_diagonal_watermark(self, draw, image_size, text, font, color, opacity, spacing, rotation):
        """
        应用对角线水印
        """
        # 简化实现，沿对角线创建水印
        # 调整旋转角度使其更适合对角线
        adjusted_rotation = rotation + 45
        
        # 创建足够长的对角线覆盖
        diagonal_length = int((image_size[0]**2 + image_size[1]**2)**0.5)
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
                # 应用单个水印
                self._apply_single_watermark(draw, image_size, text, font, color, opacity, h_pos, v_pos, adjusted_rotation)
