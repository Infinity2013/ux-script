import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
sender = 'xiaoliangx.wu@intel.com'
smtpserver = 'OutlookSH.intel.com'
receiver = 'xiaoliangx.wu@intel.com'
smtp = smtplib.SMTP()

def send_email(mailargs):

    msg =  mailargs.get("msg")
    subject = mailargs.get("subject")
    cc = mailargs.get("cc")

    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['Cc'] = cc
    msgRoot['To'] = receiver
    msgText = MIMEText('%s'%msg,'html','utf-8')
    msgRoot.attach(msgText)
    while 1:
        try:
            smtp.sendmail(sender, receiver, msgRoot.as_string())
            break;
        except:
            smtp.connect(smtpserver)

if __name__ == "__main__":
    mailargs = {}
    mailargs["msg"] = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD4mCAkkkacE13icKh2/Ic9X9fqrFMlr99GnOFegKNaMvQI1OTDZGe6vJjrIgTMf7tuN5m6WlmFr6BfbfMsBt1kctyoumWTQGue35BjhA4X61NlvPODJ1hydSEeK1Y0bWb0GxRZ5NDbCmVnGNoQor3wcanmdCC4Zp9lBd8sPoGkGTsCiHntdMz7YuODP4JnuNsTkwIjJ4etsQq4SVtvm2KjFpB3W+MpNQYceY19YM+7wlykybk4kGhR03+u1FMvR0agBpbDwhh2Ms4HdPWBNsqU54yi3N8oJF6/UfhNa9eY5hcn1PLbs35j9mJTrAqTOUg/xDOTNtE2WC/VroTnuPfn wxl@wxl-ubuntu"
    mailargs["subject"] = "test"
    mailargs["cc"] = "xiaoliangx.wu@intel.com"

    send_email(mailargs)
