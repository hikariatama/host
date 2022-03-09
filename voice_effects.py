"""
    Copyright 2021 t.me/megaass
    Licensed under the Apache License, Version 2.0

    Author is not responsible for any consequencies caused by using this
    software or any of its parts. If you have any questions or wishes, feel
    free to contact owner by sending pm to @megaass.

    Modded and code-refactoring by t.me/innocoffee
"""

from pydub import AudioSegment
from .. import loader, utils
from telethon import types
import io
import requests

# requires: pydub

overlays = {}


async def create_overlay(message, reply):
    args = utils.get_args_raw(message).split()
    if args:
        overlay = args[0]
        vol = args[1] if len(args) > 1 else ""
        vol = 100 - min(int(vol), 99) if vol and vol.isdigit() else 100
    else:
        overlay = "pablo"

    if overlay not in overlays:
        overlay = overlays.keys()[0]

    voice = io.BytesIO()
    await reply.download_media(voice)
    voice.seek(0)
    voice = AudioSegment.from_file(voice)

    biogr = io.BytesIO(overlays[overlay])
    biogr.seek(0)
    biogr = AudioSegment.from_file(biogr)[: len(voice)] - vol

    out = biogr.overlay(voice, position=0)
    output = io.BytesIO()
    output.name = f"{overlay}.ogg"
    out.export(output, format="ogg", bitrate="64k", codec="libopus")
    output.seek(0)

    return output, out


class MinusMod(loader.Module):
    """Add voice overlays over messages"""

    strings = {
        "name": "VoiceEffects",
        "downloading": "<b>Downloading</b>",
        "no_audio": "<b>You need to reply to audio</b>",
    }

    async def client_ready(self, client, db):
        global overlays
        overlays = {
            "pablo": (
                await utils.run_sync(requests.get, "https://x0.at/9z_9.mp3")
            ).content,
            "kids": (
                await utils.run_sync(requests.get, "https://x0.at/4bfh.mp3")
            ).content,
            "camry": (
                await utils.run_sync(requests.get, "https://x0.at/W8ui.mp3")
            ).content,
            "gta": (
                await utils.run_sync(requests.get, "https://x0.at/KCkV.mp3")
            ).content,
            "amogus": (
                await utils.run_sync(requests.get, "https://x0.at/wPms.mp3")
            ).content,
            "chill": (
                await utils.run_sync(requests.get, "https://x0.at/JBs4.mp3")
            ).content,
        }

    async def handle_message(self, message):
        reply = await message.get_reply_message()
        if not reply or not reply.file or not reply.file.mime_type.startswith("audio"):
            return await utils.answer(message, self.strings("no_audio"))

        await utils.answer(message, self.strings("downloading"))
        output, out = await create_overlay(message, reply)
        await message.client.send_file(
            message.to_id,
            output,
            reply_to=reply.id,
            voice_note=True,
            duration=len(out) / 1000,
        )
        await message.delete()

    async def sfcmd(self, message):
        """(in reply to voice) <pablo|kids|camry|gta|amogus|chill> [volume]"""
        return await self.handle_message(message)
