# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

A small, rule-based music recommender. It matches songs to a listener's "vibe".

---

## 2. Intended Use  

**Goal / Task:** Suggest the top 5 songs from a small catalog that fit a listener's taste. It does not predict what a real person will play next. It only ranks songs by how well they match a profile.

**Intended use**
- Classroom learning about how recommenders work.
- Trying out scoring rules and seeing the results.
- Explaining each pick with clear reasons.

**Assumes the user can describe their taste with four things:** a favorite genre, a favorite mood, a target energy from 0 to 1, and whether they like acoustic music.

**Not intended for**
- Real music apps or real listeners.
- Judging artists or songs.
- Deciding who gets promoted or paid.
- Any case where a wrong pick could hurt someone.

---

## 3. How the Model Works  

The recommender works like a judge giving every song a score out of 5 points, then handing back the highest-scoring songs.

You tell it your taste: a favorite genre, a favorite mood, how energetic you want the music to feel (on a scale from 0 to 1), and whether you like acoustic sounds. For each song in the catalog it awards points:

- **2 points** if the song's genre is your favorite genre.
- **1 point** if the song's mood is your favorite mood.
- **Up to 1.5 points for energy.** The closer the song's energy is to what you asked for, the more points it gets. A song that is too calm earns fewer points than one that is just right, and so does a song that is too intense, so it is about being close rather than being high or low.
- **Up to 0.5 points for acoustic feel.** If you like acoustic music, songs with a more acoustic sound earn more. If you don't, more electronic songs earn more.

Once every song has a score, the system sorts them from best to worst and shows the top five. Each one comes with its reasons, such as "genre match" or "energy closeness", so you can see exactly why it was picked.

Compared with the starter code, which returned the first few songs unchanged, this version actually reads the song file, scores each song, and ranks them. I also added 8 songs to the catalog and made the energy score reward closeness instead of simply high or low values.

---

## 4. Data  

- The catalog is `data/songs.csv`. It has **18 songs**.
- The first 10 came with the project. I added 8.
- Each song has a title, artist, genre, mood and five numbers: energy, tempo, valence, danceability and acousticness.
- Five advanced fields were added in the challenge: popularity (0-100), release decade, three mood tags, instrumentalness and language. Profiles can use them, but the six main test profiles do not.
- Genres: 15 in total, including pop, lofi, rock, jazz, hip hop, classical, country, r&b, metal, reggae, edm and blues.
- Moods: 14 in total, including happy, chill, intense, moody, romantic and melancholic.
- All songs, artists and numbers are made up.

**Limits**
- Only lofi (3 songs) and pop (2) repeat. Every other genre has one song.
- The catalog is tiny.
- It has no lyrics, language, year, or artist popularity.
- It leans toward Western pop-style genres.
- There are no real listening records, so nothing is learned from other users.

---

## 5. Strengths  

- **It separates very different tastes well.** Chill Lofi and Deep Intense Rock share no songs.
- **Its picks usually match my ear.** Sunrise City tops the happy pop list. Library Rain tops the chill lofi list. Storm Runner tops the rock list.
- **It explains itself.** Every song comes with reasons, like "genre match (+2.0)".
- **The energy rule is fair.** It rewards songs that are close to the target, not just higher or lower.
- **It is easy to change.** The weights are simple numbers, so I could test a new setup quickly.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly.

**Weakness found: exact genre and mood labels can outweigh what the listener actually asked for.** A genre match is worth 2 points and a mood match 1 point, while energy can only earn up to 1.5 points, so a song with the right labels wins even when its energy is far off. In the "Classical at Full Blast" test, a user asked for very high energy (0.95) and was still given the calmest song in the catalog (energy 0.18) at number one, because it was the only classical and peaceful song. The same thing happened to the blues listener who wanted energy 0.9. This also treats users unevenly: a lofi fan has three lofi songs that can earn the genre points, while nearly every other genre has just one song, so those listeners get one strong result and then filler. The system also ignores `valence` (how positive a song sounds), so it cannot tell dark music from upbeat music at the same energy, and its catalog of 18 hand-made songs is far too small to say anything about real taste.

---

## 7. Evaluation  

How I checked whether the recommender behaved as expected.

### Profiles tested

Six profiles, run with `python -m src.main`: **High-Energy Pop** (pop, happy, energy 0.8), **Chill Lofi** (lofi, chill, 0.4, likes acoustic), **Deep Intense Rock** (rock, intense, 0.9), and three adversarial ones meant to trick the scoring: **Sad but Energetic** (blues, melancholic, 0.9), **Genre Not in Catalog** (bossa nova, happy, 0.5, likes acoustic) and **Classical at Full Blast** (classical, peaceful, 0.95, likes acoustic). I also ran one experiment: halving the genre weight and doubling the energy weight.

### What surprised me

- **Gym Hero keeps showing up.** It appeared in four of the six lists, including for a user who only asked for happy pop. In plain terms: Gym Hero is a pop song, so it gets the full genre points a pop fan asks for, and it is very energetic, so it also scores well for anyone who wants lively music. The system never checks whether the song feels happy or like a workout track. It only counts "is it pop?" and "is it close to my energy?", and Gym Hero says yes to both. A song that really is happy but is labeled "indie pop" (Rooftop Lights) gets no genre points at all because the label is not exactly "pop", so it ranks lower even though it feels closer to what the user wanted.
- **The calmest song won a high-energy request.** Moonlit Sonata Remix (energy 0.18) was number one for the user who asked for 0.95, just because its genre and mood matched.
- **Confident results with no good match.** For the bossa nova user, no song could earn genre points, the best score was only 2.28, and the output still looked as sure of itself as any other.
- **The weight experiment helped some users and not others.** With energy doubled and genre halved, Rooftop Lights moved above Gym Hero for the pop user and the high-energy songs got much closer to the classical and blues winners. The two Chill Lofi leaders swapped on a 0.01 difference, which is not meaningful.

### Comparing each pair of profiles

1. **Pop vs. Lofi:** No songs in common. Pop wants lively, electronic songs and lofi wants slow, acoustic ones, so the lists are opposites on both energy and acoustic feel, which is exactly what those two users should see.
2. **Pop vs. Rock:** They share Sunrise City and Gym Hero. Both want high energy and non-acoustic music, so overlap makes sense, and rock moves Storm Runner to the top because of its rock genre and intense mood.
3. **Pop vs. Sad but Energetic:** Only Gym Hero is shared. The blues listener gets one blues song at the top and then just the loudest songs in the catalog, while the pop listener gets pop and happy songs.
4. **Pop vs. Bossa Nova:** They share Rooftop Lights and Sunrise City because both want "happy". The bossa nova user, who wants medium energy and acoustic sounds, also gets Dusty Porch Swing, Coffee Shop Stories and Focus Flow, which are calmer than anything in the pop list.
5. **Pop vs. Classical at Full Blast:** Only Gym Hero is shared. The classical user's number one is a very calm piano-style song, nothing like the lively pop list, which comes from the labels and not from the energy they asked for.
6. **Lofi vs. Rock:** No overlap, and the biggest contrast in the test: low energy and acoustic against very high energy and electronic. This is the clearest evidence that the scoring really separates tastes.
7. **Lofi vs. Sad but Energetic:** No overlap. Rainy Window Blues (energy 0.38, quite acoustic) feels like it would fit the lofi list, but it only appears for the blues user because it matches that genre and mood, which shows how much the labels matter.
8. **Lofi vs. Bossa Nova:** They share Coffee Shop Stories and Focus Flow. Both users want calm, acoustic-leaning music, so the overlap makes sense, and the bossa nova user's higher energy target (0.5) pulls in Dusty Porch Swing.
9. **Lofi vs. Classical at Full Blast:** No overlap. Both like acoustic sounds but want opposite energy, and the classical user's top song is far calmer than their request, so only the acoustic taste is honored.
10. **Rock vs. Sad but Energetic:** Four of five songs are the same (Storm Runner, Gym Hero, Pulse Factory, Iron Tide). Both want energy 0.9 and no acoustic sound, so once the labels are out of the way the lists are almost identical. The only real difference is Rainy Window Blues at the top for blues.
11. **Rock vs. Bossa Nova:** Only Sunrise City is shared. One wants very loud and electronic music and the other wants medium and acoustic, so they differ as expected.
12. **Rock vs. Classical at Full Blast:** Four of five songs are shared. After Moonlit Sonata Remix gets in on its labels, the rest of the classical list is just the highest-energy songs, which is the rock list. That shows energy is the only thing doing any work after the first result.
13. **Sad but Energetic vs. Bossa Nova:** No overlap. A high-energy blues fan and a medium-energy acoustic fan want very different music, so there is nothing to share.
14. **Sad but Energetic vs. Classical at Full Blast:** Four of five songs are shared (Pulse Factory, Gym Hero, Storm Runner, Iron Tide). Both lists have one song that wins on genre and mood labels, followed by the same loud songs, so the system treats these two very different users the same after the first slot.
15. **Bossa Nova vs. Classical at Full Blast:** No overlap. Medium energy and acoustic against very high energy: the bossa nova list is mellow and the classical list is led by a calm outlier and then loud songs, so the profiles are testing different things and the output reflects that.

**Do the results make sense overall?** Mostly yes. Profiles with clearly different tastes get clearly different lists, and profiles with similar energy targets get similar fill. The weak spots are the ones above: labels beat energy, and the system never admits when nothing matches well.

---

## 8. Future Work  

1. **Use `valence`.** Then it can tell a dark song from an upbeat one with the same energy.
2. **Give partial credit to similar labels.** "Indie pop" should count a little for "pop". "Aggressive" should count a little for "intense".
3. **Be honest about weak matches.** If the best score is low, say so.
4. **Mix up the top 5.** Avoid filling the list with near copies of the same song.
5. **Allow more than one taste.** A user could pick two genres or a range of energy.

---

## 9. Personal Reflection  

**Biggest learning moment.** A recommender is mostly a set of choices about what to count and how much each thing is worth. My weights decided everything. Genre was worth 2 points and energy at most 1.5. So a calm classical song won a request for very high energy. I only saw this because I built "adversarial" profiles on purpose. The normal profiles all looked fine.

**How AI helped, and when I double-checked it.** The AI helped me plan the scoring rule, write the code, add songs, and draft the docs. It was fast at the boring parts. But I had to check its work:
- Its hand-calculated scores were a little off from the real program output (4.86 vs 4.85). The ranking was right, but I used the program's numbers in the docs.
- It wrote a wrong number in my README (a score of 1.44 that the program printed as 1.42). It also claimed Gym Hero showed up in five of six lists, and the real answer was four. I caught both by comparing against the terminal output.
- The starter `main.py` import did not work with the `python -m src.main` command in the README. Running it showed the problem, and we fixed it.

The lesson: trust the program's output over anyone's explanation of it, including the AI's.

**What surprised me.** Four simple rules felt like real recommendations. "Because: genre match, mood match, energy close" made the list feel smart, even though nothing is learned. The reasons list did a lot of that work. It also made the mistakes easy to see. The Gym Hero problem was obvious as soon as the reasons were printed.

**What I would try next.**
- Use `valence` so dark and upbeat songs at the same energy can be told apart.
- Give partial credit to similar labels, such as "indie pop" for "pop" and "aggressive" for "intense".
- Show a warning when even the best score is low.
- Add many more songs, so every genre has more than one.

This also changed how I see music apps. A "good" pick may just be the one that matched the labels the app cares about. A real app has far more data than mine, but the same kind of choices can still hide bias.
