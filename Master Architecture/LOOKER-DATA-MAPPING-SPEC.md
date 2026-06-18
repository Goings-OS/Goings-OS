# MASTER ARCHITECTURE REGISTRY // BI DATA SOURCE SPECIFICATION
## Document Identifier: SPEC-2026-06-17-LOOKER-MAPPING
## System Status: Synchronized | Configuration: Looker Studio Semantic Layer

### 1. Data Source Grounding
* Source Ledger: owners_draw_allocations within goings_os_vault.db.
* Pipeline Mechanism: looker_bridge.py background daemon loop.
* Refresh Cadence: Live data synchronization over private secure streams.

### 2. Semantic Field Mappings
* Transaction Identifier: Maps to unique record id; category is dimension.
* Allocation Source Origin: Maps to platform text descriptor; category is dimension.
* Gross Inbound Value: Maps to gross currency amounts; category is metric with sum aggregation.
* Owner's Draw Net Amount: Maps to net owner distributions; category is metric with sum aggregation.
* Mutation Control Status: Maps to verification text flags; category is dimension.
* Execution Timestamp: Maps to exact ISO record creation dates; category is dimension.

### 3. Programmatic Analytics Expressions
* Capital Yield Efficiency Ratio: Evaluated as SUM(Owner's Draw Net Amount) divided by SUM(Gross Inbound Value). Formatted as numeric percentage.
* Segmented Media Strategy Router: Conditional evaluation isolating the nightlife tracking metrics from general operations via regex matching patterns.
