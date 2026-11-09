from datetime import date, datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


# ============================================================================
# 1. FOYDALANUVCHILAR VA XAVFSIZLIK (Users & Security + Referral + VIP Tiers)
# ============================================================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), default="Kinoman")
    language: Mapped[str] = mapped_column(String(5), default="uz")

    # 3-Tier Subscription ('free', 'standard_vip', 'premium_vip')
    vip_tier: Mapped[str] = mapped_column(String(20), default="free")
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    vip_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Kids Mode & App Lock (PIN + Biometrics)
    is_kids_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    kids_mode_pin: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    theme_preference: Mapped[str] = mapped_column(String(10), default="system")  # 'dark', 'light', 'system'
    is_app_lock_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    app_lock_pin_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Referral & Instagram Growth Gate
    referral_code: Mapped[Optional[str]] = mapped_column(String(32), unique=True, nullable=True)
    referred_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    instagram_reward_claimed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # ========================================================================
    # CINESOCIAL & ECONOMY ADDON (CineProfile, CineWallet, Patron Tiers)
    # ========================================================================
    cine_username: Mapped[Optional[str]] = mapped_column(String(40), unique=True, nullable=True, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(280), default="Kino va seriallar olami ishqibozi 🎬")
    favorite_genres: Mapped[List[str]] = mapped_column(JSON, default=list)
    badges: Mapped[List[str]] = mapped_column(JSON, default=list)
    patron_tier: Mapped[str] = mapped_column(String(20), default="none")  # 'none', 'bronze', 'silver', 'gold'
    total_donated_uzs: Mapped[int] = mapped_column(Integer, default=0)

    # Dual-Balance Wallet (Real Transferable vs Bonus Non-Transferable)
    wallet_balance_uzs: Mapped[int] = mapped_column(Integer, default=45000)
    bonus_balance_uzs: Mapped[int] = mapped_column(Integer, default=15000)

    # Social Graph & Privacy
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    following_count: Mapped[int] = mapped_column(Integer, default=0)
    total_likes_received: Mapped[int] = mapped_column(Integer, default=0)
    mention_privacy: Mapped[str] = mapped_column(String(20), default="all")  # 'all', 'following', 'none'
    hide_watch_history: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# 2. FRANSHIZALAR VA KOINOTLAR (Movie Universes: Marvel, DC, Harry Potter...)
# ============================================================================
class Franchise(Base):
    __tablename__ = "franchises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    banner_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    movies: Mapped[List["Movie"]] = relationship("Movie", back_populates="franchise")


# ============================================================================
# 3. KINOLAR VA SERIALLAR KATALOGI (Full Catalog + Cultural Hubs + Skip Intro)
# ============================================================================
class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 'movie', 'series', 'short', 'standup', 'doc', 'cartoon'
    content_type: Mapped[str] = mapped_column(String(20), default="movie", index=True)
    # 'action', 'comedy', 'thriller', 'drama', 'scifi', 'cartoon', 'family',
    # 'uzbek_classic', 'uzbek_modern', 'turkish', 'kdrama', 'indian', 'doc', 'short', 'standup'
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    # 'uzbek', 'turkish', 'korean', 'english', 'german', 'chinese', 'qazaq', 'russian'
    language_hub: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    cefr_level: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 'A1', 'A2', 'B1', 'B2', 'C1'

    franchise_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("franchises.id", ondelete="SET NULL"), nullable=True
    )
    franchise_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    year: Mapped[int] = mapped_column(Integer, default=2024)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=120)
    imdb_rating: Mapped[float] = mapped_column(Float, default=7.5)
    age_rating: Mapped[str] = mapped_column(String(10), default="12+")  # '0+', '6+', '12+', '16+', '18+'
    country: Mapped[str] = mapped_column(String(60), default="O'zbekiston")
    director: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    cast_list: Mapped[List[str]] = mapped_column(JSON, default=list)

    poster_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    backdrop_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trailer_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Netflix-grade Skip Intro & Skip Credits markers (seconds)
    intro_start_sec: Mapped[Optional[int]] = mapped_column(Integer, default=15)
    intro_end_sec: Mapped[Optional[int]] = mapped_column(Integer, default=75)
    credits_start_sec: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    is_family_friendly: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vip_only: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count_weekly: Mapped[int] = mapped_column(Integer, default=0, index=True)
    view_count_total: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    franchise: Mapped[Optional["Franchise"]] = relationship("Franchise", back_populates="movies")
    seasons: Mapped[List["Season"]] = relationship("Season", back_populates="movie", cascade="all, delete-orphan")
    media_files: Mapped[List["MovieMedia"]] = relationship(
        "MovieMedia", back_populates="movie", cascade="all, delete-orphan"
    )


# ============================================================================
# 4. SERIAL FASLLARI VA EPIZODLARI (Season / Episode Selector)
# ============================================================================
class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    season_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    movie: Mapped["Movie"] = relationship("Movie", back_populates="seasons")
    episodes: Mapped[List["Episode"]] = relationship("Episode", back_populates="season", cascade="all, delete-orphan")


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=45)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    intro_start_sec: Mapped[Optional[int]] = mapped_column(Integer, default=10)
    intro_end_sec: Mapped[Optional[int]] = mapped_column(Integer, default=65)

    season: Mapped["Season"] = relationship("Season", back_populates="episodes")
    media_files: Mapped[List["MovieMedia"]] = relationship(
        "MovieMedia", back_populates="episode", cascade="all, delete-orphan"
    )


# ============================================================================
# 5. MEDIA FAYLLAR, DUAL SUBTITRLAR VA MTPROTO STREAMING
# ============================================================================
class MovieMedia(Base):
    __tablename__ = "movie_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    episode_id: Mapped[Optional[int]] = mapped_column(ForeignKey("episodes.id", ondelete="CASCADE"), nullable=True)
    resolution: Mapped[str] = mapped_column(String(10), nullable=False)  # '480p', '720p', '1080p'
    telegram_file_id: Mapped[str] = mapped_column(Text, nullable=False)
    storage_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    storage_message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stream_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size_mb: Mapped[float] = mapped_column(Float, default=450.0)

    # {"uz": "O'zbekcha Dublyaj", "tr": "Original Türkçe", "en": "Original English", "ru": "Русский"}
    audio_tracks: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    # {"uz": [...cues...], "en": [...cues...], "tr": [...cues...], "ko": [...cues...]}
    subtitles: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    is_offline_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    protect_content: Mapped[bool] = mapped_column(Boolean, default=True)

    movie: Mapped["Movie"] = relationship("Movie", back_populates="media_files")
    episode: Mapped[Optional["Episode"]] = relationship("Episode", back_populates="media_files")


# ============================================================================
# 6. TOMOSHA JARAYONI (Resume Playback — Fixed Episode Unique Constraint!)
# ============================================================================
class WatchProgress(Base):
    __tablename__ = "watch_progress"
    __table_args__ = (UniqueConstraint("user_id", "movie_id", "episode_id", name="uq_user_movie_episode"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    episode_id: Mapped[Optional[int]] = mapped_column(ForeignKey("episodes.id", ondelete="CASCADE"), nullable=True)
    last_timestamp: Mapped[int] = mapped_column(Integer, default=0)  # in seconds
    duration_seconds: Mapped[int] = mapped_column(Integer, default=7200)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ============================================================================
# 7. GEYMIFIKATSIYA: FAOLLIK XARITASI (HEATMAP), STREAK VA MARAFON
# ============================================================================
class UserStreak(Base):
    __tablename__ = "user_streaks"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    max_streak: Mapped[int] = mapped_column(Integer, default=0)
    marathon_points: Mapped[int] = mapped_column(Integer, default=0, index=True)
    total_watch_minutes: Mapped[int] = mapped_column(Integer, default=0)
    challenge_30_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    last_active_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"
    __table_args__ = (UniqueConstraint("user_id", "activity_date", name="uq_user_activity_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_date: Mapped[date] = mapped_column(Date, default=date.today)
    watch_minutes: Mapped[int] = mapped_column(Integer, default=0)


# ============================================================================
# 8. MARKETING, INSTAGRAM REELS VORONKASI VA UTM KONVERSIYA
# ============================================================================
class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), default="instagram_reels")
    utm_campaign: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    movie_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    clicks_count: Mapped[int] = mapped_column(Integer, default=0)
    conversions_count: Mapped[int] = mapped_column(Integer, default=0)
    vip_sales_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# 9. REQUEST DESK VA TAKLIF-SHIKOYATLAR (CRM)
# ============================================================================
class MovieRequest(Base):
    __tablename__ = "movie_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    query_text: Mapped[str] = mapped_column(String(255), nullable=False)
    votes_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # 'pending', 'uploaded', 'rejected'
    admin_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FeedbackTicket(Base):
    __tablename__ = "feedback_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ticket_type: Mapped[str] = mapped_column(String(30), nullable=False)  # 'bug', 'quality', 'idea', 'partnership'
    message: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")  # 'open', 'resolved'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# 10. EKSKLYUZIV QO'SHIMCHALAR (PRD v7.0 KILLER FEATURES)
# ============================================================================

# 10.1. Interactive Smart Subtitles — Shaxsiy Lug'at (Edu-Cinema Flashcards)
class UserVocabulary(Base):
    __tablename__ = "user_vocabulary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id: Mapped[Optional[int]] = mapped_column(ForeignKey("movies.id", ondelete="SET NULL"), nullable=True)
    word: Mapped[str] = mapped_column(String(120), nullable=False)
    translation: Mapped[str] = mapped_column(String(255), nullable=False)
    source_lang: Mapped[str] = mapped_column(String(10), default="en")
    context_sentence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp_sec: Mapped[int] = mapped_column(Integer, default=0)
    mastery_level: Mapped[int] = mapped_column(Integer, default=1)  # 1..5 spaced repetition
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 10.2. Spoylersiz Sharhlar, Zanjirli Izohlar, @Atmetka va Vaqt Kodlari (Threaded Social Comments)
class MovieReview(Base):
    __tablename__ = "movie_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_name: Mapped[str] = mapped_column(String(120), default="Kinoman")
    cine_username: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, index=True)
    user_avatar: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_badges: Mapped[List[str]] = mapped_column(JSON, default=list)
    patron_tier: Mapped[str] = mapped_column(String(20), default="none")

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("movie_reviews.id", ondelete="CASCADE"), nullable=True, index=True
    )
    reply_to_username: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    timestamp_sec: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    rating: Mapped[int] = mapped_column(Integer, default=10)  # 1..10
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    has_spoiler: Mapped[bool] = mapped_column(Boolean, default=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    awards_count: Mapped[int] = mapped_column(Integer, default=0)
    awards_uzs: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 10.3. Sevimlilar va Keyinroq Ko'rish (Watchlist & Favorites)
class Watchlist(Base):
    __tablename__ = "watchlist"
    __table_args__ = (UniqueConstraint("user_id", "movie_id", "list_type", name="uq_user_movie_list"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    list_type: Mapped[str] = mapped_column(String(20), default="favorite")  # 'favorite', 'watch_later'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 10.4. Kino Reels (Vertikal Shorts Tizerlar Oqimi)
class CinemaReel(Base):
    __tablename__ = "cinema_reels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=120)
    views_count: Mapped[int] = mapped_column(Integer, default=1450)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 10.5. Majburiy Homiy Kanallar (Sponsor Channels & OP Rotation)
class SponsorChannel(Base):
    __tablename__ = "sponsor_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    channel_id: Mapped[str] = mapped_column(String(60), nullable=False)  # '@channel' or '-100...'
    invite_link: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str] = mapped_column(String(20), default="telegram")  # 'telegram', 'instagram'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_subscribers: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    joined_count: Mapped[int] = mapped_column(Integer, default=0)


# 10.6. To'lovlar Tarixi (Telegram Stars, Payme, Click)
class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # 'stars', 'payme', 'click', 'bonus'
    plan_code: Mapped[str] = mapped_column(String(30), nullable=False)  # 'vip_1m', 'vip_3m', 'vip_1y'
    amount_uzs: Mapped[int] = mapped_column(Integer, default=0)
    stars_amount: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 10.7. Oyna-Botlar (Mirror Bots — Anti-Ban Partner Ecosystem)
class MirrorBot(Base):
    __tablename__ = "mirror_bots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    bot_username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    bot_token_masked: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    users_referred: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# 11. CINESOCIAL, CINEWALLET & CROWDFUNDING MODULLARI (PRD v8.0 ADDON)
# ============================================================================

# 11.1. Obunachilar va Do'stlar Grafi (Followers / Following)
class UserFollow(Base):
    __tablename__ = "user_follows"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follower_following"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    following_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 11.2. Ichki Ijtimoiy Bildirishnomalar (@Atmetka, Sovg'a, Izoh javobi, Mukofot)
class SocialNotification(Base):
    __tablename__ = "social_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_username: Mapped[str] = mapped_column(String(60), nullable=False)
    # 'mention', 'reply', 'gift', 'award', 'follow', 'crowdfunding'
    notif_type: Mapped[str] = mapped_column(String(30), default="mention")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    movie_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 11.3. Shaxsiy Kino-Kolleksiyalar (Public Custom Movie Lists in CineProfile)
class CustomMovieList(Base):
    __tablename__ = "custom_movie_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    cine_username: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(280), nullable=True)
    movie_codes: Mapped[List[int]] = mapped_column(JSON, default=list)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 11.4. CineWallet Double-Entry Ledger (Hamyon va Hadya Tranzaksiyalari)
class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    receiver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    sender_username: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    receiver_username: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    # 'topup', 'gift_vip', 'gift_balance', 'comment_award', 'crowdfunding', 'voucher_create', 'voucher_claim'
    tx_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    amount_uzs: Mapped[int] = mapped_column(Integer, default=0)
    plan_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 11.5. Gift Voucher ("Oltin Chipta" — Guruhga yoki Do'stga Ulashiladigan Sovg'a Kodi)
class GiftVoucher(Base):
    __tablename__ = "gift_vouchers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_username: Mapped[str] = mapped_column(String(40), nullable=False)
    gift_type: Mapped[str] = mapped_column(String(30), default="vip_1m")  # 'vip_1m', 'vip_3m', 'balance'
    value_uzs: Mapped[int] = mapped_column(Integer, default=29000)
    message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_claimed: Mapped[bool] = mapped_column(Boolean, default=False)
    claimed_by_username: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 11.6. Xalqona Dublyaj va 4K Reliz Crowdfunding Kampaniyalari (3-MODUL)
class CrowdfundingCampaign(Base):
    __tablename__ = "crowdfunding_campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    target_type: Mapped[str] = mapped_column(String(40), default="dubbing_uz")  # 'dubbing_uz', 'remaster_4k', 'server_fund'
    description: Mapped[str] = mapped_column(Text, nullable=False)
    goal_uzs: Mapped[int] = mapped_column(Integer, default=1500000)
    collected_uzs: Mapped[int] = mapped_column(Integer, default=0)
    donors_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")  # 'active', 'completed', 'refunded'
    deadline_days: Mapped[int] = mapped_column(Integer, default=14)
    poster_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# 11.7. Kampaniya Homiylari va Film Titridagi Oltin Homiylar (Movie Patron Credits)
class CampaignDonation(Base):
    __tablename__ = "campaign_donations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("crowdfunding_campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    movie_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cine_username: Mapped[str] = mapped_column(String(40), nullable=False)
    user_full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    patron_tier: Mapped[str] = mapped_column(String(20), default="bronze")
    amount_uzs: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

