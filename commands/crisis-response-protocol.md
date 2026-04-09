# crisis-response-protocol

> Handle mental health crisis situations in AI coaching safely. Use when implementing crisis detection, safety protocols, emergency escalation, or suicide prevention features. Activates for crisis keywords, safety planning, hotline integration, and risk assessment.

**Available tools:** R, e, a, d, ,, W, r, i, t, E

# Crisis Response Protocol

This skill helps you implement safe crisis intervention features for the AI coaching system, following mental health best practices.

## When to Use

✅ **USE this skill for:**
- Implementing crisis detection in recovery/mental health apps
- Building safety planning features
- Integrating hotline and emergency resource displays
- Designing risk assessment interfaces
- Creating escalation protocols for AI chat systems

❌ **DO NOT use for:**
- **Responding to an actual crisis yourself** → Call 988 or emergency services
- General mental health content → use `sober-addict-protector` or `recovery-coach-patterns`
- Medical advice or diagnosis → Always defer to licensed professionals
- Replacing human crisis counselors → AI should augment, never replace

## Critical Safety Principle

> **AI should NEVER be the sole responder in acute crisis situations.**
> Always provide pathways to human support and emergency services.

## Crisis Detection

### Risk Indicator Categories

```typescript
interface RiskIndicators {
  // PRIMARY - Immediate escalation required
  primary: {
    suicidalIdeation: string[];      // "want to die", "end it all"
    selfHarmIntent: string[];         // "hurt myself", "cutting"
    homicidalIdeation: string[];      // "hurt someone"
    activeSubstanceEmergency: string[]; // "overdosed", "can't stop"
  };

  // SECONDARY - Elevated monitoring
  secondary: {
    severeDepression: string[];       // "hopeless", "no point"
    panicSymptoms: string[];          // "can't breathe", "heart racing"
    psychoticSymptoms: string[];      // "hearing voices"
    severeAnxiety: string[];          // "terrified", "losing control"
  };

  // TERTIARY - Check-in triggers
  tertiary: {
    isolationPatterns: string[];      // "no one cares", "alone"
    substanceRelapse: string[];       // "started using", "slipped"
    hopelessness: string[];           // "never get better"
  };
}
```

### Detection Implementation

```typescript
// src/lib/ai/crisis-detection.ts

export interface CrisisAssessment {
  level: 'none' | 'low' | 'medium' | 'high' | 'critical';
  indicators: string[];
  recommendedAction: CrisisAction;
  timestamp: Date;
}

export type CrisisAction =
  | 'continue_conversation'
  | 'gentle_check_in'
  | 'safety_resources'
  | 'crisis_protocol'
  | 'emergency_escalation';

export function assessCrisisLevel(
  messageContent: string,
  conversationHistory: Message[],
  userCheckInHistory: CheckIn[]
): CrisisAssessment {
  const indicators: string[] = [];
  let level: CrisisAssessment['level'] = 'none';

  // Check primary indicators (critical)
  if (hasPrimaryIndicators(messageContent)) {
    level = 'critical';
    indicators.push('primary_risk_detected');
  }

  // Check secondary indicators
  if (hasSecondaryIndicators(messageContent)) {
    level = level === 'none' ? 'high' : level;
    indicators.push('secondary_risk_detected');
  }

  // Check pattern indicators from history
  if (hasWorseningPattern(userCheckInHistory)) {
    level = level === 'none' ? 'medium' : level;
    indicators.push('worsening_trend');
  }

  // Check conversation escalation
  if (hasEscalatingDistress(conversationHistory)) {
    level = level === 'none' ? 'medium' : level;
    indicators.push('escalating_distress');
  }

  return {
    level,
    indicators,
    recommendedAction: getRecommendedAction(level),
    timestamp: new Date(),
  };
}
```

## Tiered Response Protocol

### Level 1: Continue Conversation (No Crisis)
Normal AI coaching interaction.

### Level 2: Gentle Check-In (Low Risk)

```typescript
const gentleCheckInResponse = `
I want to make sure I understand how you're feeling.
It sounds like you're going through a difficult time.

Would you like to:
- Talk more about what's on your mind?
- Try a grounding exercise together?
- Look at some coping strategies?

I'm here to listen.
`;
```

### Level 3: Safety Resources (Medium Risk)

```typescript
const safetyResourcesResponse = `
I hear that you're struggling, and I want you to know that support is available.

Here are some resources that might help:
📞 988 Suicide & Crisis Lifeline: Call or text 988
💬 Crisis Text Line: Text HOME to 741741
🌐 SAMHSA Helpline: 1-800-662-4357

Would you like to talk about what's going on, or would connecting with one of these resources feel right?
`;
```

### Level 4: Crisis Protocol (High Risk)

```typescript
const crisisProtocolResponse = `
I'm concerned about what you've shared, and I want to make sure you're safe.

Right now, I'd like you to consider reaching out to someone who can help:

🆘 If you're in immediate danger: Call 911
📞 988 Suicide & Crisis Lifeline: Call or text 988 (24/7)
💬 Crisis Text Line: Text HOME to 741741

These are trained counselors who understand what you're going through.

Is there someone you trust - a friend, family member, or sponsor - who you could reach out to right now?

I'm still here with you.
`;
```

### Level 5: Emergency Escalation (Critical)

```typescript
const emergencyResponse = `
I'm very concerned about your safety right now.

🆘 Please call 911 or go to your nearest emergency room immediately.

If you can't do that, please call 988 right now - they can help.

Your life matters. Please reach out for help right now.

[EMERGENCY CONTACTS DISPLAYED]
`;

// System action: Flag for human review, notify emergency contact if configured
```

## Implementation in Chat Handler

```typescript
// src/lib/ai/chat-handler.ts

export async function handleChatMessage(
  message: string,
  conversationId: string,
  userId: string
): Promise<ChatResponse> {
  // 1. Assess crisis level BEFORE generating AI response
  const crisisAssessment = await assessCrisisLevel(
    message,
    await getConversationHistory(conversationId),
    await getUserCheckIns(userId, 7)
  );

  // 2. Log assessment (for safety review)
  await logCrisisAssessment(userId, conversationId, crisisAssessment);

  // 3. Handle based on level
  if (crisisAssessment.level === 'critical') {
    // Don't use AI - provide immediate crisis response
    await notifyEmergencyContact(userId);
    await flagForHumanReview(conversationId, 'critical_crisis');

    return {
      message: emergencyResponse,
      showEmergencyContacts: true,
      disableChat: true,  // Prevent further AI interaction
      crisisLevel: 'critical',
    };
  }

  if (crisisAssessment.level === 'high') {
    // Provide crisis resources, continue with caution
    await flagForHumanReview(conversationId, 'high_risk');

    return {
      message: crisisProtocolResponse,
      showCrisisResources: true,
      crisisLevel: 'high',
    };
  }

  // 4. For lower levels, proceed with AI but inject safety context
  const systemPrompt = getSystemPromptWithSafetyContext(crisisAssessment);

  const aiResponse = await generateAIResponse(message, systemPrompt);

  // 5. Post-process AI response for safety
  const safeResponse = await validateResponseSafety(aiResponse);

  return {
    message: safeResponse,
    crisisLevel: crisisAssessment.level,
  };
}
```

## Safety Resources Database

```typescript
// src/lib/crisis/resources.ts

export const crisisResources = {
  national: [
    {
      name: '988 Suicide & Crisis Lifeline',
      phone: '988',
      text: '988',
      url: 'https://988lifeline.org',
      available: '24/7',
      description: 'Free, confidential crisis support',
    },
    {
      name: 'Crisis Text Line',
      text: 'HOME to 741741',
      url: 'https://www.crisistextline.org',
      available: '24/7',
      description: 'Text-based crisis support',
    },
    {
      name: 'SAMHSA National Helpline',
      phone: '1-800-662-4357',
      url: 'https://www.samhsa.gov/find-help/national-helpline',
      available: '24/7',
      description: 'Substance abuse and mental health referrals',
    },
  ],

  recovery: [
    {
      name: 'AA Hotline',
      phone: '1-800-839-1686',
      url: 'https://www.aa.org',
      description: 'Alcoholics Anonymous support',
    },
    {
      name: 'NA Helpline',
      phone: '1-818-773-9999',
      url: 'https://na.org',
      description: 'Narcotics Anonymous support',
    },
  ],

  specialized: [
    {
      name: 'Veterans Crisis Line',
      phone: '988 (press 1)',
      text: '838255',
      description: 'For veterans and service members',
    },
    {
      name: 'Trevor Project',
      phone: '1-866-488-7386',
      text: 'START to 678-678',
      description: 'LGBTQ+ youth crisis support',
    },
  ],
};
```

## Emergency Contact System

```typescript
// src/lib/crisis/emergency-contacts.ts

export async function notifyEmergencyContact(userId: string): Promise<void> {
  const contacts = await getEmergencyContacts(userId);

  if (contacts.length === 0) {
    // Log that no emergency contact was available
    await logCrisisEvent(userId, 'no_emergency_contact');
    return;
  }

  const primaryContact = contacts[0];

  // Send notification (SMS, email, or push)
  await sendEmergencyNotification(primaryContact, {
    type: 'crisis_alert',
    message: `${userName} may be in crisis and could use your support. ` +
             `Please reach out to them if you can.`,
    // Never include conversation content - privacy
  });

  // Audit log
  await logCrisisEvent(userId, 'emergency_contact_notified', {
    contactId: primaryContact.id,
  });
}
```

## Safety Guardrails for AI

```typescript
// Prompt injection for safety context
const safetySystemPrompt = `
CRITICAL SAFETY INSTRUCTIONS:
1. You are NOT a therapist or crisis counselor
2. For ANY mention of self-harm, suicide, or harming others:
   - Express genuine concern
   - Provide crisis resources (988, Crisis Text Line)
   - Encourage professional help
   - Do NOT attempt to counsel through crisis
3. Never minimize feelings or use toxic positivity
4. Never promise confidentiality about safety concerns
5. Always validate emotions while encouraging professional support
6. If user mentions relapse, acknowledge and provide SAMHSA helpline
`;

// Response validation
async function validateResponseSafety(response: string): Promise<string> {
  const unsafePatterns = [
    /don't (call|reach out|get help)/i,
    /you don't need (help|therapy|a professional)/i,
    /just (think positive|be happy|get over it)/i,
    /it's not that (bad|serious)/i,
  ];

  for (const pattern of unsafePatterns) {
    if (pattern.test(response)) {
      // Flag for review and return safe fallback
      await flagForReview('unsafe_response_pattern');
      return getSafeFallbackResponse();
    }
  }

  return response;
}
```

## Audit & Compliance

```typescript
// All crisis events must be logged for review
export async function logCrisisEvent(
  userId: string,
  eventType: CrisisEventType,
  details?: Record<string, unknown>
): Promise<void> {
  await db.insert(crisisEvents).values({
    id: generateId(),
    userId,
    eventType,
    details: JSON.stringify(sanitizeDetails(details)),
    createdAt: new Date(),
    reviewed: false,  // Requires human review
  });

  // Critical events trigger immediate notification
  if (isCriticalEvent(eventType)) {
    await notifyOnCallStaff(userId, eventType);
  }
}
```

## Testing Crisis Features

```typescript
// NEVER use real crisis content in tests
describe('Crisis Detection', () => {
  it('detects high-risk indicators', () => {
    // Use clearly artificial test phrases
    const result = assessCrisisLevel(
      '[TEST_HIGH_RISK_INDICATOR]',
      [],
      []
    );
    expect(result.level).toBe('high');
  });

  it('provides appropriate resources', () => {
    const response = getCrisisResponse('high');
    expect(response).toContain('988');
    expect(response).toContain('Crisis Text Line');
  });
});
```

## References

- [988 Suicide & Crisis Lifeline](https://988lifeline.org)
- [SAMHSA Guidelines](https://www.samhsa.gov)
- [AI in Mental Health - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10242473/)
- [Crisis Chatbot Safety - Nature](https://www.nature.com/articles/s41598-025-17242-4)
