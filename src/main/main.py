# src/main/main.py
# 强制使用UTF-8编码
import sys
import io
import os
import locale

# 打印当前环境信息用于调试
print(f"系统编码: {sys.getdefaultencoding()}")
print(f"文件系统编码: {sys.getfilesystemencoding()}")
print(f"区域设置: {locale.getpreferredencoding()}")

# 设置环境变量以确保UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 强制使用UTF-8编码，添加errors='replace'以避免打印时的编码错误
# 添加检查，确保stdout和stderr不为None（在--windowed模式下可能为None）
if sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr is not None:
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 导入必要的模块
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QFont
from src.gui.main_window import MainWindow

def main():
    """
    应用程序入口函数
    """
    print("初始化应用程序...")
    
    # 创建Qt应用程序实例
    app = QApplication(sys.argv)
    
    # 设置Qt全局编码
    app.setApplicationName("照片水印工具")
    
    # 设置区域设置以支持中文
    qlocale = QLocale(QLocale.Chinese, QLocale.China)
    QLocale.setDefault(qlocale)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 设置全局字体（支持中文显示）
    print("设置全局字体...")
    font = QFont()
    font.setFamily("微软雅黑")
    app.setFont(font)
    
    # 创建并显示主窗口
    print("创建主窗口...")
    window = MainWindow()
    
    # 显示窗口
    window.show()
    
    # 运行应用程序主循环
    try:
        print("启动应用程序主循环...")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"应用程序退出时出错: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()