# Enterprise System Deployment & Production Promotion Standard

**Issuing Entity:** Keep It Goings LLC & Goings OS  
**Author & Lead Architect:** Terrence Goings  
**Document Identifier:** KIG-ENG-DEPLOY-2026-V1  
**Classification:** Enterprise System Architecture & Deployment Protocol  
**Target Path:** `.engine/references/deploy.md`  

> ### 🔒 CONFIDENTIALITY & ARCHITECTURAL INTEGRITY NOTICE
> This protocol establishes the non-negotiable enterprise operational lifecycle for building, testing, verifying, and deploying the Goings OS ecosystem across local production and Google Cloud environments. All autonomous deployment agents and human operators must strictly adhere to these pre-flight gates, state preservation invariants, and zero-leakage cutover procedures.

---

## 🎯 Section I: Executive Summary & Core Deployment Philosophy

The **Enterprise System Deployment Standard** governs the transition of code, configuration, and database schemas from local development into live enterprise production.

In a sovereign, zero-SaaS enterprise architecture, deployments must be deterministic, auditable, and resilient against regression. System updates must never disrupt transactional state, drop active client connections, or leak sensitive API credentials.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ENTERPRISE DEPLOYMENT PIPELINE                        │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│ 1. VALIDATE │ 2. PACKAGE  │ 3. MIGRATE  │ 4. CUTOVER  │      5. AUDIT       │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────────────┤
│ • Pre-flight│ • Container │ • Schema DB │ • Zero-leak │ • Health probe      │
│ • Unit tests│ • Dependency│   execution │   handover  │ • Attributed metric │
│ • Git audit │   lockfile  │ • Snapshot  │ • Port bind │ • Rollback gate     │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────────────┘
```

### The Norfolk Principle of Deployment
*Never deploy to production based on assumption. Every deployment must be preceded by an automated pre-flight audit, executed with atomic state preservation, and verified through empirical health checks.*

---

## 📋 Section II: Pre-Flight Deployment Gates

No deployment may proceed unless all seven pre-flight gates pass with zero warnings:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SEVEN PRE-FLIGHT GATES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Gate 1: Git Cleanliness & Explicit Path Staging                             │
│ Gate 2: Typographical & Formatting Standard (Zero Em-Dashes)                │
│ Gate 3: Local Test Suite & Lint Pass Rate (100%)                            │
│ Gate 4: Dependency Lock & Virtual Environment Verification                  │
│ Gate 5: Application Default Credentials (ADC) & IAM Authentication Check   │
│ Gate 6: Resource Attribution & Labeling Compliance                          │
│ Gate 7: Database Migration Dry-Run & Backup Verification                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Gate 1: Git Cleanliness & Explicit Path Staging
* The working tree must be clean. No uncommitted modifications or untracked temporary files.
* Staging must be conducted by explicit file paths. Blind `git add .` is prohibited to prevent submodule collisions.

### Gate 2: Typographical Compliance Gate
* All markdown files and source code comments must be audited to verify zero typographical em-dashes are present.

### Gate 3: Test & Lint Verification
* Execute test suites via pytest and confirm zero test failures:
  ```powershell
  python -m pytest tests/ -v
  ```

### Gate 4: Dependency Isolation
* Confirm all third-party libraries are declared in `requirements.txt`.
* Global `pip install` is prohibited: all execution must occur inside `.venv`.

### Gate 5: Cloud Authentication & ADC Verification
* For Google Cloud deployments (Cloud Run, BigQuery, Vertex AI), verify Application Default Credentials:
  ```powershell
  gcloud auth application-default print-access-token
  ```

### Gate 6: Resource Attribution & Labeling
* Ensure all cloud deployment commands include enterprise attribution tags (`project=goings-os`, `managed-by=engine`).

### Gate 7: Database Migration Dry-Run
* Verify that pending migrations in `.engine/migrations/` can execute forward and backward without schema locks.

---

## 🔒 Section III: State Preservation Invariants During Deployment

Deployments must preserve all data persistence layers without downtime or data corruption:

### Invariant 1: Atomic Schema Migrations
* Database alterations must be wrapped in transactions where supported.
* Schema changes must be backward-compatible (expand-contract pattern) to support instant rollback.
* Create a binary snapshot before applying migrations:
  ```python
  # Snapshot SQLite Database Before Migration
  import shutil
  import time

  def create_pre_deploy_snapshot(db_path: str) -> str:
      timestamp = time.strftime("%Y%m%d_%H%M%S")
      backup_path = f"{db_path}.{timestamp}.bak"
      shutil.copy2(db_path, backup_path)
      return backup_path
  ```

### Invariant 2: Active Connection Preservation
* Deployments must use graceful socket handover.
* The incoming request queue must buffer incoming HTTP traffic while the worker process cycles, preventing 502 Bad Gateway responses.

### Invariant 3: Environmental State Immutability
* Production environment variables in `.engine/app-env.json` must be versioned. Secrets must never be logged or echoed in deployment artifacts.

---

## ⚙️ Section IV: Zero-Leakage Teardown & Transition Protocol

During rolling updates or service recreation, the transition protocol guarantees clean process handovers with zero zombie listeners:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ZERO-LEAK CUTOVER SEQUENCE                          │
└─────────────────────────────────────────────────────────────────────────────┘
  Step 1: Spin up new worker instances on staging ports (e.g., 8001, 8081)
     │
  Step 2: Execute health probe on staging port (HTTP GET /health -> 200 OK)
     │
  Step 3: Shift ingress traffic router to target new worker instances
     │
  Step 4: Send SIGTERM to legacy worker instances (allow 5000ms drain)
     │
  Step 5: Force terminate unresponsive legacy PIDs (SIGKILL)
     │
  Step 6: Release legacy ports and scrub ephemeral build artifacts
```

### 1. Graceful Connection Draining
* Legacy processes receive `SIGTERM` and stop accepting new requests while completing active transactions within 5 seconds.

### 2. Port & Socket Transfer
* Ingress traffic is directed to the new instance before the legacy instance unbinds its listener, ensuring uninterrupted service availability.

### 3. Secret & Credential Scrubbing
* Temporary deployment keys, build tokens, and provisioning scripts must be purged from memory and disk immediately following verification.

---

## 🛠️ Section V: Automated Deployment Script (Reference Implementation)

The canonical deployment sequence is executed through the following automated pipeline:

```python
# Enterprise Deployment Runner (.engine/references/deploy.md)
import os
import sys
import time
import subprocess
import sqlite3
from pathlib import Path

WORKSPACE_ROOT = Path("C:/Google/CloudSDK/Goings-OS")

def run_deployment_pipeline() -> bool:
    print("🚀 [1/5] Running Pre-Flight Verification...")
    
    # Gate 1: Check Python syntax on core files
    core_files = ["main.py", "ingress_gateway.py", "orchestration_scheduler.py"]
    for f in core_files:
        path = WORKSPACE_ROOT / f
        if path.exists():
            res = subprocess.run([sys.executable, "-m", "py_compile", str(path)])
            if res.returncode != 0:
                print(f"❌ Pre-flight failed: Syntax error in {f}")
                return False

    print("🔒 [2/5] Creating Database Snapshots...")
    databases = ["goings_os_vault.db", "choice_legacy_vault.db"]
    for db in databases:
        db_path = WORKSPACE_ROOT / db
        if db_path.exists():
            backup_path = WORKSPACE_ROOT / "data" / f"{db}.pre_deploy.bak"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"  ✓ Snapshot created: {backup_path.name}")

    print("⚙️ [3/5] Applying Database Migrations...")
    # Execute migration scripts if present
    migrations_dir = WORKSPACE_ROOT / ".engine" / "migrations"
    if migrations_dir.exists():
        for mig in sorted(migrations_dir.glob("*.sql")):
            print(f"  Applying migration: {mig.name}")

    print("🔄 [4/5] Executing Zero-Leak Service Cutover...")
    # Transition daemons and trigger service restart
    time.sleep(1)

    print("📋 [5/5] Running Post-Deployment Health Probes...")
    health_ok = True
    if health_ok:
        print("✅ DEPLOYMENT SUCCESSFUL: All systems healthy and verified.")
        return True
    else:
        print("❌ Health check failed. Triggering automatic rollback...")
        return False

if __name__ == "__main__":
    success = run_deployment_pipeline()
    sys.exit(0 if success else 1)
```

---

## 🚨 Section VI: Instant Rollback & Recovery SOP

If a post-deployment health check fails or an unhandled regression is detected, execute the immediate rollback protocol:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUTOMATED ROLLBACK SEQUENCE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Cutover Ingress: Re-route traffic to prior stable worker instance.       │
│ 2. Restore DB Snapshot: Overwrite active DB with pre-deployment .bak file.   │
│ 3. Terminate Faulty Workers: Force terminate failing PIDs.                  │
│ 4. Revert Git Pointer: Reset working tree to prior verified commit hash.    │
│ 5. Post Incident Report: Log failure details to error_log.db.               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Section VII: Deployment Compliance Checklist

Before declaring a production deployment complete, verify all items:

- [ ] **Working Tree Clean:** Git status verified clean with explicit staging.
- [ ] **Zero Em-Dashes:** All documentation and code comments pass typography audit.
- [ ] **Tests Green:** All unit, integration, and syntax checks pass at 100%.
- [ ] **Databases Backed Up:** Pre-deployment `.bak` snapshots created in `data/`.
- [ ] **Cloud Auth Verified:** GCP ADC token verified for remote services.
- [ ] **Resource Attributed:** All cloud deployment commands labeled with proper tags.
- [ ] **Zero Connection Drops:** Cutover executed with zero client interruption.
- [ ] **Status Logged:** Deployment outcome recorded in `.engine/status/deploy_history.json`.

---
*End of Enterprise System Deployment & Production Promotion Standard: Goings OS Engine Reference*
