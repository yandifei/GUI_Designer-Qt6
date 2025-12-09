"""专门用于做日志记录处理
也方便直接调用
"""
# 系统库
import logging  # logs
import sys  # 系统库
from logging.handlers import RotatingFileHandler  # 日志大小轮转处理器
from types import TracebackType
from typing import Mapping, Optional, Type, Tuple

# 第三方库
import colorlog  # 颜色处理

# 记录器
log = logging.getLogger("爱丽丝QQ聊天AI.py")  # 创建记录器
log.setLevel(logging.DEBUG)  # 设置为最低级别记录所有调试信息

# 创建流式处理器（控制台输出）
console_handler = colorlog.StreamHandler(stream=sys.stderr)  # 使用colorlog库创建彩色控制台处理器
# console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 设置日志等级

# 创建文件处理器（日志文件写入。使用的是时间轮转处理器,每个文件1MB，保留3个备份）
try:  # 开发路径
    arisu_handler = RotatingFileHandler(
        filename="./logs/爱丽丝QQ聊天AI.log",
        encoding="utf8",
        mode="a",  # 追加写入
        maxBytes=1 * 1024 * 1024,  # 单文件最大 1MB 时轮转
        backupCount=2 # 最多保留2个历史文件
    )
except FileNotFoundError:
    try:  # 测试路径(UI包里测试)
        arisu_handler = RotatingFileHandler(
            filename="../logs/爱丽丝QQ聊天AI.log",
            encoding="utf8",
            mode="a",  # 追加写入
            maxBytes=1 * 1024 * 1024,  # 单文件最大 1MB 时轮转
            backupCount=2 # 最多保留2个历史文件
        )
    except FileNotFoundError:  # 测试路径(logs里测试)
        arisu_handler = RotatingFileHandler(
            filename="./logs/爱丽丝QQ聊天AI.log",
            encoding="utf8",
            mode="a",  # 追加写入
            maxBytes=1 * 1024 * 1024,  # 单文件最大 1MB 时轮转
            backupCount=2 # 最多保留2个历史文件
        )
arisu_handler.setLevel(logging.DEBUG)  # 设置日志等级为调试等级

# 创建控制台输出格式
# console_formatter = logging.Formatter(
#     fmt="%(asctime)s %(levelname)s:%(message)s",  # 时间，等级，消息
#     datefmt="%H:%M:%S"                  # 时分秒
# )
# 创建彩色日志格式
console_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s %(levelname)s:%(reset)s %(message_log_color)s%(message)s",
    datefmt="%H:%M:%S",  # 时间格式为时分秒
    reset=True,  # 开启重置颜色
    log_colors={
        'DEBUG': 'cyan',  # 灰色
        'INFO': 'green',  # 绿色
        'WARNING': 'yellow',  # 黄色
        'ERROR': 'bold_light_red',  # 红色(粗体)
        'CRITICAL': 'bold_light_red',  # 量红(粗体)
    },
    secondary_log_colors={
        'message': {
            'DEBUG': 'cyan',
            'INFO': 'light_green',
            'WARNING': 'light_yellow',
            'ERROR': 'red',
            'CRITICAL': 'red'
        }
    },
    style='%'
)
# 设置控制台处理器的文本的输出格式
console_handler.setFormatter(console_formatter)

# 创建文本文件的输出格式
fileFormatter = logging.Formatter(
    fmt="%(asctime)s:%(msecs)d %(levelname)s:%(message)s",  # 时间，等级，消息
    datefmt="%Y-%m-%d %H:%M:%S"  # 年月日，时分秒
)
# 设置文件处理的写入文本的输出格式（时间，等级名，消息）
arisu_handler.setFormatter(fileFormatter)

# 记录器添加处理器
log.addHandler(console_handler)  # 控制台
log.addHandler(arisu_handler)  # 文件
"""=======================================================全局异常捕获=================================================================="""
def exception_hook(exception_type, exception_value, exception_traceback):
    """捕获未处理的异常
    参数： exception_type ： 捕获的异常类型
    exception_value ： 异常的值
    exception_traceback ： 异常返回的值
    """
    # 忽略键盘中断的异常，比如pycharm的停止运行或控制台的Ctrl+C
    if issubclass(exception_type, KeyboardInterrupt):
        sys.__excepthook__(exception_type, exception_value, exception_traceback)
        return
    # error_msg = ''.join(traceback.format_exception(exception_type, exception_value, exception_traceback))
    # 记录未捕获的异常
    # critical(f"发生致命异常导致程序崩溃:")
    log.exception("发生致命异常导致程序崩溃:", exc_info=(exception_type, exception_value, exception_traceback))


# 启动函数
sys.excepthook = exception_hook  # 开启全局异常捕获
log.info("主程序开始(导包完成，全局异常捕获加载完成)")

"""=======================================================方法定义=================================================================="""
# 便捷函数（使用lambda减少代码量）
debug = lambda msg, *args, **kwargs: log.debug(msg, *args, **kwargs)
info = lambda msg, *args, **kwargs: log.info(msg, *args, **kwargs)
warning = lambda msg, *args, **kwargs: log.warning(msg, *args, **kwargs)
error = lambda msg, *args, **kwargs: log.error(msg, *args, **kwargs)
critical = lambda msg, *args, **kwargs: log.critical(msg, *args, **kwargs)



# exception需要特殊处理（默认包含堆栈信息）
def exception(
    msg: object,
    *args: object,
    exc_info: None | bool | Tuple[Type[BaseException] | BaseException | Optional[TracebackType]] |
              Tuple[None, None, None] | BaseException = True,
    stack_info: bool = False,
    stacklevel: int = 1,
    extra: Optional[Mapping[str, object]] = None
):
    """异常日志输出（自动附带堆栈信息）
    参数： msg ： 日志消息
    args ： 可变参数
    exc_info ： 异常信息参数
    stack_info ： 是否包含堆栈信息
    stacklevel ： 堆栈级别
    extra ： 额外信息
    """
    # 保持原始调用，颜色应由日志处理器控制
    log.exception(
        msg, *args,
        exc_info=exc_info,
        stack_info=stack_info,
        stacklevel=stacklevel,
        extra=extra
    )
# def exception(msg: object,*args: object):
#     """异常捕获日志输出（比致命错误日志输出强）"""
#     # 保持原始调用，颜色应由日志处理器控制
#     log.exception(msg, *args)

if __name__ == '__main__':
    debug("调试日志输出")
    info("运行正常日志输出")
    warning("警告日志输出")
    critical("致命错误日志输出")
    try:
        a = 1 / 0
    except Exception as e:
        exception("异常捕获日志输出:")
