import datetime
import json
import random
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from bs4 import BeautifulSoup
import requests
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove

from DAO import DAO

logging.basicConfig(level=logging.INFO)
bot = Bot(token="6854443839:AAGe6vJ9lTJPmI651ysoU8m5hO0x2DRQOy8")
dp = Dispatcher()
database = DAO("users.sqlite")
# 6854443839:AAGe6vJ9lTJPmI651ysoU8m5hO0x2DRQOy8


def updateTime(userId: int):
    curScore = database.getScore(userId)
    curTime = database.getLastActivity(userId)
    newTime = datetime.datetime.now()
    with open("params.json", "r") as params:
        delta = json.load(params)["score_decrease_per_day"]
    database.setScore(userId, max(0, curScore - (newTime - curTime).days * delta))
    database.setLastActivity(userId, newTime)


@dp.message(Command("score"))
async def cmd_start(message: types.Message):
    updateTime(message.from_user.id)
    await message.answer(f"Ваш счет: {database.getScore(message.from_user.id)}")


inlist = ["respect", "base", "home", "pen", "space"]


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    with open("params.json", "r") as params:
        database.addUser(message.from_user.id,
                         json.load(params)["score_for_activity"],
                         datetime.datetime.now())
    await message.answer("Hello!")


def funk5(a):
    word = []
    associations = []
    filterassociations = []

    a = str(a)
    url = "https://wordtools.ai/associations-with/" + a
    page = requests.get(url)
    # print(page.status_code)

    soup = BeautifulSoup(page.text, "html.parser")
    word = soup.findAll('div', class_='lz-def-inline')

    n = str(word[0])
    while n.find('<') != -1:
        n = n.replace(n[n.find('<'):n.find('>') + 1], '')
    n = n.replace(a, '...')
    n = n.replace(a.title(), '...')
    n = n.replace('Full definition', '')
    n = n.replace('""', '')
    n = n.replace('\n', '')

    associations = soup.findAll('div', class_='lz-word-cloud')
    for asso in associations:
        if asso.find("a", class_="lz-tooltip-item"):
            filterassociations.append(asso.text)
    assoti = filterassociations[0].split()
    return (n, assoti)


def funk1(a):
    associations = []
    filterassociations = []
    a = str(a)
    url = "https://wordtools.ai/synonyms-for/" + a
    page = requests.get(url)
    # print(page.status_code)

    soup = BeautifulSoup(page.text, "html.parser")

    associations = soup.findAll('div', class_='lz-word-cloud')
    for asso in associations:
        if asso.find("a", class_="lz-tooltip-item"):
            filterassociations.append(asso.text)
    assoti = filterassociations[0].split()
    return (assoti)


@dp.message(Command("funk5"))
async def cmd_funk5(message: types.Message):
    updateTime(message.from_user.id)
    inlist = ["respect", "base", "home", "pen", "space"]
    in1 = random.choice(inlist)
    k = funk5(in1)[1]
    await message.answer("funk5 start")
    r = random.randint(0, 2)
    f = [k[0], k[1], in1]
    kb = [
        [types.KeyboardButton(text=f[r])],
        [types.KeyboardButton(text=f[r - 1])],
        [types.KeyboardButton(text=f[r - 2])]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(funk5(in1)[0], reply_markup=keyboard)

    @dp.message(F.text.lower() == k[0])
    async def with_puree(message: types.Message):
        curScore = database.getScore(message.from_user.id)
        database.setScore(message.from_user.id, curScore - 1)
        await message.reply("Неверно")

    @dp.message(F.text.lower() == k[1])
    async def without_puree(message: types.Message):
        curScore = database.getScore(message.from_user.id)
        database.setScore(message.from_user.id, curScore - 1)
        await message.reply("Неверно")

    @dp.message(F.text.lower() == in1)
    async def without_puree(message: types.Message):
        curScore = database.getScore(message.from_user.id)
        database.setScore(message.from_user.id, curScore + 1)
        await message.reply("Верно", reply_markup=types.ReplyKeyboardRemove())


class dopfunk1(StatesGroup):
    choosing_word = State()


@dp.message(Command("funk1"))
async def cmd_funk1(message: types.Message, state: FSMContext):
    updateTime(message.from_user.id)
    in1 = random.choice(inlist)
    await message.answer("funk1 start")
    await message.answer(in1)
    await state.set_state(dopfunk1.choosing_word)

    @dp.message(dopfunk1.choosing_word, F.text.in_(funk1(in1)))
    async def with_puree(message: types.Message, state: FSMContext):
        curScore = database.getScore(message.from_user.id)
        database.setScore(message.from_user.id, curScore + 1)
        await state.clear()
        await message.reply("Верно", )

    @dp.message(dopfunk1.choosing_word, ~F.text.in_(funk1(in1)))
    async def with_puree(message: types.Message, state: FSMContext):
        curScore = database.getScore(message.from_user.id)
        database.setScore(message.from_user.id, curScore - 1)
        await message.reply("Неверно")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
