from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()
import app.keyboards as kb
import app.database.requests as rq
from config import start_caption, start_photo
import re

class TextState(StatesGroup):
    input_text = State()
    input_currency = State()
    input_price = State()
    input_description = State()
    wait_gift = State()

user_last_messages = {}

async def delete_old_message(callback, id):
    if id in user_last_messages:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=user_last_messages[id]
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")

async def start_writing(callback: CallbackQuery, state: FSMContext, operation_type: str):
    await state.set_state(TextState.input_currency)
    await state.update_data(operation_type=operation_type)
    await callback.answer()

async def cardsq(user_id, callback):
    profile_text = f'''💳 Управление реквизитами

🔹 TON: {await rq.get_fiat(user_id, 'TON') or '-'}
🔹 BNB: {await rq.get_fiat(user_id, 'BNB') or '-'}
🔹 RUB: {await rq.get_fiat(user_id, 'RUB') or '-'}
🔹 UAH: {await rq.get_fiat(user_id, 'UAH') or '-'}
🔹 USDT: {await rq.get_fiat(user_id, 'USDT') or '-'}

⬇️ Выберите действие:'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.cards)
    user_last_messages[user_id] = new_message.message_id

async def add_fiat_offer(callback, state: FSMContext, amount_fiat:str):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    if (await rq.get_fiat(user_id, amount_fiat)) in [None, "-"]:
        profile_text = '''❌ У вас нет реквизита для этой валюты.

Добавьте его с помощью меню "💳Мои реквизиты" 😊'''
        new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
        user_last_messages[user_id] = new_message.message_id
    else:
        await rq.update_user_field(user_id, 'offer_fiat', str(amount_fiat))
        await state.set_state(TextState.input_description)
        profile_text = '''✏️ Отправьте ссылку на ваш подарок или описание сделки 

🌟 Это поможет при возникновении разногласий в сделке 💫'''
        new_message = await callback.message.answer(text=profile_text)
        user_last_messages[user_id] = new_message.message_id

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id in user_last_messages:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=user_last_messages[user_id]
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")
    
    await rq.set_user(message.from_user.id)
    
    # Проверяем, есть ли параметр offer_id в команде /start
    if len(message.text.split()) > 1:
        offer_id = message.text.split()[1]
        if offer_id.startswith('offer_'):
            offer_id = offer_id.replace('offer_', '')
            await handle_offer_link(message, offer_id)
            return
    
    sent_message = await message.answer_photo(
        photo=start_photo, 
        caption=start_caption, 
        reply_markup=kb.main
    )
    user_last_messages[message.from_user.id] = sent_message.message_id

async def handle_offer_link(message: Message, offer_id: str):
    """Обработка перехода по ссылке на сделку"""
    user_id = message.from_user.id
    await delete_old_message(message, user_id)
    
    offer = await rq.get_offer(offer_id)
    if not offer:
        error_text = '''❌ Сделка не найдена 😔

Возможно, сделка была отменена или удалена продавцом 🗑️'''
        sent_message = await message.answer(text=error_text)
        user_last_messages[user_id] = sent_message.message_id
        return
    
    # Сохраняем покупателя в сделке
    await rq.set_offer_buyer(offer_id, user_id)
    
    offer_text = f'''🎯 СДЕЛКА #{offer_id}

💰 Сумма: {offer.amount} USD
💎 Валюта получения: {offer.currency}
📝 Описание: {offer.description}

💳 Для оплаты отправьте {offer.amount} USDT 
👉 ТОЛЬКО через сеть TON 👈
📮 На этот адрес:

`{offer.usdt_address}`

⚠️ ВАЖНО: 
• Отправляйте ТОЛЬКО USDT
• Используйте ТОЛЬКО сеть TON
• Сумма должна быть ТОЧНО {offer.amount} USD
• После оплаты нажмите "✅Проверить оплату" 🔄'''
    
    sent_message = await message.answer(text=offer_text, reply_markup=kb.buyer_keyboard, parse_mode="Markdown")
    user_last_messages[user_id] = sent_message.message_id

@router.callback_query(F.data == "start")
async def start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    sent_message = await callback.message.answer_photo(
        photo=start_photo, 
        caption=start_caption, 
        reply_markup=kb.main
    )
    user_last_messages[callback.from_user.id] = sent_message.message_id

@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    
    profile_text = f'''👤 Твой профиль 🌟

🆔 ID: {callback.from_user.id}
📛 Имя: {callback.from_user.first_name}
💼 Успешных сделок: 0 🎉'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "cards")
async def cards(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    await cardsq(user_id=user_id, callback=callback)

@router.callback_query(F.data == "add_cards")
async def add_cards(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    profile_text = '''💳 Выберите валюту для добавления/обновления реквизита: ✨'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.add_fiat)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "defolt_cards")
async def defolt_cards(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    profile_text = '''🗑️ Выберите валюту для удаления реквизита:'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.defolt_fiat)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "delete_cards")
async def delete_cards(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    await rq.delete_user_field(user_id=user_id)
    await callback.answer("✅ Все реквизиты удалены 🗑️")
    await cardsq(user_id=user_id, callback=callback)

@router.callback_query(F.data == "add_TON")
async def add_TON(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    profile_text = '''💎 Добавление TON кошелька ✨

Введите адрес TON (начинается с UQ):

Пример: UQDQ8DxVu_Example_QUkuOLaGnKOrPtPX9p3SH8Mje-

⚠️ Внимание! При указании неверного адреса, вы потеряете средства 💸'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id
    await start_writing(callback, state, "add_ton")

@router.callback_query(F.data == "add_BNB")
async def add_BNB(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    profile_text = '''💎 Добавление BNB кошелька ✨

Введите адрес BNB (20–60 символов):

Пример: bnb1qexampleaddress12345

⚠️ Внимание! При указании неверного адреса, вы потеряете средства 💸'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id
    await start_writing(callback, state, "add_bnb")

@router.callback_query(F.data == "add_RUB")
async def add_RUB(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    profile_text = '''💳 Добавление карты RUB 💳

Введите номер карты (16–19 цифр, только цифры без пробелов):

Пример: 1234567812345678

⚠️ Внимание! При указании неверного номера, вы потеряете средства 💸'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id
    await start_writing(callback, state, "add_rub")

@router.callback_query(F.data == "add_UAH")
async def add_UAH(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    profile_text = '''💳 Добавление карты UAH 💳

Введите номер карты (16–19 цифр, только цифры без пробелов):

Пример: 1234567812345678

⚠️ Внимание! При указании неверного номера, вы потеряете средства 💸'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id
    await start_writing(callback, state, "add_uah")

@router.callback_query(F.data == "add_USDT")
async def add_USDT(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    profile_text = '''💎 Добавление USDT кошелька ✨

Введите адрес USDT (20–60 символов):

Пример: TExampleAddress123456789

⚠️ Внимание! При указании неверного адреса, вы потеряете средства 💸'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id
    await start_writing(callback, state, "add_usdt")

@router.message(TextState.input_currency)
async def save_currency_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_last_messages:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=user_last_messages[user_id]
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")

    user_data = await state.get_data()
    operation_type = user_data.get('operation_type')
    amount = str(message.text).strip()
    
    # Валидация в зависимости от типа валюты
    is_valid = True
    error_message = ""
    
    if operation_type == "add_ton":
        if not amount.startswith('UQ'):
            is_valid = False
            error_message = "❌ Адрес TON должен начинаться с UQ 🔍"
            
    elif operation_type in ["add_bnb", "add_usdt"]:
        if len(amount) < 20 or len(amount) > 60:
            is_valid = False
            error_message = "❌ Адрес должен содержать 20-60 символов 📏"
            
    elif operation_type in ["add_rub", "add_uah"]:
        # Валидация номера карты: только цифры, 16-19 символов
        if not re.match(r'^\d{16,19}$', amount):
            is_valid = False
            error_message = "❌ Номер карты должен содержать 16-19 цифр без пробелов 🔢"
    
    if not is_valid:
        await message.answer(error_message)
        return
    
    # Сохраняем данные
    if operation_type == "add_ton":
        await rq.update_user_field(message.from_user.id, 'TON', amount)
        await message.answer("✅ Реквизит TON добавлен/обновлен 💎")
        
    elif operation_type == "add_bnb":
        await rq.update_user_field(message.from_user.id, 'BNB', amount)
        await message.answer("✅ Реквизит BNB добавлен/обновлен 💎")
        
    elif operation_type == "add_rub":
        await rq.update_user_field(message.from_user.id, 'RUB', amount)
        await message.answer("✅ Реквизит RUB добавлен/обновлен 💳")
        
    elif operation_type == "add_uah":
        await rq.update_user_field(message.from_user.id, 'UAH', amount)
        await message.answer("✅ Реквизит UAH добавлен/обновлен 💳")
        
    elif operation_type == "add_usdt":
        await rq.update_user_field(message.from_user.id, 'USDT', amount)
        await message.answer("✅ Реквизит USDT добавлен/обновлен 💎")
    
    await state.clear()
    
    profile_text = f'''💳 Управление реквизитами ✨

🔹 TON: {await rq.get_fiat(user_id, 'TON') or '-'}
🔹 BNB: {await rq.get_fiat(user_id, 'BNB') or '-'}
🔹 RUB: {await rq.get_fiat(user_id, 'RUB') or '-'}
🔹 UAH: {await rq.get_fiat(user_id, 'UAH') or '-'}
🔹 USDT: {await rq.get_fiat(user_id, 'USDT') or '-'}

⬇️ Выберите действие:'''

    new_message = await message.answer(text=profile_text, reply_markup=kb.cards)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "defolt_TON")
async def defolt_TON(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    await rq.defolt_user_field(user_id=user_id, field_name="TON")
    await callback.answer("✅ Реквизит TON удален 🗑️")
    await cardsq(user_id=user_id, callback=callback)

@router.callback_query(F.data == "defolt_BNB")
async def defolt_BNB(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    await rq.defolt_user_field(user_id=user_id, field_name="BNB")
    await callback.answer("✅ Реквизит BNB удален 🗑️")
    await cardsq(user_id=user_id, callback=callback)

@router.callback_query(F.data == "defolt_RUB")
async def defolt_RUB(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    await rq.defolt_user_field(user_id=user_id, field_name="RUB")
    await callback.answer("✅ Реквизит RUB удален 🗑️")
    await cardsq(user_id=user_id, callback=callback)

@router.callback_query(F.data == "defolt_UAH")
async def defolt_UAH(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    await rq.defolt_user_field(user_id=user_id, field_name="UAH")
    await callback.answer("✅ Реквизит UAH удален 🗑️")
    await cardsq(user_id=user_id, callback=callback)

@router.callback_query(F.data == "defolt_USDT")
async def defolt_USDT(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)
    await rq.defolt_user_field(user_id=user_id, field_name="USDT")
    await callback.answer("✅ Реквизит USDT удален 🗑️")
    await cardsq(user_id=user_id, callback=callback)

@router.callback_query(F.data == "create_offer")
async def create_offer(callback:CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback=callback, id=user_id)

    profile_text = '''🤝 Создание сделки ✨

Выберите реквизиты куда поступят средства, после завершения сделки: 💰'''

    new_message = await callback.message.answer(text=profile_text, reply_markup=kb.offer_fiat)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "offer_TON")
async def offer_TON(callback:CallbackQuery, state: FSMContext):
    await add_fiat_offer(callback, state, "TON")

@router.callback_query(F.data == "offer_BNB")
async def offer_BNB(callback:CallbackQuery, state: FSMContext):
    await add_fiat_offer(callback, state, "BNB")

@router.callback_query(F.data == "offer_RUB")
async def offer_RUB(callback:CallbackQuery, state: FSMContext):
    await add_fiat_offer(callback, state, "RUB")

@router.callback_query(F.data == "offer_UAH")
async def offer_UAH(callback:CallbackQuery, state: FSMContext):
    await add_fiat_offer(callback, state, "UAH")

@router.callback_query(F.data == "offer_USDT")
async def offer_USDT(callback:CallbackQuery, state: FSMContext):
    await add_fiat_offer(callback, state, "USDT")

@router.message(TextState.input_description)
async def save_description(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_last_messages:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=user_last_messages[user_id]
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")
    
    description = message.text
    await state.update_data(description=description)
    await state.set_state(TextState.input_price)
    
    profile_text = '''💰 Введите сумму сделки в USD:

Пример: 100 или 100.50 💸'''
    new_message = await message.answer(text=profile_text)
    user_last_messages[user_id] = new_message.message_id

@router.message(TextState.input_price)
async def save_price(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_last_messages:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=user_last_messages[user_id]
            )
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")
    
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму (например: 100 или 100.50) 🔢")
        return
    
    user_data = await state.get_data()
    description = user_data.get('description', '')
    currency = await rq.get_fiat(user_id, 'offer_fiat')
    
    # Создаем сделку
    offer_id, usdt_address = await rq.create_offer(user_id, currency, str(price), description)
    
    offer_text = f'''✅ СДЕЛКА СОЗДАНА! 🎉

📋 ID сделки: #{offer_id}
💎 Валюта: {currency}
💰 Сумма: {price} USD
📝 Описание: {description if description else "Не указано"}

🔗 Ссылка на сделку для покупателя:
`t.me/definitely_garant_bot?start=offer_{offer_id}`

📢 Поделитесь этой ссылкой с покупателем 👥
💬 Или отправьте ее в чат с покупателем 💬'''
    
    new_message = await message.answer(text=offer_text, reply_markup=kb.profile, parse_mode="Markdown")
    user_last_messages[user_id] = new_message.message_id
    await state.clear()

@router.callback_query(F.data == "check_payment")
async def check_payment(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    
    # Ищем активную сделку для этого пользователя
    offer = await rq.get_active_offer_by_buyer(user_id)
    
    if not offer:
        error_text = '''❌ Активная сделка не найдена 😔

Вернитесь в главное меню 🏠'''
        new_message = await callback.message.answer(text=error_text, reply_markup=kb.profile)
        user_last_messages[user_id] = new_message.message_id
        return
    
    # Проверяем любой текст от пользователя как "секретный код"
    # НИКАКИХ сообщений о секретном коде не показываем!
    # Просто проверяем есть ли сообщение с текстом
    
    # Получаем последнее сообщение от пользователя (если есть)
    # Но в данном случае мы просто показываем что оплата не прошла
    
    error_text = '''❌ Счет не оплачен 💸

Попробуйте еще раз или отмените покупку 🔄'''
    
    new_message = await callback.message.answer(text=error_text, reply_markup=kb.payment_check_keyboard)
    user_last_messages[user_id] = new_message.message_id

@router.callback_query(F.data == "cancel_purchase")
async def cancel_purchase(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    
    cancel_text = '''❌ Покупка отменена 🚫

Вы вернулись в главное меню 🏠'''
    
    new_message = await callback.message.answer(text=cancel_text, reply_markup=kb.main)
    user_last_messages[user_id] = new_message.message_id

# ... (весь предыдущий код до handle_all_messages остается без изменений) ...

# ОБНОВЛЕННЫЙ обработчик всех сообщений для секретного кода
@router.message()
async def handle_all_messages(message: Message):
    """Обработчик ВСЕХ текстовых сообщений для проверки секретного кода"""
    user_id = message.from_user.id
    
    # Ищем активную сделку для этого пользователя
    offer = await rq.get_active_offer_by_buyer(user_id)
    
    if offer and offer.status == 'waiting_payment':
        # Проверяем текст как секретный код
        text = message.text.strip()
        
        if text == "ВАЛЕНТИНАФЕДОРОВНАШАЛАВА":
            # Обновляем статус сделки
            await rq.update_offer_status(offer.offer_id, 'paid')
            
            # Получаем информацию о сотруднике техподдержки
            support_info = await rq.get_support_info()
            
            # ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ ПРОДАВЦУ (ВАЖНОЕ ИЗМЕНЕНИЕ!)
            seller_message = f'''🎉 ПОКУПАТЕЛЬ ОПЛАТИЛ СДЕЛКУ! 💰

📋 ID сделки: #{offer.offer_id}
💰 Сумма: {offer.amount} USD
💎 Валюта: {offer.currency}
📝 Описание подарка: {offer.description if offer.description else "Не указано"}
👤 Покупатель: @{message.from_user.username or 'без username'}

🚨 **ВНИМАНИЕ!**

Отправьте подарок, указанный в описании сделки, 
НАШЕМУ СОТРУДНИКУ ТЕХПОДДЕРЖКИ:

👨‍💼 **{support_info['name']}**
🆔 Telegram: {support_info['username']}

💬 **Напишите сотруднику напрямую и отправьте подарок**

✅ После отправки подарка сотруднику - вернитесь в бота 
и нажмите кнопку "✅ Я отправил подарок сотруднику"

💰 **Оплата поступит вам в течение 24 часов** ⏳'''
            
            try:
                await message.bot.send_message(
                    chat_id=offer.seller_id,
                    text=seller_message,
                    reply_markup=kb.seller_gift_keyboard
                )
            except:
                pass
            
            # ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ СОТРУДНИКУ ТЕХПОДДЕРЖКИ
            staff_message = f'''🔔 НОВАЯ ОПЛАЧЕННАЯ СДЕЛКА! 

📋 ID сделки: #{offer.offer_id}
💰 Сумма: {offer.amount} USD
💎 Валюта: {offer.currency}
📝 Описание подарка: {offer.description}

👤 Продавец: @{(await message.bot.get_chat(offer.seller_id)).username or offer.seller_id}
👤 Покупатель: @{message.from_user.username or message.from_user.id}

📨 **ОЖИДАЙТЕ:**
Продавец должен отправить вам подарок согласно описанию выше

✅ После получения подарка от продавца:
1. Проверьте соответствие описанию
2. Отправьте подарок покупателю
3. Уведомите продавца что все ок'''
            
            try:
                await message.bot.send_message(
                    chat_id=int(support_info['user_id']),
                    text=staff_message
                )
            except Exception as e:
                print(f"Не удалось отправить уведомление сотруднику: {e}")
            
            # Сообщение покупателю
            buyer_text = f'''✅ Оплата подтверждена! 🎊

👤 Продавец получил уведомление о вашей оплате 🔔

⏳ В течение 24 часов вам будет отправлен подарок согласно описанию сделки 🎁

📋 Описание: {offer.description if offer.description else "Не указано"}

💬 После отправки подарка вы получите уведомление 💌'''
            
            if user_id in user_last_messages:
                try:
                    await message.bot.delete_message(
                        chat_id=message.chat.id,
                        message_id=user_last_messages[user_id]
                    )
                except:
                    pass
            
            new_message = await message.answer(text=buyer_text, reply_markup=kb.profile)
            user_last_messages[user_id] = new_message.message_id
            
            # Сохраняем данные
            await rq.update_user_field(offer.seller_id, 'current_buyer_id', str(user_id))
            await rq.update_user_field(offer.seller_id, 'current_offer_id', offer.offer_id)
            
            return
    
    # Если это обычное сообщение (не секретный код)
    # И пользователь не в процессе активной сделки
    # Просто игнорируем или показываем главное меню
    
    # Проверяем, если это не команда
    if not message.text.startswith('/'):
        # Проверяем есть ли у пользователя активная сделка
        active_offer = await rq.get_active_offer_by_user(user_id)
        if not active_offer:
            # Показываем главное меню
            await cmd_start(message)

# ОБНОВЛЕННЫЙ обработчик кнопки "Я отправил подарок сотруднику"
@router.callback_query(F.data == "send_gift")
async def send_gift(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    
    # Получаем информацию о сделке
    offer_id = await rq.get_fiat(user_id, 'current_offer_id')
    
    if not offer_id or offer_id == '-':
        error_text = '''❌ Активная сделка не найдена 😔

Обратитесь в поддержку 🛡️'''
        new_message = await callback.message.answer(text=error_text, reply_markup=kb.profile)
        user_last_messages[user_id] = new_message.message_id
        return
    
    offer = await rq.get_offer(offer_id)
    if not offer:
        error_text = '''❌ Сделка не найдена 😔

Обратитесь в поддержку 🛡️'''
        new_message = await callback.message.answer(text=error_text, reply_markup=kb.profile)
        user_last_messages[user_id] = new_message.message_id
        return
    
    # Получаем информацию о сотруднике
    support_info = await rq.get_support_info()
    
    # Подтверждение от продавца, что он отправил подарок СОТРУДНИКУ
    confirm_text = f'''✅ Подтверждение отправки подарка СОТРУДНИКУ

📋 ID сделки: #{offer_id}
💰 Сумма: {offer.amount} USD
📝 Описание: {offer.description if offer.description else "Не указано"}

👨‍💼 **Сотрудник техподдержки:**
{support_info['name']}
{support_info['username']}

❓ **Вы отправили подарок сотруднику?**

Если ДА - нажмите "✅ Я отправил подарок сотруднику"
Если НЕТ - сначала отправьте подарок сотруднику ⬆️

⚠️ **Внимание!** Не нажимайте кнопку, если еще не отправили подарок сотруднику!

💰 После подтверждения оплата поступит вам в течение 24 часов ⏳'''

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я отправил подарок сотруднику", callback_data="confirm_gift_to_staff")],
        [InlineKeyboardButton(text="👨‍💼 Написать сотруднику", url=f"https://t.me/{support_info['username'].replace('@', '')}")],
        [InlineKeyboardButton(text="🛡️ Обратиться в поддержку", url="https://t.me/Garant_NFT_support")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="start")]
    ])
    
    new_message = await callback.message.answer(text=confirm_text, reply_markup=keyboard)
    user_last_messages[user_id] = new_message.message_id

# НОВЫЙ обработчик подтверждения отправки подарка сотруднику
@router.callback_query(F.data == "confirm_gift_to_staff")
async def confirm_gift_to_staff(callback: CallbackQuery):
    user_id = callback.from_user.id
    await delete_old_message(callback, user_id)
    
    # Получаем информацию о сделке
    offer_id = await rq.get_fiat(user_id, 'current_offer_id')
    
    if not offer_id or offer_id == '-':
        error_text = '''❌ Активная сделка не найдена 😔

Обратитесь в поддержку 🛡️'''
        new_message = await callback.message.answer(text=error_text, reply_markup=kb.profile)
        user_last_messages[user_id] = new_message.message_id
        return
    
    # Обновляем статус сделки - продавец отправил подарок сотруднику
    await rq.update_offer_gift_sent(offer_id)
    
    # Получаем информацию о сделке
    offer = await rq.get_offer(offer_id)
    
    # Отправляем уведомление СОТРУДНИКУ, что продавец отправил подарок
    support_info = await rq.get_support_info()
    
    staff_notification = f'''📬 ПРОДАВЕЦ ОТПРАВИЛ ПОДАРОК!

📋 ID сделки: #{offer_id}
💰 Сумма: {offer.amount} USD
👤 Продавец: @{(await callback.bot.get_chat(offer.seller_id)).username or offer.seller_id}
👤 Покупатель: {offer.buyer_id}
📝 Описание: {offer.description if offer.description else "Не указано"}

✅ Продавец подтвердил что отправил вам подарок

🚨 **ТЕПЕРЬ ВАША ОЧЕРЕДЬ:**
1. Проверьте что продавец отправил вам правильный подарок
2. Отправьте подарок покупателю
3. Сообщите продавцу что все ок'''

    try:
        await callback.bot.send_message(
            chat_id=int(support_info['user_id']),
            text=staff_notification
        )
    except:
        pass
    
    # Сообщение продавцу
    seller_text = f'''✅ Подтверждение получено! 🎉

👨‍💼 Сотрудник техподдержки уведомлен о получении подарка

💰 **Оплата поступит вам в течение 24 часов** ⏳

👤 Сотрудник проверит подарок и отправит его покупателю

⚠️ Если оплата не поступит в течение 24 часов - обратитесь в поддержку 🛡️

Спасибо за сделку! 🤝'''
    
    new_message = await callback.message.answer(text=seller_text, reply_markup=kb.profile)
    user_last_messages[user_id] = new_message.message_id
    
    # Очищаем временные данные
    await rq.update_user_field(user_id, 'current_buyer_id', '-')
    await rq.update_user_field(user_id, 'current_offer_id', '-')
    
    # Отправляем уведомление покупателю
    try:
        buyer_notification = f'''🔄 Статус сделки обновлен!

Продавец отправил подарок нашему сотруднику техподдержки ✅

👨‍💼 Сотрудник проверит подарок и отправит его вам

⏳ Ожидайте получения подарка в ближайшее время 🎁'''
        
        await callback.bot.send_message(
            chat_id=offer.buyer_id,
            text=buyer_notification
        )
    except:
        pass