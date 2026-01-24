# Gandalf Validation Intents and Outputs

## 1) Software feature request
**User Intent**
"Add dark mode to the mobile app with a toggle in settings."

**Output (CTC)**
```
# Task: Add dark mode toggle in settings

## Context
- Mobile app needs a dark mode option

## Definition of Done
- [ ] Settings includes a dark mode toggle
- [ ] App theme switches between light and dark when toggled
- [ ] Choice persists across app restarts

## Constraints
- Do not change non-UI functionality

## Deliverables
- Updated settings UI
- Theme toggle implementation
```

---

## 2) Vague business need
**User Intent**
"Increase user retention next quarter."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) What retention metric should be targeted?
   - Option A: 30-day active users
   - Option B: Weekly active users
   - Option C: 7-day return rate
```

---

## 3) Bug report
**User Intent**
"Checkout sometimes fails with a blank screen on iOS."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which iOS version is affected?
   - Option A: iOS 16+
   - Option B: iOS 15
   - Option C: All supported iOS versions
```

---

## 4) Non-technical request
**User Intent**
"Write a short thank-you note for new subscribers."

**Output (CTC)**
```
# Task: Draft thank-you note for new subscribers

## Context
- New subscribers need a short thank-you note

## Definition of Done
- [ ] Message includes a greeting
- [ ] Message thanks the subscriber
- [ ] Message is under 60 words

## Constraints
- Use friendly, professional tone

## Deliverables
- Thank-you note text
```

---

## 5) Software feature request
**User Intent**
"Add CSV export to the orders table."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Where should the export be triggered?
   - Option A: Export button above the table
   - Option B: Export option in row actions
   - Option C: Export from a settings menu
```

---

## 6) Vague business need
**User Intent**
"We need better reporting."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) What type of reporting is needed first?
   - Option A: Revenue and sales metrics
   - Option B: User activity metrics
   - Option C: Operational KPIs
```

---

## 7) Bug report
**User Intent**
"The login page shows a 500 error when users reset their password."

**Output (CTC)**
```
# Task: Fix 500 error on password reset

## Context
- Password reset flow triggers a 500 error on login page

## Definition of Done
- [ ] Password reset completes without a 500 error
- [ ] User can log in with the new password
- [ ] Error logs show no 500 responses for reset requests

## Constraints
- Do not change authentication requirements

## Deliverables
- Fix to password reset handler
```

---

## 8) Non-technical request
**User Intent**
"Create a checklist for onboarding new hires."

**Output (CTC)**
```
# Task: Create new-hire onboarding checklist

## Context
- New hires need an onboarding checklist

## Definition of Done
- [ ] Checklist includes at least 8 steps
- [ ] Steps cover first-day, first-week, and first-month tasks
- [ ] Checklist is formatted as bullet points

## Constraints
- Keep items concise

## Deliverables
- Onboarding checklist document
```

---

## 9) Software feature request
**User Intent**
"Allow users to upload profile photos."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) What image formats should be supported?
   - Option A: JPG and PNG
   - Option B: JPG, PNG, and GIF
   - Option C: All common image formats
```

---

## 10) Vague business need
**User Intent**
"Make our onboarding smoother."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which onboarding stage needs improvement first?
   - Option A: Signup flow
   - Option B: First-use tutorial
   - Option C: Email onboarding sequence
```

---

## 11) Bug report
**User Intent**
"Search results are missing items after the latest release."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which search environment is affected?
   - Option A: Production
   - Option B: Staging
   - Option C: Both production and staging
```

---

## 12) Non-technical request
**User Intent**
"Summarize this meeting transcript into bullet points."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Please provide the meeting transcript to summarize.
   - Option A: Paste the transcript here
   - Option B: Upload a file
   - Option C: Provide a link
```

---

## 13) Software feature request
**User Intent**
"Add a filter to the activity log for date ranges."

**Output (CTC)**
```
# Task: Add date range filter to activity log

## Context
- Activity log exists and needs date range filtering

## Definition of Done
- [ ] Activity log has start and end date inputs
- [ ] Results filter correctly by selected date range
- [ ] Date filter can be cleared to show all entries

## Constraints
- Do not change existing log fields

## Deliverables
- Updated activity log filter UI
- Date range filtering logic
```

---

## 14) Vague business need
**User Intent**
"We need to reduce support tickets."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which support ticket category should be addressed first?
   - Option A: Billing issues
   - Option B: Login/access issues
   - Option C: Feature usage questions
```

---

## 15) Bug report
**User Intent**
"Notifications are delayed by hours."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which notification channel is affected?
   - Option A: Email
   - Option B: Push notifications
   - Option C: SMS
```

---

## 16) Non-technical request
**User Intent**
"Draft a one-page policy for remote work."

**Output (CTC)**
```
# Task: Draft remote work policy

## Context
- A one-page remote work policy is needed

## Definition of Done
- [ ] Policy includes eligibility criteria
- [ ] Policy defines communication expectations
- [ ] Policy fits on one page

## Constraints
- Use formal tone

## Deliverables
- Remote work policy document
```

---

## 17) Software feature request
**User Intent**
"Add SSO login with Google."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which user segment should have access to Google SSO?
   - Option A: All users
   - Option B: Enterprise accounts only
   - Option C: Admins only
```

---

## 18) Vague business need
**User Intent**
"We want better dashboards."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) Which dashboard should be prioritized?
   - Option A: Executive overview
   - Option B: Sales performance
   - Option C: Customer success metrics
```

---

## 19) Bug report
**User Intent**
"The export button does nothing on the invoices page."

**Output (CTC)**
```
# Task: Fix invoice export button

## Context
- Export button on invoices page is non-functional

## Definition of Done
- [ ] Clicking export triggers a file download
- [ ] Exported file contains invoice data
- [ ] No errors appear in the console during export

## Constraints
- Do not change invoice data fields

## Deliverables
- Fix for invoice export action
```

---

## 20) Non-technical request
**User Intent**
"Create a weekly schedule for a small team with rotating shifts."

**Output (Clarification Block)**
```
Before proceeding, one clarification is needed:

1) How many team members should be included in the schedule?
   - Option A: 3 members
   - Option B: 5 members
   - Option C: 7 members
```
