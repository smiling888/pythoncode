#!/usr/bin/env python3  
#coding: utf-8  

import smtplib
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import email
import time
#import persistent
class MyEmail:
  """this moudle is for send email lzs 2006.08.26"""
  def __init__(self,femail='lzhhua110@126.com',fpwd='zhenhua@liao520',tmail='liaozhenhua@sogou-inc.com',subject='hello',mybody='this letter is from yihaomen.com'):
      self.femail=femail
      self.fpwd=fpwd
      self.temail=tmail
      self.mybody=mybody
      self.subject=subject
  def SendEmail(self):     
      my_body=self.mybody     
      msg=MIMEMultipart()
      msg['From'] = self.femail
      msg['To'] = self.temail
      msg['Subject'] =  self.subject
      msg['Reply-To'] = self.femail
      msg['Date'] = time.ctime(time.time())
      msg['X-Priority'] =  '''3'''
      msg['X-MSMail-Priority'] =  '''Normal'''      
      body=email.MIMEText.MIMEText(self.mybody,_subtype='html',_charset='gb2312')
      msg.attach(body)
      s = smtplib.SMTP('smtp.126.com')
      s.login(self.femail,self.fpwd)
      s.sendmail(self.femail,self.temail,msg.as_string())
      s.close()
email1=MyEmail()
email1.SendEmail()
