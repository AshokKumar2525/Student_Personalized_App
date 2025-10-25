"""
Gmail Service - Handle Gmail API operations
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import base64
import email
from email.mime.text import MIMEText
import os


class GmailService:
    """Service for interacting with Gmail API"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, access_token, refresh_token=None):
        """
        Initialize Gmail service with OAuth tokens
        
        Args:
            access_token: Google access token
            refresh_token: Google refresh token (optional)
        """
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=self.SCOPES
        )
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def get_user_email(self):
        """Get the authenticated user's email address"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except HttpError as error:
            print(f"Error getting user profile: {error}")
            raise
    
    def fetch_emails(self, max_results=50, page_token=None, query=None):
        """
        Fetch emails from Gmail
        
        Args:
            max_results: Maximum number of emails to fetch
            page_token: Token for pagination
            query: Gmail search query (e.g., 'is:unread', 'after:2024/01/01')
        
        Returns:
            dict: {'emails': [...], 'next_page_token': '...'}
        """
        try:
            # Build query parameters
            params = {
                'userId': 'me',
                'maxResults': max_results,
                'labelIds': ['INBOX']  # Only inbox emails
            }
            
            if page_token:
                params['pageToken'] = page_token
            
            if query:
                params['q'] = query
            
            # Get message list
            results = self.service.users().messages().list(**params).execute()
            messages = results.get('messages', [])
            
            # Fetch full details for each message
            emails = []
            for msg in messages:
                email_data = self._get_message_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return {
                'emails': emails,
                'next_page_token': results.get('nextPageToken')
            }
        
        except HttpError as error:
            print(f"Error fetching emails: {error}")
            raise
    
    def _get_message_details(self, message_id):
        """
        Get detailed information about a specific email
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            dict: Email details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            subject = self._get_header(headers, 'Subject')
            sender = self._get_header(headers, 'From')
            date_str = self._get_header(headers, 'Date')
            
            # Parse sender
            sender_name, sender_email = self._parse_sender(sender)
            
            # Parse date
            email_date = self._parse_date(date_str)
            
            # Get snippet (preview text)
            snippet = message.get('snippet', '')
            
            # Get labels
            labels = message.get('labelIds', [])
            is_read = 'UNREAD' not in labels
            is_starred = 'STARRED' in labels
            
            # Check for attachments
            has_attachments = self._has_attachments(message['payload'])
            
            # Get thread ID
            thread_id = message.get('threadId')
            
            return {
                'message_id': message_id,
                'thread_id': thread_id,
                'subject': subject,
                'sender_name': sender_name,
                'sender_email': sender_email,
                'snippet': snippet,
                'email_date': email_date,
                'is_read': is_read,
                'is_starred': is_starred,
                'has_attachments': has_attachments,
                'labels': labels
            }
        
        except HttpError as error:
            print(f"Error getting message {message_id}: {error}")
            return None
    
    def get_message_body(self, message_id):
        """
        Get full email body (for summarization)
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            dict: {'text': '...', 'html': '...'}
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            payload = message['payload']
            
            # Extract body
            body_text = ''
            body_html = ''
            
            if 'parts' in payload:
                # Multipart message
                for part in payload['parts']:
                    mime_type = part.get('mimeType')
                    body = part.get('body', {})
                    data = body.get('data', '')
                    
                    if data:
                        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        
                        if mime_type == 'text/plain':
                            body_text += decoded
                        elif mime_type == 'text/html':
                            body_html += decoded
            else:
                # Single part message
                body = payload.get('body', {})
                data = body.get('data', '')
                
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    mime_type = payload.get('mimeType')
                    
                    if mime_type == 'text/plain':
                        body_text = decoded
                    elif mime_type == 'text/html':
                        body_html = decoded
            
            return {
                'text': body_text,
                'html': body_html
            }
        
        except HttpError as error:
            print(f"Error getting message body: {error}")
            raise
    
    def mark_as_read(self, message_id):
        """Mark an email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f"Error marking as read: {error}")
            return False
    
    def mark_as_unread(self, message_id):
        """Mark an email as unread"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f"Error marking as unread: {error}")
            return False
    
    def toggle_star(self, message_id, starred=True):
        """Add or remove star from email"""
        try:
            if starred:
                body = {'addLabelIds': ['STARRED']}
            else:
                body = {'removeLabelIds': ['STARRED']}
            
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            return True
        except HttpError as error:
            print(f"Error toggling star: {error}")
            return False
    
    def get_history_id(self):
        """Get current history ID for incremental sync"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('historyId')
        except HttpError as error:
            print(f"Error getting history ID: {error}")
            return None
    
    # Helper methods
    
    def _get_header(self, headers, name):
        """Extract specific header value"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _parse_sender(self, sender_str):
        """
        Parse sender string into name and email
        
        Example: "John Doe <john@example.com>" -> ("John Doe", "john@example.com")
        """
        if not sender_str:
            return ('', '')
        
        if '<' in sender_str and '>' in sender_str:
            name = sender_str.split('<')[0].strip().strip('"')
            email = sender_str.split('<')[1].split('>')[0].strip()
            return (name, email)
        else:
            return ('', sender_str.strip())
    
    def _parse_date(self, date_str):
        """Parse email date string to datetime"""
        if not date_str:
            return datetime.utcnow()
        
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.utcnow()
    
    def _has_attachments(self, payload):
        """Check if email has attachments"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    return True
                if 'parts' in part:
                    if self._has_attachments(part):
                        return True
        return False


def create_gmail_service(access_token, refresh_token=None):
    """Factory function to create GmailService instance"""
    return GmailService(access_token, refresh_token)