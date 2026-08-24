# Music Recommendation Analytics Engine
A data-driven music recommendation system that uses human-curated playlist behavior to uncover meaningful relationships between songs and improve music discovery.

Built on **12.8M+ playlist records** across **231K+ playlists, 2.7M+ tracks, and 15K+ users**, the system uses playlist co-occurrence and **Jaccard similarity** to generate recommendations while reducing the popularity bias common in raw co-occurrence models.

The project combines a Python-based data pipeline, a normalized SQLite data warehouse, a precomputed recommendation engine, and an interactive Power BI dashboard designed for fast, user-driven music exploration.

## Demo

> **Interactive Power BI Recommendation Dashboard**
> Explore both cross-artist discovery and artist-specific recommendations generated from precomputed playlist similarity scores.

[Insert demo GIF / video preview here]

## Business Problem

Music streaming platforms need to surface recommendations that reflect listener intent, not simply overall track popularity.

Traditional co-occurrence approaches can over-recommend mainstream tracks because highly popular songs naturally appear across a large number of playlists. This project instead analyzes how users intentionally group songs within playlists and normalizes those relationships using Jaccard similarity.

The goal is to surface more contextually relevant recommendations that can support:

* Greater music discovery
* More diverse recommendations
* Reduced popularity bias
* Increased opportunities for listener engagement

## Tech Stack

**Languages & Data Processing:** Python | SQL
**Database:** SQLite
**Analytics & Visualization:** Power BI
**Data Architecture:** ETL | Relational Data Modeling | Data Warehousing
**Recommendation Modeling:** Playlist Co-occurrence | Jaccard Similarity
**Development:** Git | GitHub

## System Architecture & Data Pipeline

The system is built on a high-performance SQLite data warehouse containing **12.8M+ records** across **231K+ playlists**, **2.7M+ tracks**, and **15K+ users**, with data modeling and indexing designed to support efficient analytical queries and scalable similarity scores.

![Data Warehouse ERD](docs/MR%20Data%20Warehouse.drawio.png)

### Data Normalization & Canonicalization
Raw user-curated playlist data often suffers from text discrepancies (e.g., inconsistent capitalization, varied spacing, and duplicate string entries for identical tracks). 
* **ID Pooling:** Resolves data fragmentation by assigning unique identifiers to distinct tracks and artists.
* **Text Canonicalization:** Standardizes metadata fields before database insertion, guaranteeing that user-generated variations pool into the same relational entities.

---

## Mathematical Model: Jaccard Similarity

Relying purely on raw co-occurrence counts introduces a heavy popularity bias, where mainstream hits dominate recommendations simply because they appear everywhere. So, the engine implements Jaccard Similarity to normalize the intersection of track appearances relative to their total unique playlist volume.

The similarity between two items, $A$ and $B$, is calculated as:

$$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

Where:
* $|A \cap B|$ represents the number of playlists containing **both** tracks.
* $|A \cup B|$ represents the total unique playlists containing **either** track $A$ or track $B$.

By using the union as the denominator, the model penalizes the extremely popular tracks and elevates songs that share a high-proportion overlap with the seed track.

---

## Recommendation Pathways

To support different music discovery behaviors, the system is split into two distinct recommendation pathways:

### 1. Cross-Artist Discovery
* **Objective:** Surface new, diverse artists matching the target song without getting stuck in a single artist's discography.
* **Logic:** The query explicitly filters out the seed artist (WHERE artist != ?). This forces the Jaccard calculation to look outside the artist's catalog and find recommendations across the wider dataset.

### 2. Artist-Specific Recommendations
* **Objective:** Uncover pairings within a specific artist's discography.
* **Logic:** The query isolates the dataset strictly to the seed artist (WHERE artist = ?), allowing users to explore within a single discography.

---

## Preparing for Power BI: Backend Materialization

Computing Jaccard similarity matrices in real time across millions of track combinations would cause severe latency inside a live dashboard. To ensure quick responses inside Power BI, the backend was completely refactored into a pre-computed, optimized analytical reporting layer (`bi_track_similarities`).

* **Strategic Data Selection:** Applied a "Meaningful Track" threshold, isolating tracks appearing in >= 5 playlists.
* **Batch Processing:** Split a massive database query into small chunks of 500 tracks to prevent the system from running out of memory.
* **Database Tuning:** Optimized SQLite settings for faster data writing and automatically deleted temporary tables to save disk space.
* **Fast Visual Filtering:** Built targeted database indexes to drop query times, ensuring the Power BI dashboard responds instantly.

---

## Power BI Implementation

---

## Business Impact
