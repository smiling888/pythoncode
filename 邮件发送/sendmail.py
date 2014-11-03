#coding: utf-8
from email.Header import Header
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import smtplib, datetime

#创建一个带附件的实例
msg = MIMEMultipart()
#构造附件
#att = MIMEText(open('d:\\tc201.rar', 'rb').read(), 'base64', 'gb2312')
#att["Content-Type"] = 'application/octet-stream'
#att["Content-Disposition"] = 'attachment; filename="tc201.rar"'
#msg.attach(att)

#加邮件头
msg['to'] = 'liaozhenhua@sogou-inc.com'
msg['from'] = '1843623538@qq.com'
msg['subject'] = Header('冒烟测试结果 (' + str(datetime.date.today()) + ')', 'utf-8')
#发送邮件
server = smtplib.SMTP('smtp.qq.com')
server.sendmail(msg['from'], msg['to'], msg.as_string())
server.close()

