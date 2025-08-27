"""界面启动图标"""
try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass
#系统自带的包
import sys
# 第三方库
from PyQt6.QtWidgets import QApplication    # 界面处理类
# 自己的库
from UI.ExtendedUI  import ArisuUI          # 导入开发好的UI类
from arisu_logger import info             # 导入日志方法
from UI.functions import uninstall_program  # 导入卸载程序

"""主进程UI加载"""
arisu_app = QApplication(sys.argv)  # 管理控制事件流和设置(sys.argv控制台接收参数)
arisu_ui = ArisuUI("爱丽丝", True, "resources/Arisu.ui")
arisu_ui.show()                 # 界面展示
info("UI界面加载完成")
"""UI退出和程序安全退出"""
# UI界面退出的代码(0为正常    退出，其他为 非正常退出)
exit_code = arisu_app.exec()
info("已关闭UI界面")
# 检查是否是卸载程序
if exit_code == -20213025: # 卸载的退出码
    info("检测到用户执行了删除操作，开始执行删除指令")
    uninstall_program()  # 启动卸载程序
# 安全退出程序
sys.exit(exit_code)