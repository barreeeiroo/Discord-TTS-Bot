import asyncio
import os
import re

import discord
import gtts
from discord.ext import commands
from discord.utils import get

from clips import CLIPS
from db import DB, Admin

PREFIX = '$'
bot = commands.Bot(command_prefix=PREFIX)


def cleanemojis(string):
    return re.sub(r"<a?:([a-zA-Z0-9_-]{1,32}):[0-9]{17,21}>", r":\1:", string)


def get_voiceclient(message):
    voice_client = get(bot.voice_clients, guild=message.guild)
    return voice_client


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name='Barreiro smurfing con Leona'))
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
            DB.save_estadistica(clip)
            if Admin.is_clip_banned_for_user(clip, message.guild.id, message.author.id):
                return
            custom = "clips/" + clip.replace(" ", "") + ".mp3"
            break

    if custom is None:
        c, c_muted = 0, 0
        muted = False
        still_in = False
        for m in voice_channel.members:
            if m.bot:
                continue
            if m.id == user.id:
                still_in = True
                muted = m.voice.self_mute or m.voice.mute
            c += 1
            c_muted += 1 if (m.voice.self_mute or m.voice.mute) else 0

        lang, tld = DB.get_idioma(message.author.id)
        text = message.clean_content

        if still_in and (c < 3 or (muted and c_muted == 1)):
            prefix = ""
        else:
            prefix = (user.nick if user.nick is not None else user.name) + ' dice, '

        tts = gtts.gTTS(prefix + cleanemojis(text), lang=lang, tld=tld)
        custom = "%d.mp3" % message.guild.id
        tts.save(custom)

    vc.play(
        discord.FFmpegPCMAudio(source=custom, executable=os.environ['DISCORD_FFMPEG'], options="-loglevel panic"),
        after=lambda _: os.remove(custom) if not custom.startswith("clips/") else None
    )


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
    embed = discord.Embed(title="Lista de Clips", description="\n".join(CLIPS))
    await ctx.send(embed=embed)


@bot.command(name="lang")
async def lang(ctx, idioma=None, tld=None):
    langs = gtts.lang.tts_langs()
    if idioma is None:
        lang, tld = DB.get_idioma(ctx.author.id)
        embed = discord.Embed(title="Tus Ajustes")
        embed.add_field(name="Idioma", value=("%s (`%s`)" % (langs[lang], lang)), inline=True)
        embed.add_field(name="Dominio", value=tld, inline=True)
        await ctx.send(embed=embed)
        return

    if idioma not in langs:
        embed = discord.Embed(title="Idiomas Soportados")
        for l in langs.keys():
            embed.add_field(name=langs[l], value=l, inline=True)
        await ctx.send("Error localizando el idioma", embed=embed)
        return

    if tld is None:
        tld = "com"
    else:
        with open("./tlds.txt", "r") as f:
            tlds = f.read()
        tlds = tlds.split("\n")
        if tld not in tlds:
            embed = discord.Embed(title="Extensiones TLD Soportadas")
            embed.add_field(name="Google TLDs", value="\n".join(tlds), inline=True)
            await ctx.send("Error localizando el TLD", embed=embed)
            return

    DB.save_idioma(ctx.author.id, idioma, tld)
    embed = discord.Embed(title="Tus Ajustes")
    embed.add_field(name="Idioma", value=("%s (`%s`)" % (langs[idioma], idioma)), inline=True)
    embed.add_field(name="Dominio", value=tld, inline=True)
    await ctx.send("Se ha guardado el idioma por defecto", embed=embed)
    return


@bot.command(name="bans")
async def bans(ctx):
    user = ctx.author.id
    if not Admin.is_user_admin(user):
        await ctx.send("No eres admin perro")
        return

    b = Admin.get_banned(ctx.guild.id)
    embed = discord.Embed(title="Clips Baneados")
    if "_" in b:
        t = ""
        for ban in b["_"]:
            t += ban + "\n"
        embed.add_field(name='Globales', value=t, inline=False)

    for user in b.keys():
        if user == "_":
            continue
        user = await bot.fetch_user(int(user))
        t = ""
        for ban in b[str(user.id)]:
            t += ban + "\n"
        embed.add_field(name=user.name + "#" + user.discriminator + " (" + str(user.id) + ")", value=t, inline=False)
    await ctx.send("Lista de clips baneados", embed=embed)


@bot.command(name="ban")
async def ban(ctx, user=None, clip=None):
    u = ctx.author.id
    if not Admin.is_user_admin(u):
        await ctx.send("No eres admin perro")
        return

    if user is None or clip is None:
        await ctx.send("Usar: $ban [usuario] [clip]")
        return

    if Admin.is_clip_banned_for_user(clip, ctx.guild.id, user):
        await ctx.send("Este clip ya está baneado")
        return

    Admin.ban_clip(clip, ctx.guild.id, user)
    await ctx.send("Clip baneado")


@bot.command(name="unban")
async def unban(ctx, user=None, clip=None):
    u = ctx.author.id
    if not Admin.is_user_admin(u):
        await ctx.send("No eres admin perro")
        return

    if user is None or clip is None:
        await ctx.send("Usar: $unban [usuario] [clip]")
        return

    if not Admin.is_clip_banned_for_user(clip, ctx.guild.id, user):
        await ctx.send("Este clip no está baneado")
        return

    Admin.unban_clip(clip, ctx.guild.id, user)
    await ctx.send("Clip desbaneado")


if __name__ == "__main__":
    DB.iniciar()
    Admin.iniciar()
    bot.run(os.environ['DISCORD_TOKEN'])
