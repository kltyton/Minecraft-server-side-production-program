import os
import tkinter as tk
from tkinter import filedialog
import shutil

def main():
    # 创建GUI窗口
    print("请选择当前服务器路径")
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    # 弹出对话框让用户选择文件夹路径
    current_dir = filedialog.askdirectory(title= "请选择服务器所在文件夹")
    if current_dir:
        print("选择的文件夹路径是:", current_dir)
    else:
        print("未选择任何文件夹路径")
    # 要删除的文件名和文件夹名列表
    files_to_delete = ["模组信息.json", "需要人工排查的mod列表.json", "log.json", "MODID.json"]
    folders_to_delete = ["需要人工排查的mod文件"]

    # 遍历文件夹中的所有文件和文件夹
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)

        # 如果是文件并且文件名在files_to_delete列表中，则删除文件
        if os.path.isfile(item_path) and item in files_to_delete:
            os.remove(item_path)
            print(f"已删除文件: {item}")

        # 如果是文件夹并且文件夹名在folders_to_delete列表中，则删除文件夹及其内容
        elif os.path.isdir(item_path) and item in folders_to_delete:
            shutil.rmtree(item_path)
            print(f"已删除文件夹: {item}")

if __name__ == "__main__":
    main()
