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
        # 设置窗口标志 - 只保留关闭按钮，移除最小化按钮
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.main_splitter = None  # 保存主分割器引用
        self.screen_size = None  # 保存屏幕大小
        
        # 设置面板比例参数 - 这里可以方便地调整三个面板的宽度比例
        # 总和应该等于1.0
        self.left_panel_ratio = 0.15  # 左侧面板比例
        self.center_panel_ratio = 0.55  # 中央面板比例
        self.right_panel_ratio = 0.30  # 右侧面板比例
        
        # 设置最小宽度限制
        self.left_panel_min_width = 150  # 左侧面板最小宽度
        self.center_panel_min_width = 300  # 中央面板最小宽度
        self.right_panel_min_width = 250  # 右侧面板最小宽度
        
        # 设置初始固定大小 - 窗口首次加载时使用
        self.initial_left_width = 200
        self.initial_center_width = 400
        self.initial_right_width = 300
        
        self.init_ui()
        # 连接窗口大小变化信号
        self.resizeEvent = self.on_resize
        # 默认最大化窗口
        self.showMaximized()
    
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
        
        # 设置分割器的手柄宽度
        main_splitter.setHandleWidth(6)
        
        # 创建左侧图片列表面板
        self.image_list_panel = ImageListPanel()
        # 应用最小宽度限制
        self.image_list_panel.setMinimumWidth(self.left_panel_min_width)
        main_splitter.addWidget(self.image_list_panel)
        
        # 创建中央预览面板
        self.preview_panel = PreviewPanel()
        # 应用最小宽度限制
        self.preview_panel.setMinimumWidth(self.center_panel_min_width)
        main_splitter.addWidget(self.preview_panel)
        
        # 创建右侧设置面板
        self.settings_panel = SettingsPanel()
        # 应用最小宽度限制，确保内容可见
        self.settings_panel.setMinimumWidth(self.right_panel_min_width)
        main_splitter.addWidget(self.settings_panel)
        
        # 保存分割器引用
        self.main_splitter = main_splitter
        
        # 设置初始固定大小
        # 使用类属性方便统一修改
        main_splitter.setSizes([self.initial_left_width, self.initial_center_width, self.initial_right_width])
        
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
        设置窗口默认大小和属性
        """
        # 获取屏幕大小
        screen = self.screen()
        self.screen_size = screen.availableSize()
        
        # 设置最小大小为屏幕大小的80%
        min_width = int(self.screen_size.width() * 0.8)
        min_height = int(self.screen_size.height() * 0.8)
        self.setMinimumSize(min_width, min_height)
    
    def on_resize(self, event):
        """
        处理窗口大小变化事件，按比例调整面板大小
        """
        # 调用原始的resizeEvent
        super().resizeEvent(event)
        
        # 更新分割器大小
        self.update_splitter_sizes()
    
    def showEvent(self, event):
        """
        窗口显示事件，在窗口显示后再次更新分割器大小
        这确保了在窗口完全初始化和显示后应用正确的比例
        """
        # 调用原始的showEvent
        super().showEvent(event)
        
        # 在窗口显示后再次更新分割器大小
        # 使用QTimer延迟一点时间，确保所有尺寸都已正确设置
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self._apply_final_sizes)
    
    def update_splitter_sizes(self):
        """
        根据窗口宽度按比例更新分割器大小
        使用类属性中定义的比例值，方便统一调整
        """
        if self.main_splitter:
            # 获取可用宽度
            available_width = self.width() - 20  # 减去一些边距
            
            # 按比例计算各面板宽度
            left_width = int(available_width * self.left_panel_ratio)
            center_width = int(available_width * self.center_panel_ratio)
            right_width = int(available_width * self.right_panel_ratio)
            
            # 确保每个面板至少有最小宽度
            left_width = max(left_width, self.left_panel_min_width)
            center_width = max(center_width, self.center_panel_min_width)
            right_width = max(right_width, self.right_panel_min_width)
            
            # 设置分割器大小
            self.main_splitter.setSizes([left_width, center_width, right_width])
    
    def adjust_panel_sizes(self, left_ratio=None, center_ratio=None, right_ratio=None,
                          left_min=None, center_min=None, right_min=None):
        """
        动态调整面板大小的便捷方法
        
        参数:
            left_ratio: 左侧面板比例（0-1）
            center_ratio: 中央面板比例（0-1）
            right_ratio: 右侧面板比例（0-1）
            left_min: 左侧面板最小宽度
            center_min: 中央面板最小宽度
            right_min: 右侧面板最小宽度
        """
        # 更新比例值（如果提供）
        if left_ratio is not None:
            self.left_panel_ratio = left_ratio
        if center_ratio is not None:
            self.center_panel_ratio = center_ratio
        if right_ratio is not None:
            self.right_panel_ratio = right_ratio
            
        # 更新最小宽度（如果提供）
        if left_min is not None:
            self.left_panel_min_width = left_min
            self.image_list_panel.setMinimumWidth(left_min)
        if center_min is not None:
            self.center_panel_min_width = center_min
            self.preview_panel.setMinimumWidth(center_min)
        if right_min is not None:
            self.right_panel_min_width = right_min
            self.settings_panel.setMinimumWidth(right_min)
            
        # 重新计算并应用新的大小
        self.update_splitter_sizes()
    
    def _apply_final_sizes(self):
        """
        应用最终的分割器大小，在窗口完全显示后调用
        这个方法使用类属性中定义的比例值，确保在所有初始化完成后生效
        """
        if self.main_splitter:
            # 应用比例值
            available_width = self.width() - 20
            left_width = int(available_width * self.left_panel_ratio)
            center_width = int(available_width * self.center_panel_ratio)
            right_width = int(available_width * self.right_panel_ratio)
            
            # 确保每个面板至少有最小宽度
            left_width = max(left_width, self.left_panel_min_width)
            center_width = max(center_width, self.center_panel_min_width)
            right_width = max(right_width, self.right_panel_min_width)
            
            # 强制设置分割器大小
            self.main_splitter.setSizes([left_width, center_width, right_width])