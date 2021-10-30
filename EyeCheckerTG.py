# Based on D4n1l3k300 source code
# t.me/D4n13l3k00
# fastapi by murix (http://api.murix.ru/eye/CheckTG.py)
# xadjilut, 2021
from .. import loader, utils
import requests
def register(cb):
	cb(CheckerTGMod())
class CheckerTGMod(loader.Module):
	"""Eye Checker TG (ГЛ4ЗИК Б0Г4) v1.2"""
	strings = {
		'name': 'EyeCheckerTG',
		'check': '[EYE_API] Делаем запрос к API...',
		'version': '1.2'
		}
	def __init__(self):
		self.name = self.strings['name']
		self._me = None
		self._ratelimit = []
	async def client_ready(self, client, db):
		self._db = db
		self._client = client
		self.me = await client.get_me()
	async def checkcmd(self, m):
		""" Проверить uid на номер
		Отправляет данные в чат
		Жуёт либо <reply>, либо <uid>
		"""
		await check(m, self.strings['check'], self.strings['version'])
	async def pcheckcmd(self, m):
		""" Проверить номер на наличие в бд
		Отправляет данные в чат
		Жуёт либо <reply>, либо <phone>
		"""
		await check(m, self.strings['check'], self.strings['version'], 'p')
	async def scheckcmd(self, m):
		""" Аналогично check
		Отправляет данные в избранное
		Жуёт либо <reply>, либо <uid>
		"""
		await check(m, self.strings['check'], self.strings['version'], save=True)
	async def spcheckcmd(self, m):
		""" Аналогично pcheck
		Отправляет данные в избранное
		Жуёт либо <reply>, либо <phone>
		"""
		await check(m, self.strings['check'], self.strings['version'], 'p', True)

async def check(m, string, version, arg='u', save=False):
	reply = await m.get_reply_message()
	if utils.get_args_raw(m):
		user = utils.get_args_raw(m)
		if arg == 'u' and not user.isnumeric():
			try: user = str((await m.client.get_entity(user)).id)
			except Exception as e: return await m.edit(f"]EYE_API[ <b>Err:</b> {e}")
	elif reply:
		try:
			if arg == 'u':
				user = str(reply.sender.id)
			elif arg == 'p':
				user = reply.contact.phone_number[1:]
		except Exception as e:
			return await m.edit(f"]EYE_API[ <b>Err:</b> {e}")
	else:
		return await m.edit("?EYE_API? А кого чекать?")
	await m.edit(string)
	url_arg = ("uid" if arg == 'u' else "phone")
	resp = await utils.run_sync(
		lambda a, b, c: requests.get('http://api.murix.ru/eye?v=' + a + '&' + b + '=' + c).json()['data'], version, url_arg, user
	)
	if save:
		await m.client.send_message("me", f"[EYE_API] Ответ API: <code>{resp}</code>")
		await m.edit(f"[EYE_API] Ответ API отправлен в избранное!")
	else:
		await m.edit(f"[EYE_API] Ответ API: <code>{resp}</code>")