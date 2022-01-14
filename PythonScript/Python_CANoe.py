
# --------------------------------------------------------------------------
# Standard library imports
import os
import sys
import subprocess
import time
import msvcrt
from win32com.client import *
from win32com.client.connect import *


# Vector Canoe Class
class CANoe:
    def __init__(self):
        self.application = None
        self.application = DispatchEx("CANoe.Application")
        self.ver = self.application.Version
        print('Loaded CANoe version ',
              self.ver.major, '.',
              self.ver.minor, '.',
              self.ver.Build, '...')  # , sep,''

        self.Measurement = self.application.Measurement.Running

    def open_cfg(self, cfgname):
        # open CANoe simulation
        if (self.application != None):
            # check for valid file and it is *.cfg file
            if os.path.isfile(cfgname) and (os.path.splitext(cfgname)[1] == ".cfg"):
                self.application.Open(cfgname)
                print("opening..." + cfgname)
            else:
                raise RuntimeError("Can't find CANoe cfg file")
        else:
            raise RuntimeError("CANoe Application is missing,unable to open simulation")

    def close_cfg(self):
        # close CANoe simulation
        if (self.application != None):
            print("close cfg ...")
            # self.stop_Measurement()
            self.application.Quit()
            self.application = None

    def start_Measurement(self):
        retry = 0
        retry_counter = 5
        # try to establish measurement within 5s timeout
        while not self.application.Measurement.Running and (retry < retry_counter):
            self.application.Measurement.Start()
            time.sleep(1)
            retry += 1
        if (retry == retry_counter):
            raise RuntimeWarning("CANoe start measuremet failed, Please Check Connection!")

    def stop_Measurement(self):
        if self.application.Measurement.Running:
            self.application.Measurement.Stop()
        else:
            pass

    def get_SigVal(self, channel_num, msg_name, sig_name, bus_type="CAN"):
        """
        @summary Get the value of a raw CAN signal on the CAN simulation bus
        @param channel_num - Integer value to indicate from which channel we will read the signal, usually start from 1,
                             Check with CANoe can channel setup.
        @param msg_name - String value that indicate the message name to which the signal belong. Check DBC setup.
        @param sig_name - String value of the signal to be read
        @param bus_type - String value of the bus type - e.g. "CAN", "LIN" and etc.
        @return The CAN signal value in floating point value.
                Even if the signal is of integer type, we will still return by
                floating point value.
        @exception None
        """
        if (self.application != None):
            result = self.application.GetBus(bus_type).GetSignal(channel_num, msg_name, sig_name)
            return result.Value
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def get_EnvVar(self, var):
        if (self.application != None):
            result = self.application.Environment.GetVariable(var)
            return result.Value
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def set_EnvVar(self, var, value):
        result = None
        if (self.application != None):
            # set the environment varible
            result = self.application.Environment.GetVariable(var)
            result.Value = value
            checker = self.get_EnvVar(var)
            # check the environment varible is set properly?
            while (checker != value):
                checker = self.get_EnvVar(var)
        else:
            raise RuntimeError("CANoe is not open,unable to SetVariable")

    def get_SysVar(self, ns_name, sysvar_name):
        if (self.application != None):
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            return sys_value.Value
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def set_SysVar(self, ns_name, sysvar_name, var):
        if (self.application != None):
            systemCAN = self.application.System.Namespaces
            sys_namespace = systemCAN(ns_name)
            sys_value = sys_namespace.Variables(sysvar_name)
            sys_value.Value = var
        else:
            raise RuntimeError("CANoe is not open,unable to GetVariable")

    def DoEvents(self):
        pythoncom.PumpWaitingMessages()
        time.sleep(1)


app = CANoe()  # 定义CANoe为app
app.open_cfg(r"D:\CANoe-Demo/bmw2.cfg")  # 导入某个CANoe congif
time.sleep(5)
app.start_Measurement()

while not msvcrt.kbhit():
    EngineSpeedDspMeter = app.get_SysVar("Engine", "EngineSpeedDspMeter")
    print(EngineSpeedDspMeter)
<<<<<<< HEAD
    if (EngineSpeedDspMeter == 2):
        app.set_SysVar("Engine", "EngineSpeedDspMeter", 3.0)
=======
    if(EngineSpeedDspMeter==2):
        app.set_SysVar("Engine","EngineSpeedDspMeter",3.0)
>>>>>>> beed72609c0d06b71498fdfd6cb3a5488cddf4f2
    app.DoEvents()

