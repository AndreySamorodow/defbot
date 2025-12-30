from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✨Создать сделку", callback_data="create_offer")],
    [InlineKeyboardButton(text="👤Мой профиль", callback_data="profile"),
      InlineKeyboardButton(text="🛡Поддержка", url="https://t.me/definitely_support")],
    [InlineKeyboardButton(text="💳Мои реквизиты", callback_data="cards")]
])

profile = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️Назад", callback_data="start")]])

cards = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕Добавить/Обновить реквизиты", callback_data="add_cards")],
    [InlineKeyboardButton(text="🗑Удалить реквизит", callback_data="defolt_cards")],
    [InlineKeyboardButton(text="♻️Очистить все", callback_data="delete_cards")],
    [InlineKeyboardButton(text="⬅️Назад", callback_data="start")]
])

add_fiat = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="TON", callback_data="add_TON"), 
    InlineKeyboardButton(text="BNB", callback_data="add_BNB"),
    InlineKeyboardButton(text="RUB (Карта)", callback_data="add_RUB")], 
    [InlineKeyboardButton(text="UAH (Карта)", callback_data="add_UAH"),
    InlineKeyboardButton(text="USDT", callback_data="add_USDT"), 
    InlineKeyboardButton(text="⬅️Назад", callback_data="start")],
])

defolt_fiat = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="TON", callback_data="defolt_TON"), 
    InlineKeyboardButton(text="BNB", callback_data="defolt_BNB"),
    InlineKeyboardButton(text="RUB (Карта)", callback_data="defolt_RUB")], 
    [InlineKeyboardButton(text="UAH (Карта)", callback_data="defolt_UAH"),
    InlineKeyboardButton(text="USDT", callback_data="defolt_USDT"), 
    InlineKeyboardButton(text="⬅️Назад", callback_data="start")],
])

offer_fiat = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="TON", callback_data="offer_TON"), 
    InlineKeyboardButton(text="BNB", callback_data="offer_BNB"),
    InlineKeyboardButton(text="RUB (Карта)", callback_data="offer_RUB")], 
    [InlineKeyboardButton(text="UAH (Карта)", callback_data="offer_UAH"),
    InlineKeyboardButton(text="USDT", callback_data="offer_USDT"), 
    InlineKeyboardButton(text="⬅️Назад", callback_data="start")],
])

# Клавиатура для покупателя
buyer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅Проверить оплату", callback_data="check_payment")],
    [InlineKeyboardButton(text="❌Отменить покупку", callback_data="cancel_purchase")]
])

# Клавиатура после проверки оплаты
payment_check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔁Попробовать еще раз", callback_data="check_payment")],
    [InlineKeyboardButton(text="❌Отменить покупку", callback_data="cancel_purchase")]
])

# Клавиатура для продавца после оплаты (ОБНОВЛЕНА!)
seller_gift_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅Я отправил подарок сотруднику", callback_data="send_gift")],
    [InlineKeyboardButton(text="🛡️Обратиться в поддержку", url="https://t.me/definitely_support")]
])