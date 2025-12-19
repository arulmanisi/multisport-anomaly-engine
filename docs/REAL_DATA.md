# Working with Cricsheet data locally

Cricsheet provides ball-by-ball match data as downloadable ZIP files. We consume these manually downloaded archives for training and evaluation.

## Directory layout
- `data/raw/cricsheet/` — raw downloads (unzipped)
  - `t20/` — JSON files for T20 matches
  - `odi/` — JSON files for ODI matches
  - `test/` — JSON files for Test matches
- `data/processed/` — space for any cleaned/featurized outputs you derive

## Download steps
1. Visit the Cricsheet downloads page and grab the JSON ZIP for each format you need (e.g., T20, ODI).
2. Unzip each archive into the matching folder, e.g.:
   - `data/raw/cricsheet/t20/`
   - `data/raw/cricsheet/odi/`
   - `data/raw/cricsheet/test/`
3. (Optional) Download the Cricsheet Register CSV for consistent player IDs and store it alongside the raw data if you plan to align identities.

We do **not** scrape or automate downloads; use the official ZIPs provided by Cricsheet.
