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
        self.toolbar.main_window = self  # 添加主窗口引用
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
        
        # 设置分割器初始大小 - 增加左侧图片列表的宽度
        main_splitter.setSizes([250, 550, 400])
        
        # 将分割器添加到主布局
        main_layout.addWidget(main_splitter, 1)  # 1表示拉伸因子
        
        # 设置中央部件
        self.setCentralWidget(central_widget)
        
        # 移除错误的父子关系设置
        # self.preview_panel.setParent(central_widget)  # 这行代码导致UI混乱
        
        # 直接将主窗口与各个面板关联，建立信号槽连接
        self.preview_panel.main_window = self
        self.image_list_panel.main_window = self
        self.settings_panel.main_window = self
        
        # 移除实时更新预览的信号连接
        # 现在设置只有在点击应用水印按钮时才会生效
    
    def on_image_selected(self, image_path):
        """
        处理图片选择事件，将选中的图片添加到图片列表
        """
        # 检查图片是否已在列表中
        if image_path not in self.image_list_panel.image_paths:
            # 添加图片到列表
            self.image_list_panel.image_paths.append(image_path)
            self.image_list_panel._add_image_to_list(image_path)
    
    def on_image_double_clicked(self, image_path):
        """
        处理图片双击事件，切换当前处理的图片
        """
        # 通知预览面板切换当前显示的图片
        if hasattr(self.preview_panel, 'set_preview_image'):
            self.preview_panel.current_image_path = image_path
            self.preview_panel.set_preview_image(image_path)