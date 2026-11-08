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

## Stress Test: Diverse and Adversarial Profiles

Six profiles are defined in `src/main.py`: three typical listeners and three adversarial ones built to try to trick the scoring. All six run with `python -m src.main`, and the top 5 for each is below (terminal output, copied as text).

### High-Energy Pop

```
================================================================
High-Energy Pop
----------------------------------------------------------------
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

### Chill Lofi

```
================================================================
Chill Lofi
----------------------------------------------------------------
Profile: genre=lofi, mood=chill, energy=0.40, likes_acoustic=True
================================================================

1. Library Rain by Paper Lanterns
   Score: 4.85 / 5.00   [lofi, chill]
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness 0.35 vs 0.40 (+1.42)
     - acoustic fit (+0.43)

2. Midnight Coding by LoRoom
   Score: 4.82 / 5.00   [lofi, chill]
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness 0.42 vs 0.40 (+1.47)
     - acoustic fit (+0.35)

3. Focus Flow by LoRoom
   Score: 3.89 / 5.00   [lofi, focused]
   Reasons:
     - genre match (+2.0)
     - energy closeness 0.40 vs 0.40 (+1.50)
     - acoustic fit (+0.39)

4. Spacewalk Thoughts by Orbit Bloom
   Score: 2.78 / 5.00   [ambient, chill]
   Reasons:
     - mood match (+1.0)
     - energy closeness 0.28 vs 0.40 (+1.32)
     - acoustic fit (+0.46)

5. Coffee Shop Stories by Slow Stereo
   Score: 1.90 / 5.00   [jazz, relaxed]
   Reasons:
     - energy closeness 0.37 vs 0.40 (+1.46)
     - acoustic fit (+0.45)
```

### Deep Intense Rock

```
================================================================
Deep Intense Rock
----------------------------------------------------------------
Profile: genre=rock, mood=intense, energy=0.90, likes_acoustic=False
================================================================

1. Storm Runner by Voltline
   Score: 4.93 / 5.00   [rock, intense]
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness 0.91 vs 0.90 (+1.48)
     - acoustic fit (+0.45)

2. Gym Hero by Max Pulse
   Score: 2.93 / 5.00   [pop, intense]
   Reasons:
     - mood match (+1.0)
     - energy closeness 0.93 vs 0.90 (+1.46)
     - acoustic fit (+0.47)

3. Pulse Factory by Circuit Saint
   Score: 1.91 / 5.00   [edm, euphoric]
   Reasons:
     - energy closeness 0.95 vs 0.90 (+1.43)
     - acoustic fit (+0.48)

4. Iron Tide by Black Anvil
   Score: 1.88 / 5.00   [metal, aggressive]
   Reasons:
     - energy closeness 0.97 vs 0.90 (+1.40)
     - acoustic fit (+0.48)

5. Sunrise City by Neon Echo
   Score: 1.79 / 5.00   [pop, happy]
   Reasons:
     - energy closeness 0.82 vs 0.90 (+1.38)
     - acoustic fit (+0.41)
```

### Adversarial: Sad but Energetic

```
================================================================
Adversarial: Sad but Energetic (blues/melancholic, energy 0.9)
----------------------------------------------------------------
Profile: genre=blues, mood=melancholic, energy=0.90, likes_acoustic=False
================================================================

1. Rainy Window Blues by Delta Hollow
   Score: 3.85 / 5.00   [blues, melancholic]
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness 0.38 vs 0.90 (+0.72)
     - acoustic fit (+0.13)

2. Storm Runner by Voltline
   Score: 1.93 / 5.00   [rock, intense]
   Reasons:
     - energy closeness 0.91 vs 0.90 (+1.48)
     - acoustic fit (+0.45)

3. Gym Hero by Max Pulse
   Score: 1.93 / 5.00   [pop, intense]
   Reasons:
     - energy closeness 0.93 vs 0.90 (+1.46)
     - acoustic fit (+0.47)

4. Pulse Factory by Circuit Saint
   Score: 1.91 / 5.00   [edm, euphoric]
   Reasons:
     - energy closeness 0.95 vs 0.90 (+1.43)
     - acoustic fit (+0.48)

5. Iron Tide by Black Anvil
   Score: 1.88 / 5.00   [metal, aggressive]
   Reasons:
     - energy closeness 0.97 vs 0.90 (+1.40)
     - acoustic fit (+0.48)
```

### Adversarial: Genre Not in Catalog

```
================================================================
Adversarial: Genre Not in Catalog (bossa nova)
----------------------------------------------------------------
Profile: genre=bossa nova, mood=happy, energy=0.50, likes_acoustic=True
================================================================

1. Rooftop Lights by Indigo Parade
   Score: 2.28 / 5.00   [indie pop, happy]
   Reasons:
     - mood match (+1.0)
     - energy closeness 0.76 vs 0.50 (+1.11)
     - acoustic fit (+0.17)

2. Sunrise City by Neon Echo
   Score: 2.11 / 5.00   [pop, happy]
   Reasons:
     - mood match (+1.0)
     - energy closeness 0.82 vs 0.50 (+1.02)
     - acoustic fit (+0.09)

3. Dusty Porch Swing by Willow Creek
   Score: 1.88 / 5.00   [country, nostalgic]
   Reasons:
     - energy closeness 0.48 vs 0.50 (+1.47)
     - acoustic fit (+0.41)

4. Coffee Shop Stories by Slow Stereo
   Score: 1.75 / 5.00   [jazz, relaxed]
   Reasons:
     - energy closeness 0.37 vs 0.50 (+1.30)
     - acoustic fit (+0.45)

5. Focus Flow by LoRoom
   Score: 1.74 / 5.00   [lofi, focused]
   Reasons:
     - energy closeness 0.40 vs 0.50 (+1.35)
     - acoustic fit (+0.39)
```

### Adversarial: Classical at Full Blast

```
================================================================
Adversarial: Classical at Full Blast (classical/peaceful, energy 0.95)
----------------------------------------------------------------
Profile: genre=classical, mood=peaceful, energy=0.95, likes_acoustic=True
================================================================

1. Moonlit Sonata Remix by Clara Voss
   Score: 3.83 / 5.00   [classical, peaceful]
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy closeness 0.18 vs 0.95 (+0.34)
     - acoustic fit (+0.48)

2. Pulse Factory by Circuit Saint
   Score: 1.51 / 5.00   [edm, euphoric]
   Reasons:
     - energy closeness 0.95 vs 0.95 (+1.50)
     - acoustic fit (+0.01)

3. Gym Hero by Max Pulse
   Score: 1.50 / 5.00   [pop, intense]
   Reasons:
     - energy closeness 0.93 vs 0.95 (+1.47)
     - acoustic fit (+0.03)

4. Storm Runner by Voltline
   Score: 1.49 / 5.00   [rock, intense]
   Reasons:
     - energy closeness 0.91 vs 0.95 (+1.44)
     - acoustic fit (+0.05)

5. Iron Tide by Black Anvil
   Score: 1.49 / 5.00   [metal, aggressive]
   Reasons:
     - energy closeness 0.97 vs 0.95 (+1.47)
     - acoustic fit (+0.02)
```

### What the stress test showed

- **The typical profiles behave well.** Chill Lofi and Deep Intense Rock each get a clear #1 (Library Rain 4.85, Storm Runner 4.93), and the two top lists do not overlap.
- **Sad but Energetic:** Rainy Window Blues wins with 3.85 even though its energy is 0.38 against a requested 0.90. The 3 categorical points outweigh a 0.78-point energy penalty. The remaining four are just high-energy songs with no real fit for "sad". Iron Tide (valence 0.28, the darkest high-energy song) ranks fifth because the system never looks at `valence` and its mood is "aggressive", not "melancholic". Storm Runner and Gym Hero tie at 1.93.
- **Genre Not in Catalog:** With no genre match possible, the best score is only 2.28 out of a possible 3.0, and the system still presents confident-looking results without any warning that nothing fit well.
- **Classical at Full Blast:** Moonlit Sonata Remix wins with 3.83 at energy 0.18, although the user asked for 0.95. Genre and mood together are worth 3 points and energy at most 1.5, so a user who explicitly wants high energy can still be handed the calmest song in the catalog.
- **Takeaway:** the scoring is easily dominated by exact genre and mood labels, and it is blind to valence. Both are candidates for the Experiments section (lower the genre weight, double the energy weight, add valence).

---

## Challenge 1: Advanced Song Features

`data/songs.csv` now has five more columns for every song: `popularity` (0-100), `release_decade`, `mood_tags` (three tags per song), `instrumentalness` (0-1) and `language`. A user profile can optionally set `mood_tags`, `target_popularity`, `preferred_decade`, `likes_instrumental` and `language`, and `score_song` adds points for each preference it sets.

| New rule | Points |
|---|---|
| Mood tags: share of the user's wanted tags the song has | up to +0.75 |
| Popularity closeness to the target | up to +0.50 |
| Release decade closeness (zero at 30+ years apart) | up to +0.50 |
| Instrumental fit | up to +0.25 |
| Language match | +0.25 |

These rules only run for profiles that set the preference, so the six original profiles score exactly as before. The displayed maximum comes from `max_score()` (5.0 for the original profiles, 7.25 for the advanced ones). Three advanced profiles (Nostalgic 90s Listener, Instrumental Study Session, Mainstream Party Hits) run after the six originals in `python -m src.main`. Details of how this was built are in `ai_interactions.md`.

---

## Challenge 2: Multiple Scoring Modes

Pick a ranking strategy from the command line. Each mode is a `ScoringMode` (a Strategy-style object holding weights) in `src/recommender.py`.

| Mode | Genre | Mood | Energy | Acoustic | Idea |
|---|---|---|---|---|---|
| `genre-first` (default) | 2.0 | 1.0 | 1.5 | 0.5 | Genre matters most |
| `mood-first` | 1.0 | 2.5 | 1.5 | 0.5 | Mood matters most |
| `energy-focused` | 1.0 | 0.5 | 3.0 | 0.5 | Energy closeness matters most |

```bash
python -m src.main --mode mood-first
```

Example: for the "Classical at Full Blast" profile, `genre-first` and `mood-first` both put the calm classical song first, but `energy-focused` puts Pulse Factory first, which is much closer to the energy that was asked for.

## Challenge 3: Diversity Penalty

Add `--diversity` to re-rank the top results so they are not all from the same artist or genre. Songs are picked one at a time. Each later pick loses **1.0** point for every already-chosen song by the same artist and **0.5** for every one of the same genre.

```bash
python -m src.main --diversity
```

Example (Chill Lofi): without the penalty the top 5 are Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts, Coffee Shop Stories. With it, Focus Flow (same artist and genre as Midnight Coding) drops from 3rd to 5th, and Spacewalk Thoughts and Coffee Shop Stories move up. The explanation shows each penalty, for example `diversity: genre already picked (-0.50)`.

---

## Challenge 4: Visual Summary Table

Add `--table` to show each profile's top 5 as a bordered ASCII table with the rank, song and artist, genre and mood, score out of the maximum, and the reasons for that score. It uses only the Python standard library (`textwrap`), so there is nothing extra to install, and it combines with `--mode` and `--diversity`.

```bash
python -m src.main --table
```

```
Chill Lofi
Profile: genre=lofi, mood=chill, energy=0.40, likes_acoustic=True
+---+---------------------------+-----------------+-----------+-----------------------------------------+
| # | Song (artist)             | Genre / mood    | Score     | Reasons                                 |
+---+---------------------------+-----------------+-----------+-----------------------------------------+
| 1 | Library Rain (Paper       | lofi / chill    | 4.85/5.00 | - genre match (+2.0)                    |
|   | Lanterns)                 |                 |           | - mood match (+1.0)                     |
|   |                           |                 |           | - energy closeness 0.35 vs 0.40 (+1.42) |
|   |                           |                 |           | - acoustic fit (+0.43)                  |
+---+---------------------------+-----------------+-----------+-----------------------------------------+
| 2 | Midnight Coding (LoRoom)  | lofi / chill    | 4.82/5.00 | - genre match (+2.0)                    |
|   |                           |                 |           | - mood match (+1.0)                     |
|   |                           |                 |           | - energy closeness 0.42 vs 0.40 (+1.47) |
|   |                           |                 |           | - acoustic fit (+0.35)                  |
+---+---------------------------+-----------------+-----------+-----------------------------------------+
| 3 | Focus Flow (LoRoom)       | lofi / focused  | 3.89/5.00 | - genre match (+2.0)                    |
|   |                           |                 |           | - energy closeness 0.40 vs 0.40 (+1.50) |
|   |                           |                 |           | - acoustic fit (+0.39)                  |
+---+---------------------------+-----------------+-----------+-----------------------------------------+
| 4 | Spacewalk Thoughts (Orbit | ambient / chill | 2.78/5.00 | - mood match (+1.0)                     |
|   | Bloom)                    |                 |           | - energy closeness 0.28 vs 0.40 (+1.32) |
|   |                           |                 |           | - acoustic fit (+0.46)                  |
+---+---------------------------+-----------------+-----------+-----------------------------------------+
| 5 | Coffee Shop Stories (Slow | jazz / relaxed  | 1.90/5.00 | - energy closeness 0.37 vs 0.40 (+1.46) |
|   | Stereo)                   |                 |           | - acoustic fit (+0.45)                  |
+---+---------------------------+-----------------+-----------+-----------------------------------------+
```

---

## Experiments You Tried

### Do the results feel right?

For High-Energy Pop, Sunrise City at #1 matches my intuition. It is pop, happy, and almost exactly the requested energy, so it earns every category: genre +2.0, mood +1.0, energy +1.47 (0.82 vs 0.80), acoustic +0.41 = 4.88 out of 5.0. Gym Hero at #2 feels a little off. It is intense, not happy, and ranks above Rooftop Lights (happy, similar energy) only because "pop" matches exactly and "indie pop" does not (+2.0 beats +1.0 for mood).

The same song does not top every list (Sunrise City, Library Rain, Storm Runner and Rainy Window Blues lead different profiles), so genre is not simply drowning out variety. Gym Hero is the one repeat offender: it appears in the top 5 of four of the six profiles, because it is very high energy and scores well on energy for almost any energetic request.

### Experiment: weight shift (genre 2.0 to 1.0, energy 1.5 to 3.0)

I doubled the importance of energy and halved genre, keeping mood and acoustic the same. The maximum score rises from 5.0 to 5.5 (1.0 + 1.0 + 3.0 + 0.5), so the displayed maximum is derived from the weights (`MAX_SCORE` in `src/recommender.py`) and every score still falls between 0 and the maximum. The experiment was run on a copy of the weights, and the committed defaults stay at 2.0 / 1.0 / 1.5 / 0.5. Rankings before and after:

| Profile | Baseline top 3 | Weight shift top 3 | Change |
|---|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights | Sunrise City, Rooftop Lights, Gym Hero | #2 and #3 swap |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow | Midnight Coding, Library Rain, Focus Flow | #1 and #2 swap (4.85 vs 4.82 becomes 5.28 vs 5.29) |
| Deep Intense Rock | Storm Runner, Gym Hero, Pulse Factory | same | none |
| Sad but Energetic | Rainy Window Blues, Storm Runner, Gym Hero | same | winner's lead shrinks from 3.85 vs 1.93 to 3.57 vs 3.42 |
| Genre Not in Catalog | Rooftop Lights, Sunrise City, Dusty Porch Swing | Rooftop Lights, Dusty Porch Swing, Sunrise City | #2 and #3 swap |
| Classical at Full Blast | Moonlit Sonata Remix, Pulse Factory, Gym Hero | same | winner's lead shrinks from 3.83 vs 1.51 to 3.17 vs 3.02 |

**Verdict: more accurate for some profiles, just different for others.**
- **More accurate:** High-Energy Pop now puts Rooftop Lights (happy, 0.76 energy) above Gym Hero (intense), which fixes the surprise noted above. The two adversarial profiles are also closer to fair: the blues and classical winners still win on genre and mood, but their margins over high-energy songs shrink a lot, so the requested energy is respected much more.
- **Just different:** The Chill Lofi swap between Library Rain and Midnight Coding is a coin flip (the scores differ by 0.01), so neither order is more correct.
- **Still not fixed:** The classical and blues users still get the song that is wrong on energy at #1, and nothing signals that a request matched poorly.

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



