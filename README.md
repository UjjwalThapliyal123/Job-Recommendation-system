```markdown
## JOB RECOMMENDATION SYSTEM

A high-performance Natural Language Processing (NLP) recommendation pipeline built and trained on a curated dataset of 30,000
job records. The system utilizes optimized text vectorization and matrix mathematics to surface relevant career opportunities based on semantic similarity scoring.

To deliver sub-second production latency, the system implements an offline-precomputation and online-inference split architecture.
By pre-calculating and serializing heavy text matrices,it bypasses runtime computing overhead and allows users to search and filter the 30k corpus instantly.

## Core Architecture & Engineering Highlights

- ** Decoupled Optimization Matrix **: Isolates the heavy training phase from the application layer by saving static text profiles into
pre-cached, serialized structures (`jobs_clean.pkl`, `job_embeddings.npy`, and `tfidf_matrix.npz`).
- **Sub-Second Search Latency**: Loads a persistent `tfidf_vectorizer.pkl` to transform raw user search queries or skill inputs into a sparse
term-frequency vector, running Cosine Similarity calculations against all 30,000 records in milliseconds.
- **Persistent Geolocation Caching**: Features a localized caching layer (`geo_cache.pkl`) designed to store coordinate lookups, optimizing location-based
 job matching without introducing high-latency external API dependencies.
- **Production Code Isolation**: Engineered with a clean separation of concerns, separating the core text preprocessing and mathematical matching logic (`main.py`)
 from the interactive web deployment front-end (`app.py`) built with Streamlit.

# 🛠️ Technical Stack

- **Core Language**: Python (`main.py`, `app.py`)
- **Vector & Matrix Mathematics**: NumPy (`.npy`), SciPy Sparse Matrix (`.npz`), Pandas
- **Natural Language Processing**: Scikit-Learn (TF-IDF Vectorization), Cosine Similarity Matrix
- **Data Serialization**: Pickle (`.pkl` for dataframes, models, and local caches)

                    ┌───────────────────┐
                    │  Job Dataset      │
                    │   (30K Records)   │
                    └─────────┬─────────┘
                              │
                              ▼
                  ┌─────────────────────┐
                  │ Data Cleaning & NLP │
                  └─────────┬───────────┘
                            │
                            ▼
               ┌──────────────────────────┐
               │ TF-IDF Vectorization     │
               │ Feature Extraction       │
               └──────────┬───────────────┘
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
 jobs_clean.pkl   tfidf_matrix.npz   job_embeddings.npy

                          │
                          ▼
               ┌──────────────────────┐
               │ Recommendation Engine│
               │ Cosine Similarity    │
               └──────────┬───────────┘
                          │
                          ▼
                  Streamlit Frontend

## 📁 Repository Structure & File Manifest

```text
├── Backend/Artifacts/
│   ├── geo_cache.pkl          # Cached geolocation coordinate lookups for performance optimization
│   ├── job_embeddings.npy     # Dense matrix containing pre-computed job text embeddings
│   ├── jobs_clean.pkl         # Cleaned, tokenized, and preprocessed 30k job dataframe
│   ├── tfidf_matrix.npz       # Compressed sparse SciPy matrix representation of the job corpus
│   └── tfidf_vectorizer.pkl   # Serialized Scikit-Learn TF-IDF vectorizer object
│
├── Frontend/
│   └── app.py                 # Streamlit web-based UI application for user interaction
│
├── Notebook/
│   ├── JOB_NB_1.ipynb         # Data exploration, cleaning, and preprocessing notebook
│   ├── JOB_NB_2.ipynb         # Feature engineering, vectorization, and embedding generation
│   └── JOB_NB_3.ipynb         # Recommendation pipeline testing, matching logic evaluation
│
├── .gitignore                 # Exclusion rules for virtual environments, caches, and large files
├── README.md                  # Project documentation (this file)
├── main.py                     # Main application layer entry point
