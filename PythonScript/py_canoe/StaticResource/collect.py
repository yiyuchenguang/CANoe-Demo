import os


cu = os.path.dirname(os.path.realpath(__file__))
print(cu)


def file_name(file_dir):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.ico':
                L.append(os.path.join(root, file))
    return L

    # 其中os.path.splitext()函数将路径拆分为文件名+扩展名

files = file_name(cu)
print(files)
temp_str=''
for i in files:
    tem = i.split("\\")
    temp_str = temp_str + "\n" + '''    <file>{}/{}</file>'''.format(tem[-2],tem[-1])


temp_str ='''<RCC>
  <qresource prefix="picture">
    %s
  </qresource>
</RCC>
'''%temp_str
print(temp_str)

with open("photo.qrc",'w') as f:
    f.write(temp_str)

os.popen("pyrcc5.exe photo.qrc -o photo.py")

