# Music Recommendation Analytics Engine

## Project Overview 
A music data analytics engine engineered to discover more human recommendations, inspired by how I like to find new music on spotify.

Instead of guessing what a song feels like based on clinical audio stats, this project taps into millions of real playlists built by actual people. By evaluating how songs are naturally grouped together globally, and using statistical leveling to filter out the noise of massive pop hits, the engine uncovers genuine song connections that capture a real mood rather than commercial popularity.

## System Architecture & Data Pipeline

The engine is built on a high-performance relational SQLite data warehouse containing **12.8M+ transaction rows** across **231K+ playlists**, **2.7M+ unique tracks**, and **15K+ users**. To eliminate data fragmentation and ensure sub-second query execution across a dataset of this scale, the pipeline utilizes a dedicated canonicalization framework and targeted database indexing.

![Data Warehouse ERD](docs/MR%20Data%20Warehouse.drawio.png)

### 1. Data Normalization & Canonicalization
Raw user-curated playlist data often suffers from text discrepancies (e.g., inconsistent capitalization, varied spacing, and duplicate string entries for identical tracks). 
* **ID Pooling:** Resolves data fragmentation by assigning unique, centralized identifiers to distinct tracks and artists.
* **Text Canonicalization:** Standardizes metadata fields before database insertion, guaranteeing that user-generated variations pool into the same relational entities.

---

## Mathematical Model: Jaccard Similarity

Relying purely on raw co-occurrence counts introduces a heavy popularity bias, where mainstream hits dominate recommendations simply because they appear everywhere. So, the engine implements **Jaccard Similarity** to normalize the intersection of track appearances relative to their total unique playlist volume.

The similarity between two items, $A$ and $B$, is calculated as:

$$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

Where:
* $|A \cap B|$ represents the number of playlists containing **both** tracks.
* $|A \cup B|$ represents the total unique playlists containing **either** track $A$ or track $B$.

By using the union as the denominator, the model penalizes hyper-popular tracks and elevates songs that share a high-proportion overlap with the seed track.

---

## Recommendation Pathways

To help users discover new artists while still allowing them to explore a specific song type, the system is split into two distinct execution pathways.

### 1. Cross-Artist Discovery
* **Objective:** Surface new, diverse artists matching the target song without getting stuck in a single artist's discography.
* **Logic:** The query explicitly filters out the seed artist (WHERE artist != ?). This forces the Jaccard calculation to look outside the artist's catalog and expose adjacent sonic subcultures across the wider dataset.

### 2. Artist-Specific Recommendations
* **Objective:** Uncover pairings within a specific artist's discography.
* **Logic:** The query isolates the dataset strictly to the seed artist (WHERE artist = ?), allowing users to explore within a single discography.

---

## Preparing for Power BI: Backend Materialization

Computing Jaccard similarity matrices on-the-fly across millions of track combinations would cause severe latency inside a live dashboard. To ensure quick responses inside Power BI, the backend was completely refactored into a pre-computed, optimized analytical reporting layer (`bi_track_similarities`).

* **Strategic Data Selection:** Applied a "Meaningful Track" threshold, isolating tracks appearing in >= 5 playlists.
* **Batch Processing:** Split a massive database query into small chunks of 500 tracks to prevent the system from running out of memory.
* **Database Tuning:** Optimized SQLite settings for faster data writing and automatically deleted temporary tables to save disk space.
* **Fast Visual Filtering:** Built targeted database indexes to drop query times, ensuring the Power BI dashboard responds instantly.

---

## Future Roadmap

* **Power BI Integration:** Connect the optimized SQLite data warehouse using an ODBC driver to establish a high-performance relational Star Schema.
* **Spotify-Style UI/UX Layout:** Construct an immersive dark-mode analytics canvas featuring an interactive "Seed Track" search engine and a real-time recommendation matrix.
* **Dynamic Analytics Visuals:** Implement supporting KPI cards and distributions to display genre overlaps, contextual popularity scores, and playlist volume tracking.
* **Performance Validation:** Run end-to-end user-interaction testing to guarantee instant visual rendering without load-wheel lag.
