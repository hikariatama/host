# Friendly Telegram (telegram userbot)
# module author: @anon97945

# make sure to install dependencies
# .terminal sudo apt install libsndfile1 gcc ffmpeg rubberband-cli -y

# requires: gtts pydub soundfile pyrubberband numpy AudioSegment subprocess wave re os io

import wave
import re
import os
import sys
import soundfile
import pyrubberband

from gtts import gTTS
from io import BytesIO
from .. import loader, utils
from subprocess import Popen, PIPE
from pydub import AudioSegment, effects


async def audionormalizer(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    rawsound = AudioSegment.from_file(bytes_io_file, "wav")
    normalizedsound = effects.normalize(rawsound)
    bytes_io_file.seek(0)
    normalizedsound.export(bytes_io_file, format="wav")
    bytes_io_file.name = fn + ".wav"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def audiohandler(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    content = bytes_io_file.getvalue()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        "pipe:",
        "-acodec",
        "pcm_s16le",
        "-f",
        "wav",
        "-ac",
        "1",
        "pipe:",
    ]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    bytes_io_file.name = fn + ".wav"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return BytesIO(out), fn, fe if out.startswith(b"RIFF\xff\xff\xff") else None


async def makewaves(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    content = bytes_io_file.getvalue()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        "pipe:",
        "-c:a",
        "libopus",
        "-f",
        "opus",
        "-ac",
        "2",
        "pipe:",
    ]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    bytes_io_file.name = fn + ".opus"
    fn, fe = os.path.splitext(bytes_io_file.name)
    return BytesIO(out), fn, fe


def represents_speed(s):
    try:
        float(s)
        if 0.25 <= float(s) <= 3:
            return True
        else:
            return False
    except ValueError:
        return False


async def speedup(bytes_io_file, fn, fe, speed):
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    y, sr = soundfile.read(bytes_io_file)
    y_stretch = pyrubberband.time_stretch(y, sr, speed)
    y_shift = pyrubberband.pitch_shift(y, sr, speed)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_stretch, sr, format="wav")
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + ".wav"
    return bytes_io_file, fn, fe


@loader.tds
class TTSMod(loader.Module):
    strings = {
        "name": "Text to speech",
        "tts_lang_cfg": "Set your language code for the TTS here.",
        "no_speed": "<b>[TTS]</b> Your input was an unsupported speed value.",
        "needspeed": "You need to provide a speed value between 0.25 and 3.0.",
        "no_reply": "<b>[TTS]</b> You need to reply to a voicemessage.",
        "tts_needs_text": "<b>[TTS]</b> I need some text to convert to speech!",
        "processing": "<b>[TTS]</b> Message is being processed ...",
        "needvoice": "<b>[TTS]</b> This command needs a voicemessage",
        "speech_speed": ("<b>[TTS]</b> Speech speed set to {}x."),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "TTS_LANG", "en", lambda m: self.strings("tts_lang_cfg", m)
        )

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me(True)
        self.id = (await client.get_me(True)).user_id

    @loader.unrestricted
    @loader.ratelimit
    async def ttscmd(self, message):
        """Convert text to speech with Google APIs"""
        if self._db.get(__name__, "speech_speed") is None:
            speed = 1
        else:
            speed = float(self._db.get(__name__, "speech_speed"))
        text = utils.get_args_raw(message.message)
        if len(text) == 0:
            if message.is_reply:
                text = (await message.get_reply_message()).message
            else:
                await utils.answer(message, self.strings("tts_needs_text", message))
                return
        await utils.answer(message, self.strings("processing", message))
        logger.error(self.config["TTS_LANG"])
        tts = await utils.run_sync(gTTS, text, lang=self.config["TTS_LANG"])
        voice = BytesIO()
        await utils.run_sync(tts.write_to_fp, voice)
        voice.seek(0)
        voice.name = "voice.mp3"
        fn, fe = os.path.splitext(voice.name)
        voice, fn, fe = await audiohandler(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await speedup(voice, fn, fe, float(speed))
        voice.seek(0)
        voice, fn, fe = await audionormalizer(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await makewaves(voice, fn, fe)
        voice.seek(0)
        voice.name = fn + fe
        await utils.answer(message, voice, voice_note=True)

    async def speedvccmd(self, message):
        """Speed up voice by x"""
        speed = utils.get_args_raw(message)
        if message.is_reply:
            replymsg = await message.get_reply_message()
            if not replymsg.voice:
                return await utils.answer(message, self.strings("needvoice", message))
        else:
            return await utils.answer(message, self.strings("no_reply", message))
        if len(speed) == 0:
            return await utils.answer(message, self.strings("needspeed", message))
        if not represents_speed(speed):
            return await utils.answer(message, self.strings("no_speed", message))
        await utils.answer(message, self.strings("processing", message))
        ext = replymsg.file.ext
        voice = BytesIO()
        voice.name = replymsg.file.name
        await replymsg.client.download_file(replymsg, voice)
        voice.name = "voice" + ext
        fn, fe = os.path.splitext(voice.name)
        voice.seek(0)
        voice, fn, fe = await audiohandler(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await speedup(voice, fn, fe, float(speed))
        voice.seek(0)
        voice, fn, fe = await audionormalizer(voice, fn, fe)
        voice.seek(0)
        voice, fn, fe = await makewaves(voice, fn, fe)
        voice.seek(0)
        voice.name = fn + fe
        await utils.answer(message, voice, voice_note=True)

    async def ttsspeedcmd(self, message):
        """Set the desired speech speed
        - Example: .ttsspeed 1.5 (Would be 1.5x speed)
          Possible values between 0.25 and 3"""
        speed = utils.get_args_raw(message)
        if not represents_speed(speed):
            return await utils.answer(message, self.strings("no_speed", message))
        self._db.set(__name__, "speech_speed", speed)
        await utils.answer(
            message, self.strings("speech_speed", message).format(str(speed))
        )
