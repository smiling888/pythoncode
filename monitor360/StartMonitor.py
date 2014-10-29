#coding=utf-8
import win32api
import win32con
import win32com.client
import wx

# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

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
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def StartMonitor( self, event ):
		CheckInitEvnt()
		self.m_textCtrl3.AppendText('111\n')
		
		event.Skip()
	def CheckInitEvnt(self):
		#判断是否装了助手
		IsZhushouExits()
		#判断是否装了360
		Is360Exists()
		
app=wx.App()
frame=MyFrame1(None)
frame.Show(True)
app.MainLoop()