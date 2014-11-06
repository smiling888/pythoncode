#coding=utf-8
import win32api
import win32con
import win32com.client
import wx
import os

import wx
import wx.xrc


class MyFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"监测360拦截", pos = wx.DefaultPosition, size = wx.Size( 650,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_textCtrl3 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 520,600 ), wx.TE_MULTILINE )
		bSizer1.Add( self.m_textCtrl3, 0, wx.ALL, 5 )
		
		self.m_button3 = wx.Button( self, wx.ID_ANY, u"监测", wx.Point( 10,100 ), wx.DefaultSize, 0 )
		bSizer1.Add( self.m_button3, 0, wx.ALL, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_button3.Bind( wx.EVT_BUTTON, self.StartMonitor )

		InitVaries()
	
	def __del__( self ):
		pass
	
	
	
	# Virtual event handlers, overide them in your derived class
	def StartMonitor( self, event ):
		CheckInitEvnt()
		StartToMonitor()
		#self.m_textCtrl3.AppendText('111\n')
		
        def InitVaries(self):
            #初始化变量，1 检测字符串，时间
            self.MonitorStr=""
            self.LoopTime=4*60*60
            self.IsLoop=True
            self.CheckFileLog=os.environ["appdata"]+"\\SogouMobileTool\\Log\\MobileRun.log"
        
	def CheckInitEvnt(self):
		#判断是否装了助手
		if not IsZhushouExits():
                    pass
		#判断是否装了360
		if not Is360Exists():
                    pass
        def Is360Exists(self):
            import psutil
            a360=0
            pl=list(psutil.process_iter())
            for p in pl:
                if p.name.find('360Tray.exe')!=-1:
                    a360+=1
                    break
            return a360
        def IsZhushouExits(self):
            #判断助手是否存在
            pass
        def UninstallZhouFromPhone(self):
            #从手机卸载助手
            pass
        def InstallZhushouToPhone(self):
            #，通过重启向手机安装助手
            pass
        def CheckLog():
            #扫描Runlog文件
            if os.path.exists():
                f=open(self.CheckFileLog)
                revlines =f.readlines()
                for line in revlines:
                    if line.find(self.MonitorStr)!=-1:
                        self.m_textCtrl3.AppendText(l[0]+" "+l[1]+"\n"+l[4:]+"\n")
            else:
                self.m_textCtrl3.AppendText(self.CheckFileLog+" does not exists\n")
        def StartToMonitor(self):
            import time
            start=0
            while  self.IsLoop:
                start=start+1
                if start==self.LoopTime:
                    InstallZhushouToPhone()
                    start=0
#print __name__
if __name__=="__main__":
    app=wx.App()
    frame=MyFrame1(None)
    frame.Show(True)
    app.MainLoop()
