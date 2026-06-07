Job Recommendation Engine
A high-performance Natural Language Processing (NLP) recommendation pipeline built and trained on a curated dataset of 30,000 job records. The system utilizes optimized text vectorization and matrix mathematics to surface relevant career opportunities based on semantic similarity scoring.

To deliver sub-second production latency, the system implements an offline-precomputation and online-inference split architecture. By pre-calculating and serializing heavy text matrices, it bypasses runtime computing overhead and allows users to search and filter the 30k corpus instantly.

Core Architecture & Engineering Highlights
Decoupled Optimization Matrix: Isolates the heavy training phase from the application layer by saving static text profiles into pre-cached, serialized structures (jobs_clean.pkl, job_embeddings.npy, and tfidf_matrix.npz).

Sub-Second Search Latency: Loads a persistent tfidf_vectorizer.pkl to transform raw user search queries or skill inputs into a sparse term-frequency vector, running Cosine Similarity calculations against all 30,000 records in milliseconds.

Persistent Geolocation Caching: Features a localized caching layer (geo_cache.pkl) designed to store coordinate lookups, optimizing location-based job matching without introducing high-latency external API dependencies.

Production Code Isolation: Engineered with a clean separation of concerns, separating the core text preprocessing and mathematical matching logic (main.py) from the interactive web deployment front-end (app.py) built with Streamlit.

Technical Stack & File Manifest
Core Language: Python (main.py, app.py)

Vector & Matrix Mathematics: NumPy (.npy), SciPy Sparse Matrix (.npz), Pandas

Natural Language Processing: Scikit-Learn (TF-IDF Vectorization), Cosine Similarity Matrix

Data Serialization: Pickle (.pkl for dataframes, models, and local caches)
