#-*- coding:UTF-8-*-

import smtplib
import time
from email.mime.text import MIMEText

def send_email(text):
    sent=smtplib.SMTP()
    sent.connect('smtp.163.com',25) #SMTP拂去器地址:smtp.qiye.163.com;端口：25
    mail_name="zhangtw_neu@163.com" # 发送人邮箱地址
    mail_password = "LEKEQMVIMVFWYZMV" # 注意：这里不是密码，而应该填写授权码，如果不知道授权码，可以填写密码试一下
    sent.login(mail_name, mail_password) # 登陆
    to = ['592131686@qq.com'] # 收件人邮箱地址
    content = MIMEText('{}'.format(text)) # 正文内容
    content['Subject'] = '服务器IP' # 邮件标题
    content['From'] = mail_name # 发件人
    content['To'] =','.join(to) #收件人，用逗号连接多个邮件，实现群发
    # 发送邮件
    try:
        sent.sendmail(mail_name, to, content.as_string())  #3个参数 发送人，收件人，邮件内容
        print('Success')
        sent.close()
    except smtplib.SMTPException:
        print("Error：Fail")


if __name__ == "__main__":
    import socket
    before_IP = ""
    while True:
        # sleep for the remaining seconds until the next hour
        if before_IP != "":
            time.sleep(3600 - time.time() % 3600)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            if(s.getsockname()[0] == before_IP):
                continue
            else:
                send_email(s.getsockname()[0])
                before_IP = s.getsockname()[0]
        except:
            continue
