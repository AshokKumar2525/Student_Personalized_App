import requests
from bs4 import BeautifulSoup
from serapi import GoogleSearch

def fetch_youtube_resources(query, max_results=3):
    """Fetch YouTube videos using SerpAPI."""
    params = {
        "q": query,
        "engine": "youtube",
        "api_key": "YOUR_SERPAPI_KEY"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return [{
        "title": video["title"],
        "url": video["link"],
        "type": "video"
    } for video in results.get("video_results", [])[:max_results]]

def fetch_udemy_courses(query, max_results=2):
    """Fetch Udemy courses (requires Affiliate API)."""
    # Note: Udemy's API requires approval. Use web scraping as fallback.
    url = f"https://www.udemy.com/api-2.0/courses/?search={query}"
    headers = {"Authorization": "Basic YOUR_UDEMY_API_KEY"}
    response = requests.get(url, headers=headers)
    courses = response.json().get("results", [])
    return [{
        "title": course["title"],
        "url": course["url"],
        "type": "course"
    } for course in courses[:max_results]]

def fetch_official_docs(query):
    """Fetch official documentation (e.g., Flask, React docs)."""
    # Example: Scrape devdocs.io or official sites
    url = f"https://devdocs.io/#q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # Extract relevant links (simplified)
    return [{
        "title": "Official Documentation",
        "url": url,
        "type": "documentation"
    }]

def curate_resources(module_title, module_description):
    """Combine all sources to curate resources for a module."""
    query = f"{module_title} {module_description} tutorial"
    resources = (
        fetch_youtube_resources(query) +
        fetch_udemy_courses(query) +
        fetch_official_docs(query)
    )
    return resources



## routes
from agents.resource_curator import curate_resources

@app.route("/api/modules/<int:module_id>/resources", methods=["GET"])
def get_module_resources(module_id):
    module = PathModule.query.get(module_id)
    if not module.resources:  # Only curate if empty
        resources = curate_resources(module.title, module.description)
        for res in resources:
            db_resource = ModuleResource(
                module_id=module_id,
                title=res["title"],
                url=res["url"],
                type=res["type"]
            )
            db.session.add(db_resource)
        db.session.commit()
    return jsonify([{
        "id": r.id,
        "title": r.title,
        "url": r.url,
        "type": r.type.value
    } for r in module.resources])
