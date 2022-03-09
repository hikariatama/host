import io, inspect
from .. import loader, utils


@loader.tds
class ModulesLinkMod(loader.Module):
    """Retrieves already installed modules' links"""

    strings = {"name": "ModulesLink"}

    async def mlcmd(self, message):
        """Send module link"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "🚫 <b>No args</b>")

        try:
            f = " ".join(
                [
                    x.strings["name"]
                    for x in self.allmodules.modules
                    if args.lower() == x.strings["name"].lower()
                ]
            )
            r = inspect.getmodule(
                next(
                    filter(
                        lambda x: args.lower() == x.strings["name"].lower(),
                        self.allmodules.modules,
                    )
                )
            )

            link = str(r).split("(")[1].split(")")[0]
            if "http" not in link:
                text = f"<b>🧳 {utils.escape_html(f)}</b>"
            else:
                text = f'🧳 <b><a href="{link}">Link</a> for {utils.escape_html(f)}:</b> <code>{link}</code>'

            out = io.BytesIO(r.__loader__.data)
            out.name = f"{f}.py"
            out.seek(0)

            await message.respond(text, file=out)

            if message.out:
                await message.delete()
        except:
            await utils.answer(message, "😔 <b>Module not found</b>")
