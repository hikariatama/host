from .. import loader, utils
import io, os, pygments
from pygments.formatters import ImageFormatter
from pygments.lexers import Python3Lexer
from requests import get

#requires: pygments requests

@loader.tds
class ScreenshotMod(loader.Module):
    """Скриншот сайта или файла."""
    strings = {"name": "Screenshot"}

    async def webshotcmd(self, message):
        """Скриншот сайта. Используй: .webshot <ссылка или реплай на ссылку>."""
        reply = None
        link = utils.get_args_raw(message)
        if not link:
            reply = await message.get_reply_message()
            if not reply:
                await message.edit("<b>Нет аргументов или реплая.</b>")
                return
            link = reply.raw_text
        await message.edit("<b>Обработка...</b>")
        url = "https://webshot.deam.io/{}/?width=1920&height=1080?type=png"
        file = get(url.format(link))
        if not file.ok:
            await message.edit("<b>Что-то пошло не так...</b>")
            return
        file = io.BytesIO(file.content)
        file.name = "webScreenshot.png"
        file.seek(0)
        await message.client.send_file(message.to_id, file, reply_to=reply)
        await message.delete()

    async def fileshotcmd(self, message):
        """Скриншот файла. Используй: .fileshot <реплай на файл>."""
        await message.edit("<b>Обработка...</b>")
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("<b>Нет реплая на файл.</b>")
            return
        media = reply.media
        if not media:
            await message.edit("<b>Нет реплая на файл.</b>")
            return
        file = await message.client.download_file(media)
        text = file.decode('utf-8')
        pygments.highlight(text, Python3Lexer(), ImageFormatter(font_name='DejaVu Sans Mono', line_numbers=True),
                           'fileshot | @ftgseen.png')
        await message.client.send_file(message.to_id, 'fileshot | @ftgseen.png', force_document=True)
        os.remove("fileshot | @ftgseen.png")
        await message.delete()