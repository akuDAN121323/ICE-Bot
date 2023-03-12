import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from keepalive import keep_alive

intents = discord.Intents(guilds=True, members=True, messages=True)
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   intents=intents)

# ID channel untuk memberikan notifikasi saat bot ditambahkan ke server
NOTIF_CHANNEL_ID = 1083646119621431296  # Ganti dengan ID channel yang diinginkan


@bot.event
async def on_ready():
    print('Bot is ready!')
    # Kirim pesan ke channel saat bot siap
    channel = bot.get_channel(NOTIF_CHANNEL_ID)
    await channel.send("I'm ready!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        # mengirim pesan ke user bahwa command sedang cooldown
        await ctx.send(
            f'This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.'
        )
    elif isinstance(error, discord.errors.HTTPException) and error.code == 429:
        # menunggu beberapa waktu dan mencoba kembali setelah warning rate limit selesai
        await asyncio.sleep(error.retry_after)
        await ctx.reinvoke()
    else:
        # menampilkan error lainnya
        raise error


@bot.command()
async def setup(message):
    # Menghapus voice channel sebelumnya yang dibuat oleh bot
    voice_channels = message.guild.voice_channels
    for channel in voice_channels:
        if channel.name.endswith('WIB'):
            await channel.delete()

    # Membuat voice channel baru dengan nama yang disesuaikan
    now = datetime.utcnow()
    wib_time = now + timedelta(hours=7)
    voice_channel_name = f"{now.strftime('%H:%M')} UTC - {wib_time.strftime('%H:%M')} WIB"
    overwrites = {
        message.guild.default_role: discord.PermissionOverwrite(connect=False)
    }
    voice_channel = await message.guild.create_voice_channel(
        name=voice_channel_name, overwrites=overwrites, position=0)

    # Memulai task untuk memperbarui judul voice channel setiap menit
    @tasks.loop(seconds=600)
    async def update_voice_channel_task():
        try:
            now = datetime.utcnow()
            wib_time = now + timedelta(hours=7)
            voice_channel_name = f"{now.strftime('%H:%M')} UTC - {wib_time.strftime('%H:%M')} WIB"
            await voice_channel.edit(name=voice_channel_name)
        except discord.errors.HTTPException as e:
            if e.code == 429:
                await asyncio.sleep(e.retry_after)
                await voice_channel.edit(name=voice_channel_name)
            else:
                raise e

    update_voice_channel_task.start()


@bot.command()
async def regist(message, *, new_nickname):
    try:
        # Ubah nickname user
        new_nickname = f'[ICE] {new_nickname}'
        await message.author.edit(nick=new_nickname)
        await message.channel.send(f'Nickname has been changed to "{new_nickname}"')
    except discord.errors.Forbidden:
        await message.channel.send("I don't have permission to change your nickname.")
    except discord.errors.HTTPException as e:
        await message.channel.send(f"An error occurred: {e}")


@bot.event
async def on_guild_join(guild):
  # Kirim pesan ke channel saat bot ditambahkan ke server
  channel = bot.get_channel(NOTIF_CHANNEL_ID)
  await channel.send(f"I've been added to the server: {guild.name}")


keep_alive()  # Panggil fungsi keep_alive dari modul keepalive.py
bot.run(os.getenv(
  'DISCORD_TOKEN'))  # Jalankan bot dengan token dari environment variable
