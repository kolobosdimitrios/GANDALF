# Gandalf Demo Intents and Outputs

## Example 1
**User Intent**
"Add a short FAQ section to our landing page so users can find answers quickly."

**Output (CTC)**
```
# Task: Add FAQ section to landing page

## Context
- Landing page exists and needs an FAQ section

## Definition of Done
- [ ] Landing page includes an FAQ section with at least 3 Q&A items
- [ ] FAQ section is placed below the main content
- [ ] The new section renders correctly with existing styles

## Constraints
- Do not change other sections of the page

## Deliverables
- Updated landing page file(s)
```

---

## Example 2
**User Intent**
"Export the monthly sales report."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which format should the report be exported in?
   - Option A: CSV
   - Option B: PDF
   - Option C: XLSX
```

---

## Example 3
**User Intent**
"Make the app faster."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which area should be prioritized for speed improvements?
   - Option A: Page load time
   - Option B: Search results response time
   - Option C: File upload performance
```

---

## Example 4
**User Intent**
"Create onboarding emails for new users: welcome email and a follow-up after 3 days."

**Output (CTC)**
```
# Task: Create onboarding email templates

## Context
- New users need onboarding emails

## Definition of Done
- [ ] Welcome email template is defined
- [ ] Follow-up email template is defined for 3 days after signup
- [ ] Email content includes subject lines and body text

## Constraints
- Use existing brand tone

## Deliverables
- Two email templates (welcome, follow-up)
```

---

## Example 5
**User Intent**
"Set up alerts when daily API errors exceed 2%."

**Output (CTC)**
```
# Task: Configure API error rate alert

## Context
- Alerts are needed for daily API error thresholds

## Definition of Done
- [ ] Alert triggers when daily API error rate exceeds 2%
- [ ] Alert includes error rate percentage in the notification
- [ ] Alert configuration is saved and active

## Constraints
- Do not modify other monitoring rules

## Deliverables
- Alert configuration update
```
