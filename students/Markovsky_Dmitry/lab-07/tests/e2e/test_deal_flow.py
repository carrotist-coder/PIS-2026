import requests

BASE_URL = "http://localhost:8000"


class TestDealE2E:
    def test_full_deal_lifecycle(self):
        # Шаг 1: Создание сделки
        create_payload = {
            "client_id": "e2e-client-001",
            "title": "E2E Тестовая сделка",
            "amount": 5000.00,
            "currency": "USD"
        }

        response = requests.post(
            f"{BASE_URL}/api/deals",
            json=create_payload
        )
        assert response.status_code == 201
        deal_id = response.json()["deal_id"]
        print(f"Создана сделка: {deal_id}")

        # Шаг 2: Получение сделки
        response = requests.get(f"{BASE_URL}/api/deals/{deal_id}")
        assert response.status_code == 200
        deal = response.json()
        assert deal["status"] == "negotiation"
        assert deal["client_id"] == "e2e-client-001"
        print(f"Сделка получена, статус: {deal['status']}")

        # Шаг 3: Отметка об оплате
        response = requests.post(
            f"{BASE_URL}/api/deals/{deal_id}/mark-paid",
            json={}
        )
        assert response.status_code == 200
        print(f"Сделка отмечена как оплаченная")

        # Шаг 4: Проверка финального статуса
        response = requests.get(f"{BASE_URL}/api/deals/{deal_id}")
        assert response.status_code == 200
        deal = response.json()
        assert deal["status"] == "paid"
        print(f"Финальный статус: {deal['status']}")

    def test_cancel_deal_before_payment(self):
        # Создание сделки
        create_payload = {
            "client_id": "e2e-client-002",
            "title": "Сделка для отмены",
            "amount": 3000.00,
            "currency": "USD"
        }
        response = requests.post(f"{BASE_URL}/api/deals", json=create_payload)
        assert response.status_code == 201
        deal_id = response.json()["deal_id"]

        # Отмена сделки
        cancel_payload = {"reason": "Клиент передумал"}
        response = requests.post(
            f"{BASE_URL}/api/deals/{deal_id}/cancel",
            json=cancel_payload
        )
        assert response.status_code == 200

        # Проверка статуса
        response = requests.get(f"{BASE_URL}/api/deals/{deal_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
        print(f"Сделка успешно отменена")
