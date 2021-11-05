import io, inspect
from .. import loader, utils


@loader.tds
class ModulesLinkMod(loader.Module):
    """Ссылка на модуль"""
    strings = {'name': 'ModulesLink'}

    async def mlcmd(self, message):
        """Вывести ссылку на модуль"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, '🦊 <code>.help ModulesLink</code>')

        try:
            f = ' '.join([x.strings["name"] for x in self.allmodules.modules if args.lower() == x.strings["name"].lower()])
            r = inspect.getmodule(next(filter(lambda x: args.lower() == x.strings["name"].lower(), self.allmodules.modules)))

            link = str(r).split('(')[1].split(')')[0]
            if "http" not in link:
                text = f"🦊 <b>{f}</b>"
            else:
                text = f"🦊 <b>{f}</b>: <code>.dlmod {link}</code>"

            out = io.BytesIO(r.__loader__.data)
            out.name = f + ".py"
            out.seek(0)

            await message.respond(text, file=out)
            await message.delete()
        except:
            return await utils.answer(message, "🦊 <b>Модуль не найден</b>")