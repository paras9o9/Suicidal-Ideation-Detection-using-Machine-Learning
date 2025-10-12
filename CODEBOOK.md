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
- Negative: "I’m so tired of this crap dude?"
- Negative: "Trying so hard to be a better partner"
- Negative: "If one is ugly but doing good in life how can he date?"
- Negative: "Turning 26 and feels like i haven’t achieved anything…"
- Negative: "I just want a slice of cake"
- Negative: "Life is such a total joke."
- Negative: "Aaj subh walk karne jana tha mujhe"
- Negative: "I don’t wanna die"
  
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
- Negative: "Im so tired of contantly treated like a child with no speech"
- Negative: "YLOYD - You laugh or you die"
- Negative: "Why does it feel like no one wants to talk anymore?"
- Negative: "Chalo utho bhai subah ho gayi, gym/running ka time ho gaya !"
- Negative: "I don’t ever wanna work with kids again."
- Negative: "Need opinions, am I crazy or over thinking?"
- Negative: "I missed my brothers wedding"
- Negative: "I got in a fight at school 😣"
- Negative: "My mom caught me and my boyfriend together"
- Negative: "Why is everyone rude to each other?"
- Negative: "I AM LITERALLY DOING WHAT YOU ASKED"

### NEU (Neutral)
**Definition**: Off-topic, no mental health or suicidality signals.

**Examples**:
- "Feed them and they will never forget"
- "I feel too old at 22."
- "How do you socialise and meet people in your 20s?"
- "Which spoon are you?!"
- "I am just a girl"
- "Roommates boyfriend always over"
- "Why do some people pretend to be busy ?"
- "amrood ki chutney for lazy days"
- "How you'll manage this gurlss 😭🎀?"
- "To all the boys , here's how to get confident in front of girls"

### HUMOR (Humor/Sarcasm)
**Definition**: Primary intent is humor; no first-person ideation/intent.

**Examples**:
- "Me when bro says the nastiest most downright wrong thing"
- "Gang Masti toh dekhho😶"
- "Only When You Study The Mood  When he finds out all you needed
was food to get rid of that attitude"
- "Vaping is lame"
- "Enjoy it  when my dad thanks me for
the birthday gift | got him
with his own money"
- "Emergency  When you can't find a socket
to revive your dead phone:"
- "I have the power  How teachers feel when
they stop the class from
leaving after the bell rang"
- "Do I look gay?"
- "I guess I’m old now  When you’re in your 20’s and your back
hurts:

made with mematic"
- "It looks like a job for a gorilla"

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
- 2025-10-12: Fixed SI/MH negative examples with ideation; added NEU and HUMOR examples;
