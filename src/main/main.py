# src/main/main.py
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.gui.main_window import MainWindow


def main():
    """
    应用程序入口函数
    """
    # 创建Qt应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 设置全局字体（支持中文显示）
    font = QFont()
    font.setFamily("微软雅黑")
    app.setFont(font)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序主循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()