# 🏛️ Goings OS: AppSheet Schema Mapping Blueprint

This blueprint defines the precise key-value schema layout for the Cloud Firestore `live_transactions` collection and Option B Local Queue tables to ensure seamless integration with the Private AppSheet mobile interface.

## 1. Firebase Collection: `live_transactions` Schema Layout

Every transaction record written by the Webhook Ingress Gateway contains the following structured fields:

* `client_id` (String): Unique identifier of the contact or client; mapped as the Key Column in AppSheet.
* `transaction_amount` (Number): The total raw dollar value of the incoming stream.
* `owners_draw_allocation_split` (Number): Shareholder distribution portion; calculated automatically and tracked as an owner's draw allocation split exclusively.
* `broker_commission_split` (Number): The broker payout allocation; defaulted to $75.00 for the Norfolk Takeover Cruise or $0.00 for standard accounts.
* `credit_building_verification_status` (String): Indicates verification progress; defaults to `VERIFIED_STRIPE_INGRESS` or `PENDING_GHL_VERIFICATION`.
* `sync_timestamp` (String): ISO 8601 formatted timestamp of cloud execution.
* `allocation_description` (String): Description detailing the allocation splits.
* `source_platform` (String): Ingress origin; either `stripe` or `ghl_ingress`.

### Example JSON Payload Structure

```json
{
  "client_id": "CLI-88902",
  "transaction_amount": 150.00,
  "owners_draw_allocation_split": 75.00,
  "broker_commission_split": 75.00,
  "credit_building_verification_status": "VERIFIED_STRIPE_INGRESS",
  "sync_timestamp": "2026-06-22 04:26:40 UTC",
  "allocation_description": "Norfolk Takeover Cruise: Deposit Draw: Net Draw: $75.00; Broker split: $75.00",
  "source_platform": "stripe"
}
```

---

## 2. AppSheet Columns Configuration Guide

Configure the following column types inside the AppSheet Editor:

1. **`client_id`**:
   * Type: Text
   * Key: True
   * Label: True
   * Description: Primary identifier of the private entity.

2. **`transaction_amount`**:
   * Type: Price
   * Currency Symbol: $
   * Decimals: 2
   * Description: Raw transaction ingress amount.

3. **`owners_draw_allocation_split`**:
   * Type: Price
   * Currency Symbol: $
   * Decimals: 2
   * Description: Owner's draw allocation split tracking field.

4. **`credit_building_verification_status`**:
   * Type: Enum
   * Values: `PENDING_GHL_VERIFICATION`, `VERIFIED_STRIPE_INGRESS`, `MANUALLY_APPROVED`
   * Description: Visual compliance check flag.
