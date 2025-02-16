# 这个自定义的库是用来写用户反馈的，包括语音提示等等
# 用户反馈
pass
"""反馈思想（对反馈的内容做分类）
对不同方式的反馈做区分，这可能觉得很傻，没有必要，但是我觉的有必要
1. 字体打印到屏幕上和语音提示是不同的方式，如果一味使用print打印会有局限性，需要的语音的时候就完蛋了
2. 对反馈做区分，也能对日志级别有所了解，当然这个反馈也可以复写到不同日志等级里面去
"""
"""示例展示
打印用户在ui的选项（交互反馈）当前环境是否能使用脚本（系统反馈），任务开始（状态反馈），完成到那一步（进度反馈），
任务完成（状态反馈），发出声音提示任务完成（声音反馈），用户关闭程序（交互反馈）
"""


def interactive_feedback(feedback_content):
    """交互反馈
    在用户与程序交互时提供即时反馈（如点击按钮后的提示）。"""
    print(feedback_content)  # 默认直接打印，可以复写成反馈表

def sys_feedback(feedback_content):
    """系统反馈
    关于计算机硬件或软件状态的数据，而“反馈”或“显示”则是指将这些信息传达给用户的过程。（如系统类别，分辨率等）"""
    print(feedback_content)

def status_feedback(feedback_content):
    """状态反馈
    实时通知用户程序的当前状态（如“正在加载”、“已完成”等）。"""
    print(feedback_content)  # 默认直接打印，后期复写直接打印到UI上

def progress_feedback(feedback_content):
    """进度反馈
    告知用户当前任务的执行进度（如百分比、步骤等）。"""
    print(feedback_content)  # 默认直接打印，后期复写直接打印到UI上

def audio_feedback(feedback_content):
    """声音反馈
    描述系统通过声音向用户传达信息或状态更新的过程。（如蜂鸣声或对应的语音包）"""
    print(feedback_content)  # 默认直接打印，可以复写成语音

# def qq_feedback(self):
#     """这个暂时不写，先搞主体"""
#     pass

if __name__ == '__main__':
    interactive_feedback(1)
    sys_feedback(2)
    status_feedback(3)
    progress_feedback(4)
    audio_feedback(5)
