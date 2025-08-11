"""核心线程
Qt的线程
"""

# 自带的库
import traceback                # 崩溃分析
from time import sleep          # 暂停
from _ctypes import COMError    # 标准库模块
# 第三方库
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
from PyQt6.QtWidgets import QTextBrowser
# 自己的模块
from UI.arisu_qq_chat_ai_core import ArisuQQChatAICore
from arisu_logger import critical
from deepseek_conversation_engine import DeepseekConversationEngine
from qq_message_monitor import QQMessageMonitor

# 信号持有类（必须继承 QObject）
class Signals(QObject):
    """用来信号更新的，也就是GUI更新"""
    # 状态打印信号
    print_signal = pyqtSignal(QTextBrowser, str)  # 参数：输出控件，文本
    # 崩溃信号
    error_signal =  pyqtSignal(QTextBrowser, object, str)  # 参数：输出控件，崩溃的对象，文本

class ArisuThreading(QRunnable):
    def __init__(self, print_widget, qq_group_name, bot_name, root
                 , exit_password,init_role, qq_group_location, remove_dangerous_order):
        """Qt线程（对接口的实现）
        print_widget ： 输出窗口
        qq_group_name ：QQ群名
        bot_name ：机器人名
        root ：最高权限者
        exit_password ：退出指令的密码
        init_role ：初始人设
        qq_group_location ：0,0（窗口的位置，文本的形式）
        remove_dangerous_order ：移除危险指令 False（布尔值）
        """
        super().__init__()
        self.is_task_progress = True                        # 退出标志位
        self.print_widget : QTextBrowser = print_widget     # 输出窗口
        self.qq_group_name = qq_group_name                  # QQ群名
        self.bot_name = bot_name                            # 机器人名
        self.root = root                                    # 最高权限者
        self.exit_password = exit_password                  # 退出指令的密码
        self.init_role = init_role                          # 初始人设
        self.qq_group_location = qq_group_location          # 0,0（窗口的位置，文本的形式）
        self.remove_dangerous_order= remove_dangerous_order # 移除危险指令
        """额外属性"""
        self.keep_win_time: int = 10    # 保持窗口的时间
        self.monitoring_time: int = 1   # 消息刷新时间
        self.warning_of_overrepresentation  = "雑魚权限？真の杂鱼~🐟呢"    # 越权警告的发送的文本
        # self.id = None                # 线程id
        self.signal = Signals()         # 实例化信号的类

    def run(self):
        try:
            # 线程id
            # self.id = threading.get_ident()
            """实例化对象"""
            # print(qq_group_name, bot_name, root, exit_password, init_role, qq_group_location, remove_dangerous_order)
            # deepseek消息回复(示例化对象没有顺序要求)
            deepseek = DeepseekConversationEngine(self.init_role)  # 给deepseek这个外部变量赋值（让外部函数也能调用）

            # qq消息监听者
            arisu = QQMessageMonitor(self.qq_group_name, self.bot_name, 4)

            # 外部函数(传入需要的对象)
            ef = ArisuQQChatAICore(deepseek, arisu, self.root, self.exit_password, self.qq_group_location,
                                   self.remove_dangerous_order)

            # 保持窗口(显示、位置、大小)，设置10秒进行一次保持
            ef.thread_keep_win(self.keep_win_time)
            print(f"窗口位置:{ef.qq_group_x, ef.qq_group_y}\t保持原始窗口的刷新时间:{self.keep_win_time}秒/刷")

            """“状态输出重定向”"""
            try:
                # 设置最多为50行，多的自动删除，每次增加都是在最新的一行
                self.print_widget.document().setMaximumBlockCount(50)
                # 打印绑定窗口的信息
                text = f"{arisu.output_text}\n" if arisu.output_text else "未成功初始化窗口\n"
                self.signal.print_signal.emit(self.print_widget, text)  # 使用信号更新打印避免崩溃
            except (RuntimeError,TypeError):
                critical("启动AI自动回复过程中强行关闭了窗口")
            """核心循环逻辑"""
            while self.is_task_progress:    # 使用变量来确保是否执行和退出
                """监听窗口控制"""
                # 默认一秒监听一次窗口，防止CUP占用过高
                sleep(self.monitoring_time)
                # arisu.monitor_message()  # 对新消息进行监控
                if text := arisu.monitor_message():                      # 对新消息进行监控
                    self.signal.print_signal.emit(self.print_widget, text)

                """消息处理"""
                if len(arisu.message_processing_queues) > 0:  # 消息队列不为空，进行队列处理
                    reply = ef.split_respond_msg()  # 解析需要回应的消息
                    arisu.message_processing_queues.pop(0)  # 清理回应的消息(出队)[必须在split_respond_msg之后]
                    """开始消息处理逻辑（不是聊天就是指令）"""
                    # 非指令
                    if not reply[3]:
                        """聊天回复"""
                        reply = deepseek.ask(f"{reply[0]}:{reply[1]}，时间:{reply[2]}", False)  # 发出请求并回应(这里不重复打印到屏幕上)
                        arisu.send_message(reply)
                    # 接收到了指令（检测指令是否存在）
                    elif ef.is_order(reply[1]):  # 指令库里面检索指令(顺序不能反，因为指令可能带有参数)
                        """指令操作"""
                        # 分割指令和参数
                        order, args = ef.split_order_args(reply[1])
                        # 是否有权限调度指令(包括root和非root的指令)
                        if ef.check_permission(order, reply[0]):  # 传入指令和发送者
                            arisu.send_message(ef.execute_order(order, args))  # 传入指令执行后拿到返回结果并发送
                        else:
                            # 无权操作后的警告
                            arisu.send_message(self.warning_of_overrepresentation)  # 传入指令执行后拿到返回结果并发送
                    else:
                        """使用了不存在的指令(不是聊天也无法调用指令库的指令)"""
                        print("接收到了一条不存在的指令(不是聊天也没有在指令库中找到指令)")
                        arisu.send_message("不存在该指令")
                else:
                    pass  # print("出现新消息，这里不进行打印，因为监视方法已经打印了")
        except COMError as e:
            # # 设置崩溃后不自动删除对象，继续延用对象并重启线程
            # self.setAutoDelete(False)
            error_msg = (f"线程崩溃: {str(e)}\n{traceback.format_exc()}\n"
                         f"错误提示：\n未检测到 {self.qq_group_name} 窗口，窗口被关闭了，请重新打开窗口\n"
                         f"10秒后将自动重启该线程，请确保窗口已经打开并且在桌面上了")
            # 发射崩溃的信号，传递自身和错误
            self.signal.error_signal.emit(self.print_widget, self, error_msg)
        except Exception as e:
            error_msg = (f"线程崩溃: {str(e)}\n{traceback.format_exc()}\n"
                         f"错误提示：检测到线程池里面的线程崩溃,失去对 {self.qq_group_name} 窗口的控制，将在10秒后重启该线程")
            # error_msg = f"线程崩溃: {str(e)}\n{traceback.format_exc()}"
            # 发射崩溃的信号，传递自生和错误
            try:
                self.signal.error_signal.emit(self.print_widget, self, error_msg)
            except (RuntimeError, TypeError):
                critical("启动AI自动回复过程中强行关闭了窗口")

    def kill(self):
        """停止线程"""
        self.is_task_progress = False   # 设置标志为假

    def disconnect_signal(self):
        """断开信号连接
        我直接采用销毁信号对象，会自动将所有连接会自动断开
        """
        self.signal.deleteLater()   # 销毁信号对象