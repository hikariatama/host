from .. import loader, utils

@loader.tds
class TagAllMod(loader.Module):
    """Тегает всех в чате."""
    strings = {"name":"TagAll"}

    async def tagallcmd(self, message):
        """Используй .tagall <текст (по желанию)>."""
        args = utils.get_args_raw(message)
        tag = args or "" 

        tags = []
        async for user in message.client.iter_participants(message.to_id):
            tags.append(f"<a href='tg://user?id={user.id}'>\u2060</a>")
        
        await message.delete()
        
        await message.client.send_message(message.to_id, tag + '\u2060'.join(tags))

