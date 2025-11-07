"""
Gmail Service - Handle Gmail API operations with proper OAuth2 refresh
"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import base64
import os
import re


class GmailService:
    """Service for interacting with Gmail API with auto-refresh"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, access_token, refresh_token=None):
        """
        Initialize Gmail service with OAuth tokens
        
        Args:
            access_token: Google access token
            refresh_token: Google refresh token (REQUIRED for auto-refresh)
        """
        # Get OAuth2 credentials from environment
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment")
        
        # Create credentials with all required fields
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=self.SCOPES
        )
        
        # Refresh token if expired
        if self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
        
        self.service = build('gmail', 'v1', credentials=self.credentials)
        self.updated_token = None
    
    def get_updated_credentials(self):
        """Get updated token if it was refreshed"""
        if self.credentials.token != self.updated_token:
            return {
                'access_token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_expiry': self.credentials.expiry.isoformat() if self.credentials.expiry else None
            }
        return None
    
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
        """Get detailed information about a specific email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',  # Only get metadata for efficiency
                metadataHeaders=['Subject', 'From', 'Date']
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
            is_important = 'IMPORTANT' in labels
            
            # Check for attachments
            size_estimate = message.get('sizeEstimate', 0)
            has_attachments = size_estimate > 10000  # Rough estimate
            
            # Get thread ID
            thread_id = message.get('threadId')
            
            return {
                'message_id': message_id,
                'thread_id': thread_id,
                'subject': subject or '(No subject)',
                'sender_name': sender_name,
                'sender_email': sender_email,
                'snippet': snippet,
                'email_date': email_date,
                'is_read': is_read,
                'is_starred': is_starred,
                'is_important': is_important,
                'has_attachments': has_attachments,
                'labels': labels
            }
        
        except HttpError as error:
            print(f"Error getting message {message_id}: {error}")
            return None
    
    def get_message_body(self, message_id):
        """Get full email body (for summarization)"""
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
                    body_text, body_html = self._extract_part_body(part, body_text, body_html)
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
                'text': body_text.strip(),
                'html': body_html.strip()
            }
        
        except HttpError as error:
            print(f"Error getting message body: {error}")
            raise
    
    def _extract_part_body(self, part, body_text='', body_html=''):
        """Recursively extract body from message parts"""
        mime_type = part.get('mimeType')
        body = part.get('body', {})
        data = body.get('data', '')
        
        if data:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            if mime_type == 'text/plain':
                body_text += decoded
            elif mime_type == 'text/html':
                body_html += decoded
        
        # Recursively check nested parts
        if 'parts' in part:
            for nested_part in part['parts']:
                body_text, body_html = self._extract_part_body(nested_part, body_text, body_html)
        
        return body_text, body_html
    
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
    
    def delete_message(self, message_id):
        """Move message to trash"""
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            return True
        except HttpError as error:
            print(f"Error deleting message: {error}")
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
        """Parse sender string into name and email"""
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
    def get_message_with_attachments(self, message_id):
        """Get email with attachments and links info"""
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
            attachments = []
            
            if 'parts' in payload:
                for part in payload['parts']:
                    body_text, body_html, attachments = self._extract_parts(
                        part, body_text, body_html, attachments
                    )
            else:
                body = payload.get('body', {})
                data = body.get('data', '')
                
                if data:
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    mime_type = payload.get('mimeType')
                    
                    if mime_type == 'text/plain':
                        body_text = decoded
                    elif mime_type == 'text/html':
                        body_html = decoded
            
            # Extract links from body
            links = self._extract_links(body_text + body_html)
            # # If still no HTML but we have text, wrap it nicely
            # if not body_html and body_text:
            #     body_html = "<pre style='white-space:pre-wrap;font-family:inherit;'>" + body_text + "</pre>"

            
            return {
                'body': {
                    'text': body_text.strip(),
                    'html': body_html.strip()
                },
                'attachments': attachments,
                'links': links
            }
        
        except HttpError as error:
            print(f"Error getting message with attachments: {error}")
            raise


    def _extract_parts(self, part, body_text='', body_html='', attachments=[]):
        """Extract body, attachments recursively (supports nested MIME parts)"""
        mime_type = part.get('mimeType', '')
        filename = part.get('filename', '')
        body = part.get('body', {})
        data = body.get('data', '')

        # If it's an attachment
        if filename and body.get('attachmentId'):
            attachments.append({
                'filename': filename,
                'mimeType': mime_type,
                'size': body.get('size', 0),
                'attachmentId': body.get('attachmentId')
            })
        elif data:
            # Decode normal body data
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            if mime_type == 'text/plain':
                body_text += decoded
            elif mime_type == 'text/html':
                body_html += decoded

        # Recursively explore nested parts (for multipart/alternative, related, etc.)
        if 'parts' in part:
            for nested_part in part['parts']:
                body_text, body_html, attachments = self._extract_parts(
                    nested_part, body_text, body_html, attachments
                )

        # Handle "multipart/alternative" preference — prefer HTML over plain text
        if mime_type == 'multipart/alternative' and body_html.strip():
            # If we found an HTML version inside, prefer that
            body_text = ''
        return body_text, body_html, attachments



    def _extract_links(self, text):
        """Extract URLs from text"""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        links = url_pattern.findall(text)
        
        # Remove duplicates and limit to 10
        unique_links = list(dict.fromkeys(links))[:10]
        
        return unique_links

def create_gmail_service(access_token, refresh_token=None):
    """Factory function to create GmailService instance"""
    return GmailService(access_token, refresh_token)
