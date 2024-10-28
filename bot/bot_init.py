import logging

# Импорт аиограмм
from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Импорт кастомных функций
from functions.s3 import get_db_types, get_backups_by_database, check_database, download_database
from functions.db import restore_database, create_archive_database, drop_archive_database
from functions.common import clean_temp
from conf.config import CommonConfig

# Импорт клавиатур
from bot.keyboards import MyInlineKeyboardBuilder, MyReplyKeyboardBuilder

logger = logging.getLogger(__name__)

# Создаем диспетчер
dp = Dispatcher()
# Накладываем фильтр, чтобы он отвечал только юзерам из списка админов
dp.message.filter(F.from_user.id.in_(CommonConfig.tg_admins))

# Состояния для выбора бэкапа и подтверждения
class MyStates(StatesGroup):
    input_database = State()
    approve_restore = State()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Ловим команду старт
    """
    logger.debug('StartCommand')
    await message.answer(f"Витя, выбери одну из доступных баз!",
                         reply_markup=MyInlineKeyboardBuilder(get_db_types()).as_markup())


@dp.callback_query()
async def choose_database(callback: CallbackQuery, state: FSMContext):
    """
    Если Витя выбрал кнопку из списка баз, то ловим колбэк от нее
    """
    # Закрываем нажатую кнопку
    await callback.answer()

    # Получаем список бэкапов выбранной базы данных
    list_of_backups = get_backups_by_database(callback.data)

    # Поворачиваем в формат для ответа (string)
    text = '\n'.join(list_of_backups)

    # Отвечаем и выставляем состояние ожидания ввода базы
    await callback.message.answer(text)
    await state.set_state(MyStates.input_database)
    await callback.message.answer(f'Скопируй название нужной базы и пришли ответным сообщением')

@dp.message(MyStates.input_database)
async def choose_database2(message: Message, state: FSMContext):
    """
    Отлавливаем ввод выбранного бэкапа
    """
    await message.answer(f'Ты выбрал базу: {message.text}. Чекнем ее.')

    # Проверяем правильность ввода выбранного бэкапа TODO: добавить проверку, что БД выбрана именно из этих))
    # Если все правильно - запрашиваем подтверждение
    if not check_database(message.text):
        await message.answer('А нету такой базы, Витя.')
    else:
        await message.answer('Молодец, Витя, смог! Есть такая база в этом бэкапе. Ты уверен, что ее надо раздуплить?\nЭто займет какое-то время..',
                             reply_markup=MyReplyKeyboardBuilder('YES', 'NO').as_markup())
        await state.update_data({'choosed_backup': message.text})
        await state.set_state(MyStates.approve_restore)

@dp.message(MyStates.approve_restore)
async def choose_database3(message: Message, state: FSMContext):
    """
    Отлавливаем подтверждение. Если подтверждает - то начинаем разворачивать. Если нет, то грустим
    """
    if message.text == 'YES':
        await message.answer('Ну чтож, теперь придется некоторое время подождать. Я напишу тебе, когда все раздуплится. Но это все равно быстрее, чем выпрашивать меня лично :))',
                             reply_markup=ReplyKeyboardRemove())
        # restore procedure
        choosed_backup = await state.get_data()
        choosed_backup = choosed_backup.get('choosed_backup')
        logger.info(f'Выбранный бэкап: {choosed_backup}')
        await message.answer('Начали загрузку файла')
        result = download_database(choosed_backup)
        await message.answer(result['message'])
        if result['status']:
            logger.info('Загрузка успешно завершена, теперь удаляем старую БД с архивом')
            result = drop_archive_database()
            await message.answer(result['message'])
            if result['status']:
                logger.info('Дроп БД archive прошел успешно, теперь создаем ее')
                result = create_archive_database()
                await message.answer(result['message'])
                if result['status']:
                    logger.info('Создание БД archive прошло успешно, теперь восстанавливаем архив')
                    result = restore_database(choosed_backup)
                    await message.answer(result['message'])
                    if result['status']:
                        clean_temp()

    else:
        await message.answer('Неуверенность - не всегда плохо. Чтож, давай попробуем сначала. Жми старт, что ли')
        await state.clear()

async def start_bot() -> None:
    """
    Запуск бота
    """
    bot = Bot(token=CommonConfig.bot_token)

    await dp.start_polling(bot)