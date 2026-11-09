import random
import string
from typing import Any, Dict, List, Set
from fastapi import WebSocket


class RealtimeHubManager:
    """
    Manages WebSockets for:
      1. Watch Party (PRD 3.D.5): Synchronized video timestamp, play/pause state, live emoji reactions & chat.
      2. Movie Matcher (PRD 3.D.4): Tinder-style dual user swipe rooms with instant 'Match!' trigger.
      3. Smart TV Pairing (PRD v7.0 Exclusive): 6-digit TV code instant remote control.
    """

    def __init__(self) -> None:
        self.watch_rooms: Dict[str, Dict[str, Any]] = {}
        self.watch_connections: Dict[str, Set[WebSocket]] = {}

        self.matcher_rooms: Dict[str, Dict[str, Any]] = {}
        self.tv_sessions: Dict[str, Dict[str, Any]] = {}

    def create_watch_party(self, movie_code: int, movie_title: str, host_name: str) -> Dict[str, Any]:
        room_id = "WP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        self.watch_rooms[room_id] = {
            "room_id": room_id,
            "movie_code": movie_code,
            "movie_title": movie_title,
            "host_name": host_name,
            "current_time": 0,
            "is_playing": False,
            "participants": [host_name],
            "messages": [
                {
                    "sender": "Tizim ✦",
                    "text": f"«{movie_title}» uchun Watch Party xonasi ochildi! Do'stlaringizga kodni yuboring: {room_id}",
                }
            ],
        }
        return self.watch_rooms[room_id]

    async def connect_watch_party(self, room_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.watch_connections.setdefault(room_id, set()).add(websocket)

    def disconnect_watch_party(self, room_id: str, websocket: WebSocket) -> None:
        if room_id in self.watch_connections:
            self.watch_connections[room_id].discard(websocket)

    async def broadcast_watch_party(self, room_id: str, payload: Dict[str, Any]) -> None:
        room = self.watch_rooms.get(room_id)
        if room:
            if "current_time" in payload:
                room["current_time"] = payload["current_time"]
            if "is_playing" in payload:
                room["is_playing"] = payload["is_playing"]
            if payload.get("type") == "chat":
                room["messages"].append({"sender": payload.get("user", "Mehmon"), "text": payload.get("text", "")})
                room["messages"] = room["messages"][-30:]

        dead: List[WebSocket] = []
        for ws in self.watch_connections.get(room_id, set()):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect_watch_party(room_id, ws)

    # --- Movie Matcher (Tinder for Movies) ---
    def create_matcher_room(self, creator_name: str) -> Dict[str, Any]:
        room_code = "MM-" + "".join(random.choices(string.digits, k=4))
        self.matcher_rooms[room_code] = {
            "room_code": room_code,
            "participants": [creator_name],
            "likes": {},  # {movie_code: set_of_users}
            "matches": [],
        }
        return self.matcher_rooms[room_code]

    def swipe_movie(self, room_code: str, user_name: str, movie_code: int, liked: bool) -> Dict[str, Any]:
        room = self.matcher_rooms.setdefault(
            room_code,
            {"room_code": room_code, "participants": [user_name, "Do'stingiz ✦"], "likes": {}, "matches": []},
        )
        if user_name not in room["participants"]:
            room["participants"].append(user_name)

        is_match = False
        if liked:
            likers: Set[str] = room["likes"].setdefault(movie_code, set())
            likers.add(user_name)
            # In single-device demo mode or when 2nd participant also liked, trigger Match!
            if len(likers) >= 2 or (len(room["participants"]) == 1 and movie_code in (421, 301, 502, 101)):
                is_match = True
                if movie_code not in room["matches"]:
                    room["matches"].append(movie_code)

        return {
            "room_code": room_code,
            "movie_code": movie_code,
            "liked": liked,
            "is_match": is_match,
            "matches": room["matches"],
        }

    # --- Smart TV 6-Digit Pairing ---
    def pair_smart_tv(self, tv_code: str, movie_code: int, movie_title: str, user_name: str) -> Dict[str, Any]:
        self.tv_sessions[tv_code] = {
            "tv_code": tv_code,
            "movie_code": movie_code,
            "movie_title": movie_title,
            "user_name": user_name,
            "status": "playing_on_tv",
        }
        return self.tv_sessions[tv_code]


realtime_hub = RealtimeHubManager()
