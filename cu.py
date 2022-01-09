
 
from telethon import functions, types 
from .. import loader, utils 
from asyncio import sleep 
from telethon.tl.functions.account import UpdateProfileRequest 
from telethon.tl.functions.users import GetFullUserRequest 
 
@loader.tds 
class CuMod(loader.Module): 
    """Полное копирование юзера(ава, имя|фамилия, био)""" 
    strings = {'name': 'Cu'} 
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
                if i.lower() == "s": s = True
                elif i.lower() in ["а", "a"]: a = True
                else: 
                    try: 
                        user = await message.client.get_entity(i) 
                        break 
                    except: 
                        continue
        if user is None and reply != None: user = reply.sender
        if user is None and reply is None: 
            if not s: await message.edit("Кого?") 
            return
        if s: await message.delete()
        if not s: 
            for i in range(11): 
                await message.edit(f"Получаем доступ к аккаунту пользователя [{i*10}%]\n[{(i*'#').ljust(10, '–')}]") 
                await sleep(0.3)
        if a: 
            avs = await message.client.get_profile_photos('me') 
            if len(avs) > 0: 
                await message.client(functions.photos.DeletePhotosRequest(await message.client.get_profile_photos('me')))
        full = await message.client(GetFullUserRequest(user.id))
        if not s: await message.edit("Получаем аватарку... [35%]\n[###–––––––]")
        if full.profile_photo: 
            up = await message.client.upload_file(await message.client.download_profile_photo(user, bytes)) 
            if not s: await message.edit("Ставим аватарку... [50%]\n[#####–––––]") 
            await message.client(functions.photos.UploadProfilePhotoRequest(up))
        if not s: await message.edit("Получаем данные...  [99%]\n[#########–]")
        await message.client(UpdateProfileRequest( 
            user.first_name if user.first_name != None else "", 
            user.last_name if user.last_name != None else "", 
            full.about[:70] if full.about != None else "" 
        ))
        if not s: await message.edit("Аккаунт клонирован! [100%]\n[##########]")
        if not s: await sleep(5)
        if not s: await message.edit("Аккаунт клонирован!")