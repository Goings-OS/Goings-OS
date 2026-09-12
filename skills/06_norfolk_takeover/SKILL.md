: -
name: 06_norfolk_takeover
description: Maritime group cruise ticketing, stateroom cabin inventory, guest reservation manifests, and annual April SCC compliance for Norfolk Takeover Cruise LLC.
version: 4.2.0
author: Terrence Goings
publisher: Keep It Goings LLC & Goings OS
cognitive_engine: gemini-3.8-flash
classification: Enterprise Maritime Travel & Event Logistics Skill
: -

# 🚢 Norfolk Takeover: Maritime Ticketing & Stateroom Sales Engine

**Issuing Entity:** Keep It Goings LLC & Goings OS  
**Author & Lead Architect:** Terrence Goings  
**Operating Entity:** Norfolk Takeover Cruise LLC (Virginia SCC ID: S1115892)  
**Document Identifier:** KIG-SKILL-NTC-06  
**Classification:** Enterprise Maritime Travel & Group Event Protocol  
**Cognitive Engine:** gemini-3.8-flash  
**Target Path:** `skills/06_norfolk_takeover/SKILL.md`  

> ### 🔒 MARITIME CRUISE & STATUTORY NOTICE
> This skill governs stateroom cabin sales pipelines, passenger manifest compliance, installment payment reminders, VIP deck excursion ticketing, and corporate compliance for Norfolk Takeover Cruise LLC.

: -

## 🎯 Section I: Executive Summary & Event Positioning

Norfolk Takeover Cruise LLC is the premier maritime group travel organization operating annual charted voyages out of Norfolk and East Coast seaports. The company coordinates comprehensive group travel, curated onboard galas, private deck entertainment, and island excursions.

### Core Strategic Operations
* **Stateroom Cabin Inventory Management:** Real-time allocations across Balcony Suites, Oceanview Cabins, and Interior Staterooms.
* **Automated Installment Schedules:** Flexible payment plans with scheduled deposit milestones and automated reminders.
* **The Nightlife at Sea:** Curated all-white deck galas, VIP champagne receptions, private DJ sound stages, and island excursions.
* **Statutory SCC Governance:** Virginia SCC entity `S1115892` with statutory renewal window anchored annually to April 30.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NORFOLK TAKEOVER CRUISE PILLARS                          │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│   STATEROOM CABIN TIERS  │  THE NIGHTLIFE AT SEA    │   STATUTORY COMPLIANCE│
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • Balcony Suites         │ • Private DJ deck galas  │ • SCC ID: S1115892    │
│ • Oceanview Cabins       │ • All-white dining night │ • Cycle: April 30     │
│ • Interior Cabins        │ • Catamaran excursions  │ • Fee: $50.00 SCC     │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

: -

## 🛠️ Section II: Tool Definitions & MCP Workspace Contracts

### Primary Tool Endpoints
1. `mcpDriveCreateFolder(folderPath: string)`:
   - Target Folder: `Master Architecture/Entities/Norfolk Takeover Cruise LLC`
   - Houses cruise charter contracts, passenger manifests, vendor agreements, and port permits.
2. `mcpDriveUploadFile(params: DriveUploadParams)`:
   - Indexes cruise booking agreements, port insurance binders, and passenger receipts with SHA-256 validation.

### Lexis-Secretary Compliance Hooks
* **State Corporation Commission Renewal:** Tracks Virginia SCC Annual Registration (`S1115892`) due annually on April 30 ($50 statutory fee).
* **Portsmouth & Norfolk Telemetry:** Reconciles ticketing revenues with local municipal BPOL reporting.

: -

## 📋 Section III: Operational Directives & Typography Standards

* **Booking Deadlines:** All ticketing materials must emphasize strict cabin hold cut-offs and payment schedules.
* **The Nightlife Nomenclature:** Refer to all evening cruise entertainment exclusively as "the nightlife".
* **Cognitive Engine:** Powered exclusively by `gemini-3.8-flash`.
* **Zero Em-Dashes:** Zero em-dash typographical standard strictly enforced across all contracts and itineraries.

: -
*End of Norfolk Takeover Skill: Goings OS Private Architecture Reference*
