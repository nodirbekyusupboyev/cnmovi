import random
from typing import Optional
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    WebAppInfo,
)
from sqlalchemy import select
from app.ai_service import shazam_identify_media
from app.cache import cache
from app.config import settings
from app.database import AsyncSessionLocal
from app.models import MarketingCampaign, Movie, MovieRequest, SponsorChannel, User

router = Router()


def build_movie_keyboard(movie: Movie) -> InlineKeyboardMarkup:
    webapp_target = f"{settings.WEBAPP_URL}?movie={movie.code}"
    top_button = (
        InlineKeyboardButton(
            text=f"⟢ Pleyerda Ko'rish ({movie.title})",
            web_app=WebAppInfo(url=webapp_target),
        )
        if settings.WEBAPP_URL.startswith("https://")
        else InlineKeyboardButton(
            text=f"⟢ Web Pleyerda Ko'rish ({movie.title})",
            url=webapp_target,
        )
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [top_button],
            [
                InlineKeyboardButton(
                    text="▹ Tomosha qilish (Stream)",
                    callback_data=f"play_media:{movie.code}",
                ),
                InlineKeyboardButton(
                    text="✦ Sevimlilarga",
                    callback_data=f"fav_add:{movie.code}",
                ),
            ],
        ]
    )


def format_movie_glyph_card(movie: Movie) -> str:
    """
    PRD Section 1 — UI/UX Standartlari:
    Bot matnlarida shovqinli emojilar o'rniga vazmin gliflar (⟢, ✦, ▹, ▪, ▫) ishlatiladi.
    """
    vip_badge = "✦ VIP PREMYERA" if movie.is_vip_only else "▫ OCHIQ PREMYERA"
    return (
        f"⟢ <b>{movie.title}</b> ({movie.year})\n"
        f"▫ Asl nomi: <i>{movie.original_title or movie.title}</i>\n"
        f"▪ Kod: <code>{movie.code}</code>  |  IMDb: <b>✦ {movie.imdb_rating}</b>\n"
        f"▪ Turkum: <code>{movie.category.upper()}</code>  |  Yosh: <code>{movie.age_rating}</code>\n"
        f"▪ Til Hubi: <code>{(movie.language_hub or 'uzbek').upper()}</code>  |  Holat: {vip_badge}\n\n"
        f"▹ {movie.description or ''}\n\n"
        f"✦ <i>480p / 720p / 1080p + Ikki qavatli subtitrlar (Edu-Cinema) tayyor.</i>"
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    args = message.text.split(maxsplit=1)[1] if message.text and len(message.text.split()) > 1 else ""
    tg_id = message.from_user.id if message.from_user else 0
    full_name = message.from_user.full_name if message.from_user else "Kinoman"
    username = message.from_user.username if message.from_user else None

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.telegram_id == tg_id))
        if not user:
            user = User(
                telegram_id=tg_id,
                username=username,
                full_name=full_name,
                referral_code=f"U{tg_id}",
                is_admin=tg_id in settings.admin_id_list,
            )
            db.add(user)
            await db.commit()

        # Check Instagram Reels UTM Deep Linking: e.g. /start m_421_reel12
        if args.startswith("m_"):
            parts = args.split("_")
            movie_code = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
            campaign = await db.scalar(select(MarketingCampaign).where(MarketingCampaign.utm_campaign == args))
            if not campaign:
                campaign = MarketingCampaign(
                    source="instagram_reels",
                    utm_campaign=args,
                    movie_code=movie_code,
                    clicks_count=1,
                    conversions_count=1,
                )
                db.add(campaign)
            else:
                campaign.clicks_count += 1
                campaign.conversions_count += 1
            await db.commit()

            if movie_code:
                movie = await db.scalar(select(Movie).where(Movie.code == movie_code))
                if movie:
                    await message.answer(
                        format_movie_glyph_card(movie),
                        parse_mode="HTML",
                        reply_markup=build_movie_keyboard(movie),
                    )
                    return

    main_button = (
        InlineKeyboardButton(
            text="⟢ CNMOVI Mini App Kinoteatrni Ochish",
            web_app=WebAppInfo(url=settings.WEBAPP_URL),
        )
        if settings.WEBAPP_URL.startswith("https://")
        else InlineKeyboardButton(
            text="⟢ CNMOVI Web Kinoteatrni Ochish",
            url=settings.WEBAPP_URL,
        )
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [main_button],
            [
                InlineKeyboardButton(text="✦ Top-10 Kinolar", callback_data="bot_top10"),
                InlineKeyboardButton(text="▹ VIP & Telegram Stars", callback_data="bot_vip"),
            ],
            [
                InlineKeyboardButton(text="▪ App Lock PIN Tiklash (OTP)", callback_data="bot_otp"),
            ],
        ]
    )
    welcome_text = (
        f"⟢ <b>CNMOVI — Raqamli Kinoteatr & Edu-Cinema</b>\n\n"
        f"✦ Xush kelibsiz, <b>{full_name}</b>.\n"
        f"▪ Kino kodini yuboring (masalan: <code>421</code>, <code>101</code>, <code>301</code>)\n"
        f"▪ Instagram/TikTok video yuborsangiz — <b>Shazam AI</b> kinoni topib beradi\n"
        f"▪ Yoki pastdagi tugma orqali <b>Mini App</b> kinoteatrini oching:"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=kb)


@router.message(Command("otp"))
async def cmd_otp(message: Message) -> None:
    tg_id = message.from_user.id if message.from_user else 123456789
    otp_code = f"{random.randint(100000, 999999)}"
    await cache.set(f"otp:{tg_id}", otp_code, ttl_seconds=300)
    await message.answer(
        f"⟢ <b>App Lock — Xavfsizlik Tiklash Kodi (OTP)</b>\n\n"
        f"✦ Sizning bir martalik kodingiz: <code>{otp_code}</code>\n"
        f"▫ Amal qilish muddati: 5 daqiqa.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "bot_otp")
async def cb_otp(call: CallbackQuery) -> None:
    tg_id = call.from_user.id
    otp_code = f"{random.randint(100000, 999999)}"
    await cache.set(f"otp:{tg_id}", otp_code, ttl_seconds=300)
    await call.message.answer(
        f"⟢ <b>App Lock — Bir Martalik Tiklash Kodi (OTP)</b>\n\n"
        f"✦ Kod: <code>{otp_code}</code>\n"
        f"▫ Mini App ichidagi «PIN unutdingizmi?» oynasiga ushbu kodni kiriting.",
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data == "bot_top10")
async def cb_top10(call: CallbackQuery) -> None:
    async with AsyncSessionLocal() as db:
        top_movies = list((await db.scalars(select(Movie).order_by(Movie.view_count_weekly.desc()).limit(5))).all())
        lines = ["⟢ <b>Haftaning Top-5 Premyeralari (Jonli Reyting):</b>\n"]
        kb_rows = []
        for idx, m in enumerate(top_movies, 1):
            lines.append(f"{idx}. <b>{m.title}</b> — ✦ IMDb {m.imdb_rating} (Kod: <code>{m.code}</code>)")
            kb_rows.append([InlineKeyboardButton(text=f"⟢ #{m.code} {m.title}", callback_data=f"play_media:{m.code}")])
        kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
        await call.message.answer("\n".join(lines), parse_mode="HTML", reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("fav_add:"))
async def cb_fav_add(call: CallbackQuery) -> None:
    code = call.data.split(":")[1]
    await call.answer("✦ Film sevimlilarga qo'shildi!", show_alert=True)


@router.callback_query(F.data.startswith("play_media:"))
async def cb_play_media(call: CallbackQuery) -> None:
    code = int(call.data.split(":")[1])
    async with AsyncSessionLocal() as db:
        movie = await db.scalar(select(Movie).where(Movie.code == code))
        if movie:
            await call.message.answer(
                format_movie_glyph_card(movie),
                parse_mode="HTML",
                reply_markup=build_movie_keyboard(movie),
            )
    await call.answer()


@router.callback_query(F.data == "bot_vip")
async def cb_vip(call: CallbackQuery) -> None:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✦ Standart VIP (150 Stars / 29,000 so'm)", callback_data="buy_stars:150")],
            [InlineKeyboardButton(text="⟢ Premium VIP 3 Oy (350 Stars / 69,000 so'm)", callback_data="buy_stars:350")],
        ]
    )
    await call.message.answer(
        "⟢ <b>CNMOVI VIP Obuna Tariflari</b>\n\n"
        "▪ <b>Standart VIP (1 oy):</b> Reklamasiz, majburiy kanallarsiz, 1080p Full HD va Ikki qavatli subtitrlar.\n"
        "▪ <b>Premium VIP (3 oy):</b> Barcha imtiyozlar + Erta premyeralar + Shaxsiy kino buyurtma va Oyna-Bot.\n\n"
        "▹ To'lov usulini tanlang (Telegram Stars / Payme / Click):",
        parse_mode="HTML",
        reply_markup=kb,
    )
    await call.answer()


@router.callback_query(F.data.startswith("buy_stars:"))
async def cb_buy_stars(call: CallbackQuery, bot: Bot) -> None:
    stars = int(call.data.split(":")[1])
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="CNMOVI VIP Obuna",
        description="Reklamasiz 1080p Full HD striming va Edu-Cinema ikki qavatli subtitrlar.",
        payload=f"vip_stars_{stars}",
        currency="XTR",
        prices=[LabeledPrice(label="VIP Obuna", amount=stars)],
    )
    await call.answer()


@router.pre_checkout_query()
async def on_pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@router.message(F.video | F.audio | F.voice)
async def handle_shazam_media(message: Message) -> None:
    caption = message.caption or "portal avengers"
    async with AsyncSessionLocal() as db:
        movies = list((await db.scalars(select(Movie))).all())
        result = await shazam_identify_media(caption, movies)
        m_data = result["movie"]
        movie = await db.scalar(select(Movie).where(Movie.code == m_data["code"]))
        if movie:
            await message.answer(
                f"⟢ <b>AI Shazam Natijasi ({result['confidence']} aniqlik)</b>\n"
                f"▫ Topilgan kadr vaqti: <code>{result['matched_timecode']}</code>\n\n"
                + format_movie_glyph_card(movie),
                parse_mode="HTML",
                reply_markup=build_movie_keyboard(movie),
            )


@router.message(F.text)
async def handle_code_or_search(message: Message) -> None:
    text = (message.text or "").strip()
    async with AsyncSessionLocal() as db:
        if text.isdigit():
            code = int(text)
            movie = await db.scalar(select(Movie).where(Movie.code == code))
            if movie:
                await message.answer(
                    format_movie_glyph_card(movie),
                    parse_mode="HTML",
                    reply_markup=build_movie_keyboard(movie),
                )
                return
            await message.answer(
                f"⟢ <code>{code}</code> kodli kino topilmadi.\n"
                f"▹ Mavjud kodlar: <code>421</code>, <code>101</code>, <code>102</code>, <code>201</code>, <code>301</code>, <code>401</code>, <code>501</code>, <code>502</code>, <code>601</code>, <code>701</code>, <code>801</code>, <code>901</code>",
                parse_mode="HTML",
            )
            return

        # Text search fallback or Request Desk
        stmt = select(Movie).where(Movie.title.ilike(f"%{text}%")).limit(3)
        found = list((await db.scalars(stmt)).all())
        if found:
            for m in found:
                await message.answer(
                    format_movie_glyph_card(m),
                    parse_mode="HTML",
                    reply_markup=build_movie_keyboard(m),
                )
        else:
            req = MovieRequest(user_id=1, query_text=text[:250], status="pending")
            db.add(req)
            await db.commit()
            await message.answer(
                f"⟢ <b>Request Desk — Buyurtma qabul qilindi</b>\n\n"
                f"✦ Siz izlagan <i>«{text}»</i> filmi adminlar ro'yxatiga qo'shildi. Yuklanganda sizga xabar beramiz!",
                parse_mode="HTML",
            )


def create_bot_dispatcher() -> tuple[Optional[Bot], Dispatcher]:
    dp = Dispatcher()
    dp.include_router(router)
    if settings.BOT_TOKEN and settings.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" and ":" in settings.BOT_TOKEN:
        bot = Bot(token=settings.BOT_TOKEN)
        return bot, dp
    return None, dp
