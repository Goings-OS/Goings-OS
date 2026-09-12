# Enterprise System Scaffolding & Directory Integrity Standard

**Issuing Entity:** Keep It Goings LLC & Goings OS  
**Author & Lead Architect:** Terrence Goings  
**Document Identifier:** KIG-ENG-SCAFFOLD-2026-V1  
**Classification:** Enterprise System Architecture & Scaffolding Protocol  
**Target Path:** `.engine/references/scaffold.md`  

> ### 🔒 CONFIDENTIALITY & ARCHITECTURAL INTEGRITY NOTICE
> This protocol establishes the non-negotiable enterprise directory scaffolding, file lifecycle governance, and directory integrity verification standards for Goings OS. All autonomous companions, human engineers, and runtime engine agents must strictly comply with this framework.

---

## 🎯 Section I: Executive Summary & Core Engineering Philosophy

The **Enterprise System Scaffolding & Directory Integrity Standard** guarantees structural consistency, zero-drift execution, and clean separation of concerns across the entire Goings OS ecosystem.

In autonomous, multi-agent, and zero-SaaS enterprise environments, system entropy is the primary point of failure. Unstructured file creation, orphaned runtime scripts, nested repository conflicts, and ambiguous configuration paths degrade agent performance and corrupt state persistence.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GOINGS OS DIRECTORY INTEGRITY PILLARS                    │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│    DETERMINISTIC ROOT    │    ISOLATED RUNTIMES     │    STATE PERSISTENCE  │
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • Canonical taxonomy     │ • Sandboxed dependencies │ • Segregated vaults   │
│ • Zero-orphan policy     │ • Immutable core nodes   │ • Ephemeral / DB split│
│ • Explicit git staging   │ • Uniform service ports  │ • Continuous audit    │
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

### The Norfolk Principle of Directory Scaffolding
*A system that does not strictly enforce its own physical and logical boundaries will inevitably collapse under operational complexity. Every directory must have a single clear owner, every file must fulfill a documented contract, and all state transitions must be verifiable.*

---

## 📁 Section II: Canonical Enterprise Directory Taxonomy

The repository root `C:\Google\CloudSDK\Goings-OS` is structured into isolated, deterministic operational tiers:

```
Goings-OS/
├── .engine/                     # Engine-level execution metadata, protocols, references
│   ├── auth/                    # Local authentication tokens and credential references
│   ├── migrations/              # Database schema migrations and version manifests
│   ├── references/              # Standard protocols (scaffold, deploy, hibernate, browser)
│   ├── skills/                  # Engine runtime tool definitions and execution skills
│   └── status/                  # Node status dumps and operational heartbeats
├── brain/                       # Private second-brain knowledge vaults & agent logs
├── core_nodes/                  # Autonomous industrial node packages and services
├── data/                        # Local SQLite databases, ledger stores, and data caches
├── frontend/                    # Web client apps, portals, and visual command centers
├── goings-os-academy/           # Curriculum decks, student handouts, and enterprise playbooks
├── infra_tools/                 # Deployment scripts, daemons, and cloud infrastructure logic
├── middleware/                  # Ingress gateways, CRM brokers, and webhook routers
├── scripts/                     # Operational automation scripts and batch processors
└── workspace_bridges/           # Inter-node bridges and MCP integration valves
```

### Tier Definitions & Boundary Responsibilities

| Directory Path | Access Level | Primary Function | State Type |
| :--- | :--- | :--- | :--- |
| `.engine/` | Private System | Engine configuration, protocols, skills, and migration records | Semi-Static |
| `brain/` | Private System | Second brain memory, transcripts, and founder strategy vaults | Append-Only |
| `core_nodes/` | Enterprise Core | Domain services (KIG, TBE Shield, Luxury Affairs, Choice) | Immutable / Versioned |
| `data/` | Data Tier | Local SQLite databases, transactional ledgers, catalog stores | Dynamic State |
| `frontend/` | Client Tier | Next.js, Vite, and HTML5 Command Center interfaces | Ephemeral Build |
| `goings-os-academy/` | Academy Tier | Educational handouts, slide master decks, and playbooks | Documented Knowledge |
| `middleware/` | Gateway Tier | GoHighLevel broker, Stripe webhooks, and ingress daemons | Stateless Routing |
| `scripts/` | Tooling Tier | Maintenance, QR generation, notebook generation, and sync | Executable Tooling |
| `workspace_bridges/`| Bridge Tier | MCP valves, Looker bridges, and multi-tenant adapters | Protocol Adapters |

---

## 🔒 Section III: Directory Integrity & Governance Rules

All autonomous companions and engineers must execute under the following five mandatory rules:

### Rule 1: Zero-Orphan File Policy
* Every newly created file must reside in an established domain directory (`.engine/`, `core_nodes/`, `scripts/`, `middleware/`, etc.).
* No temporary `.txt`, `.tmp`, or unformatted scratch files may be dropped directly into the root workspace folder.
* Temporary artifacts must be routed to `.engine/artifacts/` or `brain/<session-id>/scratch/`.

### Rule 2: Strict Database & State Segregation
* Database binaries (`.db`, `.sqlite`, `.sqlite3`) must be stored in `data/` or designated persistence vaults.
* Application code must reference database paths dynamically using environment variables or configuration constants, never hard-coded relative leaps.

### Rule 3: Git Boundary & Submodule Conflict Prevention
* Never execute an un-insulated `git add .` if a sub-folder contains its own `.git` directory.
* Always explicitly stage modified files by exact path.
* Ensure all submodules are declared in `.gitmodules` with valid tracking URLs.

### Rule 4: Typographical & Formatting Compliance
* Em-dashes are strictly prohibited across all documentation, markdown files, and source comments. Use colons, commas, periods, or parentheses for clause separation.
* All major section headers must feature clean emoji visual anchors.
* Code blocks must be reserved strictly for executable code or configuration syntax.

### Rule 5: Accidental Data Loss Prevention
* Destructive directory operations (`rmdir /s`, `rm -rf`, `DROP TABLE`, `TRUNCATE`) require explicit user verification.
* Automated file refactoring must create a localized backup or git revision point prior to execution.

---

## ⚙️ Section IV: Standard Node Scaffolding Protocol

When provisioning a new service, microservice, or enterprise node inside `core_nodes/` or `middleware/`, execute the standard 4-phase scaffolding sequence:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. STRUCTURE   │ ──> │   2. CONTRACT   │ ──> │   3. REGISTRY   │ ──> │   4. AUDIT      │
│ Create folder   │     │ Add README.md,  │     │ Register in     │     │ Execute lint &  │
│ hierarchy       │     │ __init__.py,    │     │ orchestrator &  │     │ integrity check │
│                 │     │ config schema   │     │ MCP valves      │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Phase 1: Directory Structure Blueprint
A standardized node directory must contain:
```
core_nodes/<node_name>/
├── __init__.py                  # Python package initializer
├── README.md                    # Node purpose, API contracts, and usage guide
├── config.py                    # Environment settings and fallback parameters
├── service.py                   # Core business logic execution engine
├── models.py                    # Data schemas (Pydantic / Dataclasses)
└── tests/                       # Unit and integration test suites
    └── test_<node_name>.py
```

### Phase 2: Mandatory Node Metadata Schema (`README.md`)
Every node must contain a standardized `README.md` containing:
1. **Node Purpose:** Plain English summary of business functionality.
2. **Dependencies:** Required Python libraries or external endpoints.
3. **API Contract:** Input parameters, output payloads, error response format.
4. **Definition of Done:** Verification test command.

### Phase 3: Orchestrator Registration
Every active node must be registered with the master scheduler (`orchestration_scheduler.py`) or MCP valve system (`partner_mcp_valve.py`) with health check endpoints exposed.

### Phase 4: Quality Gate & Integrity Validation
Run syntax validation and compilation checks on all newly scaffolded files before committing to version control.

---

## 📋 Section V: Automated Directory Integrity Verification Standard

To verify workspace integrity programmatically, execute the standard directory audit checklist:

```python
# Directory Integrity Audit Spec (Python Reference)
import os
from pathlib import Path

REQUIRED_DIRECTORIES = [
    ".engine/references",
    ".engine/migrations",
    ".engine/auth",
    "brain",
    "core_nodes",
    "data",
    "frontend",
    "goings-os-academy",
    "infra_tools",
    "middleware",
    "scripts",
    "workspace_bridges"
]

def audit_directory_integrity(root_path: str) -> dict:
    root = Path(root_path)
    results = {"missing_dirs": [], "root_orphans": [], "status": "HEALTHY"}
    
    # 1. Verify required directory tree
    for req_dir in REQUIRED_DIRECTORIES:
        target = root / req_dir
        if not target.exists():
            results["missing_dirs"].append(req_dir)
            
    # 2. Check for unauthorized root-level temporary files
    for item in root.iterdir():
        if item.is_file() and item.suffix in [".tmp", ".bak", ".orig"]:
            results["root_orphans"].append(item.name)
            
    if results["missing_dirs"] or results["root_orphans"]:
        results["status"] = "ACTION_REQUIRED"
        
    return results
```

---

## 🛠️ Section VI: Recovery & Self-Healing SOP

When a directory violation, orphaned file flood, or structure collision is detected, execute the following remediation steps:

### Scenario A: Orphaned Files in Root
1. Inspect file creation metadata and content to determine domain ownership.
2. Relocate utility scripts to `scripts/`, database files to `data/`, and documentation to `.engine/references/` or `brain/`.
3. Clean empty temporary files.

### Scenario B: Nested Git Repository Collision
1. Identify offending nested `.git` folders with `Get-ChildItem -Path . -Recurse -Force -Filter ".git"`.
2. If the directory is a designated submodule, verify entry in `.gitmodules`.
3. If it is an accidental nested clone, safely remove the internal `.git` handle after securing uncommitted source files.

### Scenario C: Corrupted Protocol or Configuration File
1. Re-initialize the standard scaffolding template from `.engine/references/scaffold.md`.
2. Cross-verify environment variables in `.engine/app-env.json`.
3. Perform a dry-run test through `python initialize_nodes.py`.

---

## ✅ Section VII: Scaffolding Compliance Checklist

Before closing any development, migration, or deployment session, confirm the following gates:

- [ ] **Directory Conformance:** All new files reside in their designated directory tier.
- [ ] **No Root Clutter:** Root workspace contains only sanctioned entry points and configuration files.
- [ ] **Zero Em-Dashes:** Source text and markdown documentation are free of em-dash characters.
- [ ] **State Isolation:** Persistent databases and logs are isolated from ephemeral frontend builds.
- [ ] **Explicit Git Staging:** Staging was performed by specific file path, preventing accidental submodule collisions.
- [ ] **Protocol Linkage:** Node documentation is indexed and cross-referenced in `.engine/references/`.

---
*End of Enterprise System Scaffolding & Directory Integrity Standard: Goings OS Engine Reference*
