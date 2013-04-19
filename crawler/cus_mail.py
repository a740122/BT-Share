#!/usr/bin/env python
#coding:utf-8
import smtplib
from email.mime.text import MIMEText
#set your personal config file
from mail_config import gmail_config

mail_host= gmail_config['mail_host']
mail_port = gmail_config['mail_port']
mail_user= gmail_config['mail_user']
mail_pass= gmail_config['mail_pass']
mail_postfix= gmail_config['mail_postfix']


def send_mail(to_list,sub,content):
    '''
    to_list:发给谁
    sub:主题
    content:内容
    send_mail("zhkzyth@gmail.com","sub","content")
    '''
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content)
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host,mail_port)
        s.starttls()
        s.login(mail_user,mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

if __name__ == '__main__':
    """
    test case
    """
    mailto_list=["zhkzyth@gmail.com"]

    if send(mailto_list,"subject","content"):
        print "发送成功"
    else:
        print "发送失败"
