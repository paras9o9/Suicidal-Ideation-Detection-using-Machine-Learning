# Annotation Codebook: Suicidal Ideation Detection

## Overview
This codebook defines labels for binary (SI vs non-SI) and multiclass (SI, MH, NEU, HUMOR) classification of Reddit posts.

## Label Definitions

### SI (Suicidal Ideation)
**Definition**: First-person expressions of desire, intent, plan, or method to die or self-harm.

**Include**:
- Direct statements: "I want to die," "planning to end it"
- Indirect/passive: "better off dead," "no point in living"
- Method/plan mentions with self-reference

**Exclude**:
- Explicit denials: "not suicidal," "no ideation"
- Third-person only: "my friend is suicidal"
- Hypothetical without self-reference

**Examples**:
- Positive: "I keep thinking about taking all my pills"
- Positive: "I feel like I’m constantly postponing my inevitable suicide"
- Positive: "i don’t want to die anymore but this time it looks like i might anyway"
- Positive: "i want to end it so badly, give me a reason not to."
- Positive: "Everyday I wonder if I should just give up"
- Positive: "I think about suicide to frequently and idk what to think."
- Positive: "Thinking about suicide makes me feel weirdly pleasured"
- Positive: "How painful really is hanging yourself?"
- Positive: "I'm thinking about killing myself again"
- Positive: "I just tried to kill myself but I’m too big of a pussy"
- Negative: "I used to be suicidal but I'm okay now"
- Negative: "How would you like to live?"
- Negative: "Will i randomly commit suicide?"
- Negative: "Why doesn't everyone want to die"
- Negative: "i'm so tired i just want to die"
- Negative: "I don't want to be here anymore but I have to"
- Negative: "Life has gone incredibly downhill since the last 1 month."
- Negative: "Do you ever feel bad about yourself ?"
- Negative: "Aaj subh walk karne jana tha mujhe"
- Negative: "I reported my boyfriend and I feel awful"
  
### MH (Mental Health)
**Definition**: Mental health discourse (symptoms, coping, support) without SI signals.

**Include**: Anxiety, depression talk, therapy/medication, support seeking
**Exclude**: Any first-person ideation, plan, or intent

**Examples**:
- Positive: "Started therapy for my panic attacks"
- Positive: "therapy feels like capitalist leech scam they will loot you at your worst phase of life."
- Positive: "Things will not get better. Fuck everything already."
- Positive: "I’m so fucking miserable"
- Positive: "This has been the worst year of my life"
- Positive: "How did you find the suitable therapist for you?"
- Positive: "im not sober and lying to my therapist"
- Positive: "Me when zabardasti ageing and adulting 💔💔"
- Positive: "My life is a mess and I can’t forgive myself."
- Positive: "I feel like I need a break, is this shameful?"
- Negative: "I'm so depressed I don't want to live" → SI

### NEU (Neutral)
**Definition**: Off-topic, no mental health or suicidality signals.

### HUMOR (Humor/Sarcasm)
**Definition**: Primary intent is humor; no first-person ideation/intent.

## Decision Rules
- Negation: Mark non-SI if ideation explicitly denied
- Uncertainty: Route to adjudication if unclear; prefer SI if agency + desire present
- Third-person: Exclude from SI unless author self-discloses

## Ethics & Safety
- De-identify all content before annotation
- Paraphrase examples to reduce re-identification
- Annotator resources: [crisis line, support contacts]
- Escalate any identifiable imminent-risk content

## Changelog
- 2025-10-11: Initial draft
