import aiohttp

INJECTIVE_API_URL = "https://lcd.injective.network"

async def get_injective_staked_balance(address: str) -> str:
    """
    Получает застейканные средства для Injective (INJ).
    """
    url = f"{INJECTIVE_API_URL}/cosmos/staking/v1beta1/delegations/{address}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "❌ Ошибка: Невозможно получить данные. Проверьте адрес."

            data = await response.json()

            if "delegation_responses" not in data or not data["delegation_responses"]:
                return "🔹 У вас нет застейканных средств."

            result = "💰 **Ваши застейканные средства в Injective:**\n"

            for delegation in data["delegation_responses"]:
                amount = int(delegation["balance"]["amount"]) / 1e18  # INJ использует 18 десятичных знаков
                validator_address = delegation["delegation"]["validator_address"]

                result += f"🔹 **{amount:.6f} INJ** у валидатора `{validator_address}`\n"

            return result
