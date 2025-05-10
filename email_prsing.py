import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# POP3 server details
pop_server = 'outlook.office365.com'
pop_server_port = 995
username = 'your_test@outlook.com'
password = 'your_password'
# Forwarding details
forward_address = 'forwarding_test@outlook.com'
# SMTP server
smtp_server = 'smtp.office365.com'
smtp_port = 587

def extract_http_links(payload):
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    http_links = re.findall(pattern, payload)
    return http_links

def remove_http_links(payload):
    pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    payload_without_links = re.sub(pattern, '', payload)
    return payload_without_links

def send_all_email(message_all):
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = forward_address
    msg['Subject'] = 'Recived Email From POP Server'
    msg.attach(MIMEText(message_all))
    mail = smtplib.SMTP(smtp_server, smtp_port)
    mail.ehlo()
    mail.starttls()
    mail.ehlo()
    mail.login(username, password)
    mail.sendmail(username, forward_address, msg.as_string())
    mail.quit()



# Connect to POP3 server
pop_conn = poplib.POP3_SSL(pop_server, pop_server_port)
pop_conn.user(username)
pop_conn.pass_(password)

# Get email count and list
num_emails = len(pop_conn.list()[1])
message_all = ''

for i in range(num_emails):
    # Retrieve email by index
    response, lines, octets = pop_conn.retr(i + 1)
    email_content = b'\r\n'.join(lines).decode('utf-8')

    # Parse email content
    email = Parser().parsestr(email_content)

    msg_content = ""
    if (email.is_multipart()):
        for part in email.get_payload():
            if (part.get_content_type() == 'text/plain'):
                msg_content = remove_http_links(part.get_payload())

    else:
        if (email.get_content_type() == 'text/plain'):
            msg_content = remove_http_links(email.get_payload())

    message_all += 'Subject - ' + email['Subject'] + '\nFromAddr - ' + email['From'] + '\nMessage Content - \n' + msg_content + '\n\n'

    # if need, delete.
    # pop_conn.dele(i + 1)

# Send email
send_all_email(message_all)
print('send - ok')

pop_conn.quit()