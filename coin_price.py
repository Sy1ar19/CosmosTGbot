import requests
import os
from config import COINGECKO_API_URL


def get_coin_price(coin_id, currency="usd"):
    """
    Получает цену монеты в указанной валюте (по умолчанию USD).

    :param coin_id: Уникальный идентификатор монеты (например, "cosmos" для ATOM)
    :param currency: Валюта для конверсии (например, "usd")
    :return: Цена монеты в указанной валюте или None, если запрос не удался
    """
    coingecko_base_url = COINGECKO_API_URL
    endpoint = f"{coingecko_base_url}/simple/price"
    params = {
        "ids": coin_id,  # Уникальный ID монеты в CoinGecko
        "vs_currencies": currency  # Валюта для конверсии
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Вызывает исключение, если запрос завершился ошибкой
        price_data = response.json()

        price = price_data.get(coin_id, {}).get(currency)
        if price is None:
            print(f"Цена для монеты '{coin_id}' в валюте '{currency}' не найдена.")
        return price
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подключении к CoinGecko API: {e}")
        return None


if __name__ == "__main__":
    # Список монет для получения цен
    coins = {
        "ATOM": "cosmos",            # Cosmos Hub
        "TIA": "celestia",           # Celestia
        "DYDX": "dydx",              # DYDX
        "INJ": "injective-protocol"  # Injective
    }
    currency = "usd"  # Валюта для конверсии

    for coin_name, coin_id in coins.items():
        price = get_coin_price(coin_id, currency)
        if price is not None:
            print(f"Цена {coin_name} ({coin_id.upper()}) в {currency.upper()}: {price}")
        else:
            print(f"Не удалось получить цену для {coin_name} ({coin_id}).")
