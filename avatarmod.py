#   Coded by D4n13l3k00    #
#     t.me/D4n13l3k00      #
# This code under AGPL-3.0 #

import os

from telethon import functions, types

from .. import loader, utils


@loader.tds
class AvaMod(loader.Module):
    """Установка/удаление аватарок через команды"""
    strings = {
        'name': 'AvatarMod',
        'need_pic': '<b>[Avatar]</b> Нужно фото',
        'downloading': '<b>[Avatar]</b> Скачиваю',
        'installing': '<b>[Avatar]</b> Устанавливаю',
        'deleting': '<b>[Avatar]</b> Удаляю',
        'ok': '<b>[Avatar]</b> Готово',
        'no_avatar': '<b>[Avatar]</b> Нету аватарки/ок',
    }

    async def avacmd(self, m: types.Message):
        '.ava <reply_to_photo> - Установить аватар'
        client = m.client
        reply = await m.get_reply_message()
        if not reply and not reply.photo:
            return await utils.answer(m, self.strings('need_pic'))

        m = await utils.answer(m, self.strings('downloading'))
        photo = await client.download_media(message=reply.photo)
        up = await client.upload_file(photo)
        m = await utils.answer(m, self.strings('installing'))
        await client(functions.photos.UploadProfilePhotoRequest(up))
        await utils.answer(m, self.strings('ok'))
        os.remove(photo)

    async def delavacmd(self, m: types.Message):
        'Удалить текущую аватарку'
        client = m.client
        ava = await client.get_profile_photos('me', limit=1)
        if len(ava) > 0:
            m = await utils.answer(m, self.strings('deleting'))
            await client(functions.photos.DeletePhotosRequest(ava))
            await utils.answer(m, self.strings('ok'))
        else:
            await utils.answer(m, self.strings('no_avatar'))

    async def delavascmd(self, m: types.Message):
        'Удалить все аватарки'
        client = m.client
        ava = await client.get_profile_photos('me')
        if len(ava) > 0:
            m = await utils.answer(m, self.strings('deleting'))
            await client(functions.photos.DeletePhotosRequest(await m.client.get_profile_photos('me')))
            await utils.answer(m, self.strings('ok'))
        else:
            await utils.answer(m, self.strings('no_avatar'))
