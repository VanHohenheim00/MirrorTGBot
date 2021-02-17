from aiogram import executor, types, Dispatcher, filters
from models import *
from config import bot
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from lang import Lang
from utils.graber import swaps_worker
import re
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

log = logging.getLogger()

dp = Dispatcher(bot)
logger_middleware = LoggingMiddleware()
dp.middleware.setup(logger_middleware)


@dp.message_handler(lambda x: x.reply_markup)
async def pass_msg_with_btns(message):
    pass


@dp.message_handler(commands=['live', 'blive'])
async def live_handler(message: types.Message):
    try:
        _, pair = message.text.split()
        if match := re.match(r"0x\w{40}", pair):
            live_obj = await LiveGate.create(chat_id=message.chat.id, active=True)
            live_obj.pair = match.group(0)
            if message.text.startswith("/blive"):
                live_obj.alert_type = TypeOfChains.pancakeswap
            await live_obj.save()
            await bot.send_message(message.chat.id, Lang.live_changed.format(match.group(0)))
        else:
            await bot.send_message(message.chat.id, Lang.error_msg)
    except:
        await bot.send_message(message.chat.id, Lang.live_error_msg, parse_mode='html')


@dp.message_handler(commands=['lives', 'blives'])
async def live_settings_handler(message: types.Message):
    chain = TypeOfChains.uniswap if message.text.startswith("/lives") else TypeOfChains.pancakeswap
    link_tmp = "https://info.uniswap.org/pair/{}" if message.text.startswith(
        "/lives") else 'https://pancakeswap.info/pair/{}'
    msg = f"<b>Your live pairs on {chain.name} exchange:</b>\n\n"
    num = 1
    async for gate in LiveGate.filter(chat_id=message.chat.id, alert_type=chain):
        msg += f"{num}) <a href='{link_tmp.format(gate.pair)}'>{gate.pair[:4]}...{gate.pair[-4:]}</a>\n" \
               f"/stop_{gate.id} /start_{gate.id} /delete_{gate.id}\n"
        num += 1
    await bot.send_message(message.chat.id, msg, parse_mode='html', disable_web_page_preview=True)


@dp.message_handler(
    filters.RegexpCommandsFilter(regexp_commands=['stop_([0-9]*)', 'start_([0-9]*)', 'delete_([0-9]*)']))
async def live_start_stop_delete(message: types.Message):
    cmd, g_id = message.text.split('_')
    gate = await LiveGate.get_or_none(id=int(g_id))
    if not gate or gate.chat_id != message.chat.id:
        await bot.send_message(message.chat.id, Lang.gate_not_exist)
    elif cmd == "/stop":
        gate.active = False
        await gate.save()
        await bot.send_message(message.chat.id, Lang.live_stopped)
    elif cmd == "/start":
        gate.active = True
        await gate.save()
        await bot.send_message(message.chat.id, Lang.live_started)
    elif cmd == "/delete":
        await gate.delete()
        await bot.send_message(message.chat.id, Lang.live_deleted)


@dp.channel_post_handler()
async def channel_handler(message: types.Message):
    if message.text.startswith(('/lives', '/blives')):
        await live_settings_handler(message)
    elif message.text.startswith(('/live', '/blive')):
        await live_handler(message)
    elif message.text.startswith(('/start', '/stop', '/delete')):
        await live_start_stop_delete(message)


if __name__ == "__main__":
    try:
        dp.loop.run_until_complete(init())
        dp.loop.create_task(swaps_worker())
        dp.loop.create_task(swaps_worker("https://api.bscgraph.org/subgraphs/name/cakeswap",
                                         TypeOfChains.pancakeswap))
        executor.start_polling(dp)
    except Exception as e:
        log.exception(e)
