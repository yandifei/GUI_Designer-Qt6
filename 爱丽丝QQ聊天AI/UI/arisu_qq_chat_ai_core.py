"""arisu_qq_chat_ai_core
爱丽丝QQ聊天AI核心
直接整合之前的资源写的一个完整的类
指令系统+权限系统+接入deepseekAI+QQ监听
"""

import os                       # 操作系统库
# import sys                    # 系统库
import shutil                   # 清理文件夹下的所有内容（官方推荐）
from datetime import datetime   # 时间计算
from time import sleep          # 时间停顿
import threading                # 线程

# 第三方库
import psutil                                                           # 进程时间查询
import win32con                                                         # 组件
import win32gui                                                         # 句柄查找
import win32process                                                     # 进程
import win32ui                                                          # 截图使用
from PIL import Image                                                   # 截图使用
# from PyQt6.QtWidgets import QApplication                                # 退出
from qq_message_monitor import QQMessageMonitor                         # 导入QQ消息监控者这个类
from deepseek_conversation_engine import DeepseekConversationEngine     # 导入deepseek对话引擎这个类
from jmcomic import create_option_by_file, download_album, jm_exception # 导入禁漫模块
from UI import __version__                                              # 从包里面拿到最新版本

class ArisuQQChatAICore:
    def __init__(self, deepseek: DeepseekConversationEngine, arisu : QQMessageMonitor, root, exit_password, qq_group_location : str,
                 remove_dangerous_order : str):
        """额外函数实现的类
        deepseek ： DeepseekConversationEngine的实例化对象
        arisu ： QQMessageMonitor实例化对象
        root ： 超级管理员
        exit_password ： 退出密码
        qq_group_location ： QQ群位置（字符串如"1,1"）
        remove_dangerous_order : 危险指令移除（默认为False）
        """
        """数据初始化"""
        # 创建配置对象(禁漫模块)
        self.arisu = arisu                                                              # 实例化时需要指定
        self.deepseek = deepseek                                                        # 实例化时需要指定
        self.option = create_option_by_file("./用户设置/option.yml")                     # 禁漫配置
        self.qq_group_x, self.qq_group_y = self.analyze_location(qq_group_location)     # 解析放置qq群的位置
        """权限体系"""
        # 超管
        self.root = root
        # 管理员
        self.administrators = arisu.qq_group_administrator # 直接接收Q群群主和Q群管理员名字
        # #  其他人
        # self.others = None  # 非root非群主非群管理
        # 退出密码
        self.exit_password = exit_password
        # 指令权限限制（默认开启指令权限限制，仅管理员调用非root指令系统）
        self.is_order_permission_limit = True
        """指令体系"""
        self.remove_dangerous_order = True if remove_dangerous_order == "True" else False  # 移除危险指令(默认为False，不移除)
        # 指令调用时附带的参数(不可删除)
        self.args = ""
        # 无限制指令
        self.unlimited_list = self.load_unlimited_list()    # 加载无限制指令
        # root权限指令
        self.root_orders: list = self.load_root_orders()  # 加载root权限的指令列表
        # 指令映射
        if self.remove_dangerous_order:
            self.order_dict = self.load_limit_order_dict()  # 限制指令加载
        else:
            self.order_dict = self.load_order_dict()        # 无限制指令加载

        # 添加到self.order_dict或self.order_dict中，以及纳入无限制指令中
        self.add_pic_download_map_order()  # 添加图片下载映射指令
        """外部标志"""
        self.running = True # 执行退出指令后为False

    """初始化类传入参数解析"""
    @staticmethod
    def analyze_location(qq_group_location : str):
        """解析参数
        参数：
        qq_group_location : qq群位置（字符串，这里不需要校验，校验部分已经给前端的后端完成了）
        返回值：
        result[0], result[1] : 元组
        """
        format_string = qq_group_location.replace("，", ",") # 替换字符串（之前是允许接收，和,的）
        result = format_string.split(",", 1) # 分割字符串
        return int(result[0]), int(result[1])

    """额外功能方法"""
    def thread_keep_win(self, sleep_time: int = 1):
        """创建一个线程不断保持控制窗口
        参数：
        sleep_time : 多少秒执行该操作
        作用（禁止设置焦点，传窗口失焦会导致消息无法发送）：
        1.展示窗口
        2.置顶窗口
        3.保存窗口位置
        4.保持窗口大小
        """
        def keep_win():
            while True:
                self.arisu.show_win()                               # 展示窗口
                self.arisu.top_win()                                # 置顶窗口
                self.arisu.move(self.qq_group_x, self.qq_group_y)   # 保存窗口位置
                self.arisu.keep_size()                              # 保持窗口大小
                sleep(sleep_time)                                   # 休眠(避免重复执行导致CPU占用过高)

        # 保持窗口(创建一个守护进程随进程退出而退出)
        keep_win_threading = threading.Thread(target=keep_win, daemon=True)
        # 启动线程(非守护线程,包括主线程退出时立即终止)
        keep_win_threading.start()

    def exit_program(self, password):
        """退出程序
        参数：
        password ：退出程序的密码
        """
        # 匹配密码（字符串是否相同）
        if self.exit_password != password:
            # 密码错误
            return False
        # self.arisu.send_message(f"deepseek对话引擎已退出\n{self.arisu.monitor_name}：机器人已关闭")
        # # 退出程序（实际是退出当前进程）
        # sys.exit(1) # 设置1为退出码
        # # 退出程序（实际是退出整个软件）
        # QApplication.exit()
        # 退出当前的这个AI线程
        self.running = False    # 设置退出标志位
        return True

    @staticmethod
    def get_help():
        """帮助查询"""
        return f"""
爱丽丝QQ聊天AI💬，版本：{__version__}✨
1️⃣ Github仓库地址🔗：https://github.com/yandifei/ArisuQQChatAI 🚀
2️⃣ 使用 #指令查询📖 可以查询所有指令，但是部分指令的执行需要权限⚙️
3️⃣ 如果你喜欢的话，就给爱丽丝个✨Star✨吧！ (ﾉ>ω<)ﾉ❤️🌟
4️⃣ ❗禁止将该项目用于引流(带节奏)、纯色情(非学习教育和无任何意义的目的)、当键政等非法用途🚫
5️⃣ 💡还是那句话：少🦌点吧，机器人提供的情绪价值是为了让你有更好的明天🌞，禁止把它当成xn⚠️
6️⃣ 🔧本项目是基于自主研发的DeepseekConversationEngine类库开发的类库去完成用，通过pyautomation库对QQ窗口进行操作🤖
7️⃣ 📦AI类库仓库地址：https://github.com/yandifei/DeepseekConversationEngine
"""

    def get_orders(self):
        """查询所有指令"""
        return "\t".join([order for order in self.order_dict])

    def jm_down_order(self, jm_album_id):
        """禁漫本子下载指令实现
        参数：
        jm_album_id ； 本子专辑指令（250745）
        """
        # # 分割出专辑id
        # jm_album_id = order.replace("#jm:", "")  # 拿到jm本子并放到剪切板(移除多余的字符后进行请求)
        # if jm_album_id == "":    #使用了指令但是没有填任何参数
        #     print("使用了jm下载指令但是没有填本子id")
        #     return "使用了jm下载指令但是没有填本子id"
        # 使用前先清理之前的资源（因为之后要放到剪切板导致无法删除pdf）
        try:
            # 清理残留的资源(把整个缓存目录删除)和目录还原(目录创建回去)
            shutil.rmtree("./logs/发送缓存")
            os.mkdir("./logs/发送缓存")
            shutil.rmtree("./logs/下载缓存")
            os.mkdir("./logs/下载缓存")
        except FileNotFoundError:
            print("目录不存在，无需删除")
        except (PermissionError, FileExistsError):
            # 满载第二次请求是PermissionError(shutil.rmtree)，带三次是FileExistsError(os.mkdir)
            return "请等待上一份的jm发送完再使用该指令(我不是服务器，垃圾CUP没法满足同时下载多个文件)，如您不能见谅请把您的CPU借我用用！"

        # 使用option对象来下载本子
        down_error = ""   # 下载错误信息
        try:
            download_album(jm_album_id, self.option)
        except jm_exception.PartialDownloadFailedException as e:
            # 部分下载失败
            print(e)
            down_error = str(e).split(": [",1)[0] # 必须转换不然剪切板就报错
        except jm_exception.MissingAlbumPhotoException as e:
            # 请求的本子不存在
            print(e)
            down_error = str(e) # 必须转换不然剪切板就报错
        except jm_exception.JmcomicException as e:
            print("本子输入为空")
            down_error = e
        # 文件名字需改（这里使用的是整合包的本子，所以名字会变动）
        for file_name in os.listdir("./logs/发送缓存"):
            # 找到后缀名为pdf的文件
            if file_name.endswith(".pdf"):
                # 重命名文件为本子的专辑ID(注意原文件是有后缀的，改的时候才要加)
                os.rename(f"./logs/发送缓存/{file_name}",f"./logs/发送缓存/{jm_album_id}.pdf")
                break # 退出循环
        else:
            print("没有找到PDF文件")
            down_error += "指令结果：没有找到PDF文件"
            return down_error
        # 构建文件下载缓存的绝对路径
        absolute_path = os.path.abspath(f"./logs/发送缓存/{jm_album_id}.pdf")  # 使用绝对路径(避免路径错误)
        # 实现文件的复制
        self.arisu.copy_file(absolute_path)
        # 调用文件发送
        self.arisu.paste_send_file()
        # 等待1秒的点击发送完毕
        sleep(1)
        return down_error if down_error else "本子已发送，未看到可能是文件太大了还在上传"

    def get_administrators(self):
        """获得管理员
        返回格式化好的字符串
        """
        format_string = "群主：" + self.administrators[0]
        for name in self.administrators[1:]:
            format_string += "\n群管理：" + name
        return format_string

    def add_pic_download_map_order(self):
        """添加图片下载映射指令"""
        # 构造线程
        def thread_image_batch_download(num, key):
            """线程图片下载"""
            # 构造线程
            thread = threading.Thread(target=self.image_batch_download, name='图片批量下载',args=(key, num), daemon=True)
            # 启动线程
            thread.start()
            # 返回True去执行成功语句
            return True

        # 遍历图片映射表(遍历keys)
        for key in self.arisu.picture_map.keys():
            # 直接使用 lambda 函数，并使用默认参数捕获当前 key 的值
            self.order_dict[f"#{key}"] = [lambda num, k=key: thread_image_batch_download(int(num), k), "开始发送图片",
                "1.图片发送失败\n2.图片超出限制(100)\n3.参数错误"]
            self.unlimited_list.append(f"#{key}")
            # 非线程
            # self.order_dict[f"#{key}"] = [lambda num, k=key: self.image_batch_download(int(num), k), "开始发送图片",
            #                               "1.图片发送失败\n2.图片超出限制(100)\n3.参数错误"]

    def image_batch_download(self, key, num):
        """图片批量下载
        参数：
        key ： json文件的键
        num ： 图片下载的张数
        """
        # 检查批量下载是否超标
        if num > 100:
            return False
        # 开始批量下载并执行
        for _ in range(num):
            # 从json拿到url->使用arisu方法进行图片下载复制粘贴发送
            self.arisu.send_url_image(self.arisu.picture_map[key])
        return True

    def send_screen_arisu(self):
        """发送后台截图当前窗口状态
        """
        try:
            """截图"""
            # 类名和标题查找句柄
            hwnd = win32gui.FindWindow("Qt691QWindowIcon", "爱丽丝")
            # 获取窗口坐标
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            # 获取窗口设备上下文
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            # 创建位图对象
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, right - left, bottom - top)
            # 将位图选入设备上下文
            saveDC.SelectObject(saveBitMap)
            # 复制设备上下文到内存设备上下文
            saveDC.BitBlt((0, 0), (right - left, bottom - top), mfcDC, (0, 0), win32con.SRCCOPY)
            # 获取位图信息
            bmp_info = saveBitMap.GetInfo()
            bmp_str = saveBitMap.GetBitmapBits(True)
            # 生成PIL图像
            image = Image.frombuffer(
                'RGB',
                (bmp_info['bmWidth'], bmp_info['bmHeight']),
                bmp_str, 'raw', 'BGRX', 0, 1
            )
            # 保存图像
            image.save("./logs/下载缓存/当前界面状态.png")
            """发送"""
            self.arisu.send_image("./logs/下载缓存/当前界面状态.png")
        except Exception as e:
            # 打印错误
            print(e)

    @staticmethod
    def get_arisu_running_time():
        """获得软件的运行时间
        返回值：
        create_time ： 爱丽丝进程的创建时间
        """
        # 获得当前窗口的句柄
        hwnd = win32gui.FindWindow("Qt691QWindowIcon", "爱丽丝")
        # 获取窗口的进程ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        # 获取进程创建时间 (使用psutil简化操作)
        process = psutil.Process(pid)
        # 进程创建时间戳（自1970年以来的秒数）
        create_time_timestamp = process.create_time()
        # 转换为datetime对象
        create_time = datetime.fromtimestamp(create_time_timestamp)
        now = datetime.now()
        uptime = (now - create_time)
        # 计算天、小时、分钟和秒
        days = uptime.days
        seconds = uptime.seconds
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}天 {hours}时:{minutes}分:{seconds}秒"

    @staticmethod
    def get_computer_usage():
        """获得cpu、内存的使用率（非物理核心），以及爱丽丝对CPU、内存的使用率
        参数：
        返回值：
        1秒钟内CPU所有逻辑核心的使用率
        内存当前使用率的百分比

        """
        # 获得当前窗口的句柄
        hwnd = win32gui.FindWindow("Qt691QWindowIcon", "爱丽丝")
        # 获取窗口的进程ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        # 构建发送文本(1秒内CPU占用百分比，内存占用百分比，该进程对CPU占比，该进程对内存占比)
        return f"""
CPU占比：{psutil.cpu_percent(1, True)}%
内存占比：{(psutil.swap_memory().total / psutil.swap_memory().used):.2f}%
爱丽丝对CPU当前占比：{psutil.Process(pid).cpu_percent()}%
爱丽丝对内存当前占比：{psutil.Process(pid).memory_percent(memtype='rss')}
"""

    """消息处理（分割，提取）"""
    def split_respond_msg(self):
        """分割响应消息
        参数：
        arisu_object ： QQMessageMonitor这个对象(实例化就是arisu)
        返回值：
        sender ： 发送方(这里是发送方的名字，我接收它的名字)
        msg ： 消息(我需要进行回复的消息，去除@自己的名字 这个部分)
        accept_message ： 时间(发送的时间)
        is_order : 是否是指令
        """
        """发送者处理"""
        sender = self.arisu.message_processing_queues[0]["发送者"]
        # 如果发送者是自己这就就改名（@自己），因为回复时会进行@导致循环的发生（之后处理掉了）
        """消息处理"""
        message = self.arisu.message_processing_queues[0]["发送消息"]
        message = message.replace(f"@{self.arisu.monitor_name} ", "")
        """时间处理"""
        time = self.arisu.message_processing_queues[0]["发送时间"]
        """指令判断"""
        # 1.消息不为空2.有"#"开头3."#"后有字符(需要判断的文本是没有@符号的)
        if message and message[0] == "#" and len(message) > 2:
            is_order = True
        else:
            is_order = False
        # sender需要修改，所有不能为元组
        return [sender, message, time, is_order]

    """权限处理（判断）"""
    def check_permission(self, order, sender_name):
        """检查权限
        order : 发送过来的指令（带指令参数）
        sender_name : 发送者的名字
        1. 检查是否为root权限
        2. 检查是否开启了“指令权限限制”
        3. 检查权限是否足够
        """
        # 检查是否为root指令
        if order in self.root_orders:
            # 检查是否为为root权限
            # print(sender_name, self.root)
            if sender_name == self.root:
                return True
            else:
                return False
        # 非root指令
        else:
            # print(self.is_order_permission_limit, order not in self.unlimited_list, sender_name)
            # 开启指令权限限制(指令限制和不是无限制的指令)
            if self.is_order_permission_limit and order not in self.unlimited_list:
                # 发送者不是最高权限者也不是群主或群管理员
                 if sender_name == self.root or sender_name in self.administrators:
                     return True
                 return False   # 啥权限也没有
            # 未开启指令权限限制
            else:
                return True

    def close_order_permission_limit(self):
        """关闭指令权限限制"""
        self.is_order_permission_limit = False
        return True

    def open_order_permission_limit(self):
        """开启指令权限限制"""
        self.is_order_permission_limit = True
        return True

    @staticmethod
    def split_order_args(order):
        """分割指令和参数
        参数：
        order ： 用户给的指令，可能附带参数
        返回值：
        order ： 原始的指令
        args ： 附带的参数，如果没有参数则为""
        """
        if ":" in order:
            # 如果:后面什么都没有则切割后的参数为""
            split_result = order.split(":",1)       # 切割键(字典方法的键)和指令
            return split_result[0], split_result[1]
        return order, ""

    """指令处理（判断执行，）"""
    def execute_order(self, order, args):
        """指令执行
        order : 接收到的指令
        args : 指令需要的参数，可能为""和非空
        1.判断指令是否合法(不需考虑指令是否存在，仅校验指令是否带参数)
        2.判断指令是否需要二级调用
        """
        # 函数参数(有些函数方法需要参数，从用户输入的指令中获取)
        self.args = args
        # # 检查指令(用户输入的指令)是否带有参数
        # if ":" in order:
        #     # 获得参数(参数可能分割后为空，后面可以通过异常来捕获)
        #     split_result = order.split(":",1)       # 切割键(字典方法的键)和指令
        #     self.args = split_result[1]             # 如果:后面什么都没有则切割后的参数为""
        #     # 需要执行的方法(不包含参数)
        #     order = split_result[0]                 # 拿到纯净的指令用来后面带入字典里面去

        # print(type(self.order_dict[order]))
        # 判断是否直接执行指令(可能是True也可能是方法之类的)
        if isinstance(self.order_dict[order][0], bool):   # 直接执行成功/失败执行的指令
            if self.order_dict[order]:  # 成功执行的返回值(成功执行)
                return self.return_result_processing(order,True)
            else:   # 失败执行的返回值(失败执行)
                return self.return_result_processing(order,False)
        # 这里就是直接执行函数、方法了
        else:
            # 异常处理(参数错误无法执行的情况)
            try:
                # 如果有参数就执行参数指令(不管参数对错)
                if self.args:       # ""也为假
                    # 找到映射后从指令列表里面拿到第一个元素[0]，这个元素是匿名函数或True！！！
                    result = self.order_dict[order][0](self.args)   # 执行指令[方法+参数]，也可能是True
                    return_message = self.return_result_processing(order, result)   # 对返回结果做处理
                    return return_message
                # 没有参数的情况
                else:
                    """不带参数的指令"""
                    result = self.order_dict[order][0]()  # 执行指令[方法()]
                    return_message = self.return_result_processing(order, result)   # 对返回结果做处理
                    return return_message
            except TypeError as e:
                print(e)
                return "请填写必要的参数"
            except ValueError as e:
                print(e)
                return self.order_dict[order][2]    # 返回错误指令返回值

    def return_result_processing(self, order, result):
        """对返回结果做处理
        参数：
        order : 指令 (用来判断发送值是否为匿名函数、方法、函数)
        result ： 结果
        1.如果返回结果是函数就执行函数并返回结果（最终一定是字符串）
        2.如果结果不是函数就不执行（直接返回字符串）
        """
        # 执行指令的结果为真或本来就是真值
        if result:
            # 成功执行返回值(看是否为字符串)
            if isinstance(self.order_dict[order][1], str):
                return self.order_dict[order][1]    # 字符串
            else:
                return self.order_dict[order][1]()  # 执行指令[方法]
        # 指令执行结果为假
        else:
            # 失败执行返回值需要执行方法后拿到
            if isinstance(self.order_dict[order][2], str):
                return self.order_dict[order][2]    # 字符串
            else:
                return self.order_dict[order][2]()  # 执行指令[方法]

    def is_order(self, maybe_order):
        """判断是否为指令
        maybe_order ： 需要判断的指令
        """
        if ":" in maybe_order:
            maybe_order = maybe_order.split(":", 1)[0]  # 切割出指令去掉参数部分
        # 检查这个指令是否在指令库里面
        if maybe_order in self.order_dict:
            return True
        return False

    """指令映射表"""
    def load_order_dict(self):
        # 指令映射表(使用lambda来匿名函数,order_dict)
        return {
    # ==================================================额外实现的指令库========================================================="""
    # root(超管)指令
    "#退出": [lambda password: self.exit_program(password), f"deepseek对话引擎已退出\n{self.arisu.monitor_name}：机器人已关闭", "退出密码错误"],

    # 帮助之类的指令
    "#帮助": [True, lambda: self.get_help(), "查询失败"],
    "#指令查询": [True, lambda : self.get_orders(),"查询失败"],

    # 权限管理类
    "#超管": [True, lambda : self.root,"下载失败"],
    "#所有管理员": [True, lambda : self.get_administrators(), "查询失败"],
    "#开启指令权限限制": [lambda : self.open_order_permission_limit(), "已开启指令权限限制", "开启指令权限限制失败"],
    "#关闭指令权限限制": [lambda : self.close_order_permission_limit(), "已关闭指令权限限制", "关闭指令权限限制失败"],

    # 禁漫指令
    "#jm": [True, lambda : self.jm_down_order(self.args),"下载失败"],

    # 远程控制指令
    "#中控截图": [lambda : self.send_screen_arisu(), "截图完成","截图失败"],
    "#运行时间": [True, lambda : self.get_arisu_running_time(), "无法获取运行时间"],
    "#系统资源监控": [True, lambda : self.get_computer_usage(), "无法获取系统资源信息"],
    # ==========================================DeepseekConversationEngine延伸过来的指令=========================================="""
    # 特殊指令
    "#兼容": [lambda : self.deepseek.compatible_openai() ,"已经切换至兼容OpenAI的接口","切换中途发生异常"],
    "#测试接口": [lambda : self.deepseek.use_beat(),"已切换至测试接口","切换中途发生异常"],
    "#初始化": [lambda : self.deepseek.reset(),"已格式化deepseek对话引擎","初始化中途发生异常"],  # 恢复最开始设置的参数（创建对象时的默认参数）
    # 对话参数调节指令
    "#模型切换": [lambda : self.deepseek.switch_model(True),lambda : "已切换至V3模型" if self.deepseek.model_choice == "deepseek-chat" else "已切换至R1模型", "切换中途发生异常"],
    "#V3模型": [lambda : self.deepseek.set_model("V3"),"已切换至V3模型", "切换中途发生异常"],
    "#R1模型": [lambda : self.deepseek.set_model("R1"),"已切换至R1模型", "切换中途发生异常"],
    "#评分": [lambda score : self.deepseek.score_answer(score),"评分成功", "超出打分范围([0-100]分,默认50分)"],
    "#最大token数": [lambda max_tokens=4096 : self.deepseek.set_max_tokens(max_tokens),lambda : f"已修改最大token数为{self.deepseek.max_tokens}", "超出最大token数范围([1-8192]分,默认4096)"],
    "#输出格式": [lambda response_format : self.deepseek.set_response_format(response_format),lambda : f"已修改为{self.deepseek.response_format}格式", "格式有误，指定模型必须输出的格式为\"text\"或\"json_object\""],    # input("请输入指定输出格式(text或json,],默认text):")
    "#敏感词": [lambda sensitive_words : self.deepseek.set_stop(sensitive_words),lambda : f"添加敏感词 {self.args} 成功","添加失败"],    # input("设置敏感词(默认为None):")
    "#删除敏感词": [lambda stop: self.deepseek.del_stop(stop),"删除成功","敏感词不存在"],
    "#流式": [lambda : self.deepseek.set_stream(True),"已切换至流式输出","切换中途发生异常"],
    "#非流式": [lambda : self.deepseek.set_stream(),"已切换至流式输出", "切换中途发生异常"],
    "#开启请求统计": [lambda : self.deepseek.set_stream_options(True),"已开启请求统计", "必须先开启流式(stream)才能开启修改开启这个字段"],
    "#关闭请求统计": [lambda : self.deepseek.set_stream_options(),"已关闭请求统计", "关闭请求统计途中发生异常"],
    "#温度": [lambda temperature : self.deepseek.set_temperature(temperature),lambda : f"已修改温度为{self.deepseek.temperature}", "超出温度范围([0.0-2.0,]默认1.0)"],
    "#核采样": [lambda top_p : self.deepseek.set_top_p(top_p), lambda : f"已修改核采样为{self.deepseek.top_p}", "超出核采样范围([0.0-1.0]分,默认1.0)"],   # float(input("请输入核采样,],数值越小内容部分逻越严谨(0.0-1.0,],默认1.0):"))
    "#工具列表": [lambda : self.deepseek.set_tools(),"修改成功", "修改未成功"],  # input("请输入模型可能会调用的 tool 的列表(默认为None):")
    "#工具开关": [lambda : self.deepseek.switch_tool_choice(),"已开启工具调用", "已关闭工具调用"],
    "#开启对数概率输出": [lambda : self.deepseek.set_logprobs(True), "已开启对数概率输出", "开启对数概率失败"],
    "#关闭对数概率输出": [lambda : self.deepseek.set_logprobs, "已关闭对数概率输出", "关闭对数概率失败"],
    "#位置输出概率": [lambda top_logprobs : self.deepseek.set_top_logprobs(top_logprobs), lambda : f"已修改概率输出个数为{self.deepseek.top_logprobs}", "未开启对数概率输出或参数不在调用范围(0-20)"],  # int(input("请指定的每个输出位置返回输出概率top为几的token(0-20，默尔为None):"))
    # FIM对话参数指令
    "#FIM对话": [True, lambda : self.deepseek.fill_in_the_middle_ask(), "调用失败"],  # 使用FIM对话补全
    "#FIM补全开头": [lambda prompt : self.deepseek.set_prompt(prompt),"已补全开头", "补全开头失败"],
    "#FIM完整输出": [lambda : self.deepseek.set_echo(),"因为服务器那边不接受True，只接受False和None,所以这个功能无效", "因为服务器那边不接受True，只接受False和None,所以这个功能无效"],  # 这个参数就只有False和None了，改不了一点
    "#FIM对数概率输出": [lambda FIM_logprobs : self.deepseek.set_FIM_logprobs(FIM_logprobs),lambda : f"已制定输出中保留{self.deepseek.FIM_logprobs}个最可能输出token的对数概率", "参数不在调用范围[0-20]"],  # int(input("请输入需要多少个候选token数量输出对数概率(默认0):"))
    "#FIM补全后缀": [lambda suffix : self.deepseek.set_suffix(suffix),"已补全后缀", "后缀补全失败"], # input("请输入需要补全的后缀(默认为None):")
    # 上下文参数指令
    "#思维链": [lambda : self.deepseek.reasoning_content_output(), lambda : self.deepseek.reasoning_content,"思维链为空"],  # 会返回False或字符串
    "#对话轮次": [lambda dialog_round : self.deepseek.set_dialog_history(dialog_round), lambda : "已解除对话轮次限制，注意最大token数和高额消费" if self.deepseek.clear_flag == -1 else f"已设置对话轮次为{self.deepseek.clear_flag}轮", "无法设置对话轮次为负数"], # int(input("请输入最大对话轮数，超过自动删除(默认值为5):"))
    "#聊天记录": [lambda : self.deepseek.print_dialog_history(), lambda : "\n".join(self.deepseek.print_dialog_history()),"聊天记录为空"],
    "#清空对话历史": [lambda : self.deepseek.clear_dialog_history(),"已清空对话历史(人设除外)", "对话历史为空无需清空"],
    # 多人设管理指令
    "#人设切换": [lambda role_name : self.deepseek.role_switch(role_name),lambda : f"已切换人设为：{self.args}","提示库不存在该人设"],    # input("请输入切换的人设:")
    "#所有人设": [lambda : self.deepseek.role_list(),lambda : "提示库的所有人设:" + "、".join(self.deepseek.role_list()), "提示库中为空，不存在任何人设"],  # 人设做了处理
    "#人设查询": [lambda role_name : self.deepseek.select_role_content(role_name),lambda : self.deepseek.select_role_content(self.args), "不存在该人设，无法进行打印"],    # input("请输入要查询的人设:")
    "#当前人设": [lambda : self.deepseek.print_role_content(),lambda : f"当前人设:{self.deepseek.role}","当前人设为空"],
    "#人设自定": [lambda role_txt : self.deepseek.set_role(role_txt),"自定义人设成功", "自定义人设失败"],# input("请输入人设内容:")
    "#删除人设": [lambda : self.deepseek.remove_role(),"成功删除人设", "未设置人设，不需要进行删除"],
    # 场景关键词自动调控参数指令
    "#代码": [lambda : self.deepseek.scene_switch("代码"),"已切换至代码场景","切换场景失败"],
    "#数学": [lambda : self.deepseek.scene_switch("代码"),"已切换至数学场景","切换场景失败"],
    "#数据": [lambda : self.deepseek.scene_switch("数据"),"已切换至数据场景","切换场景失败"],
    "#分析": [lambda : self.deepseek.scene_switch("分析"),"已切换至分析场景","切换场景失败"],
    "#对话": [lambda : self.deepseek.scene_switch("对话"),"已切换至对话场景","切换场景失败"],
    "#翻译": [lambda : self.deepseek.scene_switch("翻译"),"已切换至翻译场景","切换场景失败"],
    "#创作": [lambda : self.deepseek.scene_switch("创作"),"已切换至创作场景","切换场景失败"],
    "#写作": [lambda : self.deepseek.scene_switch("写作"),"已切换至写作场景","切换场景失败"],
    "#作诗": [lambda : self.deepseek.scene_switch("作诗"),"已切换至作诗场景","切换场景失败"],
    # 余额和token数查询
    "#余额": [True, lambda : self.deepseek.return_balance(), "无法查询"],
    "#token": [True, lambda : self.deepseek.return_token(), lambda : self.deepseek.return_balance(), "无法查询"]
        }

    def load_limit_order_dict(self):
        """限制指令的字典"""
        # 指令映射表(使用lambda来匿名函数,order_dict)
        return {
    # ==================================================额外实现的指令库========================================================="""
    # 对话参数调节指令
    "#模型切换": [lambda : self.deepseek.switch_model(True),lambda : "已切换至V3模型" if self.deepseek.model_choice == "deepseek-chat" else "已切换至R1模型", "切换中途发生异常"],
    "#V3模型": [lambda : self.deepseek.set_model("V3"),"已切换至V3模型", "切换中途发生异常"],
    "#R1模型": [lambda : self.deepseek.set_model("R1"),"已切换至R1模型", "切换中途发生异常"],
    "#评分": [lambda score : self.deepseek.score_answer(score),"评分成功", "超出打分范围([0-100]分,默认50分)"],
    "#非流式": [lambda : self.deepseek.set_stream(),"已切换至流式输出", "切换中途发生异常"],
    # FIM对话参数
    "#FIM对话": [True, lambda : self.deepseek.fill_in_the_middle_ask(), "调用失败"],  # 使用FIM对话补全
    "#FIM补全开头": [lambda prompt : self.deepseek.set_prompt(prompt),"已补全开头", "补全开头失败"],
    "#FIM完整输出": [lambda : self.deepseek.set_echo(),"因为服务器那边不接受True，只接受False和None,所以这个功能无效", "因为服务器那边不接受True，只接受False和None,所以这个功能无效"],  # 这个参数就只有False和None了，改不了一点
    "#FIM补全后缀": [lambda suffix : self.deepseek.set_suffix(suffix),"已补全后缀", "后缀补全失败"], # input("请输入需要补全的后缀(默认为None):")
    # 上下文参数
    "#思维链": [lambda : self.deepseek.reasoning_content_output(), lambda : self.deepseek.reasoning_content,"思维链为空"],  # 会返回False或字符串
    "#清空对话历史": [lambda : self.deepseek.clear_dialog_history(),"已清空对话历史(人设除外)", "对话历史为空无需清空"],
    # 场景关键词自动调控参数
    "#代码": [lambda : self.deepseek.scene_switch("代码"),"已切换至代码场景","切换场景失败"],
    "#数学": [lambda : self.deepseek.scene_switch("代码"),"已切换至数学场景","切换场景失败"],
    "#数据": [lambda : self.deepseek.scene_switch("数据"),"已切换至数据场景","切换场景失败"],
    "#分析": [lambda : self.deepseek.scene_switch("分析"),"已切换至分析场景","切换场景失败"],
    "#对话": [lambda : self.deepseek.scene_switch("对话"),"已切换至对话场景","切换场景失败"],
    "#翻译": [lambda : self.deepseek.scene_switch("翻译"),"已切换至翻译场景","切换场景失败"],
    "#创作": [lambda : self.deepseek.scene_switch("创作"),"已切换至创作场景","切换场景失败"],
    "#写作": [lambda : self.deepseek.scene_switch("写作"),"已切换至写作场景","切换场景失败"],
    "#作诗": [lambda : self.deepseek.scene_switch("作诗"),"已切换至作诗场景","切换场景失败"],
    # 余额和token数查询
    "#余额": [True, lambda : self.deepseek.return_balance(), "无法查询"],
    "#token": [True, lambda : self.deepseek.return_token(), lambda : self.deepseek.return_balance(), "无法查询"]
        }

    @staticmethod
    def load_unlimited_list():
        """无限制指令列表"""
        return [
        # 帮助类指令
        "#帮助",
        "#指令查询",
        # 对话参数调节
        "#模型切换",
        "#V3模型",
        "#R1模型",
        "#评分",
        "#非流式",
        # FIM相关
        "#FIM对话",
        "#FIM补全开头",
        "#FIM完整输出",
        "#FIM补全后缀",
        # 上下文管理
        "#思维链",
        "#清空对话历史",
        # 场景关键词
        "#代码",
        "#数学",
        "#数据",
        "#分析",
        "#对话",
        "#翻译",
        "#创作",
        "#写作",
        "#作诗",
        # 查询类
        "#余额",
        "#token"
    ]

    @staticmethod
    def load_root_orders():
        """加载root权限的指令列表"""
        return ["#退出"]

if __name__ == '__main__':
    # jm_down_order("JM250745") # 赛马娘(小栗帽)
    # jm_down_order("#jm:422866") # 短片测试 #jm:422866
    print("额外功能正常")
