: -
name: 05_luxury_decor
description: Staging inventory management, commercial decor rentals, fixture leasing, and statutory SCC compliance for Luxury Decor & Rentals LLC.
version: 4.2.0
author: Terrence Goings
publisher: Keep It Goings LLC & Goings OS
cognitive_engine: gemini-3.8-flash
classification: Enterprise Staging & Commercial Rentals Skill
: -

# 🛋️ Luxury Decor: Staging Inventory & Commercial Rental Engine

**Issuing Entity:** Keep It Goings LLC & Goings OS  
**Author & Lead Architect:** Terrence Goings  
**Operating Entity:** Luxury Decor & Rentals LLC (Virginia SCC ID: S1128490, Effective Sept 1, 2026)  
**Document Identifier:** KIG-SKILL-LDR-05  
**Classification:** Enterprise Staging & Equipment Rental Protocol  
**Cognitive Engine:** gemini-3.8-flash  
**Target Path:** `skills/05_luxury_decor/SKILL.md`  

> ### 🔒 COMMERCIAL INVENTORY & STATUTORY NOTICE
> This skill governs commercial furniture rentals, custom event staging design, inventory leasing manifests, and statutory compliance for Luxury Decor & Rentals LLC, officially established under Virginia law effective September 1, 2026.

: -

## 🎯 Section I: Executive Summary & Market Positioning

Luxury Decor & Rentals LLC provides commercial event planners, corporate banquet coordinators, and private clients with luxury furniture, architectural lighting, ceiling drape installations, and premium staging inventory.

### Core Strategic Operations
* **Commercial Inventory Staging:** Curating luxury chiavari chairs, throne seating, velvet lounge banquettes, and custom acrylic podiums.
* **Sub-Rental Logistics:** Partnering with regional hospitality venues to provide turnkey decor packages with insured installation and teardown.
* **Asset Depreciation Tracking:** Maintaining capital asset registers under IRC Section 179 for staging hardware and commercial transport vehicles.
* **Statutory SCC Governance:** Formed effective September 1, 2026; registered for annual renewal on September 30 with $50 statutory state fee.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LUXURY DECOR & RENTALS PILLARS                        │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│     STAGING INVENTORY    │   COMMERCIAL RENTALS     │   STATUTORY COMPLIANCE│
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • Chiavari chairs (Gold) │ • Full ballroom setups   │ • SCC ID: S1128490    │
│ • Custom ceiling draping │ • Venue partner leasing  │ • Cycle: September 30 │
│ • Throne chairs & lounge │ • Transport & teardown   │ • Fee: $50.00 SCC     │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

: -

## 🛠️ Section II: Tool Definitions & MCP Workspace Contracts

### Primary Tool Endpoints
1. `mcpDriveCreateFolder(folderPath: string)`:
   - Target Folder: `Master Architecture/Entities/Luxury Decor & Rentals LLC`
   - Houses formation PDFs, inventory manifests, vendor purchase orders, and rental contracts.
2. `mcpDriveUploadFile(params: DriveUploadParams)`:
   - Indexes Certificate of Organization, Articles of Organization, and EIN Confirmation (CP 575) with SHA-256 verification.
3. `generateLuxuryDecorAnnualRegistrationSchedule()`:
   - Schedules annual Virginia SCC registration renewal for September 30 with automated 60, 30, 15, and 5-day alert intervals.

### Lexis-Secretary Compliance Hooks
* **Filing Schedule Integration:** Enforces hard fee ceiling ($75.00) rejecting any unapproved state assessment fees.
* **Vault Archival Connection:** Stores resulting Google Drive file identifiers in `entity_document_archive`.

: -

## 📋 Section III: Operational Directives & Typography Standards

* **Asset Preservation:** Every rental manifest must include security deposit holds and condition checkouts.
* **Private Accounting:** All rental revenues flow through private merchant gateways into designated LLC operational accounts.
* **Cognitive Engine:** Powered exclusively by `gemini-3.8-flash`.
* **Zero Em-Dashes:** Zero em-dash typographical standard enforced across all rental manifests and client agreements.

: -
*End of Luxury Decor Skill: Goings OS Private Architecture Reference*
