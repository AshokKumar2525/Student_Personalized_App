"""
Email AI Service - Categorization and Summarization
Uses Groq (fast & free) for categorization and OpenAI for summarization
"""

import os
import json
from groq import Groq
from openai import OpenAI
import re


class EmailAIService:
    """Service for AI-powered email operations"""
    
    # Available categories
    CATEGORIES = [
        'important', 'work', 'personal', 'finance', 
        'shopping', 'promotions', 'spam', 'other'
    ]
    
    def __init__(self):
        """Initialize AI clients"""
        self.groq_client = None
        self.openai_client = None
        
        # Initialize Groq if API key exists
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            try:
                self.groq_client = Groq(api_key=groq_key)
                print("✅ Groq client initialized for email service")
            except Exception as e:
                print(f"⚠️ Groq initialization failed: {e}")
                print("   Email categorization will use rule-based fallback")
        
        # Initialize OpenAI if API key exists
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                print("✅ OpenAI client initialized for email service")
            except Exception as e:
                print(f"⚠️ OpenAI initialization failed: {e}")
                print("   Summarization will use fallback methods")
    
    def categorize_email(self, subject, sender_email, snippet):
        """
        Categorize email using AI
        
        Args:
            subject: Email subject
            sender_email: Sender's email address
            snippet: Email preview text
        
        Returns:
            str: Category slug ('important', 'work', etc.)
        """
        # Rule-based quick categorization (fast path)
        quick_category = self._quick_categorize(subject, sender_email, snippet)
        if quick_category:
            return quick_category
        
        # AI categorization (if Groq is available)
        if self.groq_client:
            try:
                return self._ai_categorize(subject, sender_email, snippet)
            except Exception as e:
                print(f"AI categorization failed: {e}")
        
        # Fallback to 'other'
        return 'other'
    
    def _quick_categorize(self, subject, sender_email, snippet):
        """
        Quick rule-based categorization
        Returns category or None if uncertain
        """
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
        
        # Spam indicators
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
        
        return None  # Uncertain, needs AI
    
    def _ai_categorize(self, subject, sender_email, snippet):
        """
        AI-powered categorization using Groq
        """
        prompt = f"""Categorize this email into ONE of these categories: {', '.join(self.CATEGORIES)}

Email Details:
Subject: {subject}
From: {sender_email}
Preview: {snippet}

Reply with ONLY the category name (one word), nothing else.
Categories:
- important: Critical, urgent, time-sensitive emails
- work: Professional, job-related communications
- personal: Family, friends, personal matters
- finance: Banking, bills, invoices, transactions
- shopping: Orders, deliveries, e-commerce
- promotions: Marketing, newsletters, offers
- spam: Unwanted, suspicious emails
- other: Anything that doesn't fit above

Category:"""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast and free
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10
            )
            
            category = response.choices[0].message.content.strip().lower()
            
            # Validate response
            if category in self.CATEGORIES:
                return category
            else:
                return 'other'
        
        except Exception as e:
            print(f"Groq API error: {e}")
            return 'other'
    
    def summarize_email(self, subject, sender_name, body_text):
        """
        Generate AI summary of email
        
        Args:
            subject: Email subject
            sender_name: Sender's name
            body_text: Email body (plain text)
        
        Returns:
            dict: {
                'summary_text': str,
                'key_points': list,
                'action_items': list,
                'priority': str,
                'sentiment': str,
                'model_used': str
            }
        """
        # Truncate body if too long (save API costs)
        max_chars = 4000
        if len(body_text) > max_chars:
            body_text = body_text[:max_chars] + "..."
        
        # Try OpenAI first (better quality)
        if self.openai_client:
            try:
                return self._openai_summarize(subject, sender_name, body_text)
            except Exception as e:
                print(f"OpenAI summarization failed: {e}")
        
        # Fallback to Groq
        if self.groq_client:
            try:
                return self._groq_summarize(subject, sender_name, body_text)
            except Exception as e:
                print(f"Groq summarization failed: {e}")
        
        # Ultimate fallback
        return self._fallback_summary(subject, body_text)
    
    def _openai_summarize(self, subject, sender_name, body_text):
        """Summarize using OpenAI GPT-4o-mini"""
        prompt = f"""Summarize this email concisely.

                    Subject: {subject}
                    From: {sender_name}

                    Email:
                    {body_text}

                    Provide a JSON response with:
                    1. summary_text: 2-3 sentence summary
                    2. key_points: Array of 3-5 key bullet points
                    3. action_items: Array of specific actions needed (or empty array)
                    4. priority: "low", "medium", "high", or "urgent"
                    5. sentiment: "positive", "neutral", or "negative"

                    JSON:"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        result['model_used'] = 'gpt-4o-mini'
        
        return result
    
    def _groq_summarize(self, subject, sender_name, body_text):
        """Summarize using Groq Llama"""
        prompt = f"""Summarize this email concisely.

Subject: {subject}
From: {sender_name}

Email:
{body_text}

Provide a JSON response with:
1. summary_text: 2-3 sentence summary
2. key_points: Array of 3-5 key bullet points
3. action_items: Array of specific actions needed (or empty array)
4. priority: "low", "medium", "high", or "urgent"
5. sentiment: "positive", "neutral", or "negative"

JSON:"""

        response = self.groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Better for summarization
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Extract JSON from response (Groq might include extra text)
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            # Fallback parsing
            result = {
                'summary_text': content[:200],
                'key_points': [],
                'action_items': [],
                'priority': 'medium',
                'sentiment': 'neutral'
            }
        
        result['model_used'] = 'llama-3.1-70b'
        
        return result
    
    def _fallback_summary(self, subject, body_text):
        """Simple fallback when no AI is available"""
        # Extract first few sentences
        sentences = body_text.split('.')[:3]
        summary = '. '.join(sentences).strip() + '.'
        
        return {
            'summary_text': summary[:200],
            'key_points': [subject],
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