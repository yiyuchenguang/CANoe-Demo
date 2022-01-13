
import configparser
import os
class Conf(object):
    def __init__(self):
        self.conf_dict = {}
        '''https://docs.python.org/3/library/configparser.html'''

    def read(self, path):
        if os.path.exists(path): #判断文件是否存在

            config = configparser.ConfigParser()
            config.read(path)

            for section in config.sections():
                for key in config[section]:
                    topsecret = config[section]
                    self.conf_dict[key] = topsecret[key]
        else:
            print("not find conf file:",path)
            return 0
        return 1
if __name__== '__main__':
     c = Conf()
     c.read("conf.ini")
     print(c.conf_dict)
     for i in c.conf_dict:
         print(i,"=",c.conf_dict.get(i))
     #print(list(eval(c.conf_dict.get("category")).keys()))
         #print(c.conf_dict.get(i))
     # category = c.conf_dict["category"]
     # print(eval(category)["BYD_TC_DTC"])
