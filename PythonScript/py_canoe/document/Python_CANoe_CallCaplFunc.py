import time, os, msvcrt
from win32com.client import *
from win32com.client.connect import *



def DoEvents():
    pythoncom.PumpWaitingMessages()
    time.sleep(.1)

def DoEventsUntil(cond):
    while not cond():
        DoEvents()

class CanoeSync(object):
    """Wrapper class for CANoe Application object"""
    Started = False
    Stopped = False
    application = None
    ConfigPath = ""

    def __init__(self):
        app = DispatchEx('CANoe.Application')
        app.Configuration.Modified = False
        ver = app.Version
        print('Loaded CANoe version ',
              ver.major, '.',
              ver.minor, '.',
              ver.Build, '...', sep='')
        self.App = app
        CanoeSync.application = app
        self.Measurement = app.Measurement
        self.Running = lambda: self.Measurement.Running
        self.WaitForStart = lambda: DoEventsUntil(lambda: CanoeSync.Started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: CanoeSync.Stopped)
        WithEvents(self.App.Measurement, CanoeMeasurementEvents)

        self.testResul_all = [] # 用于统计测试结果


    def Start(self):
        if not self.Running():
            self.Measurement.Start()
            self.WaitForStart()

    def Stop(self):
        if self.Running():
            self.Measurement.Stop()
            self.WaitForStop()

    def Load(self, cfgPath):
        # current dir must point to the script file
        cfg = os.path.join(os.curdir, cfgPath)
        cfg = os.path.abspath(cfg)
        print('Opening: ', cfg)
        self.ConfigPath = os.path.dirname(cfg)
        self.Configuration = self.App.Configuration
        self.App.Open(cfg)

    def LoadTestSetup(self, testsetup):
        self.TestSetup = self.App.Configuration.TestSetup
        print(self.ConfigPath)
        path = os.path.join(self.ConfigPath, testsetup)
        print("传入的tse路径：", path)
        # 如果目标 tse 已存在，直接读取，否则添加它,如果已经存在，直接add的话会报错
        tse_count = self.TestSetup.TestEnvironments.Count
        print("add前tse数量:",tse_count)
        _existTse = False
        for _index_tse in range(1, tse_count + 1):
            if self.TestSetup.TestEnvironments.Item(_index_tse).FullName == path:
                testenv = self.TestSetup.TestEnvironments.Item(_index_tse)
                _existTse = True
                break
        if _existTse == False:
            testenv = self.TestSetup.TestEnvironments.Add(path)

        print("add后tse数量:", self.TestSetup.TestEnvironments.Count)

        testenv = CastTo(testenv, "ITestEnvironment2")
         # TestModules property to access the test modules
        self.TestModules = []
        self.TraverseTestItem(testenv, lambda tm: self.TestModules.append(CanoeTestModule(tm)))

    def TraverseTestItem(self, parent, testf):
        for test in parent.TestModules:
            testf(test)
        for folder in parent.Folders:
            found = self.TraverseTestItem(folder, testf)

    def RunTestModules(self):
        """ starts all test modules and waits for all of them to finish"""
        # start all test modules

        for subtm in self.TestModules:
            subtm.Start()
            while not subtm.IsDone():
                DoEvents()

            for i in range(1, subtm.tm.Sequence.Count + 1):
                self.StatisticTesResult(subtm, subtm.tm.Sequence.Item(i))
        # 统计测试结果
        import pandas as pd
        df = pd.DataFrame(self.testResul_all,columns=['TestModule', 'TestGroup', 'TestCae','TestResult'])
        print(df)

    def StatisticTesResult(self, tm, tx):
        """
        Summary test case result
        :para tx: test group or case.
        :para tg: test group
        :para tc: test case
        """
        tg = CastTo(tx, "ITestGroup")
        try:
            _count = tg.Sequence.Count
        except Exception:  # test case
            tc = CastTo(tx, "ITestCase")
            self.testResul_all.append( [tm.Name, tg.Name, tc.Name, str(tc.Verdict)])
        else:  # test group
            for j in range(1, _count + 1):
                self.StatisticTesResult(tm, tg.Sequence.Item(j))


    def SetTestModulesPath(self, log_path):
            for subtm in self.TestModules:
                report_name = subtm.tm.Report.Name + ".xml"
                fullname = os.path.join(log_path, report_name)
                report = subtm.tm.Report
                report.FullName = fullname
                print("report.FullName :", report.FullName)
    def SetLogging(self):
        """修改当前 logging 文件为默认（temp.blf）。"""
        for i in range(1, self.Configuration.OnlineSetup.LoggingCollection.Count + 1):
            print("**********",self.Configuration.OnlineSetup.LoggingCollection(i).FullName)
            filepath, tmpfilename = os.path.split(self.Configuration.OnlineSetup.LoggingCollection(i).FullName)
            _log_fullName = os.path.join(filepath, 'temp.blf')
            if os.path.exists(_log_fullName):
                os.remove(_log_fullName)
            try:
                self.Configuration.OnlineSetup.LoggingCollection(i).FullName = _log_fullName
            except Exception as e:
                print(e)
            else:
                self.logging = self.Configuration.OnlineSetup.LoggingCollection(i)
                self.temp_logName = self.logging.FullName
            print("**********", self.Configuration.OnlineSetup.LoggingCollection(i).FullName)

    def CallCaplFunc(self):
        print("无参数，无返回值 CAPL FUNC调用实例：",CanoeSync.pyCallCaplFunc_1.Call())
        print("无参数，有int返回值 CAPL FUNC调用实例：", CanoeSync.pyCallCaplFunc_2.Call())
        print("有参数参数，有int返回值 有一个long型参数：",CanoeSync.pyCallCaplFunc_3.Call(1))
        print("有参数参数，有int返回值 CAPL FUNC调用实例：",CanoeSync.pyCallCaplFunc_4.Call(1, 0x11223344, 0.5))

class CanoeTestModule:
    """Wrapper class for CANoe TestModule object"""
    def __init__(self, tm):
        self.tm = tm
        self.Events = DispatchWithEvents(tm, CanoeTestEvents)
        self.Name = tm.Name
        self.FullName = tm.FullName
        self.Path = tm.Path
        self.IsDone = lambda: self.Events.stopped
        self.Enabled = tm.Enabled

    def Start(self):
        if self.tm.Enabled:
            self.tm.Start()
            self.Events.WaitForStart()
    def WaitReportGenerate(self):
        if self.tm.Enabled:
            self.Events.WaitForReportGenerated()
class CanoeTestEvents:
    """Utility class to handle the test events"""
    def __init__(self):
        self.started = False
        self.stopped = False
        self.reportGenerated = False
        self.WaitForStart = lambda: DoEventsUntil(lambda: self.started)
        self.WaitForStop = lambda: DoEventsUntil(lambda: self.stopped)
        self.WaitForReportGenerated = lambda: DoEventsUntil(lambda: self.reportGenerated)

    def OnStart(self):
        self.started = True
        self.stopped = False
        self.reportGenerated = False
        print("<", self.Name, " started >")
    def OnStop(self, reason):
        self.started = False
        self.stopped = True
        print("<", self.Name, " stopped >")
    def OnReportGenerated(self, success, sourceFullName, generatedFullName):
        self.reportGenerated = True
        print("<test report generated>:", sourceFullName)
        # print(success)
        # print(generatedFullName)
        # print(sourceFullName)


class CanoeMeasurementEvents(object):
    """Handler for CANoe measurement events"""
    def OnStart(self):
        CanoeSync.Started = True
        CanoeSync.Stopped = False
        print("< measurement started >")

    def OnStop(self):
        CanoeSync.Started = False
        CanoeSync.Stopped = True
        print("< measurement stopped >")

    def OnInit(self):# Occurs when the measurement is initialized
        print("< measurement is initialized >")
        print(CanoeSync.application.CAPL)
        CanoeSync.pyCallCaplFunc_1 = CanoeSync.application.CAPL.GetFunction("pyCallCaplFunc_1")
        CanoeSync.pyCallCaplFunc_2 = CanoeSync.application.CAPL.GetFunction("pyCallCaplFunc_2")
        CanoeSync.pyCallCaplFunc_3 = CanoeSync.application.CAPL.GetFunction("pyCallCaplFunc_3")
        CanoeSync.pyCallCaplFunc_4 = CanoeSync.application.CAPL.GetFunction("pyCallCaplFunc_4")
        print(CanoeSync.pyCallCaplFunc_3) #debug
        print(CanoeSync.pyCallCaplFunc_3.ParameterCount)
        print(type(CanoeSync.pyCallCaplFunc_3.ParameterTypes))
def main():
    Tester = CanoeSync()
    Tester.Load(r'../bmw2.cfg')
    Tester.Start()
    Tester.CallCaplFunc()
    Tester.Stop()
if __name__ == "__main__":
    main()
