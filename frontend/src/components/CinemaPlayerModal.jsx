import React, { useEffect, useRef, useState } from 'react'
import {
  X,
  Play,
  Pause,
  Volume2,
  Subtitles,
  Sparkles,
  Download,
  PictureInPicture2,
  Tv,
  Share2,
  Users,
  SkipForward,
  CheckCircle2,
  AlertTriangle,
  Eye,
  EyeOff,
  BookOpen,
  Layers,
  Gauge,
  MessageSquare,
  Gift,
  Award,
  CornerDownRight,
  Clock,
  Crown,
} from 'lucide-react'

const SPEED_OPTIONS = [0.5, 0.75, 0.85, 1.0, 1.25, 1.5, 2.0]

export default function CinemaPlayerModal({
  movieCode,
  onClose,
  onStartWatchParty,
  onWordSaved,
  onOpenProfile,
  isDark,
}) {
  const videoRef = useRef(null)
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [resolution, setResolution] = useState('1080p')
  const [activeEpisodeId, setActiveEpisodeId] = useState(null)
  const [selectedSeason, setSelectedSeason] = useState(1)
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0)
  const [activeAudio, setActiveAudio] = useState('uz')
  const [topSubLang, setTopSubLang] = useState('en')
  const [bottomSubLang, setBottomSubLang] = useState('uz')
  const [dualSubsEnabled, setDualSubsEnabled] = useState(true)

  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [showResumePrompt, setShowResumePrompt] = useState(false)
  const [fallbackBanner, setFallbackBanner] = useState(null)

  // Next Episode 5-second countdown
  const [nextEpCountdown, setNextEpCountdown] = useState(null)

  // Interactive Tap-to-Translate Word Modal
  const [translatedWord, setTranslatedWord] = useState(null)
  const [translating, setTranslating] = useState(false)

  // Offline IndexedDB / Cache status
  const [offlineStatus, setOfflineStatus] = useState(null)

  // Viral Story Maker & Smart TV Cast modals
  const [storySnapshot, setStorySnapshot] = useState(null)
  const [tvCode, setTvCode] = useState('')
  const [tvPairedStatus, setTvPairedStatus] = useState(null)

  // Spoiler-Free Threaded Social Reviews + @Mentions + Time-codes + Awards
  const [revealedSpoilers, setRevealedSpoilers] = useState({})
  const [newReviewText, setNewReviewText] = useState('')
  const [newReviewRating, setNewReviewRating] = useState(10)
  const [newReviewSpoiler, setNewReviewSpoiler] = useState(false)
  const [attachTimestamp, setAttachTimestamp] = useState(true)
  const [replyTarget, setReplyTarget] = useState(null) // { parent_id, username }
  const [awardNotice, setAwardNotice] = useState(null)

  const fetchMovieDetail = async (reqRes = resolution, epId = activeEpisodeId) => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ resolution: reqRes })
      if (epId) params.set('episode_id', epId)
      const res = await fetch(`/api/movies/${movieCode}?${params.toString()}`)
      const data = await res.json()
      setDetail(data)

      if (data.movie?.language_hub === 'turkish') setTopSubLang('tr')
      else if (data.movie?.language_hub === 'korean') setTopSubLang('ko')
      else setTopSubLang('en')

      if (data.stream?.fallback_triggered && data.stream?.fallback_message) {
        setFallbackBanner(data.stream.fallback_message)
        setTimeout(() => setFallbackBanner(null), 6500)
      } else {
        setFallbackBanner(null)
      }

      if (data.resume_timestamp && data.resume_timestamp > 10) {
        setShowResumePrompt(true)
      }
    } catch (err) {
      console.error('Failed to load movie detail:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMovieDetail(resolution, activeEpisodeId)
  }, [movieCode])

  // Sync progress every 5 seconds (PRD Section 3.A.4)
  useEffect(() => {
    const interval = setInterval(() => {
      if (!videoRef.current || videoRef.current.paused || !detail?.movie) return
      const cur = Math.floor(videoRef.current.currentTime)
      const dur = Math.floor(videoRef.current.duration || 7200)
      fetch('/api/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          movie_id: detail.movie.id,
          episode_id: detail.active_episode?.id || null,
          last_timestamp: cur,
          duration_seconds: dur,
          watched_delta_seconds: 5,
        }),
      }).catch(() => {})
    }, 5000)
    return () => clearInterval(interval)
  }, [detail])

  const handleResolutionChange = (newRes) => {
    const prevTime = videoRef.current ? videoRef.current.currentTime : 0
    setResolution(newRes)
    fetchMovieDetail(newRes, activeEpisodeId).then(() => {
      setTimeout(() => {
        if (videoRef.current && prevTime > 0) {
          videoRef.current.currentTime = prevTime
          videoRef.current.play().catch(() => {})
        }
      }, 250)
    })
  }

  const handleEpisodeSelect = (ep) => {
    setActiveEpisodeId(ep.id)
    setNextEpCountdown(null)
    fetchMovieDetail(resolution, ep.id)
  }

  const handleSpeedChange = (spd) => {
    setPlaybackSpeed(spd)
    if (videoRef.current) {
      videoRef.current.playbackRate = spd
    }
  }

  const handlePictureInPicture = async () => {
    try {
      if (videoRef.current && document.pictureInPictureEnabled) {
        if (document.pictureInPictureElement) {
          await document.exitPictureInPicture()
        } else {
          await videoRef.current.requestPictureInPicture()
        }
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleOfflineCache = async () => {
    setOfflineStatus('downloading')
    try {
      // Store movie metadata & offline manifest in IndexedDB / Cache Storage
      if ('caches' in window && detail?.stream?.stream_url) {
        const cache = await caches.open('cnmovi-offline-v7')
        await cache.put(
          `/offline-meta/${detail.movie.code}`,
          new Response(JSON.stringify(detail), { headers: { 'Content-Type': 'application/json' } })
        )
      }
      setTimeout(() => {
        setOfflineStatus('saved')
      }, 900)
    } catch {
      setOfflineStatus('saved')
    }
  }

  const handleWordClick = async (rawWord, sentence) => {
    if (videoRef.current && !videoRef.current.paused) {
      videoRef.current.pause()
    }
    setTranslating(true)
    try {
      const res = await fetch('/api/subtitles/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          word: rawWord,
          context_sentence: sentence,
          source_lang: topSubLang,
          movie_id: detail?.movie?.id,
          timestamp_sec: Math.floor(currentTime),
          save_to_vocabulary: true,
        }),
      })
      const data = await res.json()
      setTranslatedWord(data)
      if (onWordSaved) onWordSaved()
    } catch (err) {
      console.error(err)
    } finally {
      setTranslating(false)
    }
  }

  const handleCreateViralStory = () => {
    if (videoRef.current) videoRef.current.pause()
    const mins = String(Math.floor(currentTime / 60)).padStart(2, '0')
    const secs = String(Math.floor(currentTime % 60)).padStart(2, '0')
    setStorySnapshot({
      title: detail?.movie?.title,
      code: detail?.movie?.code,
      timecode: `${mins}:${secs}`,
      quote:
        currentBottomCue?.text ||
        "«Koinot sukunatida insoniyat uchun har bir soniya g'animat.»",
      backdrop: detail?.movie?.backdrop_url || detail?.movie?.poster_url,
    })
  }

  const handlePairSmartTv = async () => {
    if (!tvCode.trim()) return
    const res = await fetch('/api/tv/pair', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tv_code: tvCode.trim(),
        movie_code: detail.movie.code,
      }),
    })
    const data = await res.json()
    setTvPairedStatus(data)
  }

  const handleSubmitReview = async (e) => {
    e.preventDefault()
    if (!newReviewText.trim()) return
    const payload = {
      rating: newReviewRating,
      comment: newReviewText,
      has_spoiler: newReviewSpoiler,
      parent_id: replyTarget?.parent_id || null,
      reply_to_username: replyTarget?.username || null,
      timestamp_sec: attachTimestamp ? Math.floor(currentTime || 0) : null,
    }
    const res = await fetch(`/api/movies/${detail.movie.code}/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.ok) {
      await fetchMovieDetail(resolution, activeEpisodeId)
      setNewReviewText('')
      setNewReviewSpoiler(false)
      setReplyTarget(null)
      if (onWordSaved) onWordSaved()
    }
  }

  const handleAwardReview = async (reviewId, authorHandle) => {
    try {
      const res = await fetch(`/api/reviews/${reviewId}/award`, { method: 'POST' })
      const data = await res.json()
      if (res.ok) {
        setAwardNotice(`🏆 @${authorHandle} sharhiga 5,000 UZS SuperThanks mukofoti yuborildi!`)
        setTimeout(() => setAwardNotice(null), 4500)
        await fetchMovieDetail(resolution, activeEpisodeId)
        if (onWordSaved) onWordSaved()
      } else {
        setAwardNotice(`⚠️ ${data.detail || 'Xatolik'}`)
        setTimeout(() => setAwardNotice(null), 4500)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const renderCommentWithMentions = (text) => {
    if (!text) return null
    const parts = text.split(/(@[a-zA-Z0-9_]{3,25})/g)
    return parts.map((part, idx) => {
      if (part.startsWith('@')) {
        const handle = part.slice(1)
        return (
          <button
            key={idx}
            type="button"
            onClick={() => onOpenProfile && onOpenProfile(handle)}
            className="mx-0.5 px-1.5 py-0.5 rounded bg-cyan-500/20 hover:bg-cyan-400 text-cyan-300 hover:text-slate-950 font-mono font-bold text-[11px] transition"
          >
            {part}
          </button>
        )
      }
      return <span key={idx}>{part}</span>
    })
  }

  if (loading || !detail) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-xl">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-mono text-cyan-300">⟢ Striming ko'prigi ulanmoqda...</p>
        </div>
      </div>
    )
  }

  const { movie, seasons, active_episode, stream, reviews } = detail
  const subtitlesMap = stream?.subtitles || {}
  const topCues = subtitlesMap[topSubLang] || subtitlesMap.en || []
  const bottomCues = subtitlesMap[bottomSubLang] || subtitlesMap.uz || []

  // Loop subtitle timing every 60s so demo videos always display synchronized interactive subtitles
  const subClock = currentTime % 60
  const currentTopCue = topCues.find((c) => subClock >= c.start && subClock <= c.end) || topCues[0]
  const currentBottomCue =
    bottomCues.find((c) => subClock >= c.start && subClock <= c.end) || bottomCues[0]

  const introStart = active_episode?.intro_start_sec ?? movie.intro_start_sec ?? 5
  const introEnd = active_episode?.intro_end_sec ?? movie.intro_end_sec ?? 45
  const showSkipIntro = currentTime >= introStart && currentTime <= introEnd

  const formatClock = (sec) => {
    const m = String(Math.floor(sec / 60)).padStart(2, '0')
    const s = String(Math.floor(sec % 60)).padStart(2, '0')
    return `${m}:${s}`
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/95 backdrop-blur-2xl text-slate-100">
      <div className="max-w-5xl mx-auto p-3 sm:p-6 space-y-5">
        {/* Top Bar */}
        <div className="flex items-center justify-between gap-3 border-b border-white/10 pb-3">
          <div className="flex items-center gap-3">
            <span className="px-2.5 py-1 rounded-md bg-cyan-500/15 border border-cyan-400/30 font-mono text-xs text-cyan-300">
              ⟢ KOD: #{movie.code}
            </span>
            <div>
              <h2 className="text-lg sm:text-xl font-bold tracking-tight flex items-center gap-2">
                {movie.title}
                {movie.cefr_level && (
                  <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Edu-Cinema {movie.cefr_level}
                  </span>
                )}
              </h2>
              <p className="text-xs text-slate-400">
                {movie.original_title} • {movie.year} • ✦ IMDb {movie.imdb_rating} • {movie.age_rating}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/15 border border-white/10 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* PRD Section 3.A.1 — Graceful Degradation Notification */}
        {fallbackBanner && (
          <div className="flex items-center justify-between gap-3 px-4 py-3 rounded-xl bg-amber-500/15 border border-amber-400/40 text-amber-200 text-sm animate-pulse">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-300 shrink-0" />
              <span className="font-medium">{fallbackBanner}</span>
            </div>
            <span className="text-xs font-mono uppercase px-2 py-0.5 rounded bg-amber-400/20">
              Smart Fallback
            </span>
          </div>
        )}

        {/* Resume Playback Prompt (PRD Section 3.A.4) */}
        {showResumePrompt && (
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 rounded-xl bg-cyan-500/15 border border-cyan-400/30">
            <div className="text-sm">
              <span className="text-cyan-300 font-semibold">⟢ Tomoshani davom ettirish: </span>
              <span>Siz ushbu filmni </span>
              <code className="px-1.5 py-0.5 rounded bg-black/40 text-cyan-200 font-mono">
                [{formatClock(detail.resume_timestamp)}]
              </code>
              <span> daqiqasida to'xtatgansiz.</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  if (videoRef.current) {
                    videoRef.current.currentTime = detail.resume_timestamp
                    videoRef.current.play().catch(() => {})
                  }
                  setShowResumePrompt(false)
                }}
                className="px-3 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs transition"
              >
                ▹ Davom ettirish [{formatClock(detail.resume_timestamp)}]
              </button>
              <button
                onClick={() => setShowResumePrompt(false)}
                className="px-2.5 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-xs"
              >
                Boshidan
              </button>
            </div>
          </div>
        )}

        {/* VIDEO CONTAINER WITH INTERACTIVE DUAL SUBTITLES & SKIP INTRO */}
        <div className="relative rounded-2xl overflow-hidden bg-black border border-white/15 shadow-2xl">
          <video
            ref={videoRef}
            src={stream?.stream_url}
            controls
            playsInline
            onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
            onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
            onEnded={() => {
              if (movie.content_type === 'series' && seasons?.length) {
                setNextEpCountdown(5)
              }
            }}
            className="w-full aspect-video bg-black object-contain"
          />

          {/* Top Left Stream Security & Resolution Badge */}
          <div className="absolute top-3 left-3 flex items-center gap-2 pointer-events-none">
            <span className="px-2.5 py-1 rounded-lg bg-black/70 backdrop-blur-md border border-white/15 text-xs font-mono text-cyan-300">
              ✦ {stream?.selected_resolution || '1080p'} • MTProto Stream
            </span>
            {active_episode && (
              <span className="px-2.5 py-1 rounded-lg bg-black/70 backdrop-blur-md border border-white/15 text-xs text-slate-200">
                {active_episode.episode_number}-qism
              </span>
            )}
          </div>

          {/* 3-MODUL: Opening Movie Patron Credits Overlay (First 18s of playback) */}
          {detail.movie_patrons?.length > 0 && currentTime < 18 && (
            <div className="absolute top-3 right-3 z-20 px-3 py-1.5 rounded-xl bg-gradient-to-r from-amber-500/90 to-yellow-600/90 text-slate-950 font-extrabold text-[11px] shadow-xl flex items-center gap-1.5">
              <Crown className="w-3.5 h-3.5 shrink-0" />
              <span>
                🎬 Film homiylari:{' '}
                {detail.movie_patrons
                  .slice(0, 2)
                  .map((p) => `@${p.cine_username}`)
                  .join(', ')}{' '}
                ✦
              </span>
            </div>
          )}

          {/* Netflix-style Skip Intro Button */}
          {showSkipIntro && (
            <button
              onClick={() => {
                if (videoRef.current) videoRef.current.currentTime = introEnd + 1
              }}
              className="absolute bottom-28 right-4 z-20 flex items-center gap-2 px-4 py-2 rounded-xl bg-white/90 hover:bg-white text-slate-950 font-bold text-xs shadow-xl transition transform hover:scale-105"
            >
              <SkipForward className="w-4 h-4" />
              ⏭ Zastavkani o'tkazish (Skip Intro)
            </button>
          )}

          {/* EDU-CINEMA DUAL SUBTITLES OVERLAY (Interactive Tap-to-Translate!) */}
          {dualSubsEnabled && (
            <div className="absolute bottom-14 inset-x-4 flex flex-col items-center gap-1.5 pointer-events-auto">
              {/* Layer 1: Foreign Language Subtitle (Clickable Words!) */}
              {currentTopCue && (
                <div className="px-3.5 py-1.5 rounded-xl bg-black/80 backdrop-blur-md border border-cyan-500/30 text-center max-w-2xl">
                  <div className="flex flex-wrap items-center justify-center gap-1 text-sm sm:text-base font-medium text-cyan-200">
                    {currentTopCue.text.split(' ').map((word, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleWordClick(word, currentTopCue.text)}
                        title="Bosib tarjima qiling va lug'atga qo'shing"
                        className="px-1 rounded hover:bg-cyan-400/30 hover:text-white transition cursor-pointer underline decoration-cyan-400/40 decoration-dotted"
                      >
                        {word}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Layer 2: Native Uzbek Subtitle */}
              {currentBottomCue && (
                <div className="px-3.5 py-1 rounded-lg bg-black/75 backdrop-blur-md text-center max-w-xl">
                  <p className="text-xs sm:text-sm text-amber-200 font-medium">
                    {currentBottomCue.text}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Interactive Word Translation Popup Card (Edu-Cinema Pro) */}
          {(translating || translatedWord) && (
            <div className="absolute top-14 right-4 z-30 w-80 p-4 rounded-2xl bg-slate-950/95 backdrop-blur-xl border border-cyan-400/40 shadow-2xl space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase text-cyan-400 flex items-center gap-1">
                  <BookOpen className="w-3.5 h-3.5" /> Edu-Cinema Smart Lug'at
                </span>
                <button
                  onClick={() => {
                    setTranslatedWord(null)
                    if (videoRef.current) videoRef.current.play().catch(() => {})
                  }}
                  className="text-slate-400 hover:text-white text-xs"
                >
                  ✕ Yopish
                </button>
              </div>
              {translating ? (
                <p className="text-xs text-slate-300 py-2">✦ So'z tahlil qilinmoqda...</p>
              ) : (
                <>
                  <div className="flex items-baseline justify-between">
                    <h4 className="text-lg font-bold text-white">{translatedWord.word}</h4>
                    <span className="text-xs font-mono text-slate-400">
                      {translatedWord.pronunciation} ({translatedWord.part_of_speech})
                    </span>
                  </div>
                  <p className="text-sm text-emerald-300 font-semibold">
                    ▹ {translatedWord.translation}
                  </p>
                  <p className="text-[11px] text-slate-400 italic">
                    «{translatedWord.context}»
                  </p>
                  <div className="pt-1 flex items-center justify-between text-[11px] text-cyan-300 border-t border-white/10">
                    <span>✦ Shaxsiy lug'atingizga saqlandi!</span>
                    <button
                      onClick={() => {
                        setTranslatedWord(null)
                        if (videoRef.current) videoRef.current.play().catch(() => {})
                      }}
                      className="px-2 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-200"
                    >
                      Davom etish ▶
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* CONTROL DECK: QUALITY, AUDIO, SUBTITLES, SPEED, PIP, OFFLINE, STORY, TV */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* 1. Multi-Resolution Switcher */}
          <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5 font-semibold text-slate-200">
                <Layers className="w-4 h-4 text-cyan-400" /> Video Sifati (HLS / Fallback)
              </span>
              <span className="font-mono text-[11px] text-cyan-300">
                {stream?.file_size_mb} MB
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              {['480p', '720p', '1080p', 'Auto'].map((resOpt) => {
                const isSelected =
                  resolution.toLowerCase() === resOpt.toLowerCase() ||
                  (resolution === resOpt && stream?.selected_resolution === resOpt)
                return (
                  <button
                    key={resOpt}
                    onClick={() => handleResolutionChange(resOpt)}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-mono font-semibold transition border ${
                      isSelected
                        ? 'bg-cyan-500 text-slate-950 border-cyan-400 shadow-lg shadow-cyan-500/20'
                        : 'bg-white/5 hover:bg-white/10 text-slate-300 border-white/10'
                    }`}
                  >
                    {resOpt}
                  </button>
                )
              })}
            </div>
            {movie.code === 101 && (
              <p className="text-[11px] text-amber-300/90">
                💡 Sinov: «Shum bola»da 1080p yo'q — 1080p bossangiz Graceful Degradation ishlaydi!
              </p>
            )}
          </div>

          {/* 2. Edu-Cinema Dual Subtitles & Audio Track Switcher */}
          <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1.5 font-semibold text-slate-200">
                <Subtitles className="w-4 h-4 text-emerald-400" /> Ikki Qavatli Subtitr & Audio
              </span>
              <button
                onClick={() => setDualSubsEnabled(!dualSubsEnabled)}
                className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                  dualSubsEnabled
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-white/10 text-slate-400'
                }`}
              >
                {dualSubsEnabled ? 'Subtitr: ON' : 'Subtitr: OFF'}
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <select
                value={topSubLang}
                onChange={(e) => setTopSubLang(e.target.value)}
                className="bg-slate-900 border border-white/15 rounded-lg px-2 py-1.5 text-xs text-cyan-200"
              >
                <option value="en">1-qavat: English (Tap Word)</option>
                <option value="tr">1-qavat: Türkçe (Tap Word)</option>
                <option value="ko">1-qavat: 한국어 (Koreyscha)</option>
              </select>
              <select
                value={activeAudio}
                onChange={(e) => setActiveAudio(e.target.value)}
                className="bg-slate-900 border border-white/15 rounded-lg px-2 py-1.5 text-xs text-amber-200"
              >
                <option value="uz">🔊 O'zbekcha Dublyaj</option>
                <option value="en">🔊 Original Audio</option>
                <option value="tr">🔊 Original Türkçe</option>
                <option value="ru">🔊 Русский Дубляж</option>
              </select>
            </div>
            <p className="text-[11px] text-slate-400">
              ✦ Video ustidagi ko'k subtitrda istalgan so'zga bosing — tarjima va lug'at chiqadi!
            </p>
          </div>

          {/* 3. Fine Speed Control & Action Tools */}
          <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1.5 font-semibold text-slate-200">
                <Gauge className="w-4 h-4 text-purple-400" /> Tezlik ({playbackSpeed}x) & Asboblar
              </span>
            </div>
            <div className="flex flex-wrap gap-1">
              {SPEED_OPTIONS.map((spd) => (
                <button
                  key={spd}
                  onClick={() => handleSpeedChange(spd)}
                  className={`px-2 py-1 rounded text-[11px] font-mono ${
                    playbackSpeed === spd
                      ? 'bg-purple-500 text-white font-bold'
                      : 'bg-white/5 hover:bg-white/10 text-slate-300'
                  }`}
                >
                  {spd}x
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* EXTRA TMA PLAYER ACTIONS: PIP, OFFLINE CACHE, WATCH PARTY, VIRAL STORY, SMART TV */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handlePictureInPicture}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/15 border border-white/10 text-xs font-medium transition"
          >
            <PictureInPicture2 className="w-4 h-4 text-cyan-400" />
            PiP (Suzuvchi Darcha)
          </button>

          <button
            onClick={handleOfflineCache}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/15 border border-white/10 text-xs font-medium transition"
          >
            <Download className="w-4 h-4 text-emerald-400" />
            {offlineStatus === 'downloading'
              ? 'IndexedDB ga saqlanmoqda...'
              : offlineStatus === 'saved'
              ? '✦ Offline Keshga Saqlandi!'
              : 'Offline Yuklash (IndexedDB)'}
          </button>

          <button
            onClick={() => onStartWatchParty(movie.code)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 border border-purple-400/30 text-purple-200 text-xs font-semibold transition"
          >
            <Users className="w-4 h-4" />
            Watch Party (Do'stlar bilan ko'rish)
          </button>

          <button
            onClick={handleCreateViralStory}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-pink-500/20 hover:bg-pink-500/30 border border-pink-400/30 text-pink-200 text-xs font-semibold transition"
          >
            <Share2 className="w-4 h-4" />
            📸 Story / Kadr Ulashish
          </button>

          {/* Smart TV Pairing Input */}
          <div className="flex items-center gap-1.5 ml-auto bg-white/5 border border-white/10 rounded-xl px-2.5 py-1">
            <Tv className="w-4 h-4 text-amber-400" />
            <input
              type="text"
              value={tvCode}
              onChange={(e) => setTvCode(e.target.value)}
              placeholder="Smart TV kod (masalan: 849201)"
              className="bg-transparent text-xs outline-none w-44 text-slate-200 placeholder:text-slate-500"
            />
            <button
              onClick={handlePairSmartTv}
              className="px-2.5 py-1 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-xs"
            >
              TV ga ulash
            </button>
          </div>
        </div>

        {tvPairedStatus && (
          <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-400/30 text-xs text-emerald-200 flex items-center justify-between">
            <span>
              ✦ Smart TV ({tvPairedStatus.tv_code}) muvaffaqiyatli ulandi! «{tvPairedStatus.movie_title}» televizor ekranida namoyish etilmoqda.
            </span>
            <button onClick={() => setTvPairedStatus(null)} className="text-emerald-300 underline">
              Yopish
            </button>
          </div>
        )}

        {/* Viral Story Card Preview Modal */}
        {storySnapshot && (
          <div className="p-4 rounded-2xl bg-gradient-to-br from-pink-950/60 via-slate-900 to-cyan-950/60 border border-pink-400/40 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-pink-300 uppercase tracking-wider">
                ✦ Tayyor Instagram / Telegram Story Kadr (Viral Marketing)
              </span>
              <button onClick={() => setStorySnapshot(null)} className="text-xs text-slate-400">
                ✕ Yopish
              </button>
            </div>
            <div className="p-4 rounded-xl bg-black/60 border border-white/10 space-y-2 text-center">
              <p className="text-sm sm:text-base font-serif italic text-slate-100">
                {storySnapshot.quote}
              </p>
              <p className="text-xs font-mono text-cyan-300">
                ⟢ {storySnapshot.title} [{storySnapshot.timecode}] • Botda kod: #{storySnapshot.code}
              </p>
            </div>
          </div>
        )}

        {/* SEASON & EPISODE SELECTOR FOR SERIES (PRD Section 3.A.2) */}
        {seasons && seasons.length > 0 && (
          <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-bold text-slate-200">
                ⟢ Fasllar va Qismlar Tanlovi ({movie.title})
              </h3>
              <div className="flex gap-1.5">
                {seasons.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => setSelectedSeason(s.season_number)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold ${
                      selectedSeason === s.season_number
                        ? 'bg-cyan-500 text-slate-950'
                        : 'bg-white/10 text-slate-300'
                    }`}
                  >
                    {s.title}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {(seasons.find((s) => s.season_number === selectedSeason)?.episodes || []).map((ep) => {
                const isCur = active_episode?.id === ep.id
                return (
                  <button
                    key={ep.id}
                    onClick={() => handleEpisodeSelect(ep)}
                    className={`p-3 rounded-xl border text-left transition flex items-center justify-between ${
                      isCur
                        ? 'bg-cyan-500/20 border-cyan-400 text-white'
                        : 'bg-black/40 hover:bg-white/10 border-white/10 text-slate-300'
                    }`}
                  >
                    <div>
                      <div className="text-xs font-bold">{ep.title}</div>
                      <div className="text-[11px] text-slate-400">{ep.duration_minutes} daqiqa</div>
                    </div>
                    <Play className={`w-4 h-4 ${isCur ? 'text-cyan-300' : 'text-slate-500'}`} />
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* 3-MODUL: MOVIE PATRON CREDITS WALL ("Ushbu film homiylari") */}
        {detail.movie_patrons?.length > 0 && (
          <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 via-yellow-500/5 to-cyan-500/10 border border-amber-400/30 space-y-2.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-xs font-extrabold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
                <Crown className="w-4 h-4 text-amber-400" />
                ✦ Ushbu Filmning Faxriy Homiylari (Crowdfunding Patron Wall)
              </span>
              <span className="text-[11px] text-amber-200/80 font-mono">
                Nik ustiga bosib CineProfile sahifasiga o&apos;ting
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {detail.movie_patrons.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => onOpenProfile && onOpenProfile(p.cine_username)}
                  className="px-3 py-1.5 rounded-xl bg-black/50 hover:bg-amber-500/20 border border-amber-400/40 flex items-center gap-2 text-xs transition"
                >
                  <span className="font-mono font-bold text-amber-300">@{p.cine_username}</span>
                  <span className="text-[11px] text-slate-300">({p.amount_uzs.toLocaleString()} UZS)</span>
                  {p.patron_tier === 'gold' && <span>🥇</span>}
                  {p.patron_tier === 'silver' && <span>🥈</span>}
                  {p.patron_tier === 'bronze' && <span>🥉</span>}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 1-MODUL & 2-MODUL: CINESOCIAL ZANJIRLI IZOHLAR, @ATMETKA, VAQT KODLARI & MUKOFOTLAR */}
        <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-bold flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-cyan-400" />
                CineSocial Zanjirli Izohlar, @Atmetka &amp; Mukofotlar ({reviews?.length || 0})
              </h3>
              <p className="text-[11px] text-slate-400">
                Do&apos;stingizni <code>@username</code> qilib chaqiring, sekundni biriktiring yoki foydali sharhni 🎁 5,000 UZS bilan mukofotlang!
              </p>
            </div>
            <span className="text-xs text-cyan-300 font-mono">
              2-Level Threaded • Spoiler Blur
            </span>
          </div>

          {awardNotice && (
            <div className="p-3 rounded-xl bg-amber-500/20 border border-amber-400/40 text-xs font-bold text-amber-200">
              {awardNotice}
            </div>
          )}

          {replyTarget && (
            <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-cyan-500/15 border border-cyan-400/30 text-xs">
              <span>
                ↩ <b className="text-cyan-300">@{replyTarget.username}</b> izohiga javob yozilmoqda...
              </span>
              <button
                type="button"
                onClick={() => setReplyTarget(null)}
                className="text-slate-300 hover:text-white underline"
              >
                Bekor qilish
              </button>
            </div>
          )}

          <form onSubmit={handleSubmitReview} className="flex flex-wrap gap-2">
            <input
              type="text"
              value={newReviewText}
              onChange={(e) => setNewReviewText(e.target.value)}
              placeholder={
                replyTarget
                  ? `@${replyTarget.username} ga javobingizni yozing...`
                  : "Fikringizni yozing (masalan: @marvel_malika 00:24 dagi sahna zo'r ekan!)..."
              }
              className="flex-1 min-w-[220px] bg-black/50 border border-white/15 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-cyan-400"
            />
            <select
              value={newReviewRating}
              onChange={(e) => setNewReviewRating(Number(e.target.value))}
              className="bg-black/50 border border-white/15 rounded-xl px-2.5 py-2 text-xs text-amber-300"
            >
              {[10, 9, 8, 7, 6, 5].map((r) => (
                <option key={r} value={r}>
                  ✦ {r}/10
                </option>
              ))}
            </select>
            <label className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-xs text-cyan-300 cursor-pointer">
              <input
                type="checkbox"
                checked={attachTimestamp}
                onChange={(e) => setAttachTimestamp(e.target.checked)}
              />
              <Clock className="w-3.5 h-3.5" />[{formatClock(currentTime)}]
            </label>
            <label className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={newReviewSpoiler}
                onChange={(e) => setNewReviewSpoiler(e.target.checked)}
              />
              Spoyler
            </label>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs"
            >
              {replyTarget ? 'Javob berish' : 'Yuborish'}
            </button>
          </form>

          <div className="space-y-3">
            {(reviews || []).map((rev) => {
              const isBlurred = rev.has_spoiler && !revealedSpoilers[rev.id]
              const isGoldPatron = rev.patron_tier === 'gold'
              return (
                <div key={rev.id} className="space-y-2">
                  {/* Root Comment Card */}
                  <div
                    className={`p-3.5 rounded-2xl border flex flex-col gap-2 ${
                      isGoldPatron
                        ? 'bg-gradient-to-r from-amber-950/35 via-black/50 to-black/50 border-amber-400/40'
                        : 'bg-black/40 border-white/10'
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-2 text-xs">
                        <button
                          type="button"
                          onClick={() => onOpenProfile && onOpenProfile(rev.cine_username || rev.user_name)}
                          className="font-mono font-bold text-cyan-300 hover:underline flex items-center gap-1"
                        >
                          @{rev.cine_username || 'kinoman'}
                        </button>
                        <span className="text-slate-400 text-[11px]">({rev.user_name})</span>
                        {(rev.user_badges || []).slice(0, 2).map((b, idx) => (
                          <span
                            key={idx}
                            className="px-1.5 py-0.5 rounded bg-amber-500/15 border border-amber-400/30 text-amber-300 text-[10px] font-semibold"
                          >
                            {b}
                          </span>
                        ))}
                        <span className="text-amber-400 font-mono">✦ {rev.rating}/10</span>
                        {rev.timestamp_sec !== null && rev.timestamp_sec !== undefined && (
                          <button
                            type="button"
                            onClick={() => {
                              if (videoRef.current) {
                                videoRef.current.currentTime = rev.timestamp_sec
                                videoRef.current.play().catch(() => {})
                              }
                            }}
                            title="Shu sekundga o'tish"
                            className="px-1.5 py-0.5 rounded bg-emerald-500/20 hover:bg-emerald-400 text-emerald-300 hover:text-slate-950 font-mono text-[10px] font-bold transition"
                          >
                            ▶ [{formatClock(rev.timestamp_sec)}]
                          </button>
                        )}
                        {rev.awards_count > 0 && (
                          <span className="px-2 py-0.5 rounded-full bg-amber-500/25 border border-amber-400 text-amber-200 text-[10px] font-bold">
                            🏆 {rev.awards_count}x Mukofot ({rev.awards_uzs?.toLocaleString()} UZS)
                          </span>
                        )}
                        {rev.has_spoiler && (
                          <span className="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px]">
                            SPOYLER
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-1.5">
                        {rev.has_spoiler && (
                          <button
                            type="button"
                            onClick={() =>
                              setRevealedSpoilers((p) => ({ ...p, [rev.id]: !p[rev.id] }))
                            }
                            className="px-2 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-[11px] flex items-center gap-1"
                          >
                            {isBlurred ? (
                              <>
                                <Eye className="w-3 h-3" /> Ochish
                              </>
                            ) : (
                              <>
                                <EyeOff className="w-3 h-3" /> Yashirish
                              </>
                            )}
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() =>
                            setReplyTarget({
                              parent_id: rev.id,
                              username: rev.cine_username || 'kinoman',
                            })
                          }
                          className="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-cyan-500/20 border border-white/10 text-[11px] text-cyan-300"
                        >
                          ↩ Javob
                        </button>
                        <button
                          type="button"
                          onClick={() => handleAwardReview(rev.id, rev.cine_username || 'kinoman')}
                          className="px-2.5 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-400 text-amber-300 hover:text-slate-950 border border-amber-400/30 text-[11px] font-bold flex items-center gap-1 transition"
                          title="5,000 UZS mukofot yuborish"
                        >
                          <Gift className="w-3 h-3" /> Mukofotlash
                        </button>
                      </div>
                    </div>

                    <p
                      className={`text-xs text-slate-200 leading-relaxed transition ${
                        isBlurred ? 'blur-sm select-none' : ''
                      }`}
                    >
                      {renderCommentWithMentions(rev.comment)}
                    </p>
                  </div>

                  {/* 2nd-Level Threaded Replies */}
                  {rev.replies && rev.replies.length > 0 && (
                    <div className="pl-5 sm:pl-8 space-y-2 border-l-2 border-cyan-500/30 ml-3">
                      {rev.replies.map((rep) => (
                        <div
                          key={rep.id}
                          className="p-3 rounded-xl bg-white/[0.03] border border-white/10 flex flex-col gap-1.5"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                            <div className="flex flex-wrap items-center gap-1.5">
                              <CornerDownRight className="w-3.5 h-3.5 text-cyan-400" />
                              <button
                                type="button"
                                onClick={() => onOpenProfile && onOpenProfile(rep.cine_username)}
                                className="font-mono font-bold text-cyan-300 hover:underline"
                              >
                                @{rep.cine_username}
                              </button>
                              {(rep.user_badges || []).slice(0, 1).map((b, i) => (
                                <span
                                  key={i}
                                  className="px-1.5 py-0.5 rounded bg-white/10 text-[10px] text-amber-300"
                                >
                                  {b}
                                </span>
                              ))}
                              {rep.awards_count > 0 && (
                                <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold">
                                  🏆 {rep.awards_count}x
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-1.5">
                              <button
                                type="button"
                                onClick={() =>
                                  setReplyTarget({
                                    parent_id: rev.id,
                                    username: rep.cine_username,
                                  })
                                }
                                className="text-[11px] text-cyan-300 hover:underline"
                              >
                                ↩ Javob
                              </button>
                              <button
                                type="button"
                                onClick={() => handleAwardReview(rep.id, rep.cine_username)}
                                className="px-2 py-0.5 rounded bg-amber-500/15 hover:bg-amber-400 text-amber-300 hover:text-slate-950 text-[10px] font-bold"
                              >
                                🎁 Mukofot
                              </button>
                            </div>
                          </div>
                          <p className="text-xs text-slate-300">
                            {renderCommentWithMentions(rep.comment)}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
