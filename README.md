# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

### How real-world recommenders work

Platforms like Spotify and YouTube combine two main approaches. **Collaborative filtering** predicts what you'll like from the behavior of *other* users. If people who liked the same songs as you also loved a track you haven't heard, it gets recommended. It needs no knowledge of the music itself, but it struggles with brand-new songs or users (the "cold start" problem). **Content-based filtering** predicts what you'll like from the *attributes of the items* you already enjoy, such as tempo, energy, mood, or genre. It works for new songs, but it can trap you in a narrow bubble. At scale, these systems learn from huge amounts of behavioral data: likes, skips, replays, listen time, playlist additions, searches, and shares. They pair that with audio features (tempo, mood, energy) and metadata (genre, artist). They blend the signals with machine-learning models, and implicit signals like a skip within 5 seconds often matter more than an explicit like.

### What my version prioritizes

My simulator is a **content-based recommender only**. There are no other users, so there is nothing to do collaborative filtering on. It prioritizes how well a song's "vibe" matches the user's stated taste. Mood and genre are categorical matches, and energy is a numeric closeness match. A song scores higher the *closer* its energy is to the user's target, not simply the higher or lower it is. For example, `1 - abs(song.energy - target_energy)`. Genre will be weighted slightly higher than mood, since genre is a stronger filter on what someone will even consider listening to. Mood and energy together capture the feel.

Two separate rules are needed. The **Scoring Rule** judges one song against one user and returns a number. The **Ranking Rule** applies that score to every song in the catalog, sorts the results from highest to lowest, and returns the top *k*. A score on its own can't produce a recommendation list, and sorting needs scores to sort by.

### Features used

**`Song`** (from `data/songs.csv`):

- `id`, `title`, `artist` are identifiers and are not used in scoring
- `genre` is a categorical match
- `mood` is a categorical match
- `energy` (0-1) is a numeric closeness match
- `tempo_bpm` is a numeric feature, normalized and optional in the score
- `valence` (0-1, musical positivity) is a numeric feature, optional
- `danceability` (0-1) is a numeric feature, optional
- `acousticness` (0-1) is compared with the user's acoustic preference

**`UserProfile`**:

- `favorite_genre` (str)
- `favorite_mood` (str)
- `target_energy` (float, 0-1)
- `likes_acoustic` (bool), which rewards high `acousticness` if true and low if false

### Algorithm recipe

**Scoring Rule** (one song vs. one user, max 5.0 points):

| Rule | Points |
|---|---|
| Genre matches `favorite_genre` | +2.0 |
| Mood matches `favorite_mood` | +1.0 |
| Energy closeness: `1.5 * (1 - abs(song.energy - target_energy))` | 0 to +1.5 |
| Acoustic fit: `0.5 * acousticness` if `likes_acoustic`, else `0.5 * (1 - acousticness)` | 0 to +0.5 |

**Ranking Rule:** score every song in the catalog, sort by score from highest to lowest, and return the top *k*. Each result carries a short explanation listing which rules contributed points.

**Why these weights:** Genre is the broadest filter on what a listener will even consider, so it gets the most points for a single match. Mood refines the feel within a genre, so it gets half as much. Energy is the one numeric feature that separates the catalog well (calm songs sit around 0.3-0.4 and high-energy songs at 0.75+), so it can contribute up to 1.5 points. That lets a close energy match outweigh a mood match. Acousticness is a tie-breaker. Tempo and danceability are left out because they largely repeat energy.

### Dataset and user profiles

The catalog in `data/songs.csv` has **18 songs**: the 10 starter songs plus 8 added ones covering new genres (hip hop, classical, country, r&b, metal, reggae, edm, blues) and new moods (confident, peaceful, nostalgic, romantic, aggressive, uplifting, euphoric, melancholic).

Two test profiles live in `src/main.py`:

```python
CHILL_LOFI   = {"genre": "lofi", "mood": "chill",   "energy": 0.40, "likes_acoustic": True}
INTENSE_ROCK = {"genre": "rock", "mood": "intense", "energy": 0.90, "likes_acoustic": False}
```

By hand, they produce completely different top results (Library Rain for lofi, Storm Runner for rock), so the profiles can tell these two tastes apart.

### Data flow

```
user_prefs + songs.csv --load_songs--> list of song dicts
  -> for each song: score_song(user_prefs, song) -> (score, reasons)
  -> sort all by score, highest first
  -> top k with explanations
```

### Expected biases

- **Genre may be over-prioritized.** A genre match is worth twice a mood match, so a same-genre song can beat a song that fits the user's mood and energy better. For example, a pop/happy user would see Gym Hero (pop, intense) ahead of Rooftop Lights (indie pop, happy, similar energy).
- **Exact-match labels ignore near-synonyms.** "aggressive" vs. "intense", "chill" vs. "relaxed", and "pop" vs. "indie pop" are scored as completely different.
- **Sparse categories.** Apart from lofi and pop, each genre and mood has only one or two songs, so matching rewards whichever single song carries the label, and many requests will have just one real candidate.
- **One taste per user.** A profile has a single target energy and one genre and mood, so listeners with mixed tastes are not represented.
- **The catalog is small and hand-made**, and it leans toward a Western-pop-style set of genres. Results say more about my weights than about real listening behavior.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default pop/happy profile:

```
Loaded songs: 18

================================================================
Profile: genre=pop, mood=happy, energy=0.80, likes_acoustic=False
================================================================

1. Sunrise City by Neon Echo
   Score: 4.88 / 5.00   [pop, happy]
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness 0.82 vs 0.80 (+1.47)
     - acoustic fit (+0.41)

2. Gym Hero by Max Pulse
   Score: 3.78 / 5.00   [pop, intense]
   Reasons:
     - genre match (+2.0)
     - energy closeness 0.93 vs 0.80 (+1.30)
     - acoustic fit (+0.47)

3. Rooftop Lights by Indigo Parade
   Score: 2.77 / 5.00   [indie pop, happy]
   Reasons:
     - mood match (+1.0)
     - energy closeness 0.76 vs 0.80 (+1.44)
     - acoustic fit (+0.33)

4. Concrete Crown by Verse Dynasty
   Score: 1.93 / 5.00   [hip hop, confident]
   Reasons:
     - energy closeness 0.78 vs 0.80 (+1.47)
     - acoustic fit (+0.46)

5. Night Drive Loop by Neon Echo
   Score: 1.81 / 5.00   [synthwave, moody]
   Reasons:
     - energy closeness 0.75 vs 0.80 (+1.42)
     - acoustic fit (+0.39)
```

Sunrise City wins because it matches on genre, mood and energy. Gym Hero beats Rooftop Lights only because "pop" is an exact genre match while "indie pop" is not, which is the genre-over-mood bias noted above.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



