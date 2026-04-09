# hipaa-compliance

> Ensure HIPAA compliance when handling PHI (Protected Health Information). Use when writing code that accesses user health data, check-ins, journal entries, or any sensitive information. Activates for audit logging, data access, security events, and compliance questions.

**Available tools:** R, e, a, d, ,, W, r, i, t, E

# HIPAA Compliance for Recovery Coach

This skill helps you maintain HIPAA compliance when developing features that handle Protected Health Information (PHI).

## What is PHI in This Application?

| Data Type | PHI Status | Handling |
|-----------|------------|----------|
| Check-in mood/cravings | PHI | Audit all access |
| Journal entries | PHI | Audit all access |
| Chat conversations | PHI | Audit all access |
| User profile (name, email) | PHI | Audit modifications |
| Sobriety date | PHI | Audit access |
| Emergency contacts | PHI | Audit access |
| Usage analytics (aggregated) | NOT PHI | No audit needed |
| Page views (no content) | NOT PHI | No audit needed |

## Audit Logging Requirements

### When to Log

**Always log these operations:**
- Viewing any PHI (check-ins, journal, messages)
- Creating/updating/deleting PHI
- Exporting user data
- Admin access to user information
- Failed authentication attempts
- Security events (rate limiting, unauthorized access)

### How to Log

Use the audit logging utilities in `src/lib/hipaa/audit.ts`:

```typescript
import {
  logPHIAccess,
  logPHIModification,
  logSecurityEvent,
  logAdminAction
} from '@/lib/hipaa/audit';

// Viewing PHI
await logPHIAccess(
  userId,
  'checkin',        // targetType
  checkinId,        // targetId
  AuditAction.PHI_VIEW
);

// Modifying PHI
await logPHIModification(
  userId,
  'journal',
  journalId,
  AuditAction.PHI_UPDATE,
  { field: 'content' }  // Never include actual content!
);

// Security event
await logSecurityEvent(
  userId,
  AuditAction.RATE_LIMIT,
  { path: '/api/chat', attempts: 60 }
);

// Admin action
await logAdminAction(
  adminId,
  AuditAction.ADMIN_USER_VIEW,
  'user',
  targetUserId
);
```

## Data Sanitization

### Never Log These Fields

The audit system automatically sanitizes, but be explicit:

```typescript
// BAD - Contains PHI
await logPHIAccess(userId, 'journal', id, action, {
  content: journalEntry.content  // NEVER DO THIS
});

// GOOD - Only metadata
await logPHIAccess(userId, 'journal', id, action, {
  wordCount: journalEntry.content.length,
  hasAttachments: false
});
```

### Sanitized Fields (Auto-Redacted)

- `password`, `token`, `secret`, `key`
- `authorization`, `cookie`, `session`
- `credential`, `content`, `message`, `notes`

## Session Security Requirements

From `src/lib/auth.ts`:

- **Session timeout**: 15 minutes of inactivity (HIPAA requirement)
- **Max session**: 8 hours absolute maximum
- **Failed login lockout**: 5 attempts = 30 minute ban
- **Password requirements**: 12+ chars, mixed case, numbers, special chars

## Code Patterns

### API Route with Audit Logging

```typescript
import { getSession, requireAuth } from '@/lib/auth';
import { logPHIAccess } from '@/lib/hipaa/audit';

export async function GET(request: Request) {
  const session = await getSession();
  if (!session) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Fetch the data
  const data = await fetchUserData(session.userId);

  // Log the access
  await logPHIAccess(
    session.userId,
    'userdata',
    session.userId,
    AuditAction.PHI_VIEW
  );

  return Response.json(data);
}
```

### Component with PHI Access

```typescript
'use client';

import { useEffect } from 'react';

export function JournalViewer({ entryId }: { entryId: string }) {
  useEffect(() => {
    // Log view on mount (server-side preferred, but client backup)
    fetch('/api/audit/log', {
      method: 'POST',
      body: JSON.stringify({
        action: 'PHI_VIEW',
        targetType: 'journal',
        targetId: entryId
      })
    });
  }, [entryId]);

  // ... render
}
```

## Compliance Checklist

Before shipping any feature that touches PHI:

- [ ] All PHI access is audit logged
- [ ] No PHI content in logs (only IDs and metadata)
- [ ] Data access requires authentication
- [ ] Admin access has separate audit trail
- [ ] Failed access attempts are logged
- [ ] Data export includes audit entry
- [ ] Sensitive fields are encrypted at rest
- [ ] Session timeout is enforced

## Audit Log Retention

- **Minimum**: 6 years (HIPAA requirement)
- **Format**: Raw logs for 1 year, compressed thereafter
- **Location**: `audit_log` table in database
- **Export**: Encrypted exports for compliance audits

## Emergency Access (Break Glass)

For emergency situations, use break-glass access:

```typescript
import { requestBreakGlassAccess } from '@/lib/hipaa/break-glass';

// This creates enhanced audit trail
const access = await requestBreakGlassAccess(
  adminId,
  targetUserId,
  'Emergency support required - user reported crisis'
);
```

Break glass access:
- Requires written justification
- Creates permanent audit record
- Triggers alert to compliance officer
- Must be reviewed within 24 hours

## Resources

- HIPAA Security Rule: 45 C.F.R. § 164.312
- Audit controls standard: 45 C.F.R. § 164.312(b)
- Incident response plan: `docs/INCIDENT-RESPONSE-PLAN.md`
- Security documentation: `docs/SECURITY-HARDENING.md`
