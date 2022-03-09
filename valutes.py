from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from .. import loader, utils


class ValuteMod(loader.Module):
    """Valute Converter"""

    strings = {"name": "Valute"}

    async def valcmd(self, message):
        """<sum> <valute> - Get exchange"""
        state = utils.get_args_raw(message)
        await utils.answer(message, "<b>Данные получены</b>")
        chat = "@exchange_rates_vsk_bot"
        async with message.client.conversation(chat) as conv:
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=1210425892)
                )
                bot_send_message = await message.client.send_message(
                    chat, format(state)
                )
                bot_response = response = await response
            except YouBlockedUserError:
                await utils.answer(message, f"<b>Убери из ЧС:</b> {chat}")
                return
            await bot_send_message.delete()
            await utils.answer(message, response.text)
            await bot_response.delete()
