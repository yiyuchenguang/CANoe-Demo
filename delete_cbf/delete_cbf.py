# -*- coding: utf-8 -*-
import os
import argparse
import stat

def file_name(file_dir, postfix):
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if postfix in os.path.splitext(file)[1]:
                file_path = os.path.join(root, file)
                print("删除文件:", file_path)
                os.chmod(file_path, stat.S_IWRITE)  # 去掉只写模式
                os.remove(os.path.join(root, file_path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--inputDirectory', required=True)
    parser.add_argument('-t', '--fileType', default=".cbf")
    args = parser.parse_args()

    directory = args.inputDirectory
    print("选择的目标文件夹:", directory)
    print("选择的删除文件类型:", args.fileType)
    if directory:
        file_name(directory, args.fileType)
