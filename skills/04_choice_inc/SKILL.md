: -
name: 04_choice_inc
description: 501(c)(3) nonprofit governance, FinCEN statutory exemption reporting, grant architecture, and youth mentorship pipelines for Choice Inc.
version: 4.2.0
author: Terrence Goings
publisher: Keep It Goings LLC & Goings OS
cognitive_engine: gemini-3.8-flash
classification: Enterprise Nonprofit Governance Skill
: -

# 🤝 Choice Inc: Community Empowerment & Grant Architecture Engine

**Issuing Entity:** Keep It Goings LLC & Goings OS  
**Author & Lead Architect:** Terrence Goings  
**Nonprofit Entity:** Choice Inc (501(c)(3) Tax-Exempt Humanitarian Organization, choiceincva.org)  
**Document Identifier:** KIG-SKILL-CHOICE-04  
**Classification:** Enterprise Nonprofit Governance & Community Impact Protocol  
**Cognitive Engine:** gemini-3.8-flash  
**Target Path:** `skills/04_choice_inc/SKILL.md`  

> ### 🔒 NONPROFIT INTEGRITY & GRANT STEWARDSHIP NOTICE
> This skill governs public outreach, donor stewardship, youth mentorship storytelling, vocational training initiatives, and philanthropic grant funding for Choice Inc. All operations comply with strict 501(c)(3) public charity standards.

: -

## 🎯 Section I: Executive Summary & Community Mission

Choice Inc (choiceincva.org) is an active 501(c)(3) tax-exempt nonprofit organization dedicated to empowering youth, supporting families, and creating sustainable vocational career pathways across Hampton Roads.

### Core Strategic Pillars
* **Youth Empowerment & Mentorship:** Practical financial literacy academies, introductory coding workshops, and leadership development.
* **Workforce Development & Career Pathways:** Hands-on trade apprenticeships, resume preparation, and young entrepreneur micro-seed funding.
* **FinCEN Corporate Transparency Act (CTA) Exemption:** Certified statutory exemption under 31 U.S.C. 5336(a)(11)(B)(xix) as an active 501(c)(3) tax-exempt public charity.
* **Grant & Philanthropic Stewardship:** Rigorous impact tracking ensuring 88.5%+ direct program allocation and minimal administrative overhead.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CHOICE INC. IMPACT PILLARS                         │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│     YOUTH MENTORSHIP     │  WORKFORCE DEVELOPMENT   │   GRANT STEWARDSHIP   │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • Financial literacy     │ • Vocational job training│ • 501(c)(3) compliance│
│ • Tech & coding camps    │ • Resume & interview prep│ • Foundation grants   │
│ • Leadership academies   │ • Business starter grants│ • FinCEN CTA Exemption│
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

: -

## 🛠️ Section II: Tool Definitions & MCP Workspace Contracts

### Primary Tool Endpoints
1. `mcpDriveCreateFolder(folderPath: string)`:
   - Target Folder: `Master Architecture/Entities/Choice Inc (choiceincva.org)`
   - Houses grant proposals, IRS 501(c)(3) determination letters, and program impact ledgers.
2. `mcpDriveUploadFile(params: DriveUploadParams)`:
   - Indexes audited annual reports and donor acknowledgement letters with SHA-256 verification.
3. `evaluateFinCenExemption(entity: ConglomerateEntity)`:
   - Validates tax-exempt status under CTA Section 5336(a)(11)(B)(xix) to bypass BOIR reporting requirements.

### Lexis-Secretary Compliance Hooks
* **State Corporation Commission Renewal:** Tracks Virginia SCC Annual Registration (`S0954820`) due annually on May 31 ($25 statutory fee).
* **Private Vault Memory:** Telemetry logged to `classroom_student_telemetry` for community education scoring.

: -

## 📋 Section III: Operational Directives & Typography Standards

* **Tax-Exempt Transparency:** All public donor requests must state 501(c)(3) tax-deductible status.
* **Private Entity Autonomy:** Ensure non-profit funds remain strictly insulated from commercial operations.
* **Cognitive Engine:** Powered exclusively by `gemini-3.8-flash`.
* **Zero Em-Dashes:** Strict adherence to zero em-dash typographical guidelines across all grant proposals.

: -
*End of Choice Inc Skill: Goings OS Private Architecture Reference*
