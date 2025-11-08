"""
YouTube Video Search Service - FIXED
Fetches relevant educational videos using YouTube Data API v3
"""

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
import time

class YouTubeService:
    """Service for searching educational YouTube videos"""
    
    def __init__(self):
        """Initialize YouTube API client"""
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        print("🔑 Initializing YouTubeService with API Key")
        if not self.api_key:
            print("⚠️ YOUTUBE_API_KEY not found in environment variables")
            self.youtube = None
        else:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                print("✅ YouTube API initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize YouTube API: {e}")
                self.youtube = None
    
    def search_videos(
        self,
        query: str,
        max_results: int = 3,
        difficulty: str = 'beginner'
    ) -> List[Dict[str, str]]:
        """
        Search for educational YouTube videos
        
        Args:
            query: Search query (e.g., "Python functions tutorial")
            max_results: Number of videos to return (default: 3)
            difficulty: Difficulty level to filter results
            
        Returns:
            List of video dictionaries with title, url, duration, views
        """
        if not self.youtube:
            print("⚠️ YouTube API not available, returning curated fallback")
            return self._get_curated_fallback_videos(query, max_results)
        
        try:
            # Enhance query with educational keywords
            enhanced_query = self._enhance_query(query, difficulty)
            
            print(f"🔍 Searching YouTube for: {enhanced_query}")
            
            # Search for videos
            search_response = self.youtube.search().list(
                q=enhanced_query,
                part='id,snippet',
                maxResults=max_results * 2,  # Get more to filter
                type='video',
                videoDefinition='any',
                videoDuration='medium',  # 4-20 minutes
                relevanceLanguage='en',
                safeSearch='strict',
                order='relevance'
            ).execute()
            
            video_ids = []
            for item in search_response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_ids.append(item['id']['videoId'])
            
            if not video_ids:
                print("⚠️ No videos found, returning curated fallback")
                return self._get_curated_fallback_videos(query, max_results)
            
            # Get video details (duration, views, etc.)
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video = self._parse_video_data(item)
                if video and self._is_educational(video):
                    videos.append(video)
                    if len(videos) >= max_results:
                        break
            
            print(f"✅ Found {len(videos)} relevant videos")
            
            # If we didn't get enough videos, add curated fallback
            if len(videos) < max_results:
                fallback_count = max_results - len(videos)
                videos.extend(self._get_curated_fallback_videos(query, fallback_count))
            
            return videos[:max_results]
            
        except HttpError as e:
            print(f"❌ YouTube API error: {e}")
            if 'quotaExceeded' in str(e):
                print("⚠️ YouTube API quota exceeded, using curated fallback")
            elif 'forbidden' in str(e).lower() or '403' in str(e):
                print("⚠️ YouTube API access forbidden (Android app restriction), using curated fallback")
            return self._get_curated_fallback_videos(query, max_results)
            
        except Exception as e:
            print(f"❌ Error searching YouTube: {e}")
            return self._get_curated_fallback_videos(query, max_results)
    
    def _enhance_query(self, query: str, difficulty: str) -> str:
        """Enhance search query with educational keywords"""
        # Add tutorial keywords
        keywords = ['tutorial', 'course', 'learn']
        
        # Add difficulty-specific terms
        if difficulty == 'beginner':
            keywords.extend(['beginner', 'basics', 'introduction'])
        elif difficulty == 'intermediate':
            keywords.extend(['intermediate', 'practical'])
        elif difficulty == 'advanced':
            keywords.extend(['advanced', 'deep dive'])
        
        # Check if query already has educational terms
        query_lower = query.lower()
        has_educational_term = any(term in query_lower for term in keywords)
        
        if not has_educational_term:
            return f"{query} tutorial"
        
        return query
    
    def _parse_video_data(self, item: Dict) -> Optional[Dict[str, str]]:
        """Parse video data from API response"""
        try:
            video_id = item['id']
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            
            return {
                'title': snippet['title'],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'video_id': video_id,
                'channel': snippet['channelTitle'],
                'views': int(statistics.get('viewCount', 0)),
                'likes': int(statistics.get('likeCount', 0)),
                'duration': item.get('contentDetails', {}).get('duration', 'PT0S'),
                'thumbnail': snippet['thumbnails'].get('high', {}).get('url', ''),
                'published_at': snippet['publishedAt']
            }
        except Exception as e:
            print(f"⚠️ Error parsing video data: {e}")
            return None
    
    def _is_educational(self, video: Dict) -> bool:
        """Filter for educational content"""
        # Filter by minimum views (indicates quality)
        if video['views'] < 500:
            return False
        
        # Filter by title keywords (avoid clickbait)
        title_lower = video['title'].lower()
        
        # Exclude certain patterns
        exclude_patterns = [
            'reaction', 'drama', 'gossip', 'vlog', 'unboxing',
            'challenge', 'prank', 'meme', 'funny moments'
        ]
        
        if any(pattern in title_lower for pattern in exclude_patterns):
            return False
        
        # Prefer educational channels/terms
        educational_terms = [
            'tutorial', 'course', 'learn', 'guide', 'introduction',
            'programming', 'coding', 'development', 'explained',
            'fundamentals', 'basics', 'crash course', 'how to'
        ]
        
        has_educational = any(term in title_lower for term in educational_terms)
        
        return has_educational
    
    def _get_curated_fallback_videos(self, query: str, count: int = 3) -> List[Dict[str, str]]:
        """
        Return curated educational video IDs as fallback
        These are high-quality educational channels' popular videos
        """
        # Map of topics to curated video IDs from trusted educational channels
        curated_videos = {
            # Programming Languages
            'python': ['rfscVS0vtbw', '_uQrJ0TkZlc', 'kqtD5dpn9C8'],
            'java': ['eIrMbAQSU34', 'grEKMHGYyns', 'A74TOX803D0'],
            'javascript': ['PkZNo7MFNFg', 'W6NZfCO5SIk', 'hdI2bqOjy3c'],
            'c++': ['vLnPwxZdW4Y', '8jLOx1hD3_o', 'ZzaPdXTrSb8'],
            
            # Web Development
            'web': ['pQN-pnXPaVg', 'yfoY53QXEnI', 'PkZNo7MFNFg'],
            'html': ['pQN-pnXPaVg', 'UB1O30fR-EE', 'qz0aGYrrlhU'],
            'css': ['yfoY53QXEnI', '1Rs2ND1ryYc', 'Qhaz36TZG5Y'],
            'react': ['Ke90Tje7VS0', 'w7ejDZ8SWv8', 'bMknfKXIFA8'],
            'node': ['TlB_eWDSMt4', 'fBNz5xF-Kx4', 'Oe421EPjeBE'],
            
            # Mobile Development
            'flutter': ['VPvVD8t02U8', 'x0uinJvhNxI', '1ukSR1GRtMU'],
            'android': ['fis26HvvDII', 'aS__9RbCyHg', 'Iz08OTTjR04'],
            'kotlin': ['F9UC9DY-vIU', 'EExSSotojVI', 'I6rkwJed-HY'],
            
            # AI & ML
            'ai': ['JMUxmLyrhSk', 'aircAruvnKk', 'tPYj3fFJGjk'],
            'machine learning': ['JMUxmLyrhSk', 'i_LwzRVP7bg', 'PPLop4L2eGk'],
            'tensorflow': ['tPYj3fFJGjk', 'MotG3XI2qSs', 'tZt6gRlRcgk'],
            'pytorch': ['c36lUUr864M', 'IC0_FRiX-sw', 'Z_ikDlimN6A'],
            
            # Quantum Computing (NEW)
            'quantum': ['SN2qvy8ChJc', 'X2q2PVl63mE', 'JhHMJCUmq28'],
            'quantum computing': ['SN2qvy8ChJc', 'X2q2PVl63mE', 'JhHMJCUmq28'],
            'qubit': ['X2q2PVl63mE', 'SN2qvy8ChJc', '7B1llCxVdkE'],
            'qiskit': ['pto1tdCGZNs', 'a1NZC5rqQD8', 'RrUTwq5jKM4'],
            
            # Data Science
            'data science': ['ua-CiDNNj30', 'LHBE6Q9XlzI', 'r-uOLxNrNk8'],
            'pandas': ['vmEHCJofslg', 'ZyhVh-qRZPA', 'PcvsOaixUh8'],
            'numpy': ['QUT1VHiLmmI', 'GB9ByFAIAH4', '8Mpc9ukltVA'],
            
            # Databases
            'sql': ['HXV3zeQKqGY', '7S_tz1z_5bA', '9Pzj7Aj25lw'],
            'mongodb': ['c2M-rlkkT5o', 'ExcRbA7fy_A', '2QQGWYe7IDU'],
            'postgresql': ['qw--VYLpxG4', 'SpfIwlAYaKk', 'eMIxuk0nOkU'],
            
            # DevOps & Cloud
            'docker': ['fqMOX6JJhGo', 'pg19Z8LL06w', '3c-iBn73dDE'],
            'kubernetes': ['X48VuDVv0do', 'PH-2FfFD2PU', 's_o8dwzRlu4'],
            'aws': ['ulprqHHWlng', 'k1RI5locZE4', '3hLmDS179YE'],
            
            # Development Tools
            'git': ['RGOj5yH7evk', 'DVRQoVRzMIY', 'HVsySz-h9r4'],
            'setup': ['8jLOx1hD3_o', 'rfscVS0vtbw', 'fis26HvvDII'],
            'environment': ['8jLOx1hD3_o', 'rfscVS0vtbw', 'fis26HvvDII'],
            'installation': ['8jLOx1hD3_o', 'rfscVS0vtbw', 'fis26HvvDII'],
            
            # General Programming Concepts
            'oop': ['pTB0EiLXUC8', 'SiBw7os-_zI', 'XgfhE_lkF7E'],
            'algorithm': ['8hly31xKli0', 'KEEKn7Me-ms', '9BW6JkF-0xM'],
            'data structures': ['RBSGKlAvoiM', '8hly31xKli0', 'zg9ih6SVACc'],
        }
        
        # Try to find matching curated videos
        query_lower = query.lower()
        video_ids = []
        
        # ✅ FIX: Better matching logic - prioritize longer, more specific matches
        matches = []
        for topic, ids in curated_videos.items():
            if topic in query_lower:
                # Score by topic length (longer = more specific)
                score = len(topic)
                matches.append((score, topic, ids))
        
        # Sort by score (highest first) and take best match
        if matches:
            matches.sort(reverse=True, key=lambda x: x[0])
            best_match = matches[0]
            video_ids = best_match[2][:count]
            print(f"✅ Using curated videos for topic: {best_match[1]}")
        
        # If no exact match, try word-level matching with scoring
        if not video_ids:
            word_matches = []
            for topic, ids in curated_videos.items():
                topic_words = set(topic.lower().split())
                query_words = set(query_lower.split())
                common_words = topic_words.intersection(query_words)
                
                if common_words:
                    # Score by number of matching words and topic specificity
                    score = len(common_words) * len(topic)
                    word_matches.append((score, topic, ids))
            
            if word_matches:
                word_matches.sort(reverse=True, key=lambda x: x[0])
                best_match = word_matches[0]
                video_ids = best_match[2][:count]
                print(f"✅ Using curated videos for related topic: {best_match[1]}")
        
        # If still no match, try to infer from query context
        if not video_ids:
            # Check for programming language keywords
            if any(lang in query_lower for lang in ['java', 'jdk', 'jvm', 'spring']):
                video_ids = curated_videos['java'][:count]
                print(f"✅ Using curated videos for inferred topic: java")
            elif any(word in query_lower for word in ['python', 'django', 'flask', 'py']):
                video_ids = curated_videos['python'][:count]
                print(f"✅ Using curated videos for inferred topic: python")
            elif any(word in query_lower for word in ['javascript', 'js', 'node', 'npm']):
                video_ids = curated_videos['javascript'][:count]
                print(f"✅ Using curated videos for inferred topic: javascript")
            elif any(word in query_lower for word in ['quantum', 'qubit', 'qiskit']):
                # For quantum topics, use AI/ML videos as closest match
                video_ids = curated_videos.get('ai', ['JMUxmLyrhSk', 'aircAruvnKk', 'tPYj3fFJGjk'])[:count]
                print(f"✅ Using curated videos for quantum computing (AI/ML category)")
            else:
                # Use diverse general videos based on query type
                if 'setup' in query_lower or 'install' in query_lower or 'environment' in query_lower:
                    video_ids = curated_videos['setup'][:count]
                    print(f"✅ Using curated videos for: setup/installation")
                elif 'algorithm' in query_lower or 'data structure' in query_lower:
                    video_ids = curated_videos['algorithm'][:count]
                    print(f"✅ Using curated videos for: algorithms")
                else:
                    # Truly generic fallback
                    video_ids = [
                        'eIrMbAQSU34',  # Java (most requested)
                        'rfscVS0vtbw',  # Python
                        'PkZNo7MFNFg',  # JavaScript
                    ][:count]
                    print(f"✅ Using general programming videos as fallback")
        
        # Convert to proper format
        videos = []
        for i, video_id in enumerate(video_ids[:count]):
            videos.append({
                'title': f"{query} - Tutorial {i+1}",
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'video_id': video_id,
                'channel': 'Educational Channel',
                'views': 100000,
                'likes': 5000,
                'duration': 'PT20M',
                'thumbnail': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                'published_at': ''
            })
        
        return videos
    
    def batch_search(
        self,
        queries: List[str],
        max_results_per_query: int = 2,
        delay: float = 0.5
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Search for multiple queries with rate limiting
        
        Args:
            queries: List of search queries
            max_results_per_query: Videos per query
            delay: Delay between requests (seconds)
            
        Returns:
            Dictionary mapping queries to video lists
        """
        results = {}
        
        for query in queries:
            results[query] = self.search_videos(query, max_results_per_query)
            time.sleep(delay)  # Rate limiting
        
        return results


# Singleton instance
_youtube_service = None

def get_youtube_service() -> YouTubeService:
    """Get or create YouTube service instance"""
    global _youtube_service
    if _youtube_service is None:
        _youtube_service = YouTubeService()
    return _youtube_service