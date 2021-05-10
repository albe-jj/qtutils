import win32com.client
import time


class LVApp:

    def __init__(self, AppName, ViName):
        self.App = win32com.client.Dispatch(AppName)
        self.Vi = self.App.GetViReference(ViName)

    # Reading data from VI's is straight forward
    def GetData(self, ControlName):
        return self.Vi.GetControlValue(ControlName)

    # Writing data to VI's is more complicated.
    # It is possible to write data by simply using SetControlValue(<Name>), but that does not trigger ValueChanged event
    # in LabView program. Since a lot of things are happening inside the event structure, it breaks TC and FP programs.
    # Instead there is a special cluster called "SetControl". It has three fields: "Name", "Scalar" and "Array".
    # To write data to any control put its name in "Name" field and value in either "Scalar" or "Array" field depending on
    # data type. Do not write data in both "Scalar" and "Array" fields as the LabView program will ignore the command. Put
    # empty string '' or empty list [[], []] in the unused field.
    # It is possible to write data to individual controls in clusters by <ClusterName>.<ControlName> notation. It will
    # trigger the ValueChanged event for that control and not the cluster.
    # After the program reads the "SetControl" structure it will empty it to flag that it's been processed. Checking if
    # the cluster is empty allows synchronous operation
    def SetData(self, ControlName, ControlData, Async = False):
        if type(ControlData) in (tuple, list):
            self.Vi.SetControlValue('SetControl', (ControlName, '', ControlData))
        else:
            self.Vi.SetControlValue('SetControl', (ControlName, ControlData, [[], []]))
        if not Async:
            while self.Vi.GetControlValue('SetControl')[0] != '': time.sleep(0.1)