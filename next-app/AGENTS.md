# Goings OS: Next-App Agent Architecture & Operational Codex

## 1. Conglomerate Scope & Operational Pillars
* **Entity HQ:** Goings OS Master Command & Control Architecture.
* **Pillar III (Luxury Decor and Rentals - LDR):** Primary event logistics, staging inventory, pipe-and-drape hardware, luxury throne seating, and Warwick warehouse asset allocation.
* **Pillar VII (One Stop on Boulevard):** Retail, bridal, and commercial event space acquisition. 
* **Financial Ledger Policy:**
  * Loan and security deposit repayments to previous ownership deferred to January 1, 2027.
  * September and October 35% advance booking deposits remain credited to One Stop on Boulevard to cover fixed overhead.
  * Final event balances settled 14 days prior to event dates are credited directly to LDR operating capital.

---

## 2. Engineering Doctrine & Linter Enforcement (Gem 16)
* **Zero-Polling Standard:** Never implement interval polling loops (`setInterval`, recursive timeouts, or perpetual GET loops) on client or telemetry endpoints. All dynamic updates must use event-driven subscriptions, WebSockets, or Server-Sent Events to preserve client battery and rendering performance.
* **Strict In-Place Refactoring:** Do not generate defensive duplicate files (`_v2`, `_backup`, `_new`). Deprecated logic must be replaced directly in place, verified against upstream interfaces, and purged of dead code paths.
* **Typography & Encoding Hygiene:** Zero tolerance for em-dashes (`\u2014`) or non-breaking spaces (`\u00A0`) within code, schemas, or automation scripts. Enforce standard ASCII hyphens (`-`) exclusively.

---

## 3. Multimodal Optical Inventory Ingress
* **Ingress Component:** `next-app/components/VideoInventoryScanner.tsx`
* **Telemetry Path:** Raw video captures (`.webm`) stream directly to Vertex AI multimodal ingress endpoints.
* **Model Pipeline:** Gemini multimodal vision models parse footage frame-by-frame to extract item taxonomy, color classification (drapes, linens, floral structures), condition scoring, and cubic volume estimation.
* **Target Persistence:** Extracted catalog rows commit directly to `/home/jupyter/Goings-OS/financial_vault.duckdb` under the `physical_asset_catalog` relation.

---

## 4. Node Bus & Telemetry Registry
* `node_08_vault`: DuckDB ledger, cash flow tables, and asset tracking.
* `node_15_elevenlabs`: Synthetic audio dispatch and voice notifications.
* `node_20_agent_bus`: Event bus routing telemetry between Next.js UI, Python workers, and external webhooks.
* `node_21_governance_kms`: Key management, policy compliance, and audit trails.