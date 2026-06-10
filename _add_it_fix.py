#!/usr/bin/env python3
"""
Follow-up to _add_it.py: fills Italian for the 10 STRINGS entries it missed —
7 paragraphs whose English was rewritten/expanded after _add_vi.py was made
(so the stale keys didn't match) + 3 newer festival strings. Inserts 'it' by
anchoring on a unique apostrophe-free substring of each key, so it's agnostic to
how the key is quoted in _localize.py. Idempotent. Run, then re-run _localize.py.
"""
import re

# (unique anchor substring of the CURRENT English key, Italian translation)
FIX = [
    ("&gt; UPCOMING ON STEAM",
     '<div class="festivals-label">&gt; PROSSIMAMENTE SU STEAM</div>'),
    ("August 3&ndash;10, 2026",
     '<span class="festival-dates">3&ndash;10 agosto 2026</span>'),
    ("September 10&ndash;14, 2026",
     '<span class="festival-dates">10&ndash;14 settembre 2026</span>'),
    ("break into the corporate network to pull data",
     "<p>Il secondo lavoro è quello vero. Fuori orario, ti infiltri nella rete aziendale per sottrarre dati che non ti appartengono. Attraversi i sistemi, forzi i firewall, resti un passo avanti a chi ti tiene d'occhio.</p>"),
    ("manage suspicion, switch personas, and pull data",
     "<p><em>Remain at Your Desk</em> è un clicker incrementale cyberpunk con due lavori. Di giorno clicchi le mansioni e vieni promosso. Di notte hackeri la rete aziendale, gestisci il sospetto, cambi identità e sottrai dati che non ti appartengono. Fatti beccare e ricominci da zero.</p>"),
    ("An audit lands on your desk and then an interrogation follows",
     "<p>Ogni hack aumenta il sospetto. Se esageri, la sicurezza inizia a farci caso. Un audit ti arriva sulla scrivania e poi segue un interrogatorio. Se la tua versione non regge, torni a fare lo Stagista senza niente.</p>"),
    ("Climb a rank and the BLACK MARKET opens",
     "<p>I crediti vengono dal lavoro diurno. Servono per potenziamenti, automazione e tempo. L'intel viene dagli hack. L'intel cade solo con gli hack, quindi ce n'è meno dei crediti e devi rischiare di più per ottenerlo. Alimenta il proprio albero di potenziamenti, e quei potenziamenti rendono ogni hack successivo più veloce e letale. Sali di rango e si apre il BLACK MARKET &mdash; lì l'intel compra vantaggi permanenti, di quelli che sopravvivono a ogni reset.</p>"),
    ("wipe the logs, or pay someone to forget they saw you",
     "<p>Le identità ti permettono di hackerare nei panni di qualcun altro. Il custode, l'admin IT, il consulente che nessuno mette in dubbio. Ognuna ha i suoi bonus ma si logora se ci si appoggia troppo. Se il sospetto sale, presenti un report falso, cancelli i log o paghi qualcuno perché dimentichi di averti visto.</p>"),
    ("The email server shows you who hates who",
     "<p>Non tutto vale la pena di essere venduto. Hackera lo stesso bersaglio abbastanza volte e costruisci un dossier. Questo crea una leva permanente che sopravvive ai reset. Il server email ti mostra chi odia chi. La rete di sicurezza ti mostra dove le telecamere non arrivano. I file dei dirigenti ti mostrano come funziona davvero il sistema.</p>"),
    ("What it tells you is the real plot of the game",
     "<p>C'è già qualcosa dentro la rete. Ti ha notato per primo. Prima o poi ti parlerà. Quello che ti dice è la vera trama del gioco.</p>"),
]

path = '_localize.py'
src = open(path, encoding='utf-8').read()
added = 0
problems = []
for anchor, it_val in FIX:
    idx = src.find(anchor)
    if idx < 0:
        problems.append(("anchor not found", anchor)); continue
    mclose = re.search(r'\n[ \t]*\},', src[idx:])
    if not mclose:
        problems.append(("entry close not found", anchor)); continue
    end = idx + mclose.start()
    if "'it':" in src[idx:end] or '"it":' in src[idx:end]:
        continue  # already present
    src = src[:end] + f"\n        'it':    {repr(it_val)}," + src[end:]
    added += 1

open(path, 'w', encoding='utf-8').write(src)
print(f"Inserted Italian into {added} entries.")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  ", p)
