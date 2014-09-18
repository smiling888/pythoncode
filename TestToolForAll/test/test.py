#coding=utf-8
import wx
print 'start'


class MyFrame(wx.Frame):
    pass

class MyApp(wx.App):
    def OnInit(self):
        self.frame=MyFrame(parent=None,title='test')
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True



if __name__=="__main__":

    #myApp=MyApp()
    #myApp.MainLoop()
    app = wx.PySimpleApp()
    frame = MyNewFrame(None)
    frame.Show(True)
    app.MainLoop()
    print 'end'
