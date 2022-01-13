
'''
@Created on 20210916
@author: carlwu
@file: AutoRestart
@description:
'''
import os
import sys



from PyQt5.QtWidgets import QMainWindow, QApplication,QListWidgetItem
from Dog import Ui_Mainform
import PyQt5.QtGui as qg
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor
from StaticResource import photo
from ReadConf import Conf
from callCAN import *

temp = sys.stdout
class Stream(QObject):
    newText = pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))
        # 实时刷新界面
        QApplication.processEvents()

class MainUi(QMainWindow,Ui_Mainform):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        sys.stdout = Stream(newText=self.onUpdateEdit)
        self.setWindowTitle("Python CANoe -V1.0")
        self.setWindowIcon(qg.QIcon("StaticResource/picture/dolphin.ico"))
        self.setFixedSize(self.width(), self.height())
        self.start.clicked.connect(self.StartRun)

        conf = Conf()
        if not conf.read("conf.ini"):
            return 0

        cfg = eval(conf.conf_dict.get("cfg"))
        #print(cfg)

        self.comboBox.addItems(cfg)
        self.comboBox.currentIndexChanged[str].connect(self.comboBoxValue)  # 条目发生改变，发射信号，传递条目内容

        tse = eval(conf.conf_dict.get("tse"))
        #print(tse)
        self.listWidget.addItems(tse)
        self.listWidget.itemDoubleClicked.connect(lambda: self.change_func(self.listWidget))
        self.listWidget_2.doubleClicked.connect(lambda: self.change_func(self.listWidget_2))

    def comboBoxValue(self,text):
        print(text)

    def change_func(self, listwidget):
        if listwidget == self.listWidget:
            item = QListWidgetItem(self.listWidget.currentItem()) #转化为QListWidgetItem对象
            self.listWidget_2.addItem(item)  #添加项目。参数是QListWidgetItem对象
            #print(self.listWidget_2.count()) #返回项目总数

        else:
            self.listWidget_2.takeItem(self.listWidget_2.currentRow())#删除指定索引号的项目

    def StartRun(self):

        cfg_checked = self.comboBox.currentText()
        print("当前选择的cfg为：",cfg_checked)
        count = self.listWidget_2.count()
        tse_checked = [self.listWidget_2.item(i).text() for i in range(count)]
        print("当前选择的tse为：")
        for i in tse_checked:
            print(i)

        if cfg_checked and tse_checked :
            Tester = CanoeSync()
            Tester.Load(os.path.abspath(self.comboBox.currentText()))
            for i in range(count):
                Tester.LoadTestSetup(tse_checked[i])
                print("正在测试tse：",tse_checked[i])
                Tester.SetTestModulesPath(os.path.join(Tester.ConfigPath, r"TestReport"))
                # # Tester.SetLogging()
                Tester.Start()
                Tester.RunTestModules()
                Tester.Stop()

        else:
            print("请先选择测试的tse和cfg")

    '''关闭app事件响应'''
    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        self.ms.close()
        sys.stdout = temp
        super().closeEvent(event)

    '''绑定输出流'''
    def onUpdateEdit(self, text):
        cursor = self.printWindow.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.printWindow.setTextCursor(cursor)
        self.printWindow.ensureCursorVisible()
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    demo = MainUi()
    demo.show()
    sys.exit(app.exec_())
