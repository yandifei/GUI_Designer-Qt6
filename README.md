<div align="center">
  <h1 align="center">
    <img src="./展示项目的图片/爱丽丝.png" width="200"/>
    <br/>
    ArisuQQChatAI · 爱丽丝QQ聊天AI
  </h1> 
</div>

<br/>

<div align="center">
  <a href=https://www.microsoft.com/zh-cn/software-download/windows11><img alt="使用平台" src="https://img.shields.io/badge/platform-Windows11-blue?style=flat-square&color=00ffff"/></a>
  <a href=https://github.com/yandifei/ArisuQQChatAI/releases><img alt="最新版徽章" src="https://img.shields.io/github/release/yandifei/ArisuQQChatAI?include_prereleases&style=flat-square&color=4141dc"/></a>
  <a href=https://github.com/yandifei/ArisuQQChatAI/releases><img alt="总下载次数" src="https://img.shields.io/github/downloads/yandifei/ArisuQQChatAI/total?style=flat-square&color=00ffff" /></a>
</div>

<br/>

<div align="center">
  喜欢的话，就给爱丽丝个<a href=https://github.com/yandifei/ArisuQQChatAI>✨Star✨</a>吧！ (ﾉ>ω<)ﾉ❤️<img alt="Total Downloads" src="./爱丽丝QQ聊天AI/resources/爱丽丝表情包/非女仆/14.png" width="50"/>
</div>


## 功能介绍

- **AI自动回复**：
  - 使用deepseek的api自动回复
  - 结合指令系统对回答进行优化
  - 可**自定义人设**和上下文对话
  - 通过工具(插件)实现**多模态**，如：联网搜索某个关键词发送指定量的图片
  - 其余功能可以看：[爱丽丝QQ聊天AI.pdf](爱丽丝QQ聊天AI/文档/爱丽丝QQ聊天AI.md)或[DeepseekConversationEngine](https://github.com/yandifei/DeepseekConversationEngine)
- **自定回复策略**：
  - 关键词自动回复
  - 过滤回复指定发送者
  - 指定发送者发出消息就进行回复
  - 指定发送者及特定语句自动回复
- **权限系统**：
  - 需要承认的是权限系统存在设计缺陷(天然的)：权限可被复制。(有解决方案，但价值和意义太低了)
  - 通过权限分级可以避免某些“危险指令”导致QQ封号(如：从禁漫天堂下本子发到Q群中或发P站排行r18的图)
- **指令系统**：
  - AI无法完成的操作(调整AI的回复策略、发"美"图、运行时间和中控截图等等)
  - 后续有功能再加(文件处理、电脑状态监控等)
- **工具(插件)系统**
  - 通过插件实现多模态
  - 如：时间查询，具体到农历和国际节日等等
  - 插件工具实现了LLM的外部感知和操作执行，一个真正能干活的Agent
- **异常处理与日志**：
  - 强大的纠错机制(全局异常捕获和线程池自动重启线程)
  - 消息文本记录(撤回前监测到的消息会被记录到txt中)
  - 日志自动管理(文件进行日志轮替及详细捕获异常)

## 界面示意
<div style="display: flex; flex-direction: column; align-items: center; gap: 3px;">
  <div style="display: flex; justify-content: center; gap: 3px;">
    <img alt="主页" style="width: 400px; height: auto; " src="./展示项目的图片/主页.png"/>
    <img alt="状态监测" style="width: 400px; height: auto;" src="./展示项目的图片/状态监测.png"/>
  </div>

  <div style="display: flex; justify-content: center; gap: 3px;">
    <img alt="Q群绑定" style="width: 400px; height: auto;" src="./展示项目的图片/Q群绑定.png"/>
    <img alt="键盘快捷键" style="width: 400px; height: auto;" src="./展示项目的图片/键盘快捷键.png"/>
  </div>
  
  <div style="display: flex; justify-content: center; gap: 3px;">
    <img alt="问题链接" style="width: 400px; height: auto;" src="./展示项目的图片/问题链接.png"/>
    <img alt="用户设置" style="width: 400px; height: auto;" src="./展示项目的图片/用户设置.png"/>
  </div>

  <div style="display: flex; justify-content: center; gap: 3px;">
    <img alt="状态监测(最大化)" style="width: 400px; height: auto;" src="./展示项目的图片/状态监测(最大化).png"/>
    <img alt="日志监控(最大化)" style="width: 400px; height: auto;" src="./展示项目的图片/日志监控(最大化).png"/>
  </div>
</div>

## 安装使用
- 下载地址：[⚡Github下载⚡](https://github.com/yandifei/ArisuQQChatAI/releases)
- 直接解压即后打开“爱丽丝QQ聊天AI.exe”
- 确保你有deepseek api的密钥和这个密钥有钱
- 设置窗口录入deepseek api密钥并填写好绑定QQ群的参数
- 打开并登陆QQ，设置中在点击“超级调色盘”把主题选择为“极简白”
- 打开需要自动回复的Q群窗口，点击开启自
- 动回复按钮或一键开启按钮即可

## 项目运行
- 小白不用看这里。开发者用于异常崩溃输出和日志记录查询
- 也可以在 `爱丽丝QQ聊天AI` 文件夹中用pycharm 中打开项目运行`爱丽丝QQ聊天AI.py`
```git
# 1.克隆项目
git clone https://github.com/yandifei/ArisuQQChatAI.git

# 2.进入项目目录的开发目录（目录名需与克隆结果一致）
cd ArisuQQChatAI/爱丽丝QQ聊天AI/

# 3. [可选，强烈推荐] 创建虚拟环境
conda create -n Arisu python=3.13.9

# 激活虚拟环境(Anaconda或Miniconda)
conda activate Arisu

# 4.安装依赖(强烈建议使用虚拟环境)
pip install -r requirements.txt

# 5.启动项目(cmd使用以下指令，pycharm直接运行)
python 爱丽丝QQ聊天AI/爱丽丝QQ聊天AI.py
```

## 注意事项
- 禁止倒卖！禁止倒卖！禁止倒卖！！！
- 更新就直接覆盖安装（或者直接把原来的删除掉）
- 必须在QQ中在点击“超级调色盘”把主题选择为“极简白”(本软件2.1.0版本及其以上不用改)
- 如果要进行二次分发或转载须附上版权声明和保留开源协议
- 因为QQ更新迭代速度很快，所以`爱丽丝QQ聊天AI.pdf`文档里的QQ展示界面会因为无法及时更新文档有所不同，但是效果最终一致。

## 免责声明
- ⚠️本软件通过 DeepSeek API 生成的内容不代表开发者观点，其准确性、适当性由使用者自行判断并承担全部责任。🤖AI可能产生错误、偏见或不适宜内容，开发者不对此引发的任何后果负责。
- ⚖️如果使用该软件导致Q号被封⚡，开发者不负任何责任！(非要作死开发者也拦不住，已提供移除危险指令的选项)🎭用户需要自行承当封号的风险！！！
- 📜使用LGPL2.0开源协议，🚫禁止将该项目用于引流(带节奏)、🔞纯色情(如:写黄色小说)、❌当键政(政治敏感话题讨论)、🔥消息轰炸等非法目的。
- 💡此软件的根本目的是打造接入DeepSeek的API接口实现“满分”🧠的问题解答和为用户提供《情绪价值💖》！
- 🖼️项目中使用的所有图像资源仅供个人研究学习📚和欣赏之用🔍，如有侵权，请通知开发者立即删除。

## 致谢

此项目的开发离不开以下项目
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [Python-UIAutomation-for-Windows](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows)
- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)

## 相关项目

- [DeepseekConversationEngine](https://github.com/yandifei/DeepseekConversationEngine) 基于deepseek api开发的类库

## 问题反馈
- 其实还有别的项目要研发和个人学习(繁忙)，没时间处理issues。
- 提交 [Issues](https://github.com/yandifei/ArisuQQChatAI/issues) 或 邮箱3058439878@qq.com

