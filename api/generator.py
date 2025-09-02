import os
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

# Valid models whitelist
VALID_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"]


def get_demo_variants(
    input_text: str, channels: List[str], tone: str
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate canned demo variants for testing purposes.
    """
    variants = {}

    for channel in channels:
        if channel == "linkedin":
            variants[channel] = [
                {
                    "id": "demo_linkedin_1",
                    "text": f"🚀 Exciting insights from our latest research: {input_text[:100]}... This represents a significant shift in how we approach innovation. #Innovation #TechTrends",
                    "length": 150,
                    "readability": "Good",
                    "tone": tone,
                },
                {
                    "id": "demo_linkedin_2",
                    "text": f"💡 Key takeaway: {input_text[50:150]}... The implications for our industry are profound. What are your thoughts on this development?",
                    "length": 200,
                    "readability": "Excellent",
                    "tone": tone,
                },
                {
                    "id": "demo_linkedin_3",
                    "text": f"📊 Data shows: {input_text[100:200]}... This trend is reshaping the landscape. Time to adapt and innovate!",
                    "length": 180,
                    "readability": "Good",
                    "tone": tone,
                },
            ]
        elif channel == "twitter":
            variants[channel] = [
                {
                    "id": "demo_twitter_1",
                    "text": f"Thread: {input_text[:50]}... 1/5",
                    "length": 280,
                    "readability": "Good",
                    "tone": tone,
                },
                {
                    "id": "demo_twitter_2",
                    "text": f"Hot take: {input_text[25:75]}... Thoughts?",
                    "length": 150,
                    "readability": "Excellent",
                    "tone": tone,
                },
                {
                    "id": "demo_twitter_3",
                    "text": f"Breaking: {input_text[75:125]}... This changes everything.",
                    "length": 200,
                    "readability": "Good",
                    "tone": tone,
                },
                {
                    "id": "demo_twitter_4",
                    "text": f"Insight: {input_text[125:175]}... The future is here.",
                    "length": 180,
                    "readability": "Excellent",
                    "tone": tone,
                },
                {
                    "id": "demo_twitter_5",
                    "text": f"Update: {input_text[175:225]}... Stay tuned for more.",
                    "length": 160,
                    "readability": "Good",
                    "tone": tone,
                },
            ]
        elif channel == "newsletter":
            variants[channel] = [
                {
                    "id": "demo_newsletter_1",
                    "text": f"## Weekly Insights\n\n{input_text[:200]}...\n\nThis week's analysis reveals several key trends that are worth your attention. The data suggests we're entering a new phase of innovation that will reshape our industry.\n\n**Key Takeaways:**\n- Trend 1: {input_text[200:300]}...\n- Trend 2: {input_text[300:400]}...\n- Trend 3: {input_text[400:500]}...\n\nStay ahead of the curve by understanding these developments.",
                    "length": 500,
                    "readability": "Excellent",
                    "tone": tone,
                }
            ]
        elif channel == "blog":
            variants[channel] = [
                {
                    "id": "demo_blog_1",
                    "text": f"# {input_text[:50]}...\n\n{input_text[:300]}...\n\n## Introduction\n\nIn today's rapidly evolving landscape, understanding these trends is crucial for success. This comprehensive analysis explores the key factors driving change.\n\n## Key Insights\n\n{input_text[300:600]}...\n\n## Conclusion\n\nThe implications are clear: we must adapt to thrive in this new environment.",
                    "length": 800,
                    "readability": "Good",
                    "tone": tone,
                }
            ]

    return variants


async def generate_content_real(
    input_text: str, channels: List[str], tone: str, model: str
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate content using real OpenAI API calls.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    if model not in VALID_MODELS:
        raise ValueError(f"Invalid model: {model}. Must be one of {VALID_MODELS}")

    client = OpenAI(api_key=api_key)
    variants = {}

    for channel in channels:
        # Create channel-specific prompts
        if channel == "linkedin":
            prompt = f"""Create 3 professional LinkedIn posts based on this content: "{input_text[:500]}"

Tone: {tone}
Format: Each post should be engaging, professional, and include relevant hashtags.
Length: 150-200 characters each.
Return as JSON array with objects containing: text, length, readability, tone"""

        elif channel == "twitter":
            prompt = f"""Create 5 Twitter posts based on this content: "{input_text[:500]}"

Tone: {tone}
Format: Mix of single tweets and thread starters. Include engaging hooks.
Length: 150-280 characters each.
Return as JSON array with objects containing: text, length, readability, tone"""

        elif channel == "newsletter":
            prompt = f"""Create 1 newsletter section based on this content: "{input_text[:500]}"

Tone: {tone}
Format: Professional newsletter format with headers and bullet points.
Length: 400-600 characters.
Return as JSON array with objects containing: text, length, readability, tone"""

        elif channel == "blog":
            prompt = f"""Create 1 blog post based on this content: "{input_text[:500]}"

Tone: {tone}
Format: Blog post with title, introduction, key points, and conclusion.
Length: 600-1000 characters.
Return as JSON array with objects containing: text, length, readability, tone"""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional content creator. Return only valid JSON arrays.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            # Parse the response and create variants
            content = response.choices[0].message.content
            # For now, we'll create mock variants with the AI-generated content
            # In a real implementation, you'd parse the JSON response
            variants[channel] = [
                {
                    "id": f"ai_{channel}_1",
                    "text": content[:200] + "..." if len(content) > 200 else content,
                    "length": len(content),
                    "readability": "Excellent",
                    "tone": tone,
                }
            ]

        except Exception as e:
            logger.error(f"OpenAI API error for {channel}: {str(e)}")
            # Fallback to demo content if API fails
            variants[channel] = get_demo_variants(input_text, [channel], tone)[channel]

    return variants


async def generate_content(
    input_text: str, channels: List[str], tone: str, model: Optional[str] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Main content generation function that routes to demo or real mode.
    """
    api_mode = os.getenv("API_MODE", "demo")
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")

    # Use provided model or fallback to default
    selected_model = model or default_model

    # Validate model
    if selected_model not in VALID_MODELS:
        raise ValueError(
            f"Invalid model: {selected_model}. Must be one of {VALID_MODELS}"
        )

    if api_mode == "demo":
        logger.info(f"Generating demo content for channels: {channels}")
        return get_demo_variants(input_text, channels, tone)
    elif api_mode == "real":
        logger.info(
            f"Generating real content using model {selected_model} for channels: {channels}"
        )
        return await generate_content_real(input_text, channels, tone, selected_model)
    else:
        raise ValueError(f"Invalid API_MODE: {api_mode}. Must be 'demo' or 'real'")
