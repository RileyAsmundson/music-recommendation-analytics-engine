# Music Recommendation Analytics Engine

## Project Overview 
A music data analytics engine engineered to discover more human recommendations, inspired by the atmospheric mood of "About You" by The 1975.

Instead of guessing what a song feels like based on raw audio stats, this project taps into how real people group music by searching through thousands of user-created playlists with titles like "songs like [starting song]". By leaning on real human curation, the engine finds the songs that naturally sit alongside your favorites, making the recommendations feel truly personalized.


## Project Status 
Initially, this repository was built to ingest live playlist data directly from the Spotify Web API. However, due to platform-wide developer access changes regarding unowned public playlists, hitting severe API rate limits, and the lack of cultural/emotional context in raw acoustic metrics, the project's data architecture underwent a strategic pivot:
  * Old Approach (Archived): Utilizing live OAuth2 pipelines to scrape public user playlists. This proved unscalable due to Sandbox mode permission limitations (`403 Forbidden` errors on non-owned assets).
  * Current Approach: Transitioning to an offline data science model using large-scale, human-curated Spotify playlist datasets (via Kaggle).
