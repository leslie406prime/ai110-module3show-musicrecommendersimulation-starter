"""
Command line runner for the Music Recommender Simulation.

Run from the repo root:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs

# Taste profiles: target values the scoring rule compares each song against.
POP_HAPPY = {"genre": "pop", "mood": "happy", "energy": 0.80, "likes_acoustic": False}
CHILL_LOFI = {"genre": "lofi", "mood": "chill", "energy": 0.40, "likes_acoustic": True}
INTENSE_ROCK = {"genre": "rock", "mood": "intense", "energy": 0.90, "likes_acoustic": False}

WIDTH = 64


def print_recommendations(user_prefs: dict, recommendations: list) -> None:
    """Print a profile header and each recommendation with its score and reasons."""
    print("=" * WIDTH)
    print(
        f"Profile: genre={user_prefs['genre']}, mood={user_prefs['mood']}, "
        f"energy={user_prefs['energy']:.2f}, likes_acoustic={user_prefs['likes_acoustic']}"
    )
    print("=" * WIDTH)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} / 5.00   [{song['genre']}, {song['mood']}]")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    user_prefs = POP_HAPPY  # swap in CHILL_LOFI or INTENSE_ROCK to compare tastes
    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(user_prefs, recommendations)


if __name__ == "__main__":
    main()
