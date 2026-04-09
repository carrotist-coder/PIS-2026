"""
gRPC Client: Deal Service

Демонстрация вызовов всех RPC методов
"""

import grpc
import sys
import os
import threading
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from generated import deal_service_pb2, deal_service_pb2_grpc


def create_deal(stub):
  """Unary RPC: Создать сделку"""
  print("\n CreateDeal ")

  request = deal_service_pb2.CreateDealRequest(
    client_id="cli-test-001",
    title="gRPC Test Deal",
    amount=2500.00,
    currency="USD"
  )

  response = stub.CreateDeal(request)

  if response.success:
    print(f"Deal created: {response.deal_id}")
    return response.deal_id
  else:
    print(f"Error: {response.error_message}")
    return None


def get_deal(stub, deal_id):
  """Unary RPC: Получить сделку"""
  print(f"\n GetDeal({deal_id}) ")

  request = deal_service_pb2.GetDealRequest(deal_id=deal_id)
  response = stub.GetDeal(request)

  if response.found:
    deal = response.deal
    print(f"Deal ID: {deal.deal_id}")
    print(f"Client: {deal.client_id}")
    print(f"Title: {deal.title}")
    print(f"Amount: {deal.amount.amount} {deal.amount.currency}")
    print(f"Status: {deal.status}")
  else:
    print("Deal not found")


def mark_deal_as_paid(stub, deal_id):
  """Unary RPC: Отметить оплату"""
  print(f"\n MarkDealAsPaid({deal_id}) ")

  request = deal_service_pb2.MarkDealAsPaidRequest(deal_id=deal_id)
  response = stub.MarkDealAsPaid(request)

  if response.success:
    print(f"Deal marked as paid: {deal_id}")
  else:
    print(f"Error: {response.error_message}")


def list_deals(stub, status_filter=None):
  """Unary RPC: Список сделок"""
  request = deal_service_pb2.ListDealsRequest(
    status_filter=status_filter or "",
    limit=10
  )

  response = stub.ListDeals(request)

  print(f"Found {response.total_count} deals:")
  for deal in response.deals:
    print(f" {deal.deal_id} | {deal.status} | {deal.title} | {deal.amount.amount} {deal.amount.currency}")


def stream_deal_updates(stub, deal_id=None):
  """Server-side Streaming: Подписка на обновления сделки"""
  print("Listening for updates (press Ctrl+C to stop)...")

  request = deal_service_pb2.StreamDealUpdatesRequest(deal_id=deal_id or "")

  try:
    for deal in stub.StreamDealUpdates(request):
      print(f"Update: {deal.deal_id} | {deal.status} | {deal.title}")
  except KeyboardInterrupt:
    print("\nStopped streaming")


def run():
  channel = grpc.insecure_channel('localhost:50051')
  stub = deal_service_pb2_grpc.DealServiceStub(channel)

  # Создание сделки
  deal_id = create_deal(stub)

  if deal_id:
    # Получение сделки
    get_deal(stub, deal_id)

    # Список всех сделок
    list_deals(stub)

    # Список только оплаченных
    list_deals(stub, status_filter="paid")

  print("Starting streaming in background thread...")
  stream_thread = threading.Thread(target=stream_deal_updates, args=(stub,), daemon=True)
  stream_thread.start()

  time.sleep(10)
  print("Demo completed!")


if __name__ == '__main__':
  run()
