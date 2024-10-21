from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder


def MyInlineKeyboardBuilder(buttons: set) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for button in buttons:
        # print(button)
        builder.button(text=f"{button}", callback_data=f"{button}")
        builder.adjust(1)

    return builder

def MyReplyKeyboardBuilder(*buttons: set) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()

    print(buttons)
    for button in buttons:
        builder.button(text=button)

    return builder