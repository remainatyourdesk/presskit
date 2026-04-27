#!/usr/bin/env python3
"""
One-shot localizer for the RAYD press kit.
Reads index.html (English source of truth), produces index.{lang}.html for each
supported language with translated copy. Run from the press-kit repo root:
    python3 _localize.py
"""
import re, os, sys

LANGS = ['de', 'ja', 'zh-CN', 'zh-TW', 'pt-BR', 'ru']

# Native-language label for the language picker
LANG_LABELS = {
    'en':    'EN',
    'de':    'DE',
    'ja':    '日本語',
    'zh-CN': '简中',
    'zh-TW': '繁中',
    'pt-BR': 'PT-BR',
    'ru':    'RU',
}

# All translatable strings. Keys map to en→target by direct substring replacement.
# Each replacement is anchored to be unique enough not to collide.
STRINGS = {
    # ─── Document title ───
    'Remain At Your Desk — Press Kit | Crunch Moonkiss Studios': {
        'de':    'Remain At Your Desk — Press Kit | Crunch Moonkiss Studios',
        'ja':    'Remain At Your Desk — プレスキット | Crunch Moonkiss Studios',
        'zh-CN': 'Remain At Your Desk — 媒体资源包 | Crunch Moonkiss Studios',
        'zh-TW': 'Remain At Your Desk — 媒體資源包 | Crunch Moonkiss Studios',
        'pt-BR': 'Remain At Your Desk — Press Kit | Crunch Moonkiss Studios',
        'ru':    'Remain At Your Desk — Пресс-кит | Crunch Moonkiss Studios',
    },

    # ─── Nav ───
    '<div class="logo">PRESS KIT</div>': {
        'de':    '<div class="logo">PRESS KIT</div>',
        'ja':    '<div class="logo">プレスキット</div>',
        'zh-CN': '<div class="logo">媒体资源包</div>',
        'zh-TW': '<div class="logo">媒體資源包</div>',
        'pt-BR': '<div class="logo">PRESS KIT</div>',
        'ru':    '<div class="logo">ПРЕСС-КИТ</div>',
    },
    '<a href="#about">About</a>': {
        'de': '<a href="#about">Über</a>', 'ja': '<a href="#about">概要</a>',
        'zh-CN': '<a href="#about">关于</a>', 'zh-TW': '<a href="#about">關於</a>',
        'pt-BR': '<a href="#about">Sobre</a>', 'ru': '<a href="#about">Описание</a>',
    },
    '<a href="#capsules">Assets</a>': {
        'de': '<a href="#capsules">Assets</a>', 'ja': '<a href="#capsules">素材</a>',
        'zh-CN': '<a href="#capsules">素材</a>', 'zh-TW': '<a href="#capsules">素材</a>',
        'pt-BR': '<a href="#capsules">Recursos</a>', 'ru': '<a href="#capsules">Материалы</a>',
    },
    '<a href="#media">Media</a>': {
        'de': '<a href="#media">Medien</a>', 'ja': '<a href="#media">メディア</a>',
        'zh-CN': '<a href="#media">媒体</a>', 'zh-TW': '<a href="#media">媒體</a>',
        'pt-BR': '<a href="#media">Mídia</a>', 'ru': '<a href="#media">Медиа</a>',
    },
    '<a href="#press">Press</a>': {
        'de': '<a href="#press">Presse</a>', 'ja': '<a href="#press">掲載情報</a>',
        'zh-CN': '<a href="#press">报道</a>', 'zh-TW': '<a href="#press">報導</a>',
        'pt-BR': '<a href="#press">Imprensa</a>', 'ru': '<a href="#press">Пресса</a>',
    },
    '<a href="#team">Developer</a>': {
        'de': '<a href="#team">Entwickler</a>', 'ja': '<a href="#team">開発者</a>',
        'zh-CN': '<a href="#team">开发者</a>', 'zh-TW': '<a href="#team">開發者</a>',
        'pt-BR': '<a href="#team">Desenvolvedor</a>', 'ru': '<a href="#team">Разработчик</a>',
    },
    '<a href="#contact">Contact</a>': {
        'de': '<a href="#contact">Kontakt</a>', 'ja': '<a href="#contact">連絡先</a>',
        'zh-CN': '<a href="#contact">联系</a>', 'zh-TW': '<a href="#contact">聯絡</a>',
        'pt-BR': '<a href="#contact">Contato</a>', 'ru': '<a href="#contact">Контакты</a>',
    },

    # ─── Hero ───
    '&gt; PRESS KIT — CRUNCH MOONKISS STUDIOS': {
        'de':    '&gt; PRESS KIT — CRUNCH MOONKISS STUDIOS',
        'ja':    '&gt; プレスキット — CRUNCH MOONKISS STUDIOS',
        'zh-CN': '&gt; 媒体资源包 — CRUNCH MOONKISS STUDIOS',
        'zh-TW': '&gt; 媒體資源包 — CRUNCH MOONKISS STUDIOS',
        'pt-BR': '&gt; PRESS KIT — CRUNCH MOONKISS STUDIOS',
        'ru':    '&gt; ПРЕСС-КИТ — CRUNCH MOONKISS STUDIOS',
    },
    '<div class="subtitle">Cyberpunk Incremental Clicker</div>': {
        'de':    '<div class="subtitle">Cyberpunk Incremental Clicker</div>',
        'ja':    '<div class="subtitle">サイバーパンク・インクリメンタル・クリッカー</div>',
        'zh-CN': '<div class="subtitle">赛博朋克放置点击</div>',
        'zh-TW': '<div class="subtitle">賽博龐克放置點擊</div>',
        'pt-BR': '<div class="subtitle">Clicker Incremental Cyberpunk</div>',
        'ru':    '<div class="subtitle">Киберпанк-кликер с прогрессией</div>',
    },
    '<div class="label">Developer</div>': {
        'de': '<div class="label">Entwickler</div>', 'ja': '<div class="label">開発者</div>',
        'zh-CN': '<div class="label">开发者</div>', 'zh-TW': '<div class="label">開發者</div>',
        'pt-BR': '<div class="label">Desenvolvedor</div>', 'ru': '<div class="label">Разработчик</div>',
    },
    '<div class="label">Platform</div>': {
        'de': '<div class="label">Plattform</div>', 'ja': '<div class="label">プラットフォーム</div>',
        'zh-CN': '<div class="label">平台</div>', 'zh-TW': '<div class="label">平台</div>',
        'pt-BR': '<div class="label">Plataforma</div>', 'ru': '<div class="label">Платформа</div>',
    },
    '<div class="label">Genre</div>': {
        'de': '<div class="label">Genre</div>', 'ja': '<div class="label">ジャンル</div>',
        'zh-CN': '<div class="label">类型</div>', 'zh-TW': '<div class="label">類型</div>',
        'pt-BR': '<div class="label">Gênero</div>', 'ru': '<div class="label">Жанр</div>',
    },
    '<div class="label">Release</div>': {
        'de': '<div class="label">Release</div>', 'ja': '<div class="label">リリース</div>',
        'zh-CN': '<div class="label">发布</div>', 'zh-TW': '<div class="label">發行</div>',
        'pt-BR': '<div class="label">Lançamento</div>', 'ru': '<div class="label">Выход</div>',
    },
    '<div class="value">Cyberpunk Incremental Clicker</div>': {
        'de':    '<div class="value">Cyberpunk Incremental Clicker</div>',
        'ja':    '<div class="value">サイバーパンク・インクリメンタル・クリッカー</div>',
        'zh-CN': '<div class="value">赛博朋克放置点击</div>',
        'zh-TW': '<div class="value">賽博龐克放置點擊</div>',
        'pt-BR': '<div class="value">Clicker Incremental Cyberpunk</div>',
        'ru':    '<div class="value">Киберпанк-кликер</div>',
    },
    '<div class="value">Late 2026</div>': {
        'de': '<div class="value">Ende 2026</div>', 'ja': '<div class="value">2026年後半</div>',
        'zh-CN': '<div class="value">2026 年末</div>', 'zh-TW': '<div class="value">2026 年末</div>',
        'pt-BR': '<div class="value">Final de 2026</div>', 'ru': '<div class="value">Конец 2026</div>',
    },
    'WATCH TRAILER &rsaquo;': {
        'de': 'TRAILER ANSEHEN &rsaquo;', 'ja': 'トレーラー再生 &rsaquo;',
        'zh-CN': '观看预告片 &rsaquo;', 'zh-TW': '觀看預告片 &rsaquo;',
        'pt-BR': 'VER TRAILER &rsaquo;', 'ru': 'СМОТРЕТЬ ТРЕЙЛЕР &rsaquo;',
    },
    'VIEW ASSETS': {
        'de': 'ASSETS ANSEHEN', 'ja': '素材を見る',
        'zh-CN': '查看素材', 'zh-TW': '查看素材',
        'pt-BR': 'VER RECURSOS', 'ru': 'СМОТРЕТЬ МАТЕРИАЛЫ',
    },
    'WISHLIST ON STEAM &rsaquo;': {
        'de': 'AUF STEAM AUF WUNSCHLISTE &rsaquo;', 'ja': 'STEAMでウィッシュリストに追加 &rsaquo;',
        'zh-CN': '在 STEAM 加入愿望单 &rsaquo;', 'zh-TW': '在 STEAM 加入願望清單 &rsaquo;',
        'pt-BR': 'LISTA DE DESEJOS NO STEAM &rsaquo;', 'ru': 'В СПИСОК ЖЕЛАЕМОГО STEAM &rsaquo;',
    },

    # ─── About ───
    '<h2>About the Game</h2>': {
        'de': '<h2>Über das Spiel</h2>', 'ja': '<h2>ゲーム概要</h2>',
        'zh-CN': '<h2>游戏简介</h2>', 'zh-TW': '<h2>遊戲簡介</h2>',
        'pt-BR': '<h2>Sobre o Jogo</h2>', 'ru': '<h2>Об игре</h2>',
    },
    '<p class="lede">You have two jobs.</p>': {
        'de':    '<p class="lede">Du hast zwei Jobs.</p>',
        'ja':    '<p class="lede">あなたには二つの仕事がある。</p>',
        'zh-CN': '<p class="lede">你有两份工作。</p>',
        'zh-TW': '<p class="lede">你有兩份工作。</p>',
        'pt-BR': '<p class="lede">Você tem dois empregos.</p>',
        'ru':    '<p class="lede">У тебя две работы.</p>',
    },
    '<p>The first is fake. You click through tasks, file reports, sync databases, and collect a paycheck. Nobody knows what you actually do. You just need to look busy enough to get promoted.</p>': {
        'de':    '<p>Der erste ist fake. Du klickst dich durch Aufgaben, reichst Berichte ein, synchronisierst Datenbanken und kassierst dein Gehalt. Niemand weiß, was du wirklich tust. Du musst nur beschäftigt genug aussehen, um befördert zu werden.</p>',
        'ja':    '<p>一つ目はフェイクだ。タスクをクリックし、レポートを提出し、データベースを同期し、給料を受け取る。本当は何をしているのか誰も知らない。昇進できるくらい忙しそうに見えればいい。</p>',
        'zh-CN': '<p>第一份是假的。你点击任务、提交报告、同步数据库,然后领工资。没人知道你到底在做什么。你只需要看起来忙到能被提拔就行。</p>',
        'zh-TW': '<p>第一份是假的。你點擊任務、提交報告、同步資料庫,然後領薪水。沒人知道你到底在做什麼。你只需要看起來忙到能被提拔就行。</p>',
        'pt-BR': '<p>O primeiro é falso. Você clica em tarefas, arquiva relatórios, sincroniza bancos de dados e recebe um salário. Ninguém sabe o que você realmente faz. Você só precisa parecer ocupado o suficiente para ser promovido.</p>',
        'ru':    '<p>Первая — фальшивая. Ты кликаешь по задачам, сдаёшь отчёты, синхронизируешь базы данных и получаешь зарплату. Никто не знает, чем ты на самом деле занят. Тебе нужно лишь выглядеть достаточно занятым, чтобы получить повышение.</p>',
    },
    '<p>The second job is the real one. After hours, you break into the corporate network to pull data that isn\'t yours. You route through systems, crack firewalls, stay ahead of whoever\'s paying attention.</p>': {
        'de':    '<p>Der zweite Job ist der echte. Nach Feierabend dringst du ins Firmennetzwerk ein, um Daten zu holen, die dir nicht gehören. Du routest durch Systeme, knackst Firewalls und bleibst denen voraus, die aufpassen.</p>',
        'ja':    '<p>二つ目の仕事こそが本物だ。退勤後、企業ネットワークに侵入し、自分のものではないデータを抜き取る。システムを経由し、ファイアウォールを破り、見張る者の一歩先を行く。</p>',
        'zh-CN': '<p>第二份工作才是真正的。下班后,你闯入公司网络,提取不属于你的数据。你穿越系统、破解防火墙,始终领先那些注意你的人一步。</p>',
        'zh-TW': '<p>第二份工作才是真正的。下班後,你闖入公司網路,提取不屬於你的資料。你穿越系統、破解防火牆,始終領先那些注意你的人一步。</p>',
        'pt-BR': '<p>O segundo emprego é o real. Depois do expediente, você invade a rede corporativa para extrair dados que não são seus. Você roteia por sistemas, quebra firewalls e fica à frente de quem está prestando atenção.</p>',
        'ru':    '<p>Вторая работа — настоящая. После рабочего дня ты взламываешь корпоративную сеть, чтобы вытащить данные, которые тебе не принадлежат. Ты прокладываешь маршруты через системы, ломаешь фаерволы и остаёшься на шаг впереди тех, кто наблюдает.</p>',
    },
    '&ldquo;A clever cyberpunk take on idle games where your day job hides something much deeper.&rdquo;': {
        'de':    '&bdquo;Ein cleverer Cyberpunk-Take auf Idle-Games, bei dem dein Tagesjob etwas viel Tieferes verbirgt.&ldquo;',
        'ja':    '&ldquo;日中の仕事がもっと深い何かを隠している、巧妙なサイバーパンク・アイドルゲーム。&rdquo;',
        'zh-CN': '&ldquo;一款巧妙的赛博朋克放置游戏,你的日常工作背后藏着更深的秘密。&rdquo;',
        'zh-TW': '&ldquo;一款巧妙的賽博龐克放置遊戲,你的日常工作背後藏著更深的秘密。&rdquo;',
        'pt-BR': '&ldquo;Uma releitura cyberpunk inteligente de jogos idle onde seu trabalho diurno esconde algo muito mais profundo.&rdquo;',
        'ru':    '&laquo;Умный киберпанк-взгляд на idle-игры, где твоя дневная работа скрывает нечто гораздо более глубокое.&raquo;',
    },
    '<div class="blabel">Boilerplate</div>': {
        'de': '<div class="blabel">Boilerplate</div>', 'ja': '<div class="blabel">定型文</div>',
        'zh-CN': '<div class="blabel">官方简介</div>', 'zh-TW': '<div class="blabel">官方簡介</div>',
        'pt-BR': '<div class="blabel">Texto padrão</div>', 'ru': '<div class="blabel">Описание</div>',
    },
    '<p><em>Remain at Your Desk</em> is a cyberpunk incremental clicker with two jobs. By day you click tasks and get promoted. By night you hack the corporate network, manage suspicion, switch personas, and pull data that isn\'t yours. Get caught and start over with nothing.</p>': {
        'de':    '<p><em>Remain at Your Desk</em> ist ein Cyberpunk Incremental Clicker mit zwei Jobs. Tagsüber klickst du Aufgaben und wirst befördert. Nachts hackst du das Firmennetzwerk, kontrollierst den Verdacht, wechselst Personas und ziehst Daten, die dir nicht gehören. Lass dich erwischen und du fängst mit nichts wieder an.</p>',
        'ja':    '<p><em>Remain at Your Desk</em>は二つの仕事を持つサイバーパンク・インクリメンタル・クリッカー。日中はタスクをクリックして昇進する。夜は企業ネットワークをハックし、疑惑を管理し、ペルソナを切り替え、自分のものではないデータを抜き取る。捕まればゼロからやり直しだ。</p>',
        'zh-CN': '<p><em>Remain at Your Desk</em> 是一款拥有双重身份的赛博朋克放置点击游戏。白天点击任务、争取晋升。夜晚入侵公司网络、控制怀疑度、切换身份、窃取不属于你的数据。被抓住,就一无所有重新开始。</p>',
        'zh-TW': '<p><em>Remain at Your Desk</em> 是一款擁有雙重身份的賽博龐克放置點擊遊戲。白天點擊任務、爭取晉升。夜晚入侵公司網路、控制懷疑度、切換身份、竊取不屬於你的資料。被抓住,就一無所有重新開始。</p>',
        'pt-BR': '<p><em>Remain at Your Desk</em> é um clicker incremental cyberpunk com dois empregos. De dia você clica em tarefas e é promovido. À noite você invade a rede corporativa, gerencia a suspeita, troca de personas e extrai dados que não são seus. Seja pego e comece do zero.</p>',
        'ru':    '<p><em>Remain at Your Desk</em> — киберпанк-кликер с прогрессией и двумя работами. Днём ты кликаешь по задачам и получаешь повышения. Ночью взламываешь корпоративную сеть, управляешь подозрением, меняешь личины и вытаскиваешь чужие данные. Попадёшься — начнёшь с нуля.</p>',
    },

    # ─── Feature blocks ───
    '<div class="feature-head">Risk</div>': {
        'de': '<div class="feature-head">Risiko</div>', 'ja': '<div class="feature-head">リスク</div>',
        'zh-CN': '<div class="feature-head">风险</div>', 'zh-TW': '<div class="feature-head">風險</div>',
        'pt-BR': '<div class="feature-head">Risco</div>', 'ru': '<div class="feature-head">Риск</div>',
    },
    '<p>Every hack raises suspicion. Push too far and security starts paying attention. An audit lands on your desk and then an interrogation follows. If your story doesn\'t hold, you\'re back to Intern with nothing.</p>': {
        'de':    '<p>Jeder Hack erhöht den Verdacht. Übertreib es und die Sicherheit beginnt aufzupassen. Ein Audit landet auf deinem Schreibtisch und dann folgt ein Verhör. Wenn deine Geschichte nicht hält, bist du wieder Praktikant mit nichts.</p>',
        'ja':    '<p>ハックするたびに疑惑が高まる。やりすぎれば警備が動き出す。監査が机に届き、続いて尋問が始まる。話のつじつまが合わなければ、何もないインターンに逆戻りだ。</p>',
        'zh-CN': '<p>每次入侵都会提升怀疑度。走得太远,安保就会盯上你。审计降临到你的桌前,审讯随之而来。故事兜不住,就一无所有重回实习生。</p>',
        'zh-TW': '<p>每次入侵都會提升懷疑度。走得太遠,安保就會盯上你。稽核降臨到你的桌前,審問隨之而來。故事兜不住,就一無所有重回實習生。</p>',
        'pt-BR': '<p>Cada invasão aumenta a suspeita. Vá longe demais e a segurança começa a prestar atenção. Uma auditoria cai na sua mesa e depois vem o interrogatório. Se sua história não se sustenta, você volta a Estagiário sem nada.</p>',
        'ru':    '<p>Каждый взлом повышает подозрение. Зайди слишком далеко — и охрана начнёт обращать внимание. На стол ложится аудит, а затем — допрос. Если легенда не выдержит, ты снова стажёр и без ничего.</p>',
    },
    '<div class="feature-head">Two Economies</div>': {
        'de': '<div class="feature-head">Zwei Ökonomien</div>', 'ja': '<div class="feature-head">二つの経済</div>',
        'zh-CN': '<div class="feature-head">双重经济</div>', 'zh-TW': '<div class="feature-head">雙重經濟</div>',
        'pt-BR': '<div class="feature-head">Duas Economias</div>', 'ru': '<div class="feature-head">Две экономики</div>',
    },
    '<p>Credits come from the day job. They buy upgrades, automation, and time. Intel comes from hacks. Intel only drops on hacks, so there\'s less of it than credits and you have to take more risk to get it. It feeds its own upgrade tree, and those upgrades make every hack after faster and deadlier. Climb a rank and the BLACK MARKET opens &mdash; intel buys permanent edges there, the kind that survive every reset.</p>': {
        'de':    '<p>Credits kommen vom Tagesjob. Sie kaufen Upgrades, Automatisierung und Zeit. Intel kommt von Hacks. Intel droppt nur durch Hacks, davon gibt es weniger als Credits und du musst mehr Risiko eingehen. Es speist seinen eigenen Upgrade-Baum, und diese Upgrades machen jeden weiteren Hack schneller und tödlicher. Steig einen Rang auf und der BLACK MARKET öffnet sich &mdash; Intel kauft dort permanente Vorteile, die jeden Reset überleben.</p>',
        'ja':    '<p>クレジットは日中の仕事から来る。アップグレードや自動化、時間を買える。インテルはハックから来る。ハックでしか落ちないため、クレジットより少なく、より大きなリスクが必要だ。専用のアップグレードツリーを持ち、その後のハックを速く致命的にする。階級を上げるとBLACK MARKETが開く&mdash;インテルはそこで永続的な優位を買え、それらはあらゆるリセットを生き延びる。</p>',
        'zh-CN': '<p>积分来自白天的工作。可以购买升级、自动化和时间。情报来自入侵。情报只在入侵中掉落,因此比积分稀少,获取需要更大风险。它有自己的升级树,这些升级让之后的每次入侵更快、更致命。晋升一级后 BLACK MARKET 开启 &mdash; 在那里情报可以买到永久优势,经得起每次重置。</p>',
        'zh-TW': '<p>積分來自白天的工作。可以購買升級、自動化和時間。情報來自入侵。情報只在入侵中掉落,因此比積分稀少,獲取需要更大風險。它有自己的升級樹,這些升級讓之後的每次入侵更快、更致命。晉升一級後 BLACK MARKET 開啟 &mdash; 在那裡情報可以買到永久優勢,經得起每次重置。</p>',
        'pt-BR': '<p>Créditos vêm do trabalho diurno. Compram upgrades, automação e tempo. Intel vem das invasões. Intel só cai em hacks, então há menos dele que de créditos e você precisa correr mais riscos para consegui-lo. Alimenta sua própria árvore de upgrades, e esses upgrades fazem cada hack seguinte mais rápido e mais letal. Suba de cargo e o BLACK MARKET abre &mdash; intel compra vantagens permanentes ali, do tipo que sobrevive a cada reset.</p>',
        'ru':    '<p>Кредиты приходят с дневной работы. Они покупают улучшения, автоматизацию и время. Интел добывается взломами. Интел падает только с хаков, поэтому его меньше, чем кредитов, и за него приходится рисковать больше. У него своё дерево улучшений, и эти улучшения делают каждый следующий взлом быстрее и опаснее. Поднимись в ранге и откроется BLACK MARKET &mdash; интел покупает там постоянные преимущества, которые переживают любой сброс.</p>',
    },
    '<div class="feature-head">Cover</div>': {
        'de': '<div class="feature-head">Tarnung</div>', 'ja': '<div class="feature-head">カバー</div>',
        'zh-CN': '<div class="feature-head">掩护</div>', 'zh-TW': '<div class="feature-head">掩護</div>',
        'pt-BR': '<div class="feature-head">Cobertura</div>', 'ru': '<div class="feature-head">Прикрытие</div>',
    },
    '<p>Personas let you hack as someone else. The janitor, the IT admin, the consultant nobody questions. Each has its own bonuses but wears out if you lean on it too hard. If suspicion creeps up, you file a fake report, wipe the logs, or pay someone to forget they saw you.</p>': {
        'de':    '<p>Personas lassen dich als jemand anderes hacken. Der Hausmeister, der IT-Admin, der Berater, den niemand hinterfragt. Jede hat eigene Boni, nutzt sich aber ab, wenn du sie zu sehr beanspruchst. Steigt der Verdacht, reichst du einen gefälschten Bericht ein, löschst Logs oder bezahlst jemanden, dich zu vergessen.</p>',
        'ja':    '<p>ペルソナを使えば別人としてハックできる。清掃員、ITアドミン、誰も疑わないコンサルタント。それぞれ独自のボーナスを持つが、頼りすぎれば消耗する。疑惑が高まれば、偽のレポートを提出し、ログを消し、誰かに見たことを忘れさせる金を払う。</p>',
        'zh-CN': '<p>身份让你以别人的名义入侵。清洁工、IT 管理员、没人会质疑的顾问。每个都有独特加成,但用得太狠就会失效。怀疑度上升时,你就提交假报告、抹掉日志,或者花钱让人忘了见过你。</p>',
        'zh-TW': '<p>身份讓你以別人的名義入侵。清潔工、IT 管理員、沒人會質疑的顧問。每個都有獨特加成,但用得太狠就會失效。懷疑度上升時,你就提交假報告、抹掉日誌,或者花錢讓人忘了見過你。</p>',
        'pt-BR': '<p>As Personas deixam você invadir como outra pessoa. O zelador, o administrador de TI, o consultor que ninguém questiona. Cada uma tem seus próprios bônus, mas se desgasta se você apoiar demais nela. Se a suspeita sobe, você envia um relatório falso, apaga os logs ou paga alguém para esquecer que viu você.</p>',
        'ru':    '<p>Личины позволяют взламывать как кто-то другой. Уборщик, IT-админ, консультант, которого никто не допрашивает. У каждой свои бонусы, но они изнашиваются при чрезмерном использовании. Если подозрение растёт, ты подаёшь поддельный отчёт, стираешь логи или платишь кому-то, чтобы забыли, что видели тебя.</p>',
    },
    '<div class="feature-head">Leverage</div>': {
        'de': '<div class="feature-head">Druckmittel</div>', 'ja': '<div class="feature-head">レバレッジ</div>',
        'zh-CN': '<div class="feature-head">把柄</div>', 'zh-TW': '<div class="feature-head">把柄</div>',
        'pt-BR': '<div class="feature-head">Influência</div>', 'ru': '<div class="feature-head">Рычаги</div>',
    },
    '<p>Not everything is worth selling. Hack the same target enough times and you build a dossier. This creates permanent leverage that survives resets. The email server shows you who hates who. The security network shows you where the cameras are not. Executive files show you how the system really works.</p>': {
        'de':    '<p>Nicht alles ist es wert verkauft zu werden. Hacke dasselbe Ziel oft genug und du baust ein Dossier auf. Das erschafft permanente Druckmittel, die Resets überleben. Der E-Mail-Server zeigt dir, wer wen hasst. Das Sicherheitsnetzwerk zeigt dir, wo die Kameras nicht sind. Vorstands-Dateien zeigen dir, wie das System wirklich funktioniert.</p>',
        'ja':    '<p>すべてが売る価値があるわけではない。同じターゲットを何度もハックすればドシエが完成する。それはリセットを生き延びる永続的なレバレッジを生む。メールサーバーは誰が誰を憎んでいるか教える。セキュリティネットワークはカメラのない場所を示す。役員ファイルはシステムの本当の仕組みを明かす。</p>',
        'zh-CN': '<p>不是什么都值得卖。把同一个目标黑够次数就能建成一份档案。这会形成经得起重置的永久把柄。邮件服务器告诉你谁恨谁。安保网络告诉你哪里没有摄像头。高管文件告诉你系统真正的运作方式。</p>',
        'zh-TW': '<p>不是什麼都值得賣。把同一個目標駭夠次數就能建成一份檔案。這會形成經得起重置的永久把柄。郵件伺服器告訴你誰恨誰。安保網路告訴你哪裡沒有攝影機。高管檔案告訴你系統真正的運作方式。</p>',
        'pt-BR': '<p>Nem tudo vale a pena vender. Invada o mesmo alvo vezes o bastante e você monta um dossiê. Isso cria influência permanente que sobrevive a resets. O servidor de e-mail mostra quem odeia quem. A rede de segurança mostra onde as câmeras não estão. Os arquivos executivos mostram como o sistema realmente funciona.</p>',
        'ru':    '<p>Не всё стоит продавать. Взломай одну и ту же цель достаточно раз — и соберёшь досье. Оно создаёт постоянные рычаги, переживающие сбросы. Почтовый сервер покажет, кто кого ненавидит. Сеть безопасности — где нет камер. Файлы руководства — как система работает на самом деле.</p>',
    },
    '<div class="feature-head">Prestige</div>': {
        'de': '<div class="feature-head">Prestige</div>', 'ja': '<div class="feature-head">プレステージ</div>',
        'zh-CN': '<div class="feature-head">声望</div>', 'zh-TW': '<div class="feature-head">聲望</div>',
        'pt-BR': '<div class="feature-head">Prestígio</div>', 'ru': '<div class="feature-head">Престиж</div>',
    },
    '<p>Get promoted and you start over with stronger multipliers and personas that stick. Get caught and you start over with nothing.</p>': {
        'de':    '<p>Lass dich befördern und du startest neu mit stärkeren Multiplikatoren und bleibenden Personas. Lass dich erwischen und du startest neu mit nichts.</p>',
        'ja':    '<p>昇進すれば強いマルチプライヤーと残るペルソナを持って再スタート。捕まれば何もない状態で再スタートだ。</p>',
        'zh-CN': '<p>晋升,带着更强的倍率和保留的身份重新开始。被抓,一无所有重新开始。</p>',
        'zh-TW': '<p>晉升,帶著更強的倍率和保留的身份重新開始。被抓,一無所有重新開始。</p>',
        'pt-BR': '<p>Seja promovido e recomece com multiplicadores mais fortes e personas que ficam. Seja pego e recomece com nada.</p>',
        'ru':    '<p>Получи повышение и начни заново с сильными множителями и сохранёнными личинами. Попадись — начни заново с нуля.</p>',
    },

    # ─── Section headers ───
    '<h2>Capsule Art &amp; Key Images</h2>': {
        'de': '<h2>Capsule-Art &amp; Schlüsselbilder</h2>', 'ja': '<h2>カプセルアート &amp; キービジュアル</h2>',
        'zh-CN': '<h2>胶囊图 &amp; 关键视觉</h2>', 'zh-TW': '<h2>膠囊圖 &amp; 關鍵視覺</h2>',
        'pt-BR': '<h2>Arte de Capsule &amp; Imagens Principais</h2>', 'ru': '<h2>Капсульный арт и ключевые изображения</h2>',
    },
    '<h2>Capsule Art & Key Images</h2>': {
        'de': '<h2>Capsule-Art & Schlüsselbilder</h2>', 'ja': '<h2>カプセルアート & キービジュアル</h2>',
        'zh-CN': '<h2>胶囊图 & 关键视觉</h2>', 'zh-TW': '<h2>膠囊圖 & 關鍵視覺</h2>',
        'pt-BR': '<h2>Arte de Capsule & Imagens Principais</h2>', 'ru': '<h2>Капсульный арт и ключевые изображения</h2>',
    },
    '<h2>Screenshots &amp; Media</h2>': {
        'de': '<h2>Screenshots &amp; Medien</h2>', 'ja': '<h2>スクリーンショット &amp; メディア</h2>',
        'zh-CN': '<h2>截图 &amp; 媒体</h2>', 'zh-TW': '<h2>截圖 &amp; 媒體</h2>',
        'pt-BR': '<h2>Screenshots &amp; Mídia</h2>', 'ru': '<h2>Скриншоты и медиа</h2>',
    },
    '<h2>Screenshots & Media</h2>': {
        'de': '<h2>Screenshots & Medien</h2>', 'ja': '<h2>スクリーンショット & メディア</h2>',
        'zh-CN': '<h2>截图 & 媒体</h2>', 'zh-TW': '<h2>截圖 & 媒體</h2>',
        'pt-BR': '<h2>Screenshots & Mídia</h2>', 'ru': '<h2>Скриншоты и медиа</h2>',
    },
    '<h2>Featured In</h2>': {
        'de': '<h2>Erwähnt In</h2>', 'ja': '<h2>掲載メディア</h2>',
        'zh-CN': '<h2>媒体报道</h2>', 'zh-TW': '<h2>媒體報導</h2>',
        'pt-BR': '<h2>Destaques na Imprensa</h2>', 'ru': '<h2>Упоминания в прессе</h2>',
    },
    '<h2>Developer</h2>': {
        'de': '<h2>Entwickler</h2>', 'ja': '<h2>開発者</h2>',
        'zh-CN': '<h2>开发者</h2>', 'zh-TW': '<h2>開發者</h2>',
        'pt-BR': '<h2>Desenvolvedor</h2>', 'ru': '<h2>Разработчик</h2>',
    },
    '<h2>Contact</h2>': {
        'de': '<h2>Kontakt</h2>', 'ja': '<h2>連絡先</h2>',
        'zh-CN': '<h2>联系</h2>', 'zh-TW': '<h2>聯絡</h2>',
        'pt-BR': '<h2>Contato</h2>', 'ru': '<h2>Контакты</h2>',
    },

    # ─── Capsule labels ───
    'Main Capsule (460&times;215)': {
        'de': 'Main Capsule (460&times;215)', 'ja': 'メインカプセル (460&times;215)',
        'zh-CN': '主胶囊图 (460&times;215)', 'zh-TW': '主膠囊圖 (460&times;215)',
        'pt-BR': 'Capsule Principal (460&times;215)', 'ru': 'Основная капсула (460&times;215)',
    },
    'Header / Library Capsule (460&times;215)': {
        'de': 'Header / Library Capsule (460&times;215)', 'ja': 'ヘッダー / ライブラリカプセル (460&times;215)',
        'zh-CN': '页头 / 库胶囊图 (460&times;215)', 'zh-TW': '頁首 / 庫膠囊圖 (460&times;215)',
        'pt-BR': 'Header / Capsule de Biblioteca (460&times;215)', 'ru': 'Шапка / Капсула библиотеки (460&times;215)',
    },
    'Hero Art (1920&times;620)': {
        'de': 'Hero-Art (1920&times;620)', 'ja': 'ヒーローアート (1920&times;620)',
        'zh-CN': '主视觉 (1920&times;620)', 'zh-TW': '主視覺 (1920&times;620)',
        'pt-BR': 'Arte Hero (1920&times;620)', 'ru': 'Hero-арт (1920&times;620)',
    },
    'Library Capsule</div>': {
        'de': 'Library Capsule</div>', 'ja': 'ライブラリカプセル</div>',
        'zh-CN': '库胶囊图</div>', 'zh-TW': '庫膠囊圖</div>',
        'pt-BR': 'Capsule de Biblioteca</div>', 'ru': 'Капсула библиотеки</div>',
    },
    'Small Capsule (231&times;87)': {
        'de': 'Small Capsule (231&times;87)', 'ja': 'スモールカプセル (231&times;87)',
        'zh-CN': '小胶囊图 (231&times;87)', 'zh-TW': '小膠囊圖 (231&times;87)',
        'pt-BR': 'Capsule Pequena (231&times;87)', 'ru': 'Малая капсула (231&times;87)',
    },
    'Vertical Capsule (374&times;448)': {
        'de': 'Vertical Capsule (374&times;448)', 'ja': '縦型カプセル (374&times;448)',
        'zh-CN': '竖向胶囊图 (374&times;448)', 'zh-TW': '直向膠囊圖 (374&times;448)',
        'pt-BR': 'Capsule Vertical (374&times;448)', 'ru': 'Вертикальная капсула (374&times;448)',
    },

    # ─── Media section ───
    '&gt; Latest Trailer': {
        'de': '&gt; Neuester Trailer', 'ja': '&gt; 最新トレーラー',
        'zh-CN': '&gt; 最新预告', 'zh-TW': '&gt; 最新預告',
        'pt-BR': '&gt; Trailer Mais Recente', 'ru': '&gt; Последний трейлер',
    },
    '&gt; Launch Trailer': {
        'de': '&gt; Launch-Trailer', 'ja': '&gt; ローンチトレーラー',
        'zh-CN': '&gt; 发布预告', 'zh-TW': '&gt; 發行預告',
        'pt-BR': '&gt; Trailer de Lançamento', 'ru': '&gt; Релизный трейлер',
    },
    'CLICK TO ENLARGE': {
        'de': 'ZUM VERGRÖSSERN KLICKEN', 'ja': 'クリックで拡大',
        'zh-CN': '点击放大', 'zh-TW': '點擊放大',
        'pt-BR': 'CLIQUE PARA AMPLIAR', 'ru': 'НАЖМИТЕ ДЛЯ УВЕЛИЧЕНИЯ',
    },
    'DOWNLOAD ALL ASSETS (.ZIP)': {
        'de': 'ALLE ASSETS HERUNTERLADEN (.ZIP)', 'ja': '全素材ダウンロード (.ZIP)',
        'zh-CN': '下载全部素材 (.ZIP)', 'zh-TW': '下載全部素材 (.ZIP)',
        'pt-BR': 'BAIXAR TODOS RECURSOS (.ZIP)', 'ru': 'СКАЧАТЬ ВСЕ МАТЕРИАЛЫ (.ZIP)',
    },
    'DOWNLOAD 4K TRAILER': {
        'de': '4K-TRAILER HERUNTERLADEN', 'ja': '4Kトレーラーダウンロード',
        'zh-CN': '下载 4K 预告片', 'zh-TW': '下載 4K 預告片',
        'pt-BR': 'BAIXAR TRAILER 4K', 'ru': 'СКАЧАТЬ 4K ТРЕЙЛЕР',
    },

    # ─── Press item meta ───
    'Taiwan &middot; Gaming News': {
        'de': 'Taiwan &middot; Gaming-News', 'ja': '台湾 &middot; ゲームニュース',
        'zh-CN': '台湾 &middot; 游戏新闻', 'zh-TW': '台灣 &middot; 遊戲新聞',
        'pt-BR': 'Taiwan &middot; Notícias de Games', 'ru': 'Тайвань &middot; Игровые новости',
    },
    'Japan &middot; Industry Trade': {
        'de': 'Japan &middot; Branchenfachpresse', 'ja': '日本 &middot; 業界誌',
        'zh-CN': '日本 &middot; 行业媒体', 'zh-TW': '日本 &middot; 產業媒體',
        'pt-BR': 'Japão &middot; Imprensa de Setor', 'ru': 'Япония &middot; Отраслевая пресса',
    },
    'Korea &middot; Indie Coverage': {
        'de': 'Korea &middot; Indie-Berichterstattung', 'ja': '韓国 &middot; インディー報道',
        'zh-CN': '韩国 &middot; 独立游戏报道', 'zh-TW': '韓國 &middot; 獨立遊戲報導',
        'pt-BR': 'Coreia &middot; Cobertura Indie', 'ru': 'Корея &middot; Инди-пресса',
    },
    'Podcast &middot; Episode 310': {
        'de': 'Podcast &middot; Episode 310', 'ja': 'ポッドキャスト &middot; エピソード310',
        'zh-CN': '播客 &middot; 第 310 集', 'zh-TW': '播客 &middot; 第 310 集',
        'pt-BR': 'Podcast &middot; Episódio 310', 'ru': 'Подкаст &middot; Эпизод 310',
    },

    # ─── Team ───
    'Solo Developer / Composer — Crunch Moonkiss Studios': {
        'de':    'Solo-Entwickler / Komponist — Crunch Moonkiss Studios',
        'ja':    'ソロ開発者 / 作曲家 — Crunch Moonkiss Studios',
        'zh-CN': '独立开发者 / 作曲家 — Crunch Moonkiss Studios',
        'zh-TW': '獨立開發者 / 作曲家 — Crunch Moonkiss Studios',
        'pt-BR': 'Desenvolvedor Solo / Compositor — Crunch Moonkiss Studios',
        'ru':    'Соло-разработчик / Композитор — Crunch Moonkiss Studios',
    },
    'Jared D. is a NYC-based solo indie developer and award-winning film composer. He is also developing <em>Groove Defense</em> (Steam, TBD) — a music-driven tower defense game where every tower adds a layer to the soundtrack.': {
        'de':    'Jared D. ist ein in NYC ansässiger Solo-Indie-Entwickler und preisgekrönter Filmkomponist. Er entwickelt außerdem <em>Groove Defense</em> (Steam, TBA) — ein musikgesteuertes Tower-Defense-Spiel, bei dem jeder Turm eine Schicht zum Soundtrack hinzufügt.',
        'ja':    'Jared D. はニューヨーク在住のソロインディー開発者で受賞歴のある映画作曲家。<em>Groove Defense</em>(Steam、未定)も開発中—すべてのタワーがサウンドトラックに一層を加える音楽主導のタワーディフェンスゲーム。',
        'zh-CN': 'Jared D. 是常驻纽约的独立游戏开发者,也是获奖电影配乐作曲家。他同时在开发 <em>Groove Defense</em>(Steam,待定)—一款由音乐驱动的塔防游戏,每座防御塔都会为配乐添加一层音轨。',
        'zh-TW': 'Jared D. 是常駐紐約的獨立遊戲開發者,也是獲獎電影配樂作曲家。他同時在開發 <em>Groove Defense</em>(Steam,待定)—一款由音樂驅動的塔防遊戲,每座防禦塔都會為配樂添加一層音軌。',
        'pt-BR': 'Jared D. é um desenvolvedor indie solo baseado em NYC e compositor de filmes premiado. Também desenvolve <em>Groove Defense</em> (Steam, a definir) — um tower defense musical onde cada torre adiciona uma camada à trilha sonora.',
        'ru':    'Джаред Д. — нью-йоркский соло-инди-разработчик и удостоенный наград кинокомпозитор. Также разрабатывает <em>Groove Defense</em> (Steam, дата TBD) — музыкальный tower defense, где каждая башня добавляет слой к саундтреку.',
    },

    # ─── Contact ───
    '<div class="clabel">Press Inquiries</div>': {
        'de': '<div class="clabel">Presseanfragen</div>', 'ja': '<div class="clabel">プレス問い合わせ</div>',
        'zh-CN': '<div class="clabel">媒体咨询</div>', 'zh-TW': '<div class="clabel">媒體諮詢</div>',
        'pt-BR': '<div class="clabel">Contato de Imprensa</div>', 'ru': '<div class="clabel">Запросы прессы</div>',
    },
    '<div class="clabel">Steam Page</div>': {
        'de': '<div class="clabel">Steam-Seite</div>', 'ja': '<div class="clabel">Steamページ</div>',
        'zh-CN': '<div class="clabel">Steam 页面</div>', 'zh-TW': '<div class="clabel">Steam 頁面</div>',
        'pt-BR': '<div class="clabel">Página Steam</div>', 'ru': '<div class="clabel">Страница Steam</div>',
    },
    '<div class="clabel">Studio</div>': {
        'de': '<div class="clabel">Studio</div>', 'ja': '<div class="clabel">スタジオ</div>',
        'zh-CN': '<div class="clabel">工作室</div>', 'zh-TW': '<div class="clabel">工作室</div>',
        'pt-BR': '<div class="clabel">Estúdio</div>', 'ru': '<div class="clabel">Студия</div>',
    },
    '<div class="clabel">Location</div>': {
        'de': '<div class="clabel">Standort</div>', 'ja': '<div class="clabel">所在地</div>',
        'zh-CN': '<div class="clabel">地点</div>', 'zh-TW': '<div class="clabel">地點</div>',
        'pt-BR': '<div class="clabel">Localização</div>', 'ru': '<div class="clabel">Расположение</div>',
    },
    'New York City, USA': {
        'de': 'New York City, USA', 'ja': 'ニューヨーク, アメリカ',
        'zh-CN': '美国 纽约', 'zh-TW': '美國 紐約',
        'pt-BR': 'Nova York, EUA', 'ru': 'Нью-Йорк, США',
    },
    'Remain At Your Desk on Steam': {
        'de': 'Remain At Your Desk auf Steam', 'ja': 'SteamのRemain At Your Desk',
        'zh-CN': 'Remain At Your Desk Steam 页面', 'zh-TW': 'Remain At Your Desk Steam 頁面',
        'pt-BR': 'Remain At Your Desk no Steam', 'ru': 'Remain At Your Desk в Steam',
    },

    # ─── Footer ───
    '&copy; 2026 Crunch Moonkiss Studios — All rights reserved': {
        'de':    '&copy; 2026 Crunch Moonkiss Studios — Alle Rechte vorbehalten',
        'ja':    '&copy; 2026 Crunch Moonkiss Studios — 全著作権所有',
        'zh-CN': '&copy; 2026 Crunch Moonkiss Studios — 保留所有权利',
        'zh-TW': '&copy; 2026 Crunch Moonkiss Studios — 保留所有權利',
        'pt-BR': '&copy; 2026 Crunch Moonkiss Studios — Todos os direitos reservados',
        'ru':    '&copy; 2026 Crunch Moonkiss Studios — Все права защищены',
    },
    '&gt; SESSION TERMINATED_': {
        'de':    '&gt; SITZUNG BEENDET_',
        'ja':    '&gt; セッション終了_',
        'zh-CN': '&gt; 会话已终止_',
        'zh-TW': '&gt; 工作階段已終止_',
        'pt-BR': '&gt; SESSÃO ENCERRADA_',
        'ru':    '&gt; СЕССИЯ ЗАВЕРШЕНА_',
    },

    # ─── Screenshot alt text ───
    'alt="Night Mode — Hacking Route Choice"': {
        'de':    'alt="Nachtmodus — Hack-Route-Wahl"',
        'ja':    'alt="ナイトモード — ハックルート選択"',
        'zh-CN': 'alt="夜间模式 — 入侵路径选择"',
        'zh-TW': 'alt="夜間模式 — 入侵路徑選擇"',
        'pt-BR': 'alt="Modo Noturno — Escolha de Rota de Hack"',
        'ru':    'alt="Ночной режим — Выбор маршрута взлома"',
    },
    'alt="Day Mode — Corporate Tasks"': {
        'de':    'alt="Tagmodus — Firmenaufgaben"',
        'ja':    'alt="デイモード — 企業タスク"',
        'zh-CN': 'alt="白天模式 — 公司任务"',
        'zh-TW': 'alt="白天模式 — 公司任務"',
        'pt-BR': 'alt="Modo Diurno — Tarefas Corporativas"',
        'ru':    'alt="Дневной режим — Корпоративные задачи"',
    },
    'alt="Leverage — Archive the Dirt, or Leak It for Credits"': {
        'de':    'alt="Druckmittel — Den Dreck archivieren oder gegen Credits leaken"',
        'ja':    'alt="レバレッジ — 闇を保管するか、クレジットのために漏らすか"',
        'zh-CN': 'alt="把柄 — 存档黑料,或泄露换积分"',
        'zh-TW': 'alt="把柄 — 存檔黑料,或洩露換積分"',
        'pt-BR': 'alt="Influência — Arquive a sujeira ou vaze por créditos"',
        'ru':    'alt="Рычаги — Заархивируй компромат или слей за кредиты"',
    },
    'alt="Black Market — Permanent Perks Off the Books"': {
        'de':    'alt="Black Market — Permanente Vorteile außerhalb der Bücher"',
        'ja':    'alt="Black Market — 帳簿外の永続パーク"',
        'zh-CN': 'alt="Black Market — 帐外永久加成"',
        'zh-TW': 'alt="Black Market — 帳外永久加成"',
        'pt-BR': 'alt="Black Market — Vantagens permanentes fora dos registros"',
        'ru':    'alt="Black Market — Постоянные перки в обход бухгалтерии"',
    },
    'alt="Hack In Progress — Breach Detected"': {
        'de':    'alt="Hack in Bearbeitung — Eindringen erkannt"',
        'ja':    'alt="ハック実行中 — 侵入検知"',
        'zh-CN': 'alt="入侵进行中 — 检测到突破"',
        'zh-TW': 'alt="入侵進行中 — 偵測到突破"',
        'pt-BR': 'alt="Invasão Em Progresso — Brecha Detectada"',
        'ru':    'alt="Взлом в процессе — Обнаружено вторжение"',
    },
    'alt="CONDUIT — I See What You Are"': {
        'de':    'alt="KANAL — Ich sehe, was du bist"',
        'ja':    'alt="コンジット — 私はあなたが何者か見えている"',
        'zh-CN': 'alt="导管 — 我看见你是什么"',
        'zh-TW': 'alt="導管 — 我看見你是什麼"',
        'pt-BR': 'alt="CONDUTOR — Eu vejo o que você é"',
        'ru':    'alt="ПРОВОДНИК — Я вижу, кто ты"',
    },
    'alt="Promotion — Employee Performance Review"': {
        'de':    'alt="Beförderung — Mitarbeiter-Leistungsbeurteilung"',
        'ja':    'alt="昇進 — 従業員業績評価"',
        'zh-CN': 'alt="晋升 — 员工绩效考核"',
        'zh-TW': 'alt="晉升 — 員工績效考核"',
        'pt-BR': 'alt="Promoção — Avaliação de Desempenho do Funcionário"',
        'ru':    'alt="Повышение — Оценка работы сотрудника"',
    },
}

# Language picker HTML — gets injected into <nav>'s <ul>.
def language_picker(current_lang):
    items = []
    for code, label in LANG_LABELS.items():
        href = 'index.html' if code == 'en' else f'index.{code}.html'
        cls = 'lang-current' if code == current_lang else ''
        items.append(f'<li class="{cls}"><a href="{href}">{label}</a></li>')
    return (
        '<li style="margin-left: auto; opacity: 0.6;">|</li>\n'
        + '\n'.join(['  ' + i for i in items])
    )

# CSS for the language picker — appended into <style>.
PICKER_CSS = '''
  nav ul li.lang-current a { color: var(--green); border-bottom: 1px solid var(--green); }
  nav ul li a { font-size: 11px; }
'''

def localize(content, lang):
    out = content
    # html lang attribute
    out = out.replace('<html lang="en">', f'<html lang="{lang}">')
    # apply translations
    for src, table in STRINGS.items():
        if lang in table:
            out = out.replace(src, table[lang])
    # inject language picker into nav (replace existing </ul> with picker + </ul>)
    picker = language_picker(lang)
    # Find first </ul> after <nav> and inject picker before it
    nav_start = out.find('<nav>')
    if nav_start >= 0:
        ul_close = out.find('</ul>', nav_start)
        if ul_close >= 0:
            out = out[:ul_close] + picker + '\n  ' + out[ul_close:]
    # inject picker CSS before </style>
    out = out.replace('</style>', PICKER_CSS + '</style>')
    return out

def main():
    src_path = 'index.html'
    with open(src_path, 'r', encoding='utf-8') as f:
        src = f.read()
    # English file: just add picker (no translation)
    en_out = localize(src, 'en')
    with open(src_path, 'w', encoding='utf-8') as f:
        f.write(en_out)
    print(f'updated index.html (en, with language picker)')
    # Translated files
    for lang in LANGS:
        out = localize(src, lang)
        out_path = f'index.{lang}.html'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(out)
        # Quick stats
        translated_keys = sum(1 for s in STRINGS if lang in STRINGS[s])
        print(f'wrote {out_path} ({translated_keys} translated strings)')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
