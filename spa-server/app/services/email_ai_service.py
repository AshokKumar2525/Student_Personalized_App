"""
Email AI Service - Using Gemini for summarization
"""

import os
import json
import re
import google.generativeai as genai


class EmailAIService:
    """Service for AI-powered email operations"""
    
    # Available categories
    CATEGORIES = [
        'important', 'work', 'personal', 'finance', 
        'shopping', 'promotions', 'spam', 'other'
    ]
    
    def __init__(self):
        """Initialize AI clients"""
        self.gemini_model = None
        
        # Initialize Gemini if API key exists
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                # Use gemini-1.5-flash for faster responses
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini initialized for email service")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                print("   Email summarization will use fallback methods")
    
    def categorize_email(self, subject, sender_email, snippet):
        """
        Categorize email using rule-based logic
        
        Args:
            subject: Email subject
            sender_email: Sender's email address
            snippet: Email preview text
        
        Returns:
            str: Category slug ('important', 'work', etc.)
        """
        # Rule-based quick categorization
        quick_category = self._quick_categorize(subject, sender_email, snippet)
        if quick_category:
            return quick_category
        
        # Default to 'other'
        return 'other'
    
    def _quick_categorize(self, subject, sender_email, snippet):
        """Quick rule-based categorization"""
        subject_lower = (subject or '').lower()
        sender_lower = (sender_email or '').lower()
        snippet_lower = (snippet or '').lower()
        
        combined = f"{subject_lower} {sender_lower} {snippet_lower}"
        
        # Finance keywords
        finance_keywords = ['invoice', 'payment', 'bank', 'transaction', 'receipt', 
                           'billing', 'card', 'account statement', 'paypal', 'stripe']
        if any(kw in combined for kw in finance_keywords):
            return 'finance'
        
        # Shopping keywords
        shopping_keywords = ['order', 'shipped', 'delivery', 'tracking', 'amazon', 
                            'ebay', 'purchase', 'cart', 'discount']
        if any(kw in combined for kw in shopping_keywords):
            return 'shopping'
        
        # Spam/Promotions indicators
        spam_keywords = ['unsubscribe', 'click here', 'limited time', 'act now', 
                        'congratulations', 'winner', 'claim your', 'viagra']
        spam_domains = ['noreply@', 'no-reply@', 'notifications@']
        if any(kw in combined for kw in spam_keywords) or any(d in sender_lower for d in spam_domains):
            return 'promotions'
        
        # Work-related
        work_keywords = ['meeting', 'deadline', 'project', 'team', 'report', 
                        'presentation', 'schedule', 'calendar']
        if any(kw in combined for kw in work_keywords):
            return 'work'
        
        return None
    
    def summarize_email(self, subject, sender_name, body_text):
        """
        Generate AI summary using Gemini
        
        Args:
            subject: Email subject
            sender_name: Sender's name
            body_text: Email body (plain text)
        
        Returns:
            dict: Summary data
        """
        # Truncate body if too long
        max_chars = 8000
        if len(body_text) > max_chars:
            body_text = body_text[:max_chars] + "..."
        
        # Try Gemini
        if self.gemini_model:
            try:
                return self._gemini_summarize(subject, sender_name, body_text)
            except Exception as e:
                print(f"Gemini summarization failed: {e}")
        
        # Fallback
        return self._fallback_summary(subject, body_text)
    
    def _gemini_summarize(self, subject, sender_name, body_text):
        """Summarize using Gemini API"""
        prompt = f"""Analyze this email and provide a concise summary.

Subject: {subject}
From: {sender_name}

Email Content:
{body_text}

Provide your response in this exact format (no markdown, no code blocks):

SUMMARY:
[2-3 sentence summary of the email]

KEY POINTS:
- [First key point]
- [Second key point]
- [Third key point]

ACTION ITEMS:
- [Action item 1 if any, or write "None"]
- [Action item 2 if any]

PRIORITY: [low/medium/high/urgent]
SENTIMENT: [positive/neutral/negative]"""

        try:
            response = self.gemini_model.generate_content(prompt)
            text = response.text
            
            # Parse the response
            summary_match = re.search(r'SUMMARY:\s*(.+?)(?=KEY POINTS:|$)', text, re.DOTALL)
            key_points_match = re.search(r'KEY POINTS:\s*(.+?)(?=ACTION ITEMS:|$)', text, re.DOTALL)
            action_items_match = re.search(r'ACTION ITEMS:\s*(.+?)(?=PRIORITY:|$)', text, re.DOTALL)
            priority_match = re.search(r'PRIORITY:\s*(\w+)', text)
            sentiment_match = re.search(r'SENTIMENT:\s*(\w+)', text)
            
            # Extract and clean data
            summary_text = summary_match.group(1).strip() if summary_match else text[:200]
            
            # Extract key points
            key_points = []
            if key_points_match:
                points_text = key_points_match.group(1)
                key_points = [
                    p.strip().lstrip('- •*').strip() 
                    for p in points_text.split('\n') 
                    if p.strip() and p.strip() not in ['', '-', '•', '*']
                ][:5]  # Max 5 points
            
            # Extract action items
            action_items = []
            if action_items_match:
                actions_text = action_items_match.group(1)
                action_items = [
                    a.strip().lstrip('- •*').strip() 
                    for a in actions_text.split('\n') 
                    if a.strip() and a.strip().lower() not in ['', '-', '•', '*', 'none', 'n/a']
                ][:5]  # Max 5 actions
            
            priority = priority_match.group(1).lower() if priority_match else 'medium'
            sentiment = sentiment_match.group(1).lower() if sentiment_match else 'neutral'
            
            # Validate priority and sentiment
            if priority not in ['low', 'medium', 'high', 'urgent']:
                priority = 'medium'
            if sentiment not in ['positive', 'neutral', 'negative']:
                sentiment = 'neutral'
            
            return {
                'summary_text': summary_text,
                'key_points': key_points,
                'action_items': action_items,
                'priority': priority,
                'sentiment': sentiment,
                'model_used': 'gemini-pro'
            }
            
        except Exception as e:
            print(f"Gemini parsing error: {e}")
            raise
    
    def _fallback_summary(self, subject, body_text):
        """Simple fallback when AI is not available"""
        # Extract first few sentences
        sentences = body_text.split('.')[:3]
        summary = '. '.join(s.strip() for s in sentences if s.strip()).strip()
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return {
            'summary_text': summary[:300] if summary else subject[:200],
            'key_points': [subject] if subject else [],
            'action_items': [],
            'priority': 'medium',
            'sentiment': 'neutral',
            'model_used': 'fallback'
        }


# Singleton instance
_ai_service = None

def get_ai_service():
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = EmailAIService()
    return _ai_service