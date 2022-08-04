from config import dp
import handlers.admin
import handlers.user
from aiogram.utils import executor


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
