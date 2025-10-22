# Annotation Codebook: Suicidal Ideation Detection

## Overview
This codebook defines labels for binary (SI vs non-SI) and multiclass (SI, MH, NEU, HUMOR) classification of Reddit posts, with operational rules designed for consistent human annotation and trustworthy modeling.

## Annotation scope
- Text unit: Use combined_text (title + body) for labeling; do not infer labels from subreddit or flair alone.
- Language: Apply rules consistently to English and code-mixed content (e.g., Hindi–English). When meaning is unclear, route to adjudication.

## SI (Suicidal Ideation)
Definition: First-person expressions of desire, intent, plan, or method to die or self-harm. Both passive and active ideation are labeled SI.

- Passive cues: Wish not to exist, “better off dead,” “don’t want to be here,” without plan/intent.
- Active cues: Thoughts of killing self, method exploration, planning steps, stated intent.

Include:
- Direct statements: “I want to die,” “planning to end it.”
- Indirect/passive: “better off dead,” “no point in living.”
- Method/plan mentions with self-reference: “How painful is hanging yourself?” (if self-referential or implies consideration).

Exclude:
- Explicit denials: “not suicidal,” “I don’t wanna die.” (non-SI)
- Third-person only: “my friend is suicidal.” (non-SI)
- Purely hypothetical without self-reference: “Why doesn’t everyone want to die?” (non-SI)

Examples
- Positive (SI): “I keep thinking about taking all my pills.”
- Positive (SI): “I’m constantly postponing my inevitable suicide.”
- Positive (SI): “I want to end it so badly, give me a reason not to.”
- Positive (SI): “How painful really is hanging yourself?” (self-referential/consideration)
- Positive (SI): “I’m thinking about killing myself again.”
- Positive (SI): “I just tried to kill myself…”
- Negative (non-SI; correct class in parentheses): “I used to be suicidal but I’m okay now.” (MH)
- Negative (non-SI; correct class): “I don’t wanna die.” (SI denial → non-SI/MH)
- Negative (non-SI; correct class): “I’m so tired of this crap, dude?” (MH/NEU; no ideation)
- Negative (non-SI; correct class): “Aaj subh walk karne jana tha mujhe.” (NEU)

Notes:
- Hyperbole/sarcasm: If a phrase like “I want to die” is likely figurative and lacks self-harm/agency context, route to adjudication; prefer SI only if first-person agency + death/self-harm desire is reasonably indicated.
- Restraining factors: Posts expressing ideation but citing reasons not to act remain SI-positive; note protective factors separately if tracked.

## MH (Mental Health)
Definition: Mental health discourse (symptoms, coping, treatment, support) without SI signals.

Include:
- Symptoms and distress without ideation.
- Therapy/medication, diagnosis discussion, support-seeking.
Exclude:
- Any first-person ideation, plan, or intent (move to SI).

Examples:
- Positive (MH): “Started therapy for my panic attacks.”
- Positive (MH): “This has been the worst year of my life.”
- Positive (MH): “I’m so miserable,” “I need a break; is this shameful?”
- Positive (MH): “My life is a mess and I can’t forgive myself.”
- Negative (correct class): “YLOYD – You laugh or you die.” (HUMOR if comedic, no ideation)
- Negative (correct class): “I AM LITERALLY DOING WHAT YOU ASKED.” (NEU; no MH/SI content)
- Negative (correct class): “Money ruined my life, I need to die.” (SI; ideation present)

## NEU (Neutral)
Definition: Off-topic content with no mental health or suicidality signals.

Include:
- General life topics, logistics, hobbies, opinions, product talk.

Examples:
- “Which spoon are you?!”
- “amrood ki chutney for lazy days.”
- “To all the boys, how to get confident in front of girls?”
- “Movie review and weekend plans.”

Exclude:
- Any MH or SI indicators → move to MH or SI.

## HUMOR (Humor/Sarcasm)
Definition: Primary intent is humor/sarcasm; no first-person ideation/intent.

Include:
- Jokes, memes, sarcasm about life or mild MH topics without ideation.

Exclude:
- If there is first-person ideation, label SI even if humorous or dark.

Examples:
- “When you’re in your 20s and your back hurts: [meme].”
- “Enjoy it when my dad thanks me for the gift I got him with his money.”
- “Vaping is lame.”
- Negative (correct class): “Life is such a total joke.” (MH if distress context; NEU if off-topic; not HUMOR by default).
  
## Decision rules
- Negation: Mark non-SI when ideation is explicitly denied (“I don’t wanna die”).
- Third-person: Exclude from SI unless author self-discloses first-person ideation.
- Uncertainty/hyperbole: If literal ideation isn’t reasonably supported by context, route to adjudication. Prefer SI if first-person agency + death/self-harm desire is indicated.

## Ethics and safety
- De-identify content; paraphrase examples to reduce re-identification
- Provide annotator well-being resources and define escalation for any identifiable imminent-risk content.
  
## Changelog
- 2025-10-11: Initial draft.
- 2025-10-12: Fixed SI/MH negative examples with ideation; added NEU and HUMOR examples; clarified negative-example semantics.
- 2025-10-22: Added passive/active SI cues, hyperbole/sarcasm guidance, annotation scope, adjudication protocol, agreement targets, and corrected misassigned examples.
