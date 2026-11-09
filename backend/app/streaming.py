import hashlib
import hmac
import time
from typing import Any, Dict, List, Optional
from app.config import settings
from app.models import MovieMedia

QUALITY_PRIORITY = ["1080p", "720p", "480p"]


def generate_signed_stream_token(media_id: int, user_id: int, ttl_seconds: int = 14400) -> str:
    """
    Generates an anti-piracy time-limited HMAC signature for a video stream.
    Prevents external bots or scrapers from hotlinking video streams.
    """
    expires = int(time.time()) + ttl_seconds
    payload = f"{media_id}:{user_id}:{expires}"
    sig = hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()[:20]
    return f"{expires}.{sig}"


def verify_signed_stream_token(media_id: int, user_id: int, token: str) -> bool:
    try:
        expires_str, sig = token.split(".", 1)
        expires = int(expires_str)
        if time.time() > expires:
            return False
        payload = f"{media_id}:{user_id}:{expires}"
        expected = hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()[:20]
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False


def resolve_quality_with_fallback(
    media_list: List[MovieMedia],
    requested_resolution: str = "1080p",
    user_id: int = 0,
) -> Dict[str, Any]:
    """
    PRD Section 3.A.1 — Multi-Format & Smart Fallback (Graceful Degradation):
    If the requested quality (e.g. '1080p') is not available in the database,
    playback never fails; it automatically falls back to the highest available
    resolution and returns the exact Scandinavian glyph notification:
      '✦ Ushbu format mavjud emas. Maksimal sifat (720p) ulandi'
    """
    if not media_list:
        return {
            "selected_resolution": None,
            "requested_resolution": requested_resolution,
            "fallback_triggered": False,
            "fallback_message": None,
            "stream_url": None,
            "available_resolutions": [],
            "audio_tracks": {},
            "subtitles": {},
        }

    by_res: Dict[str, MovieMedia] = {m.resolution: m for m in media_list}
    available = [r for r in QUALITY_PRIORITY if r in by_res] or list(by_res.keys())

    target_res = requested_resolution
    if requested_resolution.lower() == "auto":
        target_res = available[0]

    fallback_triggered = False
    fallback_message: Optional[str] = None

    if target_res in by_res:
        chosen = by_res[target_res]
    else:
        chosen = by_res[available[0]]
        fallback_triggered = True
        fallback_message = f"✦ Ushbu format mavjud emas. Maksimal sifat ({chosen.resolution}) ulandi"

    signed_token = generate_signed_stream_token(chosen.id, user_id)
    return {
        "media_id": chosen.id,
        "selected_resolution": chosen.resolution,
        "requested_resolution": requested_resolution,
        "fallback_triggered": fallback_triggered,
        "fallback_message": fallback_message,
        "stream_url": chosen.stream_url,
        "signed_token": signed_token,
        "telegram_file_id": chosen.telegram_file_id,
        "file_size_mb": chosen.file_size_mb,
        "available_resolutions": available,
        "audio_tracks": chosen.audio_tracks or {},
        "subtitles": chosen.subtitles or {},
        "is_offline_allowed": chosen.is_offline_allowed,
        "protect_content": chosen.protect_content,
    }
