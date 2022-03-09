# for more info: https://murix.ru/files/ftg
# by xadjilut, 2021

import random
import re

from .. import loader, utils
from telethon.tl.types import Message, Channel


@loader.tds
class CensorMod(loader.Module):
    """Фильтр обсценной лексики на регуляр очке на каждый день"""

    strings = {
        "name": "censor",
        "censor_cmd": "Читай <code>.help censor</code>",
        "cens_yes": "❌<b>Мат не нужен, редиска обнаружен</b>\n\n%text%",
        "cens_no": "👌<b>Мат не найден</b>\n\n",
        "cens_null": "❓<b>А что проверять?</b>",
        "censon_not_admin": "🙈<b>Не могу удалять чужие посты в этом чате</b>",
        "censon_invalid": "❗️<b>Невалидный юзернейм</b>",
        "censon_cmd_1": "🔒<b>Фильтрация мата включена в чате с айди</b> <code>%id%</code>",
        "censon_cmd_2": "👮<b>Глобальная фильтрация мата включена в чате с айди</b> <code>%id%</code>",
        "censoff_cmd": "🔌<b>Фильтрация мата отключена в чате с айди</b> <code>%id%</code>",
        "censoff_all": "🔌<b>Фильтрация мата отключена во всех чатах</b>",
        "censlist_cmd": "📃<b>Где фильтрую мат:</b>\n\n%list%",
        "censlist_empty": "🔌<b>Нигде не фильтрую мат.</b>",
        "censx_cmd": "📄<b>Кастомные исключения для фильтра:</b>\n\n%list%",
        "censx_add": "📝<b>Исключения добавлены</b>",
        "censx_del": "🗑<b>Исключения удалены</b>",
        "censx_empty": "🗑<b>Нет кастомных исключений</b>",
        "censx_invalid": "🐵<b>Непонел, ну лан</b>",
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.me_id = (await client.get_me()).id

    async def censorcmd(self, message):
        """Нулевой указатель, редирект на справку"""
        await message.edit(self.strings["censor_cmd"])

    async def censcmd(self, message):
        """.cens <reply>|<text>
        Проверка фильтра обсценной лексики"""
        args = utils.get_args_raw(message)
        if not message.is_reply and not args:
            return await message.edit(self.strings["cens_null"])
        if message.is_reply:
            reply = await message.get_reply_message()
            raw_text = reply.raw_text
        else:
            raw_text = args
        exc = self.db.get(self.name, "exc", [])
        censtext = OCR.filterText(raw_text, exc=exc)
        if raw_text != censtext:
            await message.edit(self.strings["cens_yes"].replace("%text%", censtext))
        else:
            await message.edit(
                self.strings["cens_no"] + (censtext if not message.is_reply else "")
            )

    async def censlistcmd(self, message):
        """Выводит список айди чатов, в которых работает фильтрация"""
        ids = dict(self.db).get(self.name)
        if not ids:
            return await message.edit(self.strings["censlist_empty"])
        censlist = [
            f'<code>{x}</code>{"*" if ids[x]==2 else ""}'
            for x in ids
            if isinstance(x, int) and ids[x] > 0
        ]
        if not censlist:
            return await message.edit(self.strings["censlist_empty"])
        answer = " ".join(censlist)
        await message.edit(self.strings["censlist_cmd"].replace("%list%", answer))

    async def censoncmd(self, message):
        """.censon [<id>|<username>|*]
        Запуск фильтрации в том чате, куда отправлена команда
        Можно запустить в любом чате по id или username
        * запускает на все сообщения в текущем чате (по умолчанию на свои)"""
        args = utils.get_args_raw(message)
        if args == "*":
            chat = message.chat
            if (
                not isinstance(chat, Channel)
                or not chat.admin_rights
                or not chat.admin_rights.delete_messages
            ):
                return await message.edit(self.strings["censon_not_admin"])
            flag = 2
            args = args[:-1]
        else:
            flag = 1
        if not args:
            id = utils.get_chat_id(message)
        elif args.isnumeric():
            id = int(args)
        else:
            try:
                id = (await self.client.get_entity(args)).id
            except Exception:
                return await message.edit(self.strings["censon_invalid"])
        self.db.set(self.name, id, flag)
        await message.edit(self.strings[f"censon_cmd_{flag}"].replace("%id%", str(id)))

    async def censoffcmd(self, message):
        """.censoff [<id>|<username>|all]
        Остановка фильтрации в том чате, куда отправлена команда
        Можно остановить в любом чате по id или username
        all останавливает фильтрацию во всех чатах"""
        args = utils.get_args_raw(message)
        if args == "all":
            exc = self.db.get(self.name, "exc", [])
            del self.db[self.name]
            self.db.set(self.name, "exc", exc)
            return await message.edit(self.strings["censoff_all"])
        if not args:
            id = utils.get_chat_id(message)
        elif args.isnumeric():
            id = int(args)
        else:
            try:
                id = (await self.client.get_entity(args)).id
            except Exception:
                return await message.edit(self.strings["censon_invalid"])
        self.db.set(self.name, id, 0)
        await message.edit(self.strings["censoff_cmd"].replace("%id%", str(id)))

    async def censxcmd(self, message):
        """.censx [+ <text>|-]
        Добавляет и удаляет кастомные исключения для фильтра
        Исключения в text записывать чеpез пробел
        Команда без аргументов выводит список кастомных исключений"""
        args = utils.get_args(message)
        if len(args) == 1 and args[0] == "-":
            self.db.set(self.name, "exc", [])
            return await message.edit(self.strings["censx_del"])
        if len(args) > 1 and args[0] == "+":
            self.db.set(self.name, "exc", [x.lower() for x in args[1:]])
            return await message.edit(self.strings["censx_add"])
        if not args:
            exc = self.db.get(self.name, "exc", [])
            if not exc:
                return await message.edit(self.strings["censx_empty"])
            return await message.edit(
                self.strings["censx_cmd"].replace(
                    "%list%", " ".join([f"<code>{x}</code>" for x in exc])
                )
            )
        await message.edit(self.strings["censx_invalid"])

    async def watcher(self, event):
        if not isinstance(event, Message):
            return
        id = utils.get_chat_id(event)
        flag = self.db.get(self.name, id, 0)
        if not flag or (flag == 1 and event.sender_id != self.me_id):
            return
        exc = self.db.get(self.name, "exc", [])
        censtext = OCR.filterText(event.raw_text, exc=exc)
        if censtext == event.raw_text:
            return
        message = event
        try:
            await event.delete()
        except Exception:
            chat = message.chat
            if (
                not isinstance(chat, Channel)
                or not chat.admin_rights
                or not chat.admin_rights.delete_messages
            ):
                self.db.set(self.name, id, 1)
                return await message.answer(self.strings["censon_not_admin"])
        if flag == 2 and event.sender_id != self.me_id:
            return
        message.text = censtext
        await self.client.send_message(id, event, reply_to=message.reply_to_msg_id)


class OCR:

    # это не оптическое распознавание изображений, это сокращение от ObsceneCensorRus
    # спиздил код отсюда: https://github.com/vearutop/php-obscene-censor-rus
    # и всё переписал на питоне, все права защищены, хули
    # by xadjilut, 2021

    LT_P = "пПnPp"
    LT_I = "иИiI1uІИ́Їіи́ї"
    LT_E = "еЕeEЕ́е́"
    LT_D = "дДdD"
    LT_Z = "зЗ3zZ3"
    LT_M = "мМmM"
    LT_U = "уУyYuUУ́у́"
    LT_O = "оОoO0О́о́"
    LT_L = "лЛlL"
    LT_S = "сСcCsS"
    LT_A = "аАaAА́а́"
    LT_N = "нНhH"
    LT_G = "гГgG"
    LT_CH = "чЧ4"
    LT_K = "кКkK"
    LT_C = "цЦcC"
    LT_R = "рРpPrR"
    LT_H = "хХxXhH"
    LT_YI = "йЙy"
    LT_YA = "яЯЯ́я́"
    LT_YO = "ёЁ"
    LT_YU = "юЮЮ́ю́"
    LT_B = "бБ6bB"
    LT_T = "тТtT"
    LT_HS = "ъЪ"
    LT_SS = "ьЬ"
    LT_Y = "ыЫ"

    exceptions = (
        "команд",
        "рубл",
        "премь",
        "оскорб",
        "краснояр",
        "бояр",
        "ноябр",
        "карьер",
        "мандат",
        "употр",
        "плох",
        "интер",
        "веер",
        "фаер",
        "феер",
        "hyundai",
        "тату",
        "браконь",
        "roup",
        "сараф",
        "держ",
        "слаб",
        "ридер",
        "истреб",
        "потреб",
        "коридор",
        "sound",
        "дерг",
        "подоб",
        "коррид",
        "дубл",
        "курьер",
        "экст",
        "try",
        "enter",
        "oun",
        "aube",
        "ibarg",
        "16",
        "kres",
        "глуб",
        "ebay",
        "eeb",
        "shuy",
        "ансам",
        "cayenne",
        "ain",
        "oin",
        "тряс",
        "ubu",
        "uen",
        "uip",
        "oup",
        "кораб",
        "боеп",
        "деепр",
        "хульс",
        "een",
        "ee6",
        "ein",
        "сугуб",
        "карб",
        "гроб",
        "лить",
        "рсук",
        "влюб",
        "хулио",
        "ляп",
        "граб",
        "ибог",
        "вело",
        "ебэ",
        "перв",
        "eep",
        "ying",
        "laun",
        "чаепитие",
        "озлоб",
        "козолуп",
        "грёб",
        "греб",
        "теб",
        "себ",
        "мандарин",
        "сабля",
        "колеб",
        "облит",
        "собл",
        "хула",
        "хульн",
        "дробл",
        "оглобл",
        "глазолуп",
        "двое",
        "трое",
        "ябед",
        "яблон",
        "яблоч",
        "ипостас",
        "скипидар",
        "ветхую",
        "бляш",
        "хулит",
        "епископ",
        "хулив",
    )

    @staticmethod
    def filterText(text, charset="UTF-8", exc=()):
        utf8 = "UTF-8"

        if charset != utf8:
            text = text.decode(charset).encode(utf8)
            m = re.findall(
                r"\b\d*("
                "\w*["
                + OCR.LT_P
                + "]["
                + OCR.LT_I
                + OCR.LT_E
                + "]["
                + OCR.LT_Z
                + "]["
                + OCR.LT_D
                + "]\w*"  # пизда
                "|(?:[^"
                + OCR.LT_I
                + OCR.LT_U
                + "\s]+|"
                + OCR.LT_N
                + OCR.LT_I
                + ")?(?<!стра)["
                + OCR.LT_H
                + "]["
                + OCR.LT_U
                + "]["
                + OCR.LT_YI
                + OCR.LT_E
                + OCR.LT_YA
                + OCR.LT_YO
                + OCR.LT_I
                + OCR.LT_L
                + OCR.LT_YU
                + "](?!иг)\w*"  # хуй; не пускает "подстрахуй", "хулиган"
                "|\w*["
                + OCR.LT_B
                + "]["
                + OCR.LT_L
                + "](?:["
                + OCR.LT_YA
                + "]+["
                + OCR.LT_D
                + OCR.LT_T
                + "]?"
                "|[" + OCR.LT_I + "]+[" + OCR.LT_D + OCR.LT_T + "]+"
                "|["
                + OCR.LT_I
                + "]+["
                + OCR.LT_A
                + "]+)(?!х)\w*"  # бля, блядь; не пускает "бляха"
                "|(?:\w*["
                + OCR.LT_YI
                + OCR.LT_U
                + OCR.LT_E
                + OCR.LT_A
                + OCR.LT_O
                + OCR.LT_HS
                + OCR.LT_SS
                + OCR.LT_Y
                + OCR.LT_YA
                + "]["
                + OCR.LT_E
                + OCR.LT_YO
                + OCR.LT_YA
                + OCR.LT_I
                + "]["
                + OCR.LT_B
                + OCR.LT_P
                + "](?!ы\b|ол)\w*"  # не пускает "еёбы", "наиболее", "наибольшее"...
                "|[" + OCR.LT_E + OCR.LT_YO + "][" + OCR.LT_B + "]\w*"
                "|[" + OCR.LT_I + "][" + OCR.LT_B + "][" + OCR.LT_A + "]\w+"
                "|["
                + OCR.LT_YI
                + "]["
                + OCR.LT_O
                + "]["
                + OCR.LT_B
                + OCR.LT_P
                + "]\w*)"  # ебать
                #'|\w*[' + OCR.LT_S + '][' + OCR.LT_C + ']?[' + OCR.LT_U + ']+(?:[' + OCR.LT_CH + ']*[' + OCR.LT_K + ']+'
                #'|[' + OCR.LT_CH + ']+[' + OCR.LT_K + ']*)[' + OCR.LT_A + OCR.LT_O + ']\w*' # сука
                "|\w*(?:["
                + OCR.LT_P
                + "]["
                + OCR.LT_I
                + OCR.LT_E
                + "]["
                + OCR.LT_D
                + "]["
                + OCR.LT_A
                + OCR.LT_O
                + OCR.LT_E
                + "]?["
                + OCR.LT_R
                + "](?!о)\w*"  # не пускает "Педро"
                "|["
                + OCR.LT_P
                + "]["
                + OCR.LT_E
                + "]["
                + OCR.LT_D
                + "]["
                + OCR.LT_E
                + OCR.LT_I
                + "]?["
                + OCR.LT_G
                + OCR.LT_K
                + "])"  # пидарас
                "|\w*["
                + OCR.LT_Z
                + "]["
                + OCR.LT_A
                + OCR.LT_O
                + "]["
                + OCR.LT_L
                + "]["
                + OCR.LT_U
                + "]["
                + OCR.LT_P
                + "]\w*"  # залупа
                "|\w*["
                + OCR.LT_M
                + "]["
                + OCR.LT_A
                + "]["
                + OCR.LT_N
                + "]["
                + OCR.LT_D
                + "]["
                + OCR.LT_A
                + OCR.LT_O
                + "]\w*"  # манда
                "|\w*["
                + OCR.LT_G
                + "]["
                + OCR.LT_O
                + OCR.LT_A
                + "]["
                + OCR.LT_N
                + "]["
                + OCR.LT_D
                + "]["
                + OCR.LT_O
                + "]["
                + OCR.LT_N
                + "]\w*"  # гондон
                ")",
                text,
            )

        c = len(m)

        # exclusion=array('хлеба','наиболее');
        # m[1]=array_diff($m[1],$exclusion);

        if c:
            i = 0
            xwords = []
            while i < c:
                # if i >= c: break
                word_orig = m[i]
                word = word_orig.lower()

                for x in OCR.exceptions + tuple(exc):
                    if x in word:
                        word = False
                        del m[i]
                        xwords.append(word_orig)
                        i -= 1
                        c -= 1
                        break

                if word:
                    m[i] = "".join(
                        [
                            (
                                ""
                                if x in (" ", ",", ";", ".", "!", "-", "?", "\t", "\n")
                                else x
                            )
                            for x in list(m[i])
                        ]
                    )

                i += 1

            m = set(m)

            asterisks = ["*" * len(word) for word in m]
            _xwords = " ".join(xwords)
            for x, y in zip(m, asterisks):
                text = text.replace(x, y)
                _xwords = _xwords.replace(x, y)

            for x, y in zip(_xwords.split(), xwords):
                text = text.replace(x, y)

        return text
