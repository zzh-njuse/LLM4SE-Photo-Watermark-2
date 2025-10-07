# src/gui/settings_panel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QComboBox, QSlider, QPushButton, QColorDialog, QFrame,
                             QRadioButton, QGroupBox, QGridLayout, QMessageBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from ..core.template_manager import TemplateManager

class SettingsPanel(QWidget):
    """
    右侧设置面板，用于配置水印的各种属性
    """
    def __init__(self, parent=None):
        super(SettingsPanel, self).__init__(parent)
        # 先初始化模板管理器，确保在init_ui中可用
        self.template_manager = TemplateManager()
        self.watermark_color = '#000000'  # 默认黑色
        self.init_ui()
        # 加载初始设置
        self.load_initial_settings()
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
        
        # 模板设置
        self._add_template_settings(layout)
        
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
    
    def _add_template_settings(self, layout):
        """添加模板管理相关设置"""
        self.template_settings_group = QGroupBox("模板管理")
        template_layout = QVBoxLayout()
        
        # 模板名称输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("模板名称:"))
        self.template_name_input = QLineEdit()
        self.template_name_input.setPlaceholderText("输入模板名称")
        name_layout.addWidget(self.template_name_input)
        
        # 保存模板按钮
        self.save_template_btn = QPushButton("保存为模板")
        self.save_template_btn.clicked.connect(self._save_template)
        name_layout.addWidget(self.save_template_btn)
        
        # 已保存模板列表
        list_layout = QHBoxLayout()
        list_layout.addWidget(QLabel("已保存模板:"))
        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(200)
        self._refresh_template_list()
        list_layout.addWidget(self.template_combo)
        
        # 加载模板按钮
        self.load_template_btn = QPushButton("加载")
        self.load_template_btn.clicked.connect(self._load_template)
        list_layout.addWidget(self.load_template_btn)
        
        # 删除模板按钮
        self.delete_template_btn = QPushButton("删除")
        self.delete_template_btn.clicked.connect(self._delete_template)
        list_layout.addWidget(self.delete_template_btn)
        
        # 添加到主布局
        template_layout.addLayout(name_layout)
        template_layout.addLayout(list_layout)
        self.template_settings_group.setLayout(template_layout)
        layout.addWidget(self.template_settings_group)
    
    def _refresh_template_list(self):
        """
        刷新模板列表
        """
        self.template_combo.clear()
        templates = self.template_manager.get_all_templates()
        self.template_combo.addItems(templates)
    
    def _save_template(self):
        """
        保存当前设置为模板
        """
        template_name = self.template_name_input.text().strip()
        if not template_name:
            QMessageBox.warning(self, "警告", "请输入模板名称")
            return
        
        # 获取当前设置
        settings = self._get_current_settings()
        
        # 保存模板
        if self.template_manager.save_template(template_name, settings):
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 已保存")
            self.template_name_input.clear()
            self._refresh_template_list()
        else:
            QMessageBox.warning(self, "错误", "保存模板失败")
    
    def _load_template(self):
        """
        加载选中的模板
        """
        template_name = self.template_combo.currentText()
        if not template_name:
            QMessageBox.warning(self, "警告", "请选择要加载的模板")
            return
        
        # 加载模板
        settings = self.template_manager.load_template(template_name)
        if settings:
            self._apply_template(settings)
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 已加载")
        else:
            QMessageBox.warning(self, "错误", "加载模板失败")
    
    def _delete_template(self):
        """
        删除选中的模板
        """
        template_name = self.template_combo.currentText()
        if not template_name:
            QMessageBox.warning(self, "警告", "请选择要删除的模板")
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除模板 '{template_name}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.template_manager.delete_template(template_name):
                QMessageBox.information(self, "成功", f"模板 '{template_name}' 已删除")
                self._refresh_template_list()
            else:
                QMessageBox.warning(self, "错误", "删除模板失败")
    
    def _apply_template(self, settings):
        """
        应用模板设置到UI
        
        Args:
            settings: 水印设置字典
        """
        # 应用文本设置 - 适配不同的属性名
        if 'text' in settings:
            if hasattr(self, 'watermark_text_input'):
                self.watermark_text_input.setText(settings['text'])
            elif hasattr(self, 'watermark_text'):
                self.watermark_text.setText(settings['text'])
        
        # 应用字体设置 - 适配不同的属性名
        if hasattr(self, 'font_combo'):
            font_key = 'font_family' if 'font_family' in settings else 'font'
            if font_key in settings:
                index = self.font_combo.findText(settings[font_key])
                if index >= 0:
                    self.font_combo.setCurrentIndex(index)
        
        # 字体大小
        if 'font_size' in settings and hasattr(self, 'font_size_slider'):
            self.font_size_slider.setValue(settings['font_size'])
        elif 'size' in settings and hasattr(self, 'size_slider'):
            self.size_slider.setValue(settings['size'])
        
        # 透明度
        if hasattr(self, 'opacity_slider'):
            if 'opacity' in settings:
                opacity_value = settings['opacity']
                # 确保值为整数类型
                if isinstance(opacity_value, float):
                    # 检查透明度值是否在0-1范围内（需要转换为0-100的滑块值）
                    if 0 <= opacity_value <= 1:
                        opacity_value = int(opacity_value * 100)
                    else:
                        opacity_value = int(opacity_value)
                # 确保值在有效范围内
                opacity_value = max(0, min(255, opacity_value))
                # 设置值
                self.opacity_slider.setValue(opacity_value)
        
        # 旋转角度
        if 'rotation' in settings and hasattr(self, 'rotation_slider'):
            self.rotation_slider.setValue(settings['rotation'])
        
        # 应用颜色设置
        if 'color' in settings:
            color_str = settings['color']
            if color_str.startswith('#'):
                # 尝试不同的颜色控件属性名
                if hasattr(self, 'color_display'):
                    self.color_display.setStyleSheet(f"background-color: {color_str};")
                    self.current_color = QColor(color_str)
                elif hasattr(self, 'color_button') and hasattr(self, 'color_value'):
                    self.color_button.setStyleSheet(f"background-color: {color_str}; border: 1px solid #CCCCCC;")
                    self.color_value.setText(color_str)
        
        # 应用位置设置
        if 'h_position' in settings and hasattr(self, 'h_position_slider'):
            self.h_position_slider.setValue(int(settings['h_position'] * 100))
        
        if 'v_position' in settings and hasattr(self, 'v_position_slider'):
            self.v_position_slider.setValue(int(settings['v_position'] * 100))
        
        # 应用样式设置
        if 'style' in settings:
            style = settings['style']
            if style == 'single' and hasattr(self, 'single_radio'):
                self.single_radio.setChecked(True)
            elif style == 'tile' and hasattr(self, 'tile_radio'):
                self.tile_radio.setChecked(True)
            elif style == 'diagonal' and hasattr(self, 'diagonal_radio'):
                self.diagonal_radio.setChecked(True)
        
        if 'spacing' in settings and hasattr(self, 'spacing_slider'):
            self.spacing_slider.setValue(settings['spacing'])
        
        # 应用输出设置
        if 'format' in settings and hasattr(self, 'format_combo'):
            index = self.format_combo.findText(settings['format'])
            if index >= 0:
                self.format_combo.setCurrentIndex(index)
        
        if 'quality' in settings and hasattr(self, 'quality_slider'):
            self.quality_slider.setValue(settings['quality'])
            
        # 更新位置值显示并触发位置变化事件
        if hasattr(self, 'h_position_value'):
            self.h_position_value.setText(f"{self.h_position_slider.value()}%")
        if hasattr(self, 'v_position_value'):
            self.v_position_value.setText(f"{self.v_position_slider.value()}%")
        self._on_position_change()
    
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
        position_group = QGroupBox("水印位置设置")
        position_group_layout = QVBoxLayout()
        
        # 预设位置 - 九宫格布局
        preset_title = QLabel("预设位置：")
        preset_grid_layout = QGridLayout()
        preset_grid_layout.setSpacing(5)
        
        # 九宫格位置预设按钮
        self.position_buttons = []
        # 定义九宫格位置坐标 (h, v)
        positions = [
            (0, 0), (50, 0), (100, 0),  # 顶部
            (0, 50), (50, 50), (100, 50),  # 中部
            (0, 100), (50, 100), (100, 100)  # 底部
        ]
        
        for i, (h, v) in enumerate(positions):
            button = QPushButton()
            button.setFixedSize(30, 30)
            button.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc; border-radius: 3px;")
            # 设置按钮点击事件
            button.clicked.connect(lambda checked, h_val=h, v_val=v: self.set_preset_position(h_val, v_val))
            # 添加到网格布局中
            preset_grid_layout.addWidget(button, i // 3, i % 3)
            self.position_buttons.append(button)
        
        # 添加预设位置布局
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(preset_title, 1)
        preset_layout.addLayout(preset_grid_layout, 2)
        position_group_layout.addLayout(preset_layout)
        
        # 手动微调 - 水平位置
        position_layout = QHBoxLayout()
        h_label = QLabel("水平位置")
        self.h_position_slider = QSlider(Qt.Horizontal)
        self.h_position_slider.setRange(0, 100)
        self.h_position_slider.setValue(50)
        self.h_position_value = QLabel("50%")
        self.h_position_slider.valueChanged.connect(lambda value: self.h_position_value.setText(f"{value}%"))
        self.h_position_slider.valueChanged.connect(self._on_position_change)
        
        position_layout.addWidget(h_label, 1)
        position_layout.addWidget(self.h_position_slider, 2)
        position_layout.addWidget(self.h_position_value, 1)
        position_group_layout.addLayout(position_layout)
        
        # 手动微调 - 垂直位置
        v_pos_layout = QHBoxLayout()
        v_label = QLabel("垂直位置")
        self.v_position_slider = QSlider(Qt.Horizontal)
        self.v_position_slider.setRange(0, 100)
        self.v_position_slider.setValue(50)
        self.v_position_value = QLabel("50%")
        self.v_position_slider.valueChanged.connect(lambda value: self.v_position_value.setText(f"{value}%"))
        self.v_position_slider.valueChanged.connect(self._on_position_change)
        
        v_pos_layout.addWidget(v_label, 1)
        v_pos_layout.addWidget(self.v_position_slider, 2)
        v_pos_layout.addWidget(self.v_position_value, 1)
        position_group_layout.addLayout(v_pos_layout)
        
        # 设置组布局
        position_group.setLayout(position_group_layout)
        layout.addWidget(position_group)
        
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
    
    def _on_position_change(self):
        """
        当水印位置发生变化时调用
        确保预览更新并更新水印判定区域
        """
        # 触发预览更新
        if hasattr(self, 'preview_panel') and self.preview_panel:
            print(f"DEBUG: 位置发生变化，更新预览和水印判定区域")
            self.preview_panel.update_watermark_preview()
        elif hasattr(self, 'main_window') and hasattr(self.main_window, 'preview_panel'):
            print(f"DEBUG: 位置发生变化，通过main_window更新预览和水印判定区域")
            self.main_window.preview_panel.update_watermark_preview()
    
    def set_preset_position(self, h_pos, v_pos):
        """
        设置水印预设位置
        
        Args:
            h_pos: 水平位置值 (0-100)
            v_pos: 垂直位置值 (0-100)
        """
        # 更新滑块位置
        self.h_position_slider.setValue(h_pos)
        self.v_position_slider.setValue(v_pos)
        
        # 更新显示的百分比值
        self.h_position_value.setText(f"{h_pos}%")
        self.v_position_value.setText(f"{v_pos}%")
        
        # 更新按钮样式以显示当前选中的位置
        for i, button in enumerate(self.position_buttons):
            h, v = [(0, 0), (50, 0), (100, 0), (0, 50), (50, 50), (100, 50), (0, 100), (50, 100), (100, 100)][i]
            if h == h_pos and v == v_pos:
                button.setStyleSheet("background-color: #4CAF50; border: 1px solid #388E3C; border-radius: 3px;")
            else:
                button.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc; border-radius: 3px;")
        
        # 触发预览更新
        self._on_position_change()
    
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
        # 保存为最后使用的设置
        self.template_manager.save_last_settings(self.applied_settings)
        print(f"设置已应用: {self.applied_settings}")
        return self.applied_settings
    
    def load_initial_settings(self):
        """
        加载初始设置（先尝试加载最后设置，失败则加载默认模板）
        """
        # 先尝试加载最后一次使用的设置
        settings = self.template_manager.load_last_settings()
        
        # 如果没有最后设置，尝试加载默认模板
        if not settings:
            settings = self.template_manager.load_default_template()
        
        # 如果有设置，应用到UI
        if settings:
            self._apply_template(settings)
    
    def get_applied_settings(self):
        """
        获取已应用的设置
        """
        return self.applied_settings if hasattr(self, 'applied_settings') else self._get_current_settings()
