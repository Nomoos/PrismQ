"""
Example task handlers for demonstrating configuration-based registration.

These handlers are referenced in configs/task_handlers.json
"""

import logging
from .models import Task

logger = logging.getLogger(__name__)


def handle_send_email(task: Task) -> None:
    """
    Handle email sending tasks.
    
    Expected payload:
    - to: email address
    - subject: email subject
    - body: email body
    """
    payload = task.get_payload_dict()
    
    to = payload.get('to', 'unknown@example.com')
    subject = payload.get('subject', 'No subject')
    body = payload.get('body', '')
    
    logger.info(f"Sending email to {to}: {subject}")
    # Actual email sending logic would go here
    print(f"📧 Email sent to {to}: {subject}")


def handle_generate_report(task: Task) -> None:
    """
    Handle report generation tasks.
    
    Expected payload:
    - report_type: type of report (sales, inventory, etc.)
    - format: output format (pdf, csv, xlsx)
    - filters: dict of filter criteria
    """
    payload = task.get_payload_dict()
    
    report_type = payload.get('report_type', 'unknown')
    format = payload.get('format', 'pdf')
    filters = payload.get('filters', {})
    
    logger.info(f"Generating {report_type} report in {format} format")
    # Actual report generation logic would go here
    print(f"📊 Generated {report_type} report ({format})")


def handle_backup_database(task: Task) -> None:
    """
    Handle database backup tasks.
    
    Expected payload:
    - database_name: name of database to backup
    - backup_path: destination path for backup
    - compress: whether to compress backup
    """
    payload = task.get_payload_dict()
    
    database_name = payload.get('database_name', 'default')
    backup_path = payload.get('backup_path', '/backups')
    compress = payload.get('compress', True)
    
    logger.info(f"Backing up database {database_name} to {backup_path}")
    # Actual backup logic would go here
    compression = " (compressed)" if compress else ""
    print(f"💾 Database {database_name} backed up{compression}")


def handle_process_payment(task: Task) -> None:
    """
    Handle payment processing tasks.
    
    Expected payload:
    - amount: payment amount
    - currency: currency code
    - payment_method: payment method type
    - customer_id: customer identifier
    """
    payload = task.get_payload_dict()
    
    amount = payload.get('amount', 0.0)
    currency = payload.get('currency', 'USD')
    payment_method = payload.get('payment_method', 'credit_card')
    customer_id = payload.get('customer_id', 'unknown')
    
    logger.info(
        f"Processing payment of {amount} {currency} for customer {customer_id}"
    )
    # Actual payment processing logic would go here
    print(f"💳 Processed payment: {currency} {amount} ({payment_method})")
