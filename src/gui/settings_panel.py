# src/gui/settings_panel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QComboBox, QSlider, QPushButton, QColorDialog, QFrame,
                             QRadioButton, QGroupBox, QGridLayout, QMessageBox, QScrollArea)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont
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
        """初始化设置面板UI,添加滚动功能"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建滚动内容窗口
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标题
        title_label = QLabel("水印设置")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333333;")
        scroll_layout.addWidget(title_label)
        
        # 添加分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        scroll_layout.addWidget(line)
        
        # 模板设置
        self._add_template_settings(scroll_layout)
        
        # 水印文本设置
        self._add_text_settings(scroll_layout)
        
        # 字体设置
        self._add_font_settings(scroll_layout)
        
        # 水印样式设置
        self._add_style_settings(scroll_layout)
        
        # 输出设置
        self._add_output_settings(scroll_layout)
        
        # 添加垂直拉伸
        scroll_layout.addStretch()
        
        # 设置滚动区域内容
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
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
        
        # 应用字体样式设置
        if hasattr(self, 'bold_checkbox') and 'bold' in settings:
            self.bold_checkbox.setChecked(settings['bold'])
        if hasattr(self, 'italic_checkbox') and 'italic' in settings:
            self.italic_checkbox.setChecked(settings['italic'])
        
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
        
        # 应用文本效果设置
        if hasattr(self, 'shadow_checkbox') and 'shadow' in settings:
            self.shadow_checkbox.setChecked(settings['shadow'])
        
        if hasattr(self, 'stroke_checkbox') and 'stroke' in settings:
            self.stroke_checkbox.setChecked(settings['stroke'])
        
        if hasattr(self, 'stroke_width_slider') and 'stroke_width' in settings:
            self.stroke_width_slider.setValue(settings['stroke_width'])
            self.stroke_width_value.setText(f"{settings['stroke_width']}px")
        
        if hasattr(self, 'stroke_color_button') and hasattr(self, 'stroke_color_value') and 'stroke_color' in settings:
            color_str = settings['stroke_color']
            if color_str.startswith('#'):
                self.stroke_color_button.setStyleSheet(f"background-color: {color_str}; border: 1px solid #CCCCCC;")
                self.stroke_color_value.setText(color_str)
        
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
        # 创建字体设置分组
        font_group = QGroupBox("文本设置")
        font_group_layout = QVBoxLayout()
        
        # 字体选择
        font_layout = QHBoxLayout()
        font_label = QLabel("字体")
        self.font_combo = QComboBox()
        # 添加更多常用字体
        self.font_combo.addItems(["微软雅黑", "宋体", "黑体", "Arial", "Times New Roman", 
                                 "SimSun", "SimHei", "KaiTi", "Courier New", "Verdana"])
        font_layout.addWidget(font_label, 1)
        font_layout.addWidget(self.font_combo, 2)
        font_group_layout.addLayout(font_layout)
        
        # 字体样式（粗体、斜体）
        style_layout = QHBoxLayout()
        style_label = QLabel("样式")
        self.bold_checkbox = QPushButton("B")
        self.bold_checkbox.setFixedWidth(30)
        self.bold_checkbox.setCheckable(True)
        # 修改信号连接，确保样式改变时触发更新
        if hasattr(self, '_on_settings_change'):
            self.bold_checkbox.clicked.connect(self._on_settings_change)
        elif hasattr(self, '_on_position_change'):
            self.bold_checkbox.clicked.connect(self._on_position_change)
        
        self.italic_checkbox = QPushButton("I")
        self.italic_checkbox.setFixedWidth(30)
        self.italic_checkbox.setCheckable(True)
        # 修改信号连接，确保样式改变时触发更新
        if hasattr(self, '_on_settings_change'):
            self.italic_checkbox.clicked.connect(self._on_settings_change)
        elif hasattr(self, '_on_position_change'):
            self.italic_checkbox.clicked.connect(self._on_position_change)
        style_layout.addWidget(style_label, 1)
        style_layout.addWidget(self.bold_checkbox)
        style_layout.addWidget(self.italic_checkbox)
        style_layout.addStretch(1)
        font_group_layout.addLayout(style_layout)
        
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
        font_group_layout.addLayout(size_layout)
        
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
        font_group_layout.addLayout(opacity_layout)
        
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
        font_group_layout.addLayout(rotation_layout)
        
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
        font_group_layout.addLayout(color_layout)
        
        # 添加文本效果设置（阴影、描边）
        effect_group = QGroupBox("文本效果")
        effect_group_layout = QVBoxLayout()
        
        # 阴影效果
        shadow_layout = QHBoxLayout()
        self.shadow_checkbox = QPushButton("阴影")
        self.shadow_checkbox.setCheckable(True)
        self.shadow_checkbox.clicked.connect(self._on_position_change)
        shadow_layout.addWidget(self.shadow_checkbox)
        shadow_layout.addStretch(1)
        effect_group_layout.addLayout(shadow_layout)
        
        # 描边效果
        stroke_layout = QHBoxLayout()
        stroke_label = QLabel("描边宽度")
        self.stroke_checkbox = QPushButton("启用")
        self.stroke_checkbox.setCheckable(True)
        self.stroke_checkbox.clicked.connect(self._on_position_change)
        self.stroke_width_slider = QSlider(Qt.Horizontal)
        self.stroke_width_slider.setRange(1, 10)
        self.stroke_width_slider.setValue(2)
        self.stroke_width_value = QLabel("2px")
        self.stroke_width_slider.valueChanged.connect(lambda value: self.stroke_width_value.setText(f"{value}px"))
        self.stroke_width_slider.valueChanged.connect(self._on_position_change)
        stroke_layout.addWidget(stroke_label, 1)
        stroke_layout.addWidget(self.stroke_checkbox, 1)
        stroke_layout.addWidget(self.stroke_width_slider, 2)
        stroke_layout.addWidget(self.stroke_width_value, 1)
        effect_group_layout.addLayout(stroke_layout)
        
        # 描边颜色
        stroke_color_layout = QHBoxLayout()
        stroke_color_label = QLabel("描边颜色")
        self.stroke_color_button = QPushButton()
        self.stroke_color_button.setFixedWidth(30)
        self.stroke_color_button.setStyleSheet("background-color: #000000; border: 1px solid #CCCCCC;")
        self.stroke_color_button.clicked.connect(self.select_stroke_color)
        self.stroke_color_value = QLineEdit("#000000")
        stroke_color_layout.addWidget(stroke_color_label, 1)
        stroke_color_layout.addWidget(self.stroke_color_button, 1)
        stroke_color_layout.addWidget(self.stroke_color_value, 2)
        effect_group_layout.addLayout(stroke_color_layout)
        
        # 设置效果组布局
        effect_group.setLayout(effect_group_layout)
        
        # 设置字体组布局
        font_group.setLayout(font_group_layout)
        
        # 添加到主布局
        layout.addWidget(font_group)
        layout.addWidget(effect_group)
    
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
        current_color = QColor(self.color_value.text()) if self.color_value.text() else Qt.white
        color = QColorDialog.getColor(current_color, self, "选择水印颜色")
        if color.isValid():
            print(f"DEBUG: 选择了新颜色: {color.name()}")
            self.color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #CCCCCC;")
            self.color_value.setText(color.name())
            # 立即获取设置并打印
            settings = self._get_current_settings()
            print(f"DEBUG: 选择颜色后设置: {settings}")
            # 触发预览更新
            print(f"DEBUG: 触发预览更新")
            self._on_position_change()
    
    def select_stroke_color(self):
        """选择描边颜色"""
        current_color = QColor(self.stroke_color_value.text()) if self.stroke_color_value.text() else Qt.black
        color = QColorDialog.getColor(current_color, self, "选择描边颜色")
        if color.isValid():
            self.stroke_color_button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #CCCCCC;")
            self.stroke_color_value.setText(color.name())
            # 触发预览更新
            self._on_position_change()
    
    def apply_watermark(self, image, settings):
        """应用水印到图片上"""
        from PIL import Image, ImageDraw, ImageFont
        import os
        import sys
        import logging
        
        # 创建图像副本，并确保是RGBA模式以支持透明度
        if image.mode != 'RGBA':
            watermarked = image.convert('RGBA')
        else:
            watermarked = image.copy()
        
        draw = ImageDraw.Draw(watermarked)
        
        # 获取水印文本和设置
        text = settings.get('text', '')
        font_size = settings.get('size', 30)
        opacity = int(settings.get('opacity', 0.5) * 255)  # 转换为0-255范围
        color_str = settings.get('color', '#FFFFFF')
        font_name = settings.get('font', 'SimHei')  # 默认使用中文字体
        bold = settings.get('bold', False)
        italic = settings.get('italic', False)
        shadow = settings.get('shadow', False)
        stroke = settings.get('stroke', False)
        stroke_width = settings.get('stroke_width', 2)
        stroke_color_str = settings.get('stroke_color', '#000000')
        rotation = settings.get('rotation', 0)
        
        print(f"应用水印设置: 文本='{text}', 字体='{font_name}', 大小={font_size}, 颜色={color_str}, 描边={stroke}, 阴影={shadow}")
        
        # 确保文本是安全的字符串
        try:
            safe_text = str(text) if text else ''
            # 确保是UTF-8编码的字符串
            safe_text = safe_text.encode('utf-8', 'surrogateescape').decode('utf-8', 'surrogateescape')
            print(f"安全处理后的文本: {repr(safe_text)}")
        except Exception as e:
            print(f"文本安全处理失败: {e}")
            safe_text = ""
        
        # 将十六进制颜色转换为RGBA元组
        try:
            # 移除#号（如果有）
            color_str = color_str.lstrip('#')
            # 转换为RGB
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            # 创建RGBA颜色
            text_color = (r, g, b, opacity)
            print(f"颜色转换成功: {text_color}")
        except Exception as e:
            print(f"颜色转换错误: {e}")
            # 默认使用白色
            text_color = (255, 255, 255, opacity)
            print(f"使用默认白色: {text_color}")
        
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
            print(f"使用默认黑色描边: {stroke_color}")
        
        # 尝试加载字体，确保中文能正确显示
        font = None
        
        # 获取粗体和斜体设置
        bold = settings.get('bold', False)
        italic = settings.get('italic', False)
        print(f"字体样式设置: 粗体={bold}, 斜体={italic}")
        
        # 根据bold和italic属性构建字体选项列表
        font_options = []
        if bold and italic:
            # 粗斜体
            font_options = [f"{font_name}:bold:italic", f"{font_name}-BoldItalic"]
        elif bold:
            # 粗体
            font_options = [f"{font_name}:bold", f"{font_name}-Bold"]
        elif italic:
            # 斜体
            font_options = [f"{font_name}:italic", f"{font_name}-Italic"]
        
        # 优先使用中文字体
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'Arial']
        
        # 字体加载策略：先尝试带有样式的字体选项，再尝试用户指定的字体，最后尝试中文字体列表
        font_to_try = font_options.copy()
        if font_name and font_name not in font_to_try:
            font_to_try.append(font_name)
        font_to_try.extend(chinese_fonts)
        
        # Windows系统字体目录
        windows_font_dirs = ['C:\Windows\Fonts', 'C:\WINNT\Fonts']
        
        try:
            # 先尝试带有样式的字体选项
            if font_options:
                print(f"优先尝试带样式的字体选项: {font_options}")
                for styled_font in font_options:
                    print(f"尝试加载带样式字体: {styled_font}")
                    try:
                        font = ImageFont.truetype(styled_font, font_size)
                        print(f"成功加载带样式字体: {styled_font}")
                        break
                    except Exception as e:
                        print(f"加载带样式字体失败 {styled_font}: {str(e)}")
            
            # 如果带样式的字体加载失败，尝试普通字体
            if font is None:
                print("带样式字体加载失败，尝试普通字体")
                for font_name_try in font_to_try:
                    # 跳过已经尝试过的带样式字体
                    if ':' in font_name_try or '-' in font_name_try and any(suffix in font_name_try for suffix in ['Bold', 'Italic']):
                        continue
                    
                    print(f"尝试加载字体: {font_name_try}")
                    
                    # 尝试直接加载字体名称
                    try:
                        font = ImageFont.truetype(font_name_try, font_size)
                        print(f"成功加载字体: {font_name_try}")
                                    # 记录字体样式设置，稍后在绘制时使用
                        print(f"字体样式设置将在绘制时应用: 粗体={bold}, 斜体={italic}")
                        break
                    except:
                        # 尝试添加.ttf后缀
                        try:
                            font = ImageFont.truetype(f"{font_name_try}.ttf", font_size)
                            print(f"成功加载字体: {font_name_try}.ttf")
                            break
                        except:
                            # 尝试在Windows字体目录中查找
                            found = False
                            for font_dir in windows_font_dirs:
                                if os.path.exists(font_dir):
                                    font_path = os.path.join(font_dir, f"{font_name_try}.ttf")
                                    if os.path.exists(font_path):
                                        try:
                                            font = ImageFont.truetype(font_path, font_size)
                                            print(f"成功从系统目录加载字体: {font_path}")
                                            found = True
                                            break
                                        except:
                                            continue
                            if found:
                                break
        except Exception as e:
            print(f"字体加载异常: {e}")
            
        # 如果所有字体都加载失败，使用默认字体
        if font is None:
            print("使用默认字体")
            font = ImageFont.load_default()
        
        # 确保文本不为空
        if safe_text.strip():
            # 创建临时图像来绘制文字
            temp_img = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
                
            # 获取文本尺寸 - 使用try-except避免编码问题
            text_width, text_height = 100, 30  # 默认值
            try:
                # 使用try-except包装文本尺寸计算
                try:
                    # 优先使用textbbox
                    bbox = temp_draw.textbbox((0, 0), safe_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    print(f"文本尺寸计算成功: {text_width}x{text_height}")
                except Exception as e1:
                    print(f"textbbox失败: {e1}")
                    try:
                        # 尝试使用textsize（旧版本PIL）
                        text_width, text_height = temp_draw.textsize(safe_text, font=font)
                        print(f"textsize计算成功: {text_width}x{text_height}")
                    except Exception as e2:
                        print(f"textsize也失败: {e2}")
                        print(f"使用默认文本尺寸: {text_width}x{text_height}")
            except Exception as e:
                print(f"文本尺寸计算失败: {e}")
                print(f"使用默认文本尺寸: {text_width}x{text_height}")
            
            # 获取位置设置
            h_position = settings.get('h_position', 0.5)
            v_position = settings.get('v_position', 0.5)
            
            # 计算水印位置
            x = max(0, int((watermarked.size[0] - text_width) * h_position))
            y = max(0, int((watermarked.size[1] - text_height) * v_position))
            print(f"计算水印位置: ({x}, {y})")
            
            # 处理旋转
            if rotation != 0:
                print(f"处理旋转: {rotation}度")
                try:
                    # 创建一个新的临时图像用于旋转
                    text_img = Image.new('RGBA', (text_width + 40, text_height + 40), (255, 255, 255, 0))
                    text_draw = ImageDraw.Draw(text_img)
                    
                    # 绘制文本到临时图像 - 注意参数名：color改为fill，stroke_color改为stroke_fill
                    self._draw_text_with_effects(text_draw, (20, 20), safe_text, font, fill=text_color, 
                                     shadow=shadow, stroke=stroke, stroke_width=stroke_width, stroke_fill=stroke_color,
                                     bold=bold, italic=italic)
                    
                    # 旋转文本图像
                    rotated_text = text_img.rotate(rotation, expand=True, fillcolor=(255, 255, 255, 0))
                    
                    # 计算旋转后的位置
                    rot_x = max(0, x - rotated_text.width // 2 + text_width // 2)
                    rot_y = max(0, y - rotated_text.height // 2 + text_height // 2)
                    print(f"旋转后位置: ({rot_x}, {rot_y})")
                    
                    # 粘贴旋转后的文本到主图像
                    watermarked.paste(rotated_text, (rot_x, rot_y), rotated_text)
                except Exception as e:
                    print(f"旋转处理失败: {e}")
                    # 降级方案：直接绘制不旋转的文本
                    print("降级到直接绘制文本")
                    self._draw_text_with_effects(draw, (x, y), safe_text, font, fill=text_color, 
                                         shadow=shadow, stroke=stroke, stroke_width=stroke_width, stroke_fill=stroke_color,
                                         bold=bold, italic=italic)
            else:
                # 直接绘制文本到图像，添加效果
                print("直接绘制文本，无旋转")
                self._draw_text_with_effects(draw, (x, y), safe_text, font, fill=text_color, 
                                     shadow=shadow, stroke=stroke, stroke_width=stroke_width, stroke_fill=stroke_color,
                                     bold=bold, italic=italic)
        
        # 如果原始图像不是RGBA模式，转换回原始模式
        if image.mode != 'RGBA':
            watermarked = watermarked.convert(image.mode)
        
        print("水印应用完成")
        return watermarked
    
    def _draw_text_with_effects(self, draw, position, text, font, fill, shadow=False, stroke=False, stroke_width=2, stroke_fill=(0,0,0,255), bold=False, italic=False):
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
            bold: 是否粗体
            italic: 是否斜体
        """
        x, y = position
        
        print(f"===== 文本绘制开始（settings_panel）=====")
        print(f"绘制文本效果: 阴影={shadow}, 描边={stroke}, 描边宽度={stroke_width}, 粗体={bold}, 斜体={italic}")
        print(f"文本颜色: {fill}, 类型: {type(fill)}")
        print(f"描边颜色: {stroke_fill}, 类型: {type(stroke_fill)}")
        
        # 调整位置用于斜体效果
        adjusted_x, adjusted_y = x, y
        if italic:
            print("应用斜体效果")
        
        try:
            # 绘制阴影
            if shadow:
                shadow_color = (0, 0, 0, int(fill[3] * 0.5))  # 半透明黑色阴影
                print("绘制阴影")
                if italic:
                    # 斜体文本的阴影：使用临时图像和仿射变换
                    text_width, text_height = font.getsize(text)
                    shadow_img = Image.new('RGBA', (text_width + 20, text_height + 20), (255, 255, 255, 0))
                    shadow_draw = ImageDraw.Draw(shadow_img)
                    shadow_draw.text((10, 10), text, font=font, fill=shadow_color)
                    italic_skew = 0.2
                    width, height = shadow_img.size
                    italic_shadow = shadow_img.transform(
                        (width + int(height * italic_skew), height),
                        Image.AFFINE,
                        (1, italic_skew, 0, 0, 1, 0),
                        fillcolor=(255, 255, 255, 0)
                    )
                    # 粘贴斜体阴影到主图像（偏移2像素）
                    draw.bitmap((adjusted_x + 2, adjusted_y + 2), italic_shadow, fill=None)
                else:
                    # 正常文本的阴影
                    draw.text((adjusted_x + 2, adjusted_y + 2), text, font=font, fill=shadow_color)
            
            # 绘制描边
            if stroke and stroke_fill:
                print("绘制描边")
                if italic:
                    # 斜体文本的描边：使用临时图像和仿射变换
                    text_width, text_height = font.getsize(text)
                    stroke_img = Image.new('RGBA', (text_width + 20, text_height + 20), (255, 255, 255, 0))
                    stroke_draw = ImageDraw.Draw(stroke_img)
                    # 先绘制描边到临时图像
                    for offset in range(1, stroke_width + 1):
                        for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
                            stroke_draw.text((10 + dx, 10 + dy), text, font=font, fill=stroke_fill)
                    # 应用斜体变换
                    italic_skew = 0.2
                    width, height = stroke_img.size
                    italic_stroke = stroke_img.transform(
                        (width + int(height * italic_skew), height),
                        Image.AFFINE,
                        (1, italic_skew, 0, 0, 1, 0),
                        fillcolor=(255, 255, 255, 0)
                    )
                    # 粘贴斜体描边到主图像
                    draw.bitmap((adjusted_x, adjusted_y), italic_stroke, fill=None)
                else:
                    # 正常文本的描边
                    # 只绘制四个方向的描边，避免对角线方向的问题
                    for offset in range(1, stroke_width + 1):
                        draw.text((adjusted_x - offset, adjusted_y), text, font=font, fill=stroke_fill)
                        draw.text((adjusted_x + offset, adjusted_y), text, font=font, fill=stroke_fill)
                        draw.text((adjusted_x, adjusted_y - offset), text, font=font, fill=stroke_fill)
                        draw.text((adjusted_x, adjusted_y + offset), text, font=font, fill=stroke_fill)
            
            # 应用粗体效果
            if bold:
                print("应用粗体效果")
                bold_offset = 1
                if italic:
                    # 斜体文本的粗体：使用临时图像和仿射变换
                    text_width, text_height = font.getsize(text)
                    bold_img = Image.new('RGBA', (text_width + 20, text_height + 20), (255, 255, 255, 0))
                    bold_draw = ImageDraw.Draw(bold_img)
                    # 先绘制粗体效果到临时图像
                    for dx, dy in [(bold_offset, 0), (-bold_offset, 0), (0, bold_offset), (0, -bold_offset)]:
                        bold_draw.text((10 + dx, 10 + dy), text, font=font, fill=fill)
                    # 应用斜体变换
                    italic_skew = 0.2
                    width, height = bold_img.size
                    italic_bold = bold_img.transform(
                        (width + int(height * italic_skew), height),
                        Image.AFFINE,
                        (1, italic_skew, 0, 0, 1, 0),
                        fillcolor=(255, 255, 255, 0)
                    )
                    # 粘贴斜体粗体到主图像
                    draw.bitmap((adjusted_x, adjusted_y), italic_bold, fill=None)
                else:
                    # 正常文本的粗体
                    # 在相邻位置绘制文本
                    for dx, dy in [(bold_offset, 0), (-bold_offset, 0), (0, bold_offset), (0, -bold_offset)]:
                        draw.text((adjusted_x + dx, adjusted_y + dy), text, font=font, fill=fill)
            
            # 绘制主文本
            print("绘制主文本")
            if italic:
                # 正确的斜体效果实现：使用Image的transform方法创建倾斜效果
                # 首先计算文本尺寸
                text_width, text_height = font.getsize(text)
                # 创建一个临时图像来绘制文本
                temp_img = Image.new('RGBA', (text_width + 20, text_height + 20), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                # 绘制文本到临时图像
                temp_draw.text((10, 10), text, font=font, fill=fill)
                # 创建斜体变换矩阵（向右倾斜）
                italic_skew = 0.2  # 斜体倾斜系数
                # 计算变换参数
                width, height = temp_img.size
                # 使用仿射变换创建斜体效果
                # 斜切变换矩阵: [1, skew, 0, 0, 1, 0]
                italic_img = temp_img.transform(
                    (width + int(height * italic_skew), height),
                    Image.AFFINE,
                    (1, italic_skew, 0, 0, 1, 0),
                    fillcolor=(255, 255, 255, 0)
                )
                # 粘贴斜体文本到主图像
                # 先获取主图像的模式
                main_mode = draw.im.mode
                # 如果主图像不是RGBA模式，需要先转换
                if main_mode != 'RGBA':
                    # 使用paste方法而不是bitmap以支持透明度
                    draw.im.paste(italic_img, (adjusted_x, adjusted_y), italic_img)
                else:
                    # RGBA模式下直接绘制
                    draw.bitmap((adjusted_x, adjusted_y), italic_img, fill=None)
            else:
                # 正常文本
                draw.text((adjusted_x, adjusted_y), text, font=font, fill=fill)
            print("文本绘制完成")
        except Exception as e:
            print(f"文本绘制异常: {e}")
            # 降级方案：尝试不使用效果直接绘制
            try:
                print("尝试降级绘制")
                draw.text((x, y), text, font=font, fill=fill)
            except Exception as e2:
                print(f"降级绘制也失败: {e2}")
    
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
            'quality': self.quality_slider.value() if hasattr(self, 'quality_slider') else 90,
            # 新增高级文本设置
            'bold': self.bold_checkbox.isChecked() if hasattr(self, 'bold_checkbox') else False,
            'italic': self.italic_checkbox.isChecked() if hasattr(self, 'italic_checkbox') else False,
            'shadow': self.shadow_checkbox.isChecked() if hasattr(self, 'shadow_checkbox') else False,
            'stroke': self.stroke_checkbox.isChecked() if hasattr(self, 'stroke_checkbox') else False,
            'stroke_width': self.stroke_width_slider.value() if hasattr(self, 'stroke_width_slider') else 2,
            'stroke_color': self.stroke_color_value.text() if hasattr(self, 'stroke_color_value') else '#000000'
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
