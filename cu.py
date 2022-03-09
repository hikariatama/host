from telethon import functions
from .. import loader, utils
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest


@loader.tds
class CuMod(loader.Module):
    """Полное копирование юзера(ава, имя|фамилия, био)"""

    strings = {"name": "Cu"}

    @loader.owner
    async def cucmd(self, message):
        """.cu <s> <a> <reply/@username>
        <s> - Скрытый режим
        <a> - Удалить ваши аватарки
        Аргументы после юзера не указывайте, не скушает
        Примеры:
        .cu s @user/reply
        .cu a @user/reply
        .cu s a @user/reply"""
        reply = await message.get_reply_message()
        user = None
        s = False
        a = False
        if utils.get_args_raw(message):
            args = utils.get_args_raw(message).split(" ")
            for i in args:
                if i.lower() == "s":
                    s = True
                elif i.lower() in ["а", "a"]:
                    a = True
                else:
                    try:
                        user = await message.client.get_entity(i)
                        break
                    except Exception:
                        continue
        if user is None and reply is not None:
            user = reply.sender
        if user is None and reply is None:
            if not s:
                await message.edit("Кого?")
            return
        if s:
            await message.delete()

        if a:
            avs = await message.client.get_profile_photos("me")
            if len(avs) > 0:
                await message.client(
                    functions.photos.DeletePhotosRequest(
                        await message.client.get_profile_photos("me")
                    )
                )
        full = await message.client(GetFullUserRequest(user.id))
        if full.full_user.profile_photo:
            up = await message.client.upload_file(
                await message.client.download_profile_photo(user, bytes)
            )
            await message.client(functions.photos.UploadProfilePhotoRequest(up))
        await message.client(
            UpdateProfileRequest(
                user.first_name if user.first_name is not None else "",
                user.last_name if user.last_name is not None else "",
                full.full_user.about[:70] if full.full_user.about is not None else "",
            )
        )
        if not s:
            await message.edit("Аккаунт клонирован!")
