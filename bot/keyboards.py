from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def MyInlineKeyboardBuilder(buttons: set) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    
    for button in buttons:
        builder.button(text=f"{button}", callback_data=f"{button}")
        builder.adjust(1)

    return builder

def MyReplyKeyboardBuilder(*buttons: set) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()

    for button in buttons:
        builder.button(text=button)

    return builder