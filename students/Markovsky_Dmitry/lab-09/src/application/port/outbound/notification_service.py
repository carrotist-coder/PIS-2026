"""Outbound port for notifications."""

from abc import ABC, abstractmethod


class NotificationService(ABC):
    """
    Outbound port: Service for sending notifications.
    
    This interface defines how the application layer sends
    notifications to users (email, SMS, push, etc.).
    """
    
    @abstractmethod
    def send_invoice_created(
        self,
        client_email: str,
        deal_title: str,
        invoice_id: str,
        payment_link: str
    ) -> None:
        """
        Send invoice created notification to client.
        
        Args:
            client_email: Email address of the client
            deal_title: Title of the deal
            invoice_id: Invoice identifier
            payment_link: URL for payment
            
        Note:
            This operation is asynchronous and may be queued for retry.
        """
        pass
    
    @abstractmethod
    def notify_manager(
        self,
        manager_email: str,
        deal_id: str,
        message: str
    ) -> None:
        """
        Send notification to manager.
        
        Args:
            manager_email: Email address of the manager
            deal_id: Deal identifier
            message: Notification message content
        """
        pass