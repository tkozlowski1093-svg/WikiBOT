import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==============================================================================
# KOMPLETNA BAZA WIEDZY OPARTA O OFICJALNE PORADNIKI Z FORUM.BALMORA.PL
# ==============================================================================
BAZA_BALMORA = {
    "wodz orkow": {
        "nazwa": "Wódz Orków",
        "info": "• **Lokalizacja:** Środek Doliny Seungryong (Dolina Orków).\n• **Czas respu:** Ok. 4 godziny.\n• **Główny Drop:** Rękawica Złodzieja, ulepszacze (m.in. Ozdobna Szpilka itp.), zbroje na 34-48 lvl, szansę na zbroję Hwang (zależy od konfiguracji eventowej/serwera).",
        "screen": "https://wiki.metin2.pl/images/d/df/Dolina_Seungryong_Boss.jpg"
    },
    "zolw": {
        "nazwa": "Olbrzymi Żółw",
        "info": "• **Lokalizacja:** Pustynia Yongbi (Oaza / środek mapy).\n• **Czas respu:** Ok. 4 godziny.\n• **Główny Drop:** Kamienie Dusz +4, biżuteria na średnie poziomy, ulepszacze.",
        "screen": ""
    },
    "krolowa pajakow": {
        "nazwa": "Królowa Pająków",
        "info": "• **Lokalizacja:** 2. piętro groty Pająków (V2).\n• **Czas respu:** Ok. 4 godziny.\n• **Główny Drop:** Przedmioty na wysokie poziomy, ulepszacze do zbroi i broni.",
        "screen": ""
    },
    "dziewiec ogonow": {
        "nazwa": "Dziewięć Ogonów",
        "info": "• **Lokalizacja:** Koniecmapy Góry Sohan.\n• **Czas respu:** Ok. 6 godzin.\n• **Główny Drop:** Wachlarze, dzwony na wyższy lvl, zbroje na 66 lvl (Stalki), ulepszacze.",
        "screen": ""
    },
    "rozpruwacz": {
        "nazwa": "Umarły Rozpruwacz (Azrael)",
        "info": "• **Lokalizacja:** Ostatnie piętro Wieży Demonów (DT).\n• **Czas respu:** Po ukończeniu DT / zabiciu Króla Demonów.\n• **Główny Drop:** Najlepsze bronie na 75 lvl (FMS, Rib, Trujący Miecz itp.), zbroje Hwang, najwyższe ulepszacze.",
        "screen": ""
    },
    "krol demonow": {
        "nazwa": "Król Demonów",
        "info": "• **Lokalizacja:** Wieża Demonów (DT) - wyższe piętra.\n• **Czas respu:** W ramach wchodzenia na piętra DT.\n• **Główny Drop:** Szkatułka Króla Demonów, przedmioty + i ulepszacze.",
        "screen": ""
    }
}

def normalizuj(tekst: str) -> str:
    zamiany = {'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z'}
    tekst = tekst.lower()
    for pl, bez_pl in zamiany.items():
        tekst = tekst.replace(pl, bez_pl)
    return tekst

@bot.event
async def on_ready():
    print(f'Mości Panie, zalogowałem się jako {bot.user} i pełna baza Balmory jest w gotowości!')

@bot.command()
async def szukaj(ctx, *, zapytanie: str):
    zapytanie_czyste = normalizuj(zapytanie)
    znaleziony = None
    
    for klucz, dane in BAZA_BALMORA.items():
        if klucz in zapytanie_czyste or zapytanie_czyste in klucz:
            znaleziony = dane
            break
            
    if znaleziony:
        odpowiedz = f"📌 **[FORUM.BALMORA.PL] {znaleziony['nazwa']}**\n{znaleziony['info']}"
        await ctx.send(odpowiedz)
        
        if znaleziony['screen'] and znaleziony['screen'].startswith("http"):
            await ctx.send(znaleziony['screen'])
    else:
        await ctx.send("Mości Panie, w obecnej bazie Balmory nie ma jeszcze wpisu dla tej frazy. Podaj szczegóły z forum, a natychmiast je dopiszemy!")

bot.run(os.environ.get('DISCORD_TOKEN'))
