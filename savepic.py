from .. import loader
import io


class SaverMod(loader.Module):
    strings = {"name": "SavePic"}

    async def згcmd(self, m):
        ".зг + реплай на самоуничтожающееся фото Чтобы сохранить"
        reply = await m.get_reply_message()
        if not reply or not reply.media.ttl_seconds:
            return await m.edit("Реплаем на самоуничтожающееся фото! ")
        await m.delete()
        new = io.BytesIO(await reply.download_media(bytes))
        new.name = reply.file.name
        await m.client.send_file("me", new)
