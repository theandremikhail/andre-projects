import os.path
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
from email.mime.text import MIMEText
import re


# Scope to read and send emails
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def clean_reply(text):
    # Replace multiple newlines with a single newline
    return re.sub(r'\n{2,}', '\n\n', text.strip())


def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_email_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode()
    else:
        return base64.urlsafe_b64decode(payload['body']['data']).decode()

def read_unread_emails(service):
    # Fetch latest unread message
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread", maxResults=1).execute()
    messages = results.get('messages', [])

    if not messages:
        return []

    # Get the full message + thread
    msg = messages[0]
    msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
    thread_id = msg_data['threadId']
    thread = service.users().threads().get(userId='me', id=thread_id).execute()

    # Extract subject and headers from latest message
    payload = msg_data['payload']
    headers = payload.get('headers', [])
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
    message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), '')

    # Build the full thread as context
    full_thread = []
    for message in thread['messages']:
        inner_headers = message['payload'].get('headers', [])
        inner_sender = next((h['value'] for h in inner_headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in inner_headers if h['name'] == 'Date'), '')
        body = get_email_body(message['payload'])

        if body:
            full_thread.append(f"On {date}, {inner_sender} wrote:\n{body.strip()}\n")

    conversation = "\n".join(full_thread).strip()

    print(thread_id)
    return [{
        'subject': subject,
        'from': sender,
        'body': conversation,
        'threadId': thread_id,
        'messageId': message_id  # Needed for In-Reply-To
    }]



def create_reply_message(sender, to, subject, body, thread_id=None, in_reply_to=None, references=None):
    # message = MIMEText(message_text)
    reply_html = body.replace("\n", "<br>")
    message = MIMEText(reply_html, "html")

    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
    if references:
        message['References'] = references


    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw, 'threadId': thread_id} if thread_id else {'raw': raw}

def send_email(service, to, subject, body, thread_id=None, in_reply_to=None, references=None):
    try:
        # Format the message as HTML with proper reply headers
        reply_html = body.replace("\n", "<br>")
        message = MIMEText(reply_html, "html")
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject

        # print("[DEBUG] Final email body (HTML):")
        # print(reply_html)

        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
        if references:
            message['References'] = references

        # Encode for Gmail API
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw_message}

        if thread_id:
            body['threadId'] = thread_id

        # Send the message
        sent = service.users().messages().send(userId="me", body=body).execute()
        print(f"✅ Replied in thread {thread_id} — Message ID: {sent['id']}")

    except Exception as error:
        print(f"❌ Send error: {error}")


if __name__ == '__main__':
    service = authenticate_gmail()
    read_unread_emails(service)
