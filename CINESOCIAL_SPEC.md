# QO'SHIMCHA MODULLAR SPETSIFIKATSIYASI (CineSocial & Economy Addon — PRD v8.0 Mukammal Tahrir)
### Loyiha: CNMOVI Telegram Cinema Mini App — Ijtimoiy Tarmoq, Sovg'alar va Donat Ekotizimi

Ushbu hujjat mavjud **CNMOVI (PRD v7.0)** tizimiga qo'shiladigan 3 ta yangi yirik modulning to'liq arxitekturasi, xavfsizlik qoidalari va UX ssenariylarini belgilaydi:
1. **1-MODUL: CineProfile (Ilova ichidagi mustaqil kino ijtimoiy tarmog'i)**
2. **2-MODUL: CineWallet & Gifting (Ikki qatlamli hamyon, VIP hadya qilish va Izoh mukofotlari)**
3. **3-MODUL: Donat & Crowdfunding (Xalqona Dublyaj Fondi, Film Homiylari Titri va Patron Darajalari)**

---

## 1. 1-MODUL: CineProfile (Kino Ijtimoiy Tarmog'i)

### A. Telegramdan Mustaqil Profil va Anti-Squatting Himoyasi
* **Unikal Nickname (`@cine_username`):** Har bir foydalanuvchi ilova ichida o'ziga takrorlanmas `@username` yaratadi (masalan: `@kinochi_nodir`, `@marvel_malika`, `@javohir_cine`).
  * **Format va Validatsiya:** `^[a-z0-9_]{3,20}$` (faqat kichik lotin harflari, raqamlar va pastki chiziq).
  * **Reserved Nicknames (Taqiqlangan niklar):** `@admin`, `@cnmovi`, `@support`, `@payme`, `@click`, `@official`, `@bot` kabi tizim nomlarini band qilish avtomatik bloklanadi.
* **Profil Ma'lumotlari:**
  * Shaxsiy avatar, Bio tavsifi (*"Faqat Kristofer Nolan va milliy tarixiy filmlar muxlisi"*).
  * Sevimli janrlar nishoni (`#SciFi`, `#UzbekClassic`, `#KDrama`) va maxsus unvonlar (`✦ Founder`, `🥇 Gold Legend`, `✦ Kinotanqidchi`).
  * Ijtimoiy ko'rsatkichlar: **Obunachilar (Followers)**, **Obunalar (Following)**, **Jami olingan layklar va mukofotlar**.
* **Shaxsiy Kino-Kolleksiyalar (Public Custom Lists):**
  * Foydalanuvchi o'z profilida ochiq pleylistlar tuza oladi (masalan: *"Dam olish kunlari ko'radigan Top-5 fantastik filmlarim"*). Boshqa foydalanuvchilar ushbu kolleksiyalarni ko'rishi va layk bosishi mumkin.
* **Maxfiylik Nazorati (Privacy Controls):**
  * *"Meni kimlar `@mention` qila oladi?"* (`all` | `following` | `none`).
  * *"Ko'rayotgan kinolarim tarixini profilda yashirish (Incognito Mode)"*.

### B. Kinolar Ostidagi Zanjirli Izohlar, `@Atmetka` va Vaqt Kodlari (Social Threaded Comments)
* **2-Darajali Izohlar Zanjiri (2-Level Threaded Replies):**
  * Mobil ekranda izohlar siqilib qolmasligi uchun YouTube/Instagram standarti qo'llaniladi: Asosiy izoh (`parent_id = null`) va uning ostida javoblar zanjiri (`parent_id = root.id`, `reply_to_username = "@..."`).
* **Vaqt Kodiga Bog'langan Izohlar (Time-coded Comments):**
  * Foydalanuvchi pleyerda kino ko'rayotgan paytda izoh yozsa, joriy sekund (`timestamp_sec`, masalan `[02:22]`) izohga biriktiriladi. Boshqa tomoshabin `[02:22]` ustiga bossa, pleyer darhol o'sha sahnaga sakraydi.
* **Profilga O'tish va `@Mention` (Atmetka):**
  * Har qanday izohdagi `@username` ustiga bosilganda shu foydalanuvchining **CineProfile** modal oynasi ochiladi (u yerda Obuna bo'lish yoki unga VIP/Balans sovg'a qilish tugmalari chiqadi).
  * Izohda `@kinochi_nodir` deb yozilsa, o'sha foydalanuvchiga darhol ichki bildirishnoma (`SocialNotification`) boradi: *"@marvel_malika sizni 'Qasoskorlar: Intiho (#421)' sharhida eslab o'tdi"*.

---

## 2. 2-MODUL: CineWallet & Gifting (Ichki Hamyon va Sovg'alar Tizimi)

### A. Ikki Qatlamli Balans Arxitekturasi (Anti-Abuse Dual Balance)
* **1. Asosiy Balans (`wallet_balance_uzs`):** Payme, Click yoki Telegram Stars orqali to'ldirilgan haqiqiy balans. Ushbu balansdan do'stlarga VIP hadya qilish, balans o'tkazish, izohlarni mukofotlash va crowdfunding'ga pul tikish mumkin.
* **2. Bonus Balans (`bonus_balance_uzs`):** Streak, referal va promo-kodlar orqali yig'ilgan bonuslar. Multi-akkaunt firibgarligining oldini olish uchun bonus balansni boshqa foydalanuvchiga o'tkazib bo'lmaydi — faqat shaxsiy VIP obuna uchun ishlatiladi.
* **Double-Entry Ledger (`WalletTransaction`):** Barcha kirim-chiqimlar va sovg'alar alohida buxgalteriya jadvalida saqlanadi.

### B. 3 Xil Hadya Mexanizmi (Viral Gifting)
1. **Direct Gift (`@username` orqali):**
   * Do'stining `@cine_username`ini kiritib unga **Standart VIP (1 oy)**, **Premium VIP (3 oy)**, **Founder VIP (1 yil)** yoki **Balans (UZS)** hadya qilish.
   * Sovg'aga maxsus tabriknoma xabari qo'shiladi va qabul qiluvchiga bildirishnoma yuboriladi.
2. **Comment Award (Izoh Muallifini Mukofotlash):**
   * Kino ostida ajoyib tahlil yoki foydali izoh yozgan odamning sharhi yonidagi `🎁 Mukofotlash` tugmasini bosish orqali uning hamyoniga **5,000 UZS** mukofot yuborish. Izohda `🏆 Mukofotlangan` oltin belgisi paydo bo'ladi.
3. **Gift Voucher Link ("Oltin Chipta" / Guruh uchun Drop):**
   * Foydalanuvchi o'z balansidan VIP yoki summa ajratib, bir martalik maxsus promokod/havola (`GIFT-VIP-XXXX`) yaratadi va uni Telegram guruhga yoki do'stiga yuboradi. Kim birinchi bo'lib faollashtirsa, sovg'a o'shanga o'tadi.

---

## 3. 3-MODUL: Donat & Crowdfunding (Loyihani va Dublyajni Qo'llab-Quvvatlash)

### A. Maqsadli Crowdfunding — "Xalqona Dublyaj & 4K Reliz Fondi"
* Foydalanuvchilar konkret film yoki serialning **O'zbekcha professional dublyaji** yoki **4K Restavratsiyasi** uchun jamoaviy pul yig'ishda (`CrowdfundingCampaign`) qatnashadilar.
* Har bir kampaniyada **Jonli Progress Bar** (yig'ilgan summa, maqsad, foiz va ishtirokchilar soni) hamda **Escrow Kafolati** (agar muddatda yig'ilmasa, mablag' `CineWallet`ga avtomatik qaytishi) ko'rsatiladi.

### B. Film Sahifasi va Pleyerdagi "Faxriy Homiylar Taxtasi" (Movie Patron Credits)
* Homiylik asosida chiqqan filmlarning pleyer oynasida **"✦ Ushbu film homiylari (Movie Patrons)"** bloki ko'rinadi.
* Video boshlanishida dastlabki 10 soniyada pleyer burchagida oltin titr chiqadi: *"🎬 Ushbu film @kinochi_nodir, @marvel_malika va homiylar ko'magida taqdim etildi"*.

### C. Donator Darajalari (Patron Tiers) va Imtiyozlar
* Jami donat va crowdfunding hissasiga ko'ra avtomatik beriladigan darajalar:
  * 🥉 **Bronze Patron** (`10,000+ UZS`): Izohlarda `🥉 Bronze Homiy` nishoni.
  * 🥈 **Silver Patron** (`50,000+ UZS`): Kumush profil ramkasi + Request Desk'da ovoz kuchi `x3`.
  * 🥇 **Gold Legend** (`150,000+ UZS`): Oltin profil ramkasi, izohlari oltin hoshiyada ajralib turishi va **Homiylar Shon-Sharaf Zali (Hall of Fame)** peshqadami.
