#!/usr/bin/env python3
"""
One-shot patcher that adds Italian (`it`) to _localize.py. Idempotent —
running twice is a no-op. Run from the press-kit repo root:
    python3 _add_it.py
    python3 _localize.py

Conventions (match the existing langs / the game's it.json):
  - HTML tags / entities preserved exactly
  - "Crunch Moonkiss Studios", "Remain At Your Desk"/"Remain at Your Desk",
    "Steam", "Black Market", "CONDUIT", "Capsule"/"Hero Art"/"Library Capsule"
    asset terms stay as-is (CONDUIT is kept English in the game's it.json)
  - LEVERAGE -> "Leva" (matches the game's Italian)
"""
import re, _add_vi

NEW_LANG = 'it'
NEW_LABEL = 'IT'

# Italian, keyed by the exact English source string.
IT = {
    'Remain At Your Desk — Press Kit | Crunch Moonkiss Studios':
        'Remain At Your Desk — Kit Stampa | Crunch Moonkiss Studios',
    '<div class="logo">PRESS KIT</div>': '<div class="logo">KIT STAMPA</div>',
    '<a href="#about">About</a>':       '<a href="#about">Informazioni</a>',
    '<a href="#capsules">Assets</a>':   '<a href="#capsules">Risorse</a>',
    '<a href="#media">Media</a>':       '<a href="#media">Media</a>',
    '<a href="#press">Press</a>':       '<a href="#press">Stampa</a>',
    '<a href="#team">Developer</a>':    '<a href="#team">Sviluppatore</a>',
    '<a href="#contact">Contact</a>':   '<a href="#contact">Contatti</a>',
    '&gt; PRESS KIT — CRUNCH MOONKISS STUDIOS':
        '&gt; KIT STAMPA — CRUNCH MOONKISS STUDIOS',
    '<div class="subtitle">Cyberpunk Incremental Clicker</div>':
        '<div class="subtitle">Clicker Incrementale Cyberpunk</div>',
    '<div class="label">Developer</div>':    '<div class="label">Sviluppatore</div>',
    '<div class="label">Platform</div>':     '<div class="label">Piattaforma</div>',
    '<div class="label">Genre</div>':        '<div class="label">Genere</div>',
    '<div class="label">Demo</div>':         '<div class="label">Demo</div>',
    '<div class="label">Full Release</div>': '<div class="label">Uscita Completa</div>',
    '<div class="value demo-date">May 19, 2026</div>':
        '<div class="value demo-date">19 maggio 2026</div>',
    '<div class="value">Cyberpunk Incremental Clicker</div>':
        '<div class="value">Clicker Incrementale Cyberpunk</div>',
    '<div class="value">Late 2026</div>':    '<div class="value">Fine 2026</div>',
    'WATCH TRAILER &rsaquo;':        'GUARDA IL TRAILER &rsaquo;',
    'VIEW ASSETS':                  'VEDI LE RISORSE',
    'WISHLIST ON STEAM &rsaquo;':   'AGGIUNGI ALLA LISTA DEI DESIDERI SU STEAM &rsaquo;',
    '<h2>About the Game</h2>':      '<h2>Informazioni sul Gioco</h2>',
    '<p class="about-lede">You have <span class="twojobs">two jobs</span>. <em>One is fake.</em></p>':
        '<p class="about-lede">Hai <span class="twojobs">due lavori</span>. <em>Uno è finto.</em></p>',
    '<p>The first is fake. You click through tasks, file reports, sync databases, and collect a paycheck. Nobody knows what you actually do. You just need to look busy enough to get promoted.</p>':
        '<p>Il primo è finto. Clicchi tra le mansioni, archivi report, sincronizzi database e incassi lo stipendio. Nessuno sa cosa fai davvero. Devi solo sembrare abbastanza occupato da farti promuovere.</p>',
    "<p>The second job is the real one. After hours, you break into the corporate network to pull data that isn't yours. You route through systems, crack firewalls, stay ahead of whoever's paying attention.</p>":
        "<p>Il secondo lavoro è quello vero. Fuori orario, ti infiltri nella rete aziendale per sottrarre dati che non ti appartengono. Attraversi i sistemi, forzi i firewall, resti un passo avanti a chi ti tiene d'occhio.</p>",
    'data-label="BOILERPLATE"':     'data-label="DESCRIZIONE UFFICIALE"',
    "<p><em>Remain at Your Desk</em> is a cyberpunk incremental clicker with two jobs. By day you click tasks and get promoted. By night you hack the corporate network you're supposed to protect. Risk vs. reward, suspicion vs. progression, and an AI in the system that's been watching longer than you have.</p>":
        "<p><em>Remain at Your Desk</em> è un clicker incrementale cyberpunk con due lavori. Di giorno clicchi le mansioni e vieni promosso. Di notte hackeri la rete aziendale che dovresti proteggere. Rischio contro ricompensa, sospetto contro progressione, e un'IA nel sistema che osserva da più tempo di te.</p>",
    '<span class="term">Risk</span>':           '<span class="term">Rischio</span>',
    '<span class="term">Two Economies</span>':  '<span class="term">Due Economie</span>',
    '<span class="term">Cover</span>':          '<span class="term">Copertura</span>',
    "<p>Every hack raises suspicion. Push too far and security starts paying attention. An audit lands on your desk and then an interrogation follows. Suspicion bleeds off during your day-job clicks, so the corporate grind is the cooldown for the part of the game that's actually fun.</p>":
        "<p>Ogni hack aumenta il sospetto. Se esageri, la sicurezza inizia a farci caso. Un audit ti arriva sulla scrivania e poi segue un interrogatorio. Il sospetto cala mentre clicchi nel lavoro diurno, quindi la routine aziendale è il recupero per la parte di gioco che è davvero divertente.</p>",
    "<p>Credits come from the day job. They buy upgrades, automation, and time. Intel comes from hacks. Intel only drops on hacks, so there's less to hoard and more to spend deliberately on big targets. The two economies pull against each other.</p>":
        "<p>I crediti vengono dal lavoro diurno. Servono per potenziamenti, automazione e tempo. L'intel viene dagli hack. L'intel cade solo con gli hack, quindi c'è meno da accumulare e più da spendere con criterio sui bersagli grossi. Le due economie tirano in direzioni opposte.</p>",
    "<p>Personas let you hack as someone else. The janitor, the IT admin, the consultant nobody questions. Each has its own bonuses but wears out, and switching mid-shift carries its own risk.</p>":
        "<p>Le identità ti permettono di hackerare nei panni di qualcun altro. Il custode, l'admin IT, il consulente che nessuno mette in dubbio. Ognuna ha i suoi bonus ma si logora, e cambiare a metà turno comporta i suoi rischi.</p>",
    '<div class="head">Leverage</div>':     '<div class="head">Leva</div>',
    '<p>Not everything is worth selling. Hack the same target enough times and you build a dossier. This creates permanent leverage that survives audits, terminations, and even prestige resets.</p>':
        '<p>Non tutto vale la pena di essere venduto. Hackera lo stesso bersaglio abbastanza volte e costruisci un dossier. Questo crea una leva permanente che sopravvive ad audit, licenziamenti e persino ai reset di prestigio.</p>',
    '<div class="head">Prestige</div>':     '<div class="head">Prestigio</div>',
    '<div class="head">CONDUIT</div>':      '<div class="head">CONDUIT</div>',
    "<p>There's something already inside the network. It noticed you first. It will speak to you eventually. What it wants you to do — and what it actually is — depends on how you've been playing.</p>":
        "<p>C'è già qualcosa dentro la rete. Ti ha notato per primo. Prima o poi ti parlerà. Cosa vuole che tu faccia — e cosa sia davvero — dipende da come hai giocato.</p>",
    '<p>Get promoted and you start over with stronger multipliers and personas that stick. Get caught and you start over with nothing.</p>':
        '<p>Fatti promuovere e ricominci con moltiplicatori più forti e identità che restano. Fatti beccare e ricominci da zero.</p>',
    '<h2>Capsule Art &amp; Key Images</h2>':    '<h2>Capsule Art &amp; Immagini Principali</h2>',
    '<h2>Capsule Art & Key Images</h2>':        '<h2>Capsule Art & Immagini Principali</h2>',
    '<h2>Screenshots &amp; Media</h2>':         '<h2>Screenshot &amp; Media</h2>',
    '<h2>Screenshots & Media</h2>':             '<h2>Screenshot & Media</h2>',
    '<h2>Featured In</h2>':                     '<h2>Apparso Su</h2>',
    '<h2>Developer</h2>':                       '<h2>Sviluppatore</h2>',
    '<h2>Contact</h2>':                         '<h2>Contatti</h2>',
    'Main Capsule (460&times;215)':             'Capsule Principale (460&times;215)',
    'Header / Library Capsule (460&times;215)': 'Header / Library Capsule (460&times;215)',
    'Hero Art (1920&times;620)':                'Hero Art (1920&times;620)',
    '4K Marketing Thumbnail (3840&times;2160)': 'Miniatura Marketing 4K (3840&times;2160)',
    'Library Capsule</div>':                    'Library Capsule</div>',
    'Small Capsule (231&times;87)':             'Capsule Piccola (231&times;87)',
    'Vertical Capsule (374&times;448)':         'Capsule Verticale (374&times;448)',
    '&gt; Demo Announcement Trailer':           '&gt; Trailer di Annuncio della Demo',
    '&gt; Launch Trailer':                      '&gt; Trailer di Lancio',
    'CLICK TO ENLARGE':                         'CLICCA PER INGRANDIRE',
    'DOWNLOAD ALL ASSETS (.ZIP)':               'SCARICA TUTTE LE RISORSE (.ZIP)',
    'DOWNLOAD 4K TRAILER':                      'SCARICA IL TRAILER 4K',
    'Taiwan &middot; Gaming News':              'Taiwan &middot; Notizie di Gaming',
    'Japan &middot; Industry Trade':            'Giappone &middot; Stampa di Settore',
    'Korea &middot; Indie Coverage':            'Corea &middot; Copertura Indie',
    'Podcast &middot; Episode 310':             'Podcast &middot; Episodio 310',
    'Solo Developer / Composer — Crunch Moonkiss Studios':
        'Sviluppatore / Compositore Solitario — Crunch Moonkiss Studios',
    'Jared D. is a NYC-based solo indie developer and award-winning film composer.':
        'Jared D. è uno sviluppatore indie solitario con sede a NYC e compositore di colonne sonore premiato.',
    '<div class="clabel">Press Inquiries</div>':    '<div class="clabel">Richieste Stampa</div>',
    '<div class="clabel">Steam Page</div>':         '<div class="clabel">Pagina Steam</div>',
    '<div class="clabel">Studio</div>':             '<div class="clabel">Studio</div>',
    '<div class="clabel">Location</div>':           '<div class="clabel">Sede</div>',
    'New York City, USA':                           'New York City, USA',
    'Remain At Your Desk on Steam':                 'Remain At Your Desk su Steam',
    '&copy; 2026 Crunch Moonkiss Studios — All rights reserved':
        '&copy; 2026 Crunch Moonkiss Studios — Tutti i diritti riservati',
    '&gt; SESSION TERMINATED_':                     '&gt; SESSIONE TERMINATA_',
    'alt="Night Mode — Hacking Route Choice"':      'alt="Modalità Notte — Scelta del Percorso di Hacking"',
    'alt="Day Mode — Corporate Tasks"':             'alt="Modalità Giorno — Mansioni Aziendali"',
    'alt="Leverage — Archive the Dirt, or Leak It for Credits"':
        'alt="Leva — Archivia il Marcio o Diffondilo per Crediti"',
    'alt="Black Market — Permanent Perks Off the Books"':
        'alt="Black Market — Vantaggi Permanenti Fuori dai Registri"',
    'alt="Hack In Progress — Breach Detected"':     'alt="Hack in Corso — Violazione Rilevata"',
    'alt="CONDUIT — I See What You Are"':           'alt="CONDUIT — Vedo Cosa Sei"',
    'alt="Promotion — Employee Performance Review"':
        'alt="Promozione — Valutazione delle Prestazioni del Dipendente"',
}

# Build T from the canonical English keys in _add_vi.T so coverage is guaranteed
# 1:1 with an existing language (catches any string we forgot to translate).
missing = [en for en in _add_vi.T if en not in IT]
if missing:
    raise SystemExit("Missing IT translation for these keys:\n"
                     + "\n".join("  - " + m[:90] for m in missing))
extra = [en for en in IT if en not in _add_vi.T]
if extra:
    raise SystemExit("IT has keys not present in _add_vi.T (typo?):\n"
                     + "\n".join("  - " + m[:90] for m in extra))
T = {en: IT[en] for en in _add_vi.T}


def patch():
    path = '_localize.py'
    src = open(path, encoding='utf-8').read()

    m = re.search(r"^LANGS\s*=\s*\[(.*?)\]", src, re.MULTILINE | re.DOTALL)
    if m and f"'{NEW_LANG}'" in m.group(1):
        print('Already patched. Nothing to do.')
        return

    # 1) Add to LANGS
    src = re.sub(r"^(LANGS\s*=\s*\[[^\]]*?)(\])",
                 lambda mm: mm.group(1).rstrip().rstrip(',') + f", '{NEW_LANG}']",
                 src, count=1, flags=re.MULTILINE | re.DOTALL)

    # 2) Add label to LANG_LABELS
    src = re.sub(r"(LANG_LABELS\s*=\s*\{[^}]*?)(\n\})",
                 lambda mm: mm.group(1).rstrip() + f"\n    '{NEW_LANG}':    '{NEW_LABEL}',\n" + "}",
                 src, count=1, flags=re.DOTALL)

    # 3) Splice an 'it' line into each STRINGS entry
    missed = []
    for en_key, val in T.items():
        key_repr = repr(en_key)
        idx = src.find(f"    {key_repr}: {{")
        if idx < 0:
            alt = '"' + en_key.replace('"', '\\"') + '"'
            idx = src.find(f"    {alt}: {{")
            if idx < 0:
                missed.append(en_key[:80]); continue
            key_repr = alt
        end = src.find('\n},', idx)
        if end < 0:
            end = src.find('\n}', idx)
            if end < 0:
                missed.append(en_key[:80]); continue
        block = src[idx:end]
        if f"'{NEW_LANG}':" in block or f'"{NEW_LANG}":' in block:
            continue
        src = src[:end] + f"\n        '{NEW_LANG}':    {repr(val)}," + src[end:]

    open(path, 'w', encoding='utf-8').write(src)
    print(f"Patched _localize.py: added '{NEW_LANG}' to LANGS, LANG_LABELS, "
          f"and {len(T) - len(missed)} STRINGS entries.")
    if missed:
        print(f"WARN: {len(missed)} keys not found in _localize.py:")
        for k in missed:
            print(f"  - {k}")


if __name__ == '__main__':
    patch()
