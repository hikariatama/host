#   Coded by D4n13l3k00    #
#     t.me/D4n13l3k00      #
# This code under AGPL-3.0 #

# requires: py-tgcalls

from typing import *

import pytgcalls
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, HighQualityVideo
from telethon import types

from .. import loader, utils


@loader.tds
class ChatVoiceMod(loader.Module):
    """Module for working with voicechat"""

    strings = {
        "name": "ChatVoiceMod",
        "downloading": "<b>[ChatVoiceMod]</b> Downloading...",
        "playing": "<b>[ChatVoiceMod]</b> Playing...",
        "notjoined": "<b>[ChatVoiceMod]</b> You are not joined",
        "stop": "<b>[ChatVoiceMod]</b> Playing stopped!",
        "leave": "<b>[ChatVoiceMod]</b> Leaved!",
        "pause": "<b>[ChatVoiceMod]</b> Paused!",
        "resume": "<b>[ChatVoiceMod]</b> Resumed!",
        "mute": "<b>[ChatVoiceMod]</b> Muted!",
        "unmute": "<b>[ChatVoiceMod]</b> Unmuted!",
        "error": "<b>[ChatVoiceMod]</b> Error: <code>{}</code>",
        "noargs": "<b>[ChatVoiceMod]</b> No args",
    }

    async def client_ready(self, client, _):
        self.client = client
        self.call = PyTgCalls(client)

        @self.call.on_stream_end()
        async def _h(client: PyTgCalls, update):
            try:
                await self.call.leave_group_call(update.chat_id)
            except Exception as e:
                await self.client.send_message(
                    update.chat_id, self.strings("error").format(str(e))
                )

        await self.call.start()

    async def cplayvcmd(self, m: types.Message):
        "<link/path/reply_to_video> - Play video in voice chat"
        try:
            reply = await m.get_reply_message()
            path = utils.get_args_raw(m)
            chat = m.chat.id
            if not path:
                if not reply:
                    return await utils.answer(m, self.strings("noargs"))
                m = await utils.answer(m, self.strings("downloading"))
                path = await reply.download_media()
            try:
                self.call.get_active_call(chat)
                await self.call.leave_group_call(chat)
            except pytgcalls.exceptions.GroupCallNotFound:
                pass
            await self.call.join_group_call(
                chat,
                AudioVideoPiped(
                    path,
                    HighQualityAudio(),
                    HighQualityVideo(),
                ),
                stream_type=StreamType().pulse_stream,
            )
            await utils.answer(m, self.strings("playing"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cplayacmd(self, m: types.Message):
        "<link/path/reply_to_audio> - Play audio in voice chat"
        try:
            reply = await m.get_reply_message()
            path = utils.get_args_raw(m)
            chat = m.chat.id
            if not path:
                if not reply:
                    return await utils.answer(m, self.strings("noargs"))
                m = await utils.answer(m, self.strings("downloading"))
                path = await reply.download_media()
            try:
                self.call.get_active_call(chat)
                await self.call.leave_group_call(chat)
            except pytgcalls.exceptions.GroupCallNotFound:
                pass
            await self.call.join_group_call(
                chat,
                AudioPiped(
                    path,
                    HighQualityAudio(),
                ),
                stream_type=StreamType().pulse_stream,
            )
            await utils.answer(m, self.strings("playing"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cleavecmd(self, m: types.Message):
        "Leave"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.leave_group_call(m.chat.id)
            await utils.answer(m, self.strings("leave"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cmutecmd(self, m: types.Message):
        "Mute"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.mute_stream(m.chat.id)
            await utils.answer(m, self.strings("mute"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cunmutecmd(self, m: types.Message):
        "Unmute"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.unmute_stream(m.chat.id)
            await utils.answer(m, self.strings("unmute"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cpausecmd(self, m: types.Message):
        "Pause"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.pause_stream(m.chat.id)
            await utils.answer(m, self.strings("pause"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))

    async def cresumecmd(self, m: types.Message):
        "Resume"
        try:
            self.call.get_active_call(m.chat.id)
            await self.call.resume_stream(m.chat.id)
            await utils.answer(m, self.strings("resume"))
        except pytgcalls.exceptions.GroupCallNotFound:
            await utils.answer(m, self.strings("notjoined"))
        except Exception as e:
            await utils.answer(m, self.strings("error").format(str(e)))
