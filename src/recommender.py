import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Advanced attributes (optional so older code that builds a Song still works)
    popularity: Optional[int] = None          # 0-100
    release_decade: Optional[int] = None      # e.g. 1990
    mood_tags: Optional[List[str]] = None     # detailed tags, e.g. ["nostalgic", "warm"]
    instrumentalness: Optional[float] = None  # 0-1, 1 = no vocals
    language: Optional[str] = None            # e.g. "english", "instrumental"

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Advanced preferences (all optional; a missing one adds no points)
    mood_tags: Optional[List[str]] = None
    target_popularity: Optional[int] = None
    preferred_decade: Optional[int] = None
    likes_instrumental: Optional[bool] = None
    language: Optional[str] = None

# Scoring weights; MAX_SCORE is derived so the displayed maximum always matches them.
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_WEIGHT = 0.5
MAX_SCORE = GENRE_WEIGHT + MOOD_WEIGHT + ENERGY_WEIGHT + ACOUSTIC_WEIGHT

@dataclass(frozen=True)
class ScoringMode:
    """A ranking strategy: the weights for the four core rules, swappable at call time."""
    name: str
    description: str
    genre: float
    mood: float
    energy: float
    acoustic: float


# Strategy pattern: each mode is data, and score_song() / recommend_songs() accept any of them.
GENRE_FIRST = ScoringMode(
    "genre-first", "Genre matters most (the default).",
    GENRE_WEIGHT, MOOD_WEIGHT, ENERGY_WEIGHT, ACOUSTIC_WEIGHT)
MOOD_FIRST = ScoringMode(
    "mood-first", "Mood matters most; genre counts for less.",
    genre=1.0, mood=2.5, energy=1.5, acoustic=0.5)
ENERGY_FOCUSED = ScoringMode(
    "energy-focused", "Energy closeness matters most; labels count for less.",
    genre=1.0, mood=0.5, energy=3.0, acoustic=0.5)
MODES = {m.name: m for m in (GENRE_FIRST, MOOD_FIRST, ENERGY_FOCUSED)}
DEFAULT_MODE = GENRE_FIRST

# Diversity penalty (Challenge 3), applied while building the top-k list.
ARTIST_PENALTY = 1.0  # subtracted per song by the same artist already chosen
GENRE_PENALTY = 0.5   # subtracted per song of the same genre already chosen

# Advanced-feature weights. Each only counts when the user profile sets that preference.
TAGS_WEIGHT = 0.75          # share of the user's wanted mood tags the song has
POPULARITY_WEIGHT = 0.5     # closeness of popularity to the target (0-100)
DECADE_WEIGHT = 0.5         # closeness of release decade; 0 once 30+ years apart
DECADE_SPREAD = 30
INSTRUMENTAL_WEIGHT = 0.25  # fit with likes_instrumental
LANGUAGE_WEIGHT = 0.25      # exact language match


def max_score(user_prefs: Dict, mode: ScoringMode = DEFAULT_MODE) -> float:
    """Return the highest score possible for this profile and mode, counting only the rules it uses."""
    total = mode.genre + mode.mood + mode.energy + mode.acoustic
    optional = (
        ("mood_tags", TAGS_WEIGHT), ("target_popularity", POPULARITY_WEIGHT),
        ("preferred_decade", DECADE_WEIGHT), ("likes_instrumental", INSTRUMENTAL_WEIGHT),
        ("language", LANGUAGE_WEIGHT),
    )
    return total + sum(w for key, w in optional if user_prefs.get(key) is not None)


def _song_to_dict(song: Song) -> Dict:
    """Convert a Song dataclass into the dict format score_song expects."""
    return {
        "id": song.id, "title": song.title, "artist": song.artist,
        "genre": song.genre, "mood": song.mood, "energy": song.energy,
        "tempo_bpm": song.tempo_bpm, "valence": song.valence,
        "danceability": song.danceability, "acousticness": song.acousticness,
        "popularity": song.popularity, "release_decade": song.release_decade,
        "mood_tags": song.mood_tags, "instrumentalness": song.instrumentalness,
        "language": song.language,
    }


def _user_to_dict(user: UserProfile) -> Dict:
    """Convert a UserProfile dataclass into the user_prefs dict score_song expects."""
    return {
        "genre": user.favorite_genre, "mood": user.favorite_mood,
        "energy": user.target_energy, "likes_acoustic": user.likes_acoustic,
        "mood_tags": user.mood_tags, "target_popularity": user.target_popularity,
        "preferred_decade": user.preferred_decade, "likes_instrumental": user.likes_instrumental,
        "language": user.language,
    }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for this user, highest score first."""
        prefs = _user_to_dict(user)
        ranked = sorted(
            self.songs,
            key=lambda s: score_song(prefs, _song_to_dict(s))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a one-line explanation of why this song scored as it did."""
        score, reasons = score_song(_user_to_dict(user), _song_to_dict(song))
        return f"{song.title} scored {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV into dicts, converting numeric columns to int/float."""
    int_fields = ("id", "popularity", "release_decade")
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness", "instrumentalness")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            row["mood_tags"] = [t for t in row["mood_tags"].split("|") if t]
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: ScoringMode = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """Score one song against user preferences, returning (score, reasons); see max_score()."""
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs.get("genre"):
        score += mode.genre
        reasons.append(f"genre match (+{mode.genre:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += mode.mood
        reasons.append(f"mood match (+{mode.mood:.1f})")

    if "energy" in user_prefs:
        closeness = 1 - abs(song["energy"] - user_prefs["energy"])
        points = mode.energy * closeness
        score += points
        reasons.append(f"energy closeness {song['energy']:.2f} vs {user_prefs['energy']:.2f} (+{points:.2f})")

    if "likes_acoustic" in user_prefs:
        fit = song["acousticness"] if user_prefs["likes_acoustic"] else 1 - song["acousticness"]
        points = mode.acoustic * fit
        score += points
        reasons.append(f"acoustic fit (+{points:.2f})")

    # --- Advanced features: each is skipped if the user or the song lacks the value ---
    wanted_tags = user_prefs.get("mood_tags")
    if wanted_tags and song.get("mood_tags"):
        shared = [t for t in wanted_tags if t in song["mood_tags"]]
        points = TAGS_WEIGHT * len(shared) / len(wanted_tags)
        score += points
        if shared:
            reasons.append(f"mood tags {'/'.join(shared)} (+{points:.2f})")

    target_pop = user_prefs.get("target_popularity")
    if target_pop is not None and song.get("popularity") is not None:
        points = POPULARITY_WEIGHT * (1 - abs(song["popularity"] - target_pop) / 100)
        score += points
        reasons.append(f"popularity {song['popularity']} vs {target_pop} (+{points:.2f})")

    decade = user_prefs.get("preferred_decade")
    if decade is not None and song.get("release_decade") is not None:
        points = DECADE_WEIGHT * max(0.0, 1 - abs(song["release_decade"] - decade) / DECADE_SPREAD)
        score += points
        if points > 0:
            reasons.append(f"release decade {song['release_decade']}s vs {decade}s (+{points:.2f})")

    likes_instr = user_prefs.get("likes_instrumental")
    if likes_instr is not None and song.get("instrumentalness") is not None:
        fit = song["instrumentalness"] if likes_instr else 1 - song["instrumentalness"]
        points = INSTRUMENTAL_WEIGHT * fit
        score += points
        reasons.append(f"instrumental fit (+{points:.2f})")

    wanted_lang = user_prefs.get("language")
    if wanted_lang and song.get("language") == wanted_lang:
        score += LANGUAGE_WEIGHT
        reasons.append(f"language match ({wanted_lang}) (+{LANGUAGE_WEIGHT:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: ScoringMode = DEFAULT_MODE,
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Score every song with the given mode, rank highest first, return the top k as (song, score, explanation).

    With diversity=True, songs are picked one at a time and each later pick loses points for every
    already-chosen song with the same artist (ARTIST_PENALTY) or genre (GENRE_PENALTY).
    """
    # sorted() returns a NEW list and leaves `songs` untouched (list.sort() would
    # reorder in place), so the catalog keeps its original order for the next call.
    scored = [(song, *score_song(user_prefs, song, mode)) for song in songs]  # (song, score, reasons)
    if not diversity:
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)
        return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]

    chosen: List[Tuple[Dict, float, str]] = []
    pool = scored
    while pool and len(chosen) < k:
        best = None  # (adjusted_score, index, extra_reasons)
        for i, (song, score, reasons) in enumerate(pool):
            same_artist = sum(1 for c, _, _ in chosen if c["artist"] == song["artist"])
            same_genre = sum(1 for c, _, _ in chosen if c["genre"] == song["genre"])
            penalty = ARTIST_PENALTY * same_artist + GENRE_PENALTY * same_genre
            if best is None or score - penalty > best[0]:
                extra = []
                if same_artist:
                    extra.append(f"diversity: artist already picked (-{ARTIST_PENALTY * same_artist:.2f})")
                if same_genre:
                    extra.append(f"diversity: genre already picked (-{GENRE_PENALTY * same_genre:.2f})")
                best = (score - penalty, i, extra)
        adjusted, i, extra = best
        song, _, reasons = pool[i]
        chosen.append((song, adjusted, "; ".join(reasons + extra)))
        pool = pool[:i] + pool[i + 1:]
    return chosen
