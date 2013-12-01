# -*- coding: utf-8 -*-
'''
Simple Email Module Block Mode
@author: Alvin

Example of use:
    # at start
    qm = SingleMail.get_instance()
    qm.init('smtp.host.com', 'user@auth.com', 'SecretPassword')

    ...
    # someware in app method
    qm = SingleMail.get_instance()
    qm.send(Email(subject="Subject", text="Keep smiling :)", adr_to="marcinc81@gmail.com", adr_from="sender@email.com"))

'''

import smtplib
import logging
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate
log = logging.getLogger("EMail")
class SingleMail():
    instance = None
    def init(self, smtp_host, smtp_login, smtp_pswd, sender, smtp_port = 465):
        self.smtp_host = smtp_host
        self.smtp_login = smtp_login
        self.smtp_password = smtp_pswd
        self.smtp_port = smtp_port
        self.sender = sender
    def __init__(self):
        self.smtp_host = None
        self.smtp_login = None
        self.smtp_password = None
        self.smtp_port = None
        self.sender = None

    def make_rfc_message(self, mail_to, subject, text, mime_type='plain'):
        '''
        Creates standardized email with valid header
        '''
        msg = MIMEText(text, mime_type, 'utf-8')
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = mail_to
        msg['Date'] = formatdate()
        msg['Reply-To'] = self.sender
        msg['Message-Id'] = make_msgid('unique-send')
        return msg
    def send_email(self, mail_to, subject, text, mime_type):
        smtp = None
        try:
            smtp = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            smtp.login(self.smtp_login, self.smtp_password)

            try:
                msg = self.make_rfc_message(mail_to, subject, text, mime_type)
                content = msg.as_string()
                smtp.sendmail(self.sender, mail_to, content)
            except Exception as e:
                log.exception(e)
                smtp.quit()

        except Exception as e:
            log.exception(e)
        finally:
            if smtp:
                smtp.quit()
    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = SingleMail()
        return cls.instance
#
# class Email(object):
#     unique = 'unique-send'
#
#     def __init__(self, **props):
#         '''
#         @param adr_to: send to
#         @param adr_from: send from
#         @param subject: subject of email
#         @param mime_type: plain or html - only minor mime type of 'text/*'
#         @param text: text content of email
#         '''
#         self.text = props.get('text', '')
#         self.subject = props.get('subject', None)
#         self.adr_to = props.get('adr_to', None)
#         self.adr_from = props.get('adr_from', None)
#         self.mime_type = props.get('mime_type', 'plain')
#
#     def __str__(self):
#         return "Email to: %s, sub: %s" % (self.adr_to, self.subject)
#
#     def as_rfc_message(self):
#         '''
#         Creates standardized email with valid header
#         '''
#         msg = MIMEText(self.text, self.mime_type, 'utf-8')
#         msg['Subject'] = self.subject
#         msg['From'] = self.adr_from
#         msg['To'] = self.adr_to
#         msg['Date'] = formatdate()
#         msg['Reply-To'] = self.adr_from
#         msg['Message-Id'] = make_msgid(Email.unique)
#         return msg