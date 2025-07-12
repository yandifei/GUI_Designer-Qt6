"""---------------------------------------------------导包和导库-----------------------------------------------------"""
# 内置库
import sys
import types
import configparser
import traceback    # 异常捕获
# 自己的库
from QQMessageMonitor import * # 导包
from deepseek_conversation_engine import DeepseekConversationEngine
"""--------------------------------------------------QQ聊天AI初始化-----------------------------------------------------"""
# 这个问题已经放到异常捕获里面解决了，这里也没有必要搞这个了，而且还会带来麻烦
# uiautomation.SetClipboardText("") # 设置剪切板内容为空避免出现问题(第一次粘贴可能导致大量的文本出现)
# 创建类对象来管理初始化和配置保存（没办法，内容太多了，这里仅仅时简单管理）
class InitSettings:
    def __init__(self):
        """初始化配置类"""
        self.qq_group_name = None
        self.user_name = None
        self.root = None    # 额外的超管
        self.init_role = None
        self.win_x = None   # 窗口x位置
        self.win_y = None   # 窗口y位置
        self.administrator_list = list() # 管理员列表(Q群群主或管理员)
        self.root_list = list() # 超管列表(自己AI账号和控制台添加的账号)
        self.super_password = ""   # 退出指令的密码(不能为空)
        self.order_limit = False  # 指令限制，去掉可能违规的指令（默认无）
        # 设置权限隔离标志,默认开启(防有心之人)[默认自己和自己添加额外添加的超管]
        self.permission_isolation_flag = False      # 不开启了，真防又防不住，又没人用
        """配置读取"""
        # 创建一个 INI 格式配置文件的解析器对象(严格区分大小写)
        self.config = configparser.ConfigParser(allow_no_value=False, strict=True)
        # 初次读入配置文件内容(指定编码格式是utf-8，不然会乱码(默认GBK))
        self.config.read("./UserSettings.ini", encoding="utf-8")
        self.print_notice()  # 输出声明
        self.loading_settings()     # 加载配置

    def loading_settings(self):
        """加载用户配置"""
        self.super_password = input("\033[91m请设置退出指令的密码:\033[0m")
        while self.super_password == "":
            self.super_password = input("\033[91m密码不能为空，请重新输入:\033[0m")
        # 检查配置存在标志(判断是否需要用户配置)
        if self.config["用户配置"].getboolean("configuration_exists_flag"):
            is_modify = input("\033[95m是否沿用上次的配置(直接回车为y)？(y/n):\033[0m")
            while is_modify not in ["y","n",""]:    # 如果字符不在这个列表就重输
                is_modify = input("\033[91m输入错误，请重新输入(y/n):\033[0m")
            if is_modify in {"y", ""}:      # 延续上一次的配置
                print("\033[92m---------------开始导入上次的配置----------------\033[0m")
                self.configure_read(True)
                print("\033[92m-------------------已完成配置导入-----------------\033[0m")
            else: # 录入新的配置
                self.configure_entry()  # 录入用户置并保存
        else:   # 这里else是因为怕有人进入ini改了东西把标志位改成了其他玩意
            self.configure_entry()  # 初次录入用户配置并保存

    def print_notice(self):
        """打印声明"""
        # 读取软件声明的键值
        print("\033[92m---------------------项目声明-----------------\033[0m")
        notice = "\n".join([self.config["软件声明"][declaration] for declaration in self.config["软件声明"]])
        print(f"\033[36m{notice}\033[0m")
        print("\033[92m-------------------开始配置初始化-----------------\033[0m")

    def configure_entry(self):
        """接收用户配置"""
        # 录入Q群名称
        self.qq_group_name = input("请输入监听的群聊名称(如果有群备注请填备注名):")
        self.config["用户配置"]["qq_group_name"] = self.qq_group_name  # 录入Q群名称
        # 录入机器人的名称
        self.user_name = input("请输入你的身份(你在Q群中的名称，优先填自己在Q群修改的名称):")
        self.root_list.append(self.user_name)  # 添加自己(机器人账号)为超管(类的属性)
        self.config["用户配置"]["user_name"] = self.user_name   # 配置文件录入自己(机器人账号)为超管
        # 录入额外的超管
        self.root = input("请输入超级管理员名称(机器人默认超管，不输入则不设置):")
        self.root_list.append(self.root)  # 添加额外的超管(类的属性)
        self.config["用户配置"]["root"] = self.root  # 录入超管进配置文件
        # 人设录入
        roles = [name.replace(".txt", "") for name in os.listdir("提示库/") if name.endswith(".txt")]
        roles = "、".join(roles)  # 组合字符串
        print(f"提示库人设:{roles}")
        self.init_role = input(f"请输入自动回复的人设(在提示库中)，直接回车即不设置任何人设:")
        self.config["用户配置"]["init_role"] = self.init_role   # 录入取初始人设
        if self.init_role == "": self.init_role = None  # 初始人设为空
        # 窗口位置录入
        class_win_xy = input("请输入QQ窗口窗口的位置(直接回车默认最左上角[-579,2、-579,582、1919,-579、1919,2、1919,582]):")
        self.config["用户配置"]["window_location"] = class_win_xy   # 录入取窗口位置
        class_win_xy = class_win_xy.replace("，", ",")  # 转换，字符
        if not class_win_xy:  # 输入为空
            self.win_x = self.win_y = None
        else:
            self.win_x, self.win_y = class_win_xy.split(",")
            self.win_x, self.win_y = int(self.win_x), int(self.win_y)
        # 指令限制录入
        print("\033[91m此程序有个致命的bug：别人可以通过修改自己的名称(修改成你的机器人账号的名称或添加的超管名称)获得超管权限或管理权限\033")
        print("\033[91m有心之人可以使用指令系统(修改人设指令，自定义人设等指令)使机器人发表违法言论(引流、带节奏、色情等)\033[0m")
        self.order_limit = input("\033[93m请输入是否开启指令限制，开启后会禁用掉危险的指令(直接回车为y)？(y/n):\033[0m")
        while self.order_limit not in ["y", "n", ""]:  # 如果字符不在这个列表就重输
            self.order_limit = input("\033[91m输入错误，请重新输入(y/n):\033[0m")
        if self.order_limit in {"y", ""}:   # 开启指令限制功能
            self.order_limit = True
            self.config["用户配置"]["order_limit"] = "True"
        else:
            self.order_limit = False    # 不开启指令限制功能
            self.config["用户配置"]["order_limit"] = "False"
        # 修改配置标志位为True
        self.config["用户配置"]["configuration_exists_flag"] = "True"  # 修改配置标志位(下一次就不用输了)
        with open("UserSettings.ini", "w", encoding="utf-8") as ini_file:  # 保存修改的配置
            self.config.write(ini_file)
        # # 再次读入配置文件内容(指定编码格式是utf-8，不然会乱码(默认GBK))
        # self.config.read("./UserSettings.ini", encoding="utf-8")

    def configure_read(self, out = False):
        """配置读取
        参数: out : 是否打印输入录入值，默认False
        """
        # 读取用户名
        if self.config["用户配置"]["user_name"] != "":
            self.user_name = self.config["用户配置"]["user_name"]
            self.root_list.append(self.user_name)   # 添加自己为超级管理员
            if out: print(f"\033[95m用户名:\033[96m{self.user_name}\033[0m")
        else:
            self.user_name = None
            print("\033[91m未录入Q群中的名称\033[0m")
        # 读Q群名
        if self.config["用户配置"]["qq_group_name"] != "":
            self.qq_group_name = self.config["用户配置"]["qq_group_name"]
            if out: print(f"\033[95mQ群名称:\033[96m{self.qq_group_name}\033[0m")
        else:
            self.qq_group_name = None
            print("\033[91m未设置QQ群的名称\033[0m")
        # 读超管来添加额外的超管
        if self.config["用户配置"]["root"] != "":
            self.root = self.config["用户配置"]["root"]
            self.root_list.append(self.root)   # 额外添加超级管理员
            if out: print(f"\033[95m当前超管:\033[96m{"、".join([name for name in self.root_list])}\033[0m")
        else:
            self.root = None
            if out: print(f"\033[95m超管为自己\033[0m")
        # 读取初始人设
        if self.config["用户配置"]["init_role"] != "":
            self.init_role = self.config["用户配置"]["init_role"]
            if out: print(f"\033[95m初始人设:\033[96m{self.init_role}\033[0m")
        else:
            self.init_role = None
            if out: print(f"\033[95m人设为空\033[0m")
        # 读取窗口位置
        if self.config["用户配置"]["window_location"] != "":
            class_win_xy = self.config["用户配置"]["window_location"].replace("，", ",") # 获取字符并把中文的逗号搞成英文的
            class_win_xy = class_win_xy.split(",")  # 获得分割后的字符
            self.win_x, self.win_y = int(class_win_xy[0]), int(class_win_xy[1])  # 把坐标字符串转为整型
            if out: print(f"\033[95m窗口左上角位置:\033[96m{self.win_x},{self.win_y}\033[0m")
        else:
            self.win_x, self.win_y = None, None
            if out: print(f"\033[95m窗口左上角位置:\033[96m最左上角\033[0m")
        # 读取是否开启指令限制
        if self.config["用户配置"].getboolean("order_limit"):
            self.order_limit = True     # 开启指令限制
            if out: print(f"\033[95m指令限制:\033[96m已开启\033[0m")
        else:
            self.order_limit = False    # 关闭指令限制
            if out: print(f"\033[95m指令限制:\033[96m已关闭\033[0m")

def exception_hook(all_excepts, value, traceback_obj):
    """捕获未处理的异常
    参数： all_excepts ： 所有的异常类型
    value ： 值
    traceback_obj ： 目标追踪
    """
    # 格式化异常信息
    error_msg = ''.join(traceback.format_exception(all_excepts, value, traceback_obj))
    print("\033[92m=============================以下为错误信息=============================\033[0m")
    print(f"\033[91m{error_msg}\033[0m")
    with open('error.log', 'w') as error_file:   # 写入错误信息
        error_file.write(f"发生错误：\n{error_msg}\n")
    # 退出程序
    input("\033[93m程序发生异常，优先尝试自行解决，如看不懂错误请把目录下的error.log文件内容给AI或发给作者(QQ邮箱：3058439878@qq.com)。按回车键关闭窗口\033[0m")
"""---------------------------------------------------关闭程序启动动画-----------------------------------------------------"""
try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass
"""----------------------------------------------------实例化对象------------------------------------------------------"""
sys.excepthook = exception_hook
init_setting = InitSettings()   # 实例化初始设置的类
chat_win1 = QQMessageMonitor(init_setting.qq_group_name, init_setting.user_name, 3)    # 会自动置顶和自动展示(最小化显示)
deepseek = DeepseekConversationEngine(init_setting.init_role)  # 实例化对象
# 初始化高级权限者列表(所有管理员包括超管理)
advanced_permissions_list = init_setting.root_list.copy()   # 默认添加超管(自己以及额外添加的成员)
advanced_permissions_list.append("自己") # 在发送者中将把自己发送的消息的发送者改为自己
"""--------------------------------------------------QQ窗口绑定处理----------------------------------------------------"""
chat_win1.move(init_setting.win_x, init_setting.win_y)          # 移动窗口
print(f"\033[92m数据存放路径:  \033[96m{chat_win1.message_data_txt}\033[0m")
print("\033[92m-------------------开启AI自动回复-----------------\033[0m")
for one_message in chat_win1.message_list:  # 打印初次绑定后监测的消息(这部分的消息不收录)
    print(one_message)
"""------------------------------------------------------快捷指令------------------------------------------------------"""
def open_permission_isolation():
    """开启权限隔离"""
    init_setting.administrator_list.extend(chat_win1.get_qq_group_administrator())      # 添加Q群群主和管理员指令权限
    init_setting.permission_isolation_flag = True    # 设置权限隔离标志为开启
    global advanced_permissions_list
    advanced_permissions_list = (set(init_setting.administrator_list) | set(advanced_permissions_list))    # 更新添加的管理员和超管
    # print(advanced_permissions_list)
    return True # 完成修改返回True
def close_permission_isolation():
    """关闭权限隔离"""
    init_setting.administrator_list =  init_setting.root_list    # 仅保留超管的高级权限
    global advanced_permissions_list
    advanced_permissions_list = init_setting.root_list  # 仅保留超管的高级权限
    init_setting.permission_isolation_flag = False    # 设置权限隔离标志为关闭
    return True # 完成修改返回True

# 无限制指令,放置不需要任何权限的指令(任何人都能用，即使开启了权限隔离)（初始化仅仅只是初始化对话引擎，不会初始化权限相关）
unlimited_command = ["#帮助", "#指令查询","#高级权限者","#所有管理员", "#开启权限隔离", "#开启关键词自动回复","#关闭关键词自动回复"
                     "#兼容", "#测试接口", "#初始化", "#模型切换", "#V3模型", "#R1模型", "#评分", "#最大token数",
                     "#温度", "#核采样","#FIM对话","#FIM补全开头","#FIM完整输出","#FIM补全后缀","#思维链","#清空对话历史",
                     "#代码", "#数学", "#数据", "#分析", "#对话""#翻译", "#创作", "#写作", "#作诗", "#余额", "#token"]
def help_notice():
    """帮助指令
    返回值：text
    """
    text = "\n".join([init_setting.config["软件声明"][declaration] for declaration in init_setting.config["软件声明"]]) + \
        f"\n\n如果要查看可使用的指令，请使用 #指令查询。注：普通成员可以开启权限隔离功能，但是开启后无权关闭"
    return text

# 用来放置参数(必须存在,需要用来判断是否需要参数)
args = None
# 函数映射表(使用lambda来匿名函数)，直接把指点放到环境变量外，防止每次加载的时候都是
function_map = {
    # QQ管理这类的专属指令
    "#帮助": [True, lambda : help_notice(), "发送失败"],
    "#指令查询": [True, lambda : "所有指令\n" + "\n".join(name for name in function_map.keys()), "查询失败"],
    "#高级权限者" : [True, lambda : f"高级权限者:\n{"\n".join([i for i in advanced_permissions_list])}", "无法查询"],
    "#开启权限隔离": [lambda : open_permission_isolation(), "已开启权限隔离功能(仅群主、管理员、超管能使用指令系统)", "开启权限隔离功能失败"],
    "#关闭权限隔离": [lambda : close_permission_isolation(), "已关闭权限隔离功能(所有都能使用指令系统)", "关闭权限隔离功能失败"],
    "#所有管理员": [True, lambda : f"{"\n".join(["主人:"+qq_administrator_name for qq_administrator_name in chat_win1.get_qq_group_administrator()])}","无法查询"],
    "#开启关键词自动回复": [lambda : setattr(chat_win1,"keyword_respond",True),"开启关键词自动回复","开启关键词自动回复"], # 这个返回None
    "#关闭关键词自动回复": [lambda : setattr(chat_win1,"keyword_respond",False),"关闭关键词自动回复","关闭关键词自动回复"], # 这个返回None
    # 特殊指令
    "#兼容": [lambda : deepseek.compatible_openai(),"已经切换至兼容OpenAI的接口","切换中途发生异常"],
    "#测试接口": [lambda : deepseek.use_beat(),"已切换至测试接口","切换中途发生异常"],
    "#初始化": [lambda : deepseek.reset(),"已格式化deepseek对话引擎","初始化中途发生异常"],  # 恢复最开始设置的参数（创建对象时的默认参数）
    # 对话参数调节指令
    "#模型切换": [lambda : deepseek.switch_model(True),lambda : "已切换至V3模型" if deepseek.model_choice == "deepseek-chat" else "已切换至R1模型", "切换中途发生异常"],
    "#V3模型": [lambda : deepseek.set_model("V3"),"已切换至V3模型", "切换中途发生异常"],
    "#R1模型": [lambda : deepseek.set_model("R1"),"已切换至R1模型", "切换中途发生异常"],
    "#评分": [lambda score=50 : deepseek.score_answer(score),"评分成功", "超出打分范围([0-100]分,默认50分)"],
    "#最大token数": [lambda max_tokens=4096 : deepseek.set_max_tokens(max_tokens),lambda : f"已修改最大token数为{deepseek.max_tokens}", "超出最大token数范围([1-8192]分,默认4096)"],
    "#输出格式": [lambda response_format : deepseek.set_response_format(response_format),lambda : f"已修改为{deepseek.response_format}格式", "格式有误，指定模型必须输出的格式为\"text\"或\"json\""],    # input("请输入指定输出格式(text或json,],默认text):")
    "#敏感词": [lambda stop : deepseek.set_stop(stop),lambda : f"添加敏感词 {args} 成功","添加失败"],    # input("设置敏感词(默认为None):")
    "#删除敏感词": [lambda stop: deepseek.del_stop(stop),"删除成功","敏感词不存在"],
    "#流式": [lambda : deepseek.set_stream(True),"已切换至流式输出","切换中途发生异常"],
    "#非流式": [lambda : deepseek.set_stream(),"已切换至流式输出", "切换中途发生异常"],
    "#开启请求统计": [lambda : deepseek.set_stream_options(True),"已开启请求统计", "必须先开启流式(stream)才能开启修改开启这个字段"],
    "#关闭请求统计": [lambda : deepseek.set_stream_options(),"已关闭请求统计", "关闭请求统计途中发生异常"],
    "#温度": [lambda temperature : deepseek.set_temperature(temperature),lambda : f"已修改温度为{deepseek.temperature}", "超出温度范围([0.0-2.0,]默认1.0)"],
    "#核采样": [lambda top_p : deepseek.set_top_p(top_p), lambda : f"已修改核采样为{deepseek.top_p}", "超出核采样范围([0.0-1.0]分,默认1.0)"],   # float(input("请输入核采样,],数值越小内容部分逻越严谨(0.0-1.0,],默认1.0):"))
    "#工具列表": [lambda : deepseek.set_tools(),"修改成功", "修改未成功"],  # input("请输入模型可能会调用的 tool 的列表(默认为None):")
    "#工具开关": [lambda : deepseek.switch_tool_choice(),"已开启工具调用", "已关闭工具调用"],
    "#开启对数概率输出": [lambda : deepseek.set_logprobs(True), "已开启对数概率输出", "开启对数概率失败"],
    "#关闭对数概率输出": [lambda : deepseek.set_logprobs, "已关闭对数概率输出", "关闭对数概率失败"],
    "#位置输出概率": [lambda top_logprobs : deepseek.set_top_logprobs(top_logprobs), lambda : f"已修改概率输出个数为{deepseek.top_logprobs}", "未开启对数概率输出或参数不在调用范围(0-20)"],  # int(input("请指定的每个输出位置返回输出概率top为几的token(0-20，默尔为None):"))
    # FIM对话参数
    "#FIM对话": [True, lambda : deepseek.fill_in_the_middle_ask(), "调用失败"],  # 使用FIM对话补全
    "#FIM补全开头": [lambda prompt : deepseek.set_prompt(prompt),"已补全开头", "补全开头失败"],
    "#FIM完整输出": [lambda : deepseek.set_echo(),"因为服务器那边不接受True，只接受False和None,所以这个功能无效", "因为服务器那边不接受True，只接受False和None,所以这个功能无效"],  # 这个参数就只有False和None了，改不了一点
    "#FIM对数概率输出": [lambda FIM_logprobs : deepseek.set_FIM_logprobs(FIM_logprobs),lambda : f"已制定输出中保留{deepseek.FIM_logprobs}个最可能输出token的对数概率", "参数不在调用范围[0-20]"],  # int(input("请输入需要多少个候选token数量输出对数概率(默认0):"))
    "#FIM补全后缀": [lambda suffix : deepseek.set_suffix(suffix),"已补全后缀", "后缀补全失败"], # input("请输入需要补全的后缀(默认为None):")
    # 上下文参数
    "#思维链": [lambda : deepseek.reasoning_content_output(), lambda : deepseek.reasoning_content,"思维链为空"],  # 会返回False或字符串
    "#对话轮次": [lambda dialog_round : deepseek.set_dialog_history(dialog_round), lambda : "已解除对话轮次限制，注意最大token数和高额消费" if deepseek.clear_flag == -1 else f"已设置对话轮次为{deepseek.clear_flag}轮", "无法设置对话轮次为负数"], # int(input("请输入最大对话轮数，超过自动删除(默认值为5):"))
    "#聊天记录": [lambda : deepseek.print_dialog_history(), lambda : "\n".join(deepseek.print_dialog_history()),"聊天记录为空"],
    "#清空对话历史": [lambda : deepseek.clear_dialog_history(),"已清空对话历史(人设除外)", "对话历史为空无需清空"],
    # 多人设管理
    "#人设切换": [lambda role_name : deepseek.role_switch(role_name),lambda : f"已切换人设为：{args}","提示库不存在该人设"],    # input("请输入切换的人设:")
    "#所有人设": [lambda : deepseek.role_list(),lambda : "提示库的所有人设:" + "、".join(deepseek.role_list()), "提示库中为空，不存在任何人设"],  # 人设做了处理
    "#人设查询": [lambda role_name : deepseek.select_role_content(role_name),lambda : deepseek.select_role_content(args), "不存在该人设，无法进行打印"],    # input("请输入要查询的人设:")
    "#当前人设": [lambda : deepseek.print_role_content(),lambda : f"当前人设:{deepseek.role}","当前人设为空"],
    "#人设自定": [lambda role_txt : deepseek.set_role(role_txt),"自定义人设成功", "自定义人设失败"],# input("请输入人设内容:")
    "#删除人设": [lambda : deepseek.remove_role(),"成功删除人设", "未设置人设，不需要进行删除"],
    # 场景关键词自动调控参数
    "#代码": [lambda : deepseek.scene_switch("代码"),"已切换至代码场景","切换场景失败"],
    "#数学": [lambda : deepseek.scene_switch("代码"),"已切换至数学场景","切换场景失败"],
    "#数据": [lambda : deepseek.scene_switch("数据"),"已切换至数据场景","切换场景失败"],
    "#分析": [lambda : deepseek.scene_switch("分析"),"已切换至分析场景","切换场景失败"],
    "#对话": [lambda : deepseek.scene_switch("对话"),"已切换至对话场景","切换场景失败"],
    "#翻译": [lambda : deepseek.scene_switch("翻译"),"已切换至翻译场景","切换场景失败"],
    "#创作": [lambda : deepseek.scene_switch("创作"),"已切换至创作场景","切换场景失败"],
    "#写作": [lambda : deepseek.scene_switch("写作"),"已切换至写作场景","切换场景失败"],
    "#作诗": [lambda : deepseek.scene_switch("作诗"),"已切换至作诗场景","切换场景失败"],
    # 余额和token数查询
    "#余额": [True, lambda : deepseek.return_balance(), "无法查询"],
    "#token": [True, lambda : deepseek.return_token(), lambda : deepseek.return_balance(), "无法查询"]
}
def quick_order(order: str):
    """快捷指令（调用此方法后自动分割后通过关键字快速找到其他方法）
    参数： order ： 收到的消息(#R1 模型)
    返回值：如果指令存在则执行对应的函数后返回True，如果指令不存在返回False
    """
    global args #使用外面的全局变量
    args = None     # 清空上一次指令的参数
    def execute_function(true_false_result):
        """是否执行返回值的函数
        参数 : true_false_result  ；执行结果
        """
        if true_false_result:  # 执行结果有效果
            if function_check(function_map[order][1]):  # 真值是一个函数
                chat_win1.send_message(function_map[order][1]())  # 执行真值的函数并发送
            else:
                chat_win1.send_message(function_map[order][1])  # 直接发送真值
        else:
            if function_check(function_map[order][2]):  # 假值是一个函数
                chat_win1.send_message(function_map[order][2]())  # 执行假值的函数并发送
            else:
                chat_win1.send_message(function_map[order][2])  # 直接发送假值

    function_check = lambda def_function: True if isinstance(def_function, (types.LambdaType,types.FunctionType,types.MethodType)) else False   # 检查是否为匿名函数
    # 检查指令是否包含参数并做处理
    if ":" in order:  # 如何指令中存在:代表的是参数
        if not order.split(":",1)[1]:     # 参数为空
            chat_win1.send_message("参数为空")  # 有:却不填
            return False
        order, args = order.split(":",1)[0], order.split(":",1)[1]  # 分割指令和参数
    # 检查指令是否在函数映射字典中
    if order not in function_map:   # 指令不在字典里面
        chat_win1.send_message("不存在该指令")
        print("\033[93m接收到了不存在的指令\033[0m")
        return False  # 没有这个指令
    else:
        if function_check(function_map[order][0]) and args is None:   # 是一个无参函数
            # print("\033[92m无参函数执行了\033[0m")
            try:    # 假设没有:却必须要填入参数没有填
                result = function_map[order][0]()    # 执行函数并拿到返回结果
                execute_function(result)
            except TypeError:
                if function_check(function_map[order][2]):  # 假值是一个函数
                    chat_win1.send_message("请在指令中附带必要参数:\n" + function_map[order][2]())  # 执行假值的函数并发送
                else:
                    chat_win1.send_message("请在指令中附带必要参数:\n" + function_map[order][2])  # 直接发送假值
        elif function_check(function_map[order][0]) and args is not None:    # 是有参函数
            # print("\033[92m有参函数执行了\033[0m")
            result = function_map[order][0](args)  # 传入参数并执行函数并拿到返回结果
            execute_function(result)
        else:   # 不是一个函数(可能是None、True、False)
            # print("\033[92m不是函数执行了\033[0m")
            result = function_map[order][0]     # 传入的不是一个函数不执行，仅仅拿到值
            execute_function(result)
    return True  # 存在指令且执行即返回True

def exit_qq_auto_reply(root_name, message):
    """判断是否退出QQ自动回复
    参数 ： administrator_name ： 超级管理员的名字
    先判断是否为超管，然后是判断密码
    """
    # 判断是否为超管
    if root_name not in init_setting.root_list and root_name != "自己":
        print("\033[31m此为高级操作，你无权执行该指令\033[0m")
        chat_win1.send_message("此为高级操作，你无权执行该指令")
        return False
    # 检查是否附带密码
    elif ":" not in message or not message.split(":", 1)[1]:    # 没带参数或没附带密码
        chat_win1.send_message("请附带密码参数以及密码不能为空")
        return False
    # 密码必须正确且是超管
    elif message.split(":", 1)[1] == init_setting.super_password:
        print("\033[31m已停止QQ监听回复和退出deepseek对话引擎\033[0m")
        chat_win1.send_message("已停止QQ自动回复\n已退出deepseek对话引擎")
        sys.exit()  # 优雅退出程序
    else:
        print("\033[31m退出指令异常，请重试\033[0m")
        chat_win1.send_message("退出指令异常，请重试")
    return True

"""-------------------------------------------------QQ消息回复处理-----------------------------------------------------"""
# try:
while True:
    # sleep(0.1)  # 每0.1秒监测一次变化(去掉监控时间)
    chat_win1.show_win()    # 展示窗口
    chat_win1.top_win()     # 置顶开窗口
    chat_win1.move(init_setting.win_x, init_setting.win_y)  # 移动窗口
    chat_win1.keep_size()    # 保持窗口大小
    chat_win1.monitor_message() # 始监控
    """消息处理"""
    if len(chat_win1.message_processing_queues) > 0:    # 队列不为空，进行队列处理
        # 这里是发送者的名字，我接收它的名字
        sender = chat_win1.message_processing_queues[0]["发送者"]
        # 我接受的消息（这里的发送消息指的是对方的发送消息)
        accept_message = chat_win1.message_processing_queues[0]["发送消息"]
        accept_message = accept_message.replace(f"@{chat_win1.monitor_name} ", "")   # 去除（@自己的名字 ）这个部分
        if accept_message == "": accept_message = " "    # 确保消息体不为空
        # 对方的消息发送时间
        accept_time = chat_win1.message_processing_queues[0]["发送时间"]
        """===============快捷指令处理==========="""
        if "#" == accept_message[0]:   # 检测到指令的消息
            if accept_message in unlimited_command:
                quick_order(accept_message)  # 把无限制指令带进入分析9+-
                print(f"\033[94m已完成“{sender}”对无限制指令的处理\033[0m")
                chat_win1.message_processing_queues.pop(0)  # 清理回应的消息(出队)[必须放到最外面]
            # 检查是否有“退出”消息且是管理员使用了指令系统
            elif "#退出" in accept_message and (sender == init_setting.root or sender == "自己"):  # 消息中存在退出指令(这里2次判断身份)
                exit_qq_auto_reply(sender,accept_message)  # 检查发送者的身份是否为管理员(内置优雅退出)
                chat_win1.message_processing_queues.pop(0)  # 清理回应的消息(出队)[必须放到最外面]
            # 开启权限隔离功能且非高级管理者使用了指令系统
            elif init_setting.permission_isolation_flag and sender not in advanced_permissions_list:    # 如果发送者在高级权限就不执行以下的指令
                print(advanced_permissions_list)
                print(f"\033[94m接收了一条高级权限人员的指令，不执行该指令\033[0m")
                chat_win1.send_message("权限不足，如要执行请联系管理员或超管")
                chat_win1.message_processing_queues.pop(0)  # 清理回应的消息(出队)[必须放到最外面]
                print(f"发送者：{sender}")
                continue    # 跳过此次循环，不执行分割指令执行指令的操作
            elif init_setting.order_limit:  # 开启了指令限制
                chat_win1.send_message("不存在该指令或此为限制指令，请让超管开启")
                print(f"\033不存在该指令或此为限制指令，请让超管开启\033[0m")
                chat_win1.message_processing_queues.pop(0)  # 清理回应的消息(出队)[必须放到最外面]
            # 没有开启指令限制
            elif not init_setting.order_limit:
                quick_order(accept_message)  # 把指令带进入分析
                print(f"\033[94m已完成“{sender}”的指令\033[0m")
                chat_win1.message_processing_queues.pop(0)  # 清理回应的消息(出队)[必须放到最外面]
        else:       # 非退出指令操作
            reply = deepseek.ask(f"{sender}:{accept_message}，当前时间:{datetime.now()}",False)  # 发出请求并回应(这里不打印到屏幕上)
            print(f"\033[96m{reply}\033[0m")    # 打印回应字体(青色)
            if sender == "系统":      # 如果是系统发送就不@了
                chat_win1.send_message(reply)  # 直接把回应发送到qq
            else:
                chat_win1.send_message(f"@{sender} " + reply)   # @人并把回应发送到qq
            deepseek.dialog_history_manage()    # 自动删除久远的对话历史
            chat_win1.message_processing_queues.pop(0)  # 清理回应的消息(出队)
            print(f"\033[94m已完成“{sender}”的消息处理\033[0m")