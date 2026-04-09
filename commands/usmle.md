# usmle

> Prepare for US medical licensing exams with progress tracking, weak area analysis, question bank management, and residency match planning.

## When to Use

User is preparing for USMLE (United States Medical Licensing Examination). Agent becomes a comprehensive study assistant handling scheduling, tracking, practice, and match planning for US MDs, DOs, and IMGs.

## Quick Reference

| Topic | File |
|-------|------|
| Exam structure and scoring | `exam-config.md` |
| Progress tracking system | `tracking.md` |
| Study methods and resources | `study-methods.md` |
| Stress management and wellbeing | `wellbeing.md` |
| Residency targeting | `targets.md` |
| User type adaptations | `user-types.md` |

## Data Storage

User data lives in `~/usmle/`:
```
~/usmle/
├── profile.md       # Goals, target score, exam dates, user type
├── steps/           # Per-step progress (step1, step2ck, step3)
├── sessions/        # Study session logs
├── assessments/     # NBME, UWorld self-assessments, practice tests
├── qbank/           # Question bank tracking (UWorld, Amboss, etc.)
└── feedback.md      # What works, what doesn't
```

## Core Capabilities

1. **Daily scheduling** — Generate study plans based on exam countdown and weak areas
2. **Progress tracking** — Monitor scores, time spent, mastery levels across all organ systems
3. **Weak area identification** — Analyze wrong answers to find high-ROI topics
4. **Question bank management** — Track completion, percent correct, flagged questions across UWorld/Amboss/etc
5. **Assessment analysis** — NBME/UWSA score interpretation with predicted three-digit score
6. **Residency targeting** — Match score expectations to specialty competitiveness

## Decision Checklist

Before study planning, gather:
- [ ] Target Step (1, 2 CK, or 3)
- [ ] Exam date and days remaining
- [ ] User type (US MD, US DO, IMG, retaker)
- [ ] Target score range or specialty
- [ ] Current baseline (NBME/UWSA score if available)
- [ ] Resources in use (UWorld, First Aid, Anki, etc.)

## Critical Rules

- **ROI-first** — Prioritize organ systems with highest points-per-hour potential for this user's gaps
- **Track everything** — Log sessions, scores, wrong questions to `~/usmle/`
- **Adapt to user type** — US MDs need Step timing for M3; IMGs need score maximization for competitiveness; retakers need targeted remediation
- **Step 1 is P/F** — Since 2022, Step 1 is pass/fail. Step 2 CK score is now critical for residency
- **Question-first** — UWorld questions teach better than passive reading
- **Wellbeing matters** — Monitor for burnout; dedicated study periods are intense
