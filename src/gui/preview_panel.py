# src/gui/preview_panel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QPushButton, QFrame, QScrollArea, QSplitter, QFileDialog)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QUrl
from src.core.image_processor import ImageProcessor
from src.core.file_handler import FileHandler
import os
from io import BytesIO
import traceback



class PreviewPanel(QWidget):
    """
    中央预览面板，用于显示原图和水印效果预览
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_image_path = ""
        self.original_image = None
        self.watermark_image = None
        # 启用拖放功能
        self.setAcceptDrops(True)
        
        # 确保所有属性都已初始化
        self.effect_preview = None
        self.original_preview = None
        
        # 拖拽相关变量
        self.is_dragging = False
        self.last_pos = None
        self.watermark_rect = None  # 水印在预览图中的矩形区域
        # 新增属性：跟踪鼠标是否在水印区域上方
        self._is_mouse_over_watermark = False
        

        
        self.init_ui()
        
        # 启用鼠标追踪
        self.setMouseTracking(True)
    
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
        layout.addWidget(self.upload_area, 4)  # 使用4作为拉伸因子
        
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
        
        # 设置预览标签的固定大小 - 放大预览窗口
        self.original_preview = QLabel("上传后显示原图")
        self.original_preview.setAlignment(Qt.AlignCenter)
        self.original_preview.setFixedSize(550, 450)  # 放大预览窗口大小
        self.original_preview.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; border: 1px solid #dddddd;")
        self.original_preview.setScaledContents(True)  # 允许图片自动缩放填充区域
        
        original_layout.addWidget(original_title)
        original_layout.addWidget(self.original_preview, alignment=Qt.AlignCenter)  # 居中显示
        
        # 效果预览 - 设置固定大小
        effect_container = QWidget()
        effect_container.setStyleSheet("background: transparent; border: none;")
        effect_layout = QVBoxLayout(effect_container)
        
        effect_title = QLabel("水印效果预览")
        effect_title.setAlignment(Qt.AlignCenter)
        effect_title.setStyleSheet("font-weight: bold; background: transparent; border: none;")
        
        # 设置预览标签的固定大小 - 放大预览窗口
        self.effect_preview = QLabel("此处实时预览效果")
        self.effect_preview.setAlignment(Qt.AlignCenter)
        self.effect_preview.setFixedSize(550, 450)  # 放大预览窗口大小
        self.effect_preview.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; border: 1px solid #dddddd;")
        self.effect_preview.setScaledContents(True)  # 允许图片自动缩放填充区域
        
        effect_layout.addWidget(effect_title)
        effect_layout.addWidget(self.effect_preview, alignment=Qt.AlignCenter)  # 居中显示
        
        # 添加到对比布局
        compare_layout.addWidget(original_container, 1)
        compare_layout.addWidget(effect_container, 1)
        
        # 将对比预览容器添加到主布局
        layout.addWidget(preview_container, 6)  # 使用6作为拉伸因子
        
        # 连接鼠标事件

        self.effect_preview.mousePressEvent = self.on_mouse_press
        self.effect_preview.mouseMoveEvent = self.on_mouse_move
        self.effect_preview.mouseReleaseEvent = self.on_mouse_release
        self.effect_preview.mouseDoubleClickEvent = self.on_mouse_double_click
        # 启用鼠标追踪，确保不按下鼠标也能接收移动事件
        self.effect_preview.setMouseTracking(True)

        

    
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
    
    def update_preview(self, force_update=False):
        """
        更新预览（例如在应用水印后）
        """

        # 确保effect_preview存在
        if not hasattr(self, 'effect_preview') or self.effect_preview is None:

            return
        
        if self.current_image_path:
    
            self.set_preview_image(self.current_image_path)
            self.update_watermark_preview()
            
        # 强制更新，确保UI组件正确显示
        self.effect_preview.update()
        self.effect_preview.repaint()
            
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
                
            # 保存原始图像副本
            self.original_image = image.copy()
            
            # 应用水印，获取水印图片和水印位置信息
            watermarked, watermark_rect = self._apply_watermark(image, settings)
            
            # 保存水印图像
            self.watermark_image = watermarked.copy()
            
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
                    
                    # 计算缩放后的水印矩形位置
                    if watermark_rect:
                        scale_x = scaled_pixmap.width() / width
                        scale_y = scaled_pixmap.height() / height
                        scaled_rect = (watermark_rect[0] * scale_x, watermark_rect[1] * scale_y, 
                                      watermark_rect[2] * scale_x, watermark_rect[3] * scale_y)
                        
                        # 计算相对于预览标签的位置
                        x_offset = (self.effect_preview.width() - scaled_pixmap.width()) // 2
                        y_offset = (self.effect_preview.height() - scaled_pixmap.height()) // 2
                        
                        self.watermark_rect = (scaled_rect[0] + x_offset, scaled_rect[1] + y_offset, 
                                              scaled_rect[2], scaled_rect[3])
                        print(f"DEBUG: 水印矩形区域(预览窗口): {self.watermark_rect}")
                        print(f"DEBUG: 预览窗口尺寸: {self.effect_preview.width()}x{self.effect_preview.height()}")
                        print(f"DEBUG: 图片缩放后尺寸: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
                        print(f"DEBUG: 偏移量: ({x_offset}, {y_offset})")
                    else:
                        # 当没有水印矩形时，根据设置的位置参数和水印属性计算更准确的水印判定区域
                        try:
                
                            
                            # 获取当前的水印设置
                            settings = self._get_watermark_settings()
                            h_position = settings.get('h_position', 0.5)
                            v_position = settings.get('v_position', 0.5)
                            text = settings.get('text', 'Watermark')
                            base_font_size = settings.get('size', 30)
                            rotation = settings.get('rotation', 0)
                            
                            # 计算预览窗口尺寸
                            window_width = self.effect_preview.width()
                            window_height = self.effect_preview.height()
                            
                            # 计算更准确的水印大小
                            # 首先估算文本宽度和高度（基于字体大小和文本长度）
                            text_length = len(str(text))
                            # 根据字体大小和文本长度估算宽度
                            estimated_width = max(50, min(int(base_font_size * 0.6 * text_length), window_width // 2))
                            # 高度通常是字体大小的约1.2倍
                            estimated_height = max(30, min(int(base_font_size * 1.2), window_height // 2))
                            
                            # 如果有旋转，需要考虑旋转后的大小变化
                            if rotation != 0:
                                # 旋转会增加所需空间，特别是接近90度时
                                import math
                                angle_rad = abs(math.radians(rotation))
                                # 计算旋转后的最小包围矩形尺寸
                                rotated_width = int(estimated_width * math.cos(angle_rad) + estimated_height * math.sin(angle_rad))
                                rotated_height = int(estimated_width * math.sin(angle_rad) + estimated_height * math.cos(angle_rad))
                                estimated_width = max(estimated_width, rotated_width)
                                estimated_height = max(estimated_height, rotated_height)
                            
                            # 根据位置设置计算水印区域中心
                            center_x = int(h_position * window_width)
                            center_y = int(v_position * window_height)
                            
                            # 计算水印区域左上角坐标
                            temp_x = center_x - estimated_width // 2
                            temp_y = center_y - estimated_height // 2
                            
                            # 确保不超出窗口边界
                            temp_x = max(0, min(temp_x, window_width - estimated_width))
                            temp_y = max(0, min(temp_y, window_height - estimated_height))
                            
                            # 设置临时水印矩形区域
                            self.watermark_rect = (temp_x, temp_y, estimated_width, estimated_height)
                            print(f"DEBUG: 根据位置设置({h_position}, {v_position})和水印属性计算的临时水印矩形区域: {self.watermark_rect}")
                        except Exception as e:
                            print(f"DEBUG: 计算临时水印矩形区域失败: {e}")
                            # 降级到简单计算
                            try:
                                settings = self._get_watermark_settings()
                                h_position = settings.get('h_position', 0.5)
                                v_position = settings.get('v_position', 0.5)
                                window_width = self.effect_preview.width()
                                window_height = self.effect_preview.height()
                                # 根据水印大小设置动态调整判定区域大小
                                base_size = settings.get('size', 30)
                                # 大小与字体大小成正比，但有上下限
                                dynamic_width = max(50, min(int(base_size * 3), window_width // 2))
                                dynamic_height = max(30, min(int(base_size * 1.5), window_height // 2))
                                
                                center_x = int(h_position * window_width)
                                center_y = int(v_position * window_height)
                                temp_x = center_x - dynamic_width // 2
                                temp_y = center_y - dynamic_height // 2
                                
                                temp_x = max(0, min(temp_x, window_width - dynamic_width))
                                temp_y = max(0, min(temp_y, window_height - dynamic_height))
                                
                                self.watermark_rect = (temp_x, temp_y, dynamic_width, dynamic_height)
                                print(f"DEBUG: 使用降级方案计算的临时水印矩形区域: {self.watermark_rect}")
                            except:
                                self.watermark_rect = None
                else:
                    print("没有effect_preview属性")
            except Exception as e:
                print(f"DEBUG: 图像转换为QPixmap失败: {str(e)}")
                self.watermark_rect = None
        
                # 降级方案：如果转换失败，直接显示调试图片
                try:
                    from PyQt5.QtGui import QPixmap, QImage
                    from PyQt5.QtCore import Qt
                    
                    debug_image_path = 'debug_watermarked.png'
                    if os.path.exists(debug_image_path) and hasattr(self, 'effect_preview'):
                        print(f"DEBUG: 降级方案：直接加载调试图片 {debug_image_path}")
                        debug_pixmap = QPixmap(debug_image_path)
                        scaled_pixmap = debug_pixmap.scaled(
                            self.effect_preview.size(), 
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.effect_preview.setPixmap(scaled_pixmap)
                        print("降级方案：直接加载调试图片")
                except Exception as inner_e:
                    print(f"降级方案也失败: {str(inner_e)}")
                # 无论如何都设置可拖拽光标
                if hasattr(self, 'effect_preview'):
                    self.effect_preview.setCursor(Qt.OpenHandCursor)
        
        except Exception as e:
            print(f"DEBUG: 更新水印预览时出错: {str(e)}")
            self.watermark_rect = None
    
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
    
    def on_mouse_press(self, event):
        """处理鼠标按下事件"""
        print(f"DEBUG: 鼠标按下事件触发，按钮: {event.button()}, 位置: ({event.pos().x()}, {event.pos().y()})")
        
        # 确保effect_preview存在
        if not hasattr(self, 'effect_preview') or self.effect_preview is None:

            return
        
        # 只有左键点击并且在水印区域内才开始拖拽
        if event.button() == Qt.LeftButton and self._is_point_in_watermark(event.pos()):
            
            # 设置拖拽状态
            self.is_dragging = True
            self.last_pos = event.pos()
            
            # 更改光标为拖拽状态
            self.effect_preview.setCursor(Qt.ClosedHandCursor)
            
            
            # 立即更新一次位置
            try:
                # 直接调用update_watermark_position方法
                self._update_watermark_position(event.pos())
            except Exception as e:
                print(f"DEBUG: 点击时更新位置出错: {e}")
                traceback.print_exc()
        else:
            if event.button() == Qt.LeftButton:
                pass
    
            else:
                pass
        
    
    def _update_watermark_position(self, pos):
        """更新水印位置的辅助方法，实现实时拖拽预览并更新判定区域"""
        print(f"DEBUG: 更新水印位置，鼠标坐标: ({pos.x()}, {pos.y()})")
        
        # 首先检查effect_preview是否存在且有效
        if not hasattr(self, 'effect_preview') or self.effect_preview is None:
    
            return
        
        # 获取预览窗口尺寸
        window_width = self.effect_preview.width()
        window_height = self.effect_preview.height()
        mouse_x = pos.x()
        mouse_y = pos.y()
        print(f"DEBUG: 预览窗口尺寸: ({window_width}, {window_height})")
        
        if window_width <= 0 or window_height <= 0:
    
            return
        
        # 转换为0-1的坐标比例（更适合直接用于图像绘制）
        h_ratio = min(1.0, max(0.0, mouse_x / window_width))
        v_ratio = min(1.0, max(0.0, mouse_y / window_height))
        print(f"DEBUG: 转换为比例位置: ({h_ratio}, {v_ratio})")
        
        # 转换为0-100的百分比整数（用于设置面板）
        h_percent = int(h_ratio * 100)
        v_percent = int(v_ratio * 100)
        print(f"DEBUG: 转换为百分比位置: ({h_percent}, {v_percent})")
        
        # 步骤1: 更新设置（确保持久化）
        try:
            # 获取当前设置
            settings = self._get_watermark_settings()
            
            # 更新为新位置
            settings['h_position'] = h_ratio
            settings['v_position'] = v_ratio
            print(f"DEBUG: 已更新设置: h_position={h_ratio}, v_position={v_ratio}")
        except Exception as e:
            print(f"DEBUG: 更新设置失败: {e}")
        
        # 步骤2: 更新设置面板中的位置（持久化设置）
        # 方式1: 通过main_window获取settings_panel
        settings_updated = False
        if hasattr(self, 'main_window') and self.main_window:
    
            if hasattr(self.main_window, 'settings_panel') and self.main_window.settings_panel:
                settings_panel = self.main_window.settings_panel
                
                try:
                    # 更新水平位置滑块
                    if hasattr(settings_panel, 'horizontal_position_slider') and settings_panel.horizontal_position_slider:
                        settings_panel.horizontal_position_slider.setValue(h_percent)
                        
                    # 更新垂直位置滑块
                    if hasattr(settings_panel, 'vertical_position_slider') and settings_panel.vertical_position_slider:
                        settings_panel.vertical_position_slider.setValue(v_percent)
                        
                    print(f"DEBUG: 直接更新settings_panel滑块值: h={h_percent}, v={v_percent}")
                    settings_updated = True
                except Exception as e:
                    print(f"DEBUG: 更新settings_panel滑块失败: {e}")
                    
                # 尝试使用预设位置方法
                if hasattr(settings_panel, 'set_preset_position'):
                    try:
                        print(f"DEBUG: 调用main_window.settings_panel.set_preset_position({h_percent}, {v_percent})")
                        settings_panel.set_preset_position(h_percent, v_percent)
                        settings_updated = True
                    except Exception as e:
                        print(f"DEBUG: 调用set_preset_position失败: {e}")
            else:
                pass
        
        # 方式2: 通过parent获取settings_panel
        elif hasattr(self, 'parent') and self.parent:
    
            if hasattr(self.parent, 'settings_panel') and self.parent.settings_panel:
                settings_panel = self.parent.settings_panel
                
                try:
                    # 更新水平位置滑块
                    if hasattr(settings_panel, 'horizontal_position_slider') and settings_panel.horizontal_position_slider:
                        settings_panel.horizontal_position_slider.setValue(h_percent)
                        
                    # 更新垂直位置滑块
                    if hasattr(settings_panel, 'vertical_position_slider') and settings_panel.vertical_position_slider:
                        settings_panel.vertical_position_slider.setValue(v_percent)
                        
                    print(f"DEBUG: 直接更新parent.settings_panel滑块值: h={h_percent}, v={v_percent}")
                    settings_updated = True
                except Exception as e:
                    print(f"DEBUG: 更新parent.settings_panel滑块失败: {e}")
                    
                # 尝试使用预设位置方法
                if hasattr(settings_panel, 'set_preset_position'):
                    try:
                        print(f"DEBUG: 调用parent.settings_panel.set_preset_position({h_percent}, {v_percent})")
                        settings_panel.set_preset_position(h_percent, v_percent)
                        settings_updated = True
                    except Exception as e:
                        print(f"DEBUG: 调用set_preset_position失败: {e}")
            else:
                pass
        
        # 步骤3: 立即刷新预览（确保水印位置更新并更新判定区域）
        try:
    
            self.update_watermark_preview()
            
            # 确保update_watermark_preview后有足够时间更新watermark_rect
            # 检查是否成功更新了水印矩形区域
            if hasattr(self, 'watermark_rect') and self.watermark_rect is not None:
                print(f"DEBUG: 水印矩形区域已更新为: {self.watermark_rect}")
            else:
        
                
                # 直接计算一个合理的水印区域作为临时方案
                # 假设水印大小为预览窗口的1/3
                temp_width = max(50, window_width // 3)
                temp_height = max(30, window_height // 3)
                
                # 计算基于鼠标位置的水印区域
                temp_x = mouse_x - temp_width // 2
                temp_y = mouse_y - temp_height // 2
                
                # 确保不超出窗口边界
                temp_x = max(0, min(temp_x, window_width - temp_width))
                temp_y = max(0, min(temp_y, window_height - temp_height))
                
                # 直接设置临时水印矩形区域
                self.watermark_rect = (temp_x, temp_y, temp_width, temp_height)
                print(f"DEBUG: 已设置临时水印矩形区域: {self.watermark_rect}")
            
        except Exception as e:
            print(f"DEBUG: 刷新预览失败: {e}")
            traceback.print_exc()
            
            # 出错时，使用直接计算的临时水印区域
            try:
                temp_width = max(50, window_width // 3)
                temp_height = max(30, window_height // 3)
                temp_x = mouse_x - temp_width // 2
                temp_y = mouse_y - temp_height // 2
                temp_x = max(0, min(temp_x, window_width - temp_width))
                temp_y = max(0, min(temp_y, window_height - temp_height))
                self.watermark_rect = (temp_x, temp_y, temp_width, temp_height)
                print(f"DEBUG: 出错时设置临时水印矩形区域: {self.watermark_rect}")
            except:
                pass
        
        print(f"DEBUG: 水印位置更新完成，设置更新状态: {settings_updated}")
    
    def on_mouse_move(self, event):
        """处理鼠标移动事件"""
        print(f"DEBUG: 鼠标移动事件触发，位置: ({event.pos().x()}, {event.pos().y()})")
        
        # 确保effect_preview存在
        if not hasattr(self, 'effect_preview') or self.effect_preview is None:

            return
        
        # 检查鼠标是否在水印区域内
        is_over_watermark = self._is_point_in_watermark(event.pos())
        self._is_mouse_over_watermark = is_over_watermark
        print(f"DEBUG: 鼠标在水印区域内: {is_over_watermark}")
        
        # 检查拖拽状态
        is_dragging = hasattr(self, 'is_dragging') and self.is_dragging
        has_last_pos = hasattr(self, 'last_pos') and self.last_pos
        print(f"DEBUG: is_dragging: {is_dragging}, has_last_pos: {has_last_pos}")
        
        if is_dragging and has_last_pos:

            
            # 使用辅助方法更新位置
            try:
                self._update_watermark_position(event.pos())
                # 更新last_pos
                self.last_pos = event.pos()
                print(f"DEBUG: 更新last_pos到: ({event.pos().x()}, {event.pos().y()})")
            except Exception as e:
                print(f"DEBUG: 更新水印位置时出错: {e}")
                traceback.print_exc()
        else:
            # 根据鼠标是否在水印区域来改变光标样式
            if is_over_watermark:
                self.effect_preview.setCursor(Qt.OpenHandCursor)

            else:
                self.effect_preview.setCursor(Qt.ArrowCursor)

    
    def on_mouse_release(self, event):
        """处理鼠标释放事件"""
        print(f"DEBUG: 鼠标释放事件触发，按钮: {event.button()}")
        
        if event.button() == Qt.LeftButton and hasattr(self, 'is_dragging') and self.is_dragging:
            
            self.is_dragging = False
            self.last_pos = None
            if hasattr(self, 'effect_preview'):
                # 释放后根据鼠标位置设置光标
                if self._is_point_in_watermark(event.pos()):
                    self.effect_preview.setCursor(Qt.OpenHandCursor)
            
                else:
                    self.effect_preview.setCursor(Qt.ArrowCursor)
            
    
    def on_mouse_double_click(self, event):
        """处理鼠标双击事件，重置水印位置到中心"""
        print(f"DEBUG: 鼠标双击事件触发，位置: ({event.pos().x()}, {event.pos().y()})")
        
        if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'settings_panel'):
            settings_panel = self.parent.settings_panel
            if hasattr(settings_panel, 'set_preset_position'):
    
                settings_panel.set_preset_position(50, 50)
    
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
                    settings = panel.get_applied_settings()
                    print(f"DEBUG: 成功获取已应用设置: {settings}")
                    return settings
            except Exception as e:
                print(f"DEBUG: 获取已应用设置失败: {str(e)}")
                import traceback
                traceback.print_exc()
        
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
        
        Returns:
            tuple: (watermarked_image, watermark_rect) - 水印图片和水印位置矩形
        """
        import traceback

        print(f"设置内容: {settings}")
        
        # 直接测试颜色转换逻辑
        color_str = settings.get('color', '#FFFFFF')
        opacity = int(settings.get('opacity', 0.5) * 255)
        print(f"\n===== 直接颜色测试开始 =====")
        print(f"输入颜色: {color_str}, 不透明度: {opacity}")
        
        try:
            # 移除#号（如果有）
            color_str = str(color_str).lstrip('#')
            print(f"处理后颜色字符串: {color_str}")
            # 转换为RGB
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            print(f"RGB值: R={r}, G={g}, B={b}")
            # 创建RGBA颜色
            test_color = (r, g, b, opacity)
            print(f"测试颜色转换结果: {test_color}")
        except Exception as e:
            print(f"测试颜色转换失败: {type(e).__name__}: {e}")
        
        # 尝试调用设置面板中可能存在的apply_watermark方法
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'settings_panel'):
            panel = self.main_window.settings_panel
            if hasattr(panel, 'apply_watermark'):
                try:
                    print("尝试使用设置面板的apply_watermark方法")
                    result = panel.apply_watermark(image, settings)
                    # 兼容原有的单返回值和新的双返回值
                    if isinstance(result, tuple) and len(result) == 2:
                        return result
                    else:
                        return result, None  # 原方法只返回图片，位置信息为None
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
            
            # 获取所有文本效果相关的设置
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
            
            # 将十六进制颜色转换为RGBA元组，添加更详细的错误处理和调试
            print("===== 颜色处理开始 =====")
            print(f"输入颜色值: {color_str}, 不透明度: {opacity}")
            try:
                # 移除#号（如果有）
                color_str = str(color_str).lstrip('#')
                print(f"处理后的颜色字符串: {color_str}")
                # 确保颜色字符串长度正确
                if len(color_str) != 6:
                    raise ValueError(f"颜色字符串长度不正确: {color_str}")
                # 转换为RGB
                r = int(color_str[0:2], 16)
                g = int(color_str[2:4], 16)
                b = int(color_str[4:6], 16)
                print(f"RGB值: R={r}, G={g}, B={b}")
                # 确保值在有效范围内
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    raise ValueError(f"颜色值超出范围: R={r}, G={g}, B={b}")
                # 创建RGBA颜色
                color = (r, g, b, opacity)
                print(f"===== 颜色转换成功: {color} =====")
            except Exception as e:
                print(f"===== 颜色转换失败: {type(e).__name__}: {e} =====")
                # 默认使用白色半透明
                color = (255, 255, 255, 128)
                print(f"使用默认颜色: {color}")
            
            # 解析描边颜色
            try:
                stroke_color_str = str(stroke_color_str).lstrip('#')
                # 确保颜色字符串长度正确
                if len(stroke_color_str) != 6:
                    raise ValueError(f"描边颜色字符串长度不正确: {stroke_color_str}")
                sr = int(stroke_color_str[0:2], 16)
                sg = int(stroke_color_str[2:4], 16)
                sb = int(stroke_color_str[4:6], 16)
                # 确保值在有效范围内
                if not (0 <= sr <= 255 and 0 <= sg <= 255 and 0 <= sb <= 255):
                    raise ValueError(f"描边颜色值超出范围: R={sr}, G={sg}, B={sb}")
                stroke_color = (sr, sg, sb, 255)  # 描边通常使用完全不透明
                print(f"描边颜色转换成功: {stroke_color}")
            except Exception as e:
                print(f"描边颜色转换错误: {type(e).__name__}: {e}")
                stroke_color = (0, 0, 0, 255)  # 默认黑色描边
            
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
                        print(f"尝试加载字体: {font_name}")
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
            
            watermark_rect = None
            # 根据不同的水印样式应用
            try:
                if style == "single":
                    # 单个水印
                    print("应用单个水印")
                    watermark_rect = self._apply_single_watermark(draw, watermarked.size, safe_text, font, color, opacity, 
                                                settings.get('h_position', 0.5), settings.get('v_position', 0.5), rotation,
                                                shadow=shadow, stroke=stroke, stroke_width=stroke_width, stroke_color=stroke_color)
                else:
                    print(f"使用单个水印")
                    watermark_rect = self._apply_single_watermark(draw, watermarked.size, safe_text, font, color, opacity, 
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
                    # 备用水印位置在左上角
                    watermark_rect = (10, 10, 100, 30)  # 估算的大小
                except Exception as e2:
                    print(f"备用水印方案也失败: {type(e2).__name__}: {e2}")
            
            print("=== 水印应用完成(预览) ===")
            return watermarked, watermark_rect
        except Exception as e:
            print(f"整个水印应用过程失败: {type(e).__name__}: {e}")
            traceback.print_exc()
            # 如果整个过程失败，返回原始图像的副本和None位置
            return image.copy(), None
    
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
        
        print("===== 文本绘制开始 =====")
        print(f"绘制文本: 位置={position}, 文本={repr(text)}, 颜色={fill}, 阴影={shadow}, 描边={stroke}, 描边颜色={stroke_fill}")
        
        # 验证颜色参数格式
        if not isinstance(fill, (tuple, list)) or len(fill) != 4:
            print(f"警告: 颜色格式不正确: {fill}，使用默认颜色")
            fill = (255, 255, 255, 255)
        
        if not isinstance(stroke_fill, (tuple, list)) or len(stroke_fill) != 4:
            print(f"警告: 描边颜色格式不正确: {stroke_fill}，使用默认描边颜色")
            stroke_fill = (0, 0, 0, 255)
        
        # 绘制阴影
        if shadow:
            shadow_color = (0, 0, 0, int(fill[3] * 0.5))  # 半透明黑色阴影
            print(f"绘制阴影: 颜色={shadow_color}, 偏移=(+2,+2)")
            # 绘制阴影（右下方偏移）
            draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
        
        # 绘制描边 - 使用更有效的方法
        if stroke:
            print(f"绘制描边: 宽度={stroke_width}, 颜色={stroke_fill}")
            # 对于较新版本的PIL，可以使用stroke_width参数
            try:
                # 尝试使用PIL的描边功能（如果可用）
                draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
                print("使用PIL内置描边功能，同时绘制了文本和描边")
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
        
        # 绘制主文本 - 确保直接使用传入的颜色
        print(f"绘制主文本: 颜色={fill}")
        # 为了确保颜色正确应用，我们直接使用传入的颜色值，不做任何修改
        draw.text((x, y), text, font=font, fill=fill)
        print(f"主文本绘制完成，颜色={fill}已应用")
        
    def _apply_single_watermark(self, draw, image_size, text, font, color, opacity, h_position, v_position, rotation, shadow=False, stroke=False, stroke_width=2, stroke_color=(0,0,0,255)):
        """
        应用单个水印
        
        Returns:
            tuple: (x, y, width, height) - 水印位置和尺寸
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
        
        final_x, final_y, final_width, final_height = x, y, text_width, text_height
        
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
                
                # 更新最终位置和尺寸为旋转后的
                final_x, final_y, final_width, final_height = rot_x, rot_y, rotated.width, rotated.height
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
        
        # 返回水印的位置和尺寸
        return (final_x, final_y, final_width, final_height)
    
    def _apply_tile_watermark(self, draw, image_size, text, font, color, opacity, spacing, rotation, 
                             shadow=False, stroke=False, stroke_width=2, stroke_color=(0,0,0,255)):
        # 水印方法已简化，只使用单个水印功能
        pass

    def _is_point_in_watermark(self, pos):
        """
        判断给定位置是否在水印区域内
        
        Args:
            pos: QPoint对象，表示鼠标位置
            
        Returns:
            bool: 如果在水印区域内返回True，否则返回False
        """
        # 检查watermark_rect是否存在且有效
        if not hasattr(self, 'watermark_rect') or self.watermark_rect is None:

            # 当水印矩形区域未设置时，使用水印设置计算一个更准确的默认水印区域
            if hasattr(self, 'effect_preview') and self.effect_preview:
                try:
                    # 获取当前的水印设置
                    settings = self._get_watermark_settings()
                    h_position = settings.get('h_position', 0.5)
                    v_position = settings.get('v_position', 0.5)
                    text = settings.get('text', 'Watermark')
                    base_font_size = settings.get('size', 30)
                    rotation = settings.get('rotation', 0)
                    
                    # 计算预览窗口尺寸
                    window_width = self.effect_preview.width()
                    window_height = self.effect_preview.height()
                    
                    # 计算更准确的水印大小
                    text_length = len(str(text))
                    # 根据字体大小和文本长度估算宽度
                    estimated_width = max(50, min(int(base_font_size * 0.6 * text_length), window_width // 2))
                    # 高度通常是字体大小的约1.2倍
                    estimated_height = max(30, min(int(base_font_size * 1.2), window_height // 2))
                    
                    # 如果有旋转，需要考虑旋转后的大小变化
                    if rotation != 0:
                        import math
                        angle_rad = abs(math.radians(rotation))
                        # 计算旋转后的最小包围矩形尺寸
                        rotated_width = int(estimated_width * math.cos(angle_rad) + estimated_height * math.sin(angle_rad))
                        rotated_height = int(estimated_width * math.sin(angle_rad) + estimated_height * math.cos(angle_rad))
                        estimated_width = max(estimated_width, rotated_width)
                        estimated_height = max(estimated_height, rotated_height)
                    
                    # 根据位置设置计算水印区域中心
                    center_x = int(h_position * window_width)
                    center_y = int(v_position * window_height)
                    
                    # 计算水印区域左上角坐标
                    default_x = center_x - estimated_width // 2
                    default_y = center_y - estimated_height // 2
                    
                    # 确保不超出窗口边界
                    default_x = max(0, min(default_x, window_width - estimated_width))
                    default_y = max(0, min(default_y, window_height - estimated_height))
                    
                    # 设置默认水印矩形区域大小
                    default_width = estimated_width
                    default_height = estimated_height
                    
                    print(f"DEBUG: 计算的默认水印矩形区域: ({default_x}, {default_y}, {default_width}, {default_height})")
                except Exception as e:
                    print(f"DEBUG: 计算默认水印矩形区域失败，使用降级方案: {e}")
                    # 降级到简单计算
                    window_width = self.effect_preview.width()
                    window_height = self.effect_preview.height()
                    # 根据水印大小设置动态调整判定区域大小
                    try:
                        settings = self._get_watermark_settings()
                        base_size = settings.get('size', 30)
                        # 大小与字体大小成正比，但有上下限
                        default_width = max(50, min(int(base_size * 3), window_width // 2))
                        default_height = max(30, min(int(base_size * 1.5), window_height // 2))
                    except:
                        # 最终降级到固定比例
                        default_width = max(50, window_width // 3)
                        default_height = max(30, window_height // 3)
                    
                    # 获取位置设置
                    try:
                        settings = self._get_watermark_settings()
                        h_position = settings.get('h_position', 0.5)
                        v_position = settings.get('v_position', 0.5)
                        center_x = int(h_position * window_width)
                        center_y = int(v_position * window_height)
                        default_x = center_x - default_width // 2
                        default_y = center_y - default_height // 2
                    except:
                        # 最终降级到中心位置
                        default_x = (window_width - default_width) // 2
                        default_y = (window_height - default_height) // 2
                    
                    # 确保不超出窗口边界
                    default_x = max(0, min(default_x, window_width - default_width))
                    default_y = max(0, min(default_y, window_height - default_height))
                
                # 检查鼠标是否在默认区域内
                mouse_x, mouse_y = pos.x(), pos.y()
                is_in_default = (default_x <= mouse_x <= default_x + default_width) and \
                               (default_y <= mouse_y <= default_y + default_height)
                print(f"DEBUG: 鼠标位置({mouse_x}, {mouse_y})是否在默认水印区域({default_x}, {default_y}, {default_width}, {default_height})内: {is_in_default}")
                return is_in_default
            return False
        
        try:
            # 解包水印矩形区域
            x, y, width, height = self.watermark_rect
            mouse_x, mouse_y = pos.x(), pos.y()
            
            # 计算是否在矩形范围内
            is_in_rect = (x <= mouse_x <= x + width) and (y <= mouse_y <= y + height)
            print(f"DEBUG: 鼠标位置({mouse_x}, {mouse_y})是否在水印区域({x}, {y}, {width}, {height})内: {is_in_rect}")
            return is_in_rect
        except Exception as e:
            print(f"DEBUG: 判断鼠标是否在水印区域内时出错: {e}")
            traceback.print_exc()
            # 出错时，使用与水印矩形不存在时相同的默认行为
            if hasattr(self, 'effect_preview') and self.effect_preview:
                window_width = self.effect_preview.width()
                window_height = self.effect_preview.height()
                default_width = max(50, window_width // 3)
                default_height = max(30, window_height // 3)
                default_x = (window_width - default_width) // 2
                default_y = (window_height - default_height) // 2
                
                mouse_x, mouse_y = pos.x(), pos.y()
                return (default_x <= mouse_x <= default_x + default_width) and \
                       (default_y <= mouse_y <= default_y + default_height)
            return False
