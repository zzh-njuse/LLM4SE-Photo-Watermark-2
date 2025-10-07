# src/gui/settings_panel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QComboBox, QSlider, QPushButton, QColorDialog, QFrame,
                             QRadioButton, QGroupBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class SettingsPanel(QWidget):
    """
    右侧设置面板，用于配置水印的各种属性
    """
    def __init__(self, parent=None):
        super(SettingsPanel, self).__init__(parent)
        self.init_ui()
        self.watermark_color = '#000000'  # 默认黑色
        # 存储已应用的设置
        self.applied_settings = self._get_current_settings()
    
    def init_ui(self):
        """初始化设置面板UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标题
        title_label = QLabel("水印设置")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333333;")
        layout.addWidget(title_label)
        
        # 添加分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 水印文本设置
        self._add_text_settings(layout)
        
        # 字体设置
        self._add_font_settings(layout)
        
        # 水印样式设置
        self._add_style_settings(layout)
        
        # 输出设置
        self._add_output_settings(layout)
        
        # 添加垂直拉伸
        layout.addStretch()
    
    def _add_text_settings(self, layout):
        """添加水印文本相关设置"""
        group_box = QGroupBox("文本设置")
        group_layout = QVBoxLayout()
        
        # 水印文本输入
        text_layout = QVBoxLayout()
        text_label = QLabel("水印文本")
        self.watermark_text = QLineEdit("我的图片")
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.watermark_text)
        group_layout.addLayout(text_layout)
        
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
    
    def _add_font_settings(self, layout):
        """添加字体相关设置"""
        # 字体选择
        font_layout = QHBoxLayout()
        font_label = QLabel("字体")
        self.font_combo = QComboBox()
        # 添加一些常用字体
        self.font_combo.addItems(["微软雅黑", "宋体", "黑体", "Arial", "Times New Roman"])
        font_layout.addWidget(font_label, 1)
        font_layout.addWidget(self.font_combo, 2)
        layout.addLayout(font_layout)
        
        # 字体大小
        size_layout = QHBoxLayout()
        size_label = QLabel("字体大小")
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 100)
        self.size_slider.setValue(30)
        self.size_value = QLabel("30px")
        self.size_slider.valueChanged.connect(lambda value: self.size_value.setText(f"{value}px"))
        size_layout.addWidget(size_label, 1)
        size_layout.addWidget(self.size_slider, 2)
        size_layout.addWidget(self.size_value, 1)
        layout.addLayout(size_layout)
        
        # 透明度
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("透明度")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        self.opacity_value = QLabel("50%")
        self.opacity_slider.valueChanged.connect(lambda value: self.opacity_value.setText(f"{value}%"))
        opacity_layout.addWidget(opacity_label, 1)
        opacity_layout.addWidget(self.opacity_slider, 2)
        opacity_layout.addWidget(self.opacity_value, 1)
        layout.addLayout(opacity_layout)
        
        # 旋转角度
        rotation_layout = QHBoxLayout()
        rotation_label = QLabel("旋转角度")
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(-180, 180)
        self.rotation_slider.setValue(0)
        self.rotation_value = QLabel("0°")
        self.rotation_slider.valueChanged.connect(lambda value: self.rotation_value.setText(f"{value}°"))
        rotation_layout.addWidget(rotation_label, 1)
        rotation_layout.addWidget(self.rotation_slider, 2)
        rotation_layout.addWidget(self.rotation_value, 1)
        layout.addLayout(rotation_layout)
        
        # 水印颜色
        color_layout = QHBoxLayout()
        color_label = QLabel("水印颜色")
        self.color_button = QPushButton()
        self.color_button.setFixedWidth(30)
        self.color_button.setStyleSheet("background-color: #FFFFFF; border: 1px solid #CCCCCC;")
        self.color_button.clicked.connect(self.select_color)
        self.color_value = QLineEdit("#FFFFFF")
        color_layout.addWidget(color_label, 1)
        color_layout.addWidget(self.color_button, 1)
        color_layout.addWidget(self.color_value, 2)
        layout.addLayout(color_layout)
    
    def _add_style_settings(self, layout):
        """添加水印样式相关设置"""
        # 位置设置
        position_layout = QHBoxLayout()
        h_label = QLabel("水平位置")
        self.h_position_slider = QSlider(Qt.Horizontal)
        self.h_position_slider.setRange(0, 100)
        self.h_position_slider.setValue(50)
        self.h_position_value = QLabel("50%")
        self.h_position_slider.valueChanged.connect(lambda value: self.h_position_value.setText(f"{value}%"))
        
        v_label = QLabel("垂直位置")
        self.v_position_slider = QSlider(Qt.Horizontal)
        self.v_position_slider.setRange(0, 100)
        self.v_position_slider.setValue(50)
        self.v_position_value = QLabel("50%")
        self.v_position_slider.valueChanged.connect(lambda value: self.v_position_value.setText(f"{value}%"))
        
        position_layout.addWidget(h_label, 1)
        position_layout.addWidget(self.h_position_slider, 2)
        position_layout.addWidget(self.h_position_value, 1)
        layout.addLayout(position_layout)
        
        v_pos_layout = QHBoxLayout()
        v_pos_layout.addWidget(v_label, 1)
        v_pos_layout.addWidget(self.v_position_slider, 2)
        v_pos_layout.addWidget(self.v_position_value, 1)
        layout.addLayout(v_pos_layout)
        
        # 水印样式
        style_group = QGroupBox("水印样式")
        style_layout = QVBoxLayout()
        
        self.single_radio = QRadioButton("单个水印")
        self.single_radio.setChecked(True)
        self.tile_radio = QRadioButton("平铺水印")
        self.diagonal_radio = QRadioButton("对角线水印")
        
        style_layout.addWidget(self.single_radio)
        style_layout.addWidget(self.tile_radio)
        style_layout.addWidget(self.diagonal_radio)
        
        # 水印间距（仅在平铺或对角线模式下有效）
        spacing_layout = QHBoxLayout()
        spacing_label = QLabel("水印间距")
        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(10, 200)
        self.spacing_slider.setValue(50)
        self.spacing_value = QLabel("50px")
        self.spacing_slider.valueChanged.connect(lambda value: self.spacing_value.setText(f"{value}px"))
        
        spacing_layout.addWidget(spacing_label, 1)
        spacing_layout.addWidget(self.spacing_slider, 2)
        spacing_layout.addWidget(self.spacing_value, 1)
        style_layout.addLayout(spacing_layout)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
    
    def _add_output_settings(self, layout):
        """添加输出相关设置"""
        # 输出格式
        format_layout = QHBoxLayout()
        format_label = QLabel("输出格式")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG"])
        format_layout.addWidget(format_label, 1)
        format_layout.addWidget(self.format_combo, 2)
        layout.addLayout(format_layout)
        
        # 图片质量
        quality_layout = QHBoxLayout()
        quality_label = QLabel("图片质量")
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(0, 100)
        self.quality_slider.setValue(90)
        self.quality_value = QLabel("90%")
        self.quality_slider.valueChanged.connect(lambda value: self.quality_value.setText(f"{value}%"))
        quality_layout.addWidget(quality_label, 1)
        quality_layout.addWidget(self.quality_slider, 2)
        quality_layout.addWidget(self.quality_value, 1)
        layout.addLayout(quality_layout)
    
    def select_color(self):
        """选择水印颜色"""
        color = QColorDialog.getColor(Qt.white, self, "选择水印颜色")
        if color.isValid():
            self.color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #CCCCCC;")
            self.color_value.setText(color.name())
    
    def apply_watermark(self, image, settings):
        """应用水印到图片上，水印位置始终在图片正中央"""
        from PIL import Image, ImageDraw, ImageFont
        import os
        import sys
        
        # 创建图像副本
        watermarked = image.copy()
        draw = ImageDraw.Draw(watermarked)
        
        # 获取水印文本和设置
        text = settings.get('text', '')
        font_size = settings.get('size', 30)
        opacity = int(settings.get('opacity', 0.5) * 255)  # 转换为0-255范围
        color_str = settings.get('color', '#FFFFFF')
        
        # 将十六进制颜色转换为RGBA元组
        try:
            # 移除#号（如果有）
            color_str = color_str.lstrip('#')
            # 转换为RGB
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            # 创建RGBA颜色
            color = (r, g, b, opacity)
        except:
            # 默认使用白色
            color = (255, 255, 255, opacity)
        
        # 尝试加载字体，确保中文能正确显示
        font = None
        try:
            # 尝试多种中文字体
            font_names = [settings.get('font', 'Microsoft YaHei'), 'SimHei', 'Microsoft YaHei', 'Arial']
            for font_name in font_names:
                try:
                    # 尝试直接加载字体名称
                    font = ImageFont.truetype(font_name, font_size)
                    break
                except:
                    try:
                        # 尝试添加.ttf后缀
                        font = ImageFont.truetype(f"{font_name}.ttf", font_size)
                        break
                    except:
                        continue
        except:
            pass
        
        # 如果所有字体都加载失败，使用默认字体
        if font is None:
            font = ImageFont.load_default()
        
        # 确保文本不为空
        if text.strip():
            # 创建临时图像来绘制文字
            temp_img = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 获取文本尺寸
            try:
                # 优先使用textbbox
                bbox = temp_draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except Exception as e:
                # 如果失败，使用默认大小
                text_width, text_height = 100, 30
            
            # 计算水印位置 - 始终在正中央
            x = (watermarked.size[0] - text_width) // 2
            y = (watermarked.size[1] - text_height) // 2
            
            # 直接绘制文本到中央位置
            draw.text((x, y), text, font=font, fill=color)
        
        return watermarked
    
    def get_watermark_text(self):
        """
        获取水印文本
        """
        if hasattr(self, 'watermark_text') and self.watermark_text:
            return self.watermark_text.text()
        return "我的图片"
    
    def _get_current_settings(self):
        """
        获取当前界面上的所有设置值
        """
        settings = {
            'text': self.watermark_text.text() if hasattr(self, 'watermark_text') else "我的图片",
            'size': self.size_slider.value() if hasattr(self, 'size_slider') else 30,
            'opacity': self.opacity_slider.value() / 100.0 if hasattr(self, 'opacity_slider') else 0.5,
            'rotation': self.rotation_slider.value() if hasattr(self, 'rotation_slider') else 0,
            'color': self.color_value.text() if hasattr(self, 'color_value') else '#FFFFFF',
            'font': self.font_combo.currentText() if hasattr(self, 'font_combo') else '微软雅黑',
            'h_position': self.h_position_slider.value() / 100.0 if hasattr(self, 'h_position_slider') else 0.5,
            'v_position': self.v_position_slider.value() / 100.0 if hasattr(self, 'v_position_slider') else 0.5,
            'style': 'single',
            'spacing': self.spacing_slider.value() if hasattr(self, 'spacing_slider') else 50,
            'format': self.format_combo.currentText() if hasattr(self, 'format_combo') else 'PNG',
            'quality': self.quality_slider.value() if hasattr(self, 'quality_slider') else 90
        }
        
        # 设置水印样式
        if hasattr(self, 'tile_radio') and self.tile_radio.isChecked():
            settings['style'] = 'tile'
        elif hasattr(self, 'diagonal_radio') and self.diagonal_radio.isChecked():
            settings['style'] = 'diagonal'
        
        return settings
    
    def apply_settings(self):
        """
        应用当前设置，将当前设置保存到applied_settings
        """
        self.applied_settings = self._get_current_settings()
        print(f"设置已应用: {self.applied_settings}")
        return self.applied_settings
    
    def get_applied_settings(self):
        """
        获取已应用的设置
        """
        return self.applied_settings if hasattr(self, 'applied_settings') else self._get_current_settings()
