# requires: requests hentai

import asyncio
import logging

from hentai import Hentai, Utils
from requests.exceptions import HTTPError

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.unrestricted
@loader.ratelimit
@loader.tds
class NHentaiMod(loader.Module):
    """Hentai module 18+"""

    strings = {"name": "NHentai",
               }

    def StringBuilder(self, Hentai):
        id_nh = Hentai.id
        eng_name = Hentai.title()
        link = Hentai.url
        total_pages = Hentai.num_pages
        total_favorites = Hentai.num_favorites
        tags = ""
        for tag in Hentai.tag:
            tags += f"{tag.name} "

        text = f"<a href={link}>{eng_name}</a> [{id_nh}]\n\n"
        text += f"{tags} \n"
        text += f"❤️ {total_favorites} | 📄 {total_pages}"
        return text

    def ListHentaiBuilder(self, Hentais):
        text = ""
        i = 1
        for Hentai in Hentais:
            id_nh = Hentai.id
            eng_name = Hentai.title()
            link = Hentai.url
            total_pages = Hentai.num_pages
            total_favorites = Hentai.num_favorites

            text += f"{i}: <a href={link}>{eng_name}</a> [{id_nh}] / "
            text += f"❤️ {total_favorites} | 📄 {total_pages} \n"
            i += 1
        return text

    @loader.unrestricted
    @loader.ratelimit
    async def nhrandomcmd(self, message):
        """Random hentai manga"""
        await message.delete()
        hentai_info = Utils.get_random_hentai()
        text = self.StringBuilder(hentai_info)

        await message.client.send_file(message.chat_id, hentai_info.cover, caption=text)

    @loader.unrestricted
    @loader.ratelimit
    async def nhtagcmd(self, message):
        """Search hentai manga by tag"""
        args = utils.get_args(message)
        if args:
            hentai_info = Utils.search_by_query(args)
            text = self.ListHentaiBuilder(hentai_info)

            await utils.answer(message, text)
        else:
            await utils.answer(message, "Pls tags")
            await asyncio.sleep(5)
            await message.delete()

    @loader.unrestricted
    @loader.ratelimit
    async def nhidcmd(self, message):
        """Search hentai manga by id"""
        args = utils.get_args(message)
        if args[0].isdigit():
            try:
                hentai_info = Hentai(args[0])
                text = self.StringBuilder(hentai_info)
                await message.client.send_file(message.chat_id, hentai_info.cover, caption=text)
            except HTTPError as e:
                await utils.answer(message, str(e))
                await asyncio.sleep(5)
                await message.delete()
        else:
            await utils.answer(message, "Pls id")
            await asyncio.sleep(5)
            await message.delete()
            