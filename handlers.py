from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.enums import ParseMode
from database import save_address, get_address
from staking_api import get_staked_balance, escape_markdown
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from states import AddressState

async def command_start_handler(message: Message) -> None:
    """Обработчик команды /start"""
    await message.answer(
        escape_markdown(f"Привет, {message.from_user.full_name}! 👋\n"
                        "Отправьте команду /add_address, чтобы добавить свой адрес.\n"
                        "А затем используйте /my_stake, чтобы посмотреть, сколько у вас застейкано.")
    )

async def ask_for_address(message: Message, state: FSMContext) -> None:
    """Запрос выбора типа адреса"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Cosmos"), KeyboardButton(text="Injective")],
            [KeyboardButton(text="Celestia"), KeyboardButton(text="DYDX")]
        ],
        resize_keyboard=True
    )
    await message.answer("Какой адрес хотите ввести? Выберите:", reply_markup=keyboard)
    await state.set_state(AddressState.receive_address_type)

async def receive_address_type(message: Message, state: FSMContext) -> None:
    """Обрабатывает выбор типа адреса"""
    address_type = message.text.lower()

    if address_type not in ["cosmos", "injective", "celestia", "dydx"]:
        await message.answer(escape_markdown("❌ Выберите 'Cosmos', 'Injective', 'Celestia' или 'DYDX'. Попробуйте снова."))
        return

    await state.update_data(address_type=address_type)
    await message.answer(escape_markdown(f"Введите ваш {address_type.capitalize()}-адрес: 🔗"), reply_markup=None)
    await state.set_state(AddressState.waiting_for_address)

async def receive_address(message: Message, state: FSMContext) -> None:
    """Сохраняет введённый адрес"""
    user_data = await state.get_data()
    address_type = user_data.get("address_type", "cosmos")  # По умолчанию - cosmos
    address = message.text.strip()

    # Проверка формата адреса
    if address_type == "cosmos" and not address.startswith("cosmos1"):
        await message.answer(escape_markdown("❌ Неверный формат! Cosmos-адрес должен начинаться с 'cosmos1'. Попробуйте снова."))
        return
    if address_type == "injective" and not address.startswith("inj1"):
        await message.answer(escape_markdown("❌ Неверный формат! Injective-адрес должен начинаться с 'inj1'. Попробуйте снова."))
        return
    if address_type == "celestia" and not address.startswith("celestia1"):
        await message.answer(escape_markdown("❌ Неверный формат! Celestia-адрес должен начинаться с 'celestia1'. Попробуйте снова."))
        return
    if address_type == "dydx" and not address.startswith("dydx1"):
        await message.answer(escape_markdown("❌ Неверный формат! DYDX-адрес должен начинаться с 'dydx1'. Попробуйте снова."))
        return

    save_address(message.from_user.id, address, address_type)  # 🔹 Теперь передаём `address_type`
    print(f"✅ {address_type.capitalize()}-адрес сохранён для {message.from_user.id}: {address}")

    await message.answer(escape_markdown(f"✅ Ваш {address_type.capitalize()}-адрес сохранён!"), parse_mode=ParseMode.MARKDOWN_V2)
    await state.clear()

async def my_stake(message: Message) -> None:
    """Показываем застейканные средства пользователя (Cosmos + Injective + Celestia + DYDX)"""
    networks = {
        "cosmos": "🌌 Cosmos (ATOM)",
        "injective": "🚀 Injective (INJ)",
        "celestia": "🌞 Celestia (TIA)",
        "dydx": "📈 DYDX"
    }

    response = "📊 *Ваши застейканные активы:*\n\n"
    has_stake = False  # Проверяем, есть ли вообще застейканные монеты

    for network, label in networks.items():
        address = get_address(message.from_user.id, network)
        if address:
            staking_info = await get_staked_balance(address, network)
            response += escape_markdown(f"{label}\n{staking_info}\n\n")
            has_stake = True
        else:
            response += escape_markdown(f"❌ Вы ещё не вводили {label}-адрес. Используйте /add_address, чтобы ввести его.\n\n")

    if not has_stake:
        response = escape_markdown("❌ У вас ещё нет застейканных активов. Используйте /add_address, чтобы добавить адрес.")

    await message.answer(response.strip(), parse_mode=ParseMode.MARKDOWN_V2)

def register_handlers(dp: Dispatcher):
    """Регистрирует обработчики команд"""
    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(ask_for_address, Command("add_address"))
    dp.message.register(receive_address_type, AddressState.receive_address_type)
    dp.message.register(receive_address, AddressState.waiting_for_address)
    dp.message.register(my_stake, Command("my_stake"))
