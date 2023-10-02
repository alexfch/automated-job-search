from __future__ import print_function

import base64
import os
from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GmailClient:

    def __init__(self):
        self.from_address = "bolzhelarskiy83@gmail.com"

    def _get_creds(self):
        scopes = ['https://www.googleapis.com/auth/gmail.readonly',
                  'https://www.googleapis.com/auth/gmail.compose']
        creds = None

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.getenv("GOOGLE_CREDENTIALS"), scopes)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    def send_message(self, to, subject, content):
        creds = self._get_creds()

        try:
            service = build('gmail', 'v1', credentials=creds)
            message = EmailMessage()

            message.set_content(content)

            message['To'] = to
            message['From'] = self.from_address
            message['Subject'] = subject

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
                .decode()

            create_message = {
                'raw': encoded_message
            }
            # pylint: disable=E1101
            send_message = (service.users().messages().send
                            (userId="me", body=create_message).execute())
            print(F'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
        return send_message

    def get_folders_list(self):
        creds = self._get_creds()

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            if not labels:
                print('No labels found.')
                return
            print('Labels:')
            for label in labels:
                print(label['name'])

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')
