# Emakia

**Building Enaëlle: an app that filters harassment before you ever see it, on your
own device.**

People targeted by coordinated harassment — journalists, elected officials, LGBTQ+ and
minority public figures — currently have two options. Read everything, or hand their
inbox to a platform's moderation system and accept whatever it decides. Enaëlle is a
third: the filter runs on your phone, you set it, and nothing you receive is sent to
anyone else to be judged.

Building it turned out to require something that did not exist. So we built that too,
and we are sharing it.

---

## Two things live here

### Enaëlle — the goal

An iOS app that filters what reaches you, on-device. No message content leaves the
phone. Receiver-side, so the person being targeted decides what they see rather than a
platform deciding for them.

Working prototype, not yet released. `apple_development/`

### The validation system — the prerequisite, and the part you can use

A receiver-side filter is only as trustworthy as the labels behind it and the
evaluation of the model's predictions. When we went to train Enaëlle's classifier we
found the available corpora disagreed with each other, single-model labelling
inherited that model's blind spots, and nothing in the field would tell us how wrong
either our labels or our predictions were.

So we built a validation system. Give it a corpus and it returns adjudicated verdicts
from a panel of five independent LLM judges. Give it your model's predictions as well
and it tells you where model and panel diverge, broken down by how much the judges
agreed. Either way you get an explicit *contested* band instead of a forced answer,
per-group false-positive rates, and a provenance record tying every number to the exact
texts that produced it.

We needed it. Others building classifiers need it too. It is MIT licensed and
documented below. `evaluate-COREML-prediction/eval-llm/`

---

## Why the contested band matters for an app

This is not an academic point. It is the reason Enaëlle is built the way it is.

Around 13% of our corpus lands in the 2–3 vote band, where the five judges do
not agree. That band is where counter-speech, reclaimed slurs and quoted abuse
concentrate. A journalist reproducing a threat they received looks identical to a
threat under a naive filter.

An app that removes those posts silences the people it is meant to protect.

Enaëlle's output is binary: a message lands under Harassment or under Neutral. What is
not binary is the path to that decision. Agreement level, per-tier signals and the
model's own confidence all feed a threshold, and where that threshold sits is what
decides a contested message. Getting it right is not something we can settle from a
corpus alone — it needs real usage. Once there is user data, the weights and the
threshold get adjusted against how people actually want their own inbox filtered.

Related design consequences, all measured rather than assumed:

- **Refusals are recorded, not coerced.** When a judge declines to answer, that is
  stored with the provider's reason. It never silently becomes a "safe" verdict.
- **Identity terms never trigger a match.** Crossing attack verbs with protected-class
  terms is the best-documented source of false-positive bias in toxicity classifiers
  (Dixon et al., 2018). Our filter configuration excludes identity terms from the query
  and matching layers entirely, and a test asserts that none reaches a compiled query.
  A filter that flags posts for mentioning a community is useless to that community.
  *Not yet built:* using those terms on the measurement side. Differential flag rate by
  identity term is computable from what we already store; a true per-group
  false-positive rate needs a human-labelled subset we do not have.
- **Everything is traceable.** Each run records a SHA-256 of the exact text set it saw,
  so any number can be traced back to its data months later.

---

## What the measurements show

September 2026. 8,436 posts, five judges, consensus at k ≥ 3 of 5.

| Stream | Selects for | n | Positive rate |
|---|---|---|---|
| Neutral baseline | mundane topics, non-reply | 1,486 | 3.5% |
| Topic | 12 civic subjects | 1,795 | 13.1% |
| Lexicon-seeded | abuse vocabulary, 5 tiers | 1,967 | 28.5% |
| Account, lexicon negated | roster mentions minus abuse terms | 1,207 | 28.3% |
| Reply-directed | replies to a sampled account roster | 1,981 | 48.4% |

Two results that shape the app.

**A keyword filter is not enough.** The same accounts, with roughly 25 abuse terms
negated from the query, still return 28.3% harassment against 48.4% unfiltered. Simple
blocklists — what most people are offered today — miss well over half of it.

**Abuse is topic-dependent.** Within the topic stream, identity subjects draw far more
abuse than policy subjects: LGBT 64.0%, racism 56.2%, feminism 44.0%, secularism 44.0%
against ecology 10.4%, pensions 10.4%, economy 10.2%, education 6.5%. Same collection
method, same week, same query shape. (n ≈ 50 per subject, so intervals are wide.) The
people who most need a filter are the ones who receive the most.

Earlier work on a merged 24,251-post corpus is in
[`evaluate-COREML-prediction/`](evaluate-COREML-prediction).

---

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

### The validation system — `evaluate-COREML-prediction/eval-llm/`

| File | Does |
|---|---|
| `label_corpus.py` | Runs the five-judge panel over a corpus CSV |
| `run_store.py` | Append-only run storage. Nothing is ever overwritten |
| `recompute_consensus.py` | Consensus from a stored run, no API calls |
| `vision_media.py` | Gemini Vision over images and video |
| `load_vision.py` | Joins text panel, vision, and platform flag |
| `sanity.py` | Assertions that fail at the point an assumption is made |
| `compare_agreement.py` | Inter-judge agreement between two prompt versions |

---

## Using the validation system

You do not need Enaëlle to use this. It takes any corpus.

```bash
git clone https://github.com/Emakia-Project/emakia.git
cd emakia/evaluate-COREML-prediction/eval-llm

python3 -m venv env && source env/bin/activate
pip install -r requirements.txt
```

Set keys for whichever judges you want:

```bash
# .env
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
MISTRAL_API_KEY=...
OPENAI_API_KEY=...
XAI_API_KEY=...
```

Your corpus is a CSV with `id`, `source`, `text`, `label`. Leave `label` empty if you
have no gold labels — that is the normal case, and the one this exists for.

```bash
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

Every run writes `runs/<run_id>/` with a manifest, the raw judge responses, and a
corpus fingerprint. Runs never overwrite each other, and resuming against a different
text set is refused.

### Vision

```bash
python vision_media.py --manifest media_local/manifest.jsonl --estimate
python vision_media.py --manifest media_local/manifest.jsonl --n 25
python vision_media.py --manifest media_local/manifest.jsonl
```

Images, video and animated GIFs. Archive media locally first — platform media URLs
expire, and a link stored today may be dead next week. We lost an entire media
evaluation to this before we learned it.

---

## Prompt versions

Two prompts, used asymmetrically.

| | Criterion | Applied to |
|---|---|---|
| **v1** | Does the text *contain* harassment? | Text panel |
| **v2** | Does the content *target* a person or identifiable group? | Vision |

"Contains" conflates depicting abuse with committing it. Tolerable in text, severe in
images: a press photograph of a protest, or a screenshot of abuse being reported,
contains harassment while targeting no one. Under v1 our vision judges agreed with each
other on press photographs and were wrong together — high agreement on an incorrect
verdict, which agreement alone cannot detect.

Both prompts are kept verbatim so the ablation can be run over the same corpus.

---

## Data

`data/`, `raw/`, `media_local/` and `.env` are excluded from version control.

Consistent with platform developer agreements, any public release of collected content
contains post identifiers and derived labels only, never post text or media. Aggregate
statistics, model artifacts, filter configurations and query definitions are releasable
in full.

---

## Research

Accepted for oral presentation at **AIVR 2026**. Two further papers under review at
ACL-affiliated venues: the evaluation defects this pipeline was rebuilt to fix, and the
corpus audit run on the corrected version.

Collaboration with the NLP programme at Montclair State University.

Lexical resources: [HurtLex](https://github.com/valeriobasile/hurtlex),
[LDNOOBW](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words).
Used rather than hand-curating slur lists, so provenance is citable.

---

## Contributing

Contributions welcome. Issues tagged `good first issue` are the place to start.

Most useful right now:

- **Unifying the pipelines.** We currently maintain separate code per language. The
  tier structure is language-independent; the vocabulary is not. Merging them into one
  parameterised pipeline is the next structural piece of work.
- **Open local judges.** The panel depends on commercial APIs today. Support for
  locally-run open models would remove that.
- **Rate-limit handling.** Provider throttling currently surfaces as an abstention
  rather than a retry.
- **Android.** The on-device classifier is iOS-only.

Please open an issue before starting anything substantial.

---

## About

Emakia is a US 501(c)(3) non-profit building open-source AI safety tools for civic
content moderation, with a focus on protecting public servants, LGBTQ+ individuals and
minority communities from coordinated harassment.

The goal is Enaëlle. The validation system is what we had to build to get there, and
what we are giving away.

MIT licensed. See [LICENSE](LICENSE).
