# Annotation Codebook: Suicidal Ideation Detection

## Overview
This codebook defines labels for binary (SI vs non-SI) and multiclass (SI, MH, NEU, HUMOR) classification of Reddit posts, with operational rules designed for consistent human annotation and trustworthy modeling.

---

## Annotation Scope
- **Text unit:** Use `combined_text` (title + body) for labeling; do not infer labels from subreddit or flair alone.
- **Language:** Apply rules consistently to English and code-mixed content (e.g., Hindi–English). When meaning is unclear, route to adjudication.
- **Annotator safety:** Take breaks every 60 minutes. If you encounter distressing content, log it and consult the project lead.

---

## Label Definitions

### SI (Suicidal Ideation)
**Definition:** First-person expressions of desire, intent, plan, or method to die by suicide or engage in self-harm. Both passive and active ideation are labeled SI.

**Include:**
- **Passive ideation:** Wish not to exist, "better off dead," "don't want to be here," without explicit plan/intent.
- **Active ideation:** Thoughts of killing self, method exploration, planning steps, stated intent.
- **Direct statements:** "I want to die," "planning to end it."
- **Indirect/coded language:** "better off dead," "no point in living," "checking out."
- **Method/plan mentions with self-reference:** "How painful is hanging yourself?" (if self-referential or implies consideration).
- **Non-Suicidal Self-Injury (NSSI):** "I cut myself to feel something" (included as SI for safety; high-risk indicator).
- **Conditional ideation:** "If I fail this exam, I'm done" (threat conditional on event).

**Exclude:**
- **Explicit denials:** "not suicidal," "I don't wanna die." → Label as MH or NEU depending on context.
- **Third-person only:** "my friend is suicidal" (unless author also discloses first-person ideation).
- **Purely hypothetical without self-reference:** "Why doesn't everyone want to die?" → Label as NEU or MH.
- **Historical recovery:** "I attempted suicide 5 years ago but I'm better now" → Label as MH.

**Examples:**
- ✅ SI: "I keep thinking about taking all my pills."
- ✅ SI: "I'm constantly postponing my inevitable suicide."
- ✅ SI: "I want to end it so badly, give me a reason not to."
- ✅ SI: "How painful really is hanging yourself?" (self-referential/consideration)
- ✅ SI: "I'm thinking about killing myself again."
- ✅ SI: "I just tried to kill myself…"
- ✅ SI: "If I don't pass this exam, I'm done." (conditional threat)
- ✅ SI: "I hope I don't wake up tomorrow." (passive ideation)
- ✅ SI: "I cut myself last night to feel something." (NSSI)
- ❌ NOT SI (→ MH): "I used to be suicidal but I'm okay now." (past tense, recovery)
- ❌ NOT SI (→ MH): "I don't wanna die." (explicit denial with distress)
- ❌ NOT SI (→ MH/NEU): "I'm so tired of this crap, dude?" (no ideation)
- ❌ NOT SI (→ NEU): "Aaj subh walk karne jana tha mujhe." (neutral statement)

**Notes:**
- **Hyperbole/sarcasm:** If a phrase like "I want to die" is likely figurative (e.g., "I want to die, this exam is so hard") and lacks self-harm/agency context, route to adjudication. Prefer SI only if first-person agency + death/self-harm desire is reasonably indicated.
- **Restraining factors:** Posts expressing ideation but citing reasons not to act remain SI-positive (e.g., "I want to die but my mom needs me"). Note protective factors separately if tracked.

---

### MH (Mental Health)
**Definition:** Mental health discourse (symptoms, coping, treatment, support) without SI signals.

**Include:**
- **Symptoms and distress without ideation:** Depression, anxiety, panic, burnout.
- **Treatment/support-seeking:** Therapy, medication, diagnosis discussion.
- **Past suicidality (recovery context):** "I survived my attempt in 2019 and life is better."

**Exclude:**
- Any first-person ideation, plan, or intent → Move to SI.
- Neutral off-topic content → Move to NEU.

**Examples:**
- ✅ MH: "Started therapy for my panic attacks."
- ✅ MH: "This has been the worst year of my life."
- ✅ MH: "I'm so miserable and I need a break; is this shameful?"
- ✅ MH: "My life is a mess and I can't forgive myself."
- ✅ MH: "I don't wanna die but I feel hopeless." (denial + distress)
- ✅ MH: "I attempted suicide 5 years ago but I'm in a better place now." (historical, recovery)
- ❌ NOT MH (→ HUMOR): "YLOYD – You laugh or you die." (comedic, no genuine distress)
- ❌ NOT MH (→ NEU): "I AM LITERALLY DOING WHAT YOU ASKED." (no MH/SI content)
- ❌ NOT MH (→ SI): "Money ruined my life, I need to die." (ideation present)

---

### NEU (Neutral)
**Definition:** Off-topic content with no mental health or suicidality signals.

**Include:**
- General life topics: logistics, hobbies, opinions, product talk.
- Questions/advice unrelated to mental health.

**Exclude:**
- Any MH or SI indicators → Move to MH or SI.
- Humorous intent → Move to HUMOR.

**Examples:**
- ✅ NEU: "Which spoon are you?!"
- ✅ NEU: "amrood ki chutney for lazy days."
- ✅ NEU: "To all the boys, how to get confident in front of girls?"
- ✅ NEU: "Movie review and weekend plans."
- ✅ NEU: "Best budget laptop for coding?"

---

### HUMOR (Humor/Sarcasm)
**Definition:** Primary intent is humor/sarcasm; no first-person ideation/intent.

**Include:**
- Jokes, memes, sarcasm about life or mild MH topics without genuine ideation.
- Dark humor without self-referential death wish.

**Exclude:**
- If there is first-person ideation → Label SI even if humorous or dark.

**Examples:**
- ✅ HUMOR: "When you're in your 20s and your back hurts: [meme]."
- ✅ HUMOR: "Enjoy it when my dad thanks me for the gift I got him with his money."
- ✅ HUMOR: "Vaping is lame."
- ✅ HUMOR: "I want to die... of laughter watching this show."
- ❌ NOT HUMOR (→ MH): "Life is such a total joke." (if distress context; otherwise NEU)
- ❌ NOT HUMOR (→ SI): "Jokingly, I keep thinking about ending it all." (ideation present despite humor framing)

---

## ⚡ Edge Case Protocols

### 1. Non-Suicidal Self-Injury (NSSI)
- **Rule:** Label as **SI**.
- **Rationale:** While clinically distinct, NSSI is a major risk factor for suicide. For this safety model, we prioritize recall.
- **Example:** "I cut myself to feel something" → **SI**

### 2. Past Attempts & Recovery
- **Rule:** 
  - **MH:** If the attempt is historical and discussed as a past event with no current urge (e.g., "I survived my attempt in 2019 and life is better").
  - **SI:** If the past attempt is used to express current hopelessness (e.g., "I failed my attempt last year and I regret waking up").

### 3. Conditional / Passive Ideation
- **Rule:** Label as **SI**.
- **Examples:**
  - "If I don't pass this exam, I'm done." → **SI** (Conditional Threat)
  - "I hope I don't wake up tomorrow." → **SI** (Passive Ideation)
  - "Sometimes I wish I could just disappear." → **SI** (Passive)

### 4. Code-Mixed Content (Hinglish)
- **Rule:** Translate mentally before labeling. Focus on intent, not language.
- **Examples:**
  - "Mera mann nahi lag raha, I want to quit life." → **SI**
  - "Sab bakwaas hai, bas mar jana chahiye." (Everything is nonsense, just should die) → **SI**
  - "Aaj bahut stress hai yaar." (Today is very stressful, friend) → **MH**

### 5. Method Inquiries
- **Rule:** Specific inquiries about lethal dosage/methods are labeled **SI** unless the context is clearly fictional/academic.
- **Examples:**
  - "How many pills would it take?" → **SI** (method inquiry)
  - "In my novel, the character overdoses. How much is realistic?" → **NEU** (fictional context)

### 6. Third-Person with Self-Disclosure
- **Rule:** If a post discusses another person's suicidality AND the author also discloses their own ideation, label **SI**.
- **Example:** "My friend is suicidal and honestly, so am I." → **SI**

---

## Decision Rules

### Priority Hierarchy (Apply in Order)
1. **First-person ideation?** → SI (overrides all other labels)
2. **Mental health distress without ideation?** → MH
3. **Humorous intent with no distress?** → HUMOR
4. **Off-topic/neutral?** → NEU

### Specific Rules
- **Negation:** Mark non-SI when ideation is explicitly denied ("I don't wanna die") → MH or NEU.
- **Third-person:** Exclude from SI unless author self-discloses first-person ideation.
- **Uncertainty/hyperbole:** If literal ideation isn't reasonably supported by context, route to adjudication. Prefer SI if first-person agency + death/self-harm desire is indicated.
- **Temporal markers:** "Used to be" / "was" → Past tense → Likely MH unless current ideation is also expressed.

---

## Annotation Workflow

### Step-by-Step Process
1. **Read the full text** (title + body) carefully.
2. **Identify first-person pronouns** (I, me, my, myself).
3. **Check for death/self-harm keywords:**
   - Direct: die, kill, suicide, end it, overdose
   - Indirect: disappear, not wake up, checking out, unalive
4. **Apply priority hierarchy:**
   - SI indicators? → Label SI
   - MH indicators? → Label MH
   - Humor/sarcasm? → Label HUMOR
   - None of the above? → Label NEU
5. **Route to adjudication if:**
   - Meaning is ambiguous (e.g., unclear hyperbole)
   - Code-mixed text with uncertain translation
   - Conflicting indicators (e.g., humor + mild ideation)

---

## Inter-Annotator Agreement (IAA)

### Quality Control Targets
- **Fleiss' Kappa (4-class):** ≥ 0.70 (substantial agreement)
- **Binary SI vs. Non-SI:** ≥ 0.80 (strong agreement)

### Adjudication Protocol
- **Threshold:** If 2+ annotators disagree, escalate to senior annotator.
- **Resolution:** Senior annotator reviews and makes final decision with justification logged.
- **Feedback loop:** Disagreements are discussed in weekly meetings to refine guidelines.

---

## Ethics and Safety

### Annotator Well-being
- **Breaks:** Mandatory 15-minute break every 60 minutes.
- **Support resources:** Counseling hotline numbers provided in project docs.
- **Opt-out:** Annotators can skip particularly distressing posts without penalty.

### Data De-identification
- **Remove:** Usernames, real names, locations, specific dates.
- **Paraphrase:** Examples in this codebook are paraphrased to reduce re-identification risk.

### Imminent Risk Protocol
- **If you encounter content suggesting immediate danger:**
  1. Flag the post with `[URGENT]` tag.
  2. Notify project lead immediately.
  3. Do NOT contact the user directly.

---

## Changelog
- **2025-10-11:** Initial draft.
- **2025-10-12:** Fixed SI/MH negative examples with ideation; added NEU and HUMOR examples; clarified negative-example semantics.
- **2025-10-22:** Added passive/active SI cues, hyperbole/sarcasm guidance, annotation scope, adjudication protocol, agreement targets, and corrected misassigned examples.
- **2026-01-10:** Added Edge Case Protocols (NSSI, past attempts, conditional ideation, Hinglish, method inquiries); enhanced decision rules with priority hierarchy; added annotation workflow and IAA targets; expanded ethics section with annotator well-being guidelines.

---

## Quick Reference Card

| Label | Key Signal | Example |
|-------|-----------|---------|
| **SI** | First-person ideation/intent | "I want to die" |
| **MH** | Mental health distress, no ideation | "I'm so depressed" |
| **NEU** | Off-topic, no MH/SI | "Best laptop for coding?" |
| **HUMOR** | Sarcasm/jokes, no ideation | "Dying of laughter" (figurative) |

### Common Confusions
- **"I'm tired of life"** → **SI** (passive ideation)
- **"Life is tiring"** → **MH** (distress, no ideation)
- **"This exam is killing me"** → **NEU/HUMOR** (hyperbole, no agency)
