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
        
        # 创建图片列表 - 使用ListMode确保缩略图居左显示
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(60, 60))
        # 切换到ListMode而不是IconMode，这样图标和文本会水平排列且默认居左
        self.image_list.setViewMode(QListWidget.ListMode)
        # 设置为单列布局，垂直排列
        self.image_list.setFlow(QListWidget.TopToBottom)
        # 隐藏水平滚动条，防止文件名过长时显示滚动条
        self.image_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 启用项目文本的省略显示
        self.image_list.setTextElideMode(Qt.ElideMiddle)
        # 设置列表项的大小提示
        self.image_list.setMinimumWidth(220)
        # 允许列表项填充整个宽度
        self.image_list.setUniformItemSizes(True)
        
        # 连接双击事件，用于切换当前处理的图片
        self.image_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        
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
            self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.tif);;所有文件 (*)", options=options
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
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif']
            
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
        
        # 获取文件名并处理过长的情况
        filename = os.path.basename(file_path)
        # 限制文件名长度，如果超过30个字符则截断并添加省略号
        max_length = 30
        if len(filename) > max_length:
            # 保留扩展名，截断中间部分
            name_part, ext_part = os.path.splitext(filename)
            if len(ext_part) >= max_length / 2:
                # 如果扩展名本身就很长，直接截断
                filename = filename[:max_length-3] + "..."
            else:
                # 保留文件名开头和扩展名，中间用省略号
                name_part_length = max_length - len(ext_part) - 3
                filename = name_part[:name_part_length] + "..." + ext_part
        
        # 创建列表项 - 设置合适的大小提示
        item = QListWidgetItem(QIcon(scaled_pixmap), filename)
        item.setData(Qt.UserRole, file_path)
        item.setToolTip(file_path)  # 添加工具提示显示完整路径
        
        # 设置项的大小提示，确保有足够空间显示
        item.setSizeHint(QSize(200, 80))
        
        self.image_list.addItem(item)
    
    def on_item_double_clicked(self, item):
        """处理列表项双击事件，切换当前处理的图片"""
        # 获取图片路径
        image_path = item.data(Qt.UserRole)
        if image_path:
            # 通知主窗口切换当前处理的图片
            if hasattr(self, 'main_window') and hasattr(self.main_window, 'on_image_double_clicked'):
                self.main_window.on_image_double_clicked(image_path)