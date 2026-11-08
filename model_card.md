# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
