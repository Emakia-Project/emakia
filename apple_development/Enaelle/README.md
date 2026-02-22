# Enaelle

**Enaelle** is an iOS app from the [Emakia](https://github.com/Emakia-Project/emakia) project. It fetches social media posts (Twitter, Reddit, Facebook), classifies them for toxicity and harassment on-device with Core ML, and lets you browse results in separate tabs. Predictions are sent to the EmakiaTech backend for analytics.

---

## Features

- **Multi-platform feed**: Fetch posts from **Twitter**, **Reddit**, or **Facebook** via EmakiaTech APIs
- **Search & filters**: Topic search, result limit (10–500), optional “sensitive only” filter
- **On-device classification**: Core ML text classifier (`ToxicityTextClassifier`) labels each post as **neutral** or **harassment** with confidence scores
- **Tabbed UI**:
  - **All Tweets**: Full list with harassment indicator
  - **Sensitive**: Neutral posts with confidence
  - **Toxicity**: Harassment posts with confidence
- **Backend sync**: Each classification is sent to the EmakiaTech prediction API for storage and analysis

---

## Requirements

- **Xcode** (current version)
- **iOS 18.0+**
- **Swift 5**
- **Core ML model**: `ToxicityTextClassifier.mlmodel` (or compiled `.mlmodelc`) in the app bundle

---

## Project structure

```
Enaelle/
├── Enaelle/
│   ├── EnaelleApp.swift          # App entry point
│   ├── Views/
│   │   ├── ContentView.swift     # Main UI: platform picker, search, tabs
│   │   └── TweetCard.swift      # Post card (author, content, media, metrics)
│   ├── ViewModels/
│   │   └── TweetViewModel.swift # Fetch, classify, send predictions
│   ├── Models/
│   │   ├── Tweet.swift          # Tweet/post model + API coding keys
│   │   ├── SocialPlatform.swift # Twitter / Reddit / Facebook + API endpoints
│   │   └── PredictionRow.swift  # Payload for prediction API
│   ├── Services/
│   │   └── ToxicityClassifer.swift # Core ML wrapper + ToxicityResult
│   └── Assets.xcassets
├── EnaelleTests/
├── EnaelleUITests/
└── README.md
```

---

## Setup

1. **Clone** the repo (or open from the parent `emakia-system` / `emakia` repo).
2. **Open** `Enaelle.xcodeproj` in Xcode.
3. **Add the Core ML model** (if not already in the project):
   - Ensure `ToxicityTextClassifier.mlmodel` is in the **Enaelle** target (Xcode compiles it to `.mlmodelc`).
   - The app loads it by name: `ToxicityTextClassifier` with extension `mlmodelc`.
4. **Build and run** on a simulator or device (iOS 18+).

No extra dependencies; the app uses only SwiftUI, Foundation, Core ML, and NaturalLanguage.

---

## API endpoints (EmakiaTech backend)

The app expects these endpoints (configured in `SocialPlatform.swift` and `TweetViewModel.swift`):

| Purpose        | URL                                                                 |
|----------------|---------------------------------------------------------------------|
| Tweet cascade  | `https://emakiatech-api-b6fc087f7f4f.herokuapp.com/api/tweet-cascade` |
| Reddit cascade | `https://emakiatech-api.herokuapp.com/api/reddit-cascade`            |
| Facebook cascade | `https://emakiatech-api.herokuapp.com/api/facebook-cascade`       |
| Send prediction | `https://emakiatech-api-b6fc087f7f4f.herokuapp.com/api/prediction` |

**Tweet cascade** query parameters: `topic`, `limit`, and optionally `sensitive_filter=true`.

**Prediction** payload (JSON): `tweet_id`, `text`, `prediction`, `score`, `model_version` (e.g. `"CoreML_v1"`).

---

## Usage

1. Choose **Twitter**, **Reddit**, or **Facebook**.
2. Enter a **search topic** and set **limit** (and optionally **Show Sensitive Only**).
3. Tap **Fetch Data**. Posts load and are classified in the background (“Classifying tweets with CoreML...”).
4. Switch tabs to view **All**, **Sensitive** (neutral), or **Toxicity** (harassment). Each card shows author, content, media, and classification confidence where relevant.

---

## License & attribution

Part of the **Emakia** machine learning project.  
Created by **Corinne David** (July 2025).

For the broader Emakia setup and data pipeline, see the main [emakia](https://github.com/Emakia-Project/emakia) repository.

