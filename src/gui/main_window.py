# src/gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSplitter, QFrame)
from PyQt5.QtCore import Qt
from .image_list_panel import ImageListPanel
from .preview_panel import PreviewPanel
from .settings_panel import SettingsPanel
from .toolbar import Toolbar

class MainWindow(QMainWindow):
    """
    主窗口类，负责组织和管理所有UI组件
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("照片水印工具")
        self.setMinimumSize(1200, 800)
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建工具栏
        self.toolbar = Toolbar()
        main_layout.addWidget(self.toolbar)
        
        # 创建主分割器（水平分割左侧列表、中央预览和右侧设置）
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 创建左侧图片列表面板
        self.image_list_panel = ImageListPanel()
        main_splitter.addWidget(self.image_list_panel)
        
        # 创建中央预览面板
        self.preview_panel = PreviewPanel()
        main_splitter.addWidget(self.preview_panel)
        
        # 创建右侧设置面板
        self.settings_panel = SettingsPanel()
        main_splitter.addWidget(self.settings_panel)
        
        # 设置分割器初始大小
        main_splitter.setSizes([200, 600, 400])
        
        # 将分割器添加到主布局
        main_layout.addWidget(main_splitter, 1)  # 1表示拉伸因子
        
        # 设置中央部件
        self.setCentralWidget(central_widget)