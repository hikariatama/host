"""
    Copyright 2021 t.me/Fl1yd, t.me/spypm
    Licensed under the Apache License, Version 2.0

    Authors are not responsible for any consequences caused by using this
    software or any of its parts.
"""

import io
import json
import base64
import requests
import telethon

from telethon.tl import types
from telethon.tl.patched import Message

from typing import List, Union
from time import gmtime

from .. import loader, utils


def get_message_media(message: Message):
    return (
        message.photo
        or message.sticker
        or message.video
        or message.video_note
        or message.gif
        or message.web_preview
        if message and message.media
        else None
    )


def get_entities(entities: types.TypeMessageEntity):
    # coded by @droox
    r = []
    if entities:
        for entity in entities:
            entity = entity.to_dict()
            entity["type"] = entity.pop("_").replace("MessageEntity", "").lower()
            r.append(entity)
    return r


def get_message_text(message: Message, reply: bool = False):
    return (
        "📷 Фото"
        if message.photo and reply
        else message.file.emoji + " Стикер"
        if message.sticker and reply
        else "📹 Видеосообщение"
        if message.video_note and reply
        else "📹 Видео"
        if message.video and reply
        else "🖼 GIF"
        if message.gif and reply
        else "📊 Опрос"
        if message.poll
        else "📍 Местоположение"
        if message.geo
        else "👤 Контакт"
        if message.contact
        else f"🎵 Голосовое сообщение: {strftime(message.voice.attributes[0].duration)}"
        if message.voice
        else f"🎧 Музыка: {strftime(message.audio.attributes[0].duration)} | {message.audio.attributes[0].performer} - {message.audio.attributes[0].title}"
        if message.audio
        else f"💾 Файл: {message.file.name}"
        if type(message.media) == types.MessageMediaDocument and not get_message_media(message)
        else f"{message.media.emoticon} Дайс: {message.media.value}"
        if type(message.media) == types.MessageMediaDice
        else f"Service message: {message.action.to_dict()['_']}"
        if type(message) == types.MessageService
        else ""
    )


def strftime(time: Union[int, float]):
    t = gmtime(time)
    return (
        (
            f"{t.tm_hour:02d}:"
            if t.tm_hour > 0
            else ""
        ) + f"{t.tm_min:02d}:{t.tm_sec:02d}"
    )


@loader.tds
class ShitQuotesMod(loader.Module):
    """
    Quotes by @sh1tchannel
    """

    strings = {
        "name": "SQuotes",
        "no_reply": "<b>[SQuotes]</b> No reply",
        "api_error": "<b>[SQuotes]</b> API error",
        "no_args_or_reply": "<b>[SQuotes]</b> No args or reply",
        "args_error": "<b>[SQuotes]</b> An error ocurred while parsing args. Request was: <code>{}</code>",
    }

    async def client_ready(self, client: telethon.TelegramClient, db: dict) -> None:
        self.client = client
        self.db = db
        self.api_endpoint = "https://quotes.fl1yd.su/generate"
        self.settings = self.get_settings()


    async def qcmd(self, message: Message) -> None:
        """
        <reply> [quantity] [!file] [color] - Create nice quote from message(-s)
        """

        args: List[str] = utils.get_args(message)
        if not await message.get_reply_message():
            await utils.answer(message, self.strings["no_reply"])
            return

        isFile = "!file" in args
        [count] = [int(arg) for arg in args if arg.isdigit() and int(arg) > 0] or [1]
        [bg_color] = [arg for arg in args if arg != "!file" and not arg.isdigit()] or [self.settings["bg_color"]]

        payload = {
            "messages": await self.quote_parse_messages(message, count),
            "quote_color": bg_color,
            "text_color": self.settings["text_color"]
        }

        r = await self._api_request(payload)
        if r.status_code != 200:
            await utils.answer(message, self.strings["api_error"])
            return

        quote = io.BytesIO(r.content)
        quote.name = "SQuote" + (".png" if isFile else ".webp")

        await utils.answer(message, quote, force_document=isFile)
        await (message[0] if isinstance(message, (list, tuple, set)) else message).delete()


    async def quote_parse_messages(self, message: Message, count: int):
        payloads = []
        messages = [
            msg async for msg in self.client.iter_messages(
                message.chat_id, count, reverse = True, add_offset = 1,
                offset_id = (await message.get_reply_message()).id,
            )
        ]

        for message in messages:
            avatar = rank = reply_id = reply_name = reply_text = None
            entities = get_entities(message.entities)

            if message.fwd_from:
                if message.fwd_from.from_id:
                    if type(message.fwd_from.from_id) == types.PeerChannel:
                        user_id = message.fwd_from.from_id.channel_id
                    else:
                        user_id = message.fwd_from.from_id.user_id
                    try:
                        user = await self.client.get_entity(user_id)
                    except Exception:
                        name, avatar = await self.get_profile_data(message.sender)
                        return (
                            "Вот блин, произошла ошибка. Возможно на этом канале тебя забанили, и невозможно получить информацию.",
                            None, message.sender.id, name, avatar, "ошибка :(", None, None, None, None
                        )
                    name, avatar = await self.get_profile_data(user)
                    user_id = user.id

                elif name := message.fwd_from.from_name:
                    user_id = message.chat_id
            else:
                if reply := await message.get_reply_message():
                    reply_id = reply.sender.id
                    reply_name = telethon.utils.get_display_name(reply.sender)
                    reply_text = get_message_text(reply, True) + (
                        ". " + reply.raw_text
                        if reply.raw_text and get_message_text(reply, True)
                        else reply.raw_text or ""
                    )

                user = await self.client.get_entity(message.sender)
                name, avatar = await self.get_profile_data(user)
                user_id = user.id

                if message.is_group and message.is_channel:
                    admins = await self.client.get_participants(message.chat_id, filter = types.ChannelParticipantsAdmins)
                    if user in admins:
                        admin = admins[admins.index(user)].participant
                        rank = admin.rank or ("creator" if type(admin) == types.ChannelParticipantCreator else "admin")

            media = await self.client.download_media(get_message_media(message), bytes, thumb = -1)
            media = base64.b64encode(media).decode() if media else None

            via_bot = message.via_bot.username if message.via_bot else None
            text = (
                (message.raw_text or "") + (
                    (
                        "\n\n" + get_message_text(message)
                        if message.raw_text
                        else get_message_text(message)
                    )
                    if get_message_text(message)
                    else ""
                )
            )

            payloads.append(
                {
                    "text": text,
                    "media": media,
                    "entities": entities,
                    "author": {
                        "id": user_id,
                        "name": name,
                        "avatar": avatar,
                        "rank": rank or "",
                        "via_bot": via_bot
                    },
                    "reply": {
                        "id": reply_id,
                        "name": reply_name,
                        "text": reply_text
                    }
                }
            )

        return payloads


    async def fsqcmd(self, message: Message):
        """<@ / ID> + <text> + -r + <@ / ID> + <text>; <args> - Create fake quote"""

        args: str = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        if not (args or reply):
            await utils.answer(message, self.strings["no_args_or_reply"])
            return

        try:
            payload = await self.fakequote_parse_messages(args, reply)
        except (IndexError, ValueError):
            await utils.answer(
                message, self.strings["args_error"].format(
                    message.text)
            )
            return

        payload = {
            "messages": payload,
            "quote_color": self.settings["bg_color"],
            "text_color": self.settings["text_color"]
        }

        r = await self._api_request(payload)
        if r.status_code != 200:
            await utils.answer(message, self.strings["api_error"])
            return

        quote = io.BytesIO(r.content)
        quote.name = "SQuote.webp"

        await utils.answer(message, quote)
        await (message[0] if isinstance(message, (list, tuple, set)) else message).delete()


    async def fakequote_parse_messages(self, args: str, reply: Message):
        async def get_user(args: str):
            args_, text = args.split(), ""
            user = await self.client.get_entity(
                int(args_[0]) if args_[0].isdigit() else args_[0])

            if len(args_) < 2:
                user = await self.client.get_entity(
                    int(args) if args.isdigit() else args)
            else:
                text = args.split(maxsplit = 1)[1]
            return user, text

        if reply or reply and args:
            user = reply.sender
            name, avatar = await self.get_profile_data(user)
            text = args or ""

        else:
            messages = []
            for part in args.split("; "):
                user, text = await get_user(part)
                name, avatar = await self.get_profile_data(user)
                reply_id = reply_name = reply_text = None

                if " -r " in part:
                    user, text = await get_user(''.join(part.split(" -r ")[0]))
                    user2, text2 = await get_user(''.join(part.split(" -r ")[1]))

                    name, avatar = await self.get_profile_data(user)
                    name2, _ = await self.get_profile_data(user2)

                    reply_id = user2.id
                    reply_name = name2
                    reply_text = text2

                messages.append(
                    {
                        "text": text,
                        "media": None,
                        "entities": None,
                        "author": {
                            "id": user.id,
                            "name": name,
                            "avatar": avatar,
                            "rank": ""
                        },
                        "reply": {
                            "id": reply_id,
                            "name": reply_name,
                            "text": reply_text
                        }
                    }
                )
            return messages

        return [
            {
                "text": text,
                "media": None,
                "entities": None,
                "author": {
                    "id": user.id,
                    "name": name,
                    "avatar": avatar,
                    "rank": ""
                },
                "reply": {
                    "id": None,
                    "name": None,
                    "text": None
                }
            }
        ]


    async def get_profile_data(self, user: types.User):
        avatar = await self.client.download_profile_photo(user.id, bytes)
        return telethon.utils.get_display_name(user), \
            base64.b64encode(avatar).decode() if avatar else None


    async def sqsetcmd(self, message: Message) -> None:
        """<bg_color/text_color> <value> - Configure SQuotes"""
        args: List[str] = utils.get_args_raw(message).split(maxsplit=1)
        if not args:
            return await utils.answer(
                message,
                f"<b>[SQuotes]</b> Settings:\n\n"
                f"Max messages (<code>max_messages</code>): {self.settings['max_messages']}\n"
                f"Background color (<code>bg_color</code>): {self.settings['bg_color']}\n"
                f"Foreground color (<code>text_color</code>): {self.settings['text_color']}"
            )

        if args[0] == "reset":
            self.get_settings(True)
            await utils.answer(message, "<b>[SQuotes]</b> Settings has been reset")
            return

        if len(args) < 2:
            await utils.answer(message, "<b>[SQuotes]</b> Insufficient args")
            return

        mods = ["max_messages", "bg_color", "text_color"]
        if args[0] not in mods:
            await utils.answer(message, f"<b>[SQuotes]</b> Unknown param")
            return
        elif args[0] == "max_messages":
            if not args[1].isdigit():
                await utils.answer(message, "<b>[SQuotes]</b> Number is expected")
                return

            self.settings[args[0]] = int(args[1])

        else:
            self.settings[args[0]] = args[1]

        self.db.set("SQuotes", "settings", self.settings)
        return await utils.answer(
            message, f"<b>[SQuotes]</b> Param {args[0]} value is now {args[1]}")


    def get_settings(self, force: bool = False):
        settings: dict = self.db.get("SQuotes", "settings", {})
        if not settings or force:
            settings.update(
                {
                    "max_messages": 15,
                    "bg_color": "#162330",
                    "text_color": "#fff"
                }
            )
            self.db.set("SQuotes", "settings", settings)

        return settings


    async def _api_request(self, data: dict):
        return await utils.run_sync(requests.post, self.api_endpoint, json=data)
