"""
Command line runner for the Music Recommender Simulation.

Run from the repo root:  python -m src.main
"""

import argparse
import textwrap

from src.recommender import DEFAULT_MODE, MODES, load_songs, max_score, recommend_songs

# Taste profiles: target values the scoring rule compares each song against.
# Three typical listeners...
HIGH_ENERGY_POP = {"genre": "pop", "mood": "happy", "energy": 0.80, "likes_acoustic": False}
CHILL_LOFI = {"genre": "lofi", "mood": "chill", "energy": 0.40, "likes_acoustic": True}
DEEP_INTENSE_ROCK = {"genre": "rock", "mood": "intense", "energy": 0.90, "likes_acoustic": False}

# ...and three adversarial / edge-case profiles built to try to trick the scoring.
SAD_BUT_ENERGETIC = {"genre": "blues", "mood": "melancholic", "energy": 0.90, "likes_acoustic": False}
UNKNOWN_GENRE = {"genre": "bossa nova", "mood": "happy", "energy": 0.50, "likes_acoustic": True}
CLASSICAL_AT_FULL_BLAST = {"genre": "classical", "mood": "peaceful", "energy": 0.95, "likes_acoustic": True}

PROFILES = {
    "High-Energy Pop": HIGH_ENERGY_POP,
    "Chill Lofi": CHILL_LOFI,
    "Deep Intense Rock": DEEP_INTENSE_ROCK,
    "Adversarial: Sad but Energetic (blues/melancholic, energy 0.9)": SAD_BUT_ENERGETIC,
    "Adversarial: Genre Not in Catalog (bossa nova)": UNKNOWN_GENRE,
    "Adversarial: Classical at Full Blast (classical/peaceful, energy 0.95)": CLASSICAL_AT_FULL_BLAST,
}

# Profiles that use the advanced song attributes (tags, popularity, decade, instrumental, language).
NOSTALGIC_90S = {
    "genre": "country", "mood": "nostalgic", "energy": 0.50, "likes_acoustic": True,
    "mood_tags": ["nostalgic", "warm", "cozy"], "target_popularity": 55,
    "preferred_decade": 1990, "likes_instrumental": False, "language": "english",
}
STUDY_INSTRUMENTAL = {
    "genre": "lofi", "mood": "focused", "energy": 0.40, "likes_acoustic": True,
    "mood_tags": ["focused", "calm", "cozy"], "target_popularity": 40,
    "preferred_decade": 2020, "likes_instrumental": True, "language": "instrumental",
}
MAINSTREAM_PARTY = {
    "genre": "edm", "mood": "euphoric", "energy": 0.90, "likes_acoustic": False,
    "mood_tags": ["euphoric", "energetic", "danceable"], "target_popularity": 90,
    "preferred_decade": 2010, "likes_instrumental": False, "language": "english",
}

ADVANCED_PROFILES = {
    "Advanced: Nostalgic 90s Listener": NOSTALGIC_90S,
    "Advanced: Instrumental Study Session": STUDY_INSTRUMENTAL,
    "Advanced: Mainstream Party Hits": MAINSTREAM_PARTY,
}

WIDTH = 64


def print_recommendations(name: str, user_prefs: dict, recommendations: list, mode=DEFAULT_MODE) -> None:
    """Print a profile header and each recommendation with its score and reasons."""
    print("=" * WIDTH)
    print(name)
    print("-" * WIDTH)
    print(
        f"Profile: genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
        f"energy={user_prefs['energy']:.2f}, likes_acoustic={user_prefs['likes_acoustic']}"
    )
    print("=" * WIDTH)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} / {max_score(user_prefs, mode):.2f}   [{song['genre']}, {song['mood']}]")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def format_table(user_prefs: dict, recommendations: list, mode=DEFAULT_MODE) -> str:
    """Return the top results as an ASCII table: rank, song, genre/mood, score, and wrapped reasons."""
    headers = ["#", "Song (artist)", "Genre / mood", "Score", "Reasons"]
    reason_width = 58
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = [
            line
            for reason in explanation.split("; ")
            for line in textwrap.wrap(reason, reason_width, initial_indent="- ", subsequent_indent="  ")
        ]
        rows.append((
            [str(rank)],
            textwrap.wrap(f"{song['title']} ({song['artist']})", 28),
            [f"{song['genre']} / {song['mood']}"],
            [f"{score:.2f}/{max_score(user_prefs, mode):.2f}"],
            reasons,
        ))
    return _render(headers, rows)


def _render(headers: list, rows: list) -> str:
    """Draw a bordered table; each cell is a list of lines so rows can be several lines tall."""
    widths = [max(len(h), *(len(line) for row in rows for line in row[i])) for i, h in enumerate(headers)]
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def line(cells):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

    out = [border, line(headers), border]
    for row in rows:
        height = max(len(cell) for cell in row)
        for n in range(height):
            out.append(line([cell[n] if n < len(cell) else "" for cell in row]))
        out.append(border)
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=sorted(MODES), default=DEFAULT_MODE.name,
                        help="ranking strategy (default: genre-first)")
    parser.add_argument("--diversity", action="store_true",
                        help="penalize repeat artists and genres in the top results")
    parser.add_argument("--table", action="store_true",
                        help="show results as a summary table (with reasons) instead of a list")
    args = parser.parse_args()
    mode = MODES[args.mode]

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")
    if mode is not DEFAULT_MODE or args.diversity:
        print(f"Mode: {mode.name} ({mode.description}) | diversity penalty: {'on' if args.diversity else 'off'}\n")

    for name, user_prefs in {**PROFILES, **ADVANCED_PROFILES}.items():
        recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode, diversity=args.diversity)
        if args.table:
            print(f"{name}\nProfile: genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
                  f"energy={user_prefs['energy']:.2f}, likes_acoustic={user_prefs['likes_acoustic']}")
            print(format_table(user_prefs, recommendations, mode))
            print()
        else:
            print_recommendations(name, user_prefs, recommendations, mode)


if __name__ == "__main__":
    main()
