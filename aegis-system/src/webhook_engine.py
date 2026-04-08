"""
AEGIS Webhook Execution Engine
Agents can trigger real external actions via webhooks, API calls, and email.
"""

import json
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger("aegis.webhook_engine")


class WebhookAction:
    """A single webhook action to be executed."""

    def __init__(
        self,
        name: str,
        url: str,
        method: str = "POST",
        headers: Dict[str, str] = None,
        payload: Dict[str, Any] = None,
        timeout: int = 30,
    ):
        self.name = name
        self.url = url
        self.method = method.upper()
        self.headers = headers or {"Content-Type": "application/json"}
        self.payload = payload or {}
        self.timeout = timeout
        self.id = str(uuid4())
        self.created_at = datetime.utcnow().isoformat()

    async def execute(self) -> Dict[str, Any]:
        """Execute the webhook action and return result."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=self.method,
                    url=self.url,
                    headers=self.headers,
                    json=self.payload if self.method in ("POST", "PUT", "PATCH") else None,
                )
                result = {
                    "id": self.id,
                    "name": self.name,
                    "url": self.url,
                    "status_code": response.status_code,
                    "success": 200 <= response.status_code < 300,
                    "response": response.text[:2000] if response.text else "",
                    "executed_at": datetime.utcnow().isoformat(),
                }
                logger.info(f"Webhook {self.name}: {response.status_code}")
                return result
        except Exception as e:
            result = {
                "id": self.id,
                "name": self.name,
                "url": self.url,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "executed_at": datetime.utcnow().isoformat(),
            }
            logger.error(f"Webhook {self.name} failed: {e}")
            return result


class EmailAction:
    """Send email alert via SMTP."""

    def __init__(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_user: str = "",
        smtp_pass: str = "",
    ):
        self.to = to
        self.subject = subject
        self.body = body
        self.html = html
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.id = str(uuid4())
        self.created_at = datetime.utcnow().isoformat()

    async def execute(self) -> Dict[str, Any]:
        """Send the email and return result."""
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = self.to
            msg["Subject"] = self.subject

            if self.html:
                msg.attach(MIMEText(self.body, "html"))
            else:
                msg.attach(MIMEText(self.body, "plain"))

            async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port, start_tls=True) as smtp:
                await smtp.login(self.smtp_user, self.smtp_pass)
                await smtp.send_message(msg)

            result = {
                "id": self.id,
                "type": "email_sent",
                "to": self.to,
                "subject": self.subject,
                "success": True,
                "executed_at": datetime.utcnow().isoformat(),
            }
            logger.info(f"Email sent to {self.to}: {self.subject}")
            return result
        except Exception as e:
            result = {
                "id": self.id,
                "type": "email_failed",
                "to": self.to,
                "subject": self.subject,
                "success": False,
                "error": str(e),
                "executed_at": datetime.utcnow().isoformat(),
            }
            logger.error(f"Email to {self.to} failed: {e}")
            return result


class WebhookEngine:
    """
    Central engine for executing webhooks and emails.
    Agents call this to take real-world actions.
    """

    def __init__(self):
        self.execution_log: List[Dict[str, Any]] = []
        self.registered_webhooks: List[WebhookAction] = []

    async def execute_webhook(
        self,
        name: str,
        url: str,
        method: str = "POST",
        headers: Dict[str, str] = None,
        payload: Dict[str, Any] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Execute a webhook action."""
        action = WebhookAction(
            name=name, url=url, method=method, headers=headers, payload=payload, timeout=timeout
        )
        result = await action.execute()
        self.execution_log.append(result)
        return result

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        smtp_user: str = "",
        smtp_pass: str = "",
    ) -> Dict[str, Any]:
        """Send an email alert."""
        action = EmailAction(
            to=to,
            subject=subject,
            body=body,
            html=html,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
        )
        result = await action.execute()
        self.execution_log.append(result)
        return result

    def register_webhook(
        self,
        name: str,
        url: str,
        method: str = "POST",
        headers: Dict[str, str] = None,
        payload: Dict[str, Any] = None,
    ):
        """Register a webhook for later execution."""
        webhook = WebhookAction(name=name, url=url, method=method, headers=headers, payload=payload)
        self.registered_webhooks.append(webhook)
        return webhook.id

    async def execute_registered_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Execute a registered webhook by ID."""
        for webhook in self.registered_webhooks:
            if webhook.id == webhook_id:
                result = await webhook.execute()
                self.execution_log.append(result)
                return result
        return {"error": f"Webhook {webhook_id} not found", "success": False}

    def get_execution_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent execution log entries."""
        return self.execution_log[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get webhook execution statistics."""
        total = len(self.execution_log)
        success = sum(1 for e in self.execution_log if e.get("success"))
        return {
            "total_executions": total,
            "successful": success,
            "failed": total - success,
            "success_rate": round(success / total * 100, 1) if total > 0 else 0,
            "registered_webhooks": len(self.registered_webhooks),
        }


# Global instance
webhook_engine = WebhookEngine()
