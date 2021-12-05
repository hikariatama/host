# @Sekai_Yoneya
 
from .. import loader, utils
from telethon.tl.types import * 
 
 
@loader.tds 
class ChatStatisticMod(loader.Module): 
    "Статистика чата" 
    strings = {"name": "ChatStatistic"} 

    async def client_ready(self, client, db):
        self.client = client


    @loader.unrestricted 
    async def statacmd(self, m): 
        """Count messages for current chat"""
        al = str((await self.client.get_messages(m.to_id, limit=0)).total) 
        ph = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterPhotos())).total) 
        vi = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterVideo())).total) 
        mu = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterMusic())).total) 
        vo = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterVoice())).total) 
        vv = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterRoundVideo())).total) 
        do = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterDocument())).total) 
        urls = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterUrl())).total) 
        gifs = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterGif())).total) 
        geos = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterGeo())).total) 
        cont = str((await self.client.get_messages(m.to_id, limit=0, filter=InputMessagesFilterContacts())).total) 
        await utils.answer(m,  
            ("<b>✉️Всего сoообщений</b> {}\n" + 
             "<b>🖼️Фоток:</b> {}\n" + 
             "<b>📹Видосов:</b> {}\n" + 
             "<b>🎵Музыки:</b> {}\n" + 
             "<b>🎶Голосовых:</b> {}\n" + 
             "<b>🎥Кругляшков:</b> {}\n" + 
             "<b>📂Файлов:</b> {}\n" + 
             "<b>🔗Ссылок:</b> {}\n" + 
             "<b>🎞️Гифок:</b> {}\n" + 
             "<b>🗺️Координат:</b> {}\n" + 
             "<b>👭Контактов:</b> {}").format(al, ph, vi, mu, vo, vv, do, urls, gifs, geos, cont))
