from .. import loader, utils, main
import io

try:
    import eyed3
except:
    import os

    os.system("pip3 install eyed3")


@loader.tds
class ID3EditorMod(loader.Module):
    """Модуль, который может изменять теги по ответу на аудио.

    by @zxcminimalized
    """

    strings = {"name": "ID3 Editor"}

    async def titlecmd(self, message):
        """Поменять тег названия трека"""
        reply = await message.get_reply_message()
        try:
            test = message.message.split("title ")[1]
        except:
            await message.edit("<b>Вы не указали название!</b>")
        else:
            if not reply or not reply.audio:
                await message.edit("<b>Ответьте на аудио!</b>")
            else:
                await message.edit("<b>Отправка...</b>")
                await reply.download_media("file.mp3")
                load = eyed3.load("file.mp3")
                load.tag.title = test
                load.tag.save()
                await reply.reply(file="file.mp3")

    async def artistcmd(self, message):
        """Поменять артиста"""
        reply = await message.get_reply_message()
        try:
            test = message.message.split("artist ")[1]
        except:
            await message.edit("<b>Вы не указали артиста!</b>")
        else:
            if not reply or not reply.audio:
                await message.edit("<b>Ответьте на аудио!</b>")
            else:
                await message.edit("<b>Отправка...</b>")
                await reply.download_media("file.mp3")
                load = eyed3.load("file.mp3")
                load.tag.artist = test
                load.tag.save()
                await reply.reply(file="file.mp3")

    async def albumcmd(self, message):
        """Поменять тег альбома"""
        reply = await message.get_reply_message()
        try:
            test = message.message.split("album ")[1]
        except:
            await message.edit("<b>Вы не указали альбом!</b>")
        else:
            if not reply or not reply.audio:
                await message.edit("<b>Ответьте на аудио!</b>")
            else:
                await message.edit("<b>Отправка...</b>")
                await reply.download_media("file.mp3")
                load = eyed3.load("file.mp3")
                load.tag.album = test
                load.tag.save()
                await reply.reply(file="file.mp3")
