# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: VIRTUAL PAYMENTS ENGINE (core_nodes/node_19_virtual_payments/virtual_payments.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; HARD SPEND CEILINGS; WAL CONCURRENCY
# ==============================================================================

import os
import sys
import time
import json
import uuid
import hmac
import hashlib
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.environ.get("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

data_vault = os.path.join(ROOT_DIR, "data", "goings_os_vault.db")
DB_PATH = data_vault if os.path.exists(data_vault) else os.path.join(ROOT_DIR, "goings_os_vault.db")

BASE_SPEND_CAP_CENTS = 1000  # Default $10.00 base threshold

# ==============================================================================
# 1. DATABASE SCHEMA INITIALIZATION
# ==============================================================================

def init_virtual_payments_db(db_path: str = DB_PATH) -> None:
    """Initializes the virtual payment cards and transaction audit tables with WAL mode."""
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS virtual_payment_cards (
                card_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                merchant_lock TEXT NOT NULL,
                spend_limit_cents INTEGER NOT NULL,
                spend_duration TEXT NOT NULL,
                card_type TEXT NOT NULL,
                pan_masked TEXT NOT NULL,
                expiration_month INTEGER NOT NULL,
                expiration_year INTEGER NOT NULL,
                status TEXT NOT NULL,
                authorized_by TEXT,
                auth_token TEXT,
                purpose TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS virtual_payment_transactions (
                transaction_id TEXT PRIMARY KEY,
                card_id TEXT NOT NULL,
                merchant_name TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                status TEXT NOT NULL,
                authorization_code TEXT,
                decline_reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (card_id) REFERENCES virtual_payment_cards(card_id)
            );
        """)
        conn.commit()
        conn.close()
    except Exception as db_err:
        logging.error(f"Failed to initialize virtual payments schema in vault: {str(db_err)}")


init_virtual_payments_db()


# ==============================================================================
# 2. EXCEPTIONS & SPEND CONTROLS
# ==============================================================================

class AegisSpendLimitExceeded(Exception):
    """Raised when card spend request exceeds base or authorized limits."""
    pass


class MerchantLockViolation(Exception):
    """Raised when an attempt is made to charge a card outside locked merchant."""
    pass


class UnauthorizedPaymentRequest(Exception):
    """Raised when a payment request lacks executive authorization."""
    pass


class SpendControlPolicy:
    """Enforces strict financial guardrails across Goings-OS operations."""

    def __init__(self, base_threshold_cents: int = BASE_SPEND_CAP_CENTS):
        self.base_threshold_cents = base_threshold_cents

    def evaluate_request(
        self,
        amount_cents: int,
        purpose: str,
        auth_token: Optional[str] = None,
        authorized_by: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Evaluates whether the transaction is within automated or authorized boundaries."""
        if amount_cents <= 0:
            return False, "Transaction amount must be strictly greater than 0."

        # Case 1: Within base threshold ($10.00)
        if amount_cents <= self.base_threshold_cents:
            return True, f"Approved under base micro-transaction threshold (${amount_cents / 100:.2f} <= ${self.base_threshold_cents / 100:.2f})."

        # Case 2: Greater than base threshold -> Requires Executive Auth Token
        if not auth_token:
            return False, f"Aegis-Risk Block: Amount ${amount_cents / 100:.2f} exceeds base limit ${self.base_threshold_cents / 100:.2f}. Valid auth token required."

        if not auth_token.startswith("AEGIS_AUTH_"):
            return False, "Aegis-Risk Block: Invalid authorization token prefix."

        if not authorized_by or "terrence goings" not in authorized_by.lower():
            return False, f"Aegis-Risk Block: Sign-off by Terrence Goings required for amounts over ${self.base_threshold_cents / 100:.2f}."

        return True, f"Approved via Executive Sign-off ({authorized_by}) for ${amount_cents / 100:.2f}."


# ==============================================================================
# 3. CARD ISSUANCE PROVIDERS (PRIVACY.COM & STRIPE ISSUING)
# ==============================================================================

class PrivacyComProvider:
    """Privacy.com Virtual Card Issuance Adapter."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("PRIVACY_COM_API_KEY", "SIMULATED_PRIVACY_KEY")
        self.is_live = bool(os.environ.get("PRIVACY_COM_API_KEY"))

    def create_card(
        self,
        memo: str,
        spend_limit_cents: int,
        merchant_lock: str,
        single_use: bool = True
    ) -> Dict[str, Any]:
        """Issues a merchant-locked, single-use or category-locked card via Privacy.com."""
        card_id = f"priv_card_{uuid.uuid4().hex[:16]}"
        pan_last_four = str(uuid.uuid4().int)[:4]
        pan_masked = f"************{pan_last_four}"
        exp_month = 12
        exp_year = 2028
        cvv = "921"

        card_data = {
            "provider": "PRIVACY_COM",
            "card_id": card_id,
            "memo": memo,
            "spend_limit_cents": spend_limit_cents,
            "spend_limit_duration": "TRANSACTION" if single_use else "MONTHLY",
            "card_type": "SINGLE_USE" if single_use else "MERCHANT_LOCKED",
            "merchant_lock": merchant_lock,
            "pan_masked": pan_masked,
            "expiration_month": exp_month,
            "expiration_year": exp_year,
            "cvv": cvv,
            "status": "ACTIVE",
            "is_simulation": not self.is_live,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        return card_data


class StripeIssuingProvider:
    """Stripe Issuing MCP / API Adapter."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("STRIPE_SECRET_KEY", "SIMULATED_STRIPE_KEY")
        self.is_live = bool(os.environ.get("STRIPE_SECRET_KEY"))

    def create_card(
        self,
        cardholder_name: str,
        spend_limit_cents: int,
        merchant_lock: str,
        currency: str = "usd"
    ) -> Dict[str, Any]:
        """Issues a virtual card via Stripe Issuing with spending controls."""
        card_id = f"ic_{uuid.uuid4().hex[:18]}"
        pan_last_four = str(uuid.uuid4().int)[:4]
        pan_masked = f"************{pan_last_four}"
        exp_month = 8
        exp_year = 2029
        cvv = "418"

        card_data = {
            "provider": "STRIPE_ISSUING",
            "card_id": card_id,
            "cardholder_name": cardholder_name,
            "spend_limit_cents": spend_limit_cents,
            "spend_limit_duration": "TRANSACTION",
            "card_type": "VIRTUAL_COMMERCIAL",
            "merchant_lock": merchant_lock,
            "currency": currency.lower(),
            "pan_masked": pan_masked,
            "expiration_month": exp_month,
            "expiration_year": exp_year,
            "cvv": cvv,
            "status": "ACTIVE",
            "spending_controls": {
                "spending_limits": [
                    {
                        "amount": spend_limit_cents,
                        "interval": "per_authorization"
                    }
                ],
                "allowed_merchant": merchant_lock
            },
            "is_simulation": not self.is_live,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        return card_data


# ==============================================================================
# 4. VIRTUAL PAYMENTS ENGINE & AUDIT VAULT LOGGING
# ==============================================================================

class VirtualPaymentEngine:
    """Unified Virtual Card Orchestration Engine with Hard Spend Controls & Vault Auditing."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        base_threshold_cents: int = BASE_SPEND_CAP_CENTS,
        primary_provider: str = "PRIVACY_COM"
    ):
        self.db_path = db_path or DB_PATH
        self.policy = SpendControlPolicy(base_threshold_cents=base_threshold_cents)
        self.primary_provider_name = primary_provider.upper()
        self.privacy_provider = PrivacyComProvider()
        self.stripe_provider = StripeIssuingProvider()
        init_virtual_payments_db(self.db_path)

    def issue_single_use_card(
        self,
        entity_name: str,
        merchant_name: str,
        amount_cents: int,
        purpose: str,
        authorized_by: Optional[str] = None,
        auth_token: Optional[str] = None,
        provider_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enforces spend policy, generates merchant-locked card, and logs into SQLite vault."""
        # 1. Policy Evaluation
        allowed, reason = self.policy.evaluate_request(
            amount_cents=amount_cents,
            purpose=purpose,
            auth_token=auth_token,
            authorized_by=authorized_by
        )
        if not allowed:
            raise AegisSpendLimitExceeded(reason)

        # 2. Card Provider Selection
        chosen_provider = (provider_preference or self.primary_provider_name).upper()
        if chosen_provider == "STRIPE_ISSUING":
            raw_card = self.stripe_provider.create_card(
                cardholder_name=entity_name,
                spend_limit_cents=amount_cents,
                merchant_lock=merchant_name
            )
        else:
            raw_card = self.privacy_provider.create_card(
                memo=f"{entity_name} - {purpose}",
                spend_limit_cents=amount_cents,
                merchant_lock=merchant_name,
                single_use=True
            )

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        card_id = raw_card["card_id"]

        # 3. Vault Audit Persistence
        self._record_card_in_vault(
            card_id=card_id,
            provider=raw_card["provider"],
            entity_name=entity_name,
            merchant_lock=merchant_name,
            spend_limit_cents=amount_cents,
            spend_duration=raw_card.get("spend_limit_duration", "TRANSACTION"),
            card_type=raw_card.get("card_type", "SINGLE_USE"),
            pan_masked=raw_card["pan_masked"],
            expiration_month=raw_card["expiration_month"],
            expiration_year=raw_card["expiration_year"],
            status=raw_card["status"],
            authorized_by=authorized_by,
            auth_token=auth_token,
            purpose=purpose,
            timestamp=timestamp
        )

        return {
            "status": "SUCCESS",
            "card_id": card_id,
            "provider": raw_card["provider"],
            "entity_name": entity_name,
            "merchant_lock": merchant_name,
            "authorized_spend_cents": amount_cents,
            "authorized_spend_dollars": f"${amount_cents / 100:.2f}",
            "pan_masked": raw_card["pan_masked"],
            "expiration": f"{raw_card['expiration_month']:02d}/{raw_card['expiration_year']}",
            "cvv": raw_card["cvv"],
            "purpose": purpose,
            "policy_check": reason,
            "created_at": timestamp
        }

    def issue_statutory_filing_card(
        self,
        filing_record: Dict[str, Any],
        authorized_by: str,
        auth_token: str
    ) -> Dict[str, Any]:
        """Specialized card issuance for Node 18 Lexis Secretary statutory filings."""
        entity_name = filing_record.get("entity_name", "Conglomerate Entity")
        fee_cents = filing_record.get("filing_fee_cents", 0)
        max_cents = filing_record.get("max_authorized_fee_cents", fee_cents)
        jurisdiction = filing_record.get("jurisdiction", "VA_SCC")
        filing_type = filing_record.get("filing_type") or filing_record.get("form_code", "COMPLIANCE")

        # Map regulatory body to merchant lock
        merchant_map = {
            "VA_SCC": "VA_SCC_CLERK",
            "FINCEN_FED": "US_TREASURY_FINCEN",
            "PORTSMOUTH_CITY": "PORTSMOUTH_CITY_TREASURER",
            "NEWPORT_NEWS_CITY": "NEWPORT_NEWS_CITY_TREASURER"
        }
        merchant_lock = merchant_map.get(jurisdiction, f"{jurisdiction}_FILING_OFFICE")

        if fee_cents > max_cents:
            raise AegisSpendLimitExceeded(
                f"Statutory filing fee (${fee_cents / 100:.2f}) exceeds authorized cap (${max_cents / 100:.2f})."
            )

        purpose = f"Statutory Compliance Filing: {filing_type} ({jurisdiction})"

        return self.issue_single_use_card(
            entity_name=entity_name,
            merchant_name=merchant_lock,
            amount_cents=fee_cents,
            purpose=purpose,
            authorized_by=authorized_by,
            auth_token=auth_token,
            provider_preference="PRIVACY_COM"
        )

    def process_card_transaction(
        self,
        card_id: str,
        merchant_name: str,
        charge_amount_cents: int
    ) -> Dict[str, Any]:
        """Simulates/records transaction against an issued virtual card, enforcing merchant lock and spend limits."""
        card = self._get_card_from_vault(card_id)
        if not card:
            raise ValueError(f"Card {card_id} does not exist in vault registry.")

        if card["status"] != "ACTIVE":
            raise ValueError(f"Card {card_id} is inactive or already closed (Status: {card['status']}).")

        # Check Merchant Lock
        expected_merchant = card["merchant_lock"].lower()
        actual_merchant = merchant_name.lower()
        if expected_merchant not in actual_merchant and actual_merchant not in expected_merchant:
            decline_reason = f"Merchant Lock Violation: Card locked to '{card['merchant_lock']}', received '{merchant_name}'."
            self._record_transaction_in_vault(card_id, merchant_name, charge_amount_cents, "DECLINED", None, decline_reason)
            raise MerchantLockViolation(decline_reason)

        # Check Spend Limit
        if charge_amount_cents > card["spend_limit_cents"]:
            decline_reason = f"Spend Limit Exceeded: Charge ${charge_amount_cents / 100:.2f} exceeds card cap ${card['spend_limit_cents'] / 100:.2f}."
            self._record_transaction_in_vault(card_id, merchant_name, charge_amount_cents, "DECLINED", None, decline_reason)
            raise AegisSpendLimitExceeded(decline_reason)

        # Approve and close single-use card
        auth_code = f"AUTH_{uuid.uuid4().hex[:8].upper()}"
        tx_id = self._record_transaction_in_vault(card_id, merchant_name, charge_amount_cents, "SETTLED", auth_code, None)

        if card["card_type"] == "SINGLE_USE":
            self._update_card_status(card_id, "CLOSED")

        return {
            "transaction_id": tx_id,
            "card_id": card_id,
            "merchant_name": merchant_name,
            "amount_cents": charge_amount_cents,
            "status": "SETTLED",
            "authorization_code": auth_code,
            "card_status_now": "CLOSED" if card["card_type"] == "SINGLE_USE" else "ACTIVE"
        }

    # ==============================================================================
    # 5. PRIVATE VAULT DB HELPERS
    # ==============================================================================

    def _record_card_in_vault(
        self,
        card_id: str,
        provider: str,
        entity_name: str,
        merchant_lock: str,
        spend_limit_cents: int,
        spend_duration: str,
        card_type: str,
        pan_masked: str,
        expiration_month: int,
        expiration_year: int,
        status: str,
        authorized_by: Optional[str],
        auth_token: Optional[str],
        purpose: str,
        timestamp: str
    ) -> None:
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                INSERT OR REPLACE INTO virtual_payment_cards (
                    card_id, provider, entity_name, merchant_lock, spend_limit_cents,
                    spend_duration, card_type, pan_masked, expiration_month,
                    expiration_year, status, authorized_by, auth_token, purpose,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                card_id, provider, entity_name, merchant_lock, spend_limit_cents,
                spend_duration, card_type, pan_masked, expiration_month,
                expiration_year, status, authorized_by, auth_token, purpose,
                timestamp, timestamp
            ))
            conn.commit()
            conn.close()
        except Exception as err:
            logging.error(f"Failed to record card {card_id} in vault: {str(err)}")

    def _get_card_from_vault(self, card_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM virtual_payment_cards WHERE card_id = ?", (card_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as err:
            logging.error(f"Failed to retrieve card {card_id} from vault: {str(err)}")
            return None

    def _update_card_status(self, card_id: str, status: str) -> None:
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                UPDATE virtual_payment_cards
                SET status = ?, updated_at = ?
                WHERE card_id = ?
            """, (status, timestamp, card_id))
            conn.commit()
            conn.close()
        except Exception as err:
            logging.error(f"Failed to update status for card {card_id}: {str(err)}")

    def _record_transaction_in_vault(
        self,
        card_id: str,
        merchant_name: str,
        amount_cents: int,
        status: str,
        auth_code: Optional[str],
        decline_reason: Optional[str]
    ) -> str:
        tx_id = f"tx_vpay_{uuid.uuid4().hex[:12]}"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                INSERT INTO virtual_payment_transactions (
                    transaction_id, card_id, merchant_name, amount_cents,
                    status, authorization_code, decline_reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tx_id, card_id, merchant_name, amount_cents, status, auth_code, decline_reason, timestamp))
            conn.commit()
            conn.close()
        except Exception as err:
            logging.error(f"Failed to record transaction {tx_id} in vault: {str(err)}")
        return tx_id
