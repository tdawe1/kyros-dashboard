import os
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
import sentry_sdk
from utils.token_storage import save_token_usage

logger = logging.getLogger(__name__)

# Valid models whitelist
VALID_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini"]


def demo_responses():
    return {
        "linkedin": [
            "💡 Want to save 4 hours a week on content? Our repurposer turns a single blog into LinkedIn-ready posts in seconds. #AI #Productivity",
            "Consistency builds trust. With our tool, one draft = weeks of content. Simple, efficient, effective.",
            "From blog to boardroom: see how automation can keep your message aligned across every platform.",
        ],
        "twitter": [
            "Turn 1 blog into 10 posts. Time saved = 4 hrs/week. #AItools #SmallBusiness",
            "Consistency is trust. Automation makes it easy. 🚀",
            "Stop staring at a blank screen. Repurpose instead.",
            "AI that works behind the scenes → more focus on what matters.",
            "One draft → multiple platforms. That's leverage.",
        ],
        "newsletter": [
            """**This week's tip: Work smarter with your content**

Most small businesses spend too long rewriting the same idea for multiple channels.
Our new tool takes one blog post and transforms it into LinkedIn updates, tweets, and even a newsletter draft.

👉 Save hours. Stay consistent. Focus on growth."""
        ],
    }


def get_demo_variants(
    input_text: str, channels: List[str], tone: str
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate canned demo variants for testing purposes.
    """
    demo_content = demo_responses()
    variants = {}

    for channel in channels:
        if channel in demo_content:
            channel_variants = []
            for i, text in enumerate(demo_content[channel], 1):
                channel_variants.append(
                    {
                        "id": f"demo_{channel}_{i}",
                        "text": text,
                        "length": len(text),
                        "readability": "Excellent",
                        "tone": tone,
                    }
                )
            variants[channel] = channel_variants
        else:
            # Fallback for unsupported channels
            variants[channel] = [
                {
                    "id": f"demo_{channel}_1",
                    "text": f"Demo content for {channel}: {input_text[:100]}...",
                    "length": 100,
                    "readability": "Good",
                    "tone": tone,
                }
            ]

    return variants


async def generate_content_real(
    input_text: str, channels: List[str], tone: str, model: str, job_id: str
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

            # Log token usage to Sentry and database
            if hasattr(response, "usage") and response.usage:
                token_usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                    "model": model,
                    "channel": channel,
                }

                # Log to Sentry for monitoring
                sentry_sdk.set_context("token_usage", token_usage)
                logger.info(f"Token usage for {channel}: {token_usage}")

                # Save token usage to storage
                save_token_usage(job_id, token_usage, model, channel)

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
            sentry_sdk.capture_exception(e)
            # Fallback to demo content if API fails
            variants[channel] = get_demo_variants(input_text, [channel], tone)[channel]

    return variants


async def generate_content(
    input_text: str,
    channels: List[str],
    tone: str,
    model: Optional[str] = None,
    job_id: Optional[str] = None,
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
        return await generate_content_real(
            input_text, channels, tone, selected_model, job_id or "unknown"
        )
    else:
        raise ValueError(f"Invalid API_MODE: {api_mode}. Must be 'demo' or 'real'")
