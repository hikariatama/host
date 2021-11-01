#   Coded by D4n13l3k00    #
#     t.me/D4n13l3k00      #
# This code under AGPL-3.0 #

from .. import loader, utils
import requests


@loader.tds
class nkapimdMod(loader.Module):
    strings = {"name": "NekosLife"}

    @loader.owner
    async def nkcmd(self, m):
        "Отправить фото/гиф\nПо умолчанию отправляется neko\nМожно указать другую категорию(.nkct)"
        args = utils.get_args_raw(m)
        typ = None
        if args:
            if args in types_of:
                typ = args
        else:
            typ = "neko"
        if typ is None:
            return await m.edit("<b>не знаю такого</b>")
        await m.edit("<b>Mmm...</b>")
        reply = await m.get_reply_message()
        await m.client.send_file(m.to_id, requests.get(f"https://nekos.life/api/v2/img/{typ}").json()["url"], reply_to=reply.id if reply else None)
        await m.delete()

    async def nkctcmd(self, m):
        await m.edit(
            "Доступные категории:\n"
            + "\n".join(f"<code>{i}</code>" for i in types_of)
        )


types_of = ['smug', 'baka', 'tickle', 'slap', 'poke', 'pat', 'neko', 'nekoGif', 'meow', 'lizard', 'kiss', 'hug', 'foxGirl', 'feed', 'cuddle', 'kemonomimi', 'holo', 'woof', 'wallpaper', 'goose', 'gecg', 'avatar', 'waifu', 'randomHentaiGif', 'pussy', 'nekoGif', 'neko', 'lesbian', 'kuni', 'cumsluts', 'classic', 'boobs', 'bJ', 'anal', 'avatar', 'yuri', 'trap', 'tits', 'girlSoloGif', 'girlSolo', 'pussyWankGif', 'pussyArt', 'kemonomimi', 'kitsune', 'keta', 'holo', 'holoEro', 'hentai', 'futanari', 'femdom', 'feetGif', 'eroFeet', 'feet', 'ero', 'eroKitsune', 'eroKemonomimi', 'eroNeko', 'eroYuri', 'cumArts', 'blowJob', 'spank', 'gasm']