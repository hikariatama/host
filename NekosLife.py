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


types_of = ['femdom', 'tickle', 'classic', 'ngif', 'erofeet', 'meow', 'erok', 'poke', 'les', 'hololewd', 'lewdk', 'keta', 'feetg', 'nsfw_neko_gif', 'eroyuri', 'kiss', '_8ball', 'kuni', 'tits', 'pussy_jpg', 'cum_jpg', 'pussy', 'lewdkemo', 'lizard', 'slap', 'lewd', 'cum', 'cuddle', 'spank', 'smallboobs', 'goose',
            'Random_hentai_gif', 'avatar', 'fox_girl', 'nsfw_avatar', 'hug', 'gecg', 'boobs', 'pat', 'feet', 'smug', 'kemonomimi', 'solog', 'holo', 'wallpaper', 'bj', 'woof', 'yuri', 'trap', 'anal', 'baka', 'blowjob', 'holoero', 'feed', 'neko', 'gasm', 'hentai', 'futanari', 'ero', 'solo', 'waifu', 'pwankg', 'eron', 'erokemo']
