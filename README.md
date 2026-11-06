# Emakia

**Building Enaëlle: an app that filters harassment before you ever see it, on your own device.**

People targeted by coordinated harassment (journalists, elected officials, LGBTQ+ and minority public figures) currently have two options: read everything, or hand their inbox to a platform's moderation system and accept whatever it decides. Enaëlle is a third: the filter runs on your phone, you set it, and nothing you receive is sent to anyone else to be judged.

Building it turned out to require something that did not exist. So we built that too, and we are sharing it.

## Two things live here

### Enaëlle: the goal

An iOS app that filters what reaches you, on-device. No message content leaves the phone. Receiver-side, so the person being targeted decides what they see rather than a platform deciding for them.

**Status:** prototype on our own devices, not yet released. It needs reliable classifiers for each language first, which is what the work below produces. Code: `apple_development/`

### The validation system: the prerequisite, and the part you can use

A receiver-side filter is only as trustworthy as the labels behind it and the evaluation of the model's predictions. When we went to train Enaëlle's classifiers we found that the available corpora disagreed with each other, that single-model labelling inherited that model's blind spots, and that nothing in the field would tell us how wrong either our labels or our predictions were.

So we built a validation system. Give it a corpus and it returns verdicts from a panel of five independent LLM judges (OpenAI, Google Gemini, xAI Grok, Mistral and Anthropic Claude). Give it your model's predictions as well and it tells you where model and panel diverge, broken down by how much the judges agreed. Either way you get an explicit contested band instead of a forced answer, and a provenance record tying every number to the exact texts that produced it.

We use it to train and evaluate three versions of each on-device classifier, built on three label sets from the same texts:

| Label set | Meaning |
|---|---|
| LLM0 | the original human labels from published research datasets |
| LLM3 | harassment when at least 3 of the 5 judges agree |
| LLM4 | harassment when at least 4 of the 5 judges agree |

We needed it. Others building classifiers need it too. It is MIT licensed and documented below: `evaluate-COREML-prediction/eval-llm/`

## Languages

| Language | Status | Where |
|---|---|---|
| English | done: 78K-post corpus judged by the panel | this repository |
| French | done: 24,251-post corpus relabelled by the five-judge panel | [Emakia-Project/french-judge-panel](https://github.com/Emakia-Project/french-judge-panel) |
| Spanish | in progress: 29,491 posts being labelled (November 2026) | to be published |
| English + French + Spanish | planned: one trilingual on-device classifier, evaluated per language on new posts | to be published |

## Why the contested band matters for an app

This is not an academic point. It is the reason Enaëlle is built the way it is.

Around 13% of our corpus lands in the 2 to 3 vote band, where the five judges do not agree. That band is where counter-speech, reclaimed slurs and quoted abuse concentrate. A journalist reproducing a threat they received looks identical to a threat under a naive filter.

An app that removes those posts silences the people it is meant to protect.

Enaëlle's output is binary: a message lands under Harassment or under Neutral. What is not binary is the path to that decision. Agreement level, per-tier signals and the model's own confidence all feed a threshold, and where that threshold sits decides a contested message. Getting it right cannot be settled from a corpus alone; it needs real usage. Once there is user data, the threshold will be adjusted to how each person wants their own inbox filtered. Posts where the judges agree are handled by the general model; the subjective band is where the user's own choices decide.

Related design choices, all measured rather than assumed:

- **Refusals are recorded, not coerced.** When a judge declines to answer, that is stored as an abstention with the provider's reason. It never silently becomes a "safe" verdict.
- **Identity terms never trigger a match.** Crossing attack verbs with protected-class terms is the best-documented source of false-positive bias in toxicity classifiers (Dixon et al., 2018). Our filter configuration excludes identity terms from the query and matching layers entirely, and a test asserts that none reaches a compiled query. A filter that flags posts for mentioning a community is useless to that community. Not yet built: using those terms on the measurement side. Differential flag rate by identity term is computable from what we already store; a true per-group false-positive rate needs a human-labelled subset we do not have yet.
- **Everything is traceable.** Each run records a SHA-256 fingerprint of the exact text set it saw, so any number can be traced back to its data months later.

## What the measurements show

French civic posts from X, September 2026. 8,436 posts, five judges, consensus at k ≥ 3 of 5.

| Stream | Selects for | n | Positive rate |
|---|---|---|---|
| Neutral baseline | mundane topics, non-reply | 1,486 | 3.5% |
| Topic | 12 civic subjects | 1,795 | 13.1% |
| Lexicon-seeded | abuse vocabulary, 5 tiers | 1,967 | 28.5% |
| Account, lexicon negated | roster mentions minus abuse terms | 1,207 | 28.3% |
| Reply-directed | replies to a sampled account roster | 1,981 | 48.4% |

Two results that shape the app:

- **A keyword filter is not enough.** The same accounts, with roughly 25 abuse terms negated from the query, still return 28.3% harassment against 48.4% unfiltered. Simple blocklists, which is what most people are offered today, miss well over half of it.
- **Abuse is topic-dependent.** Within the topic stream, identity subjects draw far more abuse than policy subjects: LGBT 64.0%, racism 56.2%, feminism 44.0%, secularism 44.0%, against ecology 10.4%, pensions 10.4%, economy 10.2%, education 6.5%. Same collection method, same week, same query shape (n ≈ 50 per subject, so intervals are wide). The people who most need a filter are the ones who receive the most.

The relabelling of the merged 24,251-post French training corpus is in [french-judge-panel](https://github.com/Emakia-Project/french-judge-panel).

## Repository layout

```
emakia/
├── apple_development/             # Enaëlle: iOS app, CoreML on-device models
│
├── evaluate-COREML-prediction/    # the validation system
│   └── eval-llm/                  #   five-judge panel, consensus, run store
├── LLM-RAG-Toxicity-Evaluator/    # per-provider judge integrations
├── LLM_FN_Analysis/               # false-negative analysis
├── Backend-google-EmakiaEval/     # evaluation backend service
│
├── google_cloud_server_development/
│   ├── text_classifier_training/  # CoreML / Vertex AI training pipelines
│   └── gcloud-toolkit-recent-search/
├── load-Neo4j/                    # propagation-cascade analysis
└── data/                          # not tracked; see Data below
```

### The validation system: `evaluate-COREML-prediction/eval-llm/`

| File | Does |
|---|---|
| `label_corpus.py` | Runs the five-judge panel over a corpus CSV |
| `run_store.py` | Append-only run storage. Nothing is ever overwritten |
| `recompute_consensus.py` | Consensus from a stored run, no API calls |
| `vision_media.py` | Gemini Vision over images and video |
| `load_vision.py` | Joins text panel, vision, and platform flag |
| `sanity.py` | Assertions that fail at the point an assumption is made |
| `compare_agreement.py` | Inter-judge agreement between two prompt versions |

## Using the validation system

You do not need Enaëlle to use this. It takes any corpus.

```
git clone https://github.com/Emakia-Project/emakia.git
cd emakia/evaluate-COREML-prediction/eval-llm

python3 -m venv env && source env/bin/activate
pip install -r requirements.txt
```

Set keys for whichever judges you want:

```
# .env  (never commit this file)
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
MISTRAL_API_KEY=...
OPENAI_API_KEY=...
XAI_API_KEY=...
```

Your corpus is a CSV with `id, source, text, label`. Leave `label` empty if you have no gold labels; that is the normal case, and the one this exists for.

```
# check every judge answers before spending anything
python label_corpus.py --preflight

# cost estimate and corpus fingerprint, no API calls
python label_corpus.py --corpus data/mycorpus.csv --estimate

# 20-row smoke test
python label_corpus.py --corpus data/mycorpus.csv --n-rows 20

# full run
python label_corpus.py --corpus data/mycorpus.csv

# consensus, from stored results, no API calls
python recompute_consensus.py --run <RUN_ID> --corpus data/mycorpus.csv
```

Every run writes `runs/<run_id>/` with a manifest, the raw judge responses, and a corpus fingerprint. Runs never overwrite each other, and resuming against a different text set is refused.

**Run time.** Provider rate limits set the pace: a five-judge run over about 25,000 to 30,000 texts takes from several days to two weeks on standard API plans. Higher-tier plans shorten it.

### Vision

```
python vision_media.py --manifest media_local/manifest.jsonl --estimate
python vision_media.py --manifest media_local/manifest.jsonl --n 25
python vision_media.py --manifest media_local/manifest.jsonl
```

Images, video and animated GIFs. Archive media locally first: platform media URLs expire, and a link stored today may be dead next week. We lost an entire media evaluation to this before we learned it.

### Prompt versions

Two prompts, used asymmetrically.

| | Criterion | Applied to |
|---|---|---|
| v1 | Does the text contain harassment? | Text panel |
| v2 | Does the content target a person or identifiable group? | Vision |

"Contains" conflates depicting abuse with committing it. Tolerable in text, severe in images: a press photograph of a protest, or a screenshot of abuse being reported, contains harassment while targeting no one. Under v1 our vision judges agreed with each other on press photographs and were wrong together: high agreement on an incorrect verdict, which agreement alone cannot detect.

Both prompts are kept verbatim so the ablation can be run over the same corpus.

## Data

`data/`, `raw/`, `media_local/` and `.env` are excluded from version control.

Posts we collect from platforms are released as post identifiers and derived labels only, never post text or media, consistent with platform developer agreements. Texts from published research datasets are shared only where the original license allows it; otherwise we link to the original dataset. Aggregate statistics, model artifacts, filter configurations and query definitions are releasable in full.

## Research

- **"A Multi-Model Framework for Civic Content Moderation"** (David, Karekar, Teasley). Accepted for oral presentation at AIVR 2026, Kobe. To appear in the AIVR 2026 proceedings, Springer Smart Innovation, Systems and Technologies (SIST).
- Further papers in preparation: the evaluation defects this pipeline was rebuilt to fix, the corpus audit run on the corrected version, and the English, French and Spanish extension.

Collaboration with the NLP programme at Montclair State University.

Lexical resources: HurtLex, LDNOOBW. Used rather than hand-curating slur lists, so provenance is citable.

## Related repositories

- [french-judge-panel](https://github.com/Emakia-Project/french-judge-panel): French relabelling pipeline with the five-judge panel, LLM0 / LLM3 / LLM4 label sets and CoreML training.
- [hackathon_emakia](https://github.com/Emakia-Project/hackathon_emakia): projects from hackathons.

## Contributing

Contributions welcome. Issues tagged `good first issue` are the place to start. Emakia is also listed on [For Good First Issue](https://forgoodfirstissue.github.com/).

Most useful right now:

- **Unifying the pipelines.** English and French currently have separate code. A single pipeline for English, French and Spanish, with automated checks at every step, is in progress and will be published here.
- **Open local judges.** The panel depends on commercial APIs today. Support for locally run open models would remove that.
- **Rate-limit handling.** Provider throttling can still surface as an abstention rather than a retry in the older code.
- **Android.** The on-device classifier is iOS-only.

Please open an issue before starting anything substantial.

## About

[Emakia](https://emakia.org) is a US 501(c)(3) nonprofit building open-source AI safety tools for civic content moderation, with a focus on protecting public servants, LGBTQ+ individuals and minority communities from coordinated harassment.

The goal is Enaëlle. The validation system is what we had to build to get there, and what we are giving away.

MIT licensed. See [LICENSE](LICENSE).
