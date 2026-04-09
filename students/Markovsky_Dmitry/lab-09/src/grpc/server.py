"""
gRPC Server: Deal Service

Реализует все RPC методы из deal_service.proto
"""

import grpc
from concurrent import futures
import time
import sys
import os
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from generated import deal_service_pb2, deal_service_pb2_grpc


class DealServiceServicer(deal_service_pb2_grpc.DealServiceServicer):
  """gRPC Server: Реализация Deal Service"""

  def __init__(self):
    self.deals = {}
    self.counter = 1
    self.subscribers = {}  # deal_id -> list of active streams
    self._seed_data()

  def _seed_data(self):
    """Создание тестовых сделок"""
    test_deals = [
      ("cli-0001", "Landing Page", 1500.00, "USD", "negotiation"),
      ("cli-0002", "Mobile App", 5000.00, "USD", "invoiced"),
      ("cli-0001", "SEO Optimization", 800.00, "EUR", "paid"),
    ]

    for client_id, title, amount, currency, status in test_deals:
      deal_id = f"D-2026-{self.counter:04d}"
      deal = deal_service_pb2.Deal(
        deal_id=deal_id,
        client_id=client_id,
        title=title,
        amount=deal_service_pb2.Money(amount=amount, currency=currency),
        status=status,
        created_at=int(time.time()),
        updated_at=int(time.time())
      )
      self.deals[deal_id] = deal
      self.counter += 1

  def _notify_subscribers(self, deal_id: str, deal):
    """Уведомить всех подписчиков об изменении сделки"""
    if deal_id in self.subscribers:
      for callback in self.subscribers[deal_id]:
        callback(deal)

  def CreateDeal(self, request, context):
    """Unary RPC: Создать сделку"""
    deal_id = f"D-2026-{self.counter:04d}"
    self.counter += 1

    deal = deal_service_pb2.Deal(
      deal_id=deal_id,
      client_id=request.client_id,
      title=request.title,
      amount=deal_service_pb2.Money(amount=request.amount, currency=request.currency or "USD"),
      status="negotiation",
      created_at=int(time.time()),
      updated_at=int(time.time())
    )

    self.deals[deal_id] = deal
    self._notify_subscribers(deal_id, deal)

    print(f"Deal created: {deal_id}")

    return deal_service_pb2.CreateDealResponse(
      deal_id=deal_id,
      success=True
    )

  def GetDeal(self, request, context):
    """Unary RPC: Получить сделку по ID"""
    deal = self.deals.get(request.deal_id)

    if deal:
      return deal_service_pb2.GetDealResponse(deal=deal, found=True)
    else:
      context.set_code(grpc.StatusCode.NOT_FOUND)
      return deal_service_pb2.GetDealResponse(found=False)

  def MarkDealAsPaid(self, request, context):
    """Unary RPC: Отметить сделку как оплаченную"""
    deal = self.deals.get(request.deal_id)

    if not deal:
      return deal_service_pb2.MarkDealAsPaidResponse(
        success=False, error_message="Deal not found"
      )

    if deal.status != "invoiced":
      return deal_service_pb2.MarkDealAsPaidResponse(
        success=False, error_message=f"Cannot pay deal with status {deal.status}"
      )

    # Обновление статуса
    deal.status = "paid"
    deal.updated_at = int(time.time())
    self.deals[request.deal_id] = deal
    self._notify_subscribers(request.deal_id, deal)

    print(f"Deal marked as paid: {request.deal_id}")

    return deal_service_pb2.MarkDealAsPaidResponse(success=True)

  def ListDeals(self, request, context):
    """Unary RPC: Список сделок"""
    filtered = [
      deal for deal in self.deals.values()
      if not request.status_filter or deal.status == request.status_filter
    ]

    limit = request.limit if request.limit > 0 else 50
    results = filtered[:limit]

    return deal_service_pb2.ListDealsResponse(
      deals=results,
      total_count=len(filtered)
    )

  def StreamDealUpdates(self, request, context):
    """
    Server-side Streaming: Real-time обновления сделки

    Клиент подписывается на обновления по deal_id.
    Сервер отправляет изменения по мере их поступления.
    """
    deal_id = request.deal_id
    queue = []
    event = threading.Event()

    def callback(updated_deal):
      if not deal_id or updated_deal.deal_id == deal_id:
        queue.append(updated_deal)
        event.set()

    if deal_id not in self.subscribers:
      self.subscribers[deal_id] = []
    self.subscribers[deal_id].append(callback)

    print(f"Client subscribed to deal: {deal_id or 'ALL'}")

    try:
      while context.is_active():
        event.wait(timeout=5)
        event.clear()

        for updated_deal in queue:
          yield updated_deal
        queue.clear()

    finally:
      # Отписка при закрытии соединения
      if deal_id in self.subscribers:
        self.subscribers[deal_id].remove(callback)
        if not self.subscribers[deal_id]:
          del self.subscribers[deal_id]

      print(f"Client unsubscribed from deal: {deal_id or 'ALL'}")


def serve():
  """Запуск gRPC сервера"""
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  deal_service_pb2_grpc.add_DealServiceServicer_to_server(DealServiceServicer(), server)
  server.add_insecure_port('[::]:50051')
  server.start()

  print("gRPC Server started on port 50051")
  print("Listening for requests...")

  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    print("\nStopping server...")
    server.stop(0)


if __name__ == '__main__':
  serve()
