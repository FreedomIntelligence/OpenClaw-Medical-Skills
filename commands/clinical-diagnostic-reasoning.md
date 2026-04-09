# clinical-diagnostic-reasoning

> Identify and counteract cognitive biases in medical decision-making through systematic error analysis and contextual algorithm application. For diagnostic reasoning, treatment decisions, and clinical judgment improvement. NOT for basic medical knowledge, technical procedures, or non-clinical healthcare domains.

**Available tools:** R, e, a, d

# Clinical Diagnostic Reasoning
Improve diagnostic accuracy and treatment decisions by recognizing and overcoming systematic cognitive errors in clinical thinking.

## When to Use
✅ Use for:
- Diagnostic decision-making in clinical practice
- Treatment planning and therapeutic choices
- Case review and error analysis
- Medical education on clinical reasoning
- Patient communication and shared decision-making
- Quality improvement and patient safety initiatives

❌ NOT for:
- Learning basic medical facts or pathophysiology
- Technical procedures or surgical skills
- Healthcare administration or policy
- Non-physician clinical roles without diagnostic responsibility
- Population health management without individual patient focus

## Core Process

### Diagnostic Reasoning Flow
```
New patient presentation
    ↓
┌───[Gather information through language/history]
│   ↓
│   Does presentation suggest standard algorithm?
│   ├─ NO → Continue hypothesis generation
│   │         ↓
│   │         Develop differential diagnosis
│   │         ↓
│   │         [Proceed to bias check]
│   │
│   └─ YES → Does patient context match algorithm assumptions?
│             ├─ YES → Apply algorithm
│             │         ↓
│             │         Monitor outcomes
│             │         ↓
│             │         [Proceed to bias check]
│             │
│             └─ NO → What patient-specific factors differ?
│                     ↓
│                     Does evidence justify deviation?
│                     ├─ YES → Document rationale and modify
│                     └─ NO → Apply algorithm; reconsider if new data
│
└─── [BIAS CHECK - Always perform]
     ↓
     Am I anchored to initial impression?
     ├─ POSSIBLY → Reassess case without initial anchor
     │
     Have I found one explanation and stopped searching?
     ├─ YES → Continue search: "What else could this be?"
     │         "Does this explain ALL findings?"
     │
     Am I pattern-matching from recent/memorable case?
     ├─ YES → List specific differences between cases
     │
     Am I stereotyping this patient?
     ├─ POSSIBLY → Reset: Evaluate symptoms independently
     │
     Do I feel compelled to "do something"?
     ├─ YES → Is action justified by evidence or anxiety?
     │         Is watchful waiting appropriate?
     │
     Have I sought disconfirming evidence?
     └─ NO → Actively look for data that contradicts working diagnosis
```

### Case-Based Error Analysis Flow
```
Clinical error occurred
    ↓
What was the error?
    ├─ Wrong diagnosis
    ├─ Inappropriate treatment
    └─ Missed diagnosis
    ↓
Was this a knowledge gap or thinking error?
    ├─ KNOWLEDGE GAP → Address through study
    │                   (Not the focus of this skill)
    │
    └─ THINKING ERROR → Which cognitive bias operated?
                        ↓
                        ┌─ Anchoring? (stuck on initial impression)
                        ├─ Satisfaction of search? (stopped too early)
                        ├─ Availability? (recent case pattern-match)
                        ├─ Attribution? (stereotyped patient)
                        └─ Commission? (unnecessary action)
                        ↓
                        Was error preventable with current knowledge?
                        ├─ YES → How could bias have been recognized?
                        │         ↓
                        │         Extract generalizable lesson
                        │         ↓
                        │         Apply to future similar situations
                        │
                        └─ NO → Document for learning, not applicable
```

### Patient Communication Flow
```
Need to present medical information
    ↓
What decision does patient need to make?
    ↓
Identify equivalent framings:
    - Positive frame (% success/survival)
    - Negative frame (% failure/mortality)
    - Absolute numbers
    - Relative risk
    ↓
Which framing facilitates genuine understanding?
    ↓
Is my framing choice unintentionally biasing decision?
    ├─ YES → Present multiple equivalent framings
    │         Allow patient to process from different angles
    │
    └─ UNCERTAIN → Present both positive and negative frames
                    Verify patient comprehension
                    ↓
                    "What is your understanding of the risks/benefits?"
```

## Anti-Patterns

### Satisfaction of Search
**Novice approach:** Finds one clinically interesting explanation and stops diagnostic inquiry. "The patient has pneumonia, that explains the fever and cough."

**Expert approach:** After finding initial explanation, explicitly asks: "What else could be present? Does this explain ALL findings? Could there be a coexisting condition?"

**Timeline:** Develops over years of clinical experience through cases where initial findings were incomplete or coincidental. Critical moment comes when missing a second diagnosis causes patient harm—realization that "not finding everything is suboptimal."

### Anchoring Error
**Novice approach:** Initial symptoms or emergency department triage note establishes diagnosis that persists despite contradictory information. "ED said anxiety attack, so I'm treating anxiety."

**Expert approach:** Periodically resets evaluation without reference to initial impressions. "If I saw this patient fresh right now, what would I think?" Actively seeks information contradicting initial hypothesis.

**Timeline:** Requires recognizing pattern across multiple cases where initial impression proved misleading. Breakthrough occurs when physician catches themselves defending an anchor despite mounting contrary evidence.

### Commission Bias
**Novice approach:** Feels compelled to take action because "doing something" feels better than watchful waiting, even without clear indication. Treats borderline abnormal labs, adjusts medications unnecessarily.

**Expert approach:** Explicitly evaluates whether action is justified by evidence or driven by psychological need to intervene. Comfortable with watchful waiting when appropriate. Asks: "Will treatment help more than harm?"

**Timeline:** Often develops after causing harm through unnecessary intervention. Turning point is recognizing that action carries its own risks and that inaction is sometimes the most appropriate decision.

### Availability Error
**Novice approach:** "I just saw three patients with Lyme disease, so this patient's fatigue must be Lyme too." Pattern-matches based on superficial similarities without considering differences.

**Expert approach:** When noticing similarity to recent case, explicitly lists differences: "How is this patient NOT like that case?" Questions whether similarities are clinically meaningful or coincidental.

**Timeline:** Accumulates through experience with similar-seeming cases that proved different. Key insight comes when a "just like the last patient" case turns out completely different upon deeper investigation.

### Attribution Error
**Novice approach:** Accepts colleague's characterization that patient is "drug-seeking" or "anxious" and dismisses symptoms without independent evaluation. Stereotypes based on demographics.

**Expert approach:** Approaches each patient as individual regardless of others' characterizations. "What does THIS patient's presentation tell me?" Separates objective findings from attributed motivations.

**Timeline:** Often requires personal experience of misjudging a patient or discovering that a dismissed patient had serious pathology. Recognition that stereotypes prevented seeing actual clinical presentation.

### Algorithm Rigidity
**Novice approach:** Either follows algorithms without contextual consideration ("The guideline says X, so I must do X") OR abandons them based on gut feeling without justification.

**Expert approach:** Recognizes algorithms as population-based tools requiring interpretation. Can articulate why specific patient context justifies deviation when it does. Documents reasoning.

**Timeline:** Develops through repeated experience applying guidelines to diverse patients. Critical learning occurs when rigid application causes harm OR when appropriate deviation leads to better outcome—recognizing that expertise lies in knowing which mode applies when.

## Mental Models & Shibboleths

### Core Shibboleths
- **"Not finding everything is suboptimal"** — Expert recognition that diagnostic search shouldn't stop at first finding
- **"Understanding why we get things wrong is essential to understanding how to get things right"** — Expert frame that errors reveal cognitive patterns, not just knowledge gaps
- **Semantic equivalence awareness** — Expert automatically recognizes that "30% chance of improvement" and "70% chance of failure" are clinically identical but psychologically different

### Expert vs Novice Markers
**Novice says:** "The patient has [single diagnosis]"
**Expert says:** "The primary issue is [diagnosis], but I'm also considering [alternatives] and haven't ruled out [other possibilities]"

**Novice says:** "We need to do something"
**Expert says:** "The question is whether intervention offers more benefit than harm compared to watchful waiting"

**Novice says:** "The protocol says..."
**Expert says:** "The protocol applies when [conditions], but this patient differs in [specific ways]"

### Navigation Metaphor
Clinical reasoning requires navigating between two extremes:
- **Rigid shore:** Algorithmic medicine without contextual adaptation
- **Chaos shore:** Intuition-based medicine without evidence grounding
- **Expert navigation:** Knowing when to sail closer to structure (standard presentations) versus when context requires deviation (atypical patients)

### Trap Metaphor
Cognitive biases are predictable traps on the diagnostic path:
- Recognizable once you know what to look for
- Avoidable with deliberate countermeasures
- Universal (even experts fall in, but recognize and escape faster)
- The map of traps can be taught and learned

## References
- Source: "How Doctors Think" by Jerome Groopman
- Domain: Clinical decision-making, diagnostic reasoning, medical cognitive science
- Key insight: Medical errors stem primarily from systematic thinking patterns (cognitive biases) rather than knowledge deficits, and these patterns can be identified, taught, and corrected
