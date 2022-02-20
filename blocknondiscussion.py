#    Friendly Telegram (telegram userbot) module
#    module author: @anon97945


import asyncio
import logging

from telethon import functions
from datetime import timedelta
from telethon.tl.types import User, Channel
from telethon.errors import UserNotParticipantError

from .. import loader, utils

logger = logging.getLogger(__name__)


async def is_linkedchannel(e, c, u, message):
    if not isinstance(e, User):
        full_chat = await message.client(functions.channels.GetFullChannelRequest(channel=u))
        linked_channel_id = int(str(-100) + str(full_chat.full_chat.linked_chat_id))
        if c == linked_channel_id:
            return True
        else:
            return False
    else:
        return False


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def to_bool(value):
    if str(value).lower() in ("true"):
        return True
    if str(value).lower() in ("false"):
        return False


def replaced(sequence, old, new):
    return (new if x == old else x for x in sequence)


async def is_member(c, u, message):
    if c != (await message.client.get_me(True)).user_id:
        try:
            await message.client.get_permissions(c, u)
            return True
        except UserNotParticipantError:
            return False


@loader.tds
class BlockNonDiscussionMod(loader.Module):
    """Block Comments For Non Discussion Members"""
    strings = {"name": "Block Non Discussion",
               "not_dc": "<b>This is no Groupchat.</b>",
               "start": "<b>[BlockNonDiscussion]</b> Activated in this chat.</b>",
               "stopped": "<b>[BlockNonDiscussion]</b> Deactivated in this chat.</b>",
               "turned_off": "<b>[BlockNonDiscussion]</b> The mode is turned off in all chats.</b>",
               "no_int": "<b>Your input was no int.</b>",
               "error": "<b>Your command was wrong.</b>",
               "permerror": "<b>You have no delete permissions in this chat.</b>",
               "settings": ("<b>[BlockNonDiscussion - Settings]</b> Current settings in this"
                             " chat are:\n{}."),
               "triggered": ("{}, the comments are limited to discussiongroup members,"
                             "please join our discussiongroup first."
                             "\n\n👉🏻 {}"
                             "\n\nRespectfully, the admins.")}

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me(True)

    async def bndcmd(self, message):
        """Available commands:
           .bnd
             - Toggles the module for the current chat.
           .bnd notify <true/false>
             - Toggles the notification message.
           .bnd mute <minutes/or 0>
            - Mutes the user for x minutes. 0 to disable.
           .bnd deltimer <seconds/or 0>
            - Deletes the notification message in seconds. 0 to disable.
           .bnd clearall
            - Clears the db of the module"""
        bnd = self._db.get(__name__, "bnd", [])
        sets = self._db.get(__name__, "sets", {})
        args = utils.get_args_raw(message).lower()
        args = str(args).split()
        chat = await message.get_chat()
        chatid = message.chat_id
        chatid_str = str(chatid)

        if args:
            if args[0] == "clearall":
                self._db.set(__name__, "bnd", [])
                self._db.set(__name__, "sets", {})
                return await utils.answer(message, self.strings("turned_off", message))

        if message.is_private:
            await utils.answer(message, self.strings("not_dc", message))
            return

        if not chat.admin_rights and not chat.creator:
            return await utils.answer(message, self.strings("permerror", message))
        else:
            if not chat.admin_rights.delete_messages:
                return await utils.answer(message, self.strings("permerror", message))

        if not args:
            if chatid_str not in bnd:
                bnd.append(chatid_str)
                sets.setdefault(chatid_str, {})
                sets[chatid_str].setdefault("notify", True)
                sets[chatid_str].setdefault("mute", 1)
                sets[chatid_str].setdefault("deltimer", 60)
                self._db.set(__name__, "bnd", bnd)
                self._db.set(__name__, "sets", sets)
                return await utils.answer(message, self.strings("start", message))
            else:
                bnd.remove(chatid_str)
                sets.pop(chatid_str)
                self._db.set(__name__, "bnd", bnd)
                self._db.set(__name__, "sets", sets)
                return await utils.answer(message, self.strings("stopped", message))

        if chatid_str in bnd:
            if args[0] == "notify" and args[1] is not None and chatid_str in bnd:
                if not isinstance(to_bool(args[1]), bool):
                    return await utils.answer(message, self.strings("error", message))
                sets[chatid_str].update({"notify": to_bool(args[1])})
            elif args[0] == "mute" and args[1] is not None and chatid_str in bnd:
                if not represents_int(args[1]):
                    return await utils.answer(message, self.strings("no_int", message))
                else:
                    sets[chatid_str].update({"mute": args[1].capitalize()})
            elif args[0] == "deltimer" and args[1] is not None and chatid_str in bnd:
                if not represents_int(args[1]):
                    return await utils.answer(message, self.strings("no_int", message))
                else:
                    sets[chatid_str].update({"deltimer": args[1]})
            elif args[0] != "settings" and chatid_str in bnd:
                return
            self._db.set(__name__, "sets", sets)
            return await utils.answer(message, self.strings("settings", message).format(str(sets[chatid_str])))

    async def watcher(self, message):
        if not getattr(message, 'raw_text', False):
            return

        bnd = self._db.get(__name__, "bnd", [])
        sets = self._db.get(__name__, "sets", {})
        chatid = message.chat_id
        chatid_str = str(chatid)
        if message.is_private or chatid_str not in bnd:
            return
        chat = await message.get_chat()
        user = await message.get_sender()
        userid = message.sender_id
        entity = await message.client.get_entity(message.sender_id)

        if (await is_linkedchannel(entity, chatid, userid, message)) or isinstance(entity, Channel):
            return
        if not chat.admin_rights and not chat.creator:
            return
        else:
            if not chat.admin_rights.delete_messages:
                return
        usertag = "<a href=tg://user?id=" + str(userid) + ">" + user.first_name + \
                  "</a> (<code>" + str(userid) + "</code>)"
        if (await message.client.get_entity(chatid)).username:
            link = "https://t.me/" + str((await message.client.get_entity(chatid)).username)
        elif chat.admin_rights.invite_users:
            link = await message.client(functions.channels.GetFullChannelRequest(channel=chatid))
            link = link.full_chat.exported_invite.link
        else:
            link = ""
        if not (await is_member(chatid, userid, message)):
            await message.delete()
            if chat.admin_rights.ban_users and sets[chatid_str].get("mute") is not None:
                if sets[chatid_str].get("mute") != "0":
                    MUTETIMER = sets[chatid_str].get("mute")
                    await message.client.edit_permissions(chatid, userid,
                                                          timedelta(minutes=MUTETIMER), send_messages=False)
            if sets[chatid_str].get("notify") is True:
                msgs = await utils.answer(message, self.strings("triggered", message).format(usertag, link))
                if sets[chatid_str].get("deltimer") != "0":
                    DELTIMER = int(sets[chatid_str].get("deltimer"))
                    await asyncio.sleep(DELTIMER)
                    await message.client.delete_messages(chatid, msgs)
