import smtplib

SERVER = "smtp.gmail.com"

FROM = "xxx@gmail.com"
TO = ["yyy@gamil.com"] # must be a list

SUBJECT = "Hello!"

TEXT = "This message was sent with Python's smtplib."

# Prepare actual message

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

# Send the mail

server = smtplib.SMTP_SSL(SERVER,465)
server.login("xxx@gmail.com","yourpassword")
server.sendmail(FROM, TO, message)
server.quit()