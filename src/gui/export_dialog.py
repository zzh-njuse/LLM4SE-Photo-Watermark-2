# src/gui/export_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QRadioButton, QButtonGroup, 
                            QLineEdit, QPushButton, QFrame, QSlider, 
                            QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt

class ExportDialog(QDialog):
    """
    导出设置对话框，允许用户选择导出格式和命名规则
    """
    def __init__(self, parent=None, default_format="PNG", default_naming="suffix", 
                 default_quality=90, default_resize_type="original", 
                 default_width=None, default_height=None, default_percent=100):
        super().__init__(parent)
        self.setWindowTitle("导出设置")
        self.setMinimumWidth(400)
        # 禁用右上角的帮助按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.original_size = None  # 原始图片尺寸，需要在外部设置
        self.init_ui(default_format, default_naming, default_quality, 
                    default_resize_type, default_width, default_height, default_percent)
    
    def init_ui(self, default_format, default_naming, default_quality, 
                default_resize_type, default_width, default_height, default_percent):
        """初始化对话框UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 导出格式设置
        format_group = QVBoxLayout()
        format_label = QLabel("导出格式:")
        format_label.setStyleSheet("font-weight: bold;")
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG"])
        if default_format in ["PNG", "JPEG"]:
            self.format_combo.setCurrentText(default_format)
        
        # JPEG质量设置
        quality_layout = QHBoxLayout()
        quality_label = QLabel("质量:")
        self.quality_value_label = QLabel(f"{default_quality}%")
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(10, 100)
        self.quality_slider.setValue(default_quality)
        self.quality_slider.setEnabled(default_format == "JPEG")
        
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_value_label)
        
        # 连接信号
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        self.quality_slider.valueChanged.connect(lambda value: 
                                               self.quality_value_label.setText(f"{value}%"))
        
        # 初始化质量滑块状态
        self._on_format_changed(default_format)
        
        format_group.addWidget(format_label)
        format_group.addWidget(self.format_combo)
        format_group.addLayout(quality_layout)
        layout.addLayout(format_group)
        
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 图片尺寸设置
        resize_group = QVBoxLayout()
        resize_label = QLabel("图片尺寸:")
        resize_label.setStyleSheet("font-weight: bold;")
        
        self.resize_group = QButtonGroup(self)
        
        # 原始尺寸选项
        self.original_size_radio = QRadioButton("原始尺寸")
        self.resize_group.addButton(self.original_size_radio)
        
        # 按宽度调整选项
        width_layout = QHBoxLayout()
        self.width_radio = QRadioButton("按宽度:")
        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(1)
        self.width_spin.setMaximum(9999)
        self.width_spin.setSuffix(" px")
        if default_width:
            self.width_spin.setValue(default_width)
        width_layout.addWidget(self.width_radio)
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        self.resize_group.addButton(self.width_radio)
        
        # 按高度调整选项
        height_layout = QHBoxLayout()
        self.height_radio = QRadioButton("按高度:")
        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(1)
        self.height_spin.setMaximum(9999)
        self.height_spin.setSuffix(" px")
        if default_height:
            self.height_spin.setValue(default_height)
        height_layout.addWidget(self.height_radio)
        height_layout.addWidget(self.height_spin)
        height_layout.addStretch()
        self.resize_group.addButton(self.height_radio)
        
        # 按百分比调整选项
        percent_layout = QHBoxLayout()
        self.percent_radio = QRadioButton("按百分比:")
        self.percent_spin = QDoubleSpinBox()
        self.percent_spin.setMinimum(10)
        self.percent_spin.setMaximum(500)
        self.percent_spin.setDecimals(1)
        self.percent_spin.setSuffix("%")
        self.percent_spin.setValue(default_percent)
        percent_layout.addWidget(self.percent_radio)
        percent_layout.addWidget(self.percent_spin)
        percent_layout.addStretch()
        self.resize_group.addButton(self.percent_radio)
        
        # 设置默认选中项
        if default_resize_type == "width":
            self.width_radio.setChecked(True)
        elif default_resize_type == "height":
            self.height_radio.setChecked(True)
        elif default_resize_type == "percent":
            self.percent_radio.setChecked(True)
        else:
            self.original_size_radio.setChecked(True)
        
        resize_group.addWidget(resize_label)
        resize_group.addWidget(self.original_size_radio)
        resize_group.addLayout(width_layout)
        resize_group.addLayout(height_layout)
        resize_group.addLayout(percent_layout)
        layout.addLayout(resize_group)
        
        # 连接信号，当选择调整方式时，更新输入框状态
        self.original_size_radio.toggled.connect(self._update_resize_states)
        self.width_radio.toggled.connect(self._update_resize_states)
        self.height_radio.toggled.connect(self._update_resize_states)
        self.percent_radio.toggled.connect(self._update_resize_states)
        
        # 初始化调整选项状态
        self._update_resize_states()
        
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 命名规则设置
        naming_group = QVBoxLayout()
        naming_label = QLabel("命名规则:")
        naming_label.setStyleSheet("font-weight: bold;")
        
        self.naming_group = QButtonGroup(self)
        
        # 保留原文件名选项
        self.original_radio = QRadioButton("保留原文件名")
        self.naming_group.addButton(self.original_radio)
        
        # 添加前缀选项
        prefix_layout = QHBoxLayout()
        self.prefix_radio = QRadioButton("添加前缀:")
        self.prefix_input = QLineEdit("wm_")
        self.prefix_input.setMaximumWidth(150)
        prefix_layout.addWidget(self.prefix_radio)
        prefix_layout.addWidget(self.prefix_input)
        prefix_layout.addStretch()
        self.naming_group.addButton(self.prefix_radio)
        
        # 添加后缀选项
        suffix_layout = QHBoxLayout()
        self.suffix_radio = QRadioButton("添加后缀:")
        self.suffix_input = QLineEdit("_watermark")
        self.suffix_input.setMaximumWidth(150)
        suffix_layout.addWidget(self.suffix_radio)
        suffix_layout.addWidget(self.suffix_input)
        suffix_layout.addStretch()
        self.naming_group.addButton(self.suffix_radio)
        
        # 设置默认选中项
        if default_naming == "original":
            self.original_radio.setChecked(True)
        elif default_naming == "prefix":
            self.prefix_radio.setChecked(True)
        else:
            self.suffix_radio.setChecked(True)
        
        naming_group.addWidget(naming_label)
        naming_group.addWidget(self.original_radio)
        naming_group.addLayout(prefix_layout)
        naming_group.addLayout(suffix_layout)
        layout.addLayout(naming_group)
        
        # 连接信号，当选择前缀或后缀时，启用对应的输入框
        self.original_radio.toggled.connect(self._update_input_states)
        self.prefix_radio.toggled.connect(self._update_input_states)
        self.suffix_radio.toggled.connect(self._update_input_states)
        
        # 初始化输入框状态
        self._update_input_states()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        ok_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)
    
    def _update_input_states(self):
        """根据选中的命名规则更新输入框状态"""
        self.prefix_input.setEnabled(self.prefix_radio.isChecked())
        self.suffix_input.setEnabled(self.suffix_radio.isChecked())
    
    def _on_format_changed(self, format_text):
        """当导出格式改变时更新UI状态"""
        if format_text == "JPEG":
            # JPEG格式时启用质量滑块并恢复默认样式
            self.quality_slider.setEnabled(True)
            self.quality_slider.setStyleSheet("")  # 恢复默认样式
            self.quality_value_label.setStyleSheet("")  # 恢复默认样式
        else:
            # PNG格式时设置质量为100%并禁用
            self.quality_slider.setValue(100)
            self.quality_value_label.setText("100%")
            self.quality_slider.setEnabled(False)
            # 添加明显的禁用样式
            self.quality_slider.setStyleSheet("color: #A0A0A0; background-color: #F0F0F0;")
            self.quality_value_label.setStyleSheet("color: #A0A0A0;")
    
    def _update_resize_states(self):
        """根据选中的调整方式更新输入框状态"""
        self.width_spin.setEnabled(self.width_radio.isChecked())
        self.height_spin.setEnabled(self.height_radio.isChecked())
        self.percent_spin.setEnabled(self.percent_radio.isChecked())
    
    def set_original_size(self, size):
        """设置原始图片尺寸，用于自动计算其他尺寸"""
        self.original_size = size
        if size:
            width, height = size
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)

    def get_settings(self):
        """
        获取用户选择的设置
        
        Returns:
            dict: 包含所有导出设置的字典
        """
        # 获取选中的命名规则
        naming_rule = "suffix"  # 默认
        if self.original_radio.isChecked():
            naming_rule = "original"
        elif self.prefix_radio.isChecked():
            naming_rule = "prefix"
        
        # 获取调整方式
        resize_type = "original"
        width = None
        height = None
        percent = None
        
        if self.width_radio.isChecked():
            resize_type = "width"
            width = self.width_spin.value()
        elif self.height_radio.isChecked():
            resize_type = "height"
            height = self.height_spin.value()
        elif self.percent_radio.isChecked():
            resize_type = "percent"
            percent = self.percent_spin.value()
        
        return {
            "format": self.format_combo.currentText(),
            "quality": self.quality_slider.value(),
            "naming_rule": naming_rule,
            "prefix": self.prefix_input.text(),
            "suffix": self.suffix_input.text(),
            "resize_type": resize_type,
            "width": width,
            "height": height,
            "percent": percent
        }