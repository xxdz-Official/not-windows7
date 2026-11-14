import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor


class SystemWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("拖出窗口")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                background-color: white;
                padding: 10px;
                border: 1px solid #ccc;
            }
        """)
        self.init_ui()
        self.follow_mouse()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("🎯 从网页拖出的窗口")
        title.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #2b6ab8;
                font-size: 14pt;
                font-weight: bold;
                border: none;
                padding: 0;
            }
        """)
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        content = QLabel("这是一个从网页中拖拽出来的系统窗口！\n\n可以像普通Windows窗口一样移动、缩放。")
        content.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 20px;
                font-size: 12pt;
            }
        """)
        content.setAlignment(Qt.AlignCenter)
        layout.addWidget(content)

        self.setLayout(layout)

    def follow_mouse(self):
        pos = QCursor.pos()
        self.move(pos.x() - 200, pos.y() - 125)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('windowsvista')
    window = SystemWindow()
    window.show()
    sys.exit(app.exec_())
