#coding=utf-8
import wx
print 'aa'

def GetAppSetting():
    #解析程序路径配置

    cf=ConfigParser.ConfigParser()
    if not os.path.exists("AppSeting.ini"):
        mes=u'AppSeting.ini不在当前目录下'
        dlg=wx.MessageDialog(None,mes,u'运行出错',wx.OK,pos=wx.DefaultPosition)
        retCode=dlg.ShowModal()
        if (retCode == wx.ID_OK):
            print 'yes'
        else:
            print 'no'
        dlg.Destroy()
        return



if __name__=="__main__":
    print 'xx'
