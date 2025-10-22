# Suicidal-Ideation-Detection-using-Machine-Learning

Building a machine learning tool to detect suicidal ideation, suicidal plans, suicide attempts, suicide crisis, suicidal behavior, and non-suicidal self-injury (NSSI) from textual data is a feasible and promising approach supported by recent research.

### Executive summary
- Dataset’s purpose: To support research and model development for detecting suicidal ideation in social media text amoung the young population suffering in silent     and maybe trying to express themsefls on online, enabling early-risk signals while prioritizing privacy, ethics, and harm reduction.
- Summarize sources
  target_subreddit = (
        'SI': ['SuicideWatch, 'selfharm', 'AdultSelfHarm'],  # High SI probability
        'MH': ['depression', 'BPD', 'Vent', 'mentalhealth', 'MentalHealthSupport', 'SelfHate'],  # Mental health with SI screening
        'NEU': ['college', 'collegeIndia', 'TwentiesIndia'], # For Netural behavior
        'HUMOR': ['teenagers', 'suicidebywords', 'memes', 'darkjokes','IndianDankMemes', 'dankmemes', '2meirl4meirl'] # For distingushing humor and SI ideation
    )
- labeling scheme (binary and multi-level):
  - Binary classes: Every post is labeled either “suicidal ideation” or “non‑suicidal,” nothing in between. This makes models easier to train and results simpler to      report, but it can’t tell apart different risk levels like passive thoughts, active intent, or plans. Binary labeling reduces annotation effort and class             imbalance complexity, providing a clean starting point for benchmarking before moving to multi‑level labels.

  - Multi‑level: multiple classes that capture risk levels or categories, such as Mental Health, Neutral and Humor, this offers richer signals for analysis and           multiple levels let models and analyses distinguish passive thoughts from planning or attempts, which is valuable for research on risk progression and triage         logic.
 
- Preprocessing scope:
    We de‑identify user references, filter by English language and length, remove spam/duplicates, and apply OCR to image posts to extract embedded text.                 All steps are deterministic and versioned.
    
- Intended use constraints (research, non-clinical):
    For research only. Not a diagnostic tool. Do not use to make clinical decisions or trigger automated actions without expert oversight,                                institutional review, and external validation. Adhere to platform terms; do not redistribute raw text.
    

### Background and motivation
- Briefly explain why suicidal ideation detection is studied (early identification can support triage/intervention), and why social media text is used (timeliness and scale with caution about biases and noise).
  
- Across text classification tasks for suicidal ideation, modern NLP methods such as deep neural networks and transformer-based models tend to outperform traditional machine learning baselines on in-domain benchmarks, reflecting stronger representation learning and context modeling.

- However, performance gains are often coupled with vulnerabilities: dataset and sampling biases, noisy or weak labels, shortcut learning (e.g., subreddit/keywords as proxies), and limited generalization across time, users, and platforms.

- Recent evaluations emphasize the need for author-disjoint and domain-shifted splits, external validation, and robust error analysis to avoid inflated estimates and to assess real-world reliability beyond benchmark conditions.


### Scope and intended use
- Intended use:
This project and its models are for research, benchmarking, and method development in suicidal ideation (SI) detection using social media text; they are not medical devices and must not be used for clinical decision-making or real-time content moderation without qualified human oversight, institutional approval, and external validation on appropriate populations.

- Out-of-scope: 
This work must not be used for diagnosis, crisis triage, or to replace licensed professionals; it must not be deployed without documented assessments of bias, safety, calibration, generalization, and model/feature drift, and without robust governance for monitoring and human-in-the-loop review.

### Data sources
- Platforms and subreddits:
Data was collected from Reddit communities focused on mental health, support, and adjacent contexts, including r/SuicideWatch, r/depression, r/mentalhealth, r/MentalHealthSupport, r/Vent, r/BPD, r/selfharm, r/AdultSelfHarm, r/SelfHate, and contrast domains such as r/memes, r/dankmemes, r/2meirl4meirl, r/teenagers, r/college, and r/TwentiesIndia, reflecting common research practice for SI detection and mental health analysis on Reddit.

- Collection windows and acquisition:
Submissions were gathered across multiple scripted runs using Reddit’s Data API with OAuth credentials, accessing subreddit listings via hot, new, and time-filtered top endpoints during the project’s active collection period; rate limits adhered to Reddit’s guidance (e.g., ~100 QPM per client averaged over windows) while paginating listing endpoints per API conventions.

- APIs/tools used:
The primary toolchain used Python Reddit API Wrapper (PRAW) to authenticate, traverse subreddit listings, and extract submission metadata and text; auxiliary utilities included OCR for meme-text extraction, and standard JSON/CSV serialization, consistent with tutorials and official PRAW documentation; open-source collectors like RedditHarbor and general API guides illustrate equivalent pipelines for researchers.


### Collection methodology
- Querying criteria: 
Collection targeted Reddit posts using OAuth-authenticated access to subreddit listing endpoints (hot, new, and time-filtered top), with per-run windows spanning multiple days and repeated passes to capture temporal variation in r/SuicideWatch, r/depression, r/mentalhealth, r/Vent, and adjacent communities consistent with prior SI-focused studies and Reddit API usage patterns. Queries applied combined criteria: subreddit membership filters, a language heuristic prioritizing English (e.g., ASCII ratio and stopword presence), and minimum text length thresholds tuned per subreddit to exclude low-information posts as established in API and research guides for Reddit data extraction. Inclusion rules admitted self-posts or image posts with sufficient text or OCR-extracted meme text; exclusion rules removed [deleted]/[removed], spam-like low-score content, bot indicators, and posts failing minimum content thresholds, aligning with common Reddit research pipelines and API documentation constraints. To respect platform limits and reliability, collection observed rate-limiting best practices (windowed request pacing and pagination), as recommended by Reddit Data API documentation and practitioner guidance on safe, paginated listing traversal.

- Multimodal handling: 
Image posts were processed by downloading direct image URLs from submissions and performing OCR with a standard Python OCR stack (e.g., PIL + Tesseract), a pattern consistent with open tutorials and tooling workflows for extracting text from Reddit memes and images. The OCR pipeline included pre-processing (load, grayscale or threshold as needed), followed by Tesseract inference and optional post-processing to normalize whitespace and remove artifacts, then alignment by attaching the extracted meme text to the originating post record for downstream modeling as a combined text field, in line with multimodal social content processing practices. For multilingual scenarios and code words often used in mental health contexts, OCR was configured to default to English, with potential addition of language packs when extending beyond English; low-confidence extractions or empty results were retained with a flag to allow model-time filtering, matching guidance to keep raw OCR while marking uncertainty for later stages. Posts lacking body text but having OCR-derived text were retained to avoid losing meme-only content, which prior work indicates can be informative for affect and ideation when properly extracted and aligned with the post metadata.

- De-duplication:
Exact duplicates were removed using stable submission IDs from Reddit (submission.id) after aggregating across multiple collection runs and files, a standard practice given that repeated hot/new queries often resurface the same posts over time per Reddit API behavior. Near-duplicates were identified using URL-based checks and optional textual similarity (e.g., normalized n-gram cosine or fingerprint hashing) to catch reposts and mirrored content, which is common in meme-heavy subreddits and cross-posted mental health narratives, as recommended in dataset merging and deduplication best practices. To prevent leakage across train/validation/test splits, cross-source overlap checks grouped examples by unique post ID and, optionally, by user or URL clusters before splitting, and considered subreddit-level or temporal holdouts to reduce subreddit-as-label shortcuts and temporal confounds, aligning with prior methodological cautions in Reddit mental health research. Splits were performed after deduplication with grouping constraints (e.g., no shared IDs or near-duplicate clusters across splits) to maintain independence of evaluation sets, which is consistent with guidance for robust dataset preparation and model evaluation on Reddit data.


### Data annotation and labels
- Label design: binary (SI vs non-SI) or multi-class severity (e.g., based on Columbia-Suicide Severity Rating Scale mappings if used), and rationale.[9][3]
- Annotation process: automatic heuristics, keyword seeds, weak labels, or human labeling; inter-annotator agreement if applicable; adjudication steps; example edge cases.[3][8]
- Known label risks: keyword leakage, subreddit-as-label shortcuts, topic confounds; plan mitigations (balanced controls, adversarial splits, leakage checks).[8][3]

### Data schema
- Provide a precise field dictionary for each JSON/CSV row:  
  - id, platform, subreddit/community, created_utc, author_id (hashed), post_text, title, ocr_text, media_flags, language, label, prelim_label, source_split, char_len, token_len, toxicity/lexicon scores (if computed), and collection_date.[1][8]
- Include units, allowed values, and nullability for each field, plus versioned schema changes.[1][8]

### Preprocessing and normalization
- Text cleaning: URL/user/emoji handling, lowercasing policy, punctuation, whitespace, stopwords, and preservation of negations.[8]
- De-identification: remove usernames, emails, phone numbers, location hints; hashing IDs; note tradeoffs with context.[10][8]
- Language filtering and normalization strategies; tokenization baselines and max-len thresholds to avoid truncation bias.[8]

### Data splits and leakage prevention
- Train/validation/test split strategy: time-based, author-disjoint, and subreddit-disjoint variants to quantify generalization.[3][8]
- Document exact sizes and balancing per label per split; justify choices and record random seeds.[3][8]

### Bias, safety, and ethical considerations
- Risks: demographic bias, subreddit/topic confounds, performative language, and self-harm contagion concerns when exposing examples.[10][8]
- Mitigations: de-identification, sensitive content access controls, filtered example sharing, ethics review or advisory, and clear non-clinical use notice.[10][8]
- Harm-minimizing documentation: crisis resources note, annotation safety protocol, and usage terms requiring caution.[10][8]

### Licensing and access
- Data licensing summary: platform TOS compliance, redistribution stance (metadata vs raw text), and how to request controlled access if needed.[1][8]
- Derivative work policy: restrictions for commercial/clinical use and requirement to cite the dataset documentation.[8][10]

### Baseline tasks and evaluation
- Tasks: binary SI detection; optionally multi-level severity classification; domain transfer between subreddits/platforms.[9][8]
- Metrics: precision, recall, F1 (macro), ROC-AUC, PR-AUC; report per-class and macro to handle imbalance; include calibration assessment.[3][8]
- Splits to test: in-domain vs cross-domain; author-disjoint to avoid memorization; time-split to assess drift.[3][8]

### Baseline models
- Traditional ML: TF-IDF or n-grams with linear SVM/LogReg, plus feature ablations and leakage checks.[8]
- Deep learning: CNN/LSTM/C-LSTM baselines; note sequence length, pretrained embeddings, and regularization.[8]
- Transformers: fine-tune BERT/RoBERTa/ELECTRA and domain-adapt if necessary; report strong baselines but discuss label reliability and shortcut learning risks.[5][3]

### Robustness and generalization
- Stress tests: evaluate across subreddits, time periods, and content types (short vs long, OCR vs text-only) to expose shortcuts.[3][8]
- Domain shift: test on external datasets if allowed; discuss differences in annotation schemes and performance drops.[5][3]

### Explainability and interpretability
- Provide feature attribution examples (e.g., SHAP/Integrated Gradients) and discuss limitations and potential for false reassurance in clinical contexts.[2][10]
- Document common salient patterns and risky shortcuts (e.g., keyword over-reliance).[3][8]

### Reproducibility
- Versioning: dataset version, schema version, and changelog with added/removed records; frozen splits with hashes.[8]
- Code: scripts for collection, preprocessing, labeling, and evaluation; environment files; seed control and exact command logs.[8]

### Known limitations
- Coverage: platform/subreddit bias; language and cultural limitations; ambiguity of self-disclosure vs metaphor.[10][8]
- Label noise: weak labels and heuristic errors; steps taken and remaining risks; caution for deployment claims.[3][8]

### Citation and acknowledgments
- Provide a canonical citation for the dataset; acknowledge platform communities and any annotators/advisors.[1][8]

***

Practical next steps to finalize the documentation:
- Inventory the actual sources, date ranges, record counts, label distributions, and schema as currently collected; insert them into the above sections.[1][8]
- Lock author-disjoint and time-based splits; compute per-split stats and leak checks; freeze seeds and store split manifests.[3][8]
- Write an ethical use and access policy page with a clear non-clinical use disclaimer and instructions for requesting access, if controlled.[10][8]
- Add a Baselines section with one traditional ML, one LSTM/CNN, and one transformer fine-tune plan; reserve results slots to fill after preprocessing.[8][3]

“This repository is intended for research, benchmarking, and method development for suicidal ideation detection on social media text. It is not a medical device and must not be used for clinical decision-making or automated moderation without qualified human oversight, institutional review, and external validation. The project is out-of-scope for diagnosis, professional replacement, and any deployment lacking documented assessments of bias, safety, calibration, and drift, along with monitoring, governance, and user privacy protections.”

If helpful, a concise template to start the README or dataset card:
- Title and version; summary (3–5 lines).[8]
- Intended use and limitations (bullet list).[10]
- Data sources, dates, and collection method.[1]
- Annotation and labels (process, classes, examples).[9]
- Schema and splits (tables).[8]
- Ethical considerations and licensing.[10]
- Baselines and evaluation plan.[3]
- Changelog and citation.[8]
