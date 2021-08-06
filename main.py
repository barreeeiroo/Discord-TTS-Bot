import asyncio
import os
import re

import discord
from discord.ext import commands
from discord.utils import get
from gtts import gTTS

PREFIX = '$'
bot = commands.Bot(command_prefix=PREFIX)

CLIPS = [
    "top enemigo",
    "faker what was that",
    "son robots",
    "im a problem",
    "todos los dias igual",
    "autoataques",
    "matale",
    "cliente de mierda",
    "my team is so bad",
    "que haces putita",
    "rock solid",
    "tengo furbo",
    "chao concha",
    "puse el turbo",
    "con los terrorista",
    "no mana",
    "demacia",
    "golaso",
    "we got him",
    "vamo a juga",
    "nasus is stacking",
    "pmp",
    "atras",
    "we smell pennies",
    "hacen cosas",
    "somos sentimientos",
    "hacemos lo que podemos",
    "es el vecino",
    "venga adelante",
    "mucho espanoles",
    "piensan antes",
    "vaso",
    "cuanto peor mejor"
]


def cleanemojis(string):
    return re.sub(r"<a?:([a-zA-Z0-9_-]{1,32}):[0-9]{17,21}>", r":\1:", string)


def get_voiceclient(message):
    voice_client = get(bot.voice_clients, guild=message.guild)
    return voice_client


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Mudi Inteando'))
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        # Ignore self messages
        return

    if not message.guild:
        # Ignore private messages
        return

    if message.content.startswith(PREFIX):
        # If command, process it as it should be
        await bot.process_commands(message)
        return

    vc = get_voiceclient(message)
    if not vc or not vc.is_connected():
        # If no voice channel, ignore
        return

    user = message.author
    if not user.voice or not user.voice.channel:
        # If user is not in voice channel, ignore
        return

    voice_channel = user.voice.channel
    if voice_channel != vc.channel:
        # Only play if in the same voice channel
        return

    if "tts" not in message.channel.name.lower():
        # Only accept messages in tts channel
        return

    if message.clean_content.startswith("http"):
        # Ignorar enlaces
        return

    while vc.is_playing():
        await asyncio.sleep(0.1)

    custom = None
    for clip in CLIPS:
        if message.clean_content.lower() == clip:
            custom = "clips/" + clip.replace(" ", "") + ".mp3"
            break

    if custom is None:
        tts = gTTS((user.nick if user.nick is not None else user.name) + ' dice, ' + cleanemojis(message.clean_content), lang='es', tld='es')
        tts.save("msg.mp3")
        custom = "msg.mp3"

    vc.play(discord.FFmpegPCMAudio(source=custom, executable=os.environ['DISCORD_FFMPEG'], options="-loglevel panic"))


@bot.command(name="ven")
async def ven(ctx):
    connected = ctx.author.voice
    if not connected:
        await ctx.send("Pero tu que eres, tonto? Métete en un canal de voz antes de decirme nah")
        return
    await connected.channel.connect()


@bot.command(name="vete")
async def vete(ctx):
    vc = get_voiceclient(ctx)
    if not vc or not vc.is_connected():
        # If no voice channel, ignore
        return
    await vc.disconnect()


@bot.command(name="clips")
async def clips(ctx):
    await ctx.send("\n".join(CLIPS))


if __name__ == "__main__":
    bot.run(os.environ['DISCORD_TOKEN'])
