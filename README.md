# Music Recommendation Analytics Engine

## Project Overview 
A data-driven recommendation system designed to improve music discovery by leveraging human-curated playlist behavior instead of traditional audio-feature-based models. By analyzing how millions of users group songs into playlists, the system surfaces context-aware recommendations that better reflect listener intent, ultimately increasing engagement and session time on streaming platforms.

* **Business Problem:** 
Music streaming platforms struggle to deliver contextually relevant recommendations that capture user intent, often resulting in repetitive or irrelevant suggestions. This leads to reduced user engagement, shorter listening sessions, and increased reliance on manual search for music discovery.

## System Architecture & Data Pipeline

The system is built on a high-performance SQLite data warehouse containing **12.8M+ records** across **231K+ playlists**, **2.7M+ tracks**, and **15K+ users**, with data modeling and indexing designed to support efficient analytical queries and scalable similarity computations.

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

## Key Insights
This analysis reveals several key patterns in how users organize and discover music:
  - Human-curated playlists encode implicit context (mood, activity, niche taste) that is not captured by traditional audio features
  - Raw co-occurrence heavily favors popular tracks, requiring normalization (Jaccard) to surface more meaningful relationships
  - Filtering for “meaningful tracks” (≥5 playlists) significantly improves recommendation quality by removing noise from sparse data
  - Cross-artist filtering promotes diverse music discovery by surfacing relevant songs beyond a single artist’s catalog

---

## Recommendation Pathways

To support different music discovery behaviors, the system is split into two distinct recommendation pathways:

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

## Power BI Implementation

---

## Business Impact
