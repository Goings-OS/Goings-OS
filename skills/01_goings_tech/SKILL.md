: -
name: 01_goings_tech
description: Private technical architecture, Vertex AI cognitive pipelines, Apps Script bridges, and Cloud Run MCP tool infrastructure for Keep It Goings LLC.
version: 4.2.0
author: Terrence Goings
publisher: Keep It Goings LLC & Goings OS
cognitive_engine: gemini-3.8-flash
classification: Enterprise Technical Architecture Skill
: -

# 🤖 Goings Tech: Private AI Engine & MCP Workspace Architecture

**Issuing Entity:** Keep It Goings LLC & Goings OS  
**Author & Lead Architect:** Terrence Goings  
**Document Identifier:** KIG-SKILL-TECH-01  
**Classification:** Enterprise Private AI & MCP Architecture Protocol  
**Cognitive Engine:** gemini-3.8-flash  
**Target Path:** `skills/01_goings_tech/SKILL.md`  

> ### 🔒 ARCHITECTURAL & SYSTEM INTEGRITY NOTICE
> This skill defines the core engineering, Vertex AI integration, Google Workspace Apps Script bridges, and Cloud Run Model Context Protocol (MCP) server endpoints for Keep It Goings LLC. It enforces zero-SaaS subscription overhead through self-hosted microservices and resilient SQLite vaults.

: -

## 🎯 Section I: Executive Positioning & Core Capabilities

Keep It Goings LLC establishes enterprise technical authority across Hampton Roads and beyond by deploying automated AI systems, private microservices, and stateless MCP workflows.

### Core Strategic Capabilities
* **Cognitive Engine Alignment:** Powered natively by `gemini-3.8-flash` for high-throughput reasoning, structured schema validation, and low-latency payload evaluation.
* **Stateless Model Context Protocol (MCP):** Cloud Run compatible MCP servers exposing Application Default Credentials (ADC) and Google Workspace automation tools.
* **Zero-SaaS Architecture:** Self-hosted Python backends, FastAPI gateways, and WAL-enabled SQLite databases replacing fragile monthly SaaS subscriptions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       GOINGS TECH ENGINE ARCHITECTURE                       │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│    COGNITIVE RUNTIME     │    STATELESS MCP TOOLS   │   STORAGE INTEGRITY   │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • gemini-3.8-flash core  │ • mcpDriveCreateFolder   │ • data/goings_os_vault│
│ • Vertex AI pipelines    │ • mcpDriveUploadFile     │ • WAL concurrency     │
│ • Model Armor inspection │ • workspace_submit_lead  │ • Lexis compliance    │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

: -

## 🛠️ Section II: Tool Definitions & MCP Workspace Contracts

### Primary Tool Endpoints
1. `mcpDriveCreateFolder(folderPath: string)`:
   - Target Folder: `Master Architecture/Entities/Keep It Goings LLC`
   - Creates or resolves hierarchical Google Drive directory paths with deterministic ID resolution.
2. `mcpDriveUploadFile(params: DriveUploadParams)`:
   - Uploads, indexes, and SHA-256 verifies statutory artifacts, architecture blueprints, and code releases.
3. `workspace_submit_lead(rawPayload: LeadPayload)`:
   - Validates incoming CRM payloads against pre-execution schemas and dispatches to Google Workspace Apps Script.
4. `workspace_validate_schema(payload: unknown)`:
   - Pre-flight in-memory validation of required fields (`name`, `email`, `intent`).

### Lexis-Secretary Compliance Hooks
* **Corporate Secretary Intercept:** All entity actions trigger `archiveEntityFilingMcp` to index executive resolutions into the private vault.
* **Aegis-Risk HitL Gatekeeper:** Mandatory cryptographic sign-off by Terrence Goings before dispatching external financial transactions.

: -

## 📋 Section III: Operational Guidelines & Quality Invariants

* **Private-First Imperative:** Maintain private local data ownership and eliminate vendor lock-in.
* **Typographical Compliance:** Zero em-dashes and zero double-hyphens permitted across all templates and codebases.
* **Cognitive Engine Enactment:** All LLM prompts must strictly designate `gemini-3.8-flash`.

: -
*End of Goings Tech Skill: Goings OS Private Architecture Reference*
