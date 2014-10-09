#coding=utf-8
import wx
import os

import wx
class Frame(wx.Frame): #3
    pass
class App(wx.App):
    def OnInit(self):
        self.frame = Frame(parent=None, title='Spare') #4
        self.frame.Show()
        self.SetTopWindow(self.frame) #5
        return True

if __name__ == '__main__': #6
    app = App()
    app.MainLoop()



