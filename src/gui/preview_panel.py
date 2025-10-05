# src/gui/preview_panel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QPushButton, QFrame, QScrollArea, QSplitter)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class PreviewPanel(QWidget):
    """
    中央预览面板，用于显示原图和水印效果预览
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化预览面板UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建带有虚线框的上传区域 - 只保留这一个虚线框
        self.upload_area = QFrame()
        # 明确设置只有外层有虚线框
        self.upload_area.setStyleSheet("border: 2px dashed #cccccc; border-radius: 8px; background: transparent;")
        
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
        
        # 然后是选择按钮
        select_button = QPushButton("选择图片")
        select_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px 20px; font-size: 14px; border: none;")
        
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
        
        # 原图预览
        original_container = QWidget()
        original_container.setStyleSheet("background: transparent; border: none;")
        original_layout = QVBoxLayout(original_container)
        
        original_title = QLabel("原图")
        original_title.setAlignment(Qt.AlignCenter)
        original_title.setStyleSheet("font-weight: bold; background: transparent; border: none;")
        
        self.original_preview = QLabel("上传后显示原图")
        self.original_preview.setAlignment(Qt.AlignCenter)
        self.original_preview.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; border: none;")
        
        original_layout.addWidget(original_title)
        original_layout.addWidget(self.original_preview, 1)
        
        # 效果预览
        effect_container = QWidget()
        effect_container.setStyleSheet("background: transparent; border: none;")
        effect_layout = QVBoxLayout(effect_container)
        
        effect_title = QLabel("水印效果预览")
        effect_title.setAlignment(Qt.AlignCenter)
        effect_title.setStyleSheet("font-weight: bold; background: transparent; border: none;")
        
        self.effect_preview = QLabel("此处实时预览效果")
        self.effect_preview.setAlignment(Qt.AlignCenter)
        self.effect_preview.setStyleSheet("background-color: #f5f5f5; border-radius: 4px; border: none;")
        
        effect_layout.addWidget(effect_title)
        effect_layout.addWidget(self.effect_preview, 1)
        
        # 添加到对比布局
        compare_layout.addWidget(original_container, 1)
        compare_layout.addWidget(effect_container, 1)
        
        # 将预览容器添加到主布局，使用相同的拉伸因子确保高度一致
        layout.addWidget(preview_container, 1)
    
    def set_preview_image(self, image_path):
        """设置预览图片"""
        pixmap = QPixmap(image_path)
        
        # 调整图片大小以适应预览区域
        scaled_pixmap = pixmap.scaled(
            self.original_preview.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # 设置原图预览
        self.original_preview.setPixmap(scaled_pixmap)
        
        # 目前效果预览与原图相同，后续会添加水印效果
        self.effect_preview.setPixmap(scaled_pixmap)