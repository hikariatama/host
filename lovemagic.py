import random
from .. import utils, loader
from asyncio import sleep

@loader.tds
class ILYMod(loader.Module):
	"""Famous TikTok hearts animation implemented in FTG"""
	strings = {
		"name": "LoveMagic"
	}	
	
	async def ilycmd(self, message: "telethon.tl.types.Message") -> None:
		"""This famous TikTok animation..."""
		if not message.out:
			message = await message.respond('ily')

		arr = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🤎", "🤍", "💖"]
		h = "🖤"
		first_block = ""		
		for i in "".join([
				h * 9, "\n",
				h * 2, arr[0] * 2, h, arr[0] * 2, h * 2, "\n",
				h, arr[0] * 7, h, "\n",
				h, arr[0] * 7, h, "\n",
				h, arr[0] * 7, h, "\n",
				h * 2, arr[0] * 5, h * 2, "\n",
				h * 3, arr[0] * 3, h * 3, "\n",
				h * 4, arr[0], h * 4]).split("\n"):
			first_block += i + "\n"
			await message.edit(first_block)
			await sleep(0.1)		
		for i in arr:
			await message.edit("".join([
				h * 9, "\n",
				h * 2, i * 2, h, i * 2, h * 2, "\n",
				h, i * 7, h, "\n",
				h, i * 7, h, "\n",
				h, i * 7, h, "\n",
				h * 2, i * 5, h * 2, "\n",
				h * 3, i * 3, h * 3, "\n",
				h * 4, i, h * 4, "\n",
				h * 9]))
			await sleep(0.2)
		for _ in range(8):
			rand = random.choices(arr, k=34)
			await message.edit("".join([
				h * 9, "\n",
				h * 2, rand[0], rand[1], h, rand[2], rand[3], h * 2, "\n",
				h, rand[4], rand[5], rand[6], rand[7], rand[8],rand[9],rand[10], h, "\n",
				h, rand[11], rand[12], rand[13], rand[14], rand[15], rand[16],rand[17], h, "\n",
				h, rand[18], rand[19], rand[20], rand[21], rand[22], rand[23],rand[24], h, "\n",
				h * 2, rand[25], rand[26], rand[27], rand[28], rand[29], h*2, "\n",
				h * 3, rand[30], rand[31], rand[32], h * 3, "\n",
				h * 4, rand[33], h * 4, "\n",
				h * 9]))
			await sleep(0.2)
		fourth = "".join([
			h * 9, "\n",
			h * 2, arr[0] * 2, h, arr[0] * 2, h * 2, "\n",
			h, arr[0] * 7, h, "\n",
			h, arr[0] * 7, h, "\n",
			h, arr[0] * 7, h, "\n",
			h * 2, arr[0] * 5, h * 2, "\n",
			h * 3, arr[0] * 3, h * 3, "\n",
			h * 4, arr[0], h * 4, "\n",
			h * 9])
		await message.edit(fourth)
		for _ in range(47):
			fourth = fourth.replace("❤️", "🖤", 1)
			await message.edit(fourth)
			await sleep(0.07)
		for i in range(8):
			await message.edit((arr[0] * (8 - i) + "\n") * (8 - i))
			await sleep(0.3)
		for i in ["Я", "Я тебя", "Я тебя 🖤", "Я тебя 🖤!"]:
			await message.edit(f"<b>{i}</b>")
			await sleep(0.2)
