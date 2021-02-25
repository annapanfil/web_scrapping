import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from re import search
from getpass import getpass

def send_mail(subject="An email", text="Send by Python\nsss...",  to_email=None, from_email="Name <address@domain.com>", password=None):
    assert isinstance(to_email, list) #raise error if it is not a list
    msg = MIMEMultipart('alternative')
    msg["From"] = from_email
    msg["To"] = ", ".join(to_email) #comma-separated list
    msg["Subject"] = subject
    txt_part = MIMEText(text, 'plain')
    msg.attach(txt_part)
    # html_part = MIMEText("<h1>This is working </h1>", 'html')
    # msg.attach(html_part)

    m = search("<\S+@\S+\.\S+>", from_email)
    if m!= None:
        plain_email = from_email[m.start()+1:m.end()-1]
    else:
        plain_email = from_email

    msg_str = msg.as_string()
    #login to smtp server
    with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
        server.ehlo()
        server.starttls() #secure conection
        server.login(plain_email, password)
        try:
            server.sendmail(from_email, to_email, msg_str)
        except:
            raise Exception("Not_sent")
        server.quit()

def get_credentials():
    login = input("Email adress (e.g. Name <address@gmail.com>): ")
    password = getpass()
    return login, password

def get_text():
    subject = input("Subject: ")
    print("Message (press Ctrl-D to finish): ")
    text = ""
    while True:
        try:
            line = input()
        except EOFError:
            break
        text += line + '\n'
    to_email = input("recipients' email addresses (separated by a comma): ")
    to_email = to_email.split(',')

    return subject, text, to_email

if __name__ == '__main__':
    print("Send an email from your gmail account\n--------------------------------------\n")
    login, password = get_credentials()
    subject, text, to_email = get_text()
    send_mail(subject, text, to_email, login, password)
