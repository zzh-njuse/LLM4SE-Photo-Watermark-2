# src/gui/image_list_panel.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                             QLabel, QPushButton, QFileDialog, QFrame)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
import os

class ImageListPanel(QWidget):
    """
    左侧图片列表面板，用于显示已加载的图片缩略图
    """
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.init_ui()
    
    def init_ui(self):
        """初始化图片列表面板UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标题
        title_label = QLabel("图片列表")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # 创建按钮布局
        buttons_layout = QVBoxLayout()
        
        # 创建添加图片按钮
        add_image_button = QPushButton("添加多张图片")
        add_image_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px;")
        add_image_button.clicked.connect(self.add_images)
        buttons_layout.addWidget(add_image_button)
        
        # 创建添加文件夹按钮
        add_folder_button = QPushButton("添加文件夹")
        add_folder_button.setStyleSheet("background-color: #2196F3; color: white; padding: 6px;")
        add_folder_button.clicked.connect(self.add_folder)
        buttons_layout.addWidget(add_folder_button)
        
        layout.addLayout(buttons_layout)
        
        # 创建图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(60, 60))
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setSpacing(10)
        self.image_list.setWrapping(True)
        
        # 添加分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        layout.addWidget(self.image_list, 1)  # 1表示拉伸因子
    
    def add_images(self):
        """添加图片到列表"""
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*)", options=options
        )
        
        for file_path in files:
            if file_path not in self.image_paths:
                self.image_paths.append(file_path)
                self._add_image_to_list(file_path)
    
    def add_folder(self):
        """添加文件夹中的所有图片"""
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "", options=options)
        
        if folder_path:
            # 支持的图片格式
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
            
            # 遍历文件夹中的所有文件
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        file_path = os.path.join(root, file)
                        if file_path not in self.image_paths:
                            self.image_paths.append(file_path)
                            self._add_image_to_list(file_path)
    
    def _add_image_to_list(self, file_path):
        """将图片添加到列表控件中"""
        # 创建缩略图
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # 创建列表项
        item = QListWidgetItem(QIcon(scaled_pixmap), os.path.basename(file_path))
        item.setData(Qt.UserRole, file_path)
        self.image_list.addItem(item)