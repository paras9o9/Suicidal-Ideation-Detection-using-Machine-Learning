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
- Label Design
This dataset supports two classification frameworks to enable both accessible baselines and fine-grained risk assessment:

**Binary classification (SI vs non-SI):**

Every post is labeled either "Suicidal Ideation (SI)" or "non-SI," providing a straightforward detection task aligned with safety-critical screening applications.​

Binary labels reduce annotation complexity, class imbalance challenges, and model training overhead, establishing a strong baseline for benchmarking before advancing to multi-level taxonomies.​

Rationale: Many real-world triage systems require a simple yes/no risk flag; binary framing also facilitates comparison with prior Reddit SI detection work.​

**Multi-class classification (SI, MH, NEU, HUMOR):**

SI: First-person expressions of desire, intent, plan, or method to die or self-harm, encompassing both passive ideation ("wish I were dead") and active ideation with method consideration or planning.​

MH (Mental Health): Mental health discourse including symptoms, coping strategies, therapy/medication discussion, and support-seeking, without suicidal ideation signals.​

NEU (Neutral): Off-topic content with no mental health or suicidality indicators (e.g., general life topics, hobbies, logistics).​

HUMOR: Humorous or sarcastic content without first-person ideation; posts with genuine ideation masked as humor are labeled SI to prioritize safety.​

This multi-class scheme captures nuanced distinctions between suicidal content, mental health distress, neutral discourse, and humor, enabling richer analysis of model behavior and supporting research on disambiguation of dark humor from genuine risk signals.​

The SI class incorporates severity distinctions informed by the Columbia-Suicide Severity Rating Scale (C-SSRS), differentiating passive ideation (wish to be dead, no plan) from active ideation with intent or planning, though both are collapsed into a single SI label for this dataset version to maintain annotation consistency and sample size.​

- Annotation process:
1. **Annotation Methodology**
Approach: Dual human annotation with pilot validation​

Process Overview:​

- Initial dataset: 7,180 Reddit posts from mental health subreddits
- Annotation method: Manual human labeling using structured codebook
- Pilot phase: 200 posts (validation of annotation guidelines)
- Full annotation: All 7,180 posts labeled across 4 classes

2. **Label Taxonomy**
Four-class multiclass classification:​

Label	Definition	Count	Percentage
SI (Suicidal Ideation)	Posts expressing suicidal thoughts, plans, or intent	1,315	18.3%
MH (Mental Health)	Posts about depression, anxiety, or mental health without SI	2,860	39.8%
HUMOR	Memes, jokes, or humorous content related to mental health	2,164	30.1%
NEU (Neutral)	General discussion or informational posts	841	11.7%

3. **Annotation Codebook**
Keyword-based categorization with 6 SI subtypes:
3.1 Direct SI Language (13 keywords)

Examples: "kill myself", "suicide", "end my life", "suicidal"
High-risk, explicit suicidal intent

3.2 Indirect/Coded Language (16 keywords)

Examples: "unalive", "final message", "this is it"
Reddit-specific euphemisms avoiding content filters

3.3 Preparation/Planning (9 keywords)

Examples: "planned everything", "set date", "writing goodbye"
Imminent risk indicators

3.4 Death-related Vocabulary

Keywords: "die", "death", "dead", "dying"
General mortality themes

3.5 Method Mentions

Keywords: "hang", "overdose", "jump", "pills"
Specific suicide method references

4. **Inter-Annotator Agreement (Pilot Phase)**
Pilot Design:​

Sample size: 200 posts
Annotators: 2 independent coders (Annotator A, Annotator B)
Overlap: 100% (all 200 posts labeled by both)

Agreement Metrics:​

Metric	Value	Interpretation
Cohen's Kappa (κ)	1.0	Perfect agreement
Agreement rate	100%	All 200 posts labeled identically
Disagreements	0	Zero cases requiring adjudication
Class-wise Performance:​

Class	Annotator A Count	Annotator B Count	Agreement
SI	60	60	100%
MH	60	60	100%
NEU	40	40	100%
HUMOR	40	40	100%

5. **Adjudication Process**
Procedure:​

- Automated conflict detection script (Python)
- Disagreements flagged for review
- Confusion matrix generated to identify systematic errors
- Adjudicator reviews cases with uncertainty flags

Actual Outcome:​

- Zero disagreements in pilot → No adjudication needed
- Perfect inter-annotator agreement (κ = 1.0) validated codebook clarity

6. **Edge Cases and Challenges**
6.1 SI vs MH Boundary

Challenge: Distinguishing suicidal ideation from severe depression

Example edge case:
Post: "I'm so tired of living like this, I don't see the point anymore"

SI indicator: "tired of living", "no point"
But lacks: Explicit intent, method, plan
Resolution: Labeled as MH (depression without active SI)

Feature analysis finding:

- "Burden" themes ("better off without me") appeared equally in SI and MH
- Passive death wishes ("tired of living") showed negative correlation with SI
- These were removed from final SI keyword set due to ambiguity

6.2 Self-Harm vs Suicidal Ideation

Challenge: Non-suicidal self-injury (NSSI) vs SI

Example edge case:
Post: "I cut myself to cope with the pain"

- Contains self-harm language
- But lacks suicidal intent

Resolution: Labeled as MH (self-harm without SI)

Feature analysis finding:

- has_self_harm had negative coefficient (-0.44) for SI prediction
- Self-harm language more common in MH posts than SI posts

6.3 Dark Humor vs Genuine SI

Challenge: Distinguishing suicidal memes from real distress

Example edge case:
Post: "POV: You're planning your unaliving for the 100th time this week lol"

- Contains SI keywords ("unaliving", "planning")
- But humor markers ("lol", "POV", "100th time")

Resolution: Labeled as HUMOR
Heuristic: Presence of meme formatting, exaggeration, or laugh reactions → HUMOR category

7. **Quality Control Measures**
7.1 Pilot Validation​
- Purpose: Test codebook clarity before full annotation
- Result: κ = 1.0 (perfect agreement) confirmed guidelines were unambiguous

7.2 Automated Consistency Checks

- Script validated all labels were in {SI, MH, NEU, HUMOR}
- Flagged missing labels (none found in final dataset)
- Checked train/val/test split integrity (70/15/15 maintained)

7.3 Post-Annotation Review

- Feature importance analysis revealed which SI indicators were most predictive
- Discovered burden/passive themes were not SI-specific → refined understanding

8. **Annotation Statistics**
Final Dataset Composition:​

Split	Total Posts	SI	MH	NEU	HUMOR
Train	5,026 (70%)	920	2,002	588	1,516
Validation	1,077 (15%)	198	429	126	324
Test	1,077 (15%)	197	429	127	324
Total	7,180	1,315	2,860	841	2,164

Class Distribution:​

Moderately imbalanced (imbalance ratio: 3.4:1)
SI minority class: 18.3% of dataset
Handled via custom class weighting in models

9. **Strengths and Limitations**
Strengths:​

- Perfect inter-annotator agreement (κ = 1.0)
- Large sample size (7,180 posts)
- Structured codebook with 78 keywords across 6 categories
- Validated through pilot study before full annotation

Limitations:

- Binary inter-annotator check only (2 coders, no third adjudicator)
- Reddit-specific language may not generalize to other platforms
- Burden and passive SI themes proved ambiguous (removed in final model)
- Perfect pilot agreement may indicate easy sample (not representative of edge cases)
 
### Data schema
| Field Name           | Type    | Description                        | Allowed Values / Format                  | Nullable | Notes                     |
| -------------------- | ------- | ---------------------------------- | ---------------------------------------- | -------- | ------------------------- |
| id                   | String  | Unique Reddit post identifier      | Alphanumeric (e.g., "1nbav77")           | No       | Primary key               |
| major_category       | String  | Primary classification label       | "SI", "NON_SI"                           | No       | Target variable           |
| subcategory          | String  | Granular classification            | "SI_Direct", "NonSI_Uncategorized", etc. | Yes      | Multi-level labels        |
| subreddit            | String  | Reddit community name              | Alphanumeric without "r/" prefix         | No       | Platform/community field  |
| title                | String  | Post title text                    | UTF-8 text                               | No       | May contain special chars |
| combined_text        | String  | Title + body concatenated          | UTF-8 text                               | No       | Primary NLP field         |
| combined_text_length | Integer | Character count                    | >= 0                                     | No       | Equivalent to char_len    |
| word_count           | Integer | Word/token count                   | >= 0                                     | No       | Equivalent to token_len   |
| created_utc          | Integer | Post creation timestamp            | Unix epoch (seconds)                     | No       | Convert to datetime       |
| score                | Integer | Reddit score (upvotes - downvotes) | Any integer                              | No       | Engagement metric         |
| num_comments         | Integer | Number of comments                 | >= 0                                     | No       | Engagement metric         |
| had_image            | Boolean | Image attachment flag              | TRUE, FALSE                              | No       | Media flag component      |
| has_body_text        | Boolean | Body text present flag             | TRUE, FALSE                              | No       | Differentiates title-only |
| has_meme_text        | Boolean | OCR text extracted flag            | TRUE, FALSE                              | No       | OCR indicator             |
| prelim_label         | String  | Automated pre-label                | "SI", "NON_SI", "UNKNOWN"                | Yes      | Pre-annotation filter     |
| si_confidence        | Float   | SI classification confidence       | 0.0 to 1.0                               | Yes      | Currently unpopulated     |
| url                  | String  | Reddit permalink                   | https://www.reddit.com/...               | No       | Audit trail               |
| collection_mode      | String  | Collection method                  | "api", "scrape", "manual"                | Yes      | Currently empty           |
| collection_date      | String  | Data collection timestamp          | YYYY-MM-DD                               | No       | Distinct from post date   |
| source_file          | String  | Raw JSON source path               | Absolute file path                       | Yes      | Traceability              |
| post_date            | String  | Human-readable post date           | "YYYY-MM-DD HH:MM:SS"                    | No       | Derived from created_utc  |

### Preprocessing and normalization
## Text Preprocessing and Normalization Pipeline (Code-Free Version)

Based on your suicidal ideation detection project, here's a comprehensive documentation of your preprocessing and normalization techniques:

***

### 1. Text Cleaning

#### URL Handling
**Policy**: All URLs removed entirely
- Reddit posts often contained image links (https://i.redd.it/...) and external resource links
- URLs don't contain SI-relevant information and create noise
- Removed patterns: HTTP/HTTPS links, www. addresses, Reddit-specific URLs

#### User Mentions and Reddit Formatting
**Policy**: User mentions replaced with special tokens, subreddit mentions removed
- User mentions converted to placeholder tokens to preserve sentence structure while preventing user-specific overfitting
- Subreddit mentions removed to prevent label leakage
- Reddit markdown formatting stripped (bold, italics, hyperlinks)

#### Emoji Handling
**Policy**: Emojis converted to text descriptions
- Emojis like skull, crying face, or knife may indicate emotional state or SI intent
- Converted to text equivalents to preserve emotional context
- Example: crying face emoji → "crying face" text

#### Lowercasing
**Policy**: Full lowercasing applied throughout
- Ensures consistency: "Kill myself" = "kill myself" = "KILL MYSELF"
- Reduces vocabulary size for more efficient TF-IDF representation
- Trade-off: Loses capitalization emphasis patterns

#### Punctuation and Whitespace
**Policy**: Whitespace normalized, punctuation preserved
- Multiple spaces collapsed to single space
- Repeated punctuation normalized (multiple exclamation marks → single)
- Punctuation kept for negation handling and sentence structure

#### Stopword Handling
**Policy**: Negations preserved, other stopwords removed
- **Critical distinction**: Words like "not", "no", "never" were kept
- Removed low-information words: "the", "a", "is", "are", "was"
- Rationale: "I want to live" vs "I don't want to live" requires negation preservation
- This is clinically critical for SI detection

### 2. De-identification

#### Personal Identifiers
**Policy**: PII replaced with tokens, not fully removed
- Email addresses → EMAIL token
- Phone numbers → PHONE token
- Usernames → USER token
- Preserves sentence structure while protecting privacy

#### Location References
**Policy**: NOT removed in current pipeline
- Location mentions rare in mental health discussions
- May contain clinical context (e.g., state-specific mental health laws)
- Minimal privacy risk on pseudonymous Reddit platform

#### ID Hashing
**Policy**: Applied to metadata fields
- Reddit post IDs kept as-is (already anonymized alphanumeric codes)
- Author fields removed during collection phase
- Subreddit names preserved for validation but excluded from model features

***

### 3. Language Filtering and Normalization

#### Language Detection
**Policy**: English-only filtering applied
- Dataset of 7,180 posts is predominantly English
- Non-English posts filtered out during preprocessing
- Exception: Hindi keywords included in SI lexicon but rarely used (coefficient 0.0 in feature analysis)

#### Normalization Strategies
**Policy**: Contractions preserved as-is
- "can't" kept separate from "cannot" to preserve informal tone
- Mental health language is often colloquial
- Spelling correction NOT applied to avoid changing authentic expression
- TF-IDF treats contractions as distinct tokens

***

### 4. Tokenization and Sequence Length

#### Tokenization Approach
**Method**: Word-level tokenization with n-grams
- Unigrams: individual words ("kill", "myself")
- Bigrams: two-word phrases ("kill myself")
- Captures SI-specific expressions that require multiple words
- Maximum 5,000 TF-IDF features to balance coverage and efficiency

#### Text Length Statistics
**Your dataset characteristics**:
- Character length range: 92-7,621 characters
- Word count range: 15-2,932 words
- Most posts: 50-500 words (short to medium length)
- Mean length: approximately 400 characters

#### Maximum Length Thresholds
**For traditional ML (TF-IDF)**: No truncation needed
- TF-IDF vectorizer handles variable-length documents automatically

**For deep learning (BERT)**: 256-token maximum chosen
- Rationale: 95th percentile of posts fit within 256 tokens
- Avoids truncation bias (cutting off critical SI statements at end of long posts)
- Shorter than BERT's 512-token maximum for faster training
- Ensures SI keywords near end of posts aren't lost

***

### Summary: Applied Preprocessing Decisions

**Techniques Applied**:
- URL removal for noise reduction
- User mention tokenization to prevent overfitting
- Lowercasing for normalization
- Whitespace standardization
- Stopword removal WITH negation preservation (clinical priority)
- Emoji text conversion for emotional context
- PII tokenization for privacy
- English language filtering
- Word-level tokenization with bigrams
- 256-token maximum for BERT models

**Techniques NOT Applied (with justification)**:
- Spelling correction: Informal SI language is authentic ("wanna die" vs "want to die")
- Stemming/Lemmatization: Preserves verb tense ("killed" vs "killing")
- Subreddit name inclusion: Would create label leakage shortcut
- Aggressive location removal: Rare in text, minimal privacy gain
- Complete punctuation removal: Needed for negations and questions

**Key Innovation**: Preserving negations while removing other stopwords - this is rare in standard NLP but critical for safety-critical SI detection where "don't want to live" vs "want to live" represents opposite meanings.

This preprocessing pipeline balances noise reduction with clinical information preservation, appropriate for mental health NLP applications where subtle linguistic differences carry high-stakes implications.

### Data splits and leakage prevention
1. Split Strategy Overview
   
Primary approach: Random stratified post-level split​
Split ratios: 70% train / 15% validation / 15% test
Training set: 5,026 posts
Validation set: 1,077 posts
Test set: 1,077 posts

Total: 7,180 posts

Stratification: Not applied (evidence shows uneven class distribution across splits)

2. Exact Split Sizes and Label Distribution
Training Set (5,026 posts - 70%)

| Label | Count | Percentage of Train | Percentage of Total Class |
| ----- | ----- | ------------------- | ------------------------- |
| SI    | 920   | 18.3%               | 69.9% of all SI posts     |
| MH    | 2,002 | 39.8%               | 70.0% of all MH posts     |
| NEU   | 588   | 11.7%               | 69.9% of all NEU posts    |
| HUMOR | 1,516 | 30.2%               | 70.0% of all HUMOR posts  |

| Label | Count | Percentage of Val | Percentage of Total Class |
| ----- | ----- | ----------------- | ------------------------- |
| SI    | 198   | 18.4%             | 15.1% of all SI posts     |
| MH    | 429   | 39.8%             | 15.0% of all MH posts     |
| NEU   | 126   | 11.7%             | 15.0% of all NEU posts    |
| HUMOR | 324   | 30.1%             | 15.0% of all HUMOR posts  |

| Label | Count | Percentage of Test | Percentage of Total Class |
| ----- | ----- | ------------------ | ------------------------- |
| SI    | 197   | 18.3%              | 15.0% of all SI posts     |
| MH    | 429   | 39.8%              | 15.0% of all MH posts     |
| NEU   | 127   | 11.8%              | 15.1% of all NEU posts    |
| HUMOR | 324   | 30.1%              | 15.0% of all HUMOR posts  |

Observation: Class proportions nearly identical across splits, suggesting approximate stratification was achieved.

3. Temporal Characteristics
Post date range: September 2019 - September 2025​

Temporal distribution analysis:

Oldest post: September 3, 2019 (SuicideWatch)
Newest post: September 13, 2025 (multiple subreddits)
Time span: 6 years of Reddit data
Current split method: Random, not time-based​

Posts from 2019-2025 mixed across train/val/test
Example: September 2025 posts appear in all three splits

No temporal leakage (future information doesn't predict past)

4. Leakage Prevention Analysis
What Was Implemented
Post-level splitting: Each post treated as independent unit​

Prevents direct duplication across splits

Random seed: Not documented in dataset (improvement needed)
Metadata fields preserved but not used in models:​
Subreddit name: Present but excluded from feature space
Post ID: Unique identifiers retained
Timestamps: Available but not used for temporal modeling

Identified Leakage Risks
Risk 1: Potential author duplication​

Same user may appear in multiple splits
User ID field not visible in dataset (may have been removed)
Posts like r/Vent discussions could have repeat authors
Mitigation needed: Author-disjoint splitting

Risk 2: Subreddit distribution​

All subreddits appear in all splits
Example: r/SuicideWatch, r/depression present in train/val/test

Not subreddit-disjoint
Current mitigation: Subreddit name excluded from model features

Risk 3: Thread/comment relationships​

No parent-child post relationships tracked
All entries are top-level posts, not comments

Leakage prevented: No thread contamination

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
