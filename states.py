from aiogram.fsm.state import State, StatesGroup


class AddressState(StatesGroup):
    """Состояния FSM для работы с адресами"""
    waiting_for_address = State()  # Ожидание ввода адреса
    receive_address_type = State()
