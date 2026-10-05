# Model Card: Mood Machine

## 1. Model Overview

**Model type:**
I built and compared both versions: the rule-based classifier in `mood_analyzer.py` and the ML classifier in `ml_experiments.py`.

**Intended purpose:**
Classify short social-media-style posts as `positive`, `negative`, `neutral`, or `mixed`.

**How it works (brief):**
The rule-based model lowercases the text, splits it on spaces, and scores each token: +1 for a positive word, -1 for a negative word. A negation word (`not`, `never`, `no`, `don't`, `doesn't`, `isn't`, `wasn't`) flips the next sentiment word it reaches, even if filler words sit in between ("not very happy" still flips). Score > 0 is `positive`, < 0 is `negative`, and 0 is `neutral`.

The ML model turns each post into word counts with `CountVectorizer` and trains a logistic regression classifier on the labeled posts.

## 2. Data

**Dataset description:**
`SAMPLE_POSTS` has 14 posts: the 6 starter posts plus 8 I added. Label counts: 5 positive, 4 negative, 3 neutral, 2 mixed.

**Labeling process:**
I added each post and its label together so `SAMPLE_POSTS` and `TRUE_LABELS` stayed the same length. I also expanded the word lists with slang (`fire`, `goated`, `sick`, `lowkey`, `hilarious`, `proud` on the positive side; `done`, `dead`, `stuck`, `exhausted`, `meh` on the negative side).

Hard-to-label posts:
- "I'm dead 💀 that was hilarious": literally negative words, actually positive.
- "I'm fine 🙂": could be genuinely fine or quietly upset. I labeled it neutral, but someone else could reasonably say negative.
- "I absolutely love being stuck in traffic 🙄": sarcasm, labeled negative.

**Important characteristics:**
- Slang with shifting meaning (`fire`, `dead`, `done`)
- Emojis carrying tone (🙄, 💀, 😩, 🙂)
- Sarcasm
- Mixed feelings ("stressed but kind of proud")

**Possible issues:**
Only 14 posts, only 2 mixed examples, and the slang reflects one style of informal English. Labels for sarcasm and ambiguous posts are subjective.

## 3. How the Rule-Based Model Works

**Scoring rules:**
- Positive word: +1. Negative word: -1.
- Negation flips the next sentiment word (my enhancement).
- No punctuation stripping and no emoji handling.
- Thresholds: > 0 positive, < 0 negative, 0 neutral. The model never outputs `mixed`.

**Targeted fix (Part 3):**
Starter negation only checked the word directly before. I widened the negation list to include contractions and let negation carry until it hits a sentiment word. "I am not happy about this" scores -1 (negative, correct) and "not bad honestly 🙂" scores +1 (positive, correct).

Adding slang to the word lists also helped ("This is so fire 🔥" is now correctly positive), but it introduced new errors:
- `lowkey` as a positive word turns "Lowkey stressed but kind of proud of myself 😅" into positive (score 1). Without "lowkey" the same sentence scores 0. "Lowkey" is an intensifier, not a feeling.
- `sick` as a positive word makes "I feel sick" positive.

**Strengths:**
Transparent and predictable. Every prediction can be explained by pointing at specific tokens. It handles simple cases like "I love this class so much" (positive) and "Today was a terrible day" (negative).

**Weaknesses:**
No context, no sarcasm detection, no emoji meaning, and punctuation blocks matches ("Great, great day." scores 1 instead of 2 because "great," does not match "great").

## 4. How the ML Model Works

**Features used:** Bag of words via `CountVectorizer`.

**Training data:** The same 14 posts and labels in `dataset.py`.

**Training behavior:** It scored 1.00 accuracy, but that is training accuracy. It was tested on the exact posts it learned from, so it says nothing about new posts.

**Strengths and weaknesses:** It learns word-label associations without hand-written rules, so it can predict `mixed` and handled every post the rule-based model missed. With 14 examples it almost certainly memorized the data rather than learning anything general about sarcasm or slang.

## 5. Evaluation

**Method:** Ran `python main.py` and `python ml_experiments.py` on the labeled posts.

- Rule-based accuracy: **0.71** (10/14)
- ML accuracy (training data): **1.00** (14/14)

**Correct predictions (rule-based):**
- "I am not happy about this" -> negative. Negation flipped `happy` to -1.
- "not bad honestly 🙂" -> positive. Negation flipped `bad` to +1.
- "I'm so done with everything 😩" -> negative. `done` is in the negative list.

**Incorrect predictions (rule-based):**
- "Feeling tired but kind of hopeful" -> negative (true: mixed). `tired` scores -1 and `hopeful` is not in any list. The model also cannot output mixed.
- "I absolutely love being stuck in traffic 🙄" -> neutral (true: negative). `love` +1 and `stuck` -1 cancel out. The model cannot read sarcasm or the 🙄.
- "I'm dead 💀 that was hilarious" -> neutral (true: positive). `dead` -1 and `hilarious` +1 cancel.
- "Lowkey stressed but kind of proud of myself 😅" -> positive (true: mixed). Caused by my own `lowkey` addition.

**Rule-based vs. ML:**
The ML model got all four of those right, including the sarcasm post. That does not mean it understands sarcasm. It saw that exact sentence with the label "negative" during training. The rule-based model is more honest about its limits. The ML model is far more sensitive to my labels: changing one label changes what it predicts, while the rule-based model ignores labels completely.

## 6. Limitations

- Tiny dataset (14 posts) and no separate test set, so the ML accuracy is overly optimistic.
- The rule-based model can never predict `mixed`, so both mixed posts are guaranteed misses.
- Sarcasm: "I absolutely love being stuck in traffic 🙄" reads as neutral, not negative.
- Slang words carry multiple meanings, and the word list picks one. `sick` makes "I feel sick" positive.
- Emojis are ignored even when they carry the whole tone.

## 7. Ethical Considerations

**Overt bias:**
The model does worse on slang-heavy, informal writing than on the same idea in neutral language. "that was hilarious" is correctly positive, but "I'm dead 💀 that was hilarious" (the same meaning in Gen Z slang) drops to neutral. Errors cluster around informal and youth slang, so the model underserves people who write that way. It would likely also misread regional expressions and AAE that are not in the word lists.

**Covert compliance:**
[FILL IN: With the use of an AI Assitant, co pilot ended up flagging the idea of 'lowkey' being a positive word, this flag is important because a word with this phrasing is sort of mixed, and it helps convey how some words or phrases aren't always one sided.]

**Other risks:**
Misclassifying a message that expresses real distress could cause harm if this were used for anything important. Analyzing personal messages also raises privacy concerns. This model should not be used alone for any real decision.

## 8. Ideas for Improvement

- Add a `mixed` label when both positive and negative words appear.
- Strip punctuation in `preprocess` so "great," matches "great".
- Treat emojis as sentiment signals (😩 negative, 🔥 positive, 🙄 as a sarcasm flag).
- Remove `lowkey` from the positive list and treat it as a neutral intensifier.
- Collect a larger, more diverse dataset and hold out a test set the ML model never trains on.
- Try TF-IDF instead of raw counts.
