# <center>QQ监听者开发随笔</center>

## 机制原理
**利用的是`uiautomation`库实现的控件监听**。QQ窗口本质上是控件的集成，输入框是控件的一种，当然包括了对方发送的消息也属于控件的一种。
QQ的消息是一堆控件组合而成的(超级复合窗口)，而且这一堆控件还是动态变化的，不同的文本有不同的控件组合。
使用inspect.exe可以有效查看框口控件的信息以便编程实现多级控件控制和查找
***致命缺点***，QQ窗口如果不在前台就无法监测了，也就是窗口必须一直置顶才能被监测到，切开多少个QQ号都好，仅认聊天窗口
***
## 导包初始化
1. 通过win32api查看QQ是否打开（好像可以不写）
## QQMessageMonitor类
创建QQMessageMonitor对象后就会对窗口进行绑定，并且会进行一系列的初始化

***
## inspect.exe
官方说明：  https://learn.microsoft.com/zh-cn/windows/win32/winauto/inspect-objects
**inspect.exe下载**
如果要使用inspect.exe强烈建议走正规路径先下载SDK。从SDK里面使用inspect.exe，网上的大多有病毒（是的，我中招了，好在是虚拟机）
若要检查 UI 自动化，必须在系统上显示 UI 自动化。 有关详细信息，请参阅 Run-Time 要求。
检查作为 Windows 软件开发工具包（SDK）中的工具之一进行安装，其中包括本节中记录的所有辅助功能相关工具。 检查不会作为单独的下载分发。
Inspect.exe 位于 SDK 安装路径的 \bin\<版本>\<平台> 文件夹中。 通常不需要以管理员身份运行它。
SDK下载链接：https://go.microsoft.com/fwlink/?linkid=2305205

## 需要的包
```python
pip install requests
pip install uiautomation
pip install pywin32
pip install pillow
pip install transformers
pip install openai
```

# 算法机制
现在的机制实在是太鸡肋了，存储了2遍消息，且不说存储空间大大浪费，遍历的机制也没写好
纯纯的暴力解析，根本毫无优雅可言。
每条消息都是进行一次递归解析，且有无新消息都是对所有消息进行递归解析，这太浪费CPU资源了，后期应该改为控件ID对比，最后一个ID与我收集到的ID不符合时才进行消息解析，避免没有必要的解析和极大减少CPU压力，毕竟线程的情况下对CPU核心的压力还是很大的。



# 消息类型
时间
文本
文件
卡片
系统：加入了群聊、撤回、拍一拍
链接
群聊转发
红包消息

精华消息\撤回消息不解析(2025.12.31)
解析控件很明显看出来接下来的版本QQ想要干啥了，他现在逻辑比之前乱多了

哈哈哈哈，原来性能很低