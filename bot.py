import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Baza wiedzy zasilana WYŁĄCZNIE z oficjalnych poradników forum.balmora.pl
BAZA_BALMORA = {
    "wodz orkow": {
        "info": "Wódz Orków (oficjalny poradnik Balmora): Respi się w Dolinie Seungryong. Czas respu: ok. 4 godziny. Drop: Rękawica Złodzieja, ulepszacze.",
        "screen": "TUTAJ_WKLEJ_LINK_DO_SCREENA_Z_FORUM_BALMORY"
    }
}

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i czerpię wiedzę wyłącznie z Balmory!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    zapytanie_lower = zapytanie.lower()
    znaleziony = None
    
    for klucz, dane in BAZA_BALMORA.items():
        if klucz in zapytanie_lower or zapytanie_lower in klucz:
            znaleziony = dane
            break
            
    if znaleziony:
        await ctx.send(f"**Informacja z forum Balmora:**\n{znaleziony['info']}")
        await ctx.send(f"**Screen z forum:**\n{znaleziony['screen']}")
    else:
        await ctx.send("Mości Panie, w obecnej bazie Balmory nie ma jeszcze wpisu na ten temat.")

bot.run(os.environ.get('DISCORD_TOKEN'))
