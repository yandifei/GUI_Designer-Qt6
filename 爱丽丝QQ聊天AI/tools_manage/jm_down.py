"""jm_down.py
禁漫天堂本子下载
"""
# 内置库
import os
import shutil
from time import sleep
# 第三方库
from jmcomic import download_album, jm_exception, create_option_by_file

# 自己的库
from tools_manage.base_tool import BaseTool
from qq_message_monitor import QQMessageMonitor

class JmDown(BaseTool):
    def __init__(self, qq_message_monitor: QQMessageMonitor):
        # QQ消息监控者
        self.qq_message_monitor = qq_message_monitor
        self.name = "jm_down"
        self.description = "通过id从禁漫天堂(俗称jm或JM)下载本子/专辑/PDF"
        self.parameters = {
            "type": "object",
            "properties": {
                "jm_album_id": {
                    "type": "string",
                    "description": "本子的id(如jm123456789即id为123456789)"
                }
            },
            "required": ["jm_album_id"]
        }
        super().__init__(self.name, self.description, self.parameters)

    def execute(self, **kwargs) -> str:
        # 从 kwargs 字典中获取 'jm_album_id' 参数的值
        jm_album_id = kwargs.get('jm_album_id')
        # 检查参数有效性
        if not jm_album_id or not isinstance(jm_album_id, str):
            return "错误：请提供字符串的jm_album_id参数。"
        try:
            # 清理残留的资源(把整个缓存目录删除)和目录还原(目录创建回去)
            shutil.rmtree("./logs/发送缓存")
            os.mkdir("./logs/发送缓存")
            shutil.rmtree("./logs/下载缓存")
            os.mkdir("./logs/下载缓存")
        except FileNotFoundError:
            return "目录不存在，无需删除"
        except (PermissionError, FileExistsError):
            # 满载第二次请求是PermissionError(shutil.rmtree)，带三次是FileExistsError(os.mkdir)
            return "请等待上一份的jm发送完再使用该指令(我不是服务器，垃圾CUP没法满足同时下载多个文件)，如您不能见谅请把您的CPU借我用用！"

        # 使用option对象来下载本子
        down_error = ""   # 下载错误信息
        try:
            # 读取jm的配置
            option = create_option_by_file("./用户设置/option.yml")
            download_album(jm_album_id, option)
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
        self.qq_message_monitor.copy_file(absolute_path)
        # 调用文件发送
        self.qq_message_monitor.paste_send_file()
        # 等待1秒的点击发送完毕
        sleep(1)
        return down_error if down_error else "本子已发送，未看到可能是文件太大了还在上传"

if __name__ == '__main__':
    # jm_down_order("JM250745") # 赛马娘(小栗帽)
    # jm_down_order("#jm:422866") # 短片测试 #jm:422866
    print("额外功能正常")
