import aiohttp
from coin_price import get_coin_price  # Импортируем функцию для получения цен из CoinGecko

# Публичные API для Cosmos, Injective, Celestia и DYDX
API_URLS = {
    "cosmos": "https://rest.cosmos.directory/cosmoshub",
    "injective": "https://lcd.injective.network",
    "celestia": "https://rest.cosmos.directory/celestia",
    "dydx": "https://rest.cosmos.directory/dydx"
}

# Десятичные знаки для перевода токенов в целые числа
DECIMALS = {
    "cosmos": 1e6,  # ATOM использует 6 знаков после запятой
    "injective": 1e18,  # INJ использует 18 знаков
    "celestia": 1e6,  # TIA использует 6 знаков
    "dydx": 1e18  # DYDX использует 18 знаков
}

# ID токенов для получения цены через CoinGecko API
TOKEN_IDS = {
    "cosmos": "cosmos",
    "injective": "injective-protocol",
    "celestia": "celestia",
    "dydx": "dydx"
}

def escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы для корректного отображения в Telegram MarkdownV2.
    """
    escape_chars = r"_*[]()~`>#+-=|{}.!<>"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


async def get_validator_moniker(validator_address: str, network: str) -> str:
    """
    Получает moniker (имя) валидатора по его адресу для заданной сети.
    """
    if network not in API_URLS:
        return "❌ Неизвестная сеть"

    url = f"{API_URLS[network]}/cosmos/staking/v1beta1/validators/{validator_address}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "❌ Неизвестный валидатор"

            data = await response.json()
            moniker = data.get("validator", {}).get("description", {}).get("moniker")
            return escape_markdown(moniker) if moniker else "❌ Неизвестный валидатор"


async def get_staked_balance(address: str, network: str) -> str:
    """
    Получает застейканные средства и их стоимость в USD для Cosmos, Injective, Celestia и DYDX.
    """
    if network not in API_URLS:
        return "❌ Неизвестная сеть"

    url = f"{API_URLS[network]}/cosmos/staking/v1beta1/delegations/{address}"

    # Получаем цену токена через coin_price.py (ожидается, что `get_coin_price` является асинхронной функцией)
    token_price = get_coin_price(TOKEN_IDS[network], "usd")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return f"❌ Ошибка: Невозможно получить данные для {escape_markdown(network.capitalize())}."

            data = await response.json()
            if "delegation_responses" not in data or not data["delegation_responses"]:
                return f"🔹 У вас нет застейканных средств в {escape_markdown(network.capitalize())}."

            result = f"💰 *Ваши застейканные средства в {escape_markdown(network.capitalize())}:*\n"
            total_value = 0  # Общая стоимость в USD

            for delegation in data["delegation_responses"]:
                amount = int(delegation["balance"]["amount"]) / DECIMALS[network]
                validator_address = delegation["delegation"]["validator_address"]

                # Получаем имя валидатора
                validator_name = await get_validator_moniker(validator_address, network)

                # Экранируем текст
                validator_name = escape_markdown(validator_name)
                validator_address = escape_markdown(validator_address)

                # Рассчитываем стоимость в USD
                value_in_usd = amount * token_price if token_price else 0
                total_value += value_in_usd

                result += (
                    f"🔹 *{amount:.6f} {network.upper()}* у *{validator_name}* "
                    f"(`{validator_address}`) ~ \\${value_in_usd:,.2f}\n"
                )

            result += f"\n💵 *Общая стоимость:* \\${total_value:,.2f}\n"
            return result
