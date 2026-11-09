from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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

# High-reliability open MP4 streams for instant local playback testing
SAMPLE_STREAM_1080P = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
SAMPLE_STREAM_720P = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
SAMPLE_STREAM_480P = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
SAMPLE_REEL_1 = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
SAMPLE_REEL_2 = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
SAMPLE_REEL_3 = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"

DEFAULT_DUAL_SUBTITLES = {
    "en": [
        {"start": 0, "end": 6, "text": "In the silence of the cosmos, every second counts for humanity."},
        {"start": 6, "end": 12, "text": "We must transcend our limits and discover the unknown horizon."},
        {"start": 12, "end": 19, "text": "Courage is not the absence of fear, but acting despite the darkness."},
        {"start": 19, "end": 26, "text": "Hold the line! The destiny of our world depends on this mission."},
        {"start": 26, "end": 35, "text": "Remember every promise we made before leaving Earth behind."},
        {"start": 35, "end": 45, "text": "Wait—look at the signal coming from the quantum gateway!"},
        {"start": 45, "end": 60, "text": "Now we know that love and time can cross any dimension."},
    ],
    "uz": [
        {"start": 0, "end": 6, "text": "Koinot sukunatida insoniyat uchun har bir soniya g'animat."},
        {"start": 6, "end": 12, "text": "Biz o'z chegaralarimizdan oshib, noma'lum ufqni kashf etishimiz shart."},
        {"start": 12, "end": 19, "text": "Jasorat — qo'rquvning yo'qligi emas, zulmatga qaramay harakat qilishdir."},
        {"start": 19, "end": 26, "text": "Chekinmang! Dunyomiz taqdiri mana shu missiyaga bog'liq."},
        {"start": 26, "end": 35, "text": "Yerni tark etishdan oldin bergan har bir va'damizni eslang."},
        {"start": 35, "end": 45, "text": "To'xtang — kvant darvozasidan kelayotgan signalga qarang!"},
        {"start": 45, "end": 60, "text": "Endi bilamizki, muhabbat va vaqt har qanday o'lchamni kesib o'ta oladi."},
    ],
    "tr": [
        {"start": 0, "end": 6, "text": "Evrenin sessizliğinde insanlık için her saniye önemlidir."},
        {"start": 6, "end": 12, "text": "Sınırlarımızı aşmalı ve bilinmeyen ufku keşfetmeliyiz."},
        {"start": 12, "end": 19, "text": "Cesaret korkunun yokluğu değil, karanlığa rağmen harekete geçmektir."},
        {"start": 19, "end": 26, "text": "Hattı koruyun! Dünyamızın kaderi bu göreve bağlı."},
        {"start": 26, "end": 35, "text": "Dünyayı geride bırakmadan önce verdiğimiz her sözü hatırlayın."},
        {"start": 35, "end": 45, "text": "Bekle—kuantum kapısından gelen sinyale bak!"},
        {"start": 45, "end": 60, "text": "Artık sevginin ve zamanın her boyutu aşabileceğini biliyoruz."},
    ],
    "ko": [
        {"start": 0, "end": 6, "text": "우주의 침묵 속에서 인류에게 매 순간이 소중합니다."},
        {"start": 6, "end": 12, "text": "우리는 한계를 넘어 미지의 지평선을 발견해야 합니다."},
        {"start": 12, "end": 19, "text": "용기란 두려움이 없는 것이 아니라 어둠 속에서도 행동하는 것입니다."},
        {"start": 19, "end": 26, "text": "물러서지 마세요! 우리 세계의 운명이 이 임무에 달려 있습니다."},
    ],
}


async def seed_initial_data(db: AsyncSession) -> None:
    existing = await db.scalar(select(Movie.id).limit(1))
    if existing:
        return

    # 1. Create Demo / Admin Users with Independent CineProfile & Dual-Balance CineWallet
    admin_user = User(
        telegram_id=123456789,
        username="nodirbek_admin",
        cine_username="kinochi_nodir",
        full_name="Nodirbek ✦ Founder",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=240&q=80",
        bio="CNMOVI asoschisi. Kristofer Nolan, Marvel va O'zbek Oltin Fondi ashaddiy muxlisi 🎬",
        favorite_genres=["Sci-Fi", "O'zbek Klassika", "Blokbaster"],
        badges=["✦ Founder", "🥇 Gold Legend", "✦ Ekspert"],
        patron_tier="gold",
        total_donated_uzs=250000,
        wallet_balance_uzs=145000,
        bonus_balance_uzs=25000,
        followers_count=128,
        following_count=14,
        total_likes_received=640,
        language="uz",
        vip_tier="premium_vip",
        is_vip=True,
        vip_expires_at=datetime.now(timezone.utc) + timedelta(days=365),
        theme_preference="dark",
        referral_code="CNMOVI_BOSS",
        is_admin=True,
    )
    user_2 = User(
        telegram_id=987654321,
        username="malika_cinema",
        cine_username="marvel_malika",
        full_name="Malika Karimova",
        avatar_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=240&q=80",
        bio="K-Drama, Turk seriallari va Edu-Cinema C1 til o'rganuvchisi 🌸",
        favorite_genres=["K-Drama", "Turk Serial", "Fentezi"],
        badges=["🥈 Silver Patron", "✦ Kinotanqidchi"],
        patron_tier="silver",
        total_donated_uzs=75000,
        wallet_balance_uzs=68000,
        bonus_balance_uzs=10000,
        followers_count=84,
        following_count=22,
        total_likes_received=310,
        language="uz",
        vip_tier="standard_vip",
        is_vip=True,
        vip_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        referral_code="MALIKA77",
    )
    user_3 = User(
        telegram_id=555666777,
        username="javohir_edu",
        cine_username="javohir_cine",
        full_name="Javohir Bek",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=240&q=80",
        bio="Tarixiy epik filmlar va hujjatli ilm-fan shaydosi 🌍",
        favorite_genres=["Tarixiy Epik", "Hujjatli BBC"],
        badges=["🥉 Bronze Homiy"],
        patron_tier="bronze",
        total_donated_uzs=20000,
        wallet_balance_uzs=35000,
        bonus_balance_uzs=5000,
        followers_count=39,
        following_count=18,
        total_likes_received=95,
        language="uz",
        vip_tier="free",
        is_vip=False,
        referral_code="JAVOHIR99",
    )
    db.add_all([admin_user, user_2, user_3])
    await db.flush()

    # 2. Streaks & 30-Day Activity Heatmap
    today = date.today()
    db.add_all(
        [
            UserStreak(
                user_id=admin_user.id,
                current_streak=19,
                max_streak=28,
                marathon_points=1480,
                total_watch_minutes=2640,
                last_active_date=today,
            ),
            UserStreak(
                user_id=user_2.id,
                current_streak=26,
                max_streak=26,
                marathon_points=1320,
                total_watch_minutes=1980,
                last_active_date=today,
            ),
            UserStreak(
                user_id=user_3.id,
                current_streak=9,
                max_streak=14,
                marathon_points=890,
                total_watch_minutes=940,
                last_active_date=today,
            ),
        ]
    )

    for i in range(30):
        day = today - timedelta(days=i)
        mins = 0 if i in (21, 25) else (25 + ((i * 17) % 95))
        db.add(UserActivityLog(user_id=admin_user.id, activity_date=day, watch_minutes=mins))

    # 3. Franchises & Movie Universes
    f_marvel = Franchise(
        slug="marvel-universe",
        title="Marvel Koinoti (MCU)",
        description="Temir Odamdan tortib Qasoskorlar: Intihogacha xronologik tartibdagi superqahramonlik koinoti.",
        banner_url="https://images.unsplash.com/photo-1635805737707-575885ab0820?auto=format&fit=crop&w=1200&q=80",
    )
    f_uzbek_gold = Franchise(
        slug="uzbek-golden-fund",
        title="O'zbek Milliy Oltin Fondi",
        description="Restavratsiya qilingan 4K/HD o'lchamdagi o'lmas o'zbek klassik durdonalari.",
        banner_url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1200&q=80",
    )
    f_harry = Franchise(
        slug="wizarding-world",
        title="Garri Potter va Sehrgarlar Olami",
        description="Xogvarts maktabi va sehrgarlar olamining barcha 8 qismi xronologik tartibda.",
        banner_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80",
    )
    db.add_all([f_marvel, f_uzbek_gold, f_harry])
    await db.flush()

    # 4. Movies & Series Across All Catalog Hubs
    movies_data = [
        # Code 421 — PRD signature example
        Movie(
            code=421,
            title="Qasoskorlar: Intiho",
            original_title="Avengers: Endgame",
            description="Tanos koinotning yarmini yo'q qilgandan so'ng, qolgan Qasoskorlar vaqtni ortga qaytarish uchun so'nggi hal qiluvchi jangga kirishadilar.",
            content_type="movie",
            category="action",
            subcategory="blockbuster",
            language_hub="english",
            cefr_level="B2",
            franchise_id=f_marvel.id,
            franchise_order=1,
            year=2019,
            duration_minutes=181,
            imdb_rating=8.4,
            age_rating="12+",
            country="AQSH",
            director="Anthony & Joe Russo",
            cast_list=["Robert Downey Jr.", "Chris Evans", "Scarlett Johansson", "Josh Brolin"],
            poster_url="https://images.unsplash.com/photo-1635805737707-575885ab0820?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1635805737707-575885ab0820?auto=format&fit=crop&w=1400&q=80",
            intro_start_sec=10,
            intro_end_sec=45,
            credits_start_sec=520,
            is_family_friendly=True,
            is_vip_only=False,
            view_count_weekly=14820,
            view_count_total=94300,
        ),
        # Code 101 — O'zbek Oltin Fondi (Retro Klassika) — intentionally only 480p & 720p to showcase Graceful Degradation when 1080p is clicked!
        Movie(
            code=101,
            title="Shum bola (Restavratsiya HD)",
            original_title="Шум бола",
            description="G'afur G'ulom asari asosida suratga olingan o'zbek kinosining oltin durdonasi. Qoravoyning sarguzashtlari maxsus rang va ovoz restavratsiyasida.",
            content_type="movie",
            category="uzbek_classic",
            subcategory="retro_gold",
            language_hub="uzbek",
            franchise_id=f_uzbek_gold.id,
            franchise_order=1,
            year=1977,
            duration_minutes=89,
            imdb_rating=8.9,
            age_rating="0+",
            country="O'zbekiston",
            director="Damir Salimov",
            cast_list=["Abduraim Abduvahobov", "Saidkarim Saidobidov", "Hamza Umarov"],
            poster_url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1400&q=80",
            intro_start_sec=5,
            intro_end_sec=35,
            is_family_friendly=True,
            is_vip_only=False,
            view_count_weekly=11250,
            view_count_total=82100,
        ),
        # Code 102 — Abdullajon
        Movie(
            code=102,
            title="Abdullajon",
            original_title="Abdullajon",
            description="O'zbek qishlog'iga tushib qolgan o'zga sayyoralik bola va ketmonlarning uchishi haqidagi afsonaviy fantastik komediya.",
            content_type="movie",
            category="uzbek_classic",
            subcategory="retro_gold",
            language_hub="uzbek",
            franchise_id=f_uzbek_gold.id,
            franchise_order=2,
            year=1991,
            duration_minutes=88,
            imdb_rating=8.6,
            age_rating="6+",
            country="O'zbekiston",
            director="Zulfiqor Musoqov",
            cast_list=["Shuhrat Qayumov", "Rajab Adashev", "To'ti Yusupova"],
            poster_url="https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1400&q=80",
            is_family_friendly=True,
            view_count_weekly=8430,
            view_count_total=61000,
        ),
        # Code 201 — Mendirman Jaloliddin (Milliy Tarixiy Epik Serial)
        Movie(
            code=201,
            title="Mendirman Jaloliddin",
            original_title="Mendirman Jaloliddin",
            description="Xorazmshohlar davlatining so'nggi hukmdori, jasur sarkarda Jaloliddin Manguberdining Chingizxonga qarshi mardonavor kurashi.",
            content_type="series",
            category="uzbek_modern",
            subcategory="historical_epic",
            language_hub="uzbek",
            year=2021,
            duration_minutes=55,
            imdb_rating=8.7,
            age_rating="12+",
            country="O'zbekiston / Turkiya",
            director="Metin Günay",
            cast_list=["Emre Kıvılcım", "Yulduz Rajabova", "Javohir Zokirov", "Tohir Saidov"],
            poster_url="https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=1400&q=80",
            intro_start_sec=8,
            intro_end_sec=42,
            is_family_friendly=True,
            view_count_weekly=13400,
            view_count_total=112000,
        ),
        # Code 301 — Turkish Drama Hub (Qurilish Usmon)
        Movie(
            code=301,
            title="Qurilish: Usmon",
            original_title="Kuruluş: Osman",
            description="Ertug'rul G'oziyning o'g'li Usmon Beyning buyuk davlatga asos solish yo'lidagi ichki va tashqi dushmanlarga qarshi kurashi. Turk va O'zbek subtitrlarida!",
            content_type="series",
            category="turkish",
            subcategory="historical_epic",
            language_hub="turkish",
            cefr_level="B1",
            year=2024,
            duration_minutes=120,
            imdb_rating=8.1,
            age_rating="12+",
            country="Turkiya",
            director="Metin Günay",
            cast_list=["Burak Özçivit", "Özge Törer", "Emre Bey"],
            poster_url="https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1400&q=80",
            intro_start_sec=10,
            intro_end_sec=50,
            is_family_friendly=True,
            view_count_weekly=16900,
            view_count_total=145000,
        ),
        # Code 401 — K-Drama Hub
        Movie(
            code=401,
            title="Kalmar O'yini (2-Fasl)",
            original_title="오징어 게임 (Squid Game)",
            description="Yashirin oroldagi omon qolish o'yinlariga qaytgan 456-raqamli ishtirokchi tizimni ichidan yo'q qilishga qaror qiladi. Original koreys talaffuzi va subtitrlar bilan.",
            content_type="series",
            category="kdrama",
            subcategory="thriller",
            language_hub="korean",
            cefr_level="A2",
            year=2024,
            duration_minutes=60,
            imdb_rating=8.3,
            age_rating="18+",
            country="Janubiy Koreya",
            director="Hwang Dong-hyuk",
            cast_list=["Lee Jung-jae", "Lee Byung-hun", "Wi Ha-joon"],
            poster_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1400&q=80",
            is_family_friendly=False,
            is_vip_only=True,
            view_count_weekly=19500,
            view_count_total=188000,
        ),
        # Code 502 — Edu-Cinema English Hub (Interstellar)
        Movie(
            code=502,
            title="Interstellar (Edu-Cinema Dual Sub)",
            original_title="Interstellar",
            description="Insoniyat kelajagini qutqarish uchun qurt inidan o'tib, o'zga galaktikaga yo'l olgan fazogirlar jamoasi. Ingliz tilini C1 darajada o'rganuvchilar uchun ideal film.",
            content_type="movie",
            category="scifi",
            subcategory="space_epic",
            language_hub="english",
            cefr_level="C1",
            year=2014,
            duration_minutes=169,
            imdb_rating=8.7,
            age_rating="12+",
            country="AQSH / Britaniya",
            director="Christopher Nolan",
            cast_list=["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"],
            poster_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1400&q=80",
            is_family_friendly=True,
            view_count_weekly=12800,
            view_count_total=99000,
        ),
        # Code 501 — Harry Potter Franchise
        Movie(
            code=501,
            title="Garri Potter va Hikmatlar Toshi",
            original_title="Harry Potter and the Sorcerer's Stone",
            description="O'n bir yoshli Garri o'zining haqiqiy sehrgar ekanini bilib, Xogvarts jodugarlik va sehrgarlik maktabiga yo'l oladi.",
            content_type="movie",
            category="scifi",
            subcategory="fantasy",
            language_hub="english",
            cefr_level="B1",
            franchise_id=f_harry.id,
            franchise_order=1,
            year=2001,
            duration_minutes=152,
            imdb_rating=7.6,
            age_rating="6+",
            country="Britaniya / AQSH",
            director="Chris Columbus",
            cast_list=["Daniel Radcliffe", "Emma Watson", "Rupert Grint"],
            poster_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1400&q=80",
            is_family_friendly=True,
            view_count_weekly=9700,
            view_count_total=84000,
        ),
        # Code 601 — Documentary & Science Hub
        Movie(
            code=601,
            title="Koinot Mo'jizalari: Vaqt va Kvant Olami",
            original_title="Wonders of the Universe (BBC)",
            description="Professor Brayan Koks bilan qora tuynuklar, yulduzlar tug'ilishi va vaqtning fizika qonunlari bo'ylab ilmiy sayohat.",
            content_type="doc",
            category="doc",
            subcategory="doc_nature",
            language_hub="english",
            cefr_level="B2",
            year=2023,
            duration_minutes=52,
            imdb_rating=9.0,
            age_rating="0+",
            country="Buyuk Britaniya",
            director="BBC Studios",
            cast_list=["Brian Cox"],
            poster_url="https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=1400&q=80",
            is_family_friendly=True,
            view_count_weekly=6400,
            view_count_total=41000,
        ),
        # Code 701 — Qisqa Metrajli Filmlar (5-20 daqiqa)
        Movie(
            code=701,
            title="So'nggi Bekat (Oskar Qisqa Metraj)",
            original_title="The Last Station",
            description="Atigi 14 daqiqa ichida inson umri, ota-ona qadri va kechirim haqida chuqur falsafiy hikoya qiluvchi festival g'olibi.",
            content_type="short",
            category="short",
            subcategory="festival_winner",
            language_hub="german",
            cefr_level="A2",
            year=2024,
            duration_minutes=14,
            imdb_rating=8.2,
            age_rating="6+",
            country="Germaniya",
            director="Lukas Weber",
            cast_list=["Hans Meyer", "Clara Schütt"],
            poster_url="https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?auto=format&fit=crop&w=1400&q=80",
            is_family_friendly=True,
            view_count_weekly=5100,
            view_count_total=29000,
        ),
        # Code 801 — Stand-Up & Live Show
        Movie(
            code=801,
            title="Toshkent Oqshomi — Katta Stand-Up Konsert",
            original_title="Tashkent Stand-Up Live",
            description="Zamonaviy o'zbek yoshlari, IT sohasi, oilaviy hayot va kundalik kulgili vaziyatlar haqida 100% jonli yumoristik konsert.",
            content_type="standup",
            category="standup",
            subcategory="live_comedy",
            language_hub="uzbek",
            year=2024,
            duration_minutes=74,
            imdb_rating=8.0,
            age_rating="12+",
            country="O'zbekiston",
            director="CNMOVI Originals",
            cast_list=["Mirshakar F.", "Indi StandUp Jamoasi"],
            poster_url="https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=1400&q=80",
            is_family_friendly=True,
            view_count_weekly=7800,
            view_count_total=53000,
        ),
        # Code 901 — Kengaytirilgan Multfilmlar Hubi (3D Pixar/DreamWorks)
        Movie(
            code=901,
            title="Kung Fu Panda 4",
            original_title="Kung Fu Panda 4",
            description="Ajdarho jangchisi Po Tinchlik vodiysiga yangi ma'naviy yetakchi izlab, Xameleon ismli qudratli sehrgarga duch keladi.",
            content_type="cartoon",
            category="cartoon",
            subcategory="modern_3d",
            language_hub="english",
            cefr_level="A1",
            year=2024,
            duration_minutes=94,
            imdb_rating=7.4,
            age_rating="0+",
            country="AQSH",
            director="Mike Mitchell",
            cast_list=["Jack Black", "Awkwafina", "Viola Davis"],
            poster_url="https://images.unsplash.com/photo-1560169897-fc0cdbdfa4d5?auto=format&fit=crop&w=600&q=80",
            backdrop_url="https://images.unsplash.com/photo-1560169897-fc0cdbdfa4d5?auto=format&fit=crop&w=1400&q=80",
            is_family_friendly=True,
            view_count_weekly=15200,
            view_count_total=121000,
        ),
    ]

    db.add_all(movies_data)
    await db.flush()

    # 5. Add Seasons & Episodes for Series (Mendirman Jaloliddin, Qurilish Usmon, Kalmar O'yini)
    for m in movies_data:
        if m.content_type == "series":
            season_1 = Season(movie_id=m.id, season_number=1, title="1-Fasl")
            season_2 = Season(movie_id=m.id, season_number=2, title="2-Fasl")
            db.add_all([season_1, season_2])
            await db.flush()

            episodes = [
                Episode(
                    season_id=season_1.id,
                    episode_number=1,
                    title="1-qism: Muqaddima va Qasamyod",
                    duration_minutes=52,
                    intro_start_sec=10,
                    intro_end_sec=45,
                ),
                Episode(
                    season_id=season_1.id,
                    episode_number=2,
                    title="2-qism: Yovuzlikka qarshi ilk jang",
                    duration_minutes=54,
                    intro_start_sec=10,
                    intro_end_sec=45,
                ),
                Episode(
                    season_id=season_1.id,
                    episode_number=3,
                    title="3-qism: Xiyonat va sadoqat sinovi",
                    duration_minutes=56,
                    intro_start_sec=10,
                    intro_end_sec=45,
                ),
                Episode(
                    season_id=season_2.id,
                    episode_number=1,
                    title="1-qism: Yangi davr boshlanishi",
                    duration_minutes=58,
                    intro_start_sec=12,
                    intro_end_sec=50,
                ),
            ]
            db.add_all(episodes)
            await db.flush()

            for ep in episodes:
                for res, url, size_mb in [
                    ("480p", SAMPLE_STREAM_480P, 220.0),
                    ("720p", SAMPLE_STREAM_720P, 480.0),
                    ("1080p", SAMPLE_STREAM_1080P, 950.0),
                ]:
                    db.add(
                        MovieMedia(
                            movie_id=m.id,
                            episode_id=ep.id,
                            resolution=res,
                            telegram_file_id=f"tg_file_{m.code}_ep{ep.id}_{res}",
                            stream_url=url,
                            file_size_mb=size_mb,
                            audio_tracks={
                                "uz": "O'zbekcha Professional Dublyaj",
                                "tr": "Original Türkçe",
                                "en": "Original Audio",
                                "ru": "Русский Дубляж",
                            },
                            subtitles=DEFAULT_DUAL_SUBTITLES,
                            is_offline_allowed=True,
                            protect_content=True,
                        )
                    )
        else:
            # For Code 101 (Shum bola), omit 1080p so user can experience Graceful Degradation to 720p!
            resolutions = [
                ("480p", SAMPLE_STREAM_480P, 310.0),
                ("720p", SAMPLE_STREAM_720P, 690.0),
            ]
            if m.code != 101:
                resolutions.append(("1080p", SAMPLE_STREAM_1080P, 1420.0))

            for res, url, size_mb in resolutions:
                db.add(
                    MovieMedia(
                        movie_id=m.id,
                        episode_id=None,
                        resolution=res,
                        telegram_file_id=f"tg_file_{m.code}_{res}",
                        stream_url=url,
                        file_size_mb=size_mb,
                        audio_tracks={
                            "uz": "O'zbekcha Dublyaj (5.1)",
                            "en": "Original English",
                            "ru": "Русский",
                        },
                        subtitles=DEFAULT_DUAL_SUBTITLES,
                        is_offline_allowed=True,
                        protect_content=True,
                    )
                )

    # 6. Watch Progress (Resume Playback demo)
    db.add(
        WatchProgress(
            user_id=admin_user.id,
            movie_id=movies_data[0].id,
            episode_id=None,
            last_timestamp=142,
            duration_seconds=580,
            is_completed=False,
        )
    )

    # 7. Interactive Smart Vocabulary (Edu-Cinema Pro Flashcards)
    db.add_all(
        [
            UserVocabulary(
                user_id=admin_user.id,
                movie_id=movies_data[0].id,
                word="transcend",
                translation="chegaradan oshib o'tmoq, ustun kelmoq",
                source_lang="en",
                context_sentence="We must transcend our limits and discover the unknown horizon.",
                timestamp_sec=8,
                mastery_level=3,
            ),
            UserVocabulary(
                user_id=admin_user.id,
                movie_id=movies_data[0].id,
                word="destiny",
                translation="taqdir, qismat",
                source_lang="en",
                context_sentence="The destiny of our world depends on this mission.",
                timestamp_sec=21,
                mastery_level=4,
            ),
            UserVocabulary(
                user_id=admin_user.id,
                movie_id=movies_data[4].id,
                word="cesaret",
                translation="jasorat, mardlik (Turkcha)",
                source_lang="tr",
                context_sentence="Cesaret korkunun yokluğu değil, karanlığa rağmen harekete geçmektir.",
                timestamp_sec=14,
                mastery_level=2,
            ),
        ]
    )

    # 8. Threaded Social Comments, @Mentions, Time-codes & Comment Awards (Module 1 & 2)
    root_rev_1 = MovieReview(
        user_id=admin_user.id,
        user_name="Nodirbek ✦ Founder",
        cine_username="kinochi_nodir",
        user_avatar=admin_user.avatar_url,
        user_badges=admin_user.badges,
        patron_tier="gold",
        movie_id=movies_data[0].id,
        timestamp_sec=24,
        rating=10,
        comment="Ovoz sifati va ikki qavatli subtitrlar shunchaki ajoyib! [00:24] da Kapitan Amerika Mjolnirni ko'targan kadrda zal portlagan edi! @marvel_malika sizga ham shu sahna yoqdimi?",
        has_spoiler=False,
        likes_count=48,
        awards_count=2,
        awards_uzs=10000,
    )
    root_rev_2 = MovieReview(
        user_id=user_2.id,
        user_name="Malika Karimova",
        cine_username="marvel_malika",
        user_avatar=user_2.avatar_url,
        user_badges=user_2.badges,
        patron_tier="silver",
        movie_id=movies_data[0].id,
        timestamp_sec=42,
        rating=9,
        comment="Oxirgi jang sahnasida Temir Odam barcha toshlarni ishlatib qahramonlarcha halok bo'lishi meni yig'latdi...",
        has_spoiler=True,
        likes_count=31,
        awards_count=1,
        awards_uzs=5000,
    )
    db.add_all([root_rev_1, root_rev_2])
    await db.flush()

    reply_rev_1 = MovieReview(
        user_id=user_2.id,
        user_name="Malika Karimova",
        cine_username="marvel_malika",
        user_avatar=user_2.avatar_url,
        user_badges=user_2.badges,
        patron_tier="silver",
        movie_id=movies_data[0].id,
        parent_id=root_rev_1.id,
        reply_to_username="kinochi_nodir",
        timestamp_sec=24,
        rating=10,
        comment="@kinochi_nodir Ha, 100%! Ayniqsa «Avengers Assemble» degan joyida musiqa bilan birga badan jimirlagan 🔥",
        has_spoiler=False,
        likes_count=19,
        awards_count=1,
        awards_uzs=5000,
    )
    reply_rev_2 = MovieReview(
        user_id=user_3.id,
        user_name="Javohir Bek",
        cine_username="javohir_cine",
        user_avatar=user_3.avatar_url,
        user_badges=user_3.badges,
        patron_tier="bronze",
        movie_id=movies_data[0].id,
        parent_id=root_rev_1.id,
        reply_to_username="kinochi_nodir",
        rating=10,
        comment="@kinochi_nodir @marvel_malika Edu-Cinema subtitrda 'destiny' va 'transcend' so'zlarini shu sahnada lug'atimga saqlab oldim!",
        has_spoiler=False,
        likes_count=11,
    )
    db.add_all([reply_rev_1, reply_rev_2])

    # 9. Cinema Reels (Vertical Shorts Feed)
    db.add_all(
        [
            CinemaReel(
                movie_id=movies_data[0].id,
                title="Qasoskorlar: Hal qiluvchi portal ochilishi #421",
                caption="Kod: 421 ✦ Ikki qavatli EN/UZ subtitr bilan to'liq HD tomosha qiling!",
                video_url=SAMPLE_REEL_1,
                likes_count=1840,
                views_count=24900,
            ),
            CinemaReel(
                movie_id=movies_data[3].id,
                title="Mendirman Jaloliddin — Sarkardaning qasamyodi #201",
                caption="Kod: 201 ✦ Milliy tarixiy serialning barcha qismlari pleyerda!",
                video_url=SAMPLE_REEL_2,
                likes_count=2310,
                views_count=31200,
            ),
            CinemaReel(
                movie_id=movies_data[6].id,
                title="Interstellar — Gargantua qora tuynugi #502",
                caption="Kod: 502 ✦ Ingliz tilini kino ko'rib o'rganing (Edu-Cinema C1)",
                video_url=SAMPLE_REEL_3,
                likes_count=1590,
                views_count=19800,
            ),
        ]
    )

    # 10. Marketing Campaigns (Instagram Reels Funnel)
    db.add_all(
        [
            MarketingCampaign(
                source="instagram_reels",
                utm_campaign="m_421_reel12",
                movie_code=421,
                clicks_count=4820,
                conversions_count=3910,
                vip_sales_count=142,
            ),
            MarketingCampaign(
                source="instagram_reels",
                utm_campaign="m_301_osman_hit",
                movie_code=301,
                clicks_count=6150,
                conversions_count=5120,
                vip_sales_count=218,
            ),
            MarketingCampaign(
                source="telegram_stories",
                utm_campaign="m_101_retro_uz",
                movie_code=101,
                clicks_count=2190,
                conversions_count=1840,
                vip_sales_count=64,
            ),
        ]
    )

    # 11. Sponsor Channels, Requests & CRM Tickets
    db.add_all(
        [
            SponsorChannel(
                title="CNMOVI Premyeralar Kanali",
                channel_id="@cnmovi_official",
                invite_link="https://t.me/cnmovi_official",
                platform="telegram",
                is_active=True,
                max_subscribers=50000,
                joined_count=14280,
            ),
            SponsorChannel(
                title="CNMOVI Instagram Rasmiy",
                channel_id="cnmovi_uz",
                invite_link="https://instagram.com/cnmovi_uz",
                platform="instagram",
                is_active=True,
                max_subscribers=100000,
                joined_count=38400,
            ),
            MovieRequest(
                user_id=user_2.id,
                query_text="Dune: Ikkinchi qism (O'zbek tilida 1080p)",
                votes_count=47,
                status="pending",
            ),
            MovieRequest(
                user_id=user_3.id,
                query_text="O'tkan kunlar (1969) 4K restavratsiya versiyasi",
                votes_count=83,
                status="uploaded",
                admin_reply="Yuklandi! Kod: 105 orqali tomosha qilishingiz mumkin.",
            ),
            FeedbackTicket(
                user_id=user_2.id,
                ticket_type="idea",
                message="Subtitrda so'zga bosganda lug'atga qo'shilishi juda zo'r chiqibdi! Nemis tilidagi kinolarni ham ko'paytiringlar.",
                status="open",
            ),
            MirrorBot(
                owner_user_id=admin_user.id,
                bot_username="kino_olami_mirror_bot",
                bot_token_masked="719283****:AAH8x****",
                is_active=True,
                users_referred=640,
            ),
            PaymentTransaction(
                user_id=user_2.id,
                provider="stars",
                plan_code="vip_1m",
                amount_uzs=29000,
                stars_amount=150,
                status="completed",
            ),
        ]
    )

    # 12. CINESOCIAL, CINEWALLET & CROWDFUNDING SEED DATA (Modules 1, 2, 3)
    db.add_all(
        [
            UserFollow(follower_id=user_2.id, following_id=admin_user.id),
            UserFollow(follower_id=user_3.id, following_id=admin_user.id),
            UserFollow(follower_id=admin_user.id, following_id=user_2.id),
            SocialNotification(
                user_id=admin_user.id,
                sender_username="marvel_malika",
                notif_type="mention",
                message="@marvel_malika sizni «Qasoskorlar: Intiho (#421)» sharhida eslab o'tdi!",
                movie_code=421,
                is_read=False,
            ),
            SocialNotification(
                user_id=admin_user.id,
                sender_username="javohir_cine",
                notif_type="award",
                message="🎁 @javohir_cine sizning sharhingizni 5,000 UZS bilan mukofotladi!",
                movie_code=421,
                is_read=False,
            ),
            CustomMovieList(
                user_id=admin_user.id,
                cine_username="kinochi_nodir",
                title="Dam olish kunlari ko'radigan Top-4 Durdonalarim",
                description="O'zbek oltin klassikasi va koinot haqidagi eng kuchli filmlar jamlanmasi.",
                movie_codes=[421, 502, 101, 201],
                likes_count=64,
                is_public=True,
            ),
            CustomMovieList(
                user_id=user_2.id,
                cine_username="marvel_malika",
                title="Ingliz va Koreys tilini o'rganish uchun Top Filmlar",
                description="Ikki qavatli subtitr bilan C1 darajaga chiqish uchun tavsiyalarim.",
                movie_codes=[502, 401, 501],
                likes_count=42,
                is_public=True,
            ),
            WalletTransaction(
                sender_id=None,
                receiver_id=admin_user.id,
                sender_username="Payme",
                receiver_username="kinochi_nodir",
                tx_type="topup",
                amount_uzs=150000,
                note="CineWallet hisobni to'ldirish (Payme)",
            ),
            WalletTransaction(
                sender_id=admin_user.id,
                receiver_id=user_2.id,
                sender_username="kinochi_nodir",
                receiver_username="marvel_malika",
                tx_type="gift_vip",
                amount_uzs=29000,
                plan_code="vip_1m",
                note="🎁 Faol kinotanqid va sharhlar uchun 1 Oylik Standart VIP hadya!",
            ),
            GiftVoucher(
                code="GIFT-VIP-2026",
                creator_id=admin_user.id,
                creator_username="kinochi_nodir",
                gift_type="vip_1m",
                value_uzs=29000,
                message="CNMOVI do'stlari uchun 1 Oylik Bepul Oltin Chipta! Birinchi faollashtirgan oladi!",
                is_claimed=False,
            ),
        ]
    )

    # 13. Crowdfunding Campaigns & Movie Patron Wall (Module 3)
    camp_1 = CrowdfundingCampaign(
        movie_code=421,
        title="Qasoskorlar: Intiho — Maxsus 4K IMAX & 5.1 O'zbek Dublyaj",
        target_type="dubbing_uz",
        description="Professional aktyorlar ishtirokida to'liq studiyaviy 5.1 O'zbekcha dublyaj va IMAX kengaytirilgan kadrlar fondiga hissa qo'shing!",
        goal_uzs=1500000,
        collected_uzs=1245000,
        donors_count=18,
        status="active",
        deadline_days=9,
        poster_url="https://images.unsplash.com/photo-1635805737707-575885ab0820?auto=format&fit=crop&w=600&q=80",
    )
    camp_2 = CrowdfundingCampaign(
        movie_code=502,
        title="Interstellar — Ilmiy Terminlar bilan Mukammal O'zbek Dublyaji",
        target_type="dubbing_uz",
        description="Astrofizika atamalari buzilmagan holda sifatli O'zbekcha ovozlashtirish va C1 Edu-Cinema tahliliy subtitrlari uchun xalqona fond.",
        goal_uzs=1200000,
        collected_uzs=980000,
        donors_count=14,
        status="active",
        deadline_days=12,
        poster_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
    )
    camp_3 = CrowdfundingCampaign(
        movie_code=101,
        title="Shum bola (1977) — AI 4K 60fps Rang va Ovoz Restavratsiyasi",
        target_type="remaster_4k",
        description="Milliy oltin fondimizdagi afsonaviy filmni sun'iy intellekt yordamida 4K tiniqlikka olib chiqish loyihasi.",
        goal_uzs=2000000,
        collected_uzs=1750000,
        donors_count=27,
        status="active",
        deadline_days=15,
        poster_url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=600&q=80",
    )
    db.add_all([camp_1, camp_2, camp_3])
    await db.flush()

    db.add_all(
        [
            CampaignDonation(
                campaign_id=camp_1.id,
                movie_code=421,
                user_id=admin_user.id,
                cine_username="kinochi_nodir",
                user_full_name="Nodirbek ✦ Founder",
                patron_tier="gold",
                amount_uzs=200000,
                message="O'zbek dublyaji eng yuqori sifatda bo'lishi uchun! Олға CNMOVI!",
            ),
            CampaignDonation(
                campaign_id=camp_1.id,
                movie_code=421,
                user_id=user_2.id,
                cine_username="marvel_malika",
                user_full_name="Malika Karimova",
                patron_tier="silver",
                amount_uzs=75000,
                message="Sevimli filmim uchun kamtarona hissa 🌸",
            ),
            CampaignDonation(
                campaign_id=camp_2.id,
                movie_code=502,
                user_id=admin_user.id,
                cine_username="kinochi_nodir",
                user_full_name="Nodirbek ✦ Founder",
                patron_tier="gold",
                amount_uzs=150000,
                message="Nolanning eng buyuk asari uchun!",
            ),
            CampaignDonation(
                campaign_id=camp_3.id,
                movie_code=101,
                user_id=user_3.id,
                cine_username="javohir_cine",
                user_full_name="Javohir Bek",
                patron_tier="bronze",
                amount_uzs=25000,
                message="Qoravoyni 4K formatda ko'rish nasib qilsin!",
            ),
        ]
    )

    await db.commit()
