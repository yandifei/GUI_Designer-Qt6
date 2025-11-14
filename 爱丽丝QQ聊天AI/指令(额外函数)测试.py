from time import sleep

from qq_message_monitor import QQMessageMonitor
from deepseek_conversation_engine import DeepseekConversationEngine
from UI.arisu_qq_chat_ai_core import ArisuQQChatAICore
from tools_manage.tools_register import tools_register

arisu = QQMessageMonitor("群聊", "鸣潮想睡觉","雁低飞",4)
# arisu = QQMessageMonitor("群聊", "鸣潮自动刷声骸","雁低飞",4)

# AI函数回调注册，必须先有爱丽丝
tools_register(arisu)  # 爱丽丝作为对象传递进去然后注册函数

# deepseek消息回复(工具必须要先被注册后才创建这个对象)
deepseek = DeepseekConversationEngine("爱丽丝Pro")
# 外部函数(传入需要的对象)
ef = ArisuQQChatAICore(deepseek, arisu,"雁低飞","1","0,0","False")

# qq消息监听者

# 外部函数(传入需要的对象)-727,-727
# ef.arisu.move() # 窗口移动到左上角

# 保持窗口(显示、位置、大小)，设置10秒进行一次保持
ef.thread_keep_win(10)
print(f"窗口位置:{ef.qq_group_x, ef.qq_group_y}\t保持原始窗口的刷新时间:{10}秒/刷")

"""核心循环逻辑"""
while True and ef.running:  # 使用变量来确保是否执行和退出
    """监听窗口控制"""
    # 默认一秒监听一次窗口，防止CUP占用过高
    sleep(1)
    # 对新消息进行监控
    if text := arisu.monitor_message():  # 对新消息进行监控
        print(text)
    """消息处理"""
    if len(arisu.message_processing_queues) > 0:  # 消息队列不为空，进行队列处理
        reply = ef.split_respond_msg()  # 解析需要回应的消息
        arisu.message_processing_queues.pop(0)  # 清理回应的消息(出队)[必须在split_respond_msg之后]
        """开始消息处理逻辑（不是聊天就是指令）"""
        # 非指令
        if not reply[3]:
            """聊天回复"""
            # 如果发送者是 自己这就就改名（@自己），因为回复时会进行@导致无限循环的发生
            if ef.arisu.monitor_name == reply[0]:
                reply[0] = "自己"
            """关键词匹配规则回复"""
            if arisu.output_text == "图片":  # 满足图片标志位
                arisu.ctrl_v()  # Ctrl+V粘贴并后台点击发送
            else:
                """AI回复""" # True是我手动打开的
                reply_msg = deepseek.ask(f"{reply[0]}:{reply[1]}", False)  # 发出请求并回应(这里不重复打印到屏幕上)
                # @发送者 回复的消息（系统消息不@
                arisu.send_message(f"@{reply[0]} {reply_msg}" if reply[0] != "系统" else f"{reply_msg}")
        # 接收到了指令（检测指令是否存在）
        elif ef.is_order(reply[1]):  # 指令库里面检索指令(顺序不能反，因为指令可能带有参数)
            """指令操作"""
            # 分割指令和参数
            order, args = ef.split_order_args(reply[1])
            """鉴权是最大的文体，自己调用自己的鉴权"""
            # 是否有权限调度指令(包括root和非root的指令)
            if ef.check_permission(order, reply[0]):  # 传入指令和发送者
                # 传入指令执行后拿到返回结果并发送(@发送者 执行结果)
                # 如果发送者是自己就改名（@自己），因为回复时会进行@时会导致无限循环的发生
                arisu.send_message(f"@{reply[0] if ef.arisu.monitor_name != reply[0] else "自己"
                } {ef.execute_order(order, args)}")
            else:
                # 无权操作后的警告
                # 如果发送者是自己就改名（@自己），因为回复时会进行@时会导致无限循环的发生
                arisu.send_message(f"@{reply[0] if ef.arisu.monitor_name != reply[0] else "自己"
                } {"雑魚权限？真の杂鱼~🐟呢"}")  # 传入指令执行后拿到返回结果并发送
        else:
            """使用了不存在的指令(不是聊天也无法调用指令库的指令)"""
            # print("接收到了一条不存在的指令(不是聊天也没有在指令库中找到指令)")
            arisu.send_message(f"@{reply[0]} 不存在该指令")
    else:
        pass  # print("出现新消息，这里不进行打印，因为监视方法已经打印了")

# if __name__ == '__main__':
#