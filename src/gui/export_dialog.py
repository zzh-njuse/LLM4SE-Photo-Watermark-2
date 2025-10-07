# src/gui/export_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QRadioButton, QButtonGroup, 
                            QLineEdit, QPushButton, QFrame)
from PyQt5.QtCore import Qt

class ExportDialog(QDialog):
    """
    导出设置对话框，允许用户选择导出格式和命名规则
    """
    def __init__(self, parent=None, default_format="PNG", default_naming="suffix"):
        super().__init__(parent)
        self.setWindowTitle("导出设置")
        self.setMinimumWidth(400)
        self.init_ui(default_format, default_naming)
    
    def init_ui(self, default_format, default_naming):
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
        
        format_group.addWidget(format_label)
        format_group.addWidget(self.format_combo)
        layout.addLayout(format_group)
        
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
    
    def get_settings(self):
        """
        获取用户选择的设置
        
        Returns:
            dict: 包含format, naming_rule, prefix, suffix的字典
        """
        # 获取选中的命名规则
        naming_rule = "suffix"  # 默认
        if self.original_radio.isChecked():
            naming_rule = "original"
        elif self.prefix_radio.isChecked():
            naming_rule = "prefix"
        
        return {
            "format": self.format_combo.currentText(),
            "naming_rule": naming_rule,
            "prefix": self.prefix_input.text(),
            "suffix": self.suffix_input.text()
        }