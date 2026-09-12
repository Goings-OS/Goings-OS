# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: MULTI-CHANNEL ALERTING (core_nodes/node_17_auto_updater/notifier.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; ENTERPRISE ALERTING
# ==============================================================================

import os
import time
import json
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

# Notification Channels Configuration
GOOGLE_CHAT_WEBHOOK_ENV = "GOOGLE_CHAT_AUTO_UPDATE_WEBHOOK"
TELEGRAM_BOT_TOKEN_ENV = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID_ENV = "TELEGRAM_CHAT_ID"
TWILIO_ACCOUNT_SID_ENV = "TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN_ENV = "TWILIO_AUTH_TOKEN"
TWILIO_FROM_NUMBER_ENV = "TWILIO_FROM_NUMBER"
TWILIO_TO_NUMBER_ENV = "TWILIO_TO_NUMBER"


class MultiChannelNotifier:
    """Dispatches autonomous update telemetry across Google Chat, Telegram, and Voice."""

    def __init__(
        self,
        google_chat_webhook: Optional[str] = None,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        twilio_account_sid: Optional[str] = None,
        twilio_auth_token: Optional[str] = None,
        twilio_from_number: Optional[str] = None,
        twilio_to_number: Optional[str] = None
    ):
        self.google_chat_webhook = google_chat_webhook or os.environ.get(GOOGLE_CHAT_WEBHOOK_ENV)
        self.telegram_bot_token = telegram_bot_token or os.environ.get(TELEGRAM_BOT_TOKEN_ENV)
        self.telegram_chat_id = telegram_chat_id or os.environ.get(TELEGRAM_CHAT_ID_ENV)
        self.twilio_account_sid = twilio_account_sid or os.environ.get(TWILIO_ACCOUNT_SID_ENV)
        self.twilio_auth_token = twilio_auth_token or os.environ.get(TWILIO_AUTH_TOKEN_ENV)
        self.twilio_from_number = twilio_from_number or os.environ.get(TWILIO_FROM_NUMBER_ENV)
        self.twilio_to_number = twilio_to_number or os.environ.get(TWILIO_TO_NUMBER_ENV)

    # ==========================================================================
    # 1. GOOGLE CHAT INTERACTIVE CARD V2
    # ==========================================================================

    def build_google_chat_card(
        self,
        title: str,
        summary: str,
        diff_snippet: str,
        approval_url: str,
        severity: str = "INFO",
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Constructs Google Chat Card v2 containing diffs and interactive approval button."""
        severity_color = "#D9381E" if severity in ("CRITICAL", "SECURITY") else "#F4B400" if severity == "WARNING" else "#0F9D58"
        
        card_payload = {
            "cardsV2": [
                {
                    "cardId": f"auto_update_{int(os.times().elapsed * 1000)}",
                    "card": {
                        "header": {
                            "title": title,
                            "subtitle": f"Branch: {branch} | Severity: {severity}",
                            "imageUrl": "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/system_update/default/48px.svg",
                            "imageType": "CIRCLE"
                        },
                        "sections": [
                            {
                                "header": "Update Diagnostics",
                                "widgets": [
                                    {
                                        "decoratedText": {
                                            "topLabel": "Execution Severity",
                                            "text": f"<b>{severity}</b>",
                                            "bottomLabel": "Autonomous Engine: Node 17 Auto Updater"
                                        }
                                    },
                                    {
                                        "textParagraph": {
                                            "text": summary
                                        }
                                    }
                                ]
                            },
                            {
                                "header": "Proposed Code Diff",
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": f"<font color=\"#666666\"><pre>{diff_snippet[:1500]}</pre></font>"
                                        }
                                    }
                                ]
                            },
                            {
                                "header": "Executive Action",
                                "widgets": [
                                    {
                                        "buttonList": {
                                            "buttons": [
                                                {
                                                    "text": "Approve & Merge",
                                                    "onClick": {
                                                        "openLink": {
                                                            "url": approval_url
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        return card_payload

    def send_google_chat(
        self,
        title: str,
        summary: str,
        diff_snippet: str,
        approval_url: str,
        severity: str = "INFO",
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Posts interactive card to Google Chat webhook."""
        payload = self.build_google_chat_card(
            title=title,
            summary=summary,
            diff_snippet=diff_snippet,
            approval_url=approval_url,
            severity=severity,
            branch=branch
        )

        if not self.google_chat_webhook:
            logging.info("Google Chat webhook unconfigured; simulated card output recorded.")
            return {"status": "SIMULATED", "channel": "google_chat", "payload": payload}

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.google_chat_webhook,
                data=req_data,
                headers={"Content-Type": "application/json; charset=UTF-8"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                resp_data = resp.read().decode("utf-8")
                return {"status": "DELIVERED", "channel": "google_chat", "response": resp_data}
        except Exception as err:
            logging.error(f"Google Chat dispatch fault: {str(err)}")
            return {"status": "FAILED", "channel": "google_chat", "error": str(err)}

    # ==========================================================================
    # 2. TELEGRAM BOT API PUSH NOTIFICATIONS
    # ==========================================================================

    def send_telegram(
        self,
        title: str,
        summary: str,
        branch: str,
        severity: str,
        approval_url: str
    ) -> Dict[str, Any]:
        """Dispatches instant push notification via Telegram Bot API."""
        msg_text = (
            f"🚀 *GOINGS OS v4.2 AUTO UPDATE*\n"
            f"*Title:* {title}\n"
            f"*Branch:* `{branch}`\n"
            f"*Severity:* *{severity}*\n\n"
            f"*Summary:* {summary}\n\n"
            f"👉 [Review & Approve Deployment]({approval_url})"
        )

        payload: Dict[str, Any] = {
            "chat_id": self.telegram_chat_id,
            "text": msg_text,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "✅ Approve & Merge", "url": approval_url}
                    ]
                ]
            }
        }

        if not self.telegram_bot_token or not self.telegram_chat_id:
            logging.info("Telegram Bot credentials unconfigured; simulated notification recorded.")
            return {"status": "SIMULATED", "channel": "telegram", "payload": payload}

        try:
            api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                api_url,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                resp_data = resp.read().decode("utf-8")
                return {"status": "DELIVERED", "channel": "telegram", "response": resp_data}
        except Exception as err:
            logging.error(f"Telegram dispatch fault: {str(err)}")
            return {"status": "FAILED", "channel": "telegram", "error": str(err)}

    # ==========================================================================
    # 3. VOICE ESCALATION (TWILIO / GCP CALL API)
    # ==========================================================================

    def trigger_voice_call(self, message_text: str) -> Dict[str, Any]:
        """Triggers voice call for critical security patches."""
        twiml_payload = f"<Response><Say voice='Polly.Amy'>{message_text}</Say><Pause length='1'/><Say>Please check your emergency alert inbox immediately to authorize the security patch.</Say></Response>"
        
        call_params = {
            "To": self.twilio_to_number,
            "From": self.twilio_from_number,
            "Twiml": twiml_payload
        }

        if not (self.twilio_account_sid and self.twilio_auth_token and self.twilio_to_number and self.twilio_from_number):
            logging.info(f"Voice escalation simulated: {message_text}")
            return {
                "status": "SIMULATED",
                "channel": "voice",
                "message": message_text,
                "twiml": twiml_payload
            }

        try:
            import base64
            api_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Calls.json"
            encoded_body = urllib.parse.urlencode(call_params).encode("utf-8")
            auth_header = "Basic " + base64.b64encode(f"{self.twilio_account_sid}:{self.twilio_auth_token}".encode()).decode("ascii")

            req = urllib.request.Request(
                api_url,
                data=encoded_body,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                resp_data = resp.read().decode("utf-8")
                return {"status": "DELIVERED", "channel": "voice", "response": resp_data}
        except Exception as err:
            logging.error(f"Voice escalation dispatch fault: {str(err)}")
            return {"status": "FAILED", "channel": "voice", "error": str(err)}

    # ==========================================================================
    # 4. UNIFIED DISPATCH COORDINATOR
    # ==========================================================================

    def dispatch_alert(
        self,
        title: str,
        summary: str,
        diff_snippet: str,
        approval_url: str,
        severity: str = "INFO",
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Coordinates notification across configured channels according to severity."""
        results: Dict[str, Any] = {}

        # 1. Google Chat Card
        results["google_chat"] = self.send_google_chat(
            title=title,
            summary=summary,
            diff_snippet=diff_snippet,
            approval_url=approval_url,
            severity=severity,
            branch=branch
        )

        # 2. Telegram Push
        results["telegram"] = self.send_telegram(
            title=title,
            summary=summary,
            branch=branch,
            severity=severity,
            approval_url=approval_url
        )

        # 3. Voice Escalation on Critical Security Advisories
        if severity in ("CRITICAL", "SECURITY"):
            voice_message = f"Urgent Goings OS security alert: Critical patch available on branch {branch}. Immediate approval required."
            results["voice"] = self.trigger_voice_call(voice_message)

        return results

    def notify_deployment_approval(
        self,
        branch: str,
        timestamp: int,
        client_ip: str = "unknown"
    ) -> Dict[str, Any]:
        """Dispatches notification confirming deployment authorization and merge trigger."""
        date_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(timestamp)) if timestamp else time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        title = f"DEPLOYMENT APPROVED: {branch}"
        summary = (
            f"Autonomous patch deployment on branch {branch} was cryptographically authorized. "
            f"Authorized at {date_str} by client {client_ip}. Production merge initiated."
        )

        results: Dict[str, Any] = {}
        # Google Chat confirmation
        results["google_chat"] = self.send_google_chat(
            title=title,
            summary=summary,
            diff_snippet=f"Branch {branch} verified and queued for deployment.",
            approval_url="#approved",
            severity="INFO",
            branch=branch
        )
        # Telegram confirmation
        results["telegram"] = self.send_telegram(
            title=title,
            summary=summary,
            branch=branch,
            severity="INFO",
            approval_url="#approved"
        )
        return results

