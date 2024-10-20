import json
import re
import shutil
import subprocess
from tkinter import filedialog
import download, Formatting, Importing, transformation, run
import os

title = "Fufu超爱大米制作-一键制作服务端"
os.system(f"title {title}")

options = {
    "1": "下载原始服务端和启动服务器",
    "2": "区分服务端客户端mod",
    "3": "使用mcmod对需要人工排查的mod进行搜索（未完成）",
    "4": "必要文件导入",
    "5": "格式化(所有相关文件)",
    "6": "全自动"
}

def clear(): 
    os.system('cls')
    print("加载中.....请等待......")
    
def validate_memory_size(memory_size: str) -> bool:
    # 简单的内存大小格式验证
    pattern = r'^\d+[GM]$'
    return re.match(pattern, memory_size) is not None

def choice_java():
    memory_size = input("请输入要分配的内存大小（如 2G）：")
    while not validate_memory_size(memory_size):
        print("内存大小格式不正确，请重新输入。")
        memory_size = input("请输入要分配的内存大小（如 2G）：")
    while True:
        java_path = input("请输入 Java 的完整路径（如果不知道则直接按回车使用默认的 java）：").strip()
        print("例如：“C:/Program File/java/java17/Bin/java.exe”（一定要有英文双引号和java.exe!!!!）")
        if not java_path:
            java_path = "java"
        process = subprocess.Popen([java_path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            print("你输入的Java 版本信息：")
            print(error.decode())
        confirm = input(f"您当前输入的 Java 路径为：{java_path}，是否确定要以该 Java 版本运行程序？(输入 Y 确认，其他任意键取消): ")
        if confirm.lower() == 'y':
            print("确定以该java运行服务器")
            break
        else:
            print("已取消以该java运行程序")
    return java_path, memory_size

def initialization(java_path, memory_size):
    unknown_folder = "服务端/需要人工排查的mod文件"
    os.makedirs(unknown_folder, exist_ok=True)
    
    #选择客户端
    print("请选择客户端文件夹")
    mods_folder = filedialog.askdirectory(title="选择客户端文件夹")
    if not mods_folder:
        print("未选择文件夹，程序退出")
        return
    client_folder = "服务端/客户端缓存文件夹"
    shutil.copytree(mods_folder, client_folder, dirs_exist_ok=True)
    json_name = os.path.basename(mods_folder)
    with open(mods_folder + "/" + json_name + '.json') as f:
        clinet_data = json.load(f)

    # 获取客户端信息
    game = clinet_data['arguments']['game']
    libraries = clinet_data['libraries']
    loader_version = None
    mc_version = None
    fa_setup_version = None
    loader_type = "fabric"
    for item in game:
        if isinstance(item, str):
            if item == "--fml.forgeVersion":
                loader_version = game[game.index(item) + 1]
                loader_type ="forge"
            elif item == "--fml.mcVersion":
                mc_version = game[game.index(item) + 1]
    if loader_type == "fabric":
        fa_setup_version = input("请输入你的 Fabric 安装器版本（如果不知道则输入 1.0.0）：")
        for obj in libraries:
            name = obj.get("name", "")
            if "net.fabricmc:intermediary:" in name:
                version_parts = name.split(":")
                if len(version_parts) > 2:
                    mc_version = version_parts[-1].strip()
            elif "net.fabricmc:fabric-loader:" in name:
                fa_loader_version = name.split(":")
                if len(fa_loader_version) > 2:
                    loader_version= fa_loader_version[-1].strip()
        
    data = {
        "客户端文件夹": mods_folder,
        "mod加载器类型": loader_type ,
        "mc版本": mc_version,
        "mod加载器版本": loader_version,
        "fabric安装器版本": fa_setup_version,
        "选择的java路径": java_path,
        "分配的内存": memory_size
        }
    with open("服务端/客户端mod信息.json", "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
        
    #设置工作路径
    os.chdir("服务端")
    
def main_menu():
    java_path, memory_size = choice_java()
    clear()
    initialization(java_path, memory_size)
    clear()
    while True:
        print("-此工具由B站UP主: Fufu超爱大米制作-工具完全免费")
        print("-本工具针对于我的世界客户端整合包转化为服务端整合包")
        print("-以下是功能选择，请选择您需要的功能！")
        print("-使用该脚本前一定要先对客户端进行备份！-")
        print("-使用该脚本前一定要先对客户端进行备份！！-")
        print("-使用该脚本前一定要先对客户端进行备份！！！-")
        print("-------------------------------------------------------------------------------------")
        for key, value in options.items():
            print(f"-{key}- {value}")
        print("-------------------------------------------------------------------------------------")
        choice = input("请选择一个功能：")
        
        if choice in options:
            if choice == "2":
                transformation.main()
            elif choice == "1":
                download.main()
            elif choice == "3":
                print("未完成，别急")
            elif choice == "4":
                Importing.main()
            elif choice == "5":
                Formatting.main()
            elif choice == "6":
                run.main()
            elif choice == "7":
                download.main()
                transformation.main()
                Importing.main()
                Formatting.main()
            input("按回车键返回主菜单...")
        else:
            print("无效的选项，请重新选择。")

if __name__ == "__main__":
    main_menu()