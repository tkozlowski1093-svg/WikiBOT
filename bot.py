import discord
from discord.ext import commands
import os

# Ustawienia uprawnień (to, co włączaliśmy na stronie Discorda)
intents = discord.Intents.default()
intents.message_content = True

# Tworzymy bota, który reaguje na komendy zaczynające się od wykrzyknika
bot = commands.Bot(command_prefix='!', intents=intents)

# Co bot robi, gdy się uruchomi?
@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i jestem gotów do pracy!')

# Prosta komenda testowa
@bot.command()
async def test(ctx):
    await ctx.send('Działam, Mości Panie! Jestem gotowy do przeszukiwania forum Balmory.')

# Uruchomienie bota przy użyciu tokenu (który podamy w Railway)
bot.run(os.environ.get('DISCORD_TOKEN'))
