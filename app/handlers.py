from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey

import app.keyboards as kb
import app.database.requests as rq
from config import start_caption, start_photo

router = Router()

class TextState(StatesGroup):
    input_currency = State()
    input_price = State()
    input_description = State()

# Словарь для хранения ID последних сообщений бота для каждого пользователя
user_last_messages = {}

async def delete_old_message(callback, user_id):
    """Удаляет предыдущее сообщение бота для пользователя"""
    if user_id in user_last_messages:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=user_last_messages[user_id]
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")

async def start_writing(state: FSMContext, operation_type: str):
    """Начинает процесс ввода данных"""
    await state.set_state(TextState.input_currency)
    await state.update_data(operation_type=operation_type)

async def cards_menu(user_id, callback, state: FSMContext = None):
    """Показывает меню управления реквизитами"""
    if state:
        await state.clear()
        
    profile_text = f'''💳 Управление реквизитами

🔹 TON: {await rq.get_fiat(user_id, 'TON')}
🔹 BNB: {await rq.get_fiat(user_id, 'BNB')}
🔹 RUB: {await rq.get_fiat(user_id, 'RUB')}
🔹 UAH: {await rq.get_fiat(user_id, 'UAH')}
🔹 USDT: {await rq.get_fiat(user_id, 'USDT')}

⬇️ Выберите действие:'''

    if hasattr(callback, 'message'):
        new_message = await callback.message.answer(text=profile_text, reply_markup=kb.cards)
    else:
        new_message = await callback.answer(text=profile_text, reply_markup=kb.cards)
    
    user_last_messages[user_id] = new_message.message_id

async def add_fiat_offer(callback, state: FSMContext, amount_fiat: str):
    """Создание оффера с выбранной валютой"""
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    
    fiat_data = await rq.get_fiat(user_id, amount_fiat)
    if fiat_data == "-" or not fiat_data:
        profile_text = '''❌ У вас нет реквизита для этой валюты.

Добавьте его с помощью меню "💳Мои реквизиты"'''
        new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
        user_last_messages[user_id] = new_message.message_id
    else:
        await rq.update_user_field(user_id, 'offer_fiat', str(amount_fiat))
        await state.set_state(TextState.input_description)
        await state.update_data(currency=amount_fiat)
        
        profile_text = '''✏️ Отправьте ссылку на ваш подарок или описание сделки 

📝 Это поможет при возникновении разногласий в сделке'''
        new_message = await callback.message.answer(text=profile_text)
        user_last_messages[user_id] = new_message.message_id

async def show_main_menu(callback_or_message, user_id):
    """Показывает главное меню"""
    if hasattr(callback_or_message, 'message'):
        sent_message = await callback_or_message.message.answer_photo(
            photo=start_photo, 
            caption=start_caption, 
            reply_markup=kb.main
        )
    else:
        sent_message = await callback_or_message.answer_photo(
            photo=start_photo, 
            caption=start_caption, 
            reply_markup=kb.main
        )
    
    user_last_messages[user_id] = sent_message.message_id

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    await delete_old_message(message, user_id)
    await rq.set_user(user_id)
    await show_main_menu(message, user_id)

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """📚 Доступные команды:
    
/start - Запустить бота
/help - Получить справку
/profile - Посмотреть профиль
/cards - Управление реквизитами
/support - Связаться с поддержкой"""
    await message.answer(help_text)

@router.message(Command("support"))
async def cmd_support(message: Message):
    """Обработчик команды /support"""
    support_text = """🛡️ Поддержка
    
По всем вопросам обращайтесь:
👉 @Garant_NFT_support
    
Мы работаем 24/7!"""
    await message.answer(support_text)

@router.callback_query(F.data == "start")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки "Назад в главное меню"""
    await state.clear()
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    await show_main_menu(callback, user_id)

@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    """Показывает профиль пользователя"""
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    
    # Получаем количество успешных сделок из БД
    successful_deals = await rq.get_successful_deals(user_id)
    
    profile_text = f'''👤 Твой профиль

🆔 ID: {callback.from_user.id}
📛 Имя: {callback.from_user.first_name}
💼 Успешных сделок: {successful_deals}'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "cards")
async def cards_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки "Мои реквизиты" """
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    await cards_menu(user_id, callback, state)

@router.callback_query(F.data == "add_cards")
async def add_cards(callback: CallbackQuery):
    """Показывает меню добавления реквизитов"""
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)

    profile_text = '''💳 Добавление реквизита

Выберите валюту для добавления/обновления реквизита:'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.add_fiat)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "defolt_cards")
async def defolt_cards(callback: CallbackQuery):
    """Показывает меню удаления реквизитов"""
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)

    profile_text = '''🗑 Удаление реквизита

Выберите валюту для удаления реквизита:'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.defolt_fiat)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "delete_cards")
async def delete_cards(callback: CallbackQuery):
    """Удаляет все реквизиты"""
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    await rq.delete_user_field(user_id)
    await callback.answer("✅ Все реквизиты удалены")
    await cards_menu(user_id, callback)

# Обработчики добавления реквизитов
@router.callback_query(F.data.startswith("add_"))
async def add_fiat_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик добавления реквизитов"""
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    
    fiat_type = callback.data.split("_")[1]  # Получаем TON, BNB и т.д.
    
    messages = {
        "TON": '''💎 Добавление TON кошелька

Введите адрес TON (начинается с UQ):

Пример: UQDQ8DxVu_Example_QUkuOLaGnKOrPtPX9p3SH8Mje-

⚠️ Внимание! При указании неверного адреса, вы потеряете средства''',
        
        "BNB": '''💎 Добавление BNB кошелька

Введите адрес BNB (20–60 символов):

Пример: bnb1qexampleaddress12345

⚠️ Внимание! При указании неверного адреса, вы потеряете средства''',
        
        "RUB": '''💳 Добавление карты RUB

Введите номер карты (16–19 цифр, только цифры без пробелов):

Пример: 1234567812345678

⚠️ Внимание! При указании неверного адреса, вы потеряете средства''',
        
        "UAH": '''💳 Добавление карты UAH

Введите номер карты (16–19 цифр, только цифры без пробелов):

Пример: 1234567812345678

⚠️ Внимание! При указании неверного адреса, вы потеряете средства''',
        
        "USDT": '''💎 Добавление USDT кошелька

Введите адрес USDT (20–60 символов):

Пример: TExampleAddress123456789

⚠️ Внимание! При указании неверного адреса, вы потеряете средства'''
    }
    
    profile_text = messages.get(fiat_type, "Выберите валюту")
    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id
    
    await state.set_state(TextState.input_currency)
    await state.update_data(operation_type=f"add_{fiat_type.lower()}", fiat_type=fiat_type)

@router.message(TextState.input_currency)
async def save_currency_amount(message: Message, state: FSMContext):
    """Сохраняет введенный реквизит"""
    user_id = message.from_user.id
    await delete_old_message(message, user_id)
    
    user_data = await state.get_data()
    operation_type = user_data.get('operation_type')
    fiat_type = user_data.get('fiat_type', '').upper()
    amount = message.text.strip()
    
    # Простая валидация
    if not amount:
        await message.answer("❌ Пустое значение не допускается")
        return
    
    if operation_type.startswith("add_"):
        # Сохраняем реквизит
        await rq.update_user_field(user_id, fiat_type, amount)
        await message.answer(f"✅ Реквизит {fiat_type} добавлен/обновлен")
        await cards_menu(user_id, message, state)
    
    await state.clear()

# Обработчики удаления реквизитов
@router.callback_query(F.data.startswith("defolt_"))
async def defolt_fiat_handler(callback: CallbackQuery):
    """Обработчик удаления реквизитов"""
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    
    fiat_type = callback.data.split("_")[1]  # Получаем TON, BNB и т.д.
    await rq.defolt_user_field(user_id, fiat_type)
    await callback.answer(f"✅ Реквизит {fiat_type} удален")
    await cards_menu(user_id, callback)

@router.callback_query(F.data == "create_offer")
async def create_offer(callback: CallbackQuery, state: FSMContext):
    """Начинает создание сделки"""
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)

    profile_text = '''🤝 Создание сделки

Выберите реквизиты, куда поступят средства после завершения сделки:'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.offer_fiat)
    user_last_messages[user_id] = new_message.message_id

# Обработчики выбора валюты для оффера
@router.callback_query(F.data.startswith("offer_"))
async def offer_fiat_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора валюты для сделки"""
    fiat_type = callback.data.split("_")[1]  # Получаем TON, BNB и т.д.
    await add_fiat_offer(callback, state, fiat_type)

@router.message(TextState.input_description)
async def save_description(message: Message, state: FSMContext):
    """Сохраняет описание сделки"""
    user_id = message.from_user.id
    await delete_old_message(message, user_id)
    
    description = message.text.strip()
    user_data = await state.get_data()
    currency = user_data.get('currency')
    
    await rq.update_user_field(user_id, 'discripton_fiat', description)
    await state.set_state(TextState.input_price)
    
    profile_text = '''💵 Введите сумму сделки в USD:

Пример: 100.50'''
    new_message = await message.answer(text=profile_text)
    user_last_messages[user_id] = new_message.message_id

@router.message(TextState.input_price)
async def save_price(message: Message, state: FSMContext):
    """Сохраняет сумму сделки и создает оффер"""
    user_id = message.from_user.id
    await delete_old_message(message, user_id)
    
    try:
        price = float(message.text.strip())
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму (например: 100.50)")
        return
    
    user_data = await state.get_data()
    currency = user_data.get('currency')
    description = await rq.get_fiat(user_id, 'discripton_fiat')
    
    # Сохраняем сумму
    await rq.update_user_field(user_id, 'sum_fiat', str(price))
    
    # Создаем оффер
    offer_id = await rq.create_offer(user_id, currency, price, description)
    
    offer_text = f'''✅ Сделка создана!

📋 ID сделки: {offer_id}
💎 Валюта: {currency}
💰 Сумма: {price} USD
📝 Описание: {description if description else "Не указано"}

🔗 Ссылка на сделку: t.me/your_bot?start=offer_{offer_id}
    
📢 Поделитесь этой ссылкой с покупателем'''
    
    new_message = await message.answer(text=offer_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id
    
    await state.clear()

@router.message()
async def unknown_message(message: Message):
    """Обработчик неизвестных сообщений"""
    await message.answer("❓ Я не понимаю эту команду. Используйте /help для просмотра доступных команд")