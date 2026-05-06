#!/usr/bin/env python3
"""
One-shot patcher that adds ko / es-MX / es-ES / fr-FR translations into
_localize.py. Reads _localize.py, splices the 4 new languages into LANGS,
LANG_LABELS, and every STRINGS entry. Writes back. Idempotent — running
twice is a no-op.

Run from the press-kit repo root:
    python3 _add_new_langs.py
"""
import re, os, sys, ast

NEW_LANGS = ['ko', 'es-MX', 'es-ES', 'fr-FR']
NEW_LABELS = {'ko': '한국어', 'es-MX': 'ES-MX', 'es-ES': 'ES-ES', 'fr-FR': 'FR'}

# Translations keyed by English source string (matches keys in _localize.py STRINGS).
# Each value is a dict with the 4 new languages.
# Conventions per existing translations:
#   - Keep HTML tags intact
#   - Keep "Crunch Moonkiss Studios" / "Remain at Your Desk" / "Steam" / "BLACK MARKET" English
#   - CONDUIT: ko=CONDUIT (game keeps English), es-MX/es-ES=CONDUCTO, fr-FR=CONDUIT (matches game)
T = {
    'Remain At Your Desk — Press Kit | Crunch Moonkiss Studios': {
        'ko':    'Remain At Your Desk — 프레스 킷 | Crunch Moonkiss Studios',
        'es-MX': 'Remain At Your Desk — Press Kit | Crunch Moonkiss Studios',
        'es-ES': 'Remain At Your Desk — Press Kit | Crunch Moonkiss Studios',
        'fr-FR': 'Remain At Your Desk — Dossier de Presse | Crunch Moonkiss Studios',
    },
    '<div class="logo">PRESS KIT</div>': {
        'ko':    '<div class="logo">프레스 킷</div>',
        'es-MX': '<div class="logo">PRESS KIT</div>',
        'es-ES': '<div class="logo">PRESS KIT</div>',
        'fr-FR': '<div class="logo">DOSSIER DE PRESSE</div>',
    },
    '<a href="#about">About</a>': {
        'ko':    '<a href="#about">소개</a>',
        'es-MX': '<a href="#about">Acerca de</a>',
        'es-ES': '<a href="#about">Acerca de</a>',
        'fr-FR': '<a href="#about">À propos</a>',
    },
    '<a href="#capsules">Assets</a>': {
        'ko':    '<a href="#capsules">에셋</a>',
        'es-MX': '<a href="#capsules">Recursos</a>',
        'es-ES': '<a href="#capsules">Recursos</a>',
        'fr-FR': '<a href="#capsules">Ressources</a>',
    },
    '<a href="#media">Media</a>': {
        'ko':    '<a href="#media">미디어</a>',
        'es-MX': '<a href="#media">Medios</a>',
        'es-ES': '<a href="#media">Medios</a>',
        'fr-FR': '<a href="#media">Médias</a>',
    },
    '<a href="#press">Press</a>': {
        'ko':    '<a href="#press">언론</a>',
        'es-MX': '<a href="#press">Prensa</a>',
        'es-ES': '<a href="#press">Prensa</a>',
        'fr-FR': '<a href="#press">Presse</a>',
    },
    '<a href="#team">Developer</a>': {
        'ko':    '<a href="#team">개발자</a>',
        'es-MX': '<a href="#team">Desarrollador</a>',
        'es-ES': '<a href="#team">Desarrollador</a>',
        'fr-FR': '<a href="#team">Développeur</a>',
    },
    '<a href="#contact">Contact</a>': {
        'ko':    '<a href="#contact">연락처</a>',
        'es-MX': '<a href="#contact">Contacto</a>',
        'es-ES': '<a href="#contact">Contacto</a>',
        'fr-FR': '<a href="#contact">Contact</a>',
    },
    '&gt; PRESS KIT — CRUNCH MOONKISS STUDIOS': {
        'ko':    '&gt; 프레스 킷 — CRUNCH MOONKISS STUDIOS',
        'es-MX': '&gt; PRESS KIT — CRUNCH MOONKISS STUDIOS',
        'es-ES': '&gt; PRESS KIT — CRUNCH MOONKISS STUDIOS',
        'fr-FR': '&gt; DOSSIER DE PRESSE — CRUNCH MOONKISS STUDIOS',
    },
    '<div class="subtitle">Cyberpunk Incremental Clicker</div>': {
        'ko':    '<div class="subtitle">사이버펑크 인크리멘탈 클리커</div>',
        'es-MX': '<div class="subtitle">Clicker Incremental Cyberpunk</div>',
        'es-ES': '<div class="subtitle">Clicker Incremental Cyberpunk</div>',
        'fr-FR': '<div class="subtitle">Clicker Incrémental Cyberpunk</div>',
    },
    '<div class="label">Developer</div>': {
        'ko':    '<div class="label">개발자</div>',
        'es-MX': '<div class="label">Desarrollador</div>',
        'es-ES': '<div class="label">Desarrollador</div>',
        'fr-FR': '<div class="label">Développeur</div>',
    },
    '<div class="label">Platform</div>': {
        'ko':    '<div class="label">플랫폼</div>',
        'es-MX': '<div class="label">Plataforma</div>',
        'es-ES': '<div class="label">Plataforma</div>',
        'fr-FR': '<div class="label">Plateforme</div>',
    },
    '<div class="label">Genre</div>': {
        'ko':    '<div class="label">장르</div>',
        'es-MX': '<div class="label">Género</div>',
        'es-ES': '<div class="label">Género</div>',
        'fr-FR': '<div class="label">Genre</div>',
    },
    '<div class="label">Release</div>': {
        'ko':    '<div class="label">출시</div>',
        'es-MX': '<div class="label">Lanzamiento</div>',
        'es-ES': '<div class="label">Lanzamiento</div>',
        'fr-FR': '<div class="label">Sortie</div>',
    },
    '<div class="value">Cyberpunk Incremental Clicker</div>': {
        'ko':    '<div class="value">사이버펑크 인크리멘탈 클리커</div>',
        'es-MX': '<div class="value">Clicker Incremental Cyberpunk</div>',
        'es-ES': '<div class="value">Clicker Incremental Cyberpunk</div>',
        'fr-FR': '<div class="value">Clicker Incrémental Cyberpunk</div>',
    },
    '<div class="value">Late 2026</div>': {
        'ko':    '<div class="value">2026년 후반</div>',
        'es-MX': '<div class="value">Finales de 2026</div>',
        'es-ES': '<div class="value">Finales de 2026</div>',
        'fr-FR': '<div class="value">Fin 2026</div>',
    },
    'WATCH TRAILER &rsaquo;': {
        'ko':    '트레일러 보기 &rsaquo;',
        'es-MX': 'VER TRÁILER &rsaquo;',
        'es-ES': 'VER TRÁILER &rsaquo;',
        'fr-FR': 'VOIR LA BANDE-ANNONCE &rsaquo;',
    },
    'VIEW ASSETS': {
        'ko':    '에셋 보기',
        'es-MX': 'VER RECURSOS',
        'es-ES': 'VER RECURSOS',
        'fr-FR': 'VOIR LES RESSOURCES',
    },
    'WISHLIST ON STEAM &rsaquo;': {
        'ko':    'STEAM에서 위시리스트 추가 &rsaquo;',
        'es-MX': 'AGREGAR A LISTA DE DESEOS EN STEAM &rsaquo;',
        'es-ES': 'AÑADIR A LISTA DE DESEOS EN STEAM &rsaquo;',
        'fr-FR': 'AJOUTER À LA LISTE DE SOUHAITS STEAM &rsaquo;',
    },
    '<h2>About the Game</h2>': {
        'ko':    '<h2>게임 소개</h2>',
        'es-MX': '<h2>Acerca del Juego</h2>',
        'es-ES': '<h2>Acerca del Juego</h2>',
        'fr-FR': '<h2>À propos du jeu</h2>',
    },
    '<p class="lede">You have two jobs.</p>': {
        'ko':    '<p class="lede">당신에게는 두 개의 직업이 있다.</p>',
        'es-MX': '<p class="lede">Tienes dos trabajos.</p>',
        'es-ES': '<p class="lede">Tienes dos trabajos.</p>',
        'fr-FR': '<p class="lede">Tu as deux boulots.</p>',
    },
    '<p>The first is fake. You click through tasks, file reports, sync databases, and collect a paycheck. Nobody knows what you actually do. You just need to look busy enough to get promoted.</p>': {
        'ko':    '<p>첫 번째는 가짜다. 당신은 업무를 클릭하고, 보고서를 제출하고, 데이터베이스를 동기화하고, 월급을 받는다. 당신이 실제로 무엇을 하는지 아무도 모른다. 승진할 만큼 바빠 보이기만 하면 된다.</p>',
        'es-MX': '<p>El primero es falso. Haces clic en tareas, presentas reportes, sincronizas bases de datos y cobras el sueldo. Nadie sabe lo que realmente haces. Solo tienes que verte lo suficientemente ocupado como para que te asciendan.</p>',
        'es-ES': '<p>El primero es falso. Haces clic en tareas, presentas informes, sincronizas bases de datos y cobras la nómina. Nadie sabe lo que realmente haces. Solo tienes que parecer lo suficientemente ocupado como para que te asciendan.</p>',
        'fr-FR': '<p>Le premier est bidon. Tu cliques sur des tâches, tu déposes des rapports, tu synchronises des bases de données, et tu touches ton salaire. Personne ne sait ce que tu fais vraiment. Tu dois juste avoir l\'air assez occupé pour être promu.</p>',
    },
    '<p>The second job is the real one. After hours, you break into the corporate network to pull data that isn\'t yours. You route through systems, crack firewalls, stay ahead of whoever\'s paying attention.</p>': {
        'ko':    '<p>두 번째 직업이 진짜다. 퇴근 후, 당신은 기업 네트워크에 침입하여 자기 것이 아닌 데이터를 빼낸다. 시스템을 경유하고, 방화벽을 뚫고, 주시하는 자보다 한발 앞선다.</p>',
        'es-MX': '<p>El segundo trabajo es el real. Después de horas, te metes en la red corporativa para extraer datos que no son tuyos. Te ruteas por sistemas, descifras firewalls, y te mantienes un paso adelante de quien esté prestando atención.</p>',
        'es-ES': '<p>El segundo trabajo es el real. Fuera de horario, te cuelas en la red corporativa para sacar datos que no son tuyos. Te enrutas por sistemas, rompes firewalls, te mantienes por delante de quien esté prestando atención.</p>',
        'fr-FR': '<p>Le second boulot est le vrai. Après les heures, tu pénètres dans le réseau de l\'entreprise pour extraire des données qui ne t\'appartiennent pas. Tu passes par les systèmes, tu craques les pare-feu, tu gardes une longueur d\'avance sur ceux qui surveillent.</p>',
    },
    '<div class="blabel">Boilerplate</div>': {
        'ko':    '<div class="blabel">공식 소개</div>',
        'es-MX': '<div class="blabel">Texto base</div>',
        'es-ES': '<div class="blabel">Texto base</div>',
        'fr-FR': '<div class="blabel">Texte officiel</div>',
    },
    '<p><em>Remain at Your Desk</em> is a cyberpunk incremental clicker with two jobs. By day you click tasks and get promoted. By night you hack the corporate network, manage suspicion, switch personas, and pull data that isn\'t yours. Get caught and start over with nothing.</p>': {
        'ko':    '<p><em>Remain at Your Desk</em>는 두 개의 직업을 가진 사이버펑크 인크리멘탈 클리커다. 낮에는 업무를 클릭하고 승진한다. 밤에는 기업 네트워크를 해킹하고, 의심을 관리하며, 페르소나를 바꾸고, 자기 것이 아닌 데이터를 빼낸다. 잡히면 빈손으로 처음부터 다시 시작이다.</p>',
        'es-MX': '<p><em>Remain at Your Desk</em> es un clicker incremental cyberpunk con dos trabajos. De día haces clic en tareas y te ascienden. De noche hackeas la red corporativa, manejas la sospecha, cambias de personas, y extraes datos que no son tuyos. Te atrapan y empiezas de cero.</p>',
        'es-ES': '<p><em>Remain at Your Desk</em> es un clicker incremental cyberpunk con dos trabajos. De día haces clic en tareas y asciendes. De noche hackeas la red corporativa, gestionas la sospecha, cambias de personas, y sacas datos que no son tuyos. Si te pillan, empiezas desde cero.</p>',
        'fr-FR': '<p><em>Remain at Your Desk</em> est un clicker incrémental cyberpunk avec deux boulots. Le jour tu cliques sur des tâches et tu es promu. La nuit tu pirates le réseau de l\'entreprise, tu gères la suspicion, tu changes de persona, et tu extrais des données qui ne t\'appartiennent pas. Tu te fais prendre et tu repars à zéro.</p>',
    },
    '<div class="feature-head">Risk</div>': {
        'ko':    '<div class="feature-head">위험</div>',
        'es-MX': '<div class="feature-head">Riesgo</div>',
        'es-ES': '<div class="feature-head">Riesgo</div>',
        'fr-FR': '<div class="feature-head">Risque</div>',
    },
    '<p>Every hack raises suspicion. Push too far and security starts paying attention. An audit lands on your desk and then an interrogation follows. If your story doesn\'t hold, you\'re back to Intern with nothing.</p>': {
        'ko':    '<p>모든 해킹은 의심을 높인다. 너무 멀리 밀어붙이면 보안이 주목하기 시작한다. 감사가 당신의 책상에 떨어지고 심문이 뒤따른다. 이야기가 통하지 않으면 인턴으로 돌아가 빈손이 된다.</p>',
        'es-MX': '<p>Cada hack sube la sospecha. Empuja demasiado y la seguridad empieza a prestar atención. Una auditoría cae sobre tu escritorio y luego viene un interrogatorio. Si tu historia no aguanta, regresas a Practicante sin nada.</p>',
        'es-ES': '<p>Cada hackeo sube la sospecha. Si te pasas, la seguridad empieza a prestar atención. Una auditoría cae sobre tu mesa y después viene un interrogatorio. Si tu historia no aguanta, vuelves a Becario sin nada.</p>',
        'fr-FR': '<p>Chaque piratage augmente la suspicion. Pousse trop loin et la sécurité commence à faire attention. Un audit atterrit sur ton bureau et un interrogatoire suit. Si ton histoire ne tient pas, tu retournes Stagiaire sans rien.</p>',
    },
    '<div class="feature-head">Two Economies</div>': {
        'ko':    '<div class="feature-head">두 개의 경제</div>',
        'es-MX': '<div class="feature-head">Dos Economías</div>',
        'es-ES': '<div class="feature-head">Dos Economías</div>',
        'fr-FR': '<div class="feature-head">Deux Économies</div>',
    },
    '<p>Credits come from the day job. They buy upgrades, automation, and time. Intel comes from hacks. Intel only drops on hacks, so there\'s less of it than credits and you have to take more risk to get it. It feeds its own upgrade tree, and those upgrades make every hack after faster and deadlier. Climb a rank and the BLACK MARKET opens &mdash; intel buys permanent edges there, the kind that survive every reset.</p>': {
        'ko':    '<p>크레딧은 낮의 업무에서 나온다. 업그레이드, 자동화, 시간을 살 수 있다. 정보는 해킹에서 나온다. 정보는 해킹에서만 떨어지므로 크레딧보다 적고, 얻으려면 더 큰 위험을 감수해야 한다. 정보는 자체 업그레이드 트리를 키우며, 그 업그레이드는 이후의 모든 해킹을 더 빠르고 치명적으로 만든다. 계급이 오르면 BLACK MARKET이 열린다 &mdash; 거기서 정보는 모든 리셋을 견디는 영구적인 우위를 산다.</p>',
        'es-MX': '<p>Los créditos vienen del trabajo de día. Compran mejoras, automatización y tiempo. La info viene de los hacks. La info solo cae en hacks, así que hay menos que créditos y tienes que arriesgarte más para conseguirla. Alimenta su propio árbol de mejoras, y esas mejoras hacen que cada hack siguiente sea más rápido y mortal. Sube de rango y se abre el BLACK MARKET &mdash; la info compra ventajas permanentes ahí, del tipo que sobrevive a cada reset.</p>',
        'es-ES': '<p>Los créditos vienen del trabajo de día. Compran mejoras, automatización y tiempo. La info viene de los hackeos. La info solo cae en hackeos, así que hay menos que créditos y tienes que arriesgarte más para conseguirla. Alimenta su propio árbol de mejoras, y esas mejoras hacen que cada hackeo posterior sea más rápido y letal. Sube de rango y se abre el BLACK MARKET &mdash; ahí la info compra ventajas permanentes, del tipo que sobreviven a cada reinicio.</p>',
        'fr-FR': '<p>Les crédits viennent du boulot de jour. Ils achètent des améliorations, de l\'automatisation et du temps. L\'intel vient des piratages. L\'intel ne tombe qu\'avec les hacks, donc il y en a moins que de crédits et tu dois prendre plus de risques pour l\'obtenir. Il alimente son propre arbre d\'améliorations, et ces améliorations rendent chaque hack suivant plus rapide et plus mortel. Monte d\'un rang et le BLACK MARKET ouvre &mdash; l\'intel y achète des avantages permanents, du genre qui survivent à chaque reset.</p>',
    },
    '<div class="feature-head">Cover</div>': {
        'ko':    '<div class="feature-head">위장</div>',
        'es-MX': '<div class="feature-head">Cobertura</div>',
        'es-ES': '<div class="feature-head">Cobertura</div>',
        'fr-FR': '<div class="feature-head">Couverture</div>',
    },
    '<p>Personas let you hack as someone else. The janitor, the IT admin, the consultant nobody questions. Each has its own bonuses but wears out if you lean on it too hard. If suspicion creeps up, you file a fake report, wipe the logs, or pay someone to forget they saw you.</p>': {
        'ko':    '<p>페르소나는 다른 사람으로 해킹할 수 있게 해준다. 청소부, IT 관리자, 아무도 의심하지 않는 컨설턴트. 각각 고유한 보너스를 가지지만 너무 많이 의지하면 닳아 없어진다. 의심이 올라가면 가짜 보고서를 제출하거나, 로그를 지우거나, 누군가에게 돈을 주고 당신을 봤다는 것을 잊게 한다.</p>',
        'es-MX': '<p>Las personas te dejan hackear como alguien más. El conserje, el admin de TI, el consultor que nadie cuestiona. Cada una tiene sus propios bonos pero se gasta si la fuerzas demasiado. Si la sospecha sube, presentas un reporte falso, borras los registros, o le pagas a alguien para que olvide que te vio.</p>',
        'es-ES': '<p>Las personas te dejan hackear como otra persona. El conserje, el admin de IT, el consultor al que nadie cuestiona. Cada una tiene sus propios bonos pero se desgasta si te apoyas demasiado en ella. Si sube la sospecha, presentas un informe falso, borras los logs, o le pagas a alguien para que olvide que te vio.</p>',
        'fr-FR': '<p>Les personas te permettent de pirater en tant que quelqu\'un d\'autre. Le concierge, l\'admin IT, le consultant que personne ne questionne. Chacune a ses propres bonus mais s\'use si tu t\'y appuies trop fort. Si la suspicion monte, tu déposes un faux rapport, tu effaces les logs, ou tu payes quelqu\'un pour oublier qu\'il t\'a vu.</p>',
    },
    '<div class="feature-head">Leverage</div>': {
        'ko':    '<div class="feature-head">레버리지</div>',
        'es-MX': '<div class="feature-head">Influencia</div>',
        'es-ES': '<div class="feature-head">Influencia</div>',
        'fr-FR': '<div class="feature-head">Levier</div>',
    },
    '<p>Not everything is worth selling. Hack the same target enough times and you build a dossier. This creates permanent leverage that survives resets. The email server shows you who hates who. The security network shows you where the cameras are not. Executive files show you how the system really works.</p>': {
        'ko':    '<p>모든 것이 팔만한 가치가 있는 것은 아니다. 같은 표적을 충분히 해킹하면 도시에가 만들어진다. 이는 리셋을 견디는 영구적인 레버리지를 만든다. 이메일 서버는 누가 누구를 미워하는지 알려준다. 보안 네트워크는 카메라가 없는 곳을 알려준다. 임원 파일은 시스템이 실제로 어떻게 작동하는지 보여준다.</p>',
        'es-MX': '<p>No todo vale la pena venderlo. Hackea el mismo objetivo suficientes veces y construyes un expediente. Esto crea influencia permanente que sobrevive a los resets. El servidor de correo te muestra quién odia a quién. La red de seguridad te muestra dónde no están las cámaras. Los archivos ejecutivos te muestran cómo funciona realmente el sistema.</p>',
        'es-ES': '<p>No todo merece la pena venderlo. Hackea el mismo objetivo las veces suficientes y montas un dossier. Esto crea influencia permanente que sobrevive a los reinicios. El servidor de correo te muestra quién odia a quién. La red de seguridad te muestra dónde no están las cámaras. Los archivos ejecutivos te muestran cómo funciona realmente el sistema.</p>',
        'fr-FR': '<p>Tout ne vaut pas la peine d\'être vendu. Pirate la même cible assez de fois et tu montes un dossier. Cela crée un levier permanent qui survit aux resets. Le serveur mail te montre qui déteste qui. Le réseau de sécurité te montre où les caméras ne sont pas. Les fichiers de la direction te montrent comment le système fonctionne vraiment.</p>',
    },
    '<div class="feature-head">Prestige</div>': {
        'ko':    '<div class="feature-head">프레스티지</div>',
        'es-MX': '<div class="feature-head">Prestigio</div>',
        'es-ES': '<div class="feature-head">Prestigio</div>',
        'fr-FR': '<div class="feature-head">Prestige</div>',
    },
    '<p>Get promoted and you start over with stronger multipliers and personas that stick. Get caught and you start over with nothing.</p>': {
        'ko':    '<p>승진하면 더 강한 배율과 유지되는 페르소나로 다시 시작한다. 잡히면 빈손으로 다시 시작이다.</p>',
        'es-MX': '<p>Te ascienden y empiezas de nuevo con multiplicadores más fuertes y personas que se quedan. Te atrapan y empiezas de cero.</p>',
        'es-ES': '<p>Te ascienden y empiezas de nuevo con multiplicadores más fuertes y personas que se quedan. Si te pillan, empiezas desde cero.</p>',
        'fr-FR': '<p>Sois promu et tu repars avec des multiplicateurs plus forts et des personas qui restent. Fais-toi prendre et tu repars sans rien.</p>',
    },
    '<h2>Capsule Art &amp; Key Images</h2>': {
        'ko':    '<h2>캡슐 아트 &amp; 핵심 이미지</h2>',
        'es-MX': '<h2>Arte de Capsule &amp; Imágenes Clave</h2>',
        'es-ES': '<h2>Arte de Capsule &amp; Imágenes Clave</h2>',
        'fr-FR': '<h2>Capsule &amp; Images Clés</h2>',
    },
    '<h2>Capsule Art & Key Images</h2>': {
        'ko':    '<h2>캡슐 아트 & 핵심 이미지</h2>',
        'es-MX': '<h2>Arte de Capsule & Imágenes Clave</h2>',
        'es-ES': '<h2>Arte de Capsule & Imágenes Clave</h2>',
        'fr-FR': '<h2>Capsule & Images Clés</h2>',
    },
    '<h2>Screenshots &amp; Media</h2>': {
        'ko':    '<h2>스크린샷 &amp; 미디어</h2>',
        'es-MX': '<h2>Capturas &amp; Medios</h2>',
        'es-ES': '<h2>Capturas &amp; Medios</h2>',
        'fr-FR': '<h2>Captures d\'écran &amp; Médias</h2>',
    },
    '<h2>Screenshots & Media</h2>': {
        'ko':    '<h2>스크린샷 & 미디어</h2>',
        'es-MX': '<h2>Capturas & Medios</h2>',
        'es-ES': '<h2>Capturas & Medios</h2>',
        'fr-FR': '<h2>Captures d\'écran & Médias</h2>',
    },
    '<h2>Featured In</h2>': {
        'ko':    '<h2>언론 보도</h2>',
        'es-MX': '<h2>Destacado en</h2>',
        'es-ES': '<h2>Destacado en</h2>',
        'fr-FR': '<h2>Mentionné dans</h2>',
    },
    '<h2>Developer</h2>': {
        'ko':    '<h2>개발자</h2>',
        'es-MX': '<h2>Desarrollador</h2>',
        'es-ES': '<h2>Desarrollador</h2>',
        'fr-FR': '<h2>Développeur</h2>',
    },
    '<h2>Contact</h2>': {
        'ko':    '<h2>연락처</h2>',
        'es-MX': '<h2>Contacto</h2>',
        'es-ES': '<h2>Contacto</h2>',
        'fr-FR': '<h2>Contact</h2>',
    },
    'Main Capsule (460&times;215)': {
        'ko':    '메인 캡슐 (460&times;215)',
        'es-MX': 'Capsule Principal (460&times;215)',
        'es-ES': 'Capsule Principal (460&times;215)',
        'fr-FR': 'Capsule Principale (460&times;215)',
    },
    'Header / Library Capsule (460&times;215)': {
        'ko':    '헤더 / 라이브러리 캡슐 (460&times;215)',
        'es-MX': 'Header / Capsule de Biblioteca (460&times;215)',
        'es-ES': 'Header / Capsule de Biblioteca (460&times;215)',
        'fr-FR': 'Header / Capsule Bibliothèque (460&times;215)',
    },
    'Hero Art (1920&times;620)': {
        'ko':    '히어로 아트 (1920&times;620)',
        'es-MX': 'Arte Hero (1920&times;620)',
        'es-ES': 'Arte Hero (1920&times;620)',
        'fr-FR': 'Hero Art (1920&times;620)',
    },
    'Library Capsule</div>': {
        'ko':    '라이브러리 캡슐</div>',
        'es-MX': 'Capsule de Biblioteca</div>',
        'es-ES': 'Capsule de Biblioteca</div>',
        'fr-FR': 'Capsule Bibliothèque</div>',
    },
    'Small Capsule (231&times;87)': {
        'ko':    '스몰 캡슐 (231&times;87)',
        'es-MX': 'Capsule Pequeña (231&times;87)',
        'es-ES': 'Capsule Pequeña (231&times;87)',
        'fr-FR': 'Petite Capsule (231&times;87)',
    },
    'Vertical Capsule (374&times;448)': {
        'ko':    '버티컬 캡슐 (374&times;448)',
        'es-MX': 'Capsule Vertical (374&times;448)',
        'es-ES': 'Capsule Vertical (374&times;448)',
        'fr-FR': 'Capsule Verticale (374&times;448)',
    },
    '&gt; Latest Trailer': {
        'ko':    '&gt; 최신 트레일러',
        'es-MX': '&gt; Tráiler Más Reciente',
        'es-ES': '&gt; Tráiler Más Reciente',
        'fr-FR': '&gt; Dernière Bande-Annonce',
    },
    '&gt; Launch Trailer': {
        'ko':    '&gt; 출시 트레일러',
        'es-MX': '&gt; Tráiler de Lanzamiento',
        'es-ES': '&gt; Tráiler de Lanzamiento',
        'fr-FR': '&gt; Bande-Annonce de Lancement',
    },
    'CLICK TO ENLARGE': {
        'ko':    '클릭하여 확대',
        'es-MX': 'CLIC PARA AMPLIAR',
        'es-ES': 'CLIC PARA AMPLIAR',
        'fr-FR': 'CLIQUER POUR AGRANDIR',
    },
    'DOWNLOAD ALL ASSETS (.ZIP)': {
        'ko':    '모든 에셋 다운로드 (.ZIP)',
        'es-MX': 'DESCARGAR TODOS LOS RECURSOS (.ZIP)',
        'es-ES': 'DESCARGAR TODOS LOS RECURSOS (.ZIP)',
        'fr-FR': 'TÉLÉCHARGER TOUTES LES RESSOURCES (.ZIP)',
    },
    'DOWNLOAD 4K TRAILER': {
        'ko':    '4K 트레일러 다운로드',
        'es-MX': 'DESCARGAR TRÁILER 4K',
        'es-ES': 'DESCARGAR TRÁILER 4K',
        'fr-FR': 'TÉLÉCHARGER LA BANDE-ANNONCE 4K',
    },
    'Taiwan &middot; Gaming News': {
        'ko':    '대만 &middot; 게임 뉴스',
        'es-MX': 'Taiwán &middot; Noticias de Videojuegos',
        'es-ES': 'Taiwán &middot; Noticias de Videojuegos',
        'fr-FR': 'Taïwan &middot; Actualités Jeux Vidéo',
    },
    'Japan &middot; Industry Trade': {
        'ko':    '일본 &middot; 업계지',
        'es-MX': 'Japón &middot; Prensa de la Industria',
        'es-ES': 'Japón &middot; Prensa Sectorial',
        'fr-FR': 'Japon &middot; Presse Spécialisée',
    },
    'Korea &middot; Indie Coverage': {
        'ko':    '한국 &middot; 인디 보도',
        'es-MX': 'Corea &middot; Cobertura Indie',
        'es-ES': 'Corea &middot; Cobertura Indie',
        'fr-FR': 'Corée &middot; Couverture Indé',
    },
    'Podcast &middot; Episode 310': {
        'ko':    '팟캐스트 &middot; 310화',
        'es-MX': 'Podcast &middot; Episodio 310',
        'es-ES': 'Podcast &middot; Episodio 310',
        'fr-FR': 'Podcast &middot; Épisode 310',
    },
    'Solo Developer / Composer — Crunch Moonkiss Studios': {
        'ko':    '1인 개발자 / 작곡가 — Crunch Moonkiss Studios',
        'es-MX': 'Desarrollador Solo / Compositor — Crunch Moonkiss Studios',
        'es-ES': 'Desarrollador Solo / Compositor — Crunch Moonkiss Studios',
        'fr-FR': 'Développeur Solo / Compositeur — Crunch Moonkiss Studios',
    },
    'Jared D. is a NYC-based solo indie developer and award-winning film composer. He is also developing <em>Groove Defense</em> (Steam, TBD) — a music-driven tower defense game where every tower adds a layer to the soundtrack.': {
        'ko':    'Jared D.는 뉴욕에 거주하는 1인 인디 개발자이자 수상 경력이 있는 영화 작곡가다. 또한 <em>Groove Defense</em>(Steam, 미정)도 개발 중이다 — 모든 타워가 사운드트랙에 한 층을 더하는 음악 기반 타워 디펜스 게임이다.',
        'es-MX': 'Jared D. es un desarrollador indie en solitario radicado en NYC y compositor de cine galardonado. También desarrolla <em>Groove Defense</em> (Steam, por definir) — un tower defense musical donde cada torre añade una capa a la banda sonora.',
        'es-ES': 'Jared D. es un desarrollador indie en solitario afincado en Nueva York y compositor de cine premiado. También desarrolla <em>Groove Defense</em> (Steam, por confirmar) — un tower defense musical donde cada torre añade una capa a la banda sonora.',
        'fr-FR': 'Jared D. est un développeur indé solo basé à New York et compositeur de cinéma primé. Il développe également <em>Groove Defense</em> (Steam, à venir) — un tower defense musical où chaque tour ajoute une couche à la bande-son.',
    },
    '<div class="clabel">Press Inquiries</div>': {
        'ko':    '<div class="clabel">언론 문의</div>',
        'es-MX': '<div class="clabel">Consultas de Prensa</div>',
        'es-ES': '<div class="clabel">Consultas de Prensa</div>',
        'fr-FR': '<div class="clabel">Demandes Presse</div>',
    },
    '<div class="clabel">Steam Page</div>': {
        'ko':    '<div class="clabel">Steam 페이지</div>',
        'es-MX': '<div class="clabel">Página Steam</div>',
        'es-ES': '<div class="clabel">Página Steam</div>',
        'fr-FR': '<div class="clabel">Page Steam</div>',
    },
    '<div class="clabel">Studio</div>': {
        'ko':    '<div class="clabel">스튜디오</div>',
        'es-MX': '<div class="clabel">Estudio</div>',
        'es-ES': '<div class="clabel">Estudio</div>',
        'fr-FR': '<div class="clabel">Studio</div>',
    },
    '<div class="clabel">Location</div>': {
        'ko':    '<div class="clabel">위치</div>',
        'es-MX': '<div class="clabel">Ubicación</div>',
        'es-ES': '<div class="clabel">Ubicación</div>',
        'fr-FR': '<div class="clabel">Localisation</div>',
    },
    'New York City, USA': {
        'ko':    '미국 뉴욕시',
        'es-MX': 'Nueva York, EE.UU.',
        'es-ES': 'Nueva York, EE.UU.',
        'fr-FR': 'New York, États-Unis',
    },
    'Remain At Your Desk on Steam': {
        'ko':    'Steam의 Remain At Your Desk',
        'es-MX': 'Remain At Your Desk en Steam',
        'es-ES': 'Remain At Your Desk en Steam',
        'fr-FR': 'Remain At Your Desk sur Steam',
    },
    '&copy; 2026 Crunch Moonkiss Studios — All rights reserved': {
        'ko':    '&copy; 2026 Crunch Moonkiss Studios — 모든 권리 보유',
        'es-MX': '&copy; 2026 Crunch Moonkiss Studios — Todos los derechos reservados',
        'es-ES': '&copy; 2026 Crunch Moonkiss Studios — Todos los derechos reservados',
        'fr-FR': '&copy; 2026 Crunch Moonkiss Studios — Tous droits réservés',
    },
    '&gt; SESSION TERMINATED_': {
        'ko':    '&gt; 세션 종료_',
        'es-MX': '&gt; SESIÓN TERMINADA_',
        'es-ES': '&gt; SESIÓN TERMINADA_',
        'fr-FR': '&gt; SESSION TERMINÉE_',
    },
    'alt="Night Mode — Hacking Route Choice"': {
        'ko':    'alt="나이트 모드 — 해킹 경로 선택"',
        'es-MX': 'alt="Modo Noche — Elección de Ruta de Hack"',
        'es-ES': 'alt="Modo Noche — Elección de Ruta de Hackeo"',
        'fr-FR': 'alt="Mode Nuit — Choix de Route de Piratage"',
    },
    'alt="Day Mode — Corporate Tasks"': {
        'ko':    'alt="데이 모드 — 기업 업무"',
        'es-MX': 'alt="Modo Día — Tareas Corporativas"',
        'es-ES': 'alt="Modo Día — Tareas Corporativas"',
        'fr-FR': 'alt="Mode Jour — Tâches d\'Entreprise"',
    },
    'alt="Leverage — Archive the Dirt, or Leak It for Credits"': {
        'ko':    'alt="레버리지 — 약점을 보관하거나, 크레딧을 위해 유출"',
        'es-MX': 'alt="Influencia — Archiva el Trapo Sucio, o Filtra por Créditos"',
        'es-ES': 'alt="Influencia — Archiva los Trapos Sucios, o Filtra por Créditos"',
        'fr-FR': 'alt="Levier — Archive le Linge Sale, ou Fuite-le pour des Crédits"',
    },
    'alt="Black Market — Permanent Perks Off the Books"': {
        'ko':    'alt="Black Market — 장부 외 영구 특전"',
        'es-MX': 'alt="Black Market — Ventajas Permanentes Fuera de los Libros"',
        'es-ES': 'alt="Black Market — Ventajas Permanentes Fuera de los Libros"',
        'fr-FR': 'alt="Black Market — Avantages Permanents Hors Livres"',
    },
    'alt="Hack In Progress — Breach Detected"': {
        'ko':    'alt="해킹 진행 중 — 침입 감지"',
        'es-MX': 'alt="Hack en Progreso — Brecha Detectada"',
        'es-ES': 'alt="Hackeo en Progreso — Brecha Detectada"',
        'fr-FR': 'alt="Piratage en Cours — Brèche Détectée"',
    },
    'alt="CONDUIT — I See What You Are"': {
        'ko':    'alt="CONDUIT — 나는 네가 무엇인지 보고 있다"',
        'es-MX': 'alt="CONDUCTO — Veo Lo Que Eres"',
        'es-ES': 'alt="CONDUCTO — Veo Lo Que Eres"',
        'fr-FR': 'alt="CONDUIT — Je Vois Ce Que Tu Es"',
    },
    'alt="Promotion — Employee Performance Review"': {
        'ko':    'alt="승진 — 직원 성과 평가"',
        'es-MX': 'alt="Promoción — Evaluación de Desempeño del Empleado"',
        'es-ES': 'alt="Promoción — Evaluación de Desempeño del Empleado"',
        'fr-FR': 'alt="Promotion — Évaluation de Performance de l\'Employé"',
    },
}


def main():
    path = '_localize.py'
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    # 1. Update LANGS list
    new_langs_repr = ", ".join(f"'{l}'" for l in NEW_LANGS)
    if new_langs_repr in src:
        print(f"NEW_LANGS already present — file appears patched. Aborting.")
        sys.exit(0)
    src = re.sub(
        r"^LANGS = \[([^\]]+)\]",
        lambda m: f"LANGS = [{m.group(1)}, {new_langs_repr}]",
        src,
        count=1,
        flags=re.MULTILINE,
    )

    # 2. Append to LANG_LABELS dict
    label_lines = "".join(
        f"    '{code}':    {repr(label)},\n" for code, label in NEW_LABELS.items()
    )
    src = re.sub(
        r"(LANG_LABELS = \{[^}]+?)(\n\}\n)",
        lambda m: m.group(1) + "\n" + label_lines.rstrip("\n") + m.group(2),
        src,
        count=1,
    )

    # 3. For each STRINGS entry: locate the closing `},` of that entry's dict and
    # inject the new translations right before. We do this by walking the source
    # character by character, finding the english key, then finding the matching
    # close brace.
    missing = []
    for en_key, new_table in T.items():
        # Build the patch lines
        lines = []
        for lang in NEW_LANGS:
            v = new_table.get(lang)
            if v is None:
                continue
            lines.append(f"        {lang!r}: {v!r},\n")
        patch = "".join(lines)

        # Find the dict literal that has this English key.
        # The keys in _localize.py are written like:  '<en key>': {
        # Use a careful repr-based match: find the literal Python repr of the key
        # followed by `: {`. Use the same quoting as the source — try both single
        # and double quote variants.
        # The source file uses single-quoted strings with embedded apostrophes
        # written as `\'`. Build a needle that matches that convention.
        needles = []
        if "'" in en_key:
            escaped = en_key.replace("\\", "\\\\").replace("'", "\\'")
            needles.append(f"'{escaped}': {{")
        else:
            needles.append(f"'{en_key}': {{")
        needles.append(f'"{en_key}": {{')
        idx = -1
        for needle in needles:
            idx = src.find(needle)
            if idx >= 0:
                break
        if idx < 0:
            missing.append(en_key[:60])
            continue

        # From idx, find the dict open brace, then its matching close brace.
        brace_open = src.find('{', idx)
        depth = 0
        i = brace_open
        while i < len(src):
            c = src[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            elif c == "'" or c == '"':
                # Skip over string literal
                quote = c
                i += 1
                while i < len(src) and src[i] != quote:
                    if src[i] == '\\':
                        i += 2
                        continue
                    i += 1
            i += 1
        # i points at the matching '}'. We want to insert right before it.
        # Make sure there's a newline + proper indentation before our patch.
        # Find the start of the line containing `}` (so we can preserve indent).
        before = src[:i].rstrip(' ')
        if not before.endswith('\n'):
            before += '\n'
        src = before + patch + src[i:]
        # advance past our insertion (we modified src, so re-find the closing brace
        # is unnecessary — we just continue with the new src for the next key)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)

    print(f"Patched {path} with {len(NEW_LANGS)} new languages.")
    if missing:
        print(f"WARNING — {len(missing)} keys not found in _localize.py:")
        for k in missing:
            print(f"  - {k}")
    else:
        print(f"All {len(T)} STRINGS entries updated.")


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
