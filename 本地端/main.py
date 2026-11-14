# main.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import threading
import sys
import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QCursor


# Windows API 获取鼠标位置
user32 = ctypes.windll.user32

def get_cursor_pos():
    """用Windows API把鼠标位置薅出来"""
    point = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y


class SimpleHandler(BaseHTTPRequestHandler):
    """处理HTTP请求的处理器"""

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'status': 'ok', 'message': '后端运行正常'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/message':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
                user_message = data.get('message', '').strip()

                print(f"[消息] 收到: {user_message}")
                print(f"[时间] {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 40)

                if not user_message:
                    response = {'status': 'error', 'reply': '消息不能为空'}
                    status_code = 400
                    print("[警告] 消息是空的")
                else:
                    reply_text = f"收到: {user_message}"
                    response = {'status': 'success', 'reply': reply_text}
                    status_code = 200
                    print(f"[成功] 回复: {reply_text}")

            except json.JSONDecodeError:
                response = {'status': 'error', 'reply': '无效的JSON格式'}
                status_code = 400
                print("[坏！！！] JSON解析失败")
            except Exception as e:
                response = {'status': 'error', 'reply': f'服务器错误: {str(e)}'}
                status_code = 500
                print(f"[炸了] 服务器错误: {str(e)}")

            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/api/spawn_window':
            try:
                print("[窗口] 收到创建窗口请求")
                x, y = get_cursor_pos()
                print(f"[坐标] 鼠标位置: ({x}, {y})")

                global qt_app
                if qt_app:
                    qt_app.create_window(x, y)

                response = {'status': 'success'}
                status_code = 200
            except Exception as e:
                response = {'status': 'error', 'message': str(e)}
                status_code = 500
                print(f"[坏！！！] 创建窗口失败: {e}")

            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


import subprocess
import os


class QtApp:
    """Qt应用管理类 - 通过预加载的子进程调用window.py"""

    def __init__(self):
        self.app = None
        self.has_created = False
        self.process = None
        self.preloaded = False

    def preload_window(self):
        """提前把window.py进程拉起来，避免首次打开时卡顿"""
        if self.preloaded:
            return

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            window_script = os.path.join(script_dir, "window.py")

            # 启动预加载进程，但不显示窗口
            self.process = subprocess.Popen(
                [sys.executable, window_script, "--preload"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            self.preloaded = True
            print("[预加载] 窗口进程已就绪（信号检测间隔100ms）")

            # 偷偷监控进程状态
            self._monitor_process()

        except Exception as e:
            print(f"[警告] 预加载失败: {e}")

    def create_window(self, x, y):
        print(f"[窗口] 通过预加载进程创建窗口 at ({x}, {y})")

        try:
            import tempfile
            signal_file = os.path.join(tempfile.gettempdir(), 'window_show_signal.txt')

            # 写信号文件，通知预加载进程显示窗口
            with open(signal_file, 'w') as f:
                f.write('show')

            print("[信号] 显示信号已发送到预加载进程")

            # 检查进程状态，如果挂了就重启
            process_running = False
            if self.preloaded and self.process is not None:
                try:
                    # 检查进程是否还在运行
                    if self.process.poll() is None:
                        process_running = True
                        print("[进程] 预加载进程仍在运行，等待显示...")
                    else:
                        print("[进程] 预加载进程已退出，需要重新启动")
                except:
                    process_running = False

            # 如果进程没运行，重新启动预加载进程
            if not process_running:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                window_script = os.path.join(script_dir, "window.py")
                self.process = subprocess.Popen(
                    [sys.executable, window_script, "--preload"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                self.preloaded = True
                print("[预加载] 进程已重新启动")
                self._monitor_process()
                # 等待1秒让窗口进程初始化
                import time
                time.sleep(1.0)
                print("[预加载] 已等待1秒，准备再次发送信号")
                # 再次写信号，确保新进程能读取到
                with open(signal_file, 'w') as f:
                    f.write('show')
                print("[信号] 第二次信号已发送")

        except Exception as e:
            print(f"[坏！！！] 发送显示信号失败: {e}")

    def _monitor_process(self):
        """盯着子进程，挂了就重置标志"""
        def check():
            if self.process:
                ret = self.process.poll()
                if ret is not None:
                    print("[进程] 窗口子进程已退出，可再次触发")
                    self.has_created = False
                    self.process = None
                    self.preloaded = False
                    # 尝试清理信号文件
                    try:
                        import tempfile
                        signal_file = os.path.join(tempfile.gettempdir(), 'window_show_signal.txt')
                        if os.path.exists(signal_file):
                            os.remove(signal_file)
                    except:
                        pass
                else:
                    import threading
                    threading.Timer(0.5, check).start()
        import threading
        threading.Timer(0.5, check).start()

    def run(self):
        # 启动时预加载窗口
        self.preload_window()

        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


# 全局Qt应用实例
qt_app = None


def run_server(port=5000):
    """启动服务器"""
    global qt_app

    qt_app = QtApp()

    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)

    print('=' * 50)
    print(f'[服务器] 已启动: http://127.0.0.1:{port}')
    print(f'[等待] 前端连接中... (按 Ctrl+C 停止)')
    print('=' * 50)

    def run_http():
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

    http_thread = threading.Thread(target=run_http, daemon=True)
    http_thread.start()
    print("[HTTP] 服务器线程已启动")

    try:
        qt_app.run()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
        print("[晚安喵] 服务器已关闭")


if __name__ == '__main__':
    # 添加环境变量标记，确保预加载模式正确
    os.environ['PYTHONUNBUFFERED'] = '1'
    run_server()