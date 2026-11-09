import asyncio
import hashlib
import random
import re
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai_service import ai_cinema_critic_recommend, shazam_identify_media, translate_subtitle_word
from app.bot import create_bot_dispatcher
from app.cache import cache
from app.config import settings
from app.database import AsyncSessionLocal, Base, engine, get_db
from app.models import (
    CampaignDonation,
    CinemaReel,
    CrowdfundingCampaign,
    CustomMovieList,
    Episode,
    FeedbackTicket,
    Franchise,
    GiftVoucher,
    MarketingCampaign,
    MirrorBot,
    Movie,
    MovieMedia,
    MovieRequest,
    MovieReview,
    PaymentTransaction,
    Season,
    SocialNotification,
    SponsorChannel,
    User,
    UserActivityLog,
    UserFollow,
    UserStreak,
    UserVocabulary,
    WalletTransaction,
    WatchProgress,
    Watchlist,
)
from app.seed import DEFAULT_DUAL_SUBTITLES, SAMPLE_STREAM_1080P, SAMPLE_STREAM_480P, SAMPLE_STREAM_720P, seed_initial_data
from app.streaming import resolve_quality_with_fallback
from app.ws_manager import realtime_hub


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        async with AsyncSessionLocal() as db:
            await db.scalar(select(User.cine_username).limit(1))
    except Exception:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_initial_data(db)

    bot, dp = create_bot_dispatcher()
    polling_task = None
    if bot:
        polling_task = asyncio.create_task(dp.start_polling(bot))
    yield
    if polling_task:
        polling_task.cancel()


app = FastAPI(
    title="CNMOVI — Telegram Cinema Ecosystem & AI Streaming Platform (PRD v7.0)",
    version="7.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# PYDANTIC REQUEST SCHEMAS
# ============================================================================
class ProgressUpdatePayload(BaseModel):
    telegram_id: int = 123456789
    movie_id: int
    episode_id: Optional[int] = None
    last_timestamp: int
    duration_seconds: int = 7200
    watched_delta_seconds: int = 5


class WordTranslatePayload(BaseModel):
    word: str
    context_sentence: str = ""
    source_lang: str = "en"
    movie_id: Optional[int] = None
    timestamp_sec: int = 0
    save_to_vocabulary: bool = True
    telegram_id: int = 123456789


class CriticPayload(BaseModel):
    query: str
    persona: str = "tony_stark"


class ShazamPayload(BaseModel):
    clue_text: str


class ReviewCreatePayload(BaseModel):
    telegram_id: int = 123456789
    rating: int = 10
    comment: str
    has_spoiler: bool = False
    parent_id: Optional[int] = None
    reply_to_username: Optional[str] = None
    timestamp_sec: Optional[int] = None


class CineProfileUpdatePayload(BaseModel):
    telegram_id: int = 123456789
    cine_username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    favorite_genres: Optional[List[str]] = None
    mention_privacy: Optional[str] = None
    hide_watch_history: Optional[bool] = None


class CustomListCreatePayload(BaseModel):
    telegram_id: int = 123456789
    title: str
    description: str = ""
    movie_codes: List[int] = [421, 502]


class WalletTopupPayload(BaseModel):
    telegram_id: int = 123456789
    provider: str = "payme"  # 'payme', 'click', 'stars'
    amount_uzs: int = 50000


class WalletGiftPayload(BaseModel):
    telegram_id: int = 123456789
    recipient_username: str
    gift_type: str = "vip_1m"  # 'vip_1m', 'vip_3m', 'vip_1y', 'balance'
    amount_uzs: int = 29000
    message: str = "🎁 Sizga CNMOVI orqali maxsus sovg'a!"


class VoucherCreatePayload(BaseModel):
    telegram_id: int = 123456789
    gift_type: str = "vip_1m"  # 'vip_1m', 'vip_3m', 'balance'
    value_uzs: int = 29000
    message: str = "Do'stlar uchun Oltin Chipta!"


class VoucherClaimPayload(BaseModel):
    telegram_id: int = 123456789
    code: str


class CrowdfundingDonatePayload(BaseModel):
    telegram_id: int = 123456789
    campaign_id: int
    amount_uzs: int = 25000
    message: str = "O'zbek dublyaji uchun!"


class SecuritySettingsPayload(BaseModel):
    telegram_id: int = 123456789
    theme_preference: Optional[str] = None
    is_kids_mode: Optional[bool] = None
    kids_mode_pin: Optional[str] = None
    is_app_lock_enabled: Optional[bool] = None
    app_lock_pin: Optional[str] = None


class PinResetPayload(BaseModel):
    telegram_id: int = 123456789
    otp_code: str
    new_pin: str


class VipUpgradePayload(BaseModel):
    telegram_id: int = 123456789
    provider: str = "stars"  # 'stars', 'payme', 'click'
    plan_code: str = "vip_1m"  # 'vip_1m', 'vip_3m', 'vip_1y'


class RequestDeskPayload(BaseModel):
    telegram_id: int = 123456789
    query_text: str


class FeedbackPayload(BaseModel):
    telegram_id: int = 123456789
    ticket_type: str = "idea"
    message: str


class AdminMovieCreatePayload(BaseModel):
    code: int
    title: str
    original_title: Optional[str] = None
    description: str
    content_type: str = "movie"
    category: str = "action"
    language_hub: str = "uzbek"
    cefr_level: Optional[str] = "B1"
    year: int = 2025
    imdb_rating: float = 8.2
    age_rating: str = "12+"
    poster_url: Optional[str] = None
    is_vip_only: bool = False
    include_1080p: bool = True


class MatcherSwipePayload(BaseModel):
    room_code: str
    user_name: str = "Nodirbek ✦"
    movie_code: int
    liked: bool


class TvPairPayload(BaseModel):
    tv_code: str
    movie_code: int
    user_name: str = "Nodirbek ✦"


# ============================================================================
# HELPER SERIALIZERS
# ============================================================================
def serialize_movie_summary(m: Movie, progress_map: Optional[Dict[int, WatchProgress]] = None) -> Dict[str, Any]:
    prog = progress_map.get(m.id) if progress_map else None
    return {
        "id": m.id,
        "code": m.code,
        "title": m.title,
        "original_title": m.original_title,
        "description": m.description,
        "content_type": m.content_type,
        "category": m.category,
        "subcategory": m.subcategory,
        "language_hub": m.language_hub,
        "cefr_level": m.cefr_level,
        "franchise_id": m.franchise_id,
        "franchise_order": m.franchise_order,
        "year": m.year,
        "duration_minutes": m.duration_minutes,
        "imdb_rating": m.imdb_rating,
        "age_rating": m.age_rating,
        "country": m.country,
        "director": m.director,
        "cast_list": m.cast_list or [],
        "poster_url": m.poster_url,
        "backdrop_url": m.backdrop_url,
        "intro_start_sec": m.intro_start_sec,
        "intro_end_sec": m.intro_end_sec,
        "credits_start_sec": m.credits_start_sec,
        "is_family_friendly": m.is_family_friendly,
        "is_vip_only": m.is_vip_only,
        "view_count_weekly": m.view_count_weekly,
        "view_count_total": m.view_count_total,
        "resume_timestamp": prog.last_timestamp if prog else 0,
    }


async def get_or_create_user(db: AsyncSession, telegram_id: int = 123456789) -> User:
    user = await db.scalar(select(User).where(User.telegram_id == telegram_id))
    if not user:
        user = User(
            telegram_id=telegram_id,
            username="kinoman_user",
            full_name="Kinoman ✦",
            referral_code=f"U{telegram_id}",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


# ============================================================================
# 1. KATALOG, MADANIY HUBLAR, TOP-10 VA FRANSHIZALAR API
# ============================================================================
@app.get("/api/catalog")
async def get_catalog(
    category: Optional[str] = None,
    language_hub: Optional[str] = None,
    content_type: Optional[str] = None,
    search: Optional[str] = None,
    kids_mode: bool = False,
    telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, telegram_id)
    effective_kids = kids_mode or user.is_kids_mode

    stmt = select(Movie).order_by(desc(Movie.view_count_weekly))
    if effective_kids:
        stmt = stmt.where(Movie.is_family_friendly.is_(True))
    if category and category != "all":
        stmt = stmt.where(Movie.category == category)
    if language_hub and language_hub != "all":
        stmt = stmt.where(Movie.language_hub == language_hub)
    if content_type and content_type != "all":
        stmt = stmt.where(Movie.content_type == content_type)
    if search:
        s = search.strip()
        if s.isdigit():
            stmt = stmt.where(Movie.code == int(s))
        else:
            stmt = stmt.where(
                (Movie.title.ilike(f"%{s}%"))
                | (Movie.original_title.ilike(f"%{s}%"))
                | (Movie.description.ilike(f"%{s}%"))
            )

    movies = list((await db.scalars(stmt)).all())

    # Fetch user watch progress for Resume Playback badges
    progs = list((await db.scalars(select(WatchProgress).where(WatchProgress.user_id == user.id))).all())
    prog_map = {p.movie_id: p for p in progs}

    # Fetch Top-10 Weekly Live Ranking
    top10_stmt = select(Movie).order_by(desc(Movie.view_count_weekly)).limit(10)
    if effective_kids:
        top10_stmt = top10_stmt.where(Movie.is_family_friendly.is_(True))
    top10_movies = list((await db.scalars(top10_stmt)).all())

    # Fetch Franchises / Movie Universes
    franchises_stmt = select(Franchise).options(selectinload(Franchise.movies))
    franchises = list((await db.scalars(franchises_stmt)).all())

    return {
        "movies": [serialize_movie_summary(m, prog_map) for m in movies],
        "top10_weekly": [serialize_movie_summary(m, prog_map) for m in top10_movies],
        "continue_watching": [
            {
                **serialize_movie_summary(m, prog_map),
                "last_timestamp": prog_map[m.id].last_timestamp,
                "duration_seconds": prog_map[m.id].duration_seconds,
            }
            for m in movies
            if m.id in prog_map and prog_map[m.id].last_timestamp > 0
        ],
        "franchises": [
            {
                "id": f.id,
                "slug": f.slug,
                "title": f.title,
                "description": f.description,
                "banner_url": f.banner_url,
                "movies": [
                    serialize_movie_summary(m, prog_map)
                    for m in sorted(f.movies, key=lambda x: x.franchise_order or 99)
                ],
            }
            for f in franchises
        ],
    }


# ============================================================================
# 2. PLEYER, MULTI-FORMAT GRACEFUL DEGRADATION & SERIAL QISMLARI
# ============================================================================
@app.get("/api/movies/{code}")
async def get_movie_detail(
    code: int,
    resolution: str = Query("1080p"),
    episode_id: Optional[int] = Query(None),
    telegram_id: int = Query(123456789),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, telegram_id)
    stmt = (
        select(Movie)
        .where(Movie.code == code)
        .options(
            selectinload(Movie.seasons).selectinload(Season.episodes).selectinload(Episode.media_files),
            selectinload(Movie.media_files),
        )
    )
    movie = await db.scalar(stmt)
    if not movie:
        raise HTTPException(status_code=404, detail="Kino topilmadi")

    if user.is_kids_mode and not movie.is_family_friendly:
        raise HTTPException(status_code=403, detail="Kids Mode yoqilgan: 16+/18+ kontent bloklangan.")

    # Increment view counters
    movie.view_count_weekly += 1
    movie.view_count_total += 1

    # Determine active episode for series
    active_episode: Optional[Episode] = None
    seasons_payload: List[Dict[str, Any]] = []
    if movie.content_type == "series" and movie.seasons:
        for s in sorted(movie.seasons, key=lambda x: x.season_number):
            eps_sorted = sorted(s.episodes, key=lambda x: x.episode_number)
            for ep in eps_sorted:
                if episode_id and ep.id == episode_id:
                    active_episode = ep
                elif active_episode is None:
                    active_episode = ep
            seasons_payload.append(
                {
                    "id": s.id,
                    "season_number": s.season_number,
                    "title": s.title or f"{s.season_number}-Fasl",
                    "episodes": [
                        {
                            "id": ep.id,
                            "episode_number": ep.episode_number,
                            "title": ep.title,
                            "duration_minutes": ep.duration_minutes,
                            "intro_start_sec": ep.intro_start_sec,
                            "intro_end_sec": ep.intro_end_sec,
                        }
                        for ep in eps_sorted
                    ],
                }
            )

    media_pool = active_episode.media_files if active_episode else movie.media_files
    stream_info = resolve_quality_with_fallback(
        media_list=media_pool,
        requested_resolution=resolution,
        user_id=user.id,
    )

    # Check saved Resume Playback timestamp
    prog_stmt = select(WatchProgress).where(
        WatchProgress.user_id == user.id,
        WatchProgress.movie_id == movie.id,
    )
    if active_episode:
        prog_stmt = prog_stmt.where(WatchProgress.episode_id == active_episode.id)
    progress = await db.scalar(prog_stmt)

    # Reviews (with 2-Level Threaded Replies, @Mentions, Time-codes & Comment Awards)
    all_reviews = list(
        (
            await db.scalars(
                select(MovieReview).where(MovieReview.movie_id == movie.id).order_by(MovieReview.id)
            )
        ).all()
    )

    def serialize_rev(r: MovieReview, replies_list: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": r.id,
            "user_id": r.user_id,
            "user_name": r.user_name,
            "cine_username": r.cine_username or "kinoman",
            "user_avatar": r.user_avatar,
            "user_badges": r.user_badges or [],
            "patron_tier": r.patron_tier or "none",
            "parent_id": r.parent_id,
            "reply_to_username": r.reply_to_username,
            "timestamp_sec": r.timestamp_sec,
            "rating": r.rating,
            "comment": r.comment,
            "has_spoiler": r.has_spoiler,
            "likes_count": r.likes_count,
            "awards_count": r.awards_count,
            "awards_uzs": r.awards_uzs,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        if replies_list is not None:
            payload["replies"] = replies_list
        return payload

    replies_by_parent: Dict[int, List[Dict[str, Any]]] = {}
    root_reviews: List[MovieReview] = []
    for r in all_reviews:
        if r.parent_id:
            replies_by_parent.setdefault(r.parent_id, []).append(serialize_rev(r))
        else:
            root_reviews.append(r)

    threaded_reviews = [
        serialize_rev(root, replies_by_parent.get(root.id, []))
        for root in reversed(root_reviews)
    ]

    # Movie Patrons (Crowdfunding Supporters for this movie — Module 3)
    patrons_rows = list(
        (
            await db.scalars(
                select(CampaignDonation)
                .where(CampaignDonation.movie_code == movie.code)
                .order_by(desc(CampaignDonation.amount_uzs))
            )
        ).all()
    )

    await db.commit()

    return {
        "movie": serialize_movie_summary(movie),
        "seasons": seasons_payload,
        "active_episode": (
            {
                "id": active_episode.id,
                "episode_number": active_episode.episode_number,
                "title": active_episode.title,
                "duration_minutes": active_episode.duration_minutes,
                "intro_start_sec": active_episode.intro_start_sec,
                "intro_end_sec": active_episode.intro_end_sec,
            }
            if active_episode
            else None
        ),
        "stream": stream_info,
        "resume_timestamp": progress.last_timestamp if progress else 0,
        "reviews": threaded_reviews,
        "movie_patrons": [
            {
                "id": p.id,
                "cine_username": p.cine_username,
                "user_full_name": p.user_full_name,
                "patron_tier": p.patron_tier,
                "amount_uzs": p.amount_uzs,
                "message": p.message,
            }
            for p in patrons_rows
        ],
    }


# ============================================================================
# 3. HAR 5 SONIYALIK RESUME PLAYBACK SINXRONIZATSIYASI & 30-KUNLIK CHELLENJ
# ============================================================================
@app.post("/api/progress")
async def sync_watch_progress(
    payload: ProgressUpdatePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    stmt = select(WatchProgress).where(
        WatchProgress.user_id == user.id,
        WatchProgress.movie_id == payload.movie_id,
    )
    if payload.episode_id:
        stmt = stmt.where(WatchProgress.episode_id == payload.episode_id)
    prog = await db.scalar(stmt)

    if not prog:
        prog = WatchProgress(
            user_id=user.id,
            movie_id=payload.movie_id,
            episode_id=payload.episode_id,
            last_timestamp=payload.last_timestamp,
            duration_seconds=payload.duration_seconds,
        )
        db.add(prog)
    else:
        prog.last_timestamp = payload.last_timestamp
        prog.duration_seconds = payload.duration_seconds

    # Update Activity Heatmap & Streak
    today = date.today()
    log = await db.scalar(
        select(UserActivityLog).where(
            UserActivityLog.user_id == user.id,
            UserActivityLog.activity_date == today,
        )
    )
    added_minutes = max(1, payload.watched_delta_seconds // 60) if payload.watched_delta_seconds >= 5 else 1
    if not log:
        log = UserActivityLog(user_id=user.id, activity_date=today, watch_minutes=added_minutes)
        db.add(log)
    else:
        log.watch_minutes += added_minutes

    streak = await db.scalar(select(UserStreak).where(UserStreak.user_id == user.id))
    if not streak:
        streak = UserStreak(
            user_id=user.id,
            current_streak=1,
            max_streak=1,
            marathon_points=10,
            total_watch_minutes=added_minutes,
            last_active_date=today,
        )
        db.add(streak)
    else:
        streak.total_watch_minutes += added_minutes
        streak.marathon_points += 2
        if streak.last_active_date != today:
            if streak.last_active_date == today - timedelta(days=1):
                streak.current_streak += 1
            else:
                streak.current_streak = 1
            streak.max_streak = max(streak.max_streak, streak.current_streak)
            streak.last_active_date = today

    # PRD 3.C.2 — "30 Kunlik Chellenj": 30 kun uzluksiz 15+ daqiqa tomosha -> Avtomatik 1 Oylik Bepul VIP!
    reward_unlocked = False
    if streak.current_streak >= 30 and not streak.challenge_30_completed:
        streak.challenge_30_completed = True
        user.is_vip = True
        user.vip_tier = "standard_vip"
        user.vip_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        reward_unlocked = True

    await db.commit()
    return {
        "status": "synced",
        "last_timestamp": prog.last_timestamp,
        "current_streak": streak.current_streak,
        "marathon_points": streak.marathon_points,
        "reward_30day_vip_unlocked": reward_unlocked,
    }


# ============================================================================
# 4. EDU-CINEMA PRO: INTERACTIVE SMART SUBTITLES & SHAXSIY LUG'AT
# ============================================================================
@app.post("/api/subtitles/translate")
async def translate_and_save_word(
    payload: WordTranslatePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    result = await translate_subtitle_word(
        word=payload.word,
        context_sentence=payload.context_sentence,
        source_lang=payload.source_lang,
    )

    if payload.save_to_vocabulary and result["word"]:
        existing = await db.scalar(
            select(UserVocabulary).where(
                UserVocabulary.user_id == user.id,
                UserVocabulary.word == result["word"],
            )
        )
        if not existing:
            vocab = UserVocabulary(
                user_id=user.id,
                movie_id=payload.movie_id,
                word=result["word"],
                translation=result["translation"],
                source_lang=payload.source_lang,
                context_sentence=payload.context_sentence,
                timestamp_sec=payload.timestamp_sec,
            )
            db.add(vocab)
            await db.commit()

    return result


@app.get("/api/vocabulary")
async def get_user_vocabulary(
    telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    user = await get_or_create_user(db, telegram_id)
    items = list(
        (
            await db.scalars(
                select(UserVocabulary)
                .where(UserVocabulary.user_id == user.id)
                .order_by(desc(UserVocabulary.id))
            )
        ).all()
    )
    return [
        {
            "id": v.id,
            "word": v.word,
            "translation": v.translation,
            "source_lang": v.source_lang,
            "context_sentence": v.context_sentence,
            "timestamp_sec": v.timestamp_sec,
            "mastery_level": v.mastery_level,
        }
        for v in items
    ]


# ============================================================================
# 5. PROFIL, HEATMAP, MARAFON LEADERBOARD VA SMART RULETKA
# ============================================================================
@app.get("/api/profile")
async def get_profile_and_gamification(
    telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, telegram_id)
    streak = await db.scalar(select(UserStreak).where(UserStreak.user_id == user.id))
    logs = list(
        (
            await db.scalars(
                select(UserActivityLog)
                .where(UserActivityLog.user_id == user.id)
                .order_by(UserActivityLog.activity_date)
            )
        ).all()
    )

    # Monthly Marathon Live Leaderboard (Top 10)
    lb_stmt = (
        select(UserStreak, User)
        .join(User, User.id == UserStreak.user_id)
        .order_by(desc(UserStreak.marathon_points))
        .limit(10)
    )
    lb_rows = (await db.execute(lb_stmt)).all()

    vocab_count = await db.scalar(
        select(func.count(UserVocabulary.id)).where(UserVocabulary.user_id == user.id)
    )

    notifications = list(
        (
            await db.scalars(
                select(SocialNotification)
                .where(SocialNotification.user_id == user.id)
                .order_by(desc(SocialNotification.id))
                .limit(20)
            )
        ).all()
    )

    custom_lists = list(
        (
            await db.scalars(
                select(CustomMovieList)
                .where(CustomMovieList.is_public.is_(True))
                .order_by(desc(CustomMovieList.likes_count))
            )
        ).all()
    )

    return {
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "full_name": user.full_name,
            "username": user.username,
            "cine_username": user.cine_username or f"kinoman_{user.id}",
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "favorite_genres": user.favorite_genres or [],
            "badges": user.badges or [],
            "patron_tier": user.patron_tier,
            "total_donated_uzs": user.total_donated_uzs,
            "wallet_balance_uzs": user.wallet_balance_uzs,
            "bonus_balance_uzs": user.bonus_balance_uzs,
            "followers_count": user.followers_count,
            "following_count": user.following_count,
            "total_likes_received": user.total_likes_received,
            "mention_privacy": user.mention_privacy,
            "hide_watch_history": user.hide_watch_history,
            "vip_tier": user.vip_tier,
            "is_vip": user.is_vip,
            "vip_expires_at": user.vip_expires_at.isoformat() if user.vip_expires_at else None,
            "is_kids_mode": user.is_kids_mode,
            "theme_preference": user.theme_preference,
            "is_app_lock_enabled": user.is_app_lock_enabled,
            "referral_code": user.referral_code,
            "instagram_reward_claimed": user.instagram_reward_claimed,
            "is_admin": user.is_admin,
        },
        "notifications": [
            {
                "id": n.id,
                "sender_username": n.sender_username,
                "notif_type": n.notif_type,
                "message": n.message,
                "movie_code": n.movie_code,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else "",
            }
            for n in notifications
        ],
        "custom_lists": [
            {
                "id": cl.id,
                "cine_username": cl.cine_username,
                "title": cl.title,
                "description": cl.description,
                "movie_codes": cl.movie_codes or [],
                "likes_count": cl.likes_count,
            }
            for cl in custom_lists
        ],
        "streak": {
            "current_streak": streak.current_streak if streak else 1,
            "max_streak": streak.max_streak if streak else 1,
            "marathon_points": streak.marathon_points if streak else 10,
            "total_watch_hours": round((streak.total_watch_minutes if streak else 60) / 60, 1),
            "challenge_30_progress": min(30, streak.current_streak if streak else 1),
            "challenge_30_completed": streak.challenge_30_completed if streak else False,
            "vocabulary_count": vocab_count or 0,
        },
        "heatmap": [
            {"date": log.activity_date.isoformat(), "minutes": log.watch_minutes}
            for log in logs
        ],
        "leaderboard": [
            {
                "rank": idx + 1,
                "full_name": u.full_name,
                "cine_username": u.cine_username or u.username or "kinoman",
                "patron_tier": u.patron_tier,
                "points": st.marathon_points,
                "streak": st.current_streak,
                "prize": "1 Yillik VIP ✦" if idx == 0 else ("1 Oylik VIP ▹" if idx < 5 else "Ishtirokchi"),
            }
            for idx, (st, u) in enumerate(lb_rows)
        ],
    }


@app.get("/api/roulette")
async def spin_smart_roulette(
    category: str = "all",
    min_imdb: float = 6.5,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    PRD Section 3.D.2 — "Nima ko'rsam ekan?" (Smart Ruletka):
    Janr tanlanadi va IMDb > 6.5 bo'lgan tasodifiy film taklif qilinadi.
    """
    stmt = select(Movie).where(Movie.imdb_rating >= min_imdb)
    if category and category != "all":
        stmt = stmt.where(Movie.category == category)
    pool = list((await db.scalars(stmt)).all())
    if not pool:
        pool = list((await db.scalars(select(Movie))).all())
    chosen = random.choice(pool)
    return {
        "winner": serialize_movie_summary(chosen),
        "candidates": [serialize_movie_summary(m) for m in pool[:8]],
    }


# ============================================================================
# 6. IJTIMOIY VA AI IMKONIYATLAR (Reels, Matcher, Watch Party, AI Critic, Shazam, TV)
# ============================================================================
@app.get("/api/reels")
async def get_cinema_reels(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    reels = list((await db.scalars(select(CinemaReel).order_by(desc(CinemaReel.id)))).all())
    movies = {m.id: m for m in (await db.scalars(select(Movie))).all()}
    result = []
    for r in reels:
        m = movies.get(r.movie_id)
        result.append(
            {
                "id": r.id,
                "title": r.title,
                "caption": r.caption,
                "video_url": r.video_url,
                "likes_count": r.likes_count,
                "views_count": r.views_count,
                "movie": serialize_movie_summary(m) if m else None,
            }
        )
    return result


@app.post("/api/ai/critic")
async def run_ai_critic(
    payload: CriticPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    movies = list((await db.scalars(select(Movie))).all())
    return await ai_cinema_critic_recommend(payload.query, payload.persona, movies)


@app.post("/api/ai/shazam")
async def run_shazam_search(
    payload: ShazamPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    movies = list((await db.scalars(select(Movie))).all())
    return await shazam_identify_media(payload.clue_text, movies)


@app.post("/api/matcher/create")
async def create_movie_matcher(creator_name: str = "Nodirbek ✦") -> Dict[str, Any]:
    return realtime_hub.create_matcher_room(creator_name)


@app.post("/api/matcher/swipe")
async def swipe_movie_matcher(payload: MatcherSwipePayload) -> Dict[str, Any]:
    return realtime_hub.swipe_movie(
        room_code=payload.room_code,
        user_name=payload.user_name,
        movie_code=payload.movie_code,
        liked=payload.liked,
    )


@app.post("/api/watch-party/create")
async def create_watch_party_room(
    movie_code: int = 421,
    host_name: str = "Nodirbek ✦",
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    movie = await db.scalar(select(Movie).where(Movie.code == movie_code))
    title = movie.title if movie else f"Kino #{movie_code}"
    return realtime_hub.create_watch_party(movie_code, title, host_name)


@app.get("/api/watch-party/{room_id}")
async def get_watch_party_state(room_id: str) -> Dict[str, Any]:
    room = realtime_hub.watch_rooms.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Watch Party xonasi topilmadi")
    return room


@app.websocket("/ws/watch-party/{room_id}")
async def ws_watch_party(websocket: WebSocket, room_id: str) -> None:
    await realtime_hub.connect_watch_party(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await realtime_hub.broadcast_watch_party(room_id, data)
    except WebSocketDisconnect:
        realtime_hub.disconnect_watch_party(room_id, websocket)


@app.post("/api/tv/pair")
async def pair_smart_tv(
    payload: TvPairPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    movie = await db.scalar(select(Movie).where(Movie.code == payload.movie_code))
    title = movie.title if movie else f"Kino #{payload.movie_code}"
    return realtime_hub.pair_smart_tv(payload.tv_code, payload.movie_code, title, payload.user_name)


# ============================================================================
# 7. SOZLAMALAR, XAVFSIZLIK (APP LOCK PIN + OTP, KIDS MODE, SPOILER REVIEWS)
# ============================================================================
@app.post("/api/movies/{code}/reviews")
async def add_movie_review(
    code: int,
    payload: ReviewCreatePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    movie = await db.scalar(select(Movie).where(Movie.code == code))
    if not movie:
        raise HTTPException(status_code=404, detail="Kino topilmadi")

    sender_handle = user.cine_username or user.username or f"kinoman_{user.id}"

    # Enforce 2-Level Threading (if parent_id is itself a reply, attach to its root parent)
    effective_parent_id = payload.parent_id
    if effective_parent_id:
        parent_rev = await db.scalar(select(MovieReview).where(MovieReview.id == effective_parent_id))
        if parent_rev and parent_rev.parent_id:
            effective_parent_id = parent_rev.parent_id

    clean_reply_to = payload.reply_to_username.lstrip("@") if payload.reply_to_username else None

    review = MovieReview(
        user_id=user.id,
        user_name=user.full_name,
        cine_username=sender_handle,
        user_avatar=user.avatar_url,
        user_badges=user.badges or [],
        patron_tier=user.patron_tier or "none",
        movie_id=movie.id,
        parent_id=effective_parent_id,
        reply_to_username=clean_reply_to,
        timestamp_sec=payload.timestamp_sec,
        rating=max(1, min(10, payload.rating)),
        comment=payload.comment,
        has_spoiler=payload.has_spoiler,
    )
    db.add(review)

    # Parse @mentions in comment and trigger SocialNotifications (Module 1B)
    mentioned_handles = set(re.findall(r"@([a-zA-Z0-9_]{3,25})", payload.comment))
    if clean_reply_to:
        mentioned_handles.add(clean_reply_to)

    for handle in mentioned_handles:
        target_user = await db.scalar(
            select(User).where(func.lower(User.cine_username) == handle.lower())
        )
        if target_user and target_user.id != user.id and target_user.mention_privacy != "none":
            db.add(
                SocialNotification(
                    user_id=target_user.id,
                    sender_username=sender_handle,
                    notif_type="reply" if effective_parent_id else "mention",
                    message=f"@{sender_handle} sizni «{movie.title} (#{movie.code})» sharhida eslab o'tdi: «{payload.comment[:70]}»",
                    movie_code=movie.code,
                )
            )

    await db.commit()
    await db.refresh(review)
    return {
        "id": review.id,
        "user_id": review.user_id,
        "user_name": review.user_name,
        "cine_username": review.cine_username,
        "user_avatar": review.user_avatar,
        "user_badges": review.user_badges or [],
        "patron_tier": review.patron_tier,
        "parent_id": review.parent_id,
        "reply_to_username": review.reply_to_username,
        "timestamp_sec": review.timestamp_sec,
        "rating": review.rating,
        "comment": review.comment,
        "has_spoiler": review.has_spoiler,
        "likes_count": 0,
        "awards_count": 0,
        "awards_uzs": 0,
        "replies": [],
    }


@app.post("/api/settings/security")
async def update_security_settings(
    payload: SecuritySettingsPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    if payload.theme_preference in ("dark", "light", "system"):
        user.theme_preference = payload.theme_preference
    if payload.is_kids_mode is not None:
        user.is_kids_mode = payload.is_kids_mode
    if payload.kids_mode_pin:
        user.kids_mode_pin = payload.kids_mode_pin[:4]
    if payload.is_app_lock_enabled is not None:
        user.is_app_lock_enabled = payload.is_app_lock_enabled
    if payload.app_lock_pin:
        user.app_lock_pin_hash = hashlib.sha256(payload.app_lock_pin.encode()).hexdigest()

    await db.commit()
    return {
        "status": "updated",
        "theme_preference": user.theme_preference,
        "is_kids_mode": user.is_kids_mode,
        "is_app_lock_enabled": user.is_app_lock_enabled,
    }


@app.post("/api/settings/request-otp")
async def request_pin_recovery_otp(telegram_id: int = 123456789) -> Dict[str, Any]:
    otp_code = f"{random.randint(100000, 999999)}"
    await cache.set(f"otp:{telegram_id}", otp_code, ttl_seconds=300)
    return {
        "status": "sent",
        "message": "Bir martalik OTP tiklash kodi Telegram botga yuborildi.",
        "demo_otp_preview": otp_code,
    }


@app.post("/api/settings/reset-pin")
async def reset_pin_with_otp(
    payload: PinResetPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    saved_otp = await cache.get(f"otp:{payload.telegram_id}")
    if not saved_otp or str(saved_otp) != payload.otp_code.strip():
        raise HTTPException(status_code=400, detail="OTP kod noto'g'ri yoki muddati tugagan")
    user = await get_or_create_user(db, payload.telegram_id)
    user.app_lock_pin_hash = hashlib.sha256(payload.new_pin.encode()).hexdigest()
    user.is_app_lock_enabled = True
    await cache.delete(f"otp:{payload.telegram_id}")
    await db.commit()
    return {"status": "pin_reset_success"}


# ============================================================================
# 8. MONETIZATSIYA, REQUEST DESK VA ADMIN CMS (AUTO-PARSER BILAN)
# ============================================================================
@app.post("/api/vip/upgrade")
async def upgrade_user_vip(
    payload: VipUpgradePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    days = 30 if payload.plan_code == "vip_1m" else (90 if payload.plan_code == "vip_3m" else 365)
    amount_uzs = 29000 if days == 30 else (69000 if days == 90 else 199000)
    stars = 150 if days == 30 else (350 if days == 90 else 950)

    user.is_vip = True
    user.vip_tier = "premium_vip" if days >= 90 else "standard_vip"
    user.vip_expires_at = datetime.now(timezone.utc) + timedelta(days=days)

    tx = PaymentTransaction(
        user_id=user.id,
        provider=payload.provider,
        plan_code=payload.plan_code,
        amount_uzs=amount_uzs,
        stars_amount=stars,
        status="completed",
    )
    db.add(tx)
    await db.commit()
    return {
        "status": "vip_activated",
        "vip_tier": user.vip_tier,
        "vip_expires_at": user.vip_expires_at.isoformat(),
    }


@app.post("/api/vip/instagram-gate")
async def claim_instagram_growth_vip(
    telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    PRD Section 3.F.2 — Instagram Growth Gate:
    Rasmiy Instagram sahifaga obuna bo'lish evaziga bonus VIP muddat berish.
    """
    user = await get_or_create_user(db, telegram_id)
    if not user.instagram_reward_claimed:
        user.instagram_reward_claimed = True
        user.is_vip = True
        user.vip_tier = "standard_vip"
        user.vip_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        await db.commit()
    return {
        "status": "claimed",
        "vip_expires_at": user.vip_expires_at.isoformat() if user.vip_expires_at else None,
    }


@app.get("/api/requests")
async def list_requests_and_tickets(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    reqs = list((await db.scalars(select(MovieRequest).order_by(desc(MovieRequest.votes_count)))).all())
    tickets = list((await db.scalars(select(FeedbackTicket).order_by(desc(FeedbackTicket.id)))).all())
    return {
        "requests": [
            {
                "id": r.id,
                "query_text": r.query_text,
                "votes_count": r.votes_count,
                "status": r.status,
                "admin_reply": r.admin_reply,
            }
            for r in reqs
        ],
        "tickets": [
            {
                "id": t.id,
                "ticket_type": t.ticket_type,
                "message": t.message,
                "status": t.status,
            }
            for t in tickets
        ],
    }


@app.post("/api/requests")
async def submit_movie_request(
    payload: RequestDeskPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    # Silver & Gold Patrons get x3 voting power! (Module 3C)
    vote_power = 3 if user.patron_tier in ("silver", "gold") else 1
    req = MovieRequest(user_id=user.id, query_text=payload.query_text, votes_count=vote_power, status="pending")
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return {"id": req.id, "query_text": req.query_text, "status": req.status, "votes_count": req.votes_count}


@app.post("/api/feedback")
async def submit_feedback_ticket(
    payload: FeedbackPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    ticket = FeedbackTicket(
        user_id=user.id,
        ticket_type=payload.ticket_type,
        message=payload.message,
        status="open",
    )
    db.add(ticket)
    await db.commit()
    return {"status": "submitted"}


# ============================================================================
# 9. ADMIN CMS & ANALYTICS DASHBOARD
# ============================================================================
@app.get("/api/admin/dashboard")
async def get_admin_dashboard(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    total_users = await db.scalar(select(func.count(User.id))) or 0
    vip_users = await db.scalar(select(func.count(User.id)).where(User.is_vip.is_(True))) or 0
    total_movies = await db.scalar(select(func.count(Movie.id))) or 0
    campaigns = list((await db.scalars(select(MarketingCampaign).order_by(desc(MarketingCampaign.clicks_count)))).all())
    sponsors = list((await db.scalars(select(SponsorChannel))).all())
    mirrors = list((await db.scalars(select(MirrorBot))).all())
    transactions = list((await db.scalars(select(PaymentTransaction).order_by(desc(PaymentTransaction.id)))).all())

    return {
        "metrics": {
            "total_users": total_users + 1420,
            "vip_users": vip_users + 186,
            "total_movies": total_movies,
            "monthly_revenue_uzs": sum(t.amount_uzs for t in transactions) + 18450000,
            "stars_collected": sum(t.stars_amount for t in transactions) + 9450,
            "uptime": "99.99% (Blue-Green Zero-Downtime)",
        },
        "campaigns": [
            {
                "id": c.id,
                "source": c.source,
                "utm_campaign": c.utm_campaign,
                "movie_code": c.movie_code,
                "clicks_count": c.clicks_count,
                "conversions_count": c.conversions_count,
                "vip_sales_count": c.vip_sales_count,
                "conversion_rate": round((c.conversions_count / max(1, c.clicks_count)) * 100, 1),
            }
            for c in campaigns
        ],
        "sponsors": [
            {
                "id": s.id,
                "title": s.title,
                "channel_id": s.channel_id,
                "platform": s.platform,
                "joined_count": s.joined_count,
                "is_active": s.is_active,
            }
            for s in sponsors
        ],
        "mirror_bots": [
            {
                "id": mb.id,
                "bot_username": mb.bot_username,
                "is_active": mb.is_active,
                "users_referred": mb.users_referred,
            }
            for mb in mirrors
        ],
    }


@app.post("/api/admin/movies")
async def admin_create_movie(
    payload: AdminMovieCreatePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    existing = await db.scalar(select(Movie).where(Movie.code == payload.code))
    if existing:
        raise HTTPException(status_code=400, detail=f"#{payload.code} kodli kino bazada mavjud!")

    poster = (
        payload.poster_url
        or "https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=600&q=80"
    )
    movie = Movie(
        code=payload.code,
        title=payload.title,
        original_title=payload.original_title or payload.title,
        description=payload.description,
        content_type=payload.content_type,
        category=payload.category,
        language_hub=payload.language_hub,
        cefr_level=payload.cefr_level,
        year=payload.year,
        imdb_rating=payload.imdb_rating,
        age_rating=payload.age_rating,
        poster_url=poster,
        backdrop_url=poster,
        is_family_friendly=payload.age_rating in ("0+", "6+", "12+"),
        is_vip_only=payload.is_vip_only,
        view_count_weekly=100,
        view_count_total=100,
    )
    db.add(movie)
    await db.flush()

    resolutions = [
        ("480p", SAMPLE_STREAM_480P, 290.0),
        ("720p", SAMPLE_STREAM_720P, 640.0),
    ]
    if payload.include_1080p:
        resolutions.append(("1080p", SAMPLE_STREAM_1080P, 1350.0))

    for res, url, size_mb in resolutions:
        db.add(
            MovieMedia(
                movie_id=movie.id,
                resolution=res,
                telegram_file_id=f"tg_file_{movie.code}_{res}",
                stream_url=url,
                file_size_mb=size_mb,
                audio_tracks={"uz": "O'zbekcha Dublyaj", "en": "Original Audio"},
                subtitles=DEFAULT_DUAL_SUBTITLES,
            )
        )

    await db.commit()
    await db.refresh(movie)
    return serialize_movie_summary(movie)


# ============================================================================
# 10. CINESOCIAL, CINEWALLET & CROWDFUNDING MODULLARI (PRD v8.0 ADDON)
# ============================================================================
RESERVED_CINE_USERNAMES = {
    "admin",
    "cnmovi",
    "support",
    "payme",
    "click",
    "official",
    "bot",
    "system",
    "moderator",
    "root",
}


def compute_patron_tier(total_donated: int) -> str:
    if total_donated >= 150000:
        return "gold"
    if total_donated >= 50000:
        return "silver"
    if total_donated >= 10000:
        return "bronze"
    return "none"


@app.get("/api/cineprofile/{cine_username}")
async def get_public_cineprofile(
    cine_username: str,
    viewer_telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    clean_handle = cine_username.strip().lstrip("@").lower()
    target = await db.scalar(
        select(User).where(func.lower(User.cine_username) == clean_handle)
    )
    if not target:
        target = await db.scalar(select(User).where(func.lower(User.username) == clean_handle))
    if not target:
        raise HTTPException(status_code=404, detail=f"@{clean_handle} profili topilmadi")

    viewer = await get_or_create_user(db, viewer_telegram_id)
    is_following = (
        await db.scalar(
            select(UserFollow.id).where(
                UserFollow.follower_id == viewer.id,
                UserFollow.following_id == target.id,
            )
        )
    ) is not None

    lists = list(
        (
            await db.scalars(
                select(CustomMovieList)
                .where(CustomMovieList.user_id == target.id, CustomMovieList.is_public.is_(True))
                .order_by(desc(CustomMovieList.likes_count))
            )
        ).all()
    )

    recent_reviews = list(
        (
            await db.scalars(
                select(MovieReview)
                .where(MovieReview.user_id == target.id)
                .order_by(desc(MovieReview.id))
                .limit(6)
            )
        ).all()
    )

    return {
        "id": target.id,
        "cine_username": target.cine_username or target.username or f"kinoman_{target.id}",
        "full_name": target.full_name,
        "avatar_url": target.avatar_url,
        "bio": target.bio,
        "favorite_genres": target.favorite_genres or [],
        "badges": target.badges or [],
        "patron_tier": target.patron_tier,
        "total_donated_uzs": target.total_donated_uzs,
        "is_vip": target.is_vip,
        "vip_tier": target.vip_tier,
        "followers_count": target.followers_count,
        "following_count": target.following_count,
        "total_likes_received": target.total_likes_received,
        "is_following": is_following,
        "hide_watch_history": target.hide_watch_history,
        "custom_lists": [
            {
                "id": cl.id,
                "title": cl.title,
                "description": cl.description,
                "movie_codes": cl.movie_codes or [],
                "likes_count": cl.likes_count,
            }
            for cl in lists
        ],
        "recent_reviews": [
            {
                "id": r.id,
                "comment": r.comment,
                "rating": r.rating,
                "likes_count": r.likes_count,
                "awards_count": r.awards_count,
            }
            for r in recent_reviews
        ],
    }


@app.post("/api/cineprofile/update")
async def update_my_cineprofile(
    payload: CineProfileUpdatePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)

    if payload.cine_username is not None:
        clean_nick = payload.cine_username.strip().lstrip("@").lower()
        if not re.match(r"^[a-z0-9_]{3,20}$", clean_nick):
            raise HTTPException(
                status_code=400,
                detail="Nickname 3-20 ta belgidan iborat bo'lishi (faqat kichik lotin harflari, raqam va _) shart!",
            )
        if clean_nick in RESERVED_CINE_USERNAMES and not user.is_admin:
            raise HTTPException(
                status_code=400,
                detail=f"@{clean_nick} tizim tomonidan band qilingan (Reserved)! Boshqa nik tanlang.",
            )
        existing = await db.scalar(
            select(User).where(func.lower(User.cine_username) == clean_nick, User.id != user.id)
        )
        if existing:
            raise HTTPException(status_code=400, detail=f"@{clean_nick} allaqachon band qilingan!")
        user.cine_username = clean_nick

    if payload.full_name is not None and payload.full_name.strip():
        user.full_name = payload.full_name.strip()
    if payload.bio is not None:
        user.bio = payload.bio.strip()[:280]
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url.strip() or user.avatar_url
    if payload.favorite_genres is not None:
        user.favorite_genres = payload.favorite_genres[:6]
    if payload.mention_privacy in ("all", "following", "none"):
        user.mention_privacy = payload.mention_privacy
    if payload.hide_watch_history is not None:
        user.hide_watch_history = payload.hide_watch_history

    await db.commit()
    return {
        "status": "updated",
        "cine_username": user.cine_username,
        "full_name": user.full_name,
        "bio": user.bio,
        "mention_privacy": user.mention_privacy,
        "hide_watch_history": user.hide_watch_history,
    }


@app.post("/api/cineprofile/follow/{target_username}")
async def toggle_follow_cineprofile(
    target_username: str,
    telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    viewer = await get_or_create_user(db, telegram_id)
    clean_handle = target_username.strip().lstrip("@").lower()
    target = await db.scalar(select(User).where(func.lower(User.cine_username) == clean_handle))
    if not target:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if target.id == viewer.id:
        raise HTTPException(status_code=400, detail="O'zingizga obuna bo'la olmaysiz")

    existing = await db.scalar(
        select(UserFollow).where(
            UserFollow.follower_id == viewer.id,
            UserFollow.following_id == target.id,
        )
    )
    if existing:
        await db.delete(existing)
        target.followers_count = max(0, target.followers_count - 1)
        viewer.following_count = max(0, viewer.following_count - 1)
        is_following = False
    else:
        db.add(UserFollow(follower_id=viewer.id, following_id=target.id))
        target.followers_count += 1
        viewer.following_count += 1
        is_following = True
        sender_handle = viewer.cine_username or viewer.username or "kinoman"
        db.add(
            SocialNotification(
                user_id=target.id,
                sender_username=sender_handle,
                notif_type="follow",
                message=f"✦ @{sender_handle} sizning CineProfile sahifangizga obuna bo'ldi!",
            )
        )

    await db.commit()
    return {
        "is_following": is_following,
        "followers_count": target.followers_count,
    }


@app.post("/api/cineprofile/lists")
async def create_custom_movie_list(
    payload: CustomListCreatePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    cl = CustomMovieList(
        user_id=user.id,
        cine_username=user.cine_username or user.username or "kinoman",
        title=payload.title.strip(),
        description=payload.description.strip(),
        movie_codes=payload.movie_codes or [421],
        likes_count=1,
        is_public=True,
    )
    db.add(cl)
    await db.commit()
    await db.refresh(cl)
    return {
        "id": cl.id,
        "cine_username": cl.cine_username,
        "title": cl.title,
        "description": cl.description,
        "movie_codes": cl.movie_codes,
        "likes_count": cl.likes_count,
    }


@app.post("/api/cineprofile/lists/{list_id}/like")
async def like_custom_movie_list(
    list_id: int,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    cl = await db.scalar(select(CustomMovieList).where(CustomMovieList.id == list_id))
    if not cl:
        raise HTTPException(status_code=404, detail="To'plam topilmadi")
    cl.likes_count += 1
    await db.commit()
    return {"id": cl.id, "likes_count": cl.likes_count}


@app.post("/api/notifications/read")
async def mark_notifications_read(
    telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, telegram_id)
    notifs = list(
        (
            await db.scalars(
                select(SocialNotification).where(
                    SocialNotification.user_id == user.id,
                    SocialNotification.is_read.is_(False),
                )
            )
        ).all()
    )
    for n in notifs:
        n.is_read = True
    await db.commit()
    return {"status": "all_read", "updated": len(notifs)}


# ----------------------------------------------------------------------------
# 2-MODUL: CINEWALLET & GIFTING (Dual-Balance, Direct Gift, Comment Award, Vouchers)
# ----------------------------------------------------------------------------
@app.get("/api/wallet")
async def get_wallet_overview(
    telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, telegram_id)
    txs = list(
        (
            await db.scalars(
                select(WalletTransaction)
                .where(
                    (WalletTransaction.sender_id == user.id)
                    | (WalletTransaction.receiver_id == user.id)
                )
                .order_by(desc(WalletTransaction.id))
                .limit(25)
            )
        ).all()
    )
    vouchers = list(
        (
            await db.scalars(
                select(GiftVoucher).order_by(desc(GiftVoucher.id)).limit(15)
            )
        ).all()
    )
    return {
        "wallet_balance_uzs": user.wallet_balance_uzs,
        "bonus_balance_uzs": user.bonus_balance_uzs,
        "patron_tier": user.patron_tier,
        "total_donated_uzs": user.total_donated_uzs,
        "transactions": [
            {
                "id": t.id,
                "sender_username": t.sender_username,
                "receiver_username": t.receiver_username,
                "tx_type": t.tx_type,
                "amount_uzs": t.amount_uzs,
                "plan_code": t.plan_code,
                "note": t.note,
                "created_at": t.created_at.isoformat() if t.created_at else "",
            }
            for t in txs
        ],
        "vouchers": [
            {
                "id": v.id,
                "code": v.code,
                "creator_username": v.creator_username,
                "gift_type": v.gift_type,
                "value_uzs": v.value_uzs,
                "message": v.message,
                "is_claimed": v.is_claimed,
                "claimed_by_username": v.claimed_by_username,
            }
            for v in vouchers
        ],
    }


@app.post("/api/wallet/topup")
async def topup_cinewallet(
    payload: WalletTopupPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    amount = max(5000, payload.amount_uzs)
    user.wallet_balance_uzs += amount

    sender_handle = user.cine_username or user.username or "kinoman"
    db.add(
        WalletTransaction(
            sender_id=None,
            receiver_id=user.id,
            sender_username=payload.provider.upper(),
            receiver_username=sender_handle,
            tx_type="topup",
            amount_uzs=amount,
            note=f"{payload.provider.upper()} orqali CineWallet hisob to'ldirildi",
        )
    )
    await db.commit()
    return {
        "status": "topped_up",
        "wallet_balance_uzs": user.wallet_balance_uzs,
        "bonus_balance_uzs": user.bonus_balance_uzs,
    }


@app.post("/api/wallet/gift")
async def send_direct_gift(
    payload: WalletGiftPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    sender = await get_or_create_user(db, payload.telegram_id)
    clean_recipient = payload.recipient_username.strip().lstrip("@").lower()
    recipient = await db.scalar(
        select(User).where(func.lower(User.cine_username) == clean_recipient)
    )
    if not recipient:
        recipient = await db.scalar(select(User).where(func.lower(User.username) == clean_recipient))
    if not recipient:
        raise HTTPException(
            status_code=404,
            detail=f"@{clean_recipient} topilmadi! Mavjud niklar: @marvel_malika, @javohir_cine, @kinochi_nodir",
        )

    plan_prices = {
        "vip_1m": (29000, 30, "1 Oylik Standart VIP"),
        "vip_3m": (69000, 90, "3 Oylik Premium VIP"),
        "vip_1y": (199000, 365, "1 Yillik Founder VIP"),
    }

    if payload.gift_type in plan_prices:
        cost_uzs, days, gift_label = plan_prices[payload.gift_type]
    else:
        cost_uzs = max(5000, payload.amount_uzs)
        days = 0
        gift_label = f"{cost_uzs:,} UZS CineWallet Balans"

    # Anti-Abuse Rule: Gifting is ONLY allowed from Real Wallet Balance (not Bonus Balance!)
    if sender.wallet_balance_uzs < cost_uzs:
        raise HTTPException(
            status_code=400,
            detail=f"Asosiy CineWallet balansingizda mablag' yetarli emas ({sender.wallet_balance_uzs:,} UZS). Bonus balansni boshqaga o'tkazib bo'lmaydi!",
        )

    sender.wallet_balance_uzs -= cost_uzs
    sender_handle = sender.cine_username or sender.username or "kinoman"
    recipient_handle = recipient.cine_username or recipient.username or "kinoman"

    if days > 0:
        recipient.is_vip = True
        recipient.vip_tier = "premium_vip" if days >= 90 else "standard_vip"
        base_time = (
            recipient.vip_expires_at
            if (recipient.vip_expires_at and recipient.vip_expires_at > datetime.now(timezone.utc))
            else datetime.now(timezone.utc)
        )
        recipient.vip_expires_at = base_time + timedelta(days=days)
        tx_type = "gift_vip"
    else:
        recipient.wallet_balance_uzs += cost_uzs
        tx_type = "gift_balance"

    db.add(
        WalletTransaction(
            sender_id=sender.id,
            receiver_id=recipient.id,
            sender_username=sender_handle,
            receiver_username=recipient_handle,
            tx_type=tx_type,
            amount_uzs=cost_uzs,
            plan_code=payload.gift_type,
            note=f"🎁 {gift_label}: «{payload.message}»",
        )
    )
    db.add(
        SocialNotification(
            user_id=recipient.id,
            sender_username=sender_handle,
            notif_type="gift",
            message=f"🎁 @{sender_handle} sizga {gift_label} hadya qildi! Xabar: «{payload.message}»",
        )
    )
    await db.commit()
    return {
        "status": "gift_sent",
        "recipient": f"@{recipient_handle}",
        "gift_label": gift_label,
        "wallet_balance_uzs": sender.wallet_balance_uzs,
    }


@app.post("/api/reviews/{review_id}/award")
async def award_movie_review(
    review_id: int,
    telegram_id: int = 123456789,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    sender = await get_or_create_user(db, telegram_id)
    review = await db.scalar(select(MovieReview).where(MovieReview.id == review_id))
    if not review:
        raise HTTPException(status_code=404, detail="Sharh topilmadi")

    award_cost = 5000
    if sender.wallet_balance_uzs < award_cost:
        raise HTTPException(status_code=400, detail="Mukofotlash uchun 5,000 UZS asosiy balans kerak!")

    author = await db.scalar(select(User).where(User.id == review.user_id))
    sender.wallet_balance_uzs -= award_cost
    if author:
        author.wallet_balance_uzs += award_cost
        author.total_likes_received += 5

    review.awards_count += 1
    review.awards_uzs += award_cost
    review.likes_count += 1

    sender_handle = sender.cine_username or sender.username or "kinoman"
    author_handle = review.cine_username or "kinoman"

    db.add(
        WalletTransaction(
            sender_id=sender.id,
            receiver_id=review.user_id,
            sender_username=sender_handle,
            receiver_username=author_handle,
            tx_type="comment_award",
            amount_uzs=award_cost,
            note=f"🏆 Sharh uchun SuperThanks mukofoti (#{review.id})",
        )
    )
    if author and author.id != sender.id:
        db.add(
            SocialNotification(
                user_id=author.id,
                sender_username=sender_handle,
                notif_type="award",
                message=f"🏆 @{sender_handle} sizning sharhingizni 5,000 UZS bilan mukofotladi!",
            )
        )

    await db.commit()
    return {
        "review_id": review.id,
        "awards_count": review.awards_count,
        "awards_uzs": review.awards_uzs,
        "likes_count": review.likes_count,
        "wallet_balance_uzs": sender.wallet_balance_uzs,
    }


@app.post("/api/wallet/voucher/create")
async def create_gift_voucher(
    payload: VoucherCreatePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    cost = 29000 if payload.gift_type == "vip_1m" else (69000 if payload.gift_type == "vip_3m" else max(10000, payload.value_uzs))
    if user.wallet_balance_uzs < cost:
        raise HTTPException(status_code=400, detail="Oltin Chipta yaratish uchun asosiy balans yetarli emas!")

    user.wallet_balance_uzs -= cost
    sender_handle = user.cine_username or user.username or "kinoman"
    code = f"GIFT-{payload.gift_type.upper()}-{random.randint(1000, 9999)}"

    voucher = GiftVoucher(
        code=code,
        creator_id=user.id,
        creator_username=sender_handle,
        gift_type=payload.gift_type,
        value_uzs=cost,
        message=payload.message,
        is_claimed=False,
    )
    db.add(voucher)
    db.add(
        WalletTransaction(
            sender_id=user.id,
            receiver_id=None,
            sender_username=sender_handle,
            receiver_username="VOUCHER_DROP",
            tx_type="voucher_create",
            amount_uzs=cost,
            plan_code=payload.gift_type,
            note=f"🎫 Oltin Chipta yaratildi: {code}",
        )
    )
    await db.commit()
    return {
        "code": code,
        "gift_type": payload.gift_type,
        "value_uzs": cost,
        "wallet_balance_uzs": user.wallet_balance_uzs,
    }


@app.post("/api/wallet/voucher/claim")
async def claim_gift_voucher(
    payload: VoucherClaimPayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    clean_code = payload.code.strip().upper()
    voucher = await db.scalar(select(GiftVoucher).where(func.upper(GiftVoucher.code) == clean_code))
    if not voucher:
        raise HTTPException(status_code=404, detail="Bunday Oltin Chipta kodi topilmadi!")
    if voucher.is_claimed:
        raise HTTPException(status_code=400, detail=f"Ushbu chipta allaqachon @{voucher.claimed_by_username} tomonidan faollashtirilgan!")

    claimer_handle = user.cine_username or user.username or "kinoman"
    voucher.is_claimed = True
    voucher.claimed_by_username = claimer_handle

    if voucher.gift_type in ("vip_1m", "vip_3m"):
        days = 30 if voucher.gift_type == "vip_1m" else 90
        user.is_vip = True
        user.vip_tier = "premium_vip" if days >= 90 else "standard_vip"
        user.vip_expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    else:
        user.wallet_balance_uzs += voucher.value_uzs

    db.add(
        WalletTransaction(
            sender_id=voucher.creator_id,
            receiver_id=user.id,
            sender_username=voucher.creator_username,
            receiver_username=claimer_handle,
            tx_type="voucher_claim",
            amount_uzs=voucher.value_uzs,
            plan_code=voucher.gift_type,
            note=f"🎉 Oltin Chipta ({voucher.code}) faollashtirildi!",
        )
    )
    await db.commit()
    return {
        "status": "claimed",
        "code": voucher.code,
        "gift_type": voucher.gift_type,
        "value_uzs": voucher.value_uzs,
    }


# ----------------------------------------------------------------------------
# 3-MODUL: DONAT & CROWDFUNDING (Xalqona Dublyaj Fondi & Patron Tiers)
# ----------------------------------------------------------------------------
@app.get("/api/crowdfunding")
async def get_crowdfunding_and_patrons(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    campaigns = list(
        (
            await db.scalars(
                select(CrowdfundingCampaign).order_by(CrowdfundingCampaign.id)
            )
        ).all()
    )
    donations = list(
        (
            await db.scalars(
                select(CampaignDonation).order_by(desc(CampaignDonation.id)).limit(20)
            )
        ).all()
    )
    top_patrons = list(
        (
            await db.scalars(
                select(User)
                .where(User.total_donated_uzs > 0)
                .order_by(desc(User.total_donated_uzs))
                .limit(10)
            )
        ).all()
    )

    return {
        "campaigns": [
            {
                "id": c.id,
                "movie_code": c.movie_code,
                "title": c.title,
                "target_type": c.target_type,
                "description": c.description,
                "goal_uzs": c.goal_uzs,
                "collected_uzs": c.collected_uzs,
                "progress_pct": min(100, round((c.collected_uzs / max(1, c.goal_uzs)) * 100, 1)),
                "donors_count": c.donors_count,
                "status": c.status,
                "deadline_days": c.deadline_days,
                "poster_url": c.poster_url,
            }
            for c in campaigns
        ],
        "recent_donations": [
            {
                "id": d.id,
                "campaign_id": d.campaign_id,
                "movie_code": d.movie_code,
                "cine_username": d.cine_username,
                "user_full_name": d.user_full_name,
                "patron_tier": d.patron_tier,
                "amount_uzs": d.amount_uzs,
                "message": d.message,
            }
            for d in donations
        ],
        "hall_of_fame": [
            {
                "rank": idx + 1,
                "cine_username": u.cine_username or u.username or "kinoman",
                "full_name": u.full_name,
                "avatar_url": u.avatar_url,
                "patron_tier": u.patron_tier,
                "total_donated_uzs": u.total_donated_uzs,
                "badges": u.badges or [],
            }
            for idx, u in enumerate(top_patrons)
        ],
    }


@app.post("/api/crowdfunding/donate")
async def donate_to_crowdfunding(
    payload: CrowdfundingDonatePayload,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await get_or_create_user(db, payload.telegram_id)
    camp = await db.scalar(
        select(CrowdfundingCampaign).where(CrowdfundingCampaign.id == payload.campaign_id)
    )
    if not camp:
        raise HTTPException(status_code=404, detail="Crowdfunding kampaniyasi topilmadi")

    amount = max(5000, payload.amount_uzs)
    if user.wallet_balance_uzs < amount:
        raise HTTPException(
            status_code=400,
            detail=f"CineWallet balansingizda mablag' yetarli emas ({user.wallet_balance_uzs:,} UZS). Avval hamyonni to'ldiring!",
        )

    user.wallet_balance_uzs -= amount
    user.total_donated_uzs += amount
    new_tier = compute_patron_tier(user.total_donated_uzs)
    user.patron_tier = new_tier

    tier_badge_map = {
        "bronze": "🥉 Bronze Homiy",
        "silver": "🥈 Silver Patron",
        "gold": "🥇 Gold Legend",
    }
    badge_label = tier_badge_map.get(new_tier)
    current_badges = list(user.badges or [])
    if badge_label and badge_label not in current_badges:
        current_badges.append(badge_label)
        user.badges = current_badges

    camp.collected_uzs += amount
    camp.donors_count += 1
    if camp.collected_uzs >= camp.goal_uzs:
        camp.status = "completed"

    sender_handle = user.cine_username or user.username or "kinoman"
    db.add(
        CampaignDonation(
            campaign_id=camp.id,
            movie_code=camp.movie_code,
            user_id=user.id,
            cine_username=sender_handle,
            user_full_name=user.full_name,
            patron_tier=user.patron_tier,
            amount_uzs=amount,
            message=payload.message,
        )
    )
    db.add(
        WalletTransaction(
            sender_id=user.id,
            receiver_id=None,
            sender_username=sender_handle,
            receiver_username="CROWDFUND_ESCROW",
            tx_type="crowdfunding",
            amount_uzs=amount,
            note=f"🎬 «{camp.title}» fondiga homiylik hissasi",
        )
    )
    await db.commit()
    return {
        "status": "donated",
        "campaign_id": camp.id,
        "collected_uzs": camp.collected_uzs,
        "goal_uzs": camp.goal_uzs,
        "patron_tier": user.patron_tier,
        "total_donated_uzs": user.total_donated_uzs,
        "wallet_balance_uzs": user.wallet_balance_uzs,
    }


# ============================================================================
# 11. ULTRA-LIGHTWEIGHT SINGLE-PORT SERVING (Serves React 19 TMA from Port 8000)
# ============================================================================
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

