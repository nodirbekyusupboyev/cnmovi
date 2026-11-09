import React, { useEffect, useState } from 'react'
import {
  Film,
  Sparkles,
  Flame,
  Trophy,
  Shield,
  Search,
  Play,
  Sun,
  Moon,
  Monitor,
  Lock,
  Unlock,
  Baby,
  Compass,
  Users,
  Heart,
  X as XIcon,
  Shuffle,
  Bot,
  Music,
  BookOpen,
  Crown,
  Send,
  PlusCircle,
  BarChart3,
  Globe,
  CheckCircle2,
  Clapperboard,
  Tv,
  Instagram,
  KeyRound,
  Wallet,
  Gift,
  Bell,
  AtSign,
  Award,
  Ticket,
  ListPlus,
  UserCheck,
  UserPlus,
} from 'lucide-react'
import CinemaPlayerModal from './components/CinemaPlayerModal.jsx'

const CATALOG_HUBS = [
  { id: 'all', label: '✦ Barchasi', group: 'main' },
  { id: 'uzbek_classic', label: "🏛 O'zbek Oltin Fondi", group: 'cultural' },
  { id: 'uzbek_modern', label: "🇺🇿 Yangi O'zbek & Epik", group: 'cultural' },
  { id: 'turkish', label: '🇹🇷 Turk Seriallari Hubi', group: 'cultural' },
  { id: 'kdrama', label: '🇰🇷 K-Drama (Koreys)', group: 'cultural' },
  { id: 'action', label: '⚔️ Jangari & Blokbaster', group: 'main' },
  { id: 'scifi', label: '🚀 Fantastika & Fentezi', group: 'main' },
  { id: 'cartoon', label: '🦁 Multfilmlar (5 toifa)', group: 'main' },
  { id: 'doc', label: '🌍 Hujjatli & Ilm-Fan (BBC)', group: 'special' },
  { id: 'short', label: '⏱ Qisqa Metraj (5-20 min)', group: 'special' },
  { id: 'standup', label: '🎤 Stand-Up & Konsert', group: 'special' },
]

const LANGUAGE_HUBS = [
  { id: 'all', label: 'Barcha Tillar' },
  { id: 'uzbek', label: "O'zbek tili" },
  { id: 'english', label: '🇬🇧 English Hub (Dual Sub)' },
  { id: 'turkish', label: '🇹🇷 Türkçe Hub (Dual Sub)' },
  { id: 'korean', label: '🇰🇷 한국어 K-Hub' },
  { id: 'german', label: '🇩🇪 Deutsches Kino (A1-C1)' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('catalog') // 'catalog' | 'reels' | 'social' | 'profile' | 'admin'
  const [themeMode, setThemeMode] = useState('dark') // 'dark' | 'light' | 'system'
  const [kidsMode, setKidsMode] = useState(false)

  // App Lock State (PIN + Biometrics + OTP Recovery)
  const [isAppLocked, setIsAppLocked] = useState(false)
  const [savedPin, setSavedPin] = useState('2026')
  const [pinInput, setPinInput] = useState('')
  const [pinError, setPinError] = useState('')
  const [otpModalOpen, setOtpModalOpen] = useState(false)
  const [otpDemoCode, setOtpDemoCode] = useState('')
  const [otpInput, setOtpInput] = useState('')
  const [newPinInput, setNewPinInput] = useState('')

  // Catalog State
  const [catalogData, setCatalogData] = useState({
    movies: [],
    top10_weekly: [],
    continue_watching: [],
    franchises: [],
  })
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedLangHub, setSelectedLangHub] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeMovieCode, setActiveMovieCode] = useState(null)

  // Reels State
  const [reels, setReels] = useState([])

  // Social & AI Hub State
  const [rouletteResult, setRouletteResult] = useState(null)
  const [rouletteSpinning, setRouletteSpinning] = useState(false)
  const [matcherRoom, setMatcherRoom] = useState(null)
  const [matcherIndex, setMatcherIndex] = useState(0)
  const [matchedMovie, setMatchedMovie] = useState(null)
  const [watchPartyRoom, setWatchPartyRoom] = useState(null)
  const [partyChatInput, setPartyChatInput] = useState('')

  // AI Critic & Shazam State
  const [criticQuery, setCriticQuery] = useState('')
  const [criticPersona, setCriticPersona] = useState('tony_stark')
  const [criticResponse, setCriticResponse] = useState(null)
  const [shazamClue, setShazamClue] = useState('')
  const [shazamResult, setShazamResult] = useState(null)

  // Profile, Gamification & Vocabulary State
  const [profileData, setProfileData] = useState(null)
  const [vocabulary, setVocabulary] = useState([])
  const [requestsData, setRequestsData] = useState({ requests: [], tickets: [] })
  const [newRequestText, setNewRequestText] = useState('')

  // MODULE 1, 2, 3: CineProfile, CineWallet & Crowdfunding State
  const [walletData, setWalletData] = useState(null)
  const [crowdfundingData, setCrowdfundingData] = useState(null)
  const [inspectedProfile, setInspectedProfile] = useState(null)
  const [profileEditForm, setProfileEditForm] = useState({
    cine_username: 'kinochi_nodir',
    bio: '',
    mention_privacy: 'all',
    hide_watch_history: false,
  })
  const [profileStatusMsg, setProfileStatusMsg] = useState(null)
  const [newListForm, setNewListForm] = useState({
    title: '',
    description: '',
    codesText: '421, 502, 101',
  })
  const [giftForm, setGiftForm] = useState({
    recipient_username: 'marvel_malika',
    gift_type: 'vip_1m',
    amount_uzs: 25000,
    message: "🎁 Eng zo'r kinolarni VIP sifatda birga ko'raylik!",
  })
  const [voucherClaimCode, setVoucherClaimCode] = useState('GIFT-VIP-2026')
  const [economyNotice, setEconomyNotice] = useState(null)

  // Admin CMS State
  const [adminData, setAdminData] = useState(null)
  const [newMovieForm, setNewMovieForm] = useState({
    code: 777,
    title: '',
    description: '',
    category: 'action',
    language_hub: 'english',
    cefr_level: 'B2',
    year: 2025,
    imdb_rating: 8.5,
    include_1080p: true,
  })

  // Apply Dark / Light / System Theme without reload (PRD Section 1 & 3.E.2)
  const effectiveDark =
    themeMode === 'dark' ||
    (themeMode === 'system' &&
      window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const movieParam = params.get('movie')
    if (movieParam && !isNaN(Number(movieParam))) {
      setActiveMovieCode(Number(movieParam))
    }
  }, [])

  const loadCatalog = async () => {
    try {
      const params = new URLSearchParams()
      if (selectedCategory !== 'all') params.set('category', selectedCategory)
      if (selectedLangHub !== 'all') params.set('language_hub', selectedLangHub)
      if (searchQuery.trim()) params.set('search', searchQuery.trim())
      if (kidsMode) params.set('kids_mode', 'true')

      const res = await fetch(`/api/catalog?${params.toString()}`)
      const data = await res.json()
      setCatalogData(data)
    } catch (err) {
      console.error('Catalog load error:', err)
    }
  }

  const loadProfileAndVocab = async () => {
    try {
      const [profRes, vocRes, reqRes, walRes, cfRes] = await Promise.all([
        fetch('/api/profile'),
        fetch('/api/vocabulary'),
        fetch('/api/requests'),
        fetch('/api/wallet'),
        fetch('/api/crowdfunding'),
      ])
      const profJson = await profRes.json()
      setProfileData(profJson)
      if (profJson?.user) {
        setProfileEditForm({
          cine_username: profJson.user.cine_username || 'kinochi_nodir',
          bio: profJson.user.bio || '',
          mention_privacy: profJson.user.mention_privacy || 'all',
          hide_watch_history: Boolean(profJson.user.hide_watch_history),
        })
      }
      setVocabulary(await vocRes.json())
      setRequestsData(await reqRes.json())
      setWalletData(await walRes.json())
      setCrowdfundingData(await cfRes.json())
    } catch (err) {
      console.error(err)
    }
  }

  const handleOpenCineProfile = async (username) => {
    if (!username) return
    const clean = String(username).replace(/^@/, '').trim()
    try {
      const res = await fetch(`/api/cineprofile/${clean}`)
      if (res.ok) {
        setInspectedProfile(await res.json())
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleToggleFollow = async (targetUsername) => {
    const res = await fetch(`/api/cineprofile/follow/${targetUsername}`, { method: 'POST' })
    if (res.ok) {
      handleOpenCineProfile(targetUsername)
      loadProfileAndVocab()
    }
  }

  const handleSaveCineProfile = async (e) => {
    e.preventDefault()
    const res = await fetch('/api/cineprofile/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileEditForm),
    })
    const data = await res.json()
    if (res.ok) {
      setProfileStatusMsg(`✦ CineProfile (@${data.cine_username}) muvaffaqiyatli saqlandi!`)
      loadProfileAndVocab()
    } else {
      setProfileStatusMsg(`⚠️ ${data.detail || 'Xatolik'}`)
    }
    setTimeout(() => setProfileStatusMsg(null), 5000)
  }

  const handleCreateCustomList = async (e) => {
    e.preventDefault()
    if (!newListForm.title.trim()) return
    const codes = newListForm.codesText
      .split(',')
      .map((s) => Number(s.trim()))
      .filter((n) => !isNaN(n) && n > 0)
    const res = await fetch('/api/cineprofile/lists', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: newListForm.title,
        description: newListForm.description,
        movie_codes: codes.length ? codes : [421, 502],
      }),
    })
    if (res.ok) {
      setNewListForm({ title: '', description: '', codesText: '421, 502' })
      loadProfileAndVocab()
    }
  }

  const handleTopupWallet = async (provider, amount_uzs) => {
    const res = await fetch('/api/wallet/topup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, amount_uzs }),
    })
    if (res.ok) {
      setEconomyNotice(`💳 ${provider.toUpperCase()} orqali +${amount_uzs.toLocaleString()} UZS CineWallet balansga qo'shildi!`)
      setTimeout(() => setEconomyNotice(null), 4500)
      loadProfileAndVocab()
    }
  }

  const handleSendGift = async (e) => {
    e.preventDefault()
    const res = await fetch('/api/wallet/gift', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...giftForm,
        amount_uzs: Number(giftForm.amount_uzs),
      }),
    })
    const data = await res.json()
    if (res.ok) {
      setEconomyNotice(`🎁 ${data.recipient} ga «${data.gift_label}» muvaffaqiyatli hadya qilindi!`)
      loadProfileAndVocab()
    } else {
      setEconomyNotice(`⚠️ ${data.detail || 'Xatolik'}`)
    }
    setTimeout(() => setEconomyNotice(null), 5500)
  }

  const handleCreateVoucher = async (gift_type) => {
    const res = await fetch('/api/wallet/voucher/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        gift_type,
        value_uzs: gift_type === 'vip_3m' ? 69000 : 29000,
        message: "Do'stlar guruhi uchun Oltin Chipta!",
      }),
    })
    const data = await res.json()
    if (res.ok) {
      setVoucherClaimCode(data.code)
      setEconomyNotice(`🎫 Yangi Oltin Chipta yaratildi: ${data.code}`)
      loadProfileAndVocab()
    } else {
      setEconomyNotice(`⚠️ ${data.detail || 'Xatolik'}`)
    }
    setTimeout(() => setEconomyNotice(null), 5000)
  }

  const handleClaimVoucher = async (e) => {
    e.preventDefault()
    if (!voucherClaimCode.trim()) return
    const res = await fetch('/api/wallet/voucher/claim', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: voucherClaimCode }),
    })
    const data = await res.json()
    if (res.ok) {
      setEconomyNotice(`🎉 Oltin Chipta (${data.code}) muvaffaqiyatli faollashtirildi!`)
      loadProfileAndVocab()
    } else {
      setEconomyNotice(`⚠️ ${data.detail || 'Xatolik'}`)
    }
    setTimeout(() => setEconomyNotice(null), 5000)
  }

  const handleDonateCampaign = async (campaign_id, amount_uzs) => {
    const res = await fetch('/api/crowdfunding/donate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        campaign_id,
        amount_uzs,
        message: "O'zbekcha professional dublyaj va 4K sifat uchun!",
      }),
    })
    const data = await res.json()
    if (res.ok) {
      setEconomyNotice(
        `🎬 Rahmat! Fondga +${amount_uzs.toLocaleString()} UZS qo'shildi. Sizning statusingiz: ${data.patron_tier.toUpperCase()} PATRON!`
      )
      loadProfileAndVocab()
    } else {
      setEconomyNotice(`⚠️ ${data.detail || 'Xatolik'}`)
    }
    setTimeout(() => setEconomyNotice(null), 5500)
  }

  const loadReels = async () => {
    try {
      const res = await fetch('/api/reels')
      setReels(await res.json())
    } catch (err) {
      console.error(err)
    }
  }

  const loadAdmin = async () => {
    try {
      const res = await fetch('/api/admin/dashboard')
      setAdminData(await res.json())
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    loadCatalog()
  }, [selectedCategory, selectedLangHub, searchQuery, kidsMode])

  useEffect(() => {
    loadProfileAndVocab()
    loadReels()
    loadAdmin()
  }, [])

  // Smart Roulette Handler
  const handleSpinRoulette = async () => {
    setRouletteSpinning(true)
    try {
      const res = await fetch('/api/roulette?min_imdb=6.5')
      const data = await res.json()
      setTimeout(() => {
        setRouletteResult(data.winner)
        setRouletteSpinning(false)
      }, 650)
    } catch {
      setRouletteSpinning(false)
    }
  }

  // Movie Matcher (Tinder) Handlers
  const handleStartMatcher = async () => {
    const res = await fetch('/api/matcher/create', { method: 'POST' })
    const data = await res.json()
    setMatcherRoom(data)
    setMatcherIndex(0)
    setMatchedMovie(null)
  }

  const handleSwipeMatcher = async (liked) => {
    const pool = catalogData.movies
    if (!pool.length) return
    const currentMovie = pool[matcherIndex % pool.length]
    const res = await fetch('/api/matcher/swipe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        room_code: matcherRoom?.room_code || 'MM-7788',
        movie_code: currentMovie.code,
        liked,
      }),
    })
    const data = await res.json()
    if (data.is_match) {
      setMatchedMovie(currentMovie)
    } else {
      setMatcherIndex((i) => i + 1)
    }
  }

  // Watch Party Starter
  const handleStartWatchParty = async (movieCode = 421) => {
    const res = await fetch(`/api/watch-party/create?movie_code=${movieCode}`, {
      method: 'POST',
    })
    const room = await res.json()
    setWatchPartyRoom(room)
    setActiveMovieCode(null)
    setActiveTab('social')
  }

  // AI Critic & Shazam Handlers
  const handleAskCritic = async (e) => {
    e.preventDefault()
    if (!criticQuery.trim()) return
    const res = await fetch('/api/ai/critic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: criticQuery, persona: criticPersona }),
    })
    setCriticResponse(await res.json())
  }

  const handleRunShazam = async (e) => {
    e.preventDefault()
    if (!shazamClue.trim()) return
    const res = await fetch('/api/ai/shazam', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clue_text: shazamClue }),
    })
    setShazamResult(await res.json())
  }

  // Biometric / PIN App Lock Screen (PRD Section 3.E.1)
  const handleBiometricUnlock = () => {
    if (window.Telegram?.WebApp?.BiometricManager) {
      window.Telegram.WebApp.BiometricManager.authenticate(
        { reason: 'CNMOVI ilovasini FaceID / TouchID orqali ochish' },
        (success) => {
          if (success) setIsAppLocked(false)
        }
      )
    } else {
      setIsAppLocked(false)
    }
  }

  const handleRequestOtp = async () => {
    const res = await fetch('/api/settings/request-otp', { method: 'POST' })
    const data = await res.json()
    setOtpDemoCode(data.demo_otp_preview)
    setOtpModalOpen(true)
  }

  const handleResetPinWithOtp = async (e) => {
    e.preventDefault()
    const res = await fetch('/api/settings/reset-pin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ otp_code: otpInput, new_pin: newPinInput }),
    })
    if (res.ok) {
      setSavedPin(newPinInput)
      setIsAppLocked(false)
      setOtpModalOpen(false)
      setPinError('')
    } else {
      setPinError("OTP kod noto'g'ri!")
    }
  }

  const handleCreateAdminMovie = async (e) => {
    e.preventDefault()
    if (!newMovieForm.title.trim()) return
    const res = await fetch('/api/admin/movies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...newMovieForm,
        code: Number(newMovieForm.code),
        year: Number(newMovieForm.year),
        imdb_rating: Number(newMovieForm.imdb_rating),
      }),
    })
    if (res.ok) {
      setNewMovieForm((f) => ({ ...f, code: Number(f.code) + 1, title: '', description: '' }))
      loadCatalog()
      loadAdmin()
    }
  }

  // ==========================================================================
  // APP LOCK FULLSCREEN OVERLAY (PIN + FACEID/TOUCHID + OTP RECOVERY)
  // ==========================================================================
  if (isAppLocked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#07090E] text-white p-4">
        <div className="w-full max-w-sm p-6 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-2xl text-center space-y-5">
          <div className="w-14 h-14 rounded-2xl bg-cyan-500/15 border border-cyan-400/30 flex items-center justify-center mx-auto">
            <Lock className="w-7 h-7 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold">⟢ CNMOVI App Lock</h2>
            <p className="text-xs text-slate-400 mt-1">
              Shaxsiy daxlsizlik himoyasi. 4 xonali PIN-kodni kiriting (Demo PIN: <code>{savedPin}</code>)
            </p>
          </div>

          <input
            type="password"
            maxLength={4}
            value={pinInput}
            onChange={(e) => {
              const val = e.target.value
              setPinInput(val)
              if (val === savedPin) {
                setIsAppLocked(false)
                setPinInput('')
                setPinError('')
              } else if (val.length === 4) {
                setPinError("✦ PIN-kod noto'g'ri!")
              }
            }}
            placeholder="• • • •"
            className="w-40 text-center text-2xl tracking-[0.5em] font-mono py-2.5 rounded-2xl bg-black/60 border border-cyan-400/40 outline-none text-cyan-300 mx-auto block"
          />

          {pinError && <p className="text-xs text-rose-400">{pinError}</p>}

          <div className="flex flex-col gap-2 pt-2">
            <button
              onClick={handleBiometricUnlock}
              className="w-full py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition"
            >
              ✦ Face ID / Touch ID orqali ochish
            </button>
            <button
              onClick={handleRequestOtp}
              className="text-xs text-slate-400 hover:text-cyan-300 underline"
            >
              PIN-kodni unutdingizmi? (Telegram Bot orqali OTP tiklash)
            </button>
          </div>

          {otpModalOpen && (
            <form
              onSubmit={handleResetPinWithOtp}
              className="p-4 rounded-2xl bg-black/70 border border-amber-400/30 text-left space-y-2.5"
            >
              <p className="text-xs text-amber-300 font-mono">
                ✦ Botdan yuborilgan OTP kod: <b>{otpDemoCode}</b>
              </p>
              <input
                type="text"
                value={otpInput}
                onChange={(e) => setOtpInput(e.target.value)}
                placeholder="6 xonali OTP kod"
                className="w-full px-3 py-1.5 rounded-lg bg-white/5 border border-white/15 text-xs"
              />
              <input
                type="text"
                maxLength={4}
                value={newPinInput}
                onChange={(e) => setNewPinInput(e.target.value)}
                placeholder="Yangi 4 xonali PIN (masalan: 1111)"
                className="w-full px-3 py-1.5 rounded-lg bg-white/5 border border-white/15 text-xs"
              />
              <button
                type="submit"
                className="w-full py-1.5 rounded-lg bg-amber-500 text-slate-950 font-bold text-xs"
              >
                PIN-kodni yangilash
              </button>
            </form>
          )}
        </div>
      </div>
    )
  }

  const heroMovie = catalogData.movies[0] || catalogData.top10_weekly[0]

  return (
    <div
      className={`min-h-screen pb-24 transition-colors duration-300 ${
        effectiveDark ? 'bg-[#07090E] text-slate-100' : 'bg-[#F4F6FA] text-slate-900'
      }`}
    >
      {/* ====================================================================
          TOP GLASSMORPHIC HEADER (Theme Engine + Code Search + Kids Mode + Lock)
         ==================================================================== */}
      <header
        className={`sticky top-0 z-30 backdrop-blur-xl border-b transition-colors ${
          effectiveDark
            ? 'bg-[#07090E]/85 border-white/10'
            : 'bg-white/85 border-slate-200 shadow-sm'
        }`}
      >
        <div className="max-w-7xl mx-auto px-3 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-3">
          {/* Brand Logo */}
          <div
            onClick={() => setActiveTab('catalog')}
            className="flex items-center gap-2.5 cursor-pointer"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-cyan-500/20">
              ⟢
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold tracking-tight text-base">CNMOVI</span>
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
                  v7.0 AI
                </span>
              </div>
              <p className="text-[11px] opacity-60 hidden sm:block">
                Scandinavian Cinema & Edu-Streaming
              </p>
            </div>
          </div>

          {/* Instant Code (`421`) & Title Search Bar */}
          <div
            className={`flex-1 max-w-md flex items-center gap-2 px-3.5 py-2 rounded-2xl border ${
              effectiveDark
                ? 'bg-white/5 border-white/10 focus-within:border-cyan-400'
                : 'bg-slate-100 border-slate-300 focus-within:border-blue-500'
            }`}
          >
            <Search className="w-4 h-4 opacity-50 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                if (activeTab !== 'catalog') setActiveTab('catalog')
              }}
              placeholder="Kino kodi (421, 101, 301) yoki nomini yozing..."
              className="w-full bg-transparent text-xs outline-none"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="text-xs opacity-60">
                ✕
              </button>
            )}
          </div>

          {/* Right Quick Controls: Wallet, Notifications, Kids Mode, Theme Switcher, App Lock */}
          <div className="flex items-center gap-1.5">
            {/* CineWallet Quick Balance Pill */}
            {profileData?.user && (
              <button
                onClick={() => setActiveTab('economy')}
                title="CineWallet & Sovg'alar bo'limiga o'tish"
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-400/30 text-amber-300 text-xs font-mono font-bold transition"
              >
                <Wallet className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">
                  {(profileData.user.wallet_balance_uzs || 0).toLocaleString()} UZS
                </span>
              </button>
            )}

            {/* Notifications Bell (@Atmetka & Gifts) */}
            {profileData?.notifications && (
              <button
                onClick={() => setActiveTab('profile')}
                title="@Atmetka va Sovg'a bildirishnomalari"
                className="relative p-2 rounded-xl bg-white/5 hover:bg-white/15 border border-white/10 text-cyan-300 transition"
              >
                <Bell className="w-4 h-4" />
                {profileData.notifications.filter((n) => !n.is_read).length > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center">
                    {profileData.notifications.filter((n) => !n.is_read).length}
                  </span>
                )}
              </button>
            )}

            {/* Kids Mode (0+ / Family Filter) */}
            <button
              onClick={() => setKidsMode(!kidsMode)}
              title="Ota-onalar nazorati (Kids Mode 16+/18+ bloklash)"
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold border transition ${
                kidsMode
                  ? 'bg-emerald-500 text-slate-950 border-emerald-400'
                  : effectiveDark
                  ? 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                  : 'bg-slate-100 border-slate-300 text-slate-700'
              }`}
            >
              <Baby className="w-3.5 h-3.5" />
              <span className="hidden md:inline">{kidsMode ? 'Kids: ON' : 'Kids'}</span>
            </button>

            {/* Theme Engine: Dark / Light / System Sync */}
            <div
              className={`flex items-center p-1 rounded-xl border ${
                effectiveDark ? 'bg-white/5 border-white/10' : 'bg-slate-200 border-slate-300'
              }`}
            >
              {[
                { id: 'dark', icon: Moon, title: 'OLED Dark Mode' },
                { id: 'light', icon: Sun, title: 'Soft Light Mode' },
                { id: 'system', icon: Monitor, title: 'System Sync' },
              ].map((t) => {
                const Icon = t.icon
                return (
                  <button
                    key={t.id}
                    onClick={() => setThemeMode(t.id)}
                    title={t.title}
                    className={`p-1.5 rounded-lg transition ${
                      themeMode === t.id
                        ? 'bg-cyan-500 text-slate-950 shadow'
                        : 'opacity-60 hover:opacity-100'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </button>
                )
              })}
            </div>

            {/* App Lock Trigger */}
            <button
              onClick={() => setIsAppLocked(true)}
              title="App Lock (PIN / FaceID bilan qulflash)"
              className={`p-2 rounded-xl border transition ${
                effectiveDark
                  ? 'bg-white/5 border-white/10 hover:bg-white/15 text-cyan-400'
                  : 'bg-slate-100 border-slate-300 text-slate-800'
              }`}
            >
              <Lock className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* ====================================================================
          MAIN CONTENT AREA
         ==================================================================== */}
      <main className="max-w-7xl mx-auto px-3 sm:px-6 pt-5 space-y-8">
        {/* ==================================================================
            TAB 1: KATALOG, MADANIY HUBLAR, TOP-10 VA FRANSHIZALAR
           ================================================================== */}
        {activeTab === 'catalog' && (
          <div className="space-y-8">
            {/* HERO BANNER */}
            {heroMovie && !searchQuery && (
              <div className="relative rounded-3xl overflow-hidden border border-white/15 shadow-2xl min-h-[290px] sm:min-h-[340px] flex items-end">
                <img
                  src={heroMovie.backdrop_url || heroMovie.poster_url}
                  alt={heroMovie.title}
                  className="absolute inset-0 w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#07090E] via-[#07090E]/75 to-transparent" />
                <div className="relative z-10 p-5 sm:p-8 max-w-2xl space-y-3 text-white">
                  <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
                    <span className="px-2.5 py-1 rounded-md bg-cyan-500 text-slate-950 font-bold">
                      ⟢ KOD #{heroMovie.code}
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-white/15 backdrop-blur-md">
                      ✦ IMDb {heroMovie.imdb_rating}
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-emerald-500/20 border border-emerald-400/30 text-emerald-300">
                      480p • 720p • 1080p + Dual Subtitles
                    </span>
                  </div>
                  <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
                    {heroMovie.title}
                  </h1>
                  <p className="text-xs sm:text-sm text-slate-300 line-clamp-2">
                    {heroMovie.description}
                  </p>
                  <div className="flex flex-wrap items-center gap-2.5 pt-1">
                    <button
                      onClick={() => setActiveMovieCode(heroMovie.code)}
                      className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-extrabold text-xs sm:text-sm shadow-lg shadow-cyan-500/25 transition"
                    >
                      <Play className="w-4 h-4 fill-current" />
                      ⟢ Pleyerda Tomosha Qilish
                    </button>
                    <button
                      onClick={() => handleStartWatchParty(heroMovie.code)}
                      className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/15 text-xs sm:text-sm font-semibold transition"
                    >
                      <Users className="w-4 h-4 text-purple-300" />
                      Watch Party Ochish
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* RESUME PLAYBACK STRIP (PRD Section 3.A.4) */}
            {catalogData.continue_watching?.length > 0 && !searchQuery && (
              <section className="space-y-3">
                <h2 className="text-sm font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                  <span>⟢ Tomoshani Davom Ettirish (Har 5s avto-sinxron)</span>
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {catalogData.continue_watching.map((cw) => {
                    const pct = Math.min(
                      95,
                      Math.max(8, Math.round((cw.last_timestamp / (cw.duration_seconds || 600)) * 100))
                    )
                    const mm = String(Math.floor(cw.last_timestamp / 60)).padStart(2, '0')
                    const ss = String(cw.last_timestamp % 60).padStart(2, '0')
                    return (
                      <div
                        key={cw.id}
                        onClick={() => setActiveMovieCode(cw.code)}
                        className={`p-3 rounded-2xl border cursor-pointer transition flex items-center gap-3 ${
                          effectiveDark
                            ? 'bg-white/5 hover:bg-white/10 border-white/10'
                            : 'bg-white hover:bg-slate-50 border-slate-200 shadow-sm'
                        }`}
                      >
                        <img
                          src={cw.poster_url}
                          alt={cw.title}
                          className="w-16 h-20 rounded-xl object-cover shrink-0"
                        />
                        <div className="flex-1 min-w-0 space-y-1.5">
                          <div className="flex items-center justify-between text-[11px] font-mono text-cyan-400">
                            <span>#{cw.code}</span>
                            <span>[{mm}:{ss}] da to'xtagan</span>
                          </div>
                          <h4 className="font-bold text-sm truncate">{cw.title}</h4>
                          <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                            <div
                              className="h-full bg-cyan-400 rounded-full"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </section>
            )}

            {/* CULTURAL HUBS & GENRE FILTER BAR (PRD Section 3.B) */}
            <section className="space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <h2 className="text-sm font-bold uppercase tracking-wider opacity-80">
                  ✦ Katalog, Madaniy Hublar & Edu-Cinema Tillari
                </h2>
                <div className="flex flex-wrap gap-1.5">
                  {LANGUAGE_HUBS.map((lh) => (
                    <button
                      key={lh.id}
                      onClick={() => setSelectedLangHub(lh.id)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-medium transition ${
                        selectedLangHub === lh.id
                          ? 'bg-emerald-500 text-slate-950 font-bold'
                          : effectiveDark
                          ? 'bg-white/5 hover:bg-white/10 text-slate-300'
                          : 'bg-slate-200 text-slate-700'
                      }`}
                    >
                      {lh.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2 overflow-x-auto pb-2">
                {CATALOG_HUBS.map((hub) => (
                  <button
                    key={hub.id}
                    onClick={() => setSelectedCategory(hub.id)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap border transition ${
                      selectedCategory === hub.id
                        ? 'bg-cyan-400 text-slate-950 border-cyan-300 shadow-lg shadow-cyan-500/20'
                        : effectiveDark
                        ? 'bg-white/5 hover:bg-white/10 border-white/10 text-slate-300'
                        : 'bg-white hover:bg-slate-100 border-slate-200 text-slate-700'
                    }`}
                  >
                    {hub.label}
                  </button>
                ))}
              </div>

              {/* MOVIES GRID */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 pt-2">
                {catalogData.movies.map((m) => (
                  <div
                    key={m.id}
                    onClick={() => setActiveMovieCode(m.code)}
                    className={`group rounded-2xl overflow-hidden border cursor-pointer transition hover:-translate-y-1 ${
                      effectiveDark
                        ? 'bg-white/[0.04] hover:bg-white/[0.08] border-white/10'
                        : 'bg-white hover:shadow-lg border-slate-200'
                    }`}
                  >
                    <div className="relative aspect-[3/4] overflow-hidden bg-slate-900">
                      <img
                        src={m.poster_url}
                        alt={m.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />

                      <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5">
                        <span className="px-2 py-0.5 rounded-md bg-black/80 backdrop-blur-md border border-cyan-400/40 font-mono text-[11px] text-cyan-300 font-bold">
                          #{m.code}
                        </span>
                        {m.is_vip_only && (
                          <span className="px-2 py-0.5 rounded-md bg-amber-500 text-slate-950 font-bold text-[10px]">
                            VIP
                          </span>
                        )}
                      </div>

                      <div className="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-md bg-black/75 text-amber-300 font-mono text-[11px] font-bold">
                        ✦ {m.imdb_rating}
                      </div>

                      <div className="absolute bottom-2.5 inset-x-2.5 flex items-center justify-between text-[11px] text-slate-300">
                        <span className="uppercase font-mono px-1.5 py-0.5 rounded bg-white/15 backdrop-blur-md">
                          {m.content_type === 'series' ? 'Serial' : m.year}
                        </span>
                        {m.cefr_level && (
                          <span className="px-1.5 py-0.5 rounded bg-emerald-500/30 border border-emerald-400/40 text-emerald-200 font-mono">
                            {m.cefr_level}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="p-3 space-y-1">
                      <h3 className="font-bold text-sm truncate group-hover:text-cyan-400 transition">
                        {m.title}
                      </h3>
                      <p className="text-[11px] opacity-60 truncate">
                        {m.country} • {m.age_rating}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* HAFTANING TOP-10 FILMI (PRD Section 3.B.6 — Live Weekly Ranking) */}
            <section className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-extrabold tracking-tight flex items-center gap-2">
                  <Flame className="w-5 h-5 text-amber-400" />
                  Haftaning Top-10 Filmi (Oxirgi 7 kunlik Jonli Reyting)
                </h2>
                <span className="text-xs font-mono text-cyan-400">LIVE TOP-10</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                {catalogData.top10_weekly.slice(0, 5).map((m, idx) => (
                  <div
                    key={m.id}
                    onClick={() => setActiveMovieCode(m.code)}
                    className={`p-3 rounded-2xl border cursor-pointer flex items-center gap-3 transition ${
                      effectiveDark
                        ? 'bg-white/[0.03] hover:bg-white/[0.08] border-white/10'
                        : 'bg-white hover:shadow-md border-slate-200'
                    }`}
                  >
                    <span className="text-3xl font-black font-mono text-cyan-400/80">
                      0{idx + 1}
                    </span>
                    <img
                      src={m.poster_url}
                      alt={m.title}
                      className="w-12 h-16 rounded-lg object-cover shrink-0"
                    />
                    <div className="min-w-0">
                      <span className="text-[10px] font-mono text-cyan-400">#{m.code}</span>
                      <h4 className="text-xs font-bold truncate">{m.title}</h4>
                      <p className="text-[11px] opacity-60">
                        👁 {m.view_count_weekly.toLocaleString()} ko'rish
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* FRANSHIZALAR VA KOINOTLAR KLASTERI (PRD Section 3.B.5) */}
            <section className="space-y-3">
              <h2 className="text-base font-extrabold tracking-tight flex items-center gap-2">
                <Compass className="w-5 h-5 text-cyan-400" />
                Franshizalar va Koinotlar Klasteri (Xronologik Tartibda)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {catalogData.franchises.map((fr) => (
                  <div
                    key={fr.id}
                    className={`rounded-2xl overflow-hidden border ${
                      effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                    }`}
                  >
                    <div className="relative h-28">
                      <img
                        src={fr.banner_url}
                        alt={fr.title}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent p-3 flex flex-col justify-end">
                        <h3 className="font-bold text-white text-sm">⟢ {fr.title}</h3>
                        <p className="text-[11px] text-slate-300 line-clamp-1">
                          {fr.description}
                        </p>
                      </div>
                    </div>
                    <div className="p-3 space-y-2">
                      {fr.movies.map((fm, i) => (
                        <button
                          key={fm.id}
                          onClick={() => setActiveMovieCode(fm.code)}
                          className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-black/25 hover:bg-cyan-500/15 border border-white/5 text-xs transition"
                        >
                          <span className="truncate font-medium">
                            {i + 1}. {fm.title} ({fm.year})
                          </span>
                          <span className="font-mono text-cyan-400 ml-2">#{fm.code} ▶</span>
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {/* ==================================================================
            TAB 2: KINO REELS (VERTIKAL SHORTS TIZERLAR LENTASI — PRD 3.D.3)
           ================================================================== */}
        {activeTab === 'reels' && (
          <div className="max-w-lg mx-auto space-y-6">
            <div className="text-center space-y-1">
              <h2 className="text-lg font-extrabold">⟢ Kino Reels (Vertikal Tizerlar Oqimi)</h2>
              <p className="text-xs opacity-70">
                30-60 soniyalik eng qiziqarli sahnalar — 1 bosishda to'liq kinoga o'ting
              </p>
            </div>
            {reels.map((reel) => (
              <div
                key={reel.id}
                className="rounded-3xl overflow-hidden bg-black border border-white/15 shadow-2xl space-y-3 p-3"
              >
                <video
                  src={reel.video_url}
                  controls
                  playsInline
                  loop
                  className="w-full aspect-[9/12] object-cover rounded-2xl bg-slate-950"
                />
                <div className="p-2 flex items-center justify-between gap-3 text-white">
                  <div className="space-y-1">
                    <h3 className="font-bold text-sm">{reel.title}</h3>
                    <p className="text-xs text-slate-400">{reel.caption}</p>
                    <div className="flex items-center gap-3 text-xs text-cyan-300 font-mono">
                      <span>♥ {reel.likes_count}</span>
                      <span>👁 {reel.views_count}</span>
                    </div>
                  </div>
                  {reel.movie && (
                    <button
                      onClick={() => setActiveMovieCode(reel.movie.code)}
                      className="px-4 py-2.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-extrabold text-xs shrink-0 shadow-lg shadow-cyan-500/20"
                    >
                      ⟢ To'liq ko'rish (#{reel.movie.code})
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ==================================================================
            TAB 3: AI & IJTIMOIY MARKAZ (Ruletka, Matcher, Watch Party, AI Critic, Shazam)
           ================================================================== */}
        {activeTab === 'social' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 1. SMART RULETKA ("Nima ko'rsam ekan?" — PRD 3.D.2) */}
            <div
              className={`p-5 rounded-3xl border space-y-4 ${
                effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-extrabold text-base flex items-center gap-2">
                    <Shuffle className="w-5 h-5 text-cyan-400" />
                    «Nima ko'rsam ekan?» (Smart Ruletka)
                  </h3>
                  <p className="text-xs opacity-70">
                    Faqat IMDb &gt; 6.5 bo'lgan yuqori reytingli tasodifiy film tanlanadi
                  </p>
                </div>
                <button
                  onClick={handleSpinRoulette}
                  disabled={rouletteSpinning}
                  className="px-4 py-2 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-extrabold text-xs transition"
                >
                  {rouletteSpinning ? '✦ Aylanmoqda...' : '🎰 Ruletkani Aylantirish'}
                </button>
              </div>

              {rouletteResult && (
                <div className="p-4 rounded-2xl bg-black/40 border border-cyan-400/30 flex items-center gap-4">
                  <img
                    src={rouletteResult.poster_url}
                    alt={rouletteResult.title}
                    className="w-20 h-28 rounded-xl object-cover"
                  />
                  <div className="space-y-1.5 flex-1">
                    <span className="text-xs font-mono text-cyan-300">
                      ✦ RULETKA TANLOVI • KOD #{rouletteResult.code} • IMDb {rouletteResult.imdb_rating}
                    </span>
                    <h4 className="font-bold text-base">{rouletteResult.title}</h4>
                    <p className="text-xs opacity-75 line-clamp-2">
                      {rouletteResult.description}
                    </p>
                    <button
                      onClick={() => setActiveMovieCode(rouletteResult.code)}
                      className="px-3.5 py-1.5 rounded-lg bg-cyan-500 text-slate-950 font-bold text-xs"
                    >
                      ⟢ Hoziroq Tomosha Qilish
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* 2. MOVIE MATCHER (Tinder uslubida kino tanlash — PRD 3.D.4) */}
            <div
              className={`p-5 rounded-3xl border space-y-4 ${
                effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-extrabold text-base flex items-center gap-2">
                    <Heart className="w-5 h-5 text-pink-400" />
                    Movie Matcher (Juftliklar & Do'stlar uchun Tinder)
                  </h3>
                  <p className="text-xs opacity-70">
                    Ikkalangizga ham yoqqan kino chiqsa «Match!» bildirishnomasi chiqadi
                  </p>
                </div>
                {!matcherRoom && (
                  <button
                    onClick={handleStartMatcher}
                    className="px-4 py-2 rounded-xl bg-pink-500 hover:bg-pink-400 text-white font-bold text-xs"
                  >
                    Xona Ochish
                  </button>
                )}
              </div>

              {matcherRoom && catalogData.movies.length > 0 && (
                <div className="space-y-3">
                  <div className="text-xs font-mono text-pink-300 flex items-center justify-between">
                    <span>Xona kodi: {matcherRoom.room_code}</span>
                    <span>Ishtirokchilar: 2 (Sinxron)</span>
                  </div>

                  {matchedMovie ? (
                    <div className="p-4 rounded-2xl bg-gradient-to-r from-pink-500/20 to-cyan-500/20 border border-pink-400 text-center space-y-2">
                      <div className="text-lg font-black text-pink-300">
                        ✦ IT&apos;S A MATCH! Ikkalangizga ham yoqdi!
                      </div>
                      <p className="text-sm font-bold">
                        {matchedMovie.title} (#{matchedMovie.code})
                      </p>
                      <div className="flex justify-center gap-2 pt-1">
                        <button
                          onClick={() => setActiveMovieCode(matchedMovie.code)}
                          className="px-4 py-2 rounded-xl bg-cyan-400 text-slate-950 font-bold text-xs"
                        >
                          ⟢ Birga Tomosha Qilish
                        </button>
                        <button
                          onClick={() => {
                            setMatchedMovie(null)
                            setMatcherIndex((i) => i + 1)
                          }}
                          className="px-3 py-2 rounded-xl bg-white/10 text-xs"
                        >
                          Davom etish
                        </button>
                      </div>
                    </div>
                  ) : (
                    (() => {
                      const cand = catalogData.movies[matcherIndex % catalogData.movies.length]
                      return (
                        <div className="p-3 rounded-2xl bg-black/40 border border-white/10 flex items-center justify-between gap-3">
                          <img
                            src={cand.poster_url}
                            alt={cand.title}
                            className="w-16 h-24 rounded-xl object-cover"
                          />
                          <div className="flex-1 min-w-0">
                            <span className="text-xs font-mono text-cyan-300">
                              #{cand.code} • IMDb {cand.imdb_rating}
                            </span>
                            <h4 className="font-bold text-sm truncate">{cand.title}</h4>
                            <p className="text-xs opacity-70 line-clamp-2">{cand.description}</p>
                          </div>
                          <div className="flex flex-col gap-2">
                            <button
                              onClick={() => handleSwipeMatcher(true)}
                              className="p-2.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500 text-emerald-300 hover:text-slate-950 transition"
                              title="Yoqdi (O'ngga surish)"
                            >
                              <Heart className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleSwipeMatcher(false)}
                              className="p-2.5 rounded-xl bg-rose-500/20 hover:bg-rose-500 text-rose-300 hover:text-white transition"
                              title="Keyingisi (Chapga surish)"
                            >
                              <XIcon className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      )
                    })()
                  )}
                </div>
              )}
            </div>

            {/* 3. AI KINOTANQIDCHI (Mood & Persona Semantic Search — PRD 3.D.7) */}
            <div
              className={`p-5 rounded-3xl border space-y-4 ${
                effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
              }`}
            >
              <h3 className="font-extrabold text-base flex items-center gap-2">
                <Bot className="w-5 h-5 text-emerald-400" />
                AI Kinotanqidchi (Kayfiyat va Mashhur Obrazlar Tahlili)
              </h3>
              <form onSubmit={handleAskCritic} className="space-y-2.5">
                <div className="flex flex-wrap gap-1.5">
                  {[
                    { id: 'tony_stark', label: '🤖 Toni Stark' },
                    { id: 'shum_bola', label: '🍏 Qoravoy (Shum bola)' },
                    { id: 'jaloliddin', label: '⚔️ Jaloliddin Manguberdi' },
                    { id: 'critic', label: '🏆 Oskar Tanqidchisi' },
                  ].map((p) => (
                    <button
                      type="button"
                      key={p.id}
                      onClick={() => setCriticPersona(p.id)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                        criticPersona === p.id
                          ? 'bg-emerald-500 text-slate-950'
                          : 'bg-white/10 text-slate-300'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={criticQuery}
                    onChange={(e) => setCriticQuery(e.target.value)}
                    placeholder="Masalan: Yomg'irli kechada ko'radigan koreyscha triller yoki koinot haqida..."
                    className="flex-1 px-3.5 py-2 rounded-xl bg-black/40 border border-white/15 text-xs outline-none"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs"
                  >
                    Tahlil
                  </button>
                </div>
              </form>

              {criticResponse && (
                <div className="p-4 rounded-2xl bg-black/40 border border-emerald-500/30 space-y-3">
                  <div className="text-xs font-bold text-emerald-300">
                    {criticResponse.persona_name}:
                  </div>
                  <p className="text-xs leading-relaxed opacity-90 whitespace-pre-line">
                    {criticResponse.analysis}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {criticResponse.recommended_movies.map((rm) => (
                      <button
                        key={rm.id}
                        onClick={() => setActiveMovieCode(rm.code)}
                        className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/30 text-emerald-200 text-xs font-mono"
                      >
                        ⟢ {rm.title} (#{rm.code}) ▶
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 4. SHAZAM AI VIDEO/AUDIO QIDIRUV VA WATCH PARTY XONASI */}
            <div
              className={`p-5 rounded-3xl border space-y-4 ${
                effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
              }`}
            >
              <h3 className="font-extrabold text-base flex items-center gap-2">
                <Music className="w-5 h-5 text-amber-400" />
                Shazam AI (Instagram/TikTok Reel va Dialog bo'yicha topish)
              </h3>
              <form onSubmit={handleRunShazam} className="flex gap-2">
                <input
                  type="text"
                  value={shazamClue}
                  onChange={(e) => setShazamClue(e.target.value)}
                  placeholder="Reel tavsifi, dialog yoki sahna (masalan: 'qoravoy olma' yoki 'usmon qilich')"
                  className="flex-1 px-3.5 py-2 rounded-xl bg-black/40 border border-white/15 text-xs outline-none"
                />
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs"
                >
                  Aniqlash
                </button>
              </form>

              {shazamResult && (
                <div className="p-3.5 rounded-2xl bg-black/40 border border-amber-400/30 flex items-center justify-between gap-3">
                  <div>
                    <div className="text-[11px] font-mono text-amber-300">
                      ✦ Aniqlik: {shazamResult.confidence} • Kadr: [{shazamResult.matched_timecode}]
                    </div>
                    <h4 className="font-bold text-sm">
                      {shazamResult.movie.title} (#{shazamResult.movie.code})
                    </h4>
                  </div>
                  <button
                    onClick={() => setActiveMovieCode(shazamResult.movie.code)}
                    className="px-3 py-1.5 rounded-lg bg-amber-400 text-slate-950 font-bold text-xs"
                  >
                    Ochish ▶
                  </button>
                </div>
              )}

              {/* Active Watch Party Box */}
              <div className="pt-2 border-t border-white/10 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold flex items-center gap-1.5 text-purple-300">
                    <Users className="w-4 h-4" /> Watch Party (Sinxron Tomosha Xonasi)
                  </span>
                  {!watchPartyRoom && (
                    <button
                      onClick={() => handleStartWatchParty(421)}
                      className="px-3 py-1 rounded-lg bg-purple-500 text-white text-xs font-bold"
                    >
                      Xona Yaratish
                    </button>
                  )}
                </div>

                {watchPartyRoom && (
                  <div className="p-3 rounded-2xl bg-purple-950/30 border border-purple-400/30 space-y-2">
                    <div className="flex items-center justify-between text-xs font-mono text-purple-200">
                      <span>Xona: {watchPartyRoom.room_id}</span>
                      <button
                        onClick={() => setActiveMovieCode(watchPartyRoom.movie_code)}
                        className="underline text-cyan-300"
                      >
                        Pleyerga o'tish (#{watchPartyRoom.movie_code}) ▶
                      </button>
                    </div>
                    <div className="space-y-1 max-h-24 overflow-y-auto text-xs">
                      {watchPartyRoom.messages.map((msg, i) => (
                        <div key={i}>
                          <b className="text-purple-300">{msg.sender}: </b>
                          <span>{msg.text}</span>
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-1.5">
                      <input
                        type="text"
                        value={partyChatInput}
                        onChange={(e) => setPartyChatInput(e.target.value)}
                        placeholder="Xonaga xabar yoki reaksiya yozing..."
                        className="flex-1 bg-black/50 border border-white/10 rounded-lg px-2.5 py-1 text-xs"
                      />
                      <button
                        onClick={() => {
                          if (!partyChatInput.trim()) return
                          setWatchPartyRoom((prev) => ({
                            ...prev,
                            messages: [
                              ...prev.messages,
                              { sender: 'Siz ✦', text: partyChatInput },
                            ],
                          }))
                          setPartyChatInput('')
                        }}
                        className="px-3 py-1 rounded-lg bg-purple-500 text-white text-xs font-bold"
                      >
                        Yuborish
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================
            TAB 4: 1-MODUL (CINEPROFILE IJTIMOIY TARMOG'I), GEYMIFIKATSIYA, LUG'AT & VIP
           ================================================================== */}
        {activeTab === 'profile' && profileData && (
          <div className="space-y-6">
            {/* 1-MODUL: MUSTAQIL CINEPROFILE KARTASI (Telegramdan mustaqil @username, Avatar, Bio, Badges, Followers) */}
            <div
              className={`p-5 sm:p-6 rounded-3xl border space-y-5 ${
                effectiveDark
                  ? 'bg-gradient-to-br from-cyan-950/35 via-white/[0.04] to-amber-950/25 border-cyan-400/30'
                  : 'bg-white border-slate-200 shadow-sm'
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div
                    className={`relative w-20 h-20 rounded-3xl p-1 ${
                      profileData.user.patron_tier === 'gold'
                        ? 'bg-gradient-to-tr from-amber-400 via-yellow-200 to-amber-600 shadow-lg shadow-amber-500/30'
                        : profileData.user.patron_tier === 'silver'
                        ? 'bg-gradient-to-tr from-slate-300 to-cyan-300'
                        : 'bg-cyan-500/40'
                    }`}
                  >
                    <img
                      src={
                        profileData.user.avatar_url ||
                        'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=240&q=80'
                      }
                      alt={profileData.user.full_name}
                      className="w-full h-full object-cover rounded-2xl bg-slate-900"
                    />
                    <span className="absolute -bottom-1.5 -right-1.5 px-2 py-0.5 rounded-full bg-amber-400 text-slate-950 font-black text-[10px] uppercase">
                      {profileData.user.patron_tier === 'gold'
                        ? '🥇 GOLD'
                        : profileData.user.patron_tier === 'silver'
                        ? '🥈 SILVER'
                        : '✦ PRO'}
                    </span>
                  </div>
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-xl font-extrabold">{profileData.user.full_name}</h2>
                      <span className="px-2.5 py-0.5 rounded-lg bg-cyan-500/20 border border-cyan-400/40 font-mono text-xs text-cyan-300 font-bold">
                        @{profileData.user.cine_username}
                      </span>
                    </div>
                    <p className="text-xs opacity-80 max-w-xl">{profileData.user.bio}</p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {(profileData.user.badges || []).map((b, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-400/30 text-amber-300 text-[11px] font-semibold"
                        >
                          {b}
                        </span>
                      ))}
                      {(profileData.user.favorite_genres || []).map((g, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded-md bg-white/10 text-slate-300 text-[11px] font-mono"
                        >
                          #{g}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Followers / Following / Likes Social Counters */}
                <div className="flex items-center gap-3 bg-black/40 border border-white/10 rounded-2xl px-4 py-3 text-center">
                  <div>
                    <div className="text-lg font-black text-cyan-300">
                      {profileData.user.followers_count}
                    </div>
                    <div className="text-[10px] uppercase font-mono opacity-65">Obunachilar</div>
                  </div>
                  <div className="h-8 w-px bg-white/10" />
                  <div>
                    <div className="text-lg font-black text-purple-300">
                      {profileData.user.following_count}
                    </div>
                    <div className="text-[10px] uppercase font-mono opacity-65">Obunalar</div>
                  </div>
                  <div className="h-8 w-px bg-white/10" />
                  <div>
                    <div className="text-lg font-black text-amber-300">
                      {profileData.user.total_likes_received}
                    </div>
                    <div className="text-[10px] uppercase font-mono opacity-65">Layk & Mukofot</div>
                  </div>
                </div>
              </div>

              {/* Quick Demo Profiles Switcher (Inspect other users' CineProfiles!) */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-white/10 text-xs">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="opacity-70">🔍 Do&apos;stlar CineProfile sahifasini ko&apos;rish:</span>
                  {['marvel_malika', 'javohir_cine', 'kinochi_nodir'].map((nick) => (
                    <button
                      key={nick}
                      type="button"
                      onClick={() => handleOpenCineProfile(nick)}
                      className="px-2.5 py-1 rounded-lg bg-cyan-500/15 hover:bg-cyan-400 text-cyan-300 hover:text-slate-950 font-mono font-bold transition"
                    >
                      @{nick}
                    </button>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={() => setActiveTab('economy')}
                  className="px-3.5 py-1.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold text-xs flex items-center gap-1.5"
                >
                  <Gift className="w-3.5 h-3.5" /> Do&apos;stga VIP / Balans Sovg&apos;a Qilish
                </button>
              </div>

              {/* Edit @cine_username, Bio & Privacy Controls */}
              <form
                onSubmit={handleSaveCineProfile}
                className="grid grid-cols-1 md:grid-cols-4 gap-2.5 pt-2 border-t border-white/10 text-xs"
              >
                <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-black/40 border border-white/15">
                  <AtSign className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <input
                    type="text"
                    value={profileEditForm.cine_username}
                    onChange={(e) =>
                      setProfileEditForm({ ...profileEditForm, cine_username: e.target.value })
                    }
                    placeholder="cine_username"
                    className="bg-transparent outline-none w-full font-mono text-cyan-200"
                  />
                </div>
                <input
                  type="text"
                  value={profileEditForm.bio}
                  onChange={(e) => setProfileEditForm({ ...profileEditForm, bio: e.target.value })}
                  placeholder="Bio tavsifi..."
                  className="px-3 py-2 rounded-xl bg-black/40 border border-white/15 outline-none"
                />
                <select
                  value={profileEditForm.mention_privacy}
                  onChange={(e) =>
                    setProfileEditForm({ ...profileEditForm, mention_privacy: e.target.value })
                  }
                  className="px-3 py-2 rounded-xl bg-black/40 border border-white/15 outline-none text-slate-200"
                >
                  <option value="all">@Atmetka: Hamma chaqira oladi</option>
                  <option value="following">@Atmetka: Faqat obunalarim</option>
                  <option value="none">@Atmetka: Hech kim (Anti-Spam)</option>
                </select>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-extrabold transition"
                >
                  ✦ Profilni Saqlash
                </button>
              </form>

              {profileStatusMsg && (
                <div className="p-3 rounded-xl bg-cyan-500/20 border border-cyan-400/40 text-xs font-bold text-cyan-200">
                  {profileStatusMsg}
                </div>
              )}
            </div>

            {/* ICHKI BILDIRISHNOMALAR (@ATMETKA & SOVG'ALAR) + SHAXSIY KINO-KOLLEKSIYALAR */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* @Atmetka, Reply & Gift Notifications Inbox */}
              <div
                className={`p-5 rounded-3xl border space-y-3 ${
                  effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-extrabold text-base flex items-center gap-2">
                    <Bell className="w-5 h-5 text-rose-400" />
                    Ichki Bildirishnomalar (@Atmetka, Sovg&apos;a &amp; Mukofot)
                  </h3>
                  <button
                    onClick={async () => {
                      await fetch('/api/notifications/read', { method: 'POST' })
                      loadProfileAndVocab()
                    }}
                    className="text-xs text-cyan-400 hover:underline"
                  >
                    O&apos;qilgan deb belgilash
                  </button>
                </div>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {(profileData.notifications || []).map((n) => (
                    <div
                      key={n.id}
                      className={`p-3 rounded-2xl border flex items-start justify-between gap-2 text-xs ${
                        n.is_read
                          ? 'bg-black/25 border-white/5 opacity-75'
                          : 'bg-cyan-500/10 border-cyan-400/30'
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => handleOpenCineProfile(n.sender_username)}
                            className="font-mono font-bold text-cyan-300 hover:underline"
                          >
                            @{n.sender_username}
                          </button>
                          <span className="px-1.5 py-0.5 rounded bg-white/10 text-[10px] uppercase font-mono">
                            {n.notif_type}
                          </span>
                        </div>
                        <p className="text-slate-200">{n.message}</p>
                      </div>
                      {n.movie_code && (
                        <button
                          onClick={() => setActiveMovieCode(n.movie_code)}
                          className="px-2.5 py-1 rounded-lg bg-cyan-400 text-slate-950 font-bold text-[11px] shrink-0"
                        >
                          #{n.movie_code} ▶
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Public Custom Movie Lists (Shaxsiy Kino-Kolleksiyalar) */}
              <div
                className={`p-5 rounded-3xl border space-y-3 ${
                  effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                }`}
              >
                <h3 className="font-extrabold text-base flex items-center gap-2">
                  <ListPlus className="w-5 h-5 text-emerald-400" />
                  Ochiq Kino-Kolleksiyalar (Public Custom Lists)
                </h3>
                <form onSubmit={handleCreateCustomList} className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                  <input
                    type="text"
                    value={newListForm.title}
                    onChange={(e) => setNewListForm({ ...newListForm, title: e.target.value })}
                    placeholder="To'plam nomi (masalan: Top-5 Nolan)"
                    className="px-3 py-1.5 rounded-xl bg-black/40 border border-white/15 outline-none"
                  />
                  <input
                    type="text"
                    value={newListForm.codesText}
                    onChange={(e) => setNewListForm({ ...newListForm, codesText: e.target.value })}
                    placeholder="Kodlar: 421, 502, 101"
                    className="px-3 py-1.5 rounded-xl bg-black/40 border border-white/15 outline-none font-mono"
                  />
                  <button
                    type="submit"
                    className="px-3 py-1.5 rounded-xl bg-emerald-500 text-slate-950 font-extrabold"
                  >
                    + Kolleksiya Yaratish
                  </button>
                </form>

                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {(profileData.custom_lists || []).map((cl) => (
                    <div
                      key={cl.id}
                      className="p-3 rounded-2xl bg-black/35 border border-white/10 space-y-1.5 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="font-bold text-slate-100">{cl.title}</span>
                          <button
                            type="button"
                            onClick={() => handleOpenCineProfile(cl.cine_username)}
                            className="ml-2 font-mono text-cyan-300 hover:underline"
                          >
                            by @{cl.cine_username}
                          </button>
                        </div>
                        <button
                          onClick={async () => {
                            await fetch(`/api/cineprofile/lists/${cl.id}/like`, { method: 'POST' })
                            loadProfileAndVocab()
                          }}
                          className="px-2 py-0.5 rounded-lg bg-pink-500/20 text-pink-300 font-mono text-[11px]"
                        >
                          ♥ {cl.likes_count}
                        </button>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {(cl.movie_codes || []).map((mc) => (
                          <button
                            key={mc}
                            onClick={() => setActiveMovieCode(mc)}
                            className="px-2 py-0.5 rounded bg-cyan-500/15 hover:bg-cyan-400 text-cyan-300 hover:text-slate-950 font-mono text-[11px] font-bold transition"
                          >
                            Kino #{mc} ▶
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Top Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-cyan-500/15 to-blue-600/10 border border-cyan-400/30">
                <div className="text-xs text-cyan-300 font-mono">🔥 FAOL STREAK</div>
                <div className="text-2xl font-black mt-1">
                  {profileData.streak.current_streak} kun
                </div>
                <div className="text-[11px] opacity-70">
                  Rekord: {profileData.streak.max_streak} kun
                </div>
              </div>
              <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-500/15 to-orange-600/10 border border-amber-400/30">
                <div className="text-xs text-amber-300 font-mono">🏆 OYLIK MARAFON</div>
                <div className="text-2xl font-black mt-1">
                  {profileData.streak.marathon_points} ball
                </div>
                <div className="text-[11px] opacity-70">1-o'ringa Yillik VIP</div>
              </div>
              <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500/15 to-teal-600/10 border border-emerald-400/30">
                <div className="text-xs text-emerald-300 font-mono">🎓 EDU-LUG'ATIM</div>
                <div className="text-2xl font-black mt-1">{vocabulary.length} ta so'z</div>
                <div className="text-[11px] opacity-70">Kinolardan o'rganilgan</div>
              </div>
              <div className="p-4 rounded-2xl bg-gradient-to-br from-purple-500/15 to-pink-600/10 border border-purple-400/30">
                <div className="text-xs text-purple-300 font-mono">👑 OBUNA MAQOMI</div>
                <div className="text-xl font-black mt-1 uppercase">
                  {profileData.user.is_vip ? '✦ VIP FAOL' : 'BEPUL TARIF'}
                </div>
                <div className="text-[11px] opacity-70">
                  Jami: {profileData.streak.total_watch_hours} soat ko'rilgan
                </div>
              </div>
            </div>

            {/* GITHUB-STYLE ACTIVITY HEATMAP & 30-DAY CHALLENGE (PRD Section 3.C.1 & 3.C.2) */}
            <div
              className={`p-5 rounded-3xl border space-y-4 ${
                effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h3 className="font-extrabold text-base">
                    ⟢ Activity Heatmap (Oxirgi 30 Kunlik Faollik Xaritasi)
                  </h3>
                  <p className="text-xs opacity-70">
                    «30 Kunlik Chellenj»: Har kuni kamida 15 daqiqa tomosha qiling va avtomatik 1 Oylik Bepul VIP oling!
                  </p>
                </div>
                <span className="px-3 py-1 rounded-xl bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 font-mono text-xs">
                  Chellenj: {profileData.streak.challenge_30_progress} / 30 kun
                </span>
              </div>

              {/* 30 Green Heatmap Cells */}
              <div className="grid grid-cols-10 sm:grid-cols-15 gap-2">
                {profileData.heatmap.map((cell, idx) => {
                  const m = cell.minutes
                  const color =
                    m === 0
                      ? 'bg-white/10 border-white/5'
                      : m < 30
                      ? 'bg-emerald-900/70 border-emerald-700/50'
                      : m < 60
                      ? 'bg-emerald-600/80 border-emerald-400/50'
                      : 'bg-emerald-400 border-emerald-200 shadow-sm shadow-emerald-400/40'
                  return (
                    <div
                      key={idx}
                      title={`${cell.date}: ${cell.minutes} daqiqa`}
                      className={`h-8 rounded-lg border flex items-center justify-center text-[10px] font-mono ${color}`}
                    >
                      {m}m
                    </div>
                  )
                })}
              </div>
            </div>

            {/* EDU-CINEMA INTERACTIVE VOCABULARY FLASHCARDS & LIVE MARATHON LEADERBOARD */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Personal Vocabulary Flashcards */}
              <div
                className={`p-5 rounded-3xl border space-y-3 ${
                  effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                }`}
              >
                <h3 className="font-extrabold text-base flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-cyan-400" />
                  Edu-Cinema Shaxsiy Lug'atim (Subtitrdan saqlangan so'zlar)
                </h3>
                <div className="space-y-2 max-h-72 overflow-y-auto">
                  {vocabulary.map((v) => (
                    <div
                      key={v.id}
                      className="p-3 rounded-2xl bg-black/35 border border-white/10 flex items-start justify-between gap-2"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-cyan-300">{v.word}</span>
                          <span className="text-xs px-1.5 py-0.5 rounded bg-white/10 uppercase font-mono">
                            {v.source_lang}
                          </span>
                          <span className="text-xs font-semibold text-emerald-300">
                            — {v.translation}
                          </span>
                        </div>
                        {v.context_sentence && (
                          <p className="text-[11px] opacity-65 italic mt-1">
                            «{v.context_sentence}»
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Monthly Marathon Live Leaderboard (PRD Section 3.C.3) */}
              <div
                className={`p-5 rounded-3xl border space-y-3 ${
                  effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                }`}
              >
                <h3 className="font-extrabold text-base flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-amber-400" />
                  Oylik Marafon (Live Leaderboard)
                </h3>
                <p className="text-xs opacity-70">
                  Kino ko'rish (+10), kunlik kirish (+5), 7 kunlik streak (+20), do'st taklif qilish (+15)
                </p>
                <div className="space-y-2">
                  {profileData.leaderboard.map((row) => (
                    <div
                      key={row.rank}
                      className="p-3 rounded-2xl bg-black/35 border border-white/10 flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <span className="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-300 font-mono font-bold text-xs flex items-center justify-center">
                          #{row.rank}
                        </span>
                        <div>
                          <div className="font-bold text-sm">{row.full_name}</div>
                          <div className="text-[11px] opacity-60">
                            Streak: {row.streak} kun
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono font-bold text-sm text-cyan-300">
                          {row.points} ball
                        </div>
                        <div className="text-[10px] text-amber-300">{row.prize}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* MONETIZATION: 3-TIER VIP + TELEGRAM STARS / PAYME / CLICK + INSTAGRAM GROWTH GATE */}
            <div
              className={`p-5 rounded-3xl border space-y-4 ${
                effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="font-extrabold text-base flex items-center gap-2">
                    <Crown className="w-5 h-5 text-amber-400" />
                    3 Bosqichli VIP Obuna (Telegram Stars, Payme, Click)
                  </h3>
                  <p className="text-xs opacity-70">
                    Reklamasiz 1080p, barcha premyeralar, Edu-Cinema ikki qavatli subtitrlar va shaxsiy buyurtmalar
                  </p>
                </div>

                {/* Instagram Growth Gate (PRD 3.F.2) */}
                <button
                  onClick={async () => {
                    await fetch('/api/vip/instagram-gate', { method: 'POST' })
                    loadProfileAndVocab()
                  }}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-pink-500 to-amber-500 text-slate-950 font-extrabold text-xs shadow-lg"
                >
                  <Instagram className="w-4 h-4" />
                  Instagram Obuna = +7 Kun Bepul VIP!
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  {
                    code: 'vip_1m',
                    title: 'Standart VIP (1 Oy)',
                    price: "29,000 so'm / 150 Stars",
                    perks: ['Reklamasiz 1080p Full HD', 'Ikki qavatli subtitrlar (Edu-Cinema)', 'Majburiy kanallarsiz'],
                  },
                  {
                    code: 'vip_3m',
                    title: 'Premium VIP (3 Oy)',
                    price: "69,000 so'm / 350 Stars",
                    perks: ['Barcha Standart imtiyozlar', 'Yopiq erta premyeralar', 'Shaxsiy kino buyurtma (VIP Desk)'],
                  },
                  {
                    code: 'vip_1y',
                    title: 'Founder VIP (1 Yil + Oyna-Bot)',
                    price: "199,000 so'm / 950 Stars",
                    perks: ['1 yil cheksiz 4K/1080p', 'Shaxsiy Mirror-Bot ochish huquqi', 'Smart TV 5 ta qurilma'],
                  },
                ].map((plan) => (
                  <div
                    key={plan.code}
                    className="p-4 rounded-2xl bg-black/40 border border-white/10 flex flex-col justify-between space-y-3"
                  >
                    <div className="space-y-2">
                      <h4 className="font-bold text-sm text-amber-300">✦ {plan.title}</h4>
                      <div className="text-lg font-black">{plan.price}</div>
                      <ul className="space-y-1 text-xs opacity-80">
                        {plan.perks.map((pk, i) => (
                          <li key={i}>▹ {pk}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="grid grid-cols-3 gap-1.5 pt-2">
                      {['stars', 'payme', 'click'].map((prov) => (
                        <button
                          key={prov}
                          onClick={async () => {
                            await fetch('/api/vip/upgrade', {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ provider: prov, plan_code: plan.code }),
                            })
                            loadProfileAndVocab()
                          }}
                          className="py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-400 hover:text-slate-950 border border-cyan-400/30 text-[11px] font-bold uppercase transition"
                        >
                          {prov}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* REQUEST DESK (PRD 3.D.8 — Topilmagan kinolarni buyurtma qilish) */}
            <div
              className={`p-5 rounded-3xl border space-y-3 ${
                effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
              }`}
            >
              <h3 className="font-extrabold text-base">
                ⟢ Request Desk (Kino Buyurtma Qilish & Takliflar Stol)
              </h3>
              <form
                onSubmit={async (e) => {
                  e.preventDefault()
                  if (!newRequestText.trim()) return
                  await fetch('/api/requests', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query_text: newRequestText }),
                  })
                  setNewRequestText('')
                  loadProfileAndVocab()
                }}
                className="flex gap-2"
              >
                <input
                  type="text"
                  value={newRequestText}
                  onChange={(e) => setNewRequestText(e.target.value)}
                  placeholder="Topilmagan kino nomi va yilini yozing..."
                  className="flex-1 px-3.5 py-2 rounded-xl bg-black/40 border border-white/15 text-xs outline-none"
                />
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-cyan-400 text-slate-950 font-bold text-xs"
                >
                  Buyurtma berish
                </button>
              </form>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {requestsData.requests.map((r) => (
                  <div
                    key={r.id}
                    className="p-3 rounded-xl bg-black/35 border border-white/10 flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-semibold">{r.query_text}</div>
                      {r.admin_reply && (
                        <div className="text-emerald-300 text-[11px] mt-0.5">
                          ✦ {r.admin_reply}
                        </div>
                      )}
                    </div>
                    <span className="px-2 py-0.5 rounded bg-white/10 font-mono uppercase text-[10px]">
                      {r.status} ({r.votes_count} ovoz)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================
            TAB 5: 2-MODUL (CINEWALLET & GIFTING) VA 3-MODUL (DONAT & CROWDFUNDING)
           ================================================================== */}
        {activeTab === 'economy' && walletData && crowdfundingData && (
          <div className="space-y-8">
            {economyNotice && (
              <div className="p-4 rounded-2xl bg-emerald-500/20 border border-emerald-400/40 text-emerald-200 font-bold text-xs sm:text-sm flex items-center justify-between">
                <span>{economyNotice}</span>
                <button onClick={() => setEconomyNotice(null)} className="text-xs underline">
                  Yopish
                </button>
              </div>
            )}

            {/* 2-MODUL: CINEWALLET DUAL-BALANCE & DIRECT GIFTING */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Dual-Balance Card & 1-Click Top-Up */}
              <div
                className={`p-5 rounded-3xl border space-y-4 ${
                  effectiveDark
                    ? 'bg-gradient-to-br from-amber-500/15 via-white/[0.03] to-cyan-500/10 border-amber-400/30'
                    : 'bg-white border-slate-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono uppercase text-amber-300 flex items-center gap-1.5">
                    <Wallet className="w-4 h-4" /> 2-MODUL: CineWallet Hamyonim
                  </span>
                  <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono text-[10px] uppercase">
                    Patron: {walletData.patron_tier}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-2xl bg-black/40 border border-cyan-400/30">
                    <div className="text-[10px] font-mono text-cyan-300 uppercase">
                      Asosiy Balans (Transferable)
                    </div>
                    <div className="text-xl font-black mt-1">
                      {walletData.wallet_balance_uzs.toLocaleString()} UZS
                    </div>
                    <div className="text-[10px] opacity-65 mt-0.5">
                      Sovg&apos;a va Donat uchun ochiq
                    </div>
                  </div>
                  <div className="p-3 rounded-2xl bg-black/40 border border-purple-400/30">
                    <div className="text-[10px] font-mono text-purple-300 uppercase">
                      Bonus Balans (Anti-Abuse)
                    </div>
                    <div className="text-xl font-black mt-1">
                      {walletData.bonus_balance_uzs.toLocaleString()} UZS
                    </div>
                    <div className="text-[10px] opacity-65 mt-0.5">
                      Faqat shaxsiy VIP uchun
                    </div>
                  </div>
                </div>

                <div className="space-y-2 pt-1">
                  <div className="text-xs font-bold opacity-80">
                    ⚡ Hisobni 1-bosishda to&apos;ldirish (Payme / Click / Stars):
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      { prov: 'payme', amt: 50000, label: '+50k Payme' },
                      { prov: 'click', amt: 100000, label: '+100k Click' },
                      { prov: 'stars', amt: 150000, label: '+150k Stars' },
                    ].map((b, i) => (
                      <button
                        key={i}
                        onClick={() => handleTopupWallet(b.prov, b.amt)}
                        className="py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-400 text-cyan-200 hover:text-slate-950 border border-cyan-400/30 text-xs font-bold transition"
                      >
                        {b.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Direct Gift to Friend (@username) */}
              <form
                onSubmit={handleSendGift}
                className={`p-5 rounded-3xl border space-y-3 ${
                  effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                }`}
              >
                <h3 className="font-extrabold text-base flex items-center gap-2">
                  <Gift className="w-5 h-5 text-pink-400" />
                  Do&apos;stiga VIP va Balans Hadya Qilish (@username)
                </h3>
                <p className="text-xs opacity-70">
                  Do&apos;stingizning CineProfile nikini kiriting (masalan: <code>@marvel_malika</code> yoki <code>@javohir_cine</code>)
                </p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <input
                    type="text"
                    value={giftForm.recipient_username}
                    onChange={(e) =>
                      setGiftForm({ ...giftForm, recipient_username: e.target.value })
                    }
                    placeholder="@marvel_malika"
                    className="px-3 py-2 rounded-xl bg-black/40 border border-white/15 font-mono text-cyan-300 outline-none"
                  />
                  <select
                    value={giftForm.gift_type}
                    onChange={(e) => setGiftForm({ ...giftForm, gift_type: e.target.value })}
                    className="px-3 py-2 rounded-xl bg-black/40 border border-white/15 text-amber-300 outline-none"
                  >
                    <option value="vip_1m">🎁 1 Oylik VIP (29,000 UZS)</option>
                    <option value="vip_3m">🎁 3 Oylik VIP (69,000 UZS)</option>
                    <option value="vip_1y">👑 1 Yillik VIP (199,000 UZS)</option>
                    <option value="balance">💸 Balans O&apos;tkazish (25,000 UZS)</option>
                  </select>
                </div>
                <input
                  type="text"
                  value={giftForm.message}
                  onChange={(e) => setGiftForm({ ...giftForm, message: e.target.value })}
                  placeholder="Tabriknoma matni..."
                  className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/15 text-xs outline-none"
                />
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-pink-500 to-amber-500 hover:opacity-95 text-slate-950 font-extrabold text-xs shadow-lg"
                >
                  🎁 Hadya Yuborish (Tabriknoma bilan)
                </button>
              </form>

              {/* Gift Voucher Drop ("Oltin Chipta" Guruhlar uchun) */}
              <div
                className={`p-5 rounded-3xl border space-y-3 ${
                  effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                }`}
              >
                <h3 className="font-extrabold text-base flex items-center gap-2">
                  <Ticket className="w-5 h-5 text-amber-400" />
                  «Oltin Chipta» (Guruh uchun Gift Voucher Drop)
                </h3>
                <p className="text-xs opacity-70">
                  Telegram guruh yoki kanalga tashlash uchun 1 martalik VIP vaucher yarating — birinchi bosgan odam VIP oladi!
                </p>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => handleCreateVoucher('vip_1m')}
                    className="py-2 rounded-xl bg-amber-500/20 hover:bg-amber-400 text-amber-300 hover:text-slate-950 border border-amber-400/30 text-xs font-bold transition"
                  >
                    + 1 Oylik Chipta (29k)
                  </button>
                  <button
                    type="button"
                    onClick={() => handleCreateVoucher('vip_3m')}
                    className="py-2 rounded-xl bg-purple-500/20 hover:bg-purple-400 text-purple-300 hover:text-slate-950 border border-purple-400/30 text-xs font-bold transition"
                  >
                    + 3 Oylik Chipta (69k)
                  </button>
                </div>

                <form onSubmit={handleClaimVoucher} className="flex gap-2 pt-1">
                  <input
                    type="text"
                    value={voucherClaimCode}
                    onChange={(e) => setVoucherClaimCode(e.target.value)}
                    placeholder="Vaucher kodi: GIFT-VIP-2026"
                    className="flex-1 px-3 py-2 rounded-xl bg-black/40 border border-white/15 text-xs font-mono text-amber-300 outline-none"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 font-extrabold text-xs"
                  >
                    Faollashtirish
                  </button>
                </form>

                <div className="space-y-1 max-h-24 overflow-y-auto text-[11px] font-mono">
                  {(walletData.vouchers || []).slice(0, 3).map((v) => (
                    <div
                      key={v.id}
                      className="flex items-center justify-between px-2.5 py-1 rounded bg-black/40 border border-white/5"
                    >
                      <span className="text-amber-300">{v.code}</span>
                      <span className={v.is_claimed ? 'text-slate-500' : 'text-emerald-400'}>
                        {v.is_claimed ? `Band (@${v.claimed_by_username})` : '✦ Faol (Ochiq)'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 3-MODUL: DONAT & CROWDFUNDING (Xalqona Dublyaj & 4K Reliz Fondi + Hall of Fame) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Active Crowdfunding Campaigns (2 columns wide) */}
              <div
                className={`lg:col-span-2 p-5 rounded-3xl border space-y-4 ${
                  effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                }`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <h3 className="font-extrabold text-base flex items-center gap-2">
                      <Flame className="w-5 h-5 text-amber-400" />
                      3-MODUL: Xalqona Dublyaj &amp; 4K Restavratsiya Crowdfunding Fondi
                    </h3>
                    <p className="text-xs opacity-70">
                      Hissa qo&apos;shgan homiylar ismi film sahifasida va pleyer boshlanishidagi oltin titrda abadiy yoziladi!
                    </p>
                  </div>
                  <span className="px-2.5 py-1 rounded-xl bg-emerald-500/15 border border-emerald-400/30 text-emerald-300 text-[11px] font-mono">
                    🛡️ 100% Escrow Qaytarish Kafolati
                  </span>
                </div>

                <div className="space-y-4">
                  {(crowdfundingData.campaigns || []).map((camp) => (
                    <div
                      key={camp.id}
                      className="p-4 rounded-2xl bg-black/45 border border-white/10 flex flex-col sm:flex-row gap-4"
                    >
                      <img
                        src={camp.poster_url}
                        alt={camp.title}
                        className="w-24 h-32 rounded-xl object-cover shrink-0"
                      />
                      <div className="flex-1 space-y-2.5">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono text-[11px] font-bold">
                            Kino #{camp.movie_code} • {camp.target_type.toUpperCase()}
                          </span>
                          <span className="text-xs font-mono text-amber-300">
                            ⏱ {camp.deadline_days} kun qoldi • {camp.donors_count} homiy
                          </span>
                        </div>
                        <h4 className="font-bold text-sm sm:text-base">{camp.title}</h4>
                        <p className="text-xs opacity-75">{camp.description}</p>

                        {/* Progress Bar */}
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs font-mono">
                            <span className="text-emerald-300 font-bold">
                              Yig&apos;ildi: {camp.collected_uzs.toLocaleString()} UZS ({camp.progress_pct}%)
                            </span>
                            <span className="opacity-70">
                              Maqsad: {camp.goal_uzs.toLocaleString()} UZS
                            </span>
                          </div>
                          <div className="w-full h-2.5 rounded-full bg-white/10 overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-cyan-400 via-emerald-400 to-amber-400 rounded-full transition-all duration-500"
                              style={{ width: `${camp.progress_pct}%` }}
                            />
                          </div>
                        </div>

                        {/* 1-Click Donate Buttons */}
                        <div className="flex flex-wrap items-center gap-2 pt-1">
                          {[15000, 50000, 100000].map((amt) => (
                            <button
                              key={amt}
                              onClick={() => handleDonateCampaign(camp.id, amt)}
                              className="px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-400 text-amber-200 hover:text-slate-950 border border-amber-400/40 text-xs font-bold transition"
                            >
                              ✦ +{amt.toLocaleString()} UZS Hissa Qo&apos;shish
                            </button>
                          ))}
                          {camp.movie_code && (
                            <button
                              onClick={() => setActiveMovieCode(camp.movie_code)}
                              className="ml-auto px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-mono text-cyan-300"
                            >
                              Kinoni Ochish (#{camp.movie_code}) ▶
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Homiylar Shon-Sharaf Zali (Patron Hall of Fame & Ledger) */}
              <div className="space-y-6">
                <div
                  className={`p-5 rounded-3xl border space-y-3 ${
                    effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                  }`}
                >
                  <h3 className="font-extrabold text-base flex items-center gap-2">
                    <Crown className="w-5 h-5 text-amber-400" />
                    Homiylar Shon-Sharaf Zali (Hall of Fame)
                  </h3>
                  <p className="text-xs opacity-70">
                    🥉 Bronze (10k+) • 🥈 Silver (50k+, x3 ovoz) • 🥇 Gold Legend (150k+, Oltin ramka)
                  </p>
                  <div className="space-y-2">
                    {(crowdfundingData.hall_of_fame || []).map((p) => (
                      <div
                        key={p.rank}
                        onClick={() => handleOpenCineProfile(p.cine_username)}
                        className="p-3 rounded-2xl bg-black/40 hover:bg-white/10 border border-amber-400/25 flex items-center justify-between cursor-pointer transition"
                      >
                        <div className="flex items-center gap-2.5">
                          <img
                            src={
                              p.avatar_url ||
                              'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80'
                            }
                            alt={p.full_name}
                            className="w-9 h-9 rounded-xl object-cover"
                          />
                          <div>
                            <div className="text-xs font-bold flex items-center gap-1">
                              <span className="font-mono text-cyan-300">@{p.cine_username}</span>
                              {p.patron_tier === 'gold' && <span>🥇</span>}
                              {p.patron_tier === 'silver' && <span>🥈</span>}
                              {p.patron_tier === 'bronze' && <span>🥉</span>}
                            </div>
                            <div className="text-[11px] opacity-65">{p.full_name}</div>
                          </div>
                        </div>
                        <div className="text-right font-mono">
                          <div className="text-xs font-bold text-amber-300">
                            {p.total_donated_uzs.toLocaleString()} UZS
                          </div>
                          <div className="text-[10px] uppercase opacity-60">{p.patron_tier}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Wallet Ledger Transactions */}
                <div
                  className={`p-5 rounded-3xl border space-y-3 ${
                    effectiveDark ? 'bg-white/5 border-white/10' : 'bg-white border-slate-200'
                  }`}
                >
                  <h3 className="font-extrabold text-sm">📜 Oxirgi Tranzaksiyalar (Ledger)</h3>
                  <div className="space-y-2 max-h-56 overflow-y-auto text-xs">
                    {(walletData.transactions || []).map((tx) => (
                      <div
                        key={tx.id}
                        className="p-2.5 rounded-xl bg-black/35 border border-white/10 flex items-center justify-between gap-2"
                      >
                        <div className="min-w-0">
                          <div className="font-semibold truncate">{tx.note}</div>
                          <div className="text-[10px] font-mono opacity-60">
                            @{tx.sender_username} → @{tx.receiver_username}
                          </div>
                        </div>
                        <span className="font-mono font-bold text-amber-300 shrink-0">
                          {tx.amount_uzs.toLocaleString()} UZS
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================
            TAB 6: ADMIN CMS (Instagram UTM Voronka, Auto-Parser Kino Qo'shish, OP)
           ================================================================== */}
        {activeTab === 'admin' && adminData && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <div className="text-xs opacity-60 font-mono">JAMI FOYDALANUVCHILAR</div>
                <div className="text-2xl font-black text-cyan-400 mt-1">
                  {adminData.metrics.total_users.toLocaleString()}
                </div>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <div className="text-xs opacity-60 font-mono">FAOL VIP OBUNACHILAR</div>
                <div className="text-2xl font-black text-amber-400 mt-1">
                  {adminData.metrics.vip_users.toLocaleString()}
                </div>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <div className="text-xs opacity-60 font-mono">OYLIK DAROMAD (UZS + STARS)</div>
                <div className="text-xl font-black text-emerald-400 mt-1">
                  {adminData.metrics.monthly_revenue_uzs.toLocaleString()} so&apos;m
                </div>
              </div>
              <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
                <div className="text-xs opacity-60 font-mono">ZERO-DOWNTIME HOLATI</div>
                <div className="text-xs font-mono font-bold text-emerald-300 mt-2">
                  ✦ {adminData.metrics.uptime}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* 1-Click Admin Movie Uploader */}
              <form
                onSubmit={handleCreateAdminMovie}
                className="p-5 rounded-3xl bg-white/5 border border-white/10 space-y-3"
              >
                <h3 className="font-extrabold text-base flex items-center gap-2">
                  <PlusCircle className="w-5 h-5 text-cyan-400" />
                  Admin CMS — Yangi Kino / Serial Qo'shish (Auto-Stream)
                </h3>
                <div className="grid grid-cols-2 gap-2.5 text-xs">
                  <input
                    type="number"
                    value={newMovieForm.code}
                    onChange={(e) => setNewMovieForm({ ...newMovieForm, code: e.target.value })}
                    placeholder="Kino kodi (masalan: 777)"
                    className="px-3 py-2 rounded-xl bg-black/50 border border-white/15"
                  />
                  <input
                    type="text"
                    value={newMovieForm.title}
                    onChange={(e) => setNewMovieForm({ ...newMovieForm, title: e.target.value })}
                    placeholder="Kino nomi (masalan: Dune 2)"
                    className="px-3 py-2 rounded-xl bg-black/50 border border-white/15"
                  />
                  <select
                    value={newMovieForm.category}
                    onChange={(e) => setNewMovieForm({ ...newMovieForm, category: e.target.value })}
                    className="px-3 py-2 rounded-xl bg-black/50 border border-white/15"
                  >
                    <option value="action">Jangari & Sarguzasht</option>
                    <option value="uzbek_classic">O'zbek Oltin Fondi</option>
                    <option value="uzbek_modern">Yangi O'zbek Kinosi</option>
                    <option value="turkish">Turk Seriallari</option>
                    <option value="kdrama">K-Drama (Koreys)</option>
                    <option value="scifi">Fantastika</option>
                    <option value="cartoon">Multfilmlar</option>
                  </select>
                  <select
                    value={newMovieForm.language_hub}
                    onChange={(e) =>
                      setNewMovieForm({ ...newMovieForm, language_hub: e.target.value })
                    }
                    className="px-3 py-2 rounded-xl bg-black/50 border border-white/15"
                  >
                    <option value="english">English Hub</option>
                    <option value="uzbek">O'zbek Hub</option>
                    <option value="turkish">Türkçe Hub</option>
                    <option value="korean">Korean Hub</option>
                    <option value="german">German Hub</option>
                  </select>
                </div>
                <textarea
                  rows={2}
                  value={newMovieForm.description}
                  onChange={(e) =>
                    setNewMovieForm({ ...newMovieForm, description: e.target.value })
                  }
                  placeholder="Film qisqacha tavsifi..."
                  className="w-full px-3 py-2 rounded-xl bg-black/50 border border-white/15 text-xs"
                />
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-xs opacity-80">
                    <input
                      type="checkbox"
                      checked={newMovieForm.include_1080p}
                      onChange={(e) =>
                        setNewMovieForm({ ...newMovieForm, include_1080p: e.target.checked })
                      }
                    />
                    1080p Full HD qo'shish (o'chirilsa 720p Fallback sinovi bo'ladi)
                  </label>
                  <button
                    type="submit"
                    className="px-5 py-2 rounded-xl bg-cyan-400 text-slate-950 font-extrabold text-xs"
                  >
                    ✦ Bazaga Joylash
                  </button>
                </div>
              </form>

              {/* Instagram Reels UTM Funnel Analytics (PRD 3.D.1) */}
              <div className="p-5 rounded-3xl bg-white/5 border border-white/10 space-y-3">
                <h3 className="font-extrabold text-base flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-pink-400" />
                  Instagram Reels & Deep-Linking UTM Voronkasi
                </h3>
                <div className="space-y-2 text-xs">
                  {adminData.campaigns.map((c) => (
                    <div
                      key={c.id}
                      className="p-3 rounded-2xl bg-black/40 border border-white/10 flex items-center justify-between"
                    >
                      <div>
                        <div className="font-mono font-bold text-cyan-300">
                          t.me/bot?start={c.utm_campaign}
                        </div>
                        <div className="text-[11px] opacity-65">
                          Manba: {c.source} • Kino: #{c.movie_code}
                        </div>
                      </div>
                      <div className="text-right font-mono">
                        <div className="text-emerald-300 font-bold">
                          {c.conversions_count} start ({c.conversion_rate}%)
                        </div>
                        <div className="text-[11px] text-amber-300">
                          VIP sotuv: {c.vip_sales_count} ta
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ====================================================================
          BOTTOM SCANDINAVIAN FLOATING NAVIGATION BAR
         ==================================================================== */}
      <nav
        className={`fixed bottom-3 inset-x-3 max-w-xl mx-auto z-40 rounded-2xl backdrop-blur-2xl border px-2 py-1.5 flex items-center justify-around shadow-2xl ${
          effectiveDark
            ? 'bg-[#0C101A]/90 border-white/15'
            : 'bg-white/95 border-slate-300'
        }`}
      >
        {[
          { id: 'catalog', label: 'Katalog', icon: Film },
          { id: 'reels', label: 'Reels', icon: Clapperboard },
          { id: 'social', label: 'AI & Party', icon: Sparkles },
          { id: 'economy', label: 'Hamyon & Donat', icon: Wallet },
          { id: 'profile', label: 'CineProfile', icon: Trophy },
          { id: 'admin', label: 'Admin', icon: BarChart3 },
        ].map((tab) => {
          const Icon = tab.icon
          const active = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl text-[11px] font-semibold transition ${
                active
                  ? 'bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'opacity-65 hover:opacity-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </nav>

      {/* ====================================================================
          MULTI-QUALITY & EDU-CINEMA PLAYER MODAL
         ==================================================================== */}
      {activeMovieCode && (
        <CinemaPlayerModal
          movieCode={activeMovieCode}
          onClose={() => setActiveMovieCode(null)}
          onStartWatchParty={handleStartWatchParty}
          onWordSaved={loadProfileAndVocab}
          onOpenProfile={handleOpenCineProfile}
          isDark={effectiveDark}
        />
      )}

      {/* ====================================================================
          PUBLIC CINEPROFILE & 1-CLICK GIFT MODAL (Opens when any @username is clicked!)
         ==================================================================== */}
      {inspectedProfile && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/85 backdrop-blur-xl p-4">
          <div className="w-full max-w-lg rounded-3xl bg-[#0B0F19] border border-cyan-400/40 p-5 sm:p-6 text-slate-100 space-y-4 shadow-2xl">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3.5">
                <img
                  src={
                    inspectedProfile.avatar_url ||
                    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80'
                  }
                  alt={inspectedProfile.full_name}
                  className="w-16 h-16 rounded-2xl object-cover border-2 border-amber-400"
                />
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-extrabold text-lg">{inspectedProfile.full_name}</h3>
                    <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono text-xs font-bold">
                      @{inspectedProfile.cine_username}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-0.5">{inspectedProfile.bio}</p>
                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {(inspectedProfile.badges || []).map((b, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold"
                      >
                        {b}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setInspectedProfile(null)}
                className="p-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center bg-black/50 border border-white/10 rounded-2xl p-3">
              <div>
                <div className="font-black text-base text-cyan-300">
                  {inspectedProfile.followers_count}
                </div>
                <div className="text-[10px] uppercase font-mono opacity-60">Obunachilar</div>
              </div>
              <div>
                <div className="font-black text-base text-purple-300">
                  {inspectedProfile.following_count}
                </div>
                <div className="text-[10px] uppercase font-mono opacity-60">Obunalar</div>
              </div>
              <div>
                <div className="font-black text-base text-amber-300">
                  {(inspectedProfile.total_donated_uzs || 0).toLocaleString()} UZS
                </div>
                <div className="text-[10px] uppercase font-mono opacity-60">Homiylik Hissasi</div>
              </div>
            </div>

            {/* Follow & 1-Click Gift Actions */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleToggleFollow(inspectedProfile.cine_username)}
                className={`flex-1 py-2.5 rounded-xl font-extrabold text-xs flex items-center justify-center gap-1.5 transition ${
                  inspectedProfile.is_following
                    ? 'bg-white/15 text-slate-200 border border-white/20'
                    : 'bg-cyan-400 text-slate-950'
                }`}
              >
                {inspectedProfile.is_following ? (
                  <>
                    <UserCheck className="w-4 h-4" /> Obuna bo&apos;lingan
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" /> + Obuna bo&apos;lish
                  </>
                )}
              </button>
              <button
                onClick={() => {
                  setGiftForm((f) => ({
                    ...f,
                    recipient_username: inspectedProfile.cine_username,
                  }))
                  setInspectedProfile(null)
                  setActiveMovieCode(null)
                  setActiveTab('economy')
                }}
                className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-pink-500 to-amber-500 text-slate-950 font-extrabold text-xs flex items-center justify-center gap-1.5"
              >
                <Gift className="w-4 h-4" /> 🎁 VIP / Balans Hadya Qilish
              </button>
            </div>

            {/* User's Public Custom Lists */}
            {inspectedProfile.custom_lists?.length > 0 && (
              <div className="space-y-1.5">
                <div className="text-xs font-bold text-slate-300">
                  🎬 @{inspectedProfile.cine_username} shaxsiy kino-kolleksiyalari:
                </div>
                {inspectedProfile.custom_lists.map((cl) => (
                  <div
                    key={cl.id}
                    className="p-2.5 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between text-xs"
                  >
                    <span>{cl.title}</span>
                    <div className="flex gap-1">
                      {(cl.movie_codes || []).map((mc) => (
                        <button
                          key={mc}
                          onClick={() => {
                            setInspectedProfile(null)
                            setActiveMovieCode(mc)
                          }}
                          className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono text-[11px]"
                        >
                          #{mc} ▶
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
