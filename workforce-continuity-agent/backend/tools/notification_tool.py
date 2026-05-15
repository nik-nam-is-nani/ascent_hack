from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class NotificationChannel(str, Enum):
    SLACK = "slack"
    EMAIL = "email"
    SMS = "sms"


class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_REASSIGNED = "task_reassigned"
    TASK_AUTO_COMPLETED = "task_auto_completed"
    ABSENCE_ALERT = "absence_alert"
    MANAGER_REPORT = "manager_report"


class Notification(BaseModel):
    id: str
    channel: NotificationChannel
    recipient: str
    subject: str
    message: str
    notification_type: NotificationType
    sent_at: datetime = None
    metadata: Dict = {}


# Mock notification log
notifications_log: List[Notification] = []


def send_slack_message(channel: str, message: str, metadata: Dict = {}) -> Notification:
    """Send a mock Slack message"""
    notification = Notification(
        id=f"NOTIF-{len(notifications_log) + 1:04d}",
        channel=NotificationChannel.SLACK,
        recipient=channel,
        subject="Workforce Continuity Agent",
        message=message,
        notification_type=NotificationType.TASK_ASSIGNED,
        sent_at=datetime.now(),
        metadata=metadata
    )
    notifications_log.append(notification)
    return notification


def send_email(recipient: str, subject: str, body: str, metadata: Dict = {}) -> Notification:
    """Send a mock email"""
    notification = Notification(
        id=f"NOTIF-{len(notifications_log) + 1:04d}",
        channel=NotificationChannel.EMAIL,
        recipient=recipient,
        subject=subject,
        message=body,
        notification_type=NotificationType.MANAGER_REPORT,
        sent_at=datetime.now(),
        metadata=metadata
    )
    notifications_log.append(notification)
    return notification


def notify_task_assignment(employee_id: str, employee_name: str, task_title: str, task_id: str) -> Notification:
    """Notify employee of new task assignment"""
    message = f"New task assigned: {task_title} (ID: {task_id})"
    return send_slack_message(
        channel=f"#{employee_name.lower().replace(' ', '-')}",
        message=message,
        metadata={"task_id": task_id, "employee_id": employee_id}
    )


def notify_task_reassignment(employee_id: str, employee_name: str, task_title: str, task_id: str, reason: str) -> Notification:
    """Notify employee of task reassignment"""
    message = f"Task reassigned to you: {task_title} (ID: {task_id})\nReason: {reason}"
    return send_slack_message(
        channel=f"#{employee_name.lower().replace(' ', '-')}",
        message=message,
        metadata={"task_id": task_id, "employee_id": employee_id, "reason": reason}
    )


def notify_absence_alert(manager_id: str, manager_name: str, employee_name: str) -> Notification:
    """Alert manager about employee absence"""
    message = f"Alert: {employee_name} has been marked as absent. Workforce Continuity Agent activated."
    return send_slack_message(
        channel=f"#{manager_name.lower().replace(' ', '-')}",
        message=message,
        metadata={"employee_name": employee_name, "action": "absence_alert"}
    )


def get_notifications_for_employee(employee_id: str) -> List[Notification]:
    """Get all notifications for an employee"""
    return [n for n in notifications_log if n.recipient == employee_id]


def get_all_notifications() -> List[Notification]:
    """Get all sent notifications"""
    return notifications_log


def log_notification(notification: Notification) -> Notification:
    """Log a notification"""
    notifications_log.append(notification)
    return notification