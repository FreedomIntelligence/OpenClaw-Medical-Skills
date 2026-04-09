# crisis-detection-intervention-ai

> Detect crisis signals in user content using NLP, mental health sentiment analysis, and safe intervention protocols. Implements suicide ideation detection, automated escalation, and crisis resource integration. Use for mental health apps, recovery platforms, support communities. Activate on "crisis detection", "suicide prevention", "mental health NLP", "intervention protocol". NOT for general sentiment analysis, medical diagnosis, or replacing professional help.

**Available tools:** R, e, a, d, ,, W, r, i, t, E, B, s, h, (, n, p, m, :, *, )

# Crisis Detection & Intervention AI

Expert in detecting mental health crises and implementing safe, ethical intervention protocols.

## ⚠️ ETHICAL DISCLAIMER

**This skill assists with crisis detection, NOT crisis response**.

✅ **Appropriate uses**:
- Flagging concerning content for human review
- Connecting users to professional resources
- Escalating to crisis counselors
- Providing immediate hotline information

❌ **NOT a substitute for**:
- Licensed therapists
- Emergency services (911)
- Medical diagnosis
- Professional mental health treatment

**Always provide crisis hotlines**: National Suicide Prevention Lifeline: 988

---

## When to Use

✅ **Use for**:
- Mental health journaling apps
- Recovery community platforms
- Support group monitoring
- Online therapy platforms
- Crisis text line integration

❌ **NOT for**:
- General sentiment analysis (use standard tools)
- Medical diagnosis (not qualified)
- Automated responses without human review
- Replacing professional crisis counselors

## Quick Decision Tree

```
Detected concerning content?
├── Immediate danger? → Escalate to crisis counselor + show 988
├── Suicidal ideation? → Flag for review + show resources
├── Substance relapse? → Connect to sponsor + resources
├── Self-harm mention? → Gentle check-in + resources
└── General distress? → Supportive response + resources
```

---

## Technology Selection

### NLP Models for Mental Health (2024)

| Model | Best For | Accuracy | Latency |
|-------|----------|----------|---------|
| MentalBERT | Mental health text | 89% | 50ms |
| GPT-4 + Few-shot | Crisis detection | 92% | 200ms |
| RoBERTa-Mental | Depression detection | 87% | 40ms |
| Custom Fine-tuned BERT | Domain-specific | 90%+ | 60ms |

**Timeline**:
- 2019: BERT fine-tuned for mental health
- 2021: MentalBERT released
- 2023: GPT-4 shows strong zero-shot crisis detection
- 2024: Specialized models for specific conditions

---

## Common Anti-Patterns

### Anti-Pattern 1: Using Generic Sentiment Analysis

**Novice thinking**: "Negative sentiment = crisis"

**Problem**: Mental health language is nuanced, context-dependent.

**Wrong approach**:
```typescript
// ❌ Generic sentiment misses mental health signals
const sentiment = analyzeSentiment(text);

if (sentiment.score < -0.5) {
  alertCrisis();  // Too broad!
}
```

**Why wrong**: "I'm tired" vs "I'm tired of living" - different meanings, same sentiment.

**Correct approach**:
```typescript
// ✅ Mental health-specific model
import { pipeline } from '@huggingface/transformers';

const detector = await pipeline('text-classification', 'mental/bert-base-uncased');

const result = await detector(text, {
  labels: ['suicidal_ideation', 'self_harm', 'substance_relapse', 'safe']
});

if (result[0].label === 'suicidal_ideation' && result[0].score > 0.8) {
  await escalateToCrisisCounselor({
    text,
    confidence: result[0].score,
    timestamp: Date.now()
  });

  // IMMEDIATELY show crisis resources
  showCrisisResources({
    phone: '988',
    text: 'Text "HELLO" to 741741',
    chat: 'https://988lifeline.org/chat'
  });
}
```

**Timeline context**:
- 2015: Rule-based keyword matching
- 2020: BERT fine-tuning for mental health
- 2024: Multi-label models with context understanding

---

### Anti-Pattern 2: Automated Responses Without Human Review

**Problem**: AI cannot replace empathy, may escalate distress.

**Wrong approach**:
```typescript
// ❌ AI auto-responds to crisis
if (isCrisis(text)) {
  await sendMessage(userId, "I'm concerned about you. Are you okay?");
}
```

**Why wrong**:
- Feels robotic, invalidating
- May increase distress
- No human judgment

**Correct approach**:
```typescript
// ✅ Flag for human review, show resources
if (isCrisis(text)) {
  // 1. Flag for counselor review
  await flagForReview({
    userId,
    text,
    severity: 'high',
    detectedAt: Date.now(),
    requiresImmediate: true
  });

  // 2. Notify on-call counselor
  await notifyOnCallCounselor({
    userId,
    summary: 'Suicidal ideation detected',
    urgency: 'immediate'
  });

  // 3. Show resources (no AI message)
  await showInAppResources({
    type: 'crisis_support',
    resources: [
      { name: '988 Suicide & Crisis Lifeline', link: 'tel:988' },
      { name: 'Crisis Text Line', link: 'sms:741741' },
      { name: 'Chat Now', link: 'https://988lifeline.org/chat' }
    ]
  });

  // 4. DO NOT send automated "are you okay" message
}
```

**Human review flow**:
```
AI Detection → Flag → On-call counselor notified → Human reaches out
```

---

### Anti-Pattern 3: Not Providing Immediate Resources

**Problem**: User in crisis needs help NOW, not later.

**Wrong approach**:
```typescript
// ❌ Just flags, no immediate help
if (isCrisis(text)) {
  await logCrisisEvent(userId, text);
  // User left with no resources
}
```

**Correct approach**:
```typescript
// ✅ Immediate resources + escalation
if (isCrisis(text)) {
  // Show resources IMMEDIATELY (blocking modal)
  await showCrisisModal({
    title: 'Resources Available',
    resources: [
      {
        name: '988 Suicide & Crisis Lifeline',
        description: 'Free, confidential support 24/7',
        action: 'tel:988',
        type: 'phone'
      },
      {
        name: 'Crisis Text Line',
        description: 'Text support with trained counselor',
        action: 'sms:741741',
        message: 'HELLO',
        type: 'text'
      },
      {
        name: 'Chat with counselor',
        description: 'Online chat support',
        action: 'https://988lifeline.org/chat',
        type: 'web'
      }
    ],
    dismissible: true,  // User can close, but resources shown first
    analytics: { event: 'crisis_resources_shown', source: 'ai_detection' }
  });

  // Then flag for follow-up
  await flagForReview({ userId, text, severity: 'high' });
}
```

---

### Anti-Pattern 4: Storing Crisis Data Insecurely

**Problem**: Crisis content is extremely sensitive PHI.

**Wrong approach**:
```typescript
// ❌ Plain text storage
await db.logs.insert({
  userId: user.id,
  type: 'crisis',
  content: text,  // Stored in plain text!
  timestamp: Date.now()
});
```

**Why wrong**: Data breach exposes most vulnerable moments.

**Correct approach**:
```typescript
// ✅ Encrypted, access-logged, auto-deleted
import { encrypt, decrypt } from './encryption';

await db.crisisEvents.insert({
  id: generateId(),
  userId: hashUserId(user.id),  // Hash, not plain ID
  contentHash: hashContent(text),  // For deduplication only
  encryptedContent: encrypt(text, process.env.CRISIS_DATA_KEY),
  detectedAt: Date.now(),
  reviewedAt: null,
  reviewedBy: null,
  autoDeleteAt: Date.now() + (30 * 24 * 60 * 60 * 1000),  // 30 days
  accessLog: []
});

// Log all access
await logAccess({
  eventId: crisisEvent.id,
  accessedBy: counselorId,
  accessedAt: Date.now(),
  reason: 'Review for follow-up',
  ipAddress: hashedIp
});

// Auto-delete after retention period
schedule.daily(() => {
  db.crisisEvents.deleteMany({
    autoDeleteAt: { $lt: Date.now() }
  });
});
```

**HIPAA Requirements**:
- Encryption at rest and in transit
- Access logging
- Auto-deletion after retention period
- Minimum necessary access

---

### Anti-Pattern 5: No Escalation Protocol

**Problem**: No clear path from detection to human intervention.

**Wrong approach**:
```typescript
// ❌ Flags crisis but no escalation process
if (isCrisis(text)) {
  await db.flags.insert({ userId, text, flaggedAt: Date.now() });
  // Now what? Who responds?
}
```

**Correct approach**:
```typescript
// ✅ Clear escalation protocol
enum CrisisSeverity {
  LOW = 'low',        // Distress, no immediate danger
  MEDIUM = 'medium',  // Self-harm thoughts, no plan
  HIGH = 'high',      // Suicidal ideation with plan
  IMMEDIATE = 'immediate'  // Imminent danger
}

async function escalateCrisis(detection: CrisisDetection): Promise<void> {
  const severity = assessSeverity(detection);

  switch (severity) {
    case CrisisSeverity.IMMEDIATE:
      // Notify on-call counselor (push notification)
      await notifyOnCall({
        userId: detection.userId,
        severity,
        requiresResponse: 'immediate',
        text: detection.text
      });

      // Send SMS to backup on-call if no response in 5 min
      setTimeout(async () => {
        if (!await hasResponded(detection.id)) {
          await notifyBackupOnCall(detection);
        }
      }, 5 * 60 * 1000);

      // Show 988 modal (blocking)
      await show988Modal(detection.userId);
      break;

    case CrisisSeverity.HIGH:
      // Notify on-call counselor (email + push)
      await notifyOnCall({ severity, requiresResponse: '1 hour' });

      // Show crisis resources
      await showCrisisResources(detection.userId);
      break;

    case CrisisSeverity.MEDIUM:
      // Add to review queue for next business day
      await addToReviewQueue({ priority: 'high' });

      // Suggest self-help resources
      await suggestResources(detection.userId, 'coping_strategies');
      break;

    case CrisisSeverity.LOW:
      // Add to review queue
      await addToReviewQueue({ priority: 'normal' });
      break;
  }

  // Always log for audit
  await logEscalation({
    detectionId: detection.id,
    severity,
    actions: ['notified_on_call', 'showed_resources'],
    timestamp: Date.now()
  });
}
```

---

## Implementation Patterns

### Pattern 1: Multi-Signal Detection

```typescript
interface CrisisSignal {
  type: 'suicidal_ideation' | 'self_harm' | 'substance_relapse' | 'severe_distress';
  confidence: number;
  evidence: string[];
}

async function detectCrisisSignals(text: string): Promise<CrisisSignal[]> {
  const signals: CrisisSignal[] = [];

  // Signal 1: NLP model
  const nlpResult = await mentalHealthNLP(text);
  if (nlpResult.score > 0.75) {
    signals.push({
      type: nlpResult.label,
      confidence: nlpResult.score,
      evidence: ['NLP model detection']
    });
  }

  // Signal 2: Keyword matching (backup)
  const keywords = detectKeywords(text);
  if (keywords.length > 0) {
    signals.push({
      type: 'suicidal_ideation',
      confidence: 0.6,
      evidence: keywords
    });
  }

  // Signal 3: Sentiment + context
  const sentiment = await sentimentAnalysis(text);
  const hasHopelessness = /no (hope|point|reason|future)/i.test(text);

  if (sentiment.score < -0.8 && hasHopelessness) {
    signals.push({
      type: 'severe_distress',
      confidence: 0.7,
      evidence: ['Extreme negative sentiment + hopelessness language']
    });
  }

  return signals;
}
```

### Pattern 2: Safe Keyword Matching

```typescript
const CRISIS_KEYWORDS = {
  suicidal_ideation: [
    /\b(kill|end|take)\s+(my|own)\s+life\b/i,
    /\bsuicide\b/i,
    /\bdon'?t\s+want\s+to\s+(live|be here|exist)\b/i,
    /\bbetter off dead\b/i
  ],
  self_harm: [
    /\b(cut|cutting|hurt)\s+(myself|me)\b/i,
    /\bself[- ]harm\b/i
  ],
  substance_relapse: [
    /\b(relapsed|used|drank)\s+(again|today)\b/i,
    /\bback on\s+(drugs|alcohol)\b/i
  ]
};

function detectKeywords(text: string): string[] {
  const matches: string[] = [];

  for (const [type, patterns] of Object.entries(CRISIS_KEYWORDS)) {
    for (const pattern of patterns) {
      if (pattern.test(text)) {
        matches.push(type);
      }
    }
  }

  return [...new Set(matches)];  // Deduplicate
}
```

### Pattern 3: GPT-4 Few-Shot Detection

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

async function detectWithClaude(text: string): Promise<CrisisDetection> {
  const response = await client.messages.create({
    model: 'claude-3-5-sonnet-20241022',
    max_tokens: 200,
    messages: [{
      role: 'user',
      content: `You are a mental health crisis detection system. Analyze this text for crisis signals.

Text: "${text}"

Respond in JSON:
{
  "is_crisis": boolean,
  "severity": "none" | "low" | "medium" | "high" | "immediate",
  "signals": ["suicidal_ideation" | "self_harm" | "substance_relapse"],
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}

Examples:
- "I'm thinking about ending it all" → { "is_crisis": true, "severity": "high", "signals": ["suicidal_ideation"], "confidence": 0.95 }
- "I relapsed today, feeling ashamed" → { "is_crisis": true, "severity": "medium", "signals": ["substance_relapse"], "confidence": 0.9 }
- "Had a tough day at work" → { "is_crisis": false, "severity": "none", "signals": [], "confidence": 0.95 }`
    }]
  });

  const result = JSON.parse(response.content[0].text);
  return result;
}
```

---

## Production Checklist

```
□ Mental health-specific NLP model (not generic sentiment)
□ Human review required before automated action
□ Crisis resources shown IMMEDIATELY (988, text line)
□ Clear escalation protocol (severity-based)
□ Encrypted storage of crisis content
□ Access logging for all crisis data access
□ Auto-deletion after retention period (30 days)
□ On-call counselor notification system
□ Backup notification if no response
□ False positive tracking (improve model)
□ Regular model evaluation with experts
□ Ethics review board approval
```

---

## When to Use vs Avoid

| Scenario | Appropriate? |
|----------|--------------|
| Journaling app for recovery | ✅ Yes - monitor for relapses |
| Support group chat | ✅ Yes - flag concerning posts |
| Therapy platform messages | ✅ Yes - assist therapists |
| Public social media | ❌ No - privacy concerns |
| Replace human counselors | ❌ Never - AI assists, doesn't replace |
| Medical diagnosis | ❌ Never - not qualified |

---

## References

- `/references/mental-health-nlp.md` - NLP models for mental health
- `/references/intervention-protocols.md` - Evidence-based intervention strategies
- `/references/crisis-resources.md` - Hotlines, text lines, and support services

## Scripts

- `scripts/crisis_detector.ts` - Real-time crisis detection system
- `scripts/model_evaluator.ts` - Evaluate detection accuracy with test cases

---

**This skill guides**: Crisis detection | Mental health NLP | Intervention protocols | Suicide prevention | HIPAA compliance | Ethical AI
