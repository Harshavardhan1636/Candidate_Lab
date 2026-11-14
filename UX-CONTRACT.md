# UX contract

## Product context and authority

PRODUCT.md owns roles, privacy, lifecycle and model boundaries (user blueprint, reviewed 2026-11-01). DESIGN.md owns visual tokens; src/styles.css implements them. English, locale-formatted UTC timestamps, WCAG 2.2 AA target. Local research use only.

## Canonical UI Map

| Capability       | Canonical owner                                | Source of truth | Allowed variants                            | Verification            |
| ---------------- | ---------------------------------------------- | --------------- | ------------------------------------------- | ----------------------- |
| Form             | Field and app validation in src/components.tsx | PRODUCT.md      | create/edit                                 | e2e forms               |
| Select/Listbox   | native select wrapped in Field                 | DESIGN.md       | native popup accepted                       | keyboard e2e            |
| Scrollbar        | src/styles.css global rules                    | DESIGN.md       | forced-colors fallback                      | browser inspection      |
| Toast            | Notice and aria-live region                    | this contract   | success/error                               | e2e                     |
| CRUD             | App route helpers                              | this contract   | create returns to list; inline review stays | e2e                     |
| Dialog           | Dialog primitive                               | this contract   | modal                                       | Escape and focus checks |
| Table navigation | Pager                                          | this contract   | 10 per page                                 | filter/page e2e         |

## State and behavior

Version 0.2: Candidate navigation adds Job opportunities and My applications; recruiter navigation adds Publish jobs, Applications, Compare snapshots and Model evaluation. Auditor model evaluation is read-only and aggregate-only. Opportunity lists and application history are paginated; snapshot tables use ten rows per page. Skills reports name the profile version and state evidence limitations. Evaluation drafts use the existing unsaved-change guard. Job rubrics use version-checked edits; submitted profile versions stay fixed, and withdrawal/resubmission is retired (the old endpoint returns 410). No application action dispatches external messages.
Recruiter overview totals are database-backed and role-restricted. Each summary card navigates to its owning list; review records opens matching evidence where review actions live. Counts include sample profiles explicitly. This presentation update removes academic branding without changing account permissions, underlying records or score interpretation.
Query-string routes select jobs, candidates, matches or audit. Page/query state lives in URL parameters except sensitive resume drafts. Server filters are immediate; superseded requests are aborted. Lists are bounded and paginated; filters reset the page. Search has an explicit clear button. Every page has busy, empty, no-results and error/retry states. Buttons are native, named, keyboard focusable, disabled during requests. No native alert/confirm/prompt. Forms use noValidate and keep entered values after server errors. Textareas do not resize manually. Secrets remain masked except an explicit Show/Hide button. Session cookie is HttpOnly; no browser storage of passwords/tokens.

## Flow ledger

Registration uses the existing login layout and shared Field/Button/Notice controls. Candidate registration is direct; recruiter/auditor selection reveals a masked invitation field. Password confirmation and inline errors retain input on failure. Successful creation returns to login with email filled and passwords cleared. Existing accounts and invitation errors have explicit recovery text; the app does not imply email delivery or ownership verification.
Create job / Edit job / Add profile -> busy Save button -> confirmed server result -> return to owning list -> shared success notice. Edit profile -> version-checked save -> owning list. Matching -> confirmed snapshot run -> results. Review -> append reason -> stay on selected match. Login -> role-specific landing page. Logout -> clear session and return login. Unsaved form navigation uses a shared leave-draft dialog. Upload enforces file type/size, displays extraction warnings and permits correction before saving.

## Scope limits

No bulk actions, billing, automatic hiring, hard-delete or externally dispatched notifications. No hidden group-level thresholds. Audit threshold is a common research cutoff, not a policy recommendation. Candidate correction is scoped by backend ownership. A 403 shows access denied rather than presenting restricted data. Empty extraction never creates a zero-skill candidate silently.
