from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
from src.ai_processing.gatekeeper import AIGatekeeper
from src.database.vector_manager import VectorManager
from src.ingestion.news_scraper import NewsScraper
from src.ingestion.youtube_scraper import YouTubeScraper
import urllib.parse
import json
import datetime
from email.utils import parsedate_to_datetime

router = APIRouter()
gatekeeper = AIGatekeeper()
db = VectorManager()

BANNED_WORDS = {
    # Explicit and Mature
    "porn", "sexy", "erotic", "nudity", "strip", "dating app", "hookup", "incest", "rape", "assault", "fetish", "nsfw",
    # Violence and Crime
    "murder", "homicide", "suicide", "kill", "stab", "shoot", "bloody", "gore", "terrorist", "bombing", "hostage", "torture", "execution", "cartel",
    # Substance Abuse
    "cocaine", "heroin", "meth", "fentanyl", "weed", "marijuana", "vape", "juul", "alcohol", "drunk", "overdose", "psychedelic", "dealer",
    # Cyberbullying, Hate Speech & Privacy
    "slurs", "hate group", "neo-nazi", "white supremacist", "dox", "harass", "extortion", "blackmail", "scam", "phishing",
    "juvenile detention", "school strike", "campus incident", "student arrested", "test scores leaked", "disciplinary suspension"
}

class StudentProfile(BaseModel):
    grade_level: str
    target_career: str
    favorite_subjects: List[str]
    hobbies: List[str]

def check_banned(profile: StudentProfile):
    all_inputs = profile.favorite_subjects + profile.hobbies + [profile.target_career]
    for text in all_inputs:
        if any(b in text.lower() for b in BANNED_WORDS):
            raise HTTPException(status_code=403, detail="Inappropriate content blocked.")

def get_core_subjects(profile: StudentProfile):
    core_subjects = set([s.strip() for s in profile.favorite_subjects])
    career_lower = profile.target_career.lower()
    
    if any(k in career_lower for k in ["doctor", "medical", "neet", "mbbs"]):
        core_subjects.update(["Biology", "Physics", "Chemistry"])
    elif any(k in career_lower for k in ["engineer", "btech", "jee", "architect"]):
        core_subjects.update(["Mathematics", "Physics", "Chemistry", "Math", "Maths"])
    elif any(k in career_lower for k in ["commerce", "ca", "accountant", "business"]):
        core_subjects.update(["Accountancy", "Business Studies", "Economics"])
    return list(core_subjects)

def fast_filter(career_lower, items):
    is_medical = any(k in career_lower for k in ["doctor", "medical", "neet", "mbbs"])
    is_engineer = any(k in career_lower for k in ["engineer", "btech", "jee", "architect"])
    
    math_banned = ["math", "calculus", "algebra", "geometry", "trigonometry", "jee"]
    bio_banned = ["biology", "anatomy", "zoology", "botany", "medical", "neet"]
    
    filtered = []
    for item in items:
        text = (item.get("title", "") + " " + item.get("description", "") + " " + item.get("subject", "")).lower()
        if is_medical and any(b in text for b in math_banned): continue
        if is_engineer and any(b in text for b in bio_banned): continue
        filtered.append(item)
    return filtered

def deduplicate(items, max_count=5):
    seen_titles = set()
    distinct_results = []
    for r in items:
        title = r.get("title", "")
        if title not in seen_titles:
            seen_titles.add(title)
            distinct_results.append(r)
            if len(distinct_results) >= max_count:
                break
    return distinct_results

@router.post("/api/news")
async def get_news(profile: StudentProfile):
    check_banned(profile)
    
    async def fetch_rss(query, category, limit=10):
        if not query: return []
        q_encoded = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={q_encoded}&hl=en-US&gl=US&ceid=US:en"
        articles = await asyncio.to_thread(NewsScraper([rss_url], banned_words=BANNED_WORDS).fetch_latest_news)
        for a in articles[:limit]: a['category'] = category
        return articles[:limit]
        
    tasks = []
    
    # 1. Fetch advanced news for EACH favorite subject
    for sub in profile.favorite_subjects:
        tasks.append(fetch_rss(
            f'"{sub}" (olympiad OR competition OR breakthrough OR discovery OR education) when:2d', 
            f"Subject: {sub}", 6
        ))
        
    # 2. Fetch career news
    if profile.target_career:
        tasks.append(fetch_rss(
            f'"{profile.target_career}" (career OR industry OR breakthrough OR future) when:2d', 
            f"Career: {profile.target_career}", 6
        ))
        
    # 3. Fetch hobby news
    for hob in profile.hobbies:
        if hob.strip():
            tasks.append(fetch_rss(
                f'"{hob}" (hobby OR competition OR tutorial) when:2d',
                f"Hobby: {hob}", 4
            ))
            
    # 4. General Knowledge
    tasks.append(fetch_rss('"Science Discoveries" OR "Technology Advancements" when:2d', "General Knowledge", 4))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    articles = []
    for r in results:
        if not isinstance(r, Exception) and isinstance(r, list):
            articles.extend(r)
            
    now_date = datetime.datetime.now(datetime.timezone.utc).date()
    valid_articles = []
    for art in articles:
        try:
            pub_dt = parsedate_to_datetime(art["published"])
            if pub_dt.date() == now_date:
                art["_ts"] = pub_dt.timestamp()
                valid_articles.append(art)
        except Exception:
            pass
            
    valid_articles.sort(key=lambda x: x.get("_ts", 0), reverse=True)
    
    dynamic_news = []
    for art in valid_articles:
        dynamic_news.append({
            "title": art["title"],
            "link": art["link"],
            "published": art["published"],
            "subject": art.get("category", "News"),
            "grade_level": profile.grade_level,
            "distance": 0.001
        })
        
    final_news = fast_filter(profile.target_career.lower(), dynamic_news)
    final_news = deduplicate(final_news, 15)
    
    if final_news:
        final_news = await asyncio.to_thread(
            gatekeeper.filter_materials, final_news, profile.target_career, profile.favorite_subjects, profile.grade_level
        )
        
    return deduplicate(final_news, 10)

@router.post("/api/courses")
async def get_courses(profile: StudentProfile):
    check_banned(profile)
    # Generate module-specific embedding
    persona_text = f"Best foundational academic courses for a {profile.grade_level} student aiming to be a {profile.target_career}, focusing on {', '.join(profile.favorite_subjects)}."
    emb = await asyncio.to_thread(gatekeeper.generate_embedding, persona_text)
    if not emb: raise HTTPException(status_code=500, detail="Embedding failed.")
    
    core_subjects = get_core_subjects(profile)
    filters = {"subject": core_subjects} if core_subjects else {}
    
    raw = db.search("courses", query_embedding=emb, top_k=10, filters=filters, max_distance=1.10)
    
    # Dynamically fetch YouTube courses for EVERY favorite subject
    scraper = YouTubeScraper(banned_words=BANNED_WORDS)
    yt_tasks = [asyncio.to_thread(scraper.fetch_videos, f"{sub} full course tutorial {profile.grade_level}", 3) for sub in profile.favorite_subjects]
    yt_results = await asyncio.gather(*yt_tasks, return_exceptions=True)
    
    yt_courses = []
    for res in yt_results:
        if isinstance(res, list): yt_courses.extend(res)
            
    combined = yt_courses + raw
    filtered = fast_filter(profile.target_career.lower(), combined)
    filtered = deduplicate(filtered, 10)
    
    if filtered:
        filtered = await asyncio.to_thread(
            gatekeeper.filter_materials, filtered, profile.target_career, profile.favorite_subjects, profile.grade_level
        )
    return deduplicate(filtered, 8)

@router.post("/api/competitive")
async def get_competitive(profile: StudentProfile):
    check_banned(profile)
    nep_mapping = await asyncio.to_thread(
        gatekeeper.analyze_nep_and_exams, profile.target_career, profile.grade_level, profile.favorite_subjects
    )
    comp_exam_str = nep_mapping.get("competitive_exam", profile.target_career)
    
    # Generate module-specific embedding
    persona_text = f"Preparation materials and practice tests for {comp_exam_str} for a {profile.grade_level} student."
    emb = await asyncio.to_thread(gatekeeper.generate_embedding, persona_text)
    if not emb: raise HTTPException(status_code=500, detail="Embedding failed.")
    
    core_subjects = get_core_subjects(profile)
    filters = {"subject": core_subjects} if core_subjects else {}
    
    raw = db.search("competitive", query_embedding=emb, top_k=10, filters=filters, max_distance=1.10)
    
    # Dynamically fetch YouTube competitive exam prep
    scraper = YouTubeScraper(banned_words=BANNED_WORDS)
    yt_tasks = [
        asyncio.to_thread(scraper.fetch_videos, f"{comp_exam_str} preparation strategy", 3),
        asyncio.to_thread(scraper.fetch_videos, f"{comp_exam_str} previous year questions", 3)
    ]
    for sub in profile.favorite_subjects:
        yt_tasks.append(asyncio.to_thread(scraper.fetch_videos, f"{comp_exam_str} {sub} important topics", 2))
        
    yt_results = await asyncio.gather(*yt_tasks, return_exceptions=True)
    yt_comp = []
    for res in yt_results:
        if isinstance(res, list): yt_comp.extend(res)
            
    combined = yt_comp + raw
    filtered = fast_filter(profile.target_career.lower(), combined)
    filtered = deduplicate(filtered, 10)
    
    if filtered:
        filtered = await asyncio.to_thread(
            gatekeeper.filter_materials, filtered, profile.target_career, profile.favorite_subjects, profile.grade_level
        )
    return deduplicate(filtered, 8)

@router.post("/api/leisure")
async def get_leisure(profile: StudentProfile):
    check_banned(profile)
    
    # Dynamically fetch YouTube videos for EVERY hobby
    scraper = YouTubeScraper(banned_words=BANNED_WORDS)
    yt_tasks = [asyncio.to_thread(scraper.fetch_videos, f"{hob} tips for beginners", 4) for hob in profile.hobbies if hob.strip()]
    yt_results = await asyncio.gather(*yt_tasks, return_exceptions=True)
    
    yt_leisure = []
    for res in yt_results:
        if isinstance(res, list): yt_leisure.extend(res)
        
    # Get local FAISS data for all hobbies
    raw_faiss = []
    for hob in profile.hobbies:
        if not hob.strip(): continue
        emb = await asyncio.to_thread(gatekeeper.generate_embedding, f"Relaxing leisure activities related to {hob}")
        if emb:
            raw_faiss.extend(db.search("leisure", query_embedding=emb, top_k=5, filters={}, max_distance=1.10))
    
    combined = yt_leisure + raw_faiss
    filtered = fast_filter(profile.target_career.lower(), combined)
    return deduplicate(filtered, 8)
