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
        apply_btn = QPushButton("应用水印")
        apply_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 6px 12px;")
        layout.addWidget(apply_btn)
        
        # 导出按钮
        export_btn = QPushButton("导出图片")
        export_btn.setStyleSheet("background-color: #E91E63; color: white; padding: 6px 12px;")
        layout.addWidget(export_btn)