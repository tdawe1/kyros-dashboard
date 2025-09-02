import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from ...core.openai_client import get_openai_client, OpenAIError
from ...core.logging import get_job_logger
from ...utils.token_storage import save_token_usage

logger = logging.getLogger(__name__)
job_logger = get_job_logger()


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
    Generate demo variants for the specified channels.
    """
    demo_data = demo_responses()
    variants = {}
    current_utc = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    for channel in channels:
        if channel in demo_data:
            # Convert demo strings to variant objects
            channel_variants = []
            for i, content in enumerate(demo_data[channel]):
                variant = {
                    "id": f"demo_{channel}_{i+1}",
                    "content": content,
                    "channel": channel,
                    "tone": tone,
                    "word_count": len(content.split()),
                    "character_count": len(content),
                    "created_at": current_utc,
                }
                channel_variants.append(variant)
            variants[channel] = channel_variants
        else:
            # Fallback for unknown channels
            variants[channel] = [
                {
                    "id": f"demo_{channel}_1",
                    "content": f"Demo content for {channel} channel in {tone} tone.",
                    "channel": channel,
                    "tone": tone,
                    "word_count": 8,
                    "character_count": 50,
                    "created_at": current_utc,
                }
            ]

    return variants


async def generate_content_real(
    input_text: str, channels: List[str], tone: str, model: str, job_id: str
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate real content using OpenAI API.
    """
    client = get_openai_client()
    variants = {}
    current_utc = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    for channel in channels:
        # Channel-specific prompts
        prompts = {
            "linkedin": f"""Transform this content into 3 LinkedIn posts in a {tone} tone:

{input_text}

Requirements:
- Professional but engaging
- Include relevant hashtags
- 150-300 words per post
- Each post should have a clear call-to-action""",
            "twitter": f"""Transform this content into 5 Twitter posts in a {tone} tone:

{input_text}

Requirements:
- Concise and punchy
- Under 280 characters each
- Include relevant hashtags
- Each tweet should be standalone but related""",
            "newsletter": f"""Transform this content into a newsletter section in a {tone} tone:

{input_text}

Requirements:
- Engaging and informative
- 200-400 words
- Include a clear value proposition
- End with a call-to-action""",
        }

        prompt = prompts.get(
            channel,
            f"Transform this content for {channel} in a {tone} tone:\n\n{input_text}",
        )

        try:
            response = client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional content repurposer. Create engaging, platform-appropriate content that maintains the original message while adapting to the specific channel's format and audience.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=model,
                max_tokens=1000,
                temperature=0.7,
                job_id=job_id,
                tool_name="repurposer",
            )

            # Parse the response and create variants
            content = response["content"]
            channel_variants = []

            # Split content by common separators and create variants
            if channel == "twitter":
                # Split by line breaks for Twitter
                posts = [post.strip() for post in content.split("\n") if post.strip()]
                for i, post in enumerate(posts[:5]):  # Limit to 5 tweets
                    variant = {
                        "id": f"{job_id}_{channel}_{i+1}",
                        "content": post,
                        "channel": channel,
                        "tone": tone,
                        "word_count": len(post.split()),
                        "character_count": len(post),
                        "created_at": current_utc,
                    }
                    channel_variants.append(variant)
            else:
                # For LinkedIn and newsletter, create single variant
                variant = {
                    "id": f"{job_id}_{channel}_1",
                    "content": content,
                    "channel": channel,
                    "tone": tone,
                    "word_count": len(content.split()),
                    "character_count": len(content),
                    "created_at": "2024-01-15T10:30:00Z",
                }
                channel_variants.append(variant)

            variants[channel] = channel_variants

            # Save token usage
            if response.get("usage"):
                save_token_usage(
                    job_id=job_id,
                    token_usage=response["usage"],
                    model=model,
                    channel=channel,
                )

        except OpenAIError as e:
            logger.error(f"OpenAI API error for channel {channel}: {str(e)}")
            job_logger.log_job_error(
                job_id=job_id,
                tool_name="repurposer",
                user_id="unknown",
                error=e,
                error_context={"channel": channel, "model": model},
            )
            # Fallback to demo content
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

    # Validate model using core service
    client = get_openai_client()
    if not client.validate_model(selected_model):
        from core.openai_client import VALID_MODELS

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
