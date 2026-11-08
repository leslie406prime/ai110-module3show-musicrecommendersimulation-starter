# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Challenge 1: add five or more advanced attributes to the song data, then update both `data/songs.csv` and the scoring logic in `src/recommender.py` so scoring uses them.

**Prompts used:**

> "Challenge 1: Add Advanced Song Features. Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags (e.g., "nostalgic," "aggressive," "euphoric"). Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes. In ai_interactions.md, document the agentic workflow."

The agent made the design choices itself (which five attributes, what weights, how to keep the old profiles working) and ran its own checks.

**What did the agent generate or change?**

- `data/songs.csv`: added five columns to all 18 songs: `popularity` (0-100), `release_decade` (1960-2020), `mood_tags` (3 pipe-separated tags such as `nostalgic|warm|cozy`), `instrumentalness` (0-1) and `language`.
- `src/recommender.py`:
  - `load_songs` now converts the new numeric columns and splits `mood_tags` into a list.
  - `score_song` has five new optional rules: mood-tag overlap (up to 0.75), popularity closeness (up to 0.5), release-decade closeness (up to 0.5, zero when 30 or more years apart), instrumental fit (up to 0.25) and language match (0.25).
  - Each rule only runs when the user profile sets that preference, so the six original profiles score exactly as before.
  - New `max_score(user_prefs)` returns the true maximum for a profile (5.0 for the original profiles, 7.25 for the advanced ones), so the CLI never shows a score above its maximum.
  - `Song` and `UserProfile` gained the new fields with `None` defaults so the starter tests still build them.
- `src/main.py`: three new profiles (Nostalgic 90s Listener, Instrumental Study Session, Mainstream Party Hits), and the printed maximum now comes from `max_score`.
- Commands run: the starter tests (`pytest`) and `python -m src.main`.

**What did you verify or fix manually?**

Checks done and results:
- The 2 starter tests still pass.
- The six original profiles still produce identical scores and a 5.00 maximum (for example 1.93 / 5.00 for Storm Runner on the Sad but Energetic profile).
- I recomputed Dusty Porch Swing for the Nostalgic 90s profile by hand: 2 + 1 + 1.47 + 0.405 + 0.75 + 0.485 + 0.5 + 0.225 + 0.25 = 7.085, matching the printed 7.08 / 7.25.
- A script scored all 18 songs against all 9 profiles and confirmed every score is between 0 and that profile's maximum. Popularity is within 0-100 for every song.

Issues found along the way:
- A first attempt to apply the changes in one shell command failed on quoting, so the patch was redone as a script file. Nothing was half-applied.
- The new rules depend on made-up data (popularity, decades and tags are invented), so the results show the logic works, not that the rankings reflect real taste.
- Mood tags can overpower the labels: Coffee Shop Stories ranks second for the Nostalgic profile with no genre or mood match, purely from tag overlap and the language and acoustic rules. That could be what a user wants, but the weights are a judgment call.

*Student note: replace or add to this with your own checks. Run `python -m src.main`, read a few reason lists, and confirm they match your intuition.*

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

A simple **Strategy pattern** for Challenge 2 (multiple scoring modes). Each mode is a small frozen dataclass, `ScoringMode`, that holds the weights for genre, mood, energy and acoustic fit. The scoring and ranking functions take a mode as an argument instead of reading fixed constants.

**How did AI help you brainstorm or implement it?**

Prompt: *"Attach recommender.py. Brainstorm a design pattern, like a simple Strategy pattern, that lets me switch between ranking modes such as Genre-First, Mood-First and Energy-Focused and keeps the code modular."*

The AI suggested three options:
1. **`if mode == ...` branches inside `score_song`.** Easy, but every new mode means editing the scoring function.
2. **One subclass per mode** (a classic Strategy with an interface). Flexible, but heavy for modes that differ only in numbers.
3. **Modes as data.** A `ScoringMode` dataclass holding the weights, and one scoring function that reads them. This is a lightweight Strategy: the "strategy" is the set of weights passed in.

We chose option 3 because the modes only differ by weights, so a new mode is one line of data and `score_song` does not change. The AI also suggested keeping the old behavior as the default argument so the original profiles and tests keep working, and I checked that: the default output was byte-for-byte identical to before the change.

*Prompt for Challenge 3 (diversity penalty):* *"Describe a rule that penalizes a song's score if its artist is already in the top recommendations list. Also penalize repeated genres, but less."* The AI proposed a greedy re-rank: pick the best song, then re-score the rest, subtracting 1.0 per already-chosen song by the same artist and 0.5 per already-chosen song of the same genre, and repeat until k songs are chosen. A plain sort cannot do this, because each pick changes the scores of the rest.

**How does the pattern appear in your final code?**

- `ScoringMode`, `GENRE_FIRST`, `MOOD_FIRST`, `ENERGY_FOCUSED` and the `MODES` lookup table are in `src/recommender.py`.
- `score_song(user_prefs, song, mode)`, `max_score(user_prefs, mode)` and `recommend_songs(..., mode=..., diversity=...)` accept a mode.
- `src/main.py` has the switch: `python -m src.main --mode mood-first` and `--diversity`.

**What did you verify manually?**

- Default mode output is identical to the version before this change, and the 2 starter tests pass.
- Genre-first, mood-first and energy-focused give different rankings where expected: for the classical-at-full-blast profile, energy-focused finally puts Pulse Factory first instead of the calm classical song.
- Diversity check: for Chill Lofi, the second LoRoom song (Focus Flow) fell from #3 (3.89) to #5 (1.89) with both an artist and a genre penalty. For High-Energy Pop, Night Drive Loop (same artist as Sunrise City) was replaced by Storm Runner.
- I did not use a `git checkout -b` experiment branch, because the working tree already had uncommitted changes from earlier steps. Both modes were checked on the same tree instead.

*Student note: add your own reflection on whether the pattern felt too heavy or about right.*

---

## Challenge 4: Visual Summary Table

**Prompt used:** *"Suggest a way to use a library like tabulate or simple ASCII formatting to display my top recommendations. The table must include the reasons for each score."*

**What the AI suggested and generated:** Two options: the `tabulate` library, or plain ASCII drawing. We chose plain ASCII with `textwrap`, because the reasons column needs several lines per row and a custom renderer keeps those lines inside one bordered row without a new dependency. The new `format_table` and `_render` functions in `src/main.py` build the table, and a `--table` flag switches to it.

**What I verified:** The first version printed "- - genre match" and left the other reasons unbulleted, because the bullet logic was applied twice, so I simplified it to wrap each reason with `"- "` as the first-line indent. I then checked the table lines up for a profile with short reasons (High-Energy Pop) and one with nine reasons per song (Nostalgic 90s Listener), and that `--table` works with `--mode` and `--diversity`. The 2 starter tests still pass and the default list output is unchanged.
