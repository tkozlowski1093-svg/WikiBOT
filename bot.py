import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==============================================================================
# BAZA WIEDZY – WKLEJAMY TUTAJ DANE DOKŁADNIE TAK, JAK SĄ NA FORUM BALMORY
# ==============================================================================
BAZA_BALMORA = {
    "wodz orkow": {
        "nazwa": "Wódz Orków",
        "info": "Respi się w Dolinie Seungryong (Dolina Orków).\n• Czas respu: ok. 4 godziny\n• Drop: Rękawica Złodzieja, ulepszacze, zbroje 34-48 lvl.",
        "screen": "https://forum.balmora.pl/uploads/monthly_2021_05/dolina.png" # Wklej tu dokładny URL do obrazka z forum Balmory
    },
    "zolw": {
        "nazwa": "Olbrzymi Żółw",
        "info": "Respi się na Pustyni Yongbi (Oaza).\n• Czas respu: ok. 4 godziny\n• Drop: Kamienie Dusz +4, biżuteria.",
        "screen": "https://forum.balmora.pl/uploads/monthly_2021_05/pustynia.png"
    },
    "metin zazdrosci": {
        "nazwa": "Metin Zazdrości (35 lvl)",
        "info": "Lokalizacja: M2 (Drugie Miasto).\n• Najlepszy drop na 35 poziomie z Rękawicą Złodzieja.\n• Drop: Instrukcje (Aura, Silne, Wir), Kamienie Dusz.",
        "screen": ""
    }
}

# Funkcja czyszcząca polskie znaki, by komenda działała np. i dla "wódz" i dla "wodz"
def normalizuj(tekst: str) -> str:
    zamiany = {'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z'}
    tekst = tekst.lower()
    for pl, bez_pl in zamiany.items():
        tekst = tekst.replace(pl, bez_pl)
    return tekst

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i bazuję wyłącznie na wiedzy z forum Balmory!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    zapytanie_czyste = normalizuj(zapytanie)
    znaleziony = None
    
    # Przeszukujemy naszą bazę z Balmory
    for klucz, dane in BAZA_BALMORA.items():
        if klucz in zapytanie_czyste or zapytanie_czyste in klucz:
            znaleziony = dane
            break
            
    if znaleziony:
        odpowiedz = f"📌 **[FORUM.BALMORA.PL] {znaleziony['nazwa']}**\n{znaleziony['info']}"
        await ctx.send(odpowiedz)
        
        # Jeśli dodamy link do screena/mapy z forum, bot go wyśle
        if znaleziony['screen'] and znaleziony['screen'].startswith("http"):
            await ctx.send(f"🗺️ **Mapa / Screen z forum Balmory:**\n{znaleziony['screen']}")
    else:
        await ctx.send("Mości Panie, nie mam jeszcze w bazie wpisu z forum Balmory dla tej frazy. Dodajmy go do kodu!")

bot.run(os.environ.get('DISCORD_TOKEN'))
