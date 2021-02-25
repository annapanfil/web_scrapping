from send_mail import get_credentials
import imaplib
import email
import datetime

class Email():
    body = None

    def __init__(self, subject = "No subject", sender = "Unknown", recipient = "Unknown", date = "00.00.0000 00:00:00"):
        self.subject = subject
        self.sender = sender
        self.recipient = recipient
        self.date = date

    def __str__(self):
        return "Date: "+self.date + "\nFrom: "+self.sender + "\nTo: "+self.recipient + "\nSubject: "+self.subject + "\n\n" + str(self.body)

def get_mails(username, password):
    host ="imap.gmail.com"
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    mail.select("inbox")

    date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y") # from this day
    _, search_data = mail.search(None, '(UNSEEN)', '(SINCE {})'.format(date)) # https://gist.github.com/martinrusev/6121028
    my_messages = [] # all messages

    for num in search_data[0].split():
        _, data = mail.fetch(num, "(RFC822)") # grab the correct message
        _,b = data[0] #[(_, b)] message in byte

        msg = email.message_from_bytes(b)
        new_email = Email(msg["subject"], msg["from"], msg["to"], msg["date"]) # message header
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode = True) # plain text content of the message
                new_email.body = body.decode()
            elif part.get_content_type() == "text/html":
                html_body = part.get_payload(decode = True)
                new_email.body = html_body.decode()
        my_messages.append(new_email)

    return my_messages

if __name__ == '__main__':
    login, password = get_credentials()
    my_mails = get_mails(login, password)
    for mail in my_mails:
        print("-----------------------------------", mail, sep="\n")
