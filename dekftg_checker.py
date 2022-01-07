#   Coded by D4n13l3k00    #
#     t.me/D4n13l3k00      #
# This code under AGPL-3.0 #

from .. import loader, utils
import aiohttp


@loader.tds
class CheckerTGMod(loader.Module):
    """CheckerTG"""
    strings = {
        'name': 'CheckerTG',
        'check': '<b>[CheckerAPI]</b> Делаем запрос к API...',
        'response': '<b>[CheckerAPI]</b> Ответ API: <code>{}</code>\nВремя выполнения: <code>{}</code>'
    }

    @loader.owner
    async def checkcmd(self, m):
        """ Проверить id на слитый номер
        Жуёт либо <reply> либо <uid>
        """
        reply = await m.get_reply_message()
        if utils.get_args_raw(m):
            user = utils.get_args_raw(m)
        elif reply:
            try:
                user = str(reply.sender.id)
            except:
                return await m.edit("<b>Err</b>")
        else:
            return await m.edit("[CheckerAPI] А кого чекать?")
        await m.edit(self.strings['check'])
        async with aiohttp.ClientSession() as s, s.get('https://api.d4n13l3k00.ru/tg/leaked/check?uid=' + user) as r:
            r = await r.json()
            await m.edit(self.strings['response'].format(r['data'], str(round(r['time'], 3))+"ms"))

    @loader.owner
    async def rcheckcmd(self, m):
        """ Обратный поиск
        Жуёт <phone number>
        """
        reply = await m.get_reply_message()
        if utils.get_args_raw(m):
            phone = utils.get_args_raw(m)
        elif reply:
            try:
                phone = reply.raw_text
            except:
                return await m.edit("<b>Err</b>")
        else:
            return await m.edit("[CheckerAPI] А кого чекать?")
        await m.edit(self.strings['check'])
        async with aiohttp.ClientSession() as s, s.get('https://api.d4n13l3k00.ru/tg/leaked/check?r=1?uid=' + phone) as r:
            r = await r.json()
            await m.edit(self.strings['response'].format(r['data'], str(round(r['time'], 3))+"ms"))
