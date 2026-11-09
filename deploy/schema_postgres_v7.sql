-- ============================================================================
-- CNMOVI — DEFINITIVE POSTGRESQL 16 SCHEMA (PRD v7.0 COMPLETE EDITION)
-- All 9 Original PRD v6.0 Tables + 8 Exclusive v7.0 Modules
-- ============================================================================

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    full_name VARCHAR(255) DEFAULT 'Kinoman',
    language VARCHAR(5) DEFAULT 'uz',
    vip_tier VARCHAR(20) DEFAULT 'free',
    is_vip BOOLEAN DEFAULT FALSE,
    vip_expires_at TIMESTAMP WITH TIME ZONE,
    is_kids_mode BOOLEAN DEFAULT FALSE,
    kids_mode_pin VARCHAR(4),
    theme_preference VARCHAR(10) DEFAULT 'system',
    is_app_lock_enabled BOOLEAN DEFAULT FALSE,
    app_lock_pin_hash VARCHAR(255),
    referral_code VARCHAR(32) UNIQUE,
    referred_by_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    instagram_reward_claimed BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE franchises (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(60) UNIQUE NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    banner_url TEXT,
    logo_url TEXT
);

CREATE TABLE movies (
    id BIGSERIAL PRIMARY KEY,
    code INT UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    original_title VARCHAR(255),
    description TEXT,
    content_type VARCHAR(20) DEFAULT 'movie',
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    language_hub VARCHAR(20),
    cefr_level VARCHAR(10),
    franchise_id BIGINT REFERENCES franchises(id) ON DELETE SET NULL,
    franchise_order INT,
    year INT,
    duration_minutes INT DEFAULT 120,
    imdb_rating NUMERIC(3, 1),
    age_rating VARCHAR(10) DEFAULT '12+',
    country VARCHAR(60) DEFAULT 'O''zbekiston',
    director VARCHAR(120),
    cast_list JSONB DEFAULT '[]',
    poster_url TEXT,
    backdrop_url TEXT,
    trailer_url TEXT,
    intro_start_sec INT DEFAULT 15,
    intro_end_sec INT DEFAULT 75,
    credits_start_sec INT,
    is_family_friendly BOOLEAN DEFAULT FALSE,
    is_vip_only BOOLEAN DEFAULT FALSE,
    view_count_weekly INT DEFAULT 0,
    view_count_total INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE seasons (
    id BIGSERIAL PRIMARY KEY,
    movie_id BIGINT REFERENCES movies(id) ON DELETE CASCADE,
    season_number INT NOT NULL,
    title VARCHAR(100)
);

CREATE TABLE episodes (
    id BIGSERIAL PRIMARY KEY,
    season_id BIGINT REFERENCES seasons(id) ON DELETE CASCADE,
    episode_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    duration_minutes INT DEFAULT 45,
    thumbnail_url TEXT,
    intro_start_sec INT DEFAULT 10,
    intro_end_sec INT DEFAULT 65
);

CREATE TABLE movie_media (
    id BIGSERIAL PRIMARY KEY,
    movie_id BIGINT REFERENCES movies(id) ON DELETE CASCADE,
    episode_id BIGINT REFERENCES episodes(id) ON DELETE CASCADE,
    resolution VARCHAR(10) NOT NULL,
    telegram_file_id TEXT NOT NULL,
    storage_channel_id BIGINT,
    storage_message_id INT,
    stream_url TEXT,
    file_size_mb NUMERIC(8, 2) DEFAULT 450.0,
    audio_tracks JSONB DEFAULT '{}',
    subtitles JSONB DEFAULT '{}',
    is_offline_allowed BOOLEAN DEFAULT TRUE,
    protect_content BOOLEAN DEFAULT TRUE
);

CREATE TABLE watch_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    movie_id BIGINT REFERENCES movies(id) ON DELETE CASCADE,
    episode_id BIGINT REFERENCES episodes(id) ON DELETE CASCADE,
    last_timestamp INT NOT NULL DEFAULT 0,
    duration_seconds INT NOT NULL DEFAULT 7200,
    is_completed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, movie_id, episode_id)
);

CREATE TABLE user_streaks (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    current_streak INT DEFAULT 0,
    max_streak INT DEFAULT 0,
    marathon_points INT DEFAULT 0,
    total_watch_minutes INT DEFAULT 0,
    challenge_30_completed BOOLEAN DEFAULT FALSE,
    last_active_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE user_activity_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    activity_date DATE DEFAULT CURRENT_DATE,
    watch_minutes INT DEFAULT 0,
    UNIQUE (user_id, activity_date)
);

CREATE TABLE user_vocabulary (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    movie_id BIGINT REFERENCES movies(id) ON DELETE SET NULL,
    word VARCHAR(120) NOT NULL,
    translation VARCHAR(255) NOT NULL,
    source_lang VARCHAR(10) DEFAULT 'en',
    context_sentence TEXT,
    timestamp_sec INT DEFAULT 0,
    mastery_level INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE movie_reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    user_name VARCHAR(120) DEFAULT 'Kinoman',
    movie_id BIGINT REFERENCES movies(id) ON DELETE CASCADE,
    rating INT DEFAULT 10,
    comment TEXT NOT NULL,
    has_spoiler BOOLEAN DEFAULT FALSE,
    likes_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE cinema_reels (
    id BIGSERIAL PRIMARY KEY,
    movie_id BIGINT REFERENCES movies(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    caption TEXT,
    video_url TEXT NOT NULL,
    likes_count INT DEFAULT 0,
    views_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE marketing_campaigns (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    utm_campaign VARCHAR(100) UNIQUE NOT NULL,
    movie_code INT,
    clicks_count INT DEFAULT 0,
    conversions_count INT DEFAULT 0,
    vip_sales_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE movie_requests (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    query_text VARCHAR(255) NOT NULL,
    votes_count INT DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending',
    admin_reply TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE feedback_tickets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    ticket_type VARCHAR(30) NOT NULL,
    message TEXT NOT NULL,
    media_url TEXT,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
