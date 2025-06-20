import os.path
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
from email.mime.text import MIMEText
import re


if __name__ == '__main__':
    service = authenticate_gmail()
    read_unread_emails(service)
