#    Friendly Telegram (telegram userbot) module
#    module author: @anon97945

# requires: numpy scipy noisereduce soundfile pyrubberband

import logging
import numpy as np
import scipy.io.wavfile as wavfile
import os
import subprocess
import noisereduce as nr
import soundfile
import pyrubberband

from io import BytesIO
from pydub import AudioSegment, effects
from .. import loader, utils

logger = logging.getLogger(__name__)


async def getchattype(message):
    chattype = ""
    if message.is_group:
        if message.is_channel:
            chattype = "supergroup"
        else:
            chattype = "smallgroup"
    elif message.is_channel:
        chattype = "channel"
    elif message.is_private:
        chattype = "private"
    return chattype


def represents_nr(nr_lvl):
    try:
        float(nr_lvl)
        if 0.01 <= float(nr_lvl) <= 1:
            return True
        else:
            return False
    except ValueError:
        return False


def represents_pitch(pitch_lvl):
    try:
        float(pitch_lvl)
        if -18 <= float(pitch_lvl) <= 18:
            return True
        else:
            return False
    except ValueError:
        return False


async def audiohandler(bytes_io_file, fn, fe, new_fe, ac, codec):
    # return bytes_io_file, fn, fe, new_fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    out = fn + new_fe
    if not fe == new_fe:
        new_fe_nodot = new_fe[1:]
        with open(fn + fe, "wb") as f:
            f.write(bytes_io_file.getbuffer())
        bytes_io_file.seek(0)
        subprocess.call(
            [
                "ffmpeg",
                "-y",
                "-i",
                fn + fe,
                "-c:a",
                codec,
                "-f",
                new_fe_nodot,
                "-ar",
                "48000",
                "-b:a",
                "320k",
                "-ac",
                ac,
                out,
            ]
        )
        with open(out, "rb") as f:
            bytes_io_file = BytesIO(f.read())
        bytes_io_file.seek(0)
        new_fn, new_fe = os.path.splitext(out)
    if os.path.exists(out):
        os.remove(out)
    if os.path.exists(fn + fe):
        os.remove(fn + fe)
    return bytes_io_file, fn, new_fe


async def audiopitcher(bytes_io_file, fn, fe, pitch_lvl):
    # return bytes_io_file, fn, fe, pitch_lvl
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]
    y, sr = soundfile.read(bytes_io_file)
    y_shift = pyrubberband.pitch_shift(y, sr, pitch_lvl)
    bytes_io_file.seek(0)
    soundfile.write(bytes_io_file, y_shift, sr, format=format_ext)
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    return bytes_io_file, fn, fe


async def audiodenoiser(bytes_io_file, fn, fe, nr_lvl):
    # return bytes_io_file, fn, fe, nr_lvl
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    rate, data = wavfile.read(bytes_io_file)
    reduced_noise = nr.reduce_noise(
        y=data, sr=rate, prop_decrease=nr_lvl, stationary=False
    )
    wavfile.write(bytes_io_file, rate, reduced_noise)
    fn, fe = os.path.splitext(bytes_io_file.name)
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def audionormalizer(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]
    rawsound = AudioSegment.from_file(bytes_io_file, format_ext)
    normalizedsound = effects.normalize(rawsound)
    bytes_io_file.seek(0)
    normalizedsound.export(bytes_io_file, format=format_ext)
    bytes_io_file.name = fn + fe
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


async def dalekvoice(bytes_io_file, fn, fe):
    # return bytes_io_file, fn, fe
    bytes_io_file.seek(0)
    bytes_io_file.name = fn + fe
    format_ext = fe[1:]

    sound = AudioSegment.from_wav(bytes_io_file)
    sound = sound.set_channels(2)
    sound.export(bytes_io_file, format=format_ext)
    bytes_io_file.seek(0)
    VB = 0.2
    VL = 0.4
    H = 4
    LOOKUP_SAMPLES = 1024
    MOD_F = 50

    def diode_lookup(n_samples):
        result = np.zeros((n_samples,))
        for i in range(0, n_samples):
            v = float(i - float(n_samples) / 2) / (n_samples / 2)
            v = abs(v)
            if v < VB:
                result[i] = 0
            elif VB < v <= VL:
                result[i] = H * ((v - VB) ** 2) / (2 * VL - 2 * VB)
            else:
                result[i] = H * v - H * VL + (H * (VL - VB) ** 2) / (2 * VL - 2 * VB)
        return result

    def raw_diode(signal):
        result = np.zeros(signal.shape)
        for i in range(0, signal.shape[0]):
            v = signal[i]
            if v < VB:
                result[i] = 0
            elif VB < v <= VL:
                result[i] = H * ((v - VB) ** 2) / (2 * VL - 2 * VB)
        else:
            result[i] = H * v - H * VL + (H * (VL - VB) ** 2) / (2 * VL - 2 * VB)
        return result

    rate, data = wavfile.read(bytes_io_file)
    data = data[:, 1]
    scaler = np.max(np.abs(data))
    data = data.astype(np.float) / scaler
    n_samples = data.shape[0]
    d_lookup = diode_lookup(LOOKUP_SAMPLES)
    diode = Waveshaper(d_lookup)
    tone = np.arange(n_samples)
    tone = np.sin(2 * np.pi * tone * MOD_F / rate)
    tone = tone * 0.5
    tone2 = tone.copy()
    data2 = data.copy()
    tone = -tone + data2
    data = data + tone2
    data = diode.transform(data) + diode.transform(-data)
    tone = diode.transform(tone) + diode.transform(-tone)
    result = data - tone
    result /= np.max(np.abs(result))
    result *= scaler
    wavfile.write(bytes_io_file, rate, result.astype(np.int16))
    bytes_io_file.name = fn + fe
    fn, fe = os.path.splitext(bytes_io_file.name)
    return bytes_io_file, fn, fe


class Waveshaper:
    def __init__(self, curve):
        self.curve = curve
        self.n_bins = self.curve.shape[0]

    def transform(self, samples):
        # normalize to 0 < samples < 2
        max_val = np.max(np.abs(samples))
        if max_val >= 1.0:
            result = samples / np.max(np.abs(samples)) + 1.0
        else:
            result = samples + 1.0
        result = result * (self.n_bins - 1) / 2
        return self.curve[result.astype(np.int)]


@loader.tds
class voicetoolsMod(loader.Module):
    """Change, pitch, enhance your Voice. Also includes optional automatic mode."""

    strings = {
        "name": "VoiceTools",
        "processing": "<b>[VoiceTools]</b> Message is being processed...",
        "vc_start": "<b>[VoiceTools]</b> Auto VoiceChanger activated.",
        "vc_stopped": "<b>[VoiceTools]</b> Auto VoiceChanger deactivated.",
        "vcanon_start": "<b>[VoiceTools]</b> Auto AnonVoice activated.",
        "vcanon_stopped": "<b>[VoiceTools]</b> Auto AnonVoice deactivated.",
        "nr_start": "<b>[VoiceTools]</b> Auto VoiceEnhancer activated.",
        "nr_stopped": "<b>[VoiceTools]</b> Auto VoiceEnhancer deactivated.",
        "norm_start": "<b>[VoiceTools]</b> Auto VoiceNormalizer activated.",
        "norm_stopped": "<b>[VoiceTools]</b> Auto VoiceNormalizer deactivated.",
        "pitch_start": "<b>[VoiceTools]</b> Auto VoicePitch activated.",
        "pitch_stopped": "<b>[VoiceTools]</b> Auto VoicePitch deactivated.",
        "vtauto_stopped": "<b>[VoiceTools]</b> Auto Voice Tools deactivated.",
        "error_file": "<b>[VoiceTools] No file in the reply detected.</b>",
        "nr_level": ("<b>[VoiceTools]</b> Noise reduction level set to {}."),
        "pitch_level": ("<b>[VoiceTools]</b> Pitch level set to {}."),
        "no_nr": "<b>[VoiceTools]</b> Your input was an unsupported noise reduction level.",
        "no_pitch": "<b>[VoiceTools]</b> Your input was an unsupported pitch level.",
        "audiohandler_txt": "<b>[VoiceTools]</b> Audio is being transcoded.",
        "audiodenoiser_txt": "<b>[VoiceTools]</b> Background noise is being removed.",
        "audionormalizer_txt": "<b>[VoiceTools]</b> Audiovolume is being normalized.",
        "dalekvoice_txt": "<b>[VoiceTools]</b> Dalek Voice is being applied.",
        "pitch_txt": "<b>[VoiceTools]</b> Pitch is being applied.",
        "makewaves_txt": "<b>[VoiceTools]</b> Speech waves are being applied.",
    }

    def __init__(self):
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._me = await client.get_me(True)
        self._id = (await client.get_me(True)).user_id

    async def vtvccmd(self, message):
        """reply to a file to change the voice"""
        chatid = message.chat_id
        if message.is_reply:
            replymsg = await message.get_reply_message()
            if not replymsg.media:
                return await utils.answer(message, self.strings("error_file", message))
        else:
            return
        if not replymsg.file.name:
            filename = "voice"
        else:
            filename = replymsg.file.name
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".opus", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        nr_lvl = 0.8
        await utils.answer(message, self.strings("processing", message))
        await replymsg.client.download_file(replymsg, file)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        await message.edit(self.strings("audiohandler_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        await message.edit(self.strings("audiodenoiser_txt", message))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        await message.edit(self.strings("audionormalizer_txt", message))
        file, fn, fe = await audionormalizer(file, fn, fe)
        file.seek(0)
        await message.edit(self.strings("dalekvoice_txt", message))
        file, fn, fe = await dalekvoice(file, fn, fe)
        file.seek(0)
        await message.edit(self.strings("makewaves_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".opus", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, message)

    async def vtanoncmd(self, message):
        """reply to a file to change the voice into anonymous"""
        chatid = message.chat_id
        if message.is_reply:
            replymsg = await message.get_reply_message()
            if not replymsg.media:
                return await utils.answer(message, self.strings("error_file", message))
        else:
            return
        if not replymsg.file.name:
            filename = "voice"
        else:
            filename = replymsg.file.name
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".opus", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        nr_lvl = 0.8
        pitch_lvl = -7
        await utils.answer(message, self.strings("processing", message))
        await replymsg.client.download_file(replymsg, file)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        await message.edit(self.strings("audiohandler_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        await message.edit(self.strings("audiodenoiser_txt", message))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        await message.edit(self.strings("audionormalizer_txt", message))
        file, fn, fe = await audionormalizer(file, fn, fe)
        file.seek(0)
        await message.edit(self.strings("dalekvoice_txt", message))
        file, fn, fe = await dalekvoice(file, fn, fe)
        file.seek(0)
        file, fn, fe = await audiopitcher(file, fn, fe, float(pitch_lvl))
        file.seek(0)
        await message.edit(self.strings("makewaves_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".opus", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, message)

    async def vtpitchcmd(self, message):
        """reply to a file to pitch voice
        - Example: .vtpitch 12
          Possible values between -18 and 18"""
        chatid = message.chat_id
        if message.is_reply:
            replymsg = await message.get_reply_message()
        else:
            return
        pitch_lvl = utils.get_args_raw(message)
        if not represents_pitch(pitch_lvl):
            return await utils.answer(message, self.strings("no_pitch", message))
        if not replymsg.file.name:
            filename = "voice"
        else:
            filename = replymsg.file.name
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".opus", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        await utils.answer(message, self.strings("processing", message))
        await replymsg.client.download_file(replymsg, file)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        await message.edit(self.strings("audiohandler_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".flac", "1", "flac")
        file.seek(0)
        await message.edit(self.strings("pitch_txt", message))
        file, fn, fe = await audiopitcher(file, fn, fe, float(pitch_lvl))
        file.seek(0)
        await message.edit(self.strings("audionormalizer_txt", message))
        file, fn, fe = await audionormalizer(file, fn, fe)
        file.seek(0)
        await message.edit(self.strings("makewaves_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".opus", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, message)

    async def vtenhcmd(self, message):
        """reply to a file to enhance voice quality with
        - Volume normalize
        - Background NoiseReduce (set your noisereduce level before)"""
        chatid = message.chat_id
        if message.is_reply:
            replymsg = await message.get_reply_message()
            if not replymsg.media:
                return await utils.answer(message, self.strings("error_file", message))
        else:
            return
        if self._db.get(__name__, "nr_lvl") is None:
            nr_lvl = 0.95
        else:
            nr_lvl = float(self._db.get(__name__, "nr_lvl"))
        if not replymsg.file.name:
            filename = "voice"
        else:
            filename = replymsg.file.name
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".opus", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        await utils.answer(message, self.strings("processing", message))
        await replymsg.client.download_file(replymsg, file)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        await message.edit(self.strings("audiohandler_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        await message.edit(self.strings("audiodenoiser_txt", message))
        file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
        file.seek(0)
        await message.edit(self.strings("audionormalizer_txt", message))
        file, fn, fe = await audionormalizer(file, fn, fe)
        file.seek(0)
        await message.edit(self.strings("makewaves_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".opus", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, message)

    async def vtnormcmd(self, message):
        """reply to a file to normalize volume"""
        chatid = message.chat_id
        if message.is_reply:
            replymsg = await message.get_reply_message()
            if not replymsg.media:
                return await utils.answer(message, self.strings("error_file", message))
        else:
            return
        if not replymsg.file.name:
            filename = "voice"
        else:
            filename = replymsg.file.name
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".opus", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        await utils.answer(message, self.strings("processing", message))
        await replymsg.client.download_file(replymsg, file)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        await message.edit(self.strings("audiohandler_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        await message.edit(self.strings("audionormalizer_txt", message))
        file, fn, fe = await audionormalizer(file, fn, fe)
        file.seek(0)
        await message.edit(self.strings("makewaves_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".opus", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, message)

    async def vtmp3cmd(self, message):
        """reply to a file to convert it to mp3"""
        chatid = message.chat_id
        if message.is_reply:
            replymsg = await message.get_reply_message()
            if not replymsg.media:
                return await utils.answer(message, self.strings("error_file", message))
        else:
            return
        if not replymsg.file.name:
            filename = "voice"
        else:
            filename = replymsg.file.name
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".opus", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        await utils.answer(message, self.strings("processing", message))
        await replymsg.client.download_file(replymsg, file)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        await message.edit(self.strings("audiohandler_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file.name = fn + fe
        await message.client.send_file(message.chat_id, file, voice_note=False)
        await message.client.delete_messages(chatid, message)

    async def vtspeechcmd(self, message):
        """reply to a file to convert it to speech"""
        chatid = message.chat_id
        if message.is_reply:
            replymsg = await message.get_reply_message()
            if not replymsg.media:
                return await utils.answer(message, self.strings("error_file", message))
        else:
            return
        if not replymsg.file.name:
            filename = "voice"
        else:
            filename = replymsg.file.name
        ext = replymsg.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".opus", "")
        else:
            filename_new = filename.replace(ext, "")
        file = BytesIO()
        file.name = replymsg.file.name
        await utils.answer(message, self.strings("processing", message))
        await replymsg.client.download_file(replymsg, file)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        await message.edit(self.strings("makewaves_txt", message))
        file, fn, fe = await audiohandler(file, fn, fe, ".opus", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        await message.client.send_file(message.chat_id, file, voice_note=True)
        await message.client.delete_messages(chatid, message)

    async def vtnrlvlcmd(self, message):
        """Set the desired noisereduce level
        - Example: .vtnrlvl 0.8 (Would be 80%)
          Possible values between 0.01 and 1.0"""
        nr_lvl = utils.get_args_raw(message)
        if not represents_nr(nr_lvl):
            return await utils.answer(message, self.strings("no_nr", message))
        self._db.set(__name__, "nr_lvl", nr_lvl)
        await utils.answer(
            message, self.strings("nr_level", message).format(f"{float(nr_lvl):.0%}")
        )

    async def vtpitchlvlcmd(self, message):
        """Set the desired pitch level
        - Example: .vtpitchlvl 12 (Would be 80%)
          Possible values between -18 and 18"""
        pitch_lvl = utils.get_args_raw(message)
        if not represents_pitch(pitch_lvl):
            return await utils.answer(message, self.strings("no_pitch", message))
        self._db.set(__name__, "pitch_lvl", pitch_lvl)
        await utils.answer(
            message, self.strings("pitch_level", message).format(pitch_lvl)
        )

    async def vtautovccmd(self, message):
        """Turns on AutoVoiceChanger for your own Voicemessages in the chat"""
        vc_chats = self._db.get(__name__, "vc_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in vc_chats:
            vc_chats.append(chatid_str)
            self._db.set(__name__, "vc_watcher", vc_chats)
            await utils.answer(message, self.strings("vc_start", message))
        else:
            vc_chats.remove(chatid_str)
            self._db.set(__name__, "vc_watcher", vc_chats)
            await utils.answer(message, self.strings("vc_stopped", message))

    async def vtautoanoncmd(self, message):
        """Turns on AutoAnonVoice for your own Voicemessages in the chat"""
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in vcanon_chats:
            vcanon_chats.append(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
            await utils.answer(message, self.strings("vcanon_start", message))
        else:
            vcanon_chats.remove(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
            await utils.answer(message, self.strings("vcanon_stopped", message))

    async def vtautonrcmd(self, message):
        """Turns on AutoNoiseReduce for your own Voicemessages in the chat"""
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in nr_chats:
            nr_chats.append(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
            await utils.answer(message, self.strings("nr_start", message))
        else:
            nr_chats.remove(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
            await utils.answer(message, self.strings("nr_stopped", message))

    async def vtautonormcmd(self, message):
        """Turns on AutoVoiceNormalizer for your own Voicemessages in the chat"""
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in norm_chats:
            norm_chats.append(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
            await utils.answer(message, self.strings("norm_start", message))
        else:
            norm_chats.remove(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
            await utils.answer(message, self.strings("norm_stopped", message))

    async def vtautopitchcmd(self, message):
        """Turns on AutoVoiceNormalizer for your own Voicemessages in the chat"""
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str not in pitch_chats:
            pitch_chats.append(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
            await utils.answer(message, self.strings("pitch_start", message))
        else:
            pitch_chats.remove(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
            await utils.answer(message, self.strings("pitch_stopped", message))

    async def vtautostopcmd(self, message):
        """Turns off AutoVoice for your own Voicemessages in the chat"""
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        vc_chats = self._db.get(__name__, "vc_watcher", [])
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        chatid = message.chat_id
        chatid_str = str(chatid)
        if chatid_str in norm_chats:
            norm_chats.remove(chatid_str)
            self._db.set(__name__, "norm_watcher", norm_chats)
        if chatid_str in nr_chats:
            nr_chats.remove(chatid_str)
            self._db.set(__name__, "nr_watcher", nr_chats)
        if chatid_str in vc_chats:
            vc_chats.remove(chatid_str)
            self._db.set(__name__, "vc_watcher", vc_chats)
        if chatid_str in pitch_chats:
            pitch_chats.remove(chatid_str)
            self._db.set(__name__, "pitch_watcher", pitch_chats)
        if chatid_str in vcanon_chats:
            vcanon_chats.remove(chatid_str)
            self._db.set(__name__, "vcanon_watcher", vcanon_chats)
        await utils.answer(message, self.strings("vtauto_stopped", message))

    async def watcher(self, message):
        chatid = message.chat_id
        chatid_str = str(chatid)
        norm_chats = self._db.get(__name__, "norm_watcher", [])
        nr_chats = self._db.get(__name__, "nr_watcher", [])
        vc_chats = self._db.get(__name__, "vc_watcher", [])
        pitch_chats = self._db.get(__name__, "pitch_watcher", [])
        vcanon_chats = self._db.get(__name__, "vcanon_watcher", [])
        chat = await message.get_chat()
        chattype = await getchattype(message)
        if (
            chatid_str not in nr_chats
            and chatid_str not in vc_chats
            and chatid_str not in norm_chats
            and chatid_str not in pitch_chats
            and chatid_str not in vcanon_chats
        ):
            return
        if chattype != "channel":
            if message.sender_id != self._id:
                return
        else:
            if not chat.admin_rights.delete_messages:
                return
        if not message.voice:
            return
        if message.via_bot:
            return
        if message.forward:
            return
        if self._db.get(__name__, "nr_lvl") is None:
            nr_lvl = 0.95
        else:
            nr_lvl = float(self._db.get(__name__, "nr_lvl"))
        if self._db.get(__name__, "pitch_lvl") is None:
            pitch_lvl = 8
        else:
            pitch_lvl = float(self._db.get(__name__, "pitch_lvl"))
        if chatid_str in vc_chats:
            nr_lvl = 0.8
        elif chatid_str in vcanon_chats:
            nr_lvl = 0.8
            pitch_lvl = -7
        msgs = await message.forward_to(self._id)
        await message.client.delete_messages(chatid, message)
        file = BytesIO()
        file.name = msgs.file.name
        await message.client.download_file(msgs, file)
        if not msgs.file.name:
            filename = "voice"
        else:
            filename = msgs.file.name
        ext = msgs.file.ext
        if ext == ".oga":
            filename_new = filename.replace(ext, "")
            filename_new = filename.replace(".opus", "")
        else:
            filename_new = filename.replace(ext, "")
        file.seek(0)
        await message.client.delete_messages(self._id, msgs)
        file.name = filename_new + ext
        fn, fe = os.path.splitext(file.name)
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".mp3", "1", "libmp3lame")
        file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".wav", "1", "pcm_s16le")
        file.seek(0)
        if (
            chatid_str in nr_chats
            or chatid_str in vcanon_chats
            or chatid_str in vc_chats
        ):
            file, fn, fe = await audiodenoiser(file, fn, fe, nr_lvl)
            file.seek(0)
        if (
            chatid_str in norm_chats
            or chatid_str in vcanon_chats
            or chatid_str in vc_chats
        ):
            file, fn, fe = await audionormalizer(file, fn, fe)
            file.seek(0)
        if chatid_str in vc_chats or chatid_str in vcanon_chats:
            file, fn, fe = await dalekvoice(file, fn, fe)
            file.seek(0)
        if chatid_str in pitch_chats or chatid_str in vcanon_chats:
            file, fn, fe = await audiopitcher(file, fn, fe, float(pitch_lvl))
            file.seek(0)
        file, fn, fe = await audiohandler(file, fn, fe, ".opus", "2", "libopus")
        file.seek(0)
        file.name = fn + fe
        await message.client.send_file(message.chat_id, file, voice_note=True)
