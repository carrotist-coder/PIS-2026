"""Console implementation of NotificationService."""

from src.application.port.outbound.notification_service import NotificationService


class ConsoleNotificationService(NotificationService):
    """
    Simple console implementation of NotificationService.

    Prints notifications to console instead of actually sending emails.
    Useful for development and debugging.

    In production, this would be replaced with real email/SMS services.
    """

    def send_invoice_created(
        self,
        client_email: str,
        deal_title: str,
        invoice_id: str,
        payment_link: str
    ) -> None:
        """
        Print invoice notification to console.

        Args:
            client_email: Client's email address
            deal_title: Deal title
            invoice_id: Invoice identifier
            payment_link: Payment URL
        """
        print(f"NOTIFICATION: Invoice Created")
        print(f"To: {client_email}")
        print(f"Subject: Invoice {invoice_id} for {deal_title}")
        print(f"\nDear Client,")
        print(f"\nYour invoice {invoice_id} for deal '{deal_title}' is ready.")
        print(f"\nPayment link: {payment_link}")
        print("\nThank you for your business!")

    def notify_manager(self, manager_email: str, deal_id: str, message: str) -> None:
        """
        Print manager notification to console.

        Args:
            manager_email: Manager's email address
            deal_id: Deal identifier
            message: Notification message
        """
        print(f"MANAGER NOTIFICATION")
        print(f"To: {manager_email}")
        print(f"Deal: {deal_id}")
        print(f"Message: {message}")
