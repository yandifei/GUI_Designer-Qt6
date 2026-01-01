import shutil   # shutil.copy2() - 保留元数据（修改时间等）
from pathlib import Path

# 删除整合目录
try:
    shutil.rmtree("ArisuQQChatAI")
except FileNotFoundError:
    pass

# 需要整合的目录
(target := Path("ArisuQQChatAI")).mkdir(parents=True, exist_ok=True)
# 用户数据
(target / "用户设置").mkdir(parents=True, exist_ok=True)
(target / "用户设置" / "Bind.ini").touch(exist_ok=True)
(target / "用户设置" / "web_data").mkdir(parents=True, exist_ok=True)
(target / "用户设置" / "web_data" / "pixiv_cookies.txt").touch(exist_ok=True)

# 日志
(target / "logs").mkdir(parents=True, exist_ok=True)
(target / "logs" / "pixiv").mkdir(parents=True, exist_ok=True)
(target / "logs" / "下载缓存").mkdir(parents=True, exist_ok=True)
(target / "logs" / "发送缓存").mkdir(parents=True, exist_ok=True)

# 资源目录
(target / "resource").mkdir(parents=True, exist_ok=True)

# 文档
(target / "文档").mkdir(parents=True, exist_ok=True)


def copy_file(src: Path | str):
    # 拷贝文件到一个目录中
    shutil.copy2(src, Path("ArisuQQChatAI") / src)
def copy_dir(src: Path | str):
    # 拷贝目录到一个目录
    shutil.copytree(src, Path("ArisuQQChatAI") / src, dirs_exist_ok=True, copy_function=shutil.copy2)
# 文件
shutil.copy2("dist/爱丽丝QQ聊天AI/爱丽丝QQ聊天AI.exe", target / "爱丽丝QQ聊天AI.exe")
shutil.copy2("用户设置/KeyboardShortcut.ini", target / "用户设置/KeyboardShortcut.ini")
shutil.copy2("用户设置/option.yml", target / "用户设置/option.yml")
shutil.copy2("用户设置/UserSettings.ini", target / "用户设置/UserSettings.ini")
shutil.copy2("文档/爱丽丝QQ聊天AI.md", target / "文档/爱丽丝QQ聊天AI.md")
shutil.copy2("文档/爱丽丝QQ聊天AI.pdf", target / "文档/爱丽丝QQ聊天AI.pdf")
shutil.copy2("../README.md", target / "文档/README.md")
shutil.copy2("../README.pdf", target / "文档/README.pdf")
shutil.copy2("../LICENSE", target / "文档/LICENSE")

# 目录(目录存在就直接覆盖文件)
shutil.copytree("dist/爱丽丝QQ聊天AI/packages", target / "packages", dirs_exist_ok=True, copy_function=shutil.copy2)
shutil.copytree("resources/deepseek_v3_tokenizer", target / "resources/deepseek_v3_tokenizer", dirs_exist_ok=True, copy_function=shutil.copy2)
shutil.copytree("用户设置/关键词回复", target / "用户设置/关键词回复", dirs_exist_ok=True, copy_function=shutil.copy2)
shutil.copytree("用户设置/提示库", target / "用户设置/提示库", dirs_exist_ok=True, copy_function=shutil.copy2)




