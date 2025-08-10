"""非UI功能实现
前后端分离，ExtendUI.py从这里导入非UI的功能函数
"""
# 系统库
import os   # 系统库
import re   # 正则库
import subprocess
import sys  # 系统库

# 第三方库
from PyQt6.QtCore import QObject, pyqtSignal
# 自己的库
from arisu_logger import info, exception                     # 导入日志方法


class InputRedirection(QObject):
    """输如重定向"""
    input_text = pyqtSignal(str)  # 打造输出信号(必须放最高层级)

    def __init__(self, extender_ui):
        super().__init__()
        self.ArisuUI = extender_ui

    def readline(self, text):
        text = self.ArisuUI.ConsoleWidget.document().lastBlock().text()
        return text

class OutputRedirection(QObject):
    """输入重定向"""
    text_print = pyqtSignal(str)   # 打造输出信号(必须放最高层级)
        # console_handler.stream = self   # 输出重定向为自己

    def __init__(self):
        super().__init__()
        # 预编译高效正则表达式（匹配所有 ANSI 转义序列）
        self.ansi_escape = re.compile(r'\x1b\[[\d;]*m')
        # 颜色映射(ANSI 颜色到 HTML 颜色的映射)
        self.color_map = {
            '30': 'black', '31': 'red',
            '32': 'green', '33': 'yellow',
            '34': 'blue', '35': 'magenta',
            '36': 'cyan', '37': 'white',
            '90': 'darkGray', '91': 'lightRed',
            '92': 'lightGreen', '93': 'lightYellow',
            '94': 'lightBlue', '95': 'lightMagenta',
            '96': 'lightCyan', '97': 'white',
            '40': 'black', '41': 'red',
            '42': 'green', '43': 'yellow',
            '44': 'blue', '45': 'magenta',
            '46': 'cyan', '47': 'white'
        }
        # 样式映射
        self.style_map = {
            '0': '</span>',  # 重置
            '1': 'font-weight:bold;',  # 粗体
            '3': 'font-style:italic;',  # 斜体
            '4': 'text-decoration:underline;'  # 下划线
        }

    def write(self, text):
        # self.text_print.emit(text)
        # self.text_print.emit(self.remove_ansi_escape(text))   # 去除ANSI转义序列
        self.text_print.emit(self.ansi_to_my_color_text(text))            # 自个写的
        # self.text_print.emit(self.convert_ansi_to_html(text)) # 全AI写的

    def remove_ansi_escape(self, text):
        """移除ANSI转义序列
        text ： 需要转换的文本
        """
        return self.ansi_escape.sub('', text)

    def ansi_to_my_color_text(self, text):
        """去掉ANSI转义序列和进行颜色转换
        text ： 需要转换的文本
        1.正常的print为绿色（不用在意错误输出流，因为日志的错误已经捕获了）
        2.去掉ANSI转义序列进行转换html
        """
        # 去掉ANSI转义序列(WARNING、ERROR颜色都是从pycharm里面扒的)
        text = self.remove_ansi_escape(text)
        if "DEBUG" in text:
            return f"<font color='cyan'>{text}</font>"
        elif "INFO" in text:
            return f"<font color='green'>{text}</font>"
        elif "WARNING" in text:
            return f"<font color='#E5BF00'>{text}</font>"
        elif "ERROR" in text:
            return f"<font color='#F75464'>{text}</font>"
        elif "CRITICAL" in text:
            return f"<font color='red'>{text}</font>"
        # 过滤掉print()的第二次write("\n")
        elif text == "\n":
            return ""
        # 什么修饰都没有（print函数的输出）
        return f"<font color='grey'>{text}</font>"

    def convert_ansi_to_html(self,text):
        """将ANSI转义序列转换为HTML标签
        text ： 需要转换的文本
        """
        html_output = ""
        i = 0
        while i < len(text):
            if text[i] == '\x1b':  # 找到ESC字符
                # 检查是否是CSI序列
                if i + 1 < len(text) and text[i + 1] == '[':
                    seq_end = i + 2
                    # 找到序列结束位置
                    while seq_end < len(text) and not text[seq_end].isalpha():
                        seq_end += 1

                    if seq_end < len(text):
                        seq = text[i + 2:seq_end]
                        codes = seq.split(';')

                        # 处理样式代码
                        styles = []
                        for code in codes:
                            if code in self.style_map:
                                if code == '0':  # 重置
                                    styles = []
                                    self.current_style = ""
                                else:
                                    styles.append(self.style_map[code])

                            # 处理颜色代码
                            elif code in self.color_map:
                                if int(code) < 40:  # 前景色
                                    styles.append(f"color:{self.color_map[code]};")
                                else:  # 背景色
                                    styles.append(f"background-color:{self.color_map[code]};")

                        # 更新当前样式
                        if styles:
                            self.current_style = ''.join(styles)
                            html_output += f'<span style="{self.current_style}">'

                        # 跳过已处理的序列
                        i = seq_end
            else:
                # 转义特殊HTML字符
                char = text[i]
                if char == '<':
                    html_output += '&lt;'
                elif char == '>':
                    html_output += '&gt;'
                elif char == '&':
                    html_output += '&amp;'
                elif char == '\n':
                    html_output += '<br/>'
                elif char == ' ':
                    html_output += '&nbsp;'
                else:
                    html_output += char

            i += 1

        return html_output

def clear_temp():
    """删除残留在temp文件的MP4动态壁纸文件
    返回值：如果成功删除所有找到的缓存文件就返回True
    否则返回False（可能文件被正在使用或被添加了只读无法删除的权限等）
    """
    # 通过环境变量获取Windows临时文件夹路径
    temp_directory = os.environ.get("TEMP") or os.environ.get("TMP")

    # 构建匹配规则(python.6个字母.mp4),re.I为边界控制，使用后能从4.8ms变为2.9ms
    match_rule = re.compile(r"^python\.[a-zA-Z]{6}\.mp4$",re.I)

    # 遍历temp文件夹的所有符合匹配规则的文件，把符合的文件名构造成列表
    delete_files = [file_name for file_name in os.listdir(path=temp_directory) if re.search(match_rule, file_name)]

    flag = True # 成功卸载所有泄露文件的标志位
    # 开始删除泄露的文件
    for file_name in delete_files:  # 遍历需要删除的文件名
        try:
            # 文件绝对路径拼接后进行删除
            os.remove(os.path.join(temp_directory, file_name))
            info(f"成功删除意外溢出的文件:{file_name}")
        except PermissionError:
            # exception("文件正在被使用，以下是错误信息:")
            pass
        except(OSError,FileNotFoundError):
            exception("缓存文件(动态壁纸MP4文件)删除失败，以下是错误信息:")
    return True if flag else False


def uninstall_program():
    """卸载程序"""
    # 获取当前可执行文件路径（不用担心用户把软件的名改了）
    exe_path = os.path.abspath(sys.argv[0])
    # 当前目录路径（当前软件文件夹路径）
    directory_path = os.getcwd()
    # 通过环境变量获取Windows临时文件夹路径
    temp_directory = os.environ.get("TEMP") or os.environ.get("TMP")
    # 构建卸载文件bat的路径（放到temp目录中）
    uninstall_bat_path = os.path.join(temp_directory, f"爱丽丝QQ聊天AI{os.getpid()}.bat")
    # 卸载软件的代码
    uninstall_code = f"""
@echo off
ping -n 2 127.0.0.1
setlocal enabledelayedexpansion
set max_wait=30
set wait_count=0
:check_process
set process_name="爱丽丝QQ聊天Al.exe"
:check_process
tasklist /fi "imagename eq %process_name%" | findstr /i "%process_name%"
if %errorlevel% equ 0 (
    if %wait_count% geq %max_wait% (
        taskkill /f /im "%process_name%"
        exit /b 1
    ) else (
        ping -n 2 127.0.0.1
        set /a wait_count+=1
        goto :check_process
    )
)
rd /s /q {os.path.join(directory_path,"packages")}
rd /s /q {os.path.join(directory_path,"logs")}
rd /s /q {os.path.join(directory_path,"resources")}
rd /s /q {os.path.join(directory_path,"用户设置")}
rd /s /q {os.path.join(directory_path,"文档")}
del /f /q {exe_path}
pause
del %0
    """
    # 把删除代码写入文件里面去
    with open(uninstall_bat_path, "w", encoding="ANSI") as f:
        f.write(uninstall_code)

    # 启动批处理文件进行删除
    subprocess.Popen(
        [uninstall_bat_path],
        shell=True,                                 # 将通过系统的 shell 程序执行，而不是直接执行
        stdin=subprocess.DEVNULL,                   # 输入重定向为空
        stdout=subprocess.DEVNULL,                  # 标准输出重定向为空
        stderr=subprocess.DEVNULL,                  # 错误出重定向为空
        creationflags=subprocess.CREATE_NO_WINDOW   # 不创建可见窗口（后台运行）
    )
    info(uninstall_bat_path)
    # 启动删除文件
    # os.startfile(uninstall_bat_path)


if __name__ == '__main__':
    clear_temp()