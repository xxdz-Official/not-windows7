import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QHBoxLayout, QVBoxLayout, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QPixmap, QFont, QFontDatabase


class ErrorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 窗口基础配置，扁一点
        self.setWindowTitle('未知错误0x80070005')
        self.setFixedSize(680, 215)

        # 去掉窗口图标
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.CustomizeWindowHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowStaysOnTopHint
        )

        # 主布局，不留边距
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setStyleSheet("")

        # ===== 上半部分：图标 + 文字内容 =====
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white;")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(35, 35, 35, 20)
        content_layout.setSpacing(25)

        # 左边放图标
        icon_label = QLabel()
        icon_size = 55
        try:
            icon_pixmap = QPixmap('img/imageres_98.ico')
            if not icon_pixmap.isNull():
                icon_pixmap = icon_pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(icon_pixmap)
            else:
                icon_label.setText("✖")
                icon_label.setStyleSheet("font-size: 50px; color: #E81123; background-color: transparent;")
        except:
            icon_label.setText("✖")
            icon_label.setStyleSheet("font-size: 50px; color: #E81123; background-color: transparent;")
        icon_label.setFixedSize(icon_size + 10, icon_size + 10)
        icon_label.setAlignment(Qt.AlignCenter)

        # 右边是文字区
        text_widget = QWidget()
        text_widget.setStyleSheet("background-color: white;")
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        # 加载字体，直接撇img里了（懒得新建文件夹）
        font_id = QFontDatabase.addApplicationFont('img/Dengl.ttf')
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        font = QFont(font_families[0], 10)
        font.setPointSize(10)

        reason_label = QLabel('原因:可能是权限不足/内存不足/磁盘不足/宇宙射线干扰')
        reason_label.setWordWrap(True)
        reason_label.setFont(font)
        reason_label.setStyleSheet("background-color: transparent; color: #000000;")

        solution_label = QLabel('建议解决方案:1.重启2.重装系统3.重买电脑')
        solution_label.setWordWrap(True)
        solution_label.setFont(font)
        solution_label.setStyleSheet("background-color: transparent; color: #000000;")

        tips_label = QLabel('最好的答案是给XXDZ一个三连')
        tips_label.setWordWrap(True)
        tips_label.setFont(font)
        tips_label.setStyleSheet("background-color: transparent; color: #000000; font-weight: bold;")

        text_layout.addWidget(reason_label)
        text_layout.addWidget(solution_label)
        text_layout.addWidget(tips_label)
        text_layout.addStretch()

        content_layout.addWidget(icon_label, 0, Qt.AlignTop)
        content_layout.addWidget(text_widget, 1)

        main_layout.addWidget(content_widget, 1)

        # ===== 下半部分：灰色按钮区域 =====
        button_frame = QFrame()
        button_frame.setFixedHeight(65)
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F0F0;
                border-top: 1px solid #D0D0D0;
            }
        """)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 15, 0)
        button_layout.addStretch()

        # 确定按钮，纯原生的
        self.ok_button = QPushButton('确定')
        self.ok_button.setFixedSize(120, 40)
        self.ok_button.setStyleSheet("")
        self.ok_button.setFont(font)
        self.ok_button.clicked.connect(self.on_ok_clicked)

        button_layout.addWidget(self.ok_button)

        main_layout.addWidget(button_frame)

        # 定位到鼠标位置，往左偏100px
        cursor_pos = QCursor.pos()
        window_x = cursor_pos.x() - 250
        window_y = cursor_pos.y() - 20
        self.move(window_x, window_y)

        # 高频跟随鼠标，1ms刷新，丝滑
        self.timer = QTimer()
        self.timer.timeout.connect(self.follow_mouse)
        self.timer.start(1)

    def follow_mouse(self):
        try:
            # 动画中就不跟鼠标了，避免鬼畜
            if hasattr(self, '_animating') and self._animating:
                return

            pos = QCursor.pos()
            screen_width = QApplication.primaryScreen().size().width()
            screen_height = QApplication.primaryScreen().size().height()
            edge_threshold = 50

            # 鼠标到边缘了？让窗口飞出去！
            if pos.x() < edge_threshold:
                self.animate_window(-self.width() - 100, pos.y() - 20)
                return
            elif pos.x() > screen_width - edge_threshold:
                self.animate_window(screen_width + 100, pos.y() - 20)
                return
            elif pos.y() < edge_threshold:
                self.animate_window(pos.x() - 250, -self.height() - 100)
                return
            elif pos.y() > screen_height - edge_threshold:
                self.animate_window(pos.x() - 250, screen_height + 100)
                return

            # 正常跟着鼠标走
            self.move(pos.x() - 250, pos.y() - 20)
        except:
            pass

    def animate_window(self, target_x, target_y):
        """窗口飞出动画，带点物理感"""
        self._animating = True
        steps = 20
        current_x = self.x()
        current_y = self.y()
        dx = (target_x - current_x) / steps
        dy = (target_y - current_y) / steps

        def step():
            nonlocal current_x, current_y, steps
            if steps > 0:
                current_x += dx
                current_y += dy
                self.move(int(current_x), int(current_y))
                steps -= 1
                QTimer.singleShot(3, step)  # 每3ms一帧，飞得更快！
            else:
                # 飞完了就关掉
                self._animating = False
                self.close()
                QApplication.quit()

        step()

    def on_ok_clicked(self):
        self.close()
        QApplication.quit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            QApplication.quit()
        else:
            super().keyPressEvent(event)


import os
import tempfile

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--preload', action='store_true', help='预加载模式（不显示窗口）')
    parser.add_argument('--show', action='store_true', help='显示窗口模式')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyle('windowsvista')

    # 信号文件路径
    signal_file = os.path.join(tempfile.gettempdir(), 'window_show_signal.txt')
    print(f"[信号] 信号文件路径: {signal_file}")

    if args.preload:
        # 预加载：窗口先藏着，等信号
        print("预加载模式：窗口已准备就绪，等待显示信号...")

        # 清掉旧的信号文件
        if os.path.exists(signal_file):
            os.remove(signal_file)

        # 建窗口但不显示
        window = ErrorWindow()
        window.hide()

        # 定时检查信号文件
        def check_signal():
            if os.path.exists(signal_file):
                # 收到信号，窗口现身！
                window.show()
                window.raise_()
                window.activateWindow()
                # 删掉信号文件，防止重复触发
                os.remove(signal_file)
                print("窗口已显示")

        timer = QTimer()
        timer.timeout.connect(check_signal)
        timer.start(50)  # 每50ms瞄一眼，更及时

        sys.exit(app.exec_())
    else:
        # 普通模式，直接显示吧
        window = ErrorWindow()
        window.show()
        sys.exit(app.exec_())