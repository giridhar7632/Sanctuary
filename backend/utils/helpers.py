import json
import requests
from utils.logger import logger
from utils.config import settings
from utils.database import redis_client, openai_client, genai
from typing import Optional, Dict, Any, List

def clean_gemini_response(raw_text: str) -> dict:
    try:
        raw_text = raw_text.replace("```json\n", "").replace("\n```", "")
        
        return json.loads(raw_text)
    except Exception as e:
        logger.error(f"Error parsing JSON response: {e}")
        raise

async def get_cache_key(prefix: str, *args) -> str:
    """Generate a cache key from prefix and arguments"""
    return f"{prefix}:" + ":".join(str(arg) for arg in args)

async def cache_get(key: str) -> Optional[str]:
    """Get value from cache"""
    if not redis_client:
        return None
    try:
        return redis_client.get(key)
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
        return None

async def cache_set(key: str, value: str, ttl: int = 3600):
    """Set value in cache with TTL"""
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, value)
    except Exception as e:
        logger.warning(f"Cache set error: {e}")

async def enhanced_emotion_analysis(text: str, user_id: str) -> Dict[str, Any]:
    """Enhanced emotion analysis with caching and detailed insights"""
    # cache_key = await get_cache_key("emotion", user_id, hash(text))
    # cached_result = await cache_get(cache_key)
    
    # if cached_result:
    #     return json.loads(cached_result)

    return {
        'primary_need': 'Peace and quiet', 
        'secondary_emotions': ['Overwhelmed', 'Lonely'], 
        'stress_level': 7, 
        'recommended_duration': '30min', 
        'urgency': 'medium', 
        'wellness_category': 'burnout'
    }
    
    system_prompt = """
    You are an expert emotional wellness AI. Analyze the user's text and provide:
    1. Primary emotional need (2-4 words)
    2. Secondary emotions present
    3. Stress level (1-10)
    4. Recommended ritual duration (15min, 30min, 45min, or 60min)
    5. Urgency level (low, medium, high)
    
    Respond in JSON format only.
    """
    
    user_prompt = f"""
    Analyze this emotional state description:
    "{text}"
    
    Provide analysis in this exact JSON format:
    {{
        "primary_need": "string (2-4 words)",
        "secondary_emotions": ["emotion1", "emotion2"],
        "stress_level": number (1-10),
        "recommended_duration": "string (15min/30min/45min/60min)",
        "urgency": "string (low/medium/high)",
        "wellness_category": "string (burnout/anxiety/creative_block/etc)"
    }}
    """
    
    try:
        
        # response = await openai_client.chat.completions.create(
        #     model=settings.OPENAI_MODEL,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_prompt}
        #     ],
        #     response_format={"type": "json_object"},
        #     temperature=0.3
        # )
        
        # result = json.loads(response.choices[0].message.content)
        # # await cache_set(cache_key, json.dumps(result), ttl=1800)  # 30 min cache
        # logger.info(result)
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            system_instruction=system_prompt
        )

        response = model.generate_content(user_prompt)
        with open("response_emotion_analysis.json", "w") as f:
            json.dump(response.text, f)
        result = clean_gemini_response(response.text)
        # result = response.text
        # logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Enhanced emotion analysis error: {e}")
        # Fallback to basic analysis
        return {
            "primary_need": "emotional restoration",
            "secondary_emotions": ["fatigue"],
            "stress_level": 5,
            "recommended_duration": "30min",
            "urgency": "medium",
            "wellness_category": "general"
        }

async def intelligent_media_parsing(media_list: List[str]) -> List[Dict[str, str]]:
    """Enhanced media parsing with better accuracy and validation"""
    media_text = ", ".join(media_list)
    # cache_key = await get_cache_key("media_parse", hash(media_text))
    # cached_result = await cache_get(cache_key)
    
    # if cached_result:
    #     return json.loads(cached_result)

    return [{'type': 'book/book', 'name': 'The Ocean at the End of the Lane'}, {'type': 'music/album', 'name': 'Music for Airports'}, {'type': 'music/artist', 'name': 'Brian Eno'}]
    
    system_prompt = """
    You are an expert media cataloger. Parse natural language media references into structured data.
    
    Valid types:
    - "film/movie" for movies/films
    - "music/artist" for musicians/bands
    - "music/album" for specific albums
    - "book/book" for books
    - "tv/show" for TV series
    - "podcast" for podcasts
    
    Be intelligent about context. If someone says "The Beatles", that's "music/artist".
    If they say "Abbey Road", that's "music/album".
    
    Respond with ONLY a JSON array of objects.
    """
    
    user_prompt = f"""
    Parse this media text: "{media_text}"
    
    Examples:
    "Spirited Away, Radiohead, The Lord of the Rings" →
    [
        {{"type": "film/movie", "name": "Spirited Away"}},
        {{"type": "music/artist", "name": "Radiohead"}},
        {{"type": "book/book", "name": "The Lord of the Rings"}}
    ]
    
    Now parse the input and return JSON array only:
    """
    
    try:
        # response = await openai_client.chat.completions.create(
        #     model=settings.OPENAI_MODEL,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_prompt}
        #     ],
        #     response_format={"type": "json_object"},
        #     temperature=0.2
        # )
        
        # json_data = json.loads(response.choices[0].message.content)
        # logger.info(json_data)

        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            system_instruction=system_prompt
        )

        response = model.generate_content(user_prompt)
        with open("response_media_parsing.json", "w") as f:
            json.dump(response.text, f)
        result = clean_gemini_response(response.text)
        # logger.info(result)
        # Extract array from response
        # if isinstance(json_data, dict):
        #     logger.info("JSON data is a dictionary")
        #     for key in json_data:
        #         if isinstance(json_data[key], list):
        #             logger.info("JSON data is a list", json_data[key])
        #             result = json_data[key]
        #             break
        #     else:
        #         result = []
        # else:
        #     result = json_data if isinstance(json_data, list) else []
        
        # await cache_set(cache_key, json.dumps(result), ttl=3600)  # 1 hour cache
        return result
        
    except Exception as e:
        logger.error(f"Media parsing error: {e}")
        return []

async def enhanced_qloo_recommendations(structured_seed: List[Dict], emotional_context: Dict) -> Dict[str, str]:
    """Enhanced Qloo integration with emotional context"""
    if not structured_seed:
        return await get_fallback_recommendations(emotional_context)

    with open("structured_seed.json", "w") as f:
        json.dump(structured_seed, f)

    with open("emotional_context.json", "w") as f:
        json.dump(emotional_context, f)
    
    # cache_key = await get_cache_key("qloo", hash(str(structured_seed)), emotional_context.get("wellness_category", ""))
    # cached_result = await cache_get(cache_key)
    
    # if cached_result:
    #     return json.loads(cached_result)
    
    headers = {"Content-Type": "application/json", 'X-Api-Key': settings.QLOO_API_KEY}
    
    # Enhanced domain selection based on emotional state
    base_domains = ["music", "book", "film", "podcast"]
    if emotional_context.get("wellness_category") == "creative_block":
        domains = ["music", "book", "film"]  # Focus on inspiration
    elif emotional_context.get("urgency") == "high":
        domains = ["music", "podcast"]  # Quick access content
    else:
        domains = base_domains

    with open("domains.json", "w") as f:
        json.dump(domains, f)
    
    payload = {
        "seed": structured_seed,
        "domain": domains,
        "limit_per_domain": 2,
        "include_similar": True
    }
    
    try:
        response = requests.post(
            settings.QLOO_API_URL + '',
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        qloo_data = response.json()
        logger.info(qloo_data)
        
        recommendations = {}
        for domain in domains:
            if qloo_data.get("data", {}).get(domain):
                items = qloo_data["data"][domain][:2]  # Get top 2
                for i, item in enumerate(items):
                    rec_text = f"'{item.get('name')}'"
                    if item.get('author'):
                        rec_text += f" by {item['author']}"
                    elif item.get('artist'):
                        rec_text += f" by {item['artist']}"
                    
                    key = f"{domain}" if i == 0 else f"{domain}_alt"
                    recommendations[key] = rec_text
        
        # await cache_set(cache_key, json.dumps(recommendations), ttl=1800)
        return recommendations
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Qloo API error: {e}")
        return await get_fallback_recommendations(emotional_context)

async def get_fallback_recommendations(emotional_context: Dict) -> Dict[str, str]:
    """Intelligent fallback recommendations based on emotional context"""
    wellness_category = emotional_context.get("wellness_category", "general")
    
    fallback_db = {
        "burnout": {
            "music": "the album 'Immunity' by Jon Hopkins",
            "podcast": "the podcast 'Nothing Much Happens'",
            "book": "the book 'The Power of Now' by Eckhart Tolle"
        },
        "creative_block": {
            "music": "the album 'Music for Airports' by Brian Eno",
            "film": "the documentary 'Abstract: The Art of Design'",
            "book": "the book 'Big Magic' by Elizabeth Gilbert"
        },
        "anxiety": {
            "music": "the album 'Weightless' by Marconi Union",
            "podcast": "the podcast 'Calm'",
            "book": "the book 'Anxious Thoughts' by Katie Krimer"
        },
        "general": {
            "music": "the album 'Vespertine' by Björk",
            "film": "the movie 'My Neighbor Totoro'",
            "book": "the book 'The Midnight Library' by Matt Haig"
        }
    }
    
    return fallback_db.get(wellness_category, fallback_db["general"])

async def create_personalized_ritual(
    emotional_analysis: Dict,
    recommendations: Dict,
    user_preferences: Dict = None
) -> str:
    """Create a highly personalized ritual with advanced prompt engineering"""

    return """
    **Tonight's Ritual: A Sanctuary of Stillness**

My dear friend, I sense you're carrying a weight, a gentle hum of stress.  Let's create a space for that to melt away. This ritual is designed to ease your mind and soothe your soul.

Begin by settling into a comfortable position. Dim the lights if you like.  Let the immersive soundscapes of Jon Hopkins' *Immunity* wash over you. Allow the music's ebb and flow to mirror the rhythm of your breath, easing tension from your shoulders and jaw. (10 mins)

As the music gently fades,  we'll shift to a different kind of listening. Put on an episode of 'Nothing Much Happens'.  This podcast's gentle pace and ordinary stories offer a grounding counterpoint to the rich sounds of the music, inviting you to simply be present, without striving. (10 mins)

Finally, to deepen your sense of peace, open 'The Power of Now' by Eckhart Tolle. Read just a page or two—focus on a passage that resonates, allowing its wisdom to settle in your heart. This gentle practice connects your inner calm with insightful guidance. (10 mins)


Close your eyes, and breathe deeply.  Repeat to yourself, “I am calm. I am peaceful. I am present.”  May this quietude linger with you long after our ritual ends.
    """

    primary_need = emotional_analysis.get("primary_need", "restoration")
    duration = emotional_analysis.get("recommended_duration", "30min")
    urgency = emotional_analysis.get("urgency", "medium")
    stress_level = emotional_analysis.get("stress_level", 5)
    
    recommendations_text = "\n".join([
        f"- {domain.replace('_', ' ').title()}: {rec}" 
        for domain, rec in recommendations.items()
    ])
    
    urgency_prompts = {
        "high": "This person needs immediate relief and gentle care.",
        "medium": "This person would benefit from a thoughtful, balanced approach.",
        "low": "This person is seeking enrichment and gentle exploration."
    }
    
    system_prompt = f"""
    You are "Sanctuary," an expert AI wellness curator specializing in personalized restoration rituals.
    
    Context:
    - Emotional need: {primary_need}
    - Stress level: {stress_level}/10
    - Urgency: {urgency} ({urgency_prompts.get(urgency, '')})
    - Duration: {duration}
    
    Your writing style:
    - Warm, empathetic, and nurturing
    - Use second person ("you")
    - Be specific and actionable
    - Include gentle transitions between activities
    - Explain the "why" behind recommendations
    
    Create a ritual that feels like a caring friend's personalized recommendation.
    """
    
    user_prompt = f"""
    Based on the cultural recommendations below, create a {duration} restoration ritual:
    
    {recommendations_text}
    
    Structure your response as:
    1. A poetic title starting with "Tonight's Ritual:" or "Your Ritual:"
    2. A brief emotional acknowledgment
    3. 2-3 specific activities using the recommendations
    4. Gentle transitions between activities
    5. A closing intention or affirmation
    
    Keep it under 200 words, warm and personal.
    """
    
    try:
        # response = await openai_client.chat.completions.create(
        #     model=settings.OPENAI_MODEL,
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_prompt}
        #     ],
        #     temperature=0.8,
        #     max_tokens=300
        # )
        # logger.info(response.choices[0].message.content.strip())
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            system_instruction=system_prompt
        )

        response = model.generate_content(user_prompt)
        result = response.text
        # print(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Ritual creation error: {e}")
        return f"""Tonight's Ritual: A Moment of Peace

I sense you need some gentle restoration right now. Here's what I've prepared for you:

Begin by settling into your most comfortable space. Let yourself listen to some calming music - something that speaks to your soul in this moment. 

Take 10-15 minutes to simply be present with the sounds, letting them wash over you without any pressure to do or think anything particular.

Follow this with a few pages of reading something that nourishes your mind, or perhaps watching something beautiful and inspiring.

Remember: this time is yours. You deserve this pause, this care, this moment of sanctuary.

May you find the restoration you seek."""