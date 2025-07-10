from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt


class ResizableWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置无边框窗口但保留调整大小功能
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowSystemMenuHint
        )

        # 关键：通过样式表设置可调整大小的边框
        self.setStyleSheet("""
            QMainWindow {
                border: 6px solid transparent; /* 定义可拖动区域宽度 */
                background-color: #f0f0f0;
            }
            QMainWindow::handle {
                /* 为每个调整手柄设置样式 */
                background-color: rgba(100, 100, 100, 50);
                width: 6px;
                height: 6px;
            }
        """)

        # 允许窗口调整大小
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )


# 使用示例
if __name__ == "__main__":
    app = QApplication([])
    window = ResizableWindow()
    window.resize(800, 600)
    window.show()
    app.exec()