from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_inline_keyboard(buttons, row_width=2):
    """Создает inline клавиатуру из списка кнопок"""
    builder = InlineKeyboardBuilder()
    
    for button_row in buttons:
        if isinstance(button_row, list):
            for button in button_row:
                builder.add(InlineKeyboardButton(text=button['text'], 
                                                callback_data=button.get('callback_data'),
                                                url=button.get('url')))
            builder.adjust(row_width)
        else:
            builder.add(InlineKeyboardButton(text=button_row['text'],
                                            callback_data=button_row.get('callback_data'),
                                            url=button_row.get('url')))
    
    return builder.as_markup()

# Главное меню
main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✨ Создать сделку", callback_data="create_offer")],
    [
        InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile"),
        InlineKeyboardButton(text="🛡 Поддержка", url="https://t.me/Garant_NFT_support")
    ],
    [InlineKeyboardButton(text="💳 Мои реквизиты", callback_data="cards")],
    [InlineKeyboardButton(text="📊 Мои сделки", callback_data="my_offers")]
])

# Профиль
profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="start")]
])

# Управление реквизитами
cards = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить/Обновить реквизиты", callback_data="add_cards")],
    [InlineKeyboardButton(text="🗑 Удалить реквизит", callback_data="defolt_cards")],
    [InlineKeyboardButton(text="♻️ Очистить все", callback_data="delete_cards")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="start")]
])

# Добавление реквизитов
add_fiat = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="TON", callback_data="add_TON"), 
        InlineKeyboardButton(text="BNB", callback_data="add_BNB"),
        InlineKeyboardButton(text="RUB (Карта)", callback_data="add_RUB")
    ], 
    [
        InlineKeyboardButton(text="UAH (Карта)", callback_data="add_UAH"),
        InlineKeyboardButton(text="USDT", callback_data="add_USDT")
    ], 
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="cards")]
])

# Удаление реквизитов
defolt_fiat = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="TON", callback_data="defolt_TON"), 
        InlineKeyboardButton(text="BNB", callback_data="defolt_BNB"),
        InlineKeyboardButton(text="RUB (Карта)", callback_data="defolt_RUB")
    ], 
    [
        InlineKeyboardButton(text="UAH (Карта)", callback_data="defolt_UAH"),
        InlineKeyboardButton(text="USDT", callback_data="defolt_USDT")
    ], 
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="cards")]
])

# Выбор валюты для сделки
offer_fiat = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="TON", callback_data="offer_TON"), 
        InlineKeyboardButton(text="BNB", callback_data="offer_BNB"),
        InlineKeyboardButton(text="RUB (Карта)", callback_data="offer_RUB")
    ], 
    [
        InlineKeyboardButton(text="UAH (Карта)", callback_data="offer_UAH"),
        InlineKeyboardButton(text="USDT", callback_data="offer_USDT")
    ], 
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="start")]
])

# Клавиатура для отмены
cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отмена", callback_data="start")]
])