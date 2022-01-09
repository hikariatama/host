from .. import loader, utils
from datetime import datetime, date, time
from asyncio import sleep
import os, io, asyncio, pytz, requests

@loader.tds
class SeeChatMod(loader.Module):
    """tracking in all PM chats."""
    strings={"name": "SeeChat"}

    async def client_ready(self, message, db):
        self.db=db
        self.db.set("SeeChat", "seechat", True)
        di = "SeeChat/"
        if os.path.exists(di):
            None
        else:
            os.mkdir(di)

    async def seechatcmd(self, message):
        """use: .seechat | to enable tracking in all PM chats."""
       
        if not await message.client.get_me():
            return await message.edit("<b>Something went wrong..<b>")
        if self.db.get("SeeChat", "seechat") is not True:
            await message.edit("[SeeChat] turned on seccsessfully.")
            self.db.set("SeeChat", "seechat", True)
        else:
            await message.edit("[SeeChat] turned off seccsessfully.")
            self.db.set("SeeChat", "seechat", False)

    async def setchatcmd(self, message):
        """use: .setchat | to set this chat as a track chat."""
       
        if not await message.client.get_me():
            return await message.edit("<b>Something went wrong..<b>")
        chat = await message.client.get_entity(message.to_id)
        self.db.set("SeeChat", "log", str(chat.id))
        await message.edit('<b>This chat was set as a chat for tracks.</b>')

    async def seechatscmd(self, message):
        """use: .seechats | to see the list of tracking people."""
        
        if not message.client.get_me():
            return await message.edit("<b>Something went wrong..<b>")
        await message.edit("wait a second..")
        chats = ""
        number = 0
        for _ in os.listdir("SeeChat/"):
            number += 1
            try:
                user = await message.client.get_entity(int(_[:-4]))
            except: pass
            if not user.deleted:
                chats += f"{number} • <a href=tg://user?id={user.id}>{user.first_name}</a> ID: [<code>{user.id}</code>]\n"
            else:
                chats += f"{number} • Deleted account ID: [<code>{user.id}</code>]\n"
        await message.edit("<b>tracking users:</b>\n\n" + chats)

    async def gseecmd(self, message):
        """use: .gsee {id} | to get the tracked file."""
        
        if not message.client.get_me():
            return await message.edit("<b>Something went wrong..<b>")
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("<b>what about args?</b>")
        try:
            user = await message.client.get_entity(int(args))
            await message.edit(f"<b>PM file with: <code>{user.first_name}</code></b>")
            await message.client.send_file(message.to_id, f"SeeChat/{args}.txt")
        except: return await message.edit("<b>file is empty.</b>")

    async def delseecmd(self, message):
        """use: .delsee {id} | to delete the tracked file."""
        
        if not message.client.get_me():
            return await message.edit("<b>Something went wrong..<b>")
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("<b>what about args?</b>")
        if args == "all":
            os.system("rm -rf SeeChat/*")
            await message.edit("<b>all PM chats file has been successfully deleted.</b>")
        else:
            try:
                user = await message.client.get_entity(int(args))
                await message.edit(f"<b>the chat file has been deleted with: <code>{user.first_name}</code></b>")
                os.remove(f"SeeChat/{args}.txt")
            except: return await message.edit("<b>file can't be deleted.</b>")

    async def excseecmd(self, message):
        """use: .excsee {id} | to add / remove user from exclude tracking."""

        if not message.client.get_me():
            return await message.edit("<b>Something went wrong..<b>")
        exception = self.db.get("SeeChat", "exception", [])
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("<b>what about args?</b>")
        if args == "clear":
            self.db.set("SeeChat", "exception", [])
            return await message.edit("<b>the exclusion list was cleared successfully.</b>")
        try:
            user = await message.client.get_entity(int(args))
            if str(user.id) not in exception:
                exception.append(str(user.id))
                await message.edit(f"<b>{user.first_name}, has been added to the list of exclusions.</b>")
                os.remove(f"SeeChat/{user.id}.txt")
            else:
                exception.remove(str(user.id))
                await message.edit(f"<b>{user.first_name}, has been removed from the list of exclusions.</b>")
            self.db.set("SeeChat", "exception", exception)
        except: return await message.edit("<b>failed to remove user from the list of exclusions</b>")
    
    async def exclistcmd(self, message):
        """use: .exclist | to see the list of exceptions."""
        
        if not message.client.get_me():
            return await message.edit("<b>Something went wrong..<b>")
        exception = self.db.get("SeeChat", "exception", [])
        number = 0
        users = ""
        try:
            for _ in exception:
                user = await message.client.get_entity(int(_))
                number += 1
                users += f"{number} • <a href=tg://user?id={user.id}>{user.first_name}</a> ID: [<code>{user.id}</code>]\n"
            await message.edit("<b>list of exclusions:</b>\n\n" + users)
        except: return await message.edit("<b>the list of users is empty.</b>")

    async def watcher(self, message):
        me = await message.client.get_me()
        seechat = self.db.get("SeeChat", "seechat")
        exception = self.db.get("SeeChat", "exception", [])
        log = self.db.get("SeeChat", "log", str(me.id))
        chat = await message.client.get_entity(int(log))
        timezone = "Europe/Kiev"
        vremya = datetime.now(pytz.timezone(timezone)).strftime("[%Y-%m-%d %H:%M:%S]")
        user = await message.client.get_entity(message.chat_id)
        userid = str(user.id)
        try:
            if message.sender_id == me.id: user.first_name = me.first_name
        except: pass
        if (
            message.is_private
            and seechat is not False
            and userid not in exception
            and not user.bot
            and not user.verified
        ):
            if message.text.lower():
                file = open(f"SeeChat/{user.id}.txt", "a", encoding='utf-8')
                file.write(f"{user.first_name} >> {message.text} << {vremya}\n\n")
            if message.photo:
                if message.sender_id == me.id:
                    return
                file = io.BytesIO()
                file.name = message.file.name or f"SeeChat{message.file.ext}"
                await message.client.download_file(message, file)
                file.seek(0)
                await message.client.send_message(chat.id, f"<b>picture from</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>:")
                await message.client.send_file(chat.id, file, force_document=False)
            if (
                not message.voice
                and not message.video_note
                and not message.video
                and message.audio
                and message.sender_id == me.id
                or not message.voice
                and not message.video_note
                and not message.video
                and not message.audio
                and message.document
                and message.sender_id == me.id
            ):
                return
            elif (
                not message.voice
                and not message.video_note
                and not message.video
                and message.audio
                or not message.voice
                and not message.video_note
                and not message.video
                and message.document
                or not message.voice
                and not message.video_note
                and not message.video
            ):
                pass
            elif message.voice or message.video_note:
                if message.sender_id == me.id:
                    return
                await message.forward_to(chat.id)
            else:
                if message.sender_id == me.id:
                    return
                try:
                    file = message.file.name or "huita" + message.file.ext
                    await message.download_media(file)
                    await message.client.send_message(chat.id, f"<b>Video from</b> <a href='tg://user?id={user.id}'>{user.first_name}</a>:")
                    await message.client.send_file(chat.id, file)
                    os.remove(file)
                except:
                        pass
