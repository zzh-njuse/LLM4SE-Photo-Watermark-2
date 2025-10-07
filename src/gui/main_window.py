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
        self.main_splitter = None  # 保存主分割器引用
        self.screen_size = None  # 保存屏幕大小
        self.init_ui()
        # 设置窗口默认大小为屏幕大小的80%
        self._set_default_size()
        # 连接窗口大小变化信号
        self.resizeEvent = self.on_resize
    
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
        
        # 保存分割器引用
        self.main_splitter = main_splitter
        
        # 初始化分割器大小
        self.update_splitter_sizes()
        
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
    
    def _set_default_size(self):
        """
        设置窗口默认大小为屏幕大小的80%
        """
        # 获取屏幕大小
        screen = self.screen()
        self.screen_size = screen.availableSize()
        
        # 计算80%的屏幕大小
        default_width = int(self.screen_size.width() * 0.8)
        default_height = int(self.screen_size.height() * 0.8)
        
        # 设置最小和默认大小
        self.setMinimumSize(default_width, default_height)
        
        # 设置窗口大小
        self.resize(default_width, default_height)
        
        # 将窗口居中显示
        self.move(
            int((self.screen_size.width() - default_width) / 2),
            int((self.screen_size.height() - default_height) / 2)
        )
    
    def on_resize(self, event):
        """
        处理窗口大小变化事件，按比例调整面板大小
        """
        # 调用原始的resizeEvent
        super().resizeEvent(event)
        
        # 更新分割器大小
        self.update_splitter_sizes()
    
    def update_splitter_sizes(self):
        """
        根据窗口宽度按比例更新分割器大小
        使用固定比例：左侧列表面板占25%，中央预览面板占50%，右侧设置面板占25%
        """
        if self.main_splitter:
            # 获取可用宽度
            available_width = self.width() - 20  # 减去一些边距
            
            # 按比例计算各面板宽度
            left_width = int(available_width * 0.25)  # 左侧面板占25%
            center_width = int(available_width * 0.50)  # 中央面板占50%
            right_width = int(available_width * 0.25)  # 右侧面板占25%
            
            # 设置分割器大小
            self.main_splitter.setSizes([left_width, center_width, right_width])