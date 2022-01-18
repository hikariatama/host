#   Coded by D4n13l3k00    #
#     t.me/D4n13l3k00      #
# This code under AGPL-3.0 #

# requires: aiohttp pydantic

import asyncio
import io
import logging
from typing import *
from datetime import datetime, timedelta
import aiohttp
import pydantic
import telethon
from telethon import types
from telethon.events import ChatAction
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

from .. import loader, utils


@loader.tds
class CaptchaMod(loader.Module):
    'Captcha for chats'

    strings = {
        'name':'Captcha',
        'pls_pass_captcha': '<a href="tg://user?id={}">Хэй</a>, пройди капчу! У тебя одна попытка\nИначе получишь бан на 5 минут!',
        'captcha_status': '<b>[Capthca]</b> {}'
    }
    
    class CUserModel(pydantic.BaseModel):
        chat: int
        user: int
        message: int
        answer: str
        
    async def client_ready(self, _, db):
        self.db = db
        self.log = logging.getLogger(__name__)
        self._db = 'CaptchaMod'
        self.locked_users: List[self.CUserModel] = []
        
    async def watcher(self, m):
        'Watcher'
        client: telethon.TelegramClient = m.client
        if isinstance(m, ChatAction.Event):
            if m.chat_id not in self.db.get(self._db, 'chats', []):
                return
            if m.user_added or m.user_joined:
                users = [i.id for i in m.users]
                for u in users:
                    _u = await client.get_entity(u)
                    if _u.bot:
                        continue
                    async with aiohttp.ClientSession() as s, s.get('https://api.d4n13l3k00.ru/captcha/generate') as r:
                        answer = r.headers['Captcha-Code']
                        im = io.BytesIO(await r.read())
                        im.name = '@DekFTGModules_catpcha.png'
                        m = await client.send_file(m.chat, im, caption=self.strings('pls_pass_captcha').format(u))
                        self.locked_users.append(self.CUserModel(chat=m.chat_id, user=u, message=m.id, answer=answer))
                await asyncio.sleep(60)
                l: List[self.CUserModel] = list(filter(lambda x: x.chat == m.chat_id and x.user in users, self.locked_users))
                if l:
                    for u in l:
                        self.locked_users.remove(u)
                        await (await client.get_messages(u.chat, ids=u.message)).delete()
                        await client(EditBannedRequest(u.chat, u.user, ChatBannedRights(
                            until_date=None,
                            view_messages=True
                        )))
            elif m.user_kicked or m.user_left:
                users = [i.id for i in m.users]
                for u in users:
                    l: List[self.CUserModel] = list(filter(lambda x: x.chat == m.chat_id and x.user == u, self.locked_users))
                    if l:
                        ntt = l[0]
                        self.locked_users.remove(ntt)
                        return
        
        if isinstance(m, types.Message):
            client: telethon.TelegramClient = m.client
            l: List[self.CUserModel] = list(filter(lambda x: x.chat == m.chat_id and x.user == m.sender_id, self.locked_users))
            if l:
                ntt = l[0]
                self.locked_users.remove(ntt)
                await (await client.get_messages(ntt.chat, ids=ntt.message)).delete()
                await m.delete()
                if ntt.answer.lower() != m.raw_text.lower():
                    await client(EditBannedRequest(ntt.chat, ntt.user, ChatBannedRights(
                        until_date=None,
                        view_messages=True
                    )))
                
    async def swcaptchacmd(self, m: types.Message):
        'Turn on/off captha in chat'
        l: list = self.db.get(self._db, 'chats', [])
        if m.chat_id in l:
            l.remove(m.chat_id)
            self.db.set(self._db, 'chats', l)
            return await utils.answer(m, self.strings('captcha_status').format('OFF'))
        l.append(m.chat_id)
        self.db.set(self._db, 'chats', l)
        await utils.answer(m, self.strings('captcha_status').format('ON'))
