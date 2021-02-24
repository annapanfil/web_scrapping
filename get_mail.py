from send_mail import get_credentials
import imaplib
import email
import datetime

def get_mails(username, password):
    host ="imap.gmail.com"
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    mail.select("inbox")

    date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y") # from this day
    _, search_data = mail.search(None, '(UNSEEN)', '(SINCE {})'.format(date)) # https://gist.github.com/martinrusev/6121028
    my_messages = [] # all messages

    for num in search_data[0].split():
        email_data = {} # content of our message
        _, data = mail.fetch(num, "(RFC822)") # grab the correct message
        _,b = data[0] #[(_, b)] message in byte

        msg = email.message_from_bytes(b)
        for header in ["subject", "to", "from", "date"]:     # print a message header
            print("{}: {}".format(header, msg[header]))
            email_data["header"] = msg["header"]
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode = True) # plain text content of the message
                print(body)
                email_data["body"] = body
            elif part.get_content_type() == "text/html":
                 html_body = part.get_payload(decode = True)
                 print(html_body.decode())
                 email_data["html_body"] = html_body
        my_messages.append(email_data)

    return my_messages

if __name__ == '__main__':
    login, password = get_credentials()
    my_mails = get_mails(login, password)
