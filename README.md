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

## Future Roadmap

* **Power BI Visualization Dashboard:** Developing a visual layer to map out track clusters, network graphs of shared playlist co-occurrences, and interactive similarity score distributions.

