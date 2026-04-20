# Deferred Scope: `Docassist` Post-MVP

> This file preserves valuable ideas from the earlier, broader specification without forcing them into MVP.
> Treat it as a structured backlog for later planning, not as a delivery commitment.

## Purpose

The previous version of `docs/SPEC.md` mixed core product intent with advanced domain ideas, technical design, and future-platform ambitions.

Those ideas are preserved here so they can be revisited after the first production release.

---

## 1. Advanced Clinical Features

- clinical significance detection beyond raw score history
- response and remission tracking based on validated thresholds
- therapy review windows tied to medication start date or dose changes
- rule-based "no improvement" detection after a configured evaluation period
- richer safety classification with `info`, `warning`, and `critical` levels
- therapy review notes and structured doctor follow-up decisions

## 2. Advanced Analytics

- dedicated analytics views for trend interpretation
- cross-scale comparison over time
- comorbidity analysis based on which scale improves first
- medication-effect views that correlate adherence, dose, and score changes
- dashboard metrics optimized for large patient panels

## 3. Expanded Alerting

- overdue questionnaire reminders
- medication review due alerts
- deterioration alerts based on percentage worsening rules
- alert acknowledgement workflows across the doctor dashboard
- broader reminder system for both doctor and patient

## 4. Admin And Configuration Expansion

- medication catalog management
- questionnaire template management beyond the initial fixed set
- specialty-aware catalogs and rules
- broader operational dashboards and system statistics

## 5. Platform Expansion

- multi-specialty support beyond psychiatry
- shared records across clinics or teams
- mobile-native applications
- EMR/EHR integration
- pharmacy or e-prescribing integration

## 6. Technical Ideas Preserved From The Previous Spec

These were present in the earlier draft and may still be useful later:

- specialty-agnostic data model
- full audit trail for all clinical data access
- large explicit SQL schema in the spec
- exhaustive endpoint inventory in the spec
- detailed frontend page and component inventory in the spec
- CI and infra requirements embedded directly in the spec

For the current template, these details should usually live elsewhere:

- product intent in `docs/SPEC.md`
- architecture and boundaries in `docs/ARCHITECTURE.md`
- validation commands in `docs/TESTING.md`
- stack specifics in `docs/STACK.md`
- exact implementation contracts in `docs/PHASE_XX.md`

## 7. Candidate Release Order After MVP

1. Expand safety and reminder workflows.
2. Add richer doctor analytics and therapy review support.
3. Generalize configuration and admin tooling.
4. Re-evaluate multi-specialty expansion.
5. Consider external integrations only after the core workflow is stable in production.
