#!/usr/bin/env python3
"""
One-shot patcher that adds Vietnamese (`vi`) to _localize.py. Idempotent —
running twice is a no-op.

Run from the press-kit repo root:
    python3 _add_vi.py
"""
import re, os, sys

NEW_LANG = 'vi'
NEW_LABEL = 'VI'  # short Latin abbreviation matching DE/RU/PT-BR/etc.

# Vietnamese translations keyed by English source. Conventions:
#   - HTML tags / entities preserved exactly
#   - "Crunch Moonkiss Studios", "Remain at Your Desk", "Steam", "BLACK MARKET" stay English
#   - CONDUIT (when spoken) → ỐNG DẪN (matches in-game convention; see CLAUDE.md)
#   - "Press kit" → "HỒ SƠ BÁO CHÍ"
T = {
    'Remain At Your Desk — Press Kit | Crunch Moonkiss Studios':
        'Remain At Your Desk — Hồ Sơ Báo Chí | Crunch Moonkiss Studios',
    '<div class="logo">PRESS KIT</div>':
        '<div class="logo">HỒ SƠ BÁO CHÍ</div>',
    '<a href="#about">About</a>':       '<a href="#about">Giới thiệu</a>',
    '<a href="#capsules">Assets</a>':   '<a href="#capsules">Tài nguyên</a>',
    '<a href="#media">Media</a>':       '<a href="#media">Truyền thông</a>',
    '<a href="#press">Press</a>':       '<a href="#press">Báo chí</a>',
    '<a href="#team">Developer</a>':    '<a href="#team">Nhà phát triển</a>',
    '<a href="#contact">Contact</a>':   '<a href="#contact">Liên hệ</a>',
    '&gt; PRESS KIT — CRUNCH MOONKISS STUDIOS':
        '&gt; HỒ SƠ BÁO CHÍ — CRUNCH MOONKISS STUDIOS',
    '<div class="subtitle">Cyberpunk Incremental Clicker</div>':
        '<div class="subtitle">Clicker Incremental Cyberpunk</div>',
    '<div class="label">Developer</div>':       '<div class="label">Nhà phát triển</div>',
    '<div class="label">Platform</div>':        '<div class="label">Nền tảng</div>',
    '<div class="label">Genre</div>':           '<div class="label">Thể loại</div>',
    '<div class="label">Demo</div>':            '<div class="label">Demo</div>',
    '<div class="label">Full Release</div>':    '<div class="label">Phát hành chính thức</div>',
    '<div class="value demo-date">May 19, 2026</div>':
        '<div class="value demo-date">19 tháng 5, 2026</div>',
    '<div class="value">Cyberpunk Incremental Clicker</div>':
        '<div class="value">Clicker Incremental Cyberpunk</div>',
    '<div class="value">Late 2026</div>':
        '<div class="value">Cuối 2026</div>',
    'WATCH TRAILER &rsaquo;':       'XEM TRAILER &rsaquo;',
    'VIEW ASSETS':                  'XEM TÀI NGUYÊN',
    'WISHLIST ON STEAM &rsaquo;':   'THÊM VÀO DANH SÁCH MONG MUỐN STEAM &rsaquo;',
    '<h2>About the Game</h2>':      '<h2>Về Trò Chơi</h2>',
    '<p class="about-lede">You have <span class="twojobs">two jobs</span>. <em>One is fake.</em></p>':
        '<p class="about-lede">Bạn có <span class="twojobs">hai công việc</span>. <em>Một là giả.</em></p>',
    '<p>The first is fake. You click through tasks, file reports, sync databases, and collect a paycheck. Nobody knows what you actually do. You just need to look busy enough to get promoted.</p>':
        '<p>Công việc đầu tiên là giả. Bạn click qua các nhiệm vụ, nộp báo cáo, đồng bộ cơ sở dữ liệu, và lãnh lương. Không ai biết bạn thật sự làm gì. Bạn chỉ cần trông có vẻ bận đủ để được thăng chức.</p>',
    '<p>The second job is the real one. After hours, you break into the corporate network to pull data that isn\'t yours. You route through systems, crack firewalls, stay ahead of whoever\'s paying attention.</p>':
        "<p>Công việc thứ hai mới là thật. Sau giờ làm, bạn xâm nhập vào mạng nội bộ công ty để rút những dữ liệu không thuộc về mình. Bạn định tuyến qua các hệ thống, phá tường lửa, đi trước những kẻ đang theo dõi.</p>",
    'data-label="BOILERPLATE"':     'data-label="MÔ TẢ CHÍNH THỨC"',
    '<p><em>Remain at Your Desk</em> is a cyberpunk incremental clicker with two jobs. By day you click tasks and get promoted. By night you hack the corporate network you\'re supposed to protect. Risk vs. reward, suspicion vs. progression, and an AI in the system that\'s been watching longer than you have.</p>':
        "<p><em>Remain at Your Desk</em> là một game cyberpunk incremental clicker với hai công việc. Ban ngày bạn click nhiệm vụ và được thăng chức. Ban đêm bạn hack mạng nội bộ mà đáng lẽ bạn phải bảo vệ. Rủi ro đổi phần thưởng, nghi ngờ đổi tiến độ, và một AI trong hệ thống đã theo dõi lâu hơn bạn nghĩ.</p>",
    '<span class="term">Risk</span>':           '<span class="term">Rủi ro</span>',
    '<span class="term">Two Economies</span>':  '<span class="term">Hai Nền Kinh Tế</span>',
    '<span class="term">Cover</span>':          '<span class="term">Vỏ Bọc</span>',
    '<p>Every hack raises suspicion. Push too far and security starts paying attention. An audit lands on your desk and then an interrogation follows. Suspicion bleeds off during your day-job clicks, so the corporate grind is the cooldown for the part of the game that\'s actually fun.</p>':
        "<p>Mỗi lần hack đều làm tăng nghi ngờ. Đi quá xa thì bộ phận an ninh sẽ chú ý. Một cuộc kiểm toán đáp xuống bàn bạn, rồi đến một cuộc thẩm vấn. Nghi ngờ giảm dần khi bạn click công việc ban ngày, nên cày corporate chính là thời gian hồi cho phần chơi thật sự thú vị.</p>",
    '<p>Credits come from the day job. They buy upgrades, automation, and time. Intel comes from hacks. Intel only drops on hacks, so there\'s less to hoard and more to spend deliberately on big targets. The two economies pull against each other.</p>':
        "<p>Tín dụng đến từ công việc ban ngày. Chúng dùng để mua nâng cấp, tự động hoá, và thời gian. Thông tin đến từ hack. Thông tin chỉ rơi khi hack, nên ít thứ để tích trữ và nhiều thứ để chi tiêu có chủ đích cho mục tiêu lớn. Hai nền kinh tế kéo nhau ngược chiều.</p>",
    '<p>Personas let you hack as someone else. The janitor, the IT admin, the consultant nobody questions. Each has its own bonuses but wears out, and switching mid-shift carries its own risk.</p>':
        "<p>Nhân dạng cho phép bạn hack với danh tính người khác. Người lao công, IT admin, chuyên viên tư vấn không ai nghi ngờ. Mỗi loại có lợi ích riêng nhưng dần hao mòn, và chuyển nhân dạng giữa ca cũng mang rủi ro của nó.</p>",
    '<div class="head">Leverage</div>':         '<div class="head">Đòn Bẩy</div>',
    '<p>Not everything is worth selling. Hack the same target enough times and you build a dossier. This creates permanent leverage that survives audits, terminations, and even prestige resets.</p>':
        "<p>Không phải thứ gì cũng nên bán. Hack đủ nhiều lần cùng một mục tiêu và bạn xây được một hồ sơ. Điều này tạo ra đòn bẩy vĩnh viễn sống sót qua kiểm toán, sa thải, và cả prestige reset.</p>",
    '<div class="head">Prestige</div>':         '<div class="head">Thăng Tiến</div>',
    '<div class="head">CONDUIT</div>':          '<div class="head">ỐNG DẪN</div>',
    "<p>There's something already inside the network. It noticed you first. It will speak to you eventually. What it wants you to do — and what it actually is — depends on how you've been playing.</p>":
        "<p>Có thứ gì đó đã ở sẵn trong mạng. Nó để ý bạn trước. Cuối cùng nó sẽ nói chuyện với bạn. Nó muốn bạn làm gì — và nó thật sự là gì — tuỳ vào cách bạn đã chơi.</p>",
    '<p>Get promoted and you start over with stronger multipliers and personas that stick. Get caught and you start over with nothing.</p>':
        "<p>Được thăng chức và bạn làm lại từ đầu với hệ số mạnh hơn và nhân dạng được giữ lại. Bị bắt và bạn làm lại từ đầu với hai bàn tay trắng.</p>",
    '<h2>Capsule Art &amp; Key Images</h2>':    '<h2>Capsule Art &amp; Hình Ảnh Chính</h2>',
    '<h2>Capsule Art & Key Images</h2>':        '<h2>Capsule Art & Hình Ảnh Chính</h2>',
    '<h2>Screenshots &amp; Media</h2>':         '<h2>Ảnh chụp &amp; Truyền thông</h2>',
    '<h2>Screenshots & Media</h2>':             '<h2>Ảnh chụp & Truyền thông</h2>',
    '<h2>Featured In</h2>':                     '<h2>Được Đăng Tải</h2>',
    '<h2>Developer</h2>':                       '<h2>Nhà Phát Triển</h2>',
    '<h2>Contact</h2>':                         '<h2>Liên Hệ</h2>',
    'Main Capsule (460&times;215)':             'Capsule Chính (460&times;215)',
    'Header / Library Capsule (460&times;215)': 'Header / Library Capsule (460&times;215)',
    'Hero Art (1920&times;620)':                'Hero Art (1920&times;620)',
    '4K Marketing Thumbnail (3840&times;2160)': 'Hình Marketing 4K (3840&times;2160)',
    'Library Capsule</div>':                    'Library Capsule</div>',
    'Small Capsule (231&times;87)':             'Capsule Nhỏ (231&times;87)',
    'Vertical Capsule (374&times;448)':         'Capsule Dọc (374&times;448)',
    '&gt; Demo Announcement Trailer':           '&gt; Trailer Công Bố Demo',
    '&gt; Launch Trailer':                      '&gt; Trailer Ra Mắt',
    'CLICK TO ENLARGE':                         'CLICK ĐỂ PHÓNG TO',
    'DOWNLOAD ALL ASSETS (.ZIP)':               'TẢI TẤT CẢ TÀI NGUYÊN (.ZIP)',
    'DOWNLOAD 4K TRAILER':                      'TẢI TRAILER 4K',
    'Taiwan &middot; Gaming News':              'Đài Loan &middot; Tin Tức Game',
    'Japan &middot; Industry Trade':            'Nhật Bản &middot; Báo Ngành',
    'Korea &middot; Indie Coverage':            'Hàn Quốc &middot; Tin Indie',
    'Podcast &middot; Episode 310':             'Podcast &middot; Tập 310',
    'Solo Developer / Composer — Crunch Moonkiss Studios':
        'Nhà Phát Triển / Nhà Soạn Nhạc Độc Lập — Crunch Moonkiss Studios',
    'Jared D. is a NYC-based solo indie developer and award-winning film composer.':
        'Jared D. là một nhà phát triển indie độc lập tại NYC và là nhà soạn nhạc phim đoạt giải.',
    '<div class="clabel">Press Inquiries</div>':    '<div class="clabel">Yêu Cầu Báo Chí</div>',
    '<div class="clabel">Steam Page</div>':         '<div class="clabel">Trang Steam</div>',
    '<div class="clabel">Studio</div>':             '<div class="clabel">Studio</div>',
    '<div class="clabel">Location</div>':           '<div class="clabel">Vị Trí</div>',
    'New York City, USA':                           'Thành phố New York, Hoa Kỳ',
    'Remain At Your Desk on Steam':                 'Remain At Your Desk trên Steam',
    '&copy; 2026 Crunch Moonkiss Studios — All rights reserved':
        '&copy; 2026 Crunch Moonkiss Studios — Mọi quyền được bảo lưu',
    '&gt; SESSION TERMINATED_':                     '&gt; PHIÊN ĐÃ KẾT THÚC_',
    'alt="Night Mode — Hacking Route Choice"':      'alt="Chế Độ Đêm — Lựa Chọn Tuyến Hack"',
    'alt="Day Mode — Corporate Tasks"':             'alt="Chế Độ Ngày — Nhiệm Vụ Công Ty"',
    'alt="Leverage — Archive the Dirt, or Leak It for Credits"':
        'alt="Đòn Bẩy — Lưu Trữ Hay Rò Rỉ Lấy Tín Dụng"',
    'alt="Black Market — Permanent Perks Off the Books"':
        'alt="Black Market — Đặc Quyền Vĩnh Viễn Ngoài Sổ Sách"',
    'alt="Hack In Progress — Breach Detected"':     'alt="Đang Hack — Phát Hiện Xâm Nhập"',
    'alt="CONDUIT — I See What You Are"':           'alt="ỐNG DẪN — Tôi Thấy Ngươi Là Gì"',
    'alt="Promotion — Employee Performance Review"': 'alt="Thăng Chức — Đánh Giá Hiệu Suất Nhân Viên"',
}


def patch():
    path = '_localize.py'
    src = open(path, encoding='utf-8').read()

    # Already patched?
    if "'vi':" in src and f"'{NEW_LANG}'" in src and "LANGS = " in src:
        # Check if vi is in LANGS list
        m = re.search(r"^LANGS\s*=\s*\[(.*?)\]", src, re.MULTILINE | re.DOTALL)
        if m and "'vi'" in m.group(1):
            print('Already patched. Nothing to do.')
            return

    # 1) Add 'vi' to LANGS
    src = re.sub(
        r"^(LANGS\s*=\s*\[[^\]]*?)(\])",
        lambda m: m.group(1).rstrip().rstrip(',') + ", 'vi']",
        src,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )

    # 2) Add 'vi' label to LANG_LABELS (insert before the closing })
    src = re.sub(
        r"(LANG_LABELS\s*=\s*\{[^}]*?)(\n\})",
        lambda m: m.group(1).rstrip() + f"\n    '{NEW_LANG}':    '{NEW_LABEL}',\n" + "}",
        src,
        count=1,
        flags=re.DOTALL,
    )

    # 3) For each STRINGS entry, splice in a 'vi': '<translation>' line
    #    before the closing '},'. Match on the English key and find the next
    #    closing brace.
    missed = []
    for en_key, vi_val in T.items():
        # Escape the key for use as a regex
        # We want to find: '<en_key>': { ... },
        # where ... contains other language entries.
        # Use raw substring search instead of regex on the key (keys contain
        # regex meta-chars, HTML, etc.).
        key_repr = repr(en_key)  # produces python-quoted form matching source
        # Find the start of this entry
        idx = src.find(f"    {key_repr}: {{")
        if idx < 0:
            # Maybe alternate quote style (the source uses both ' and " for keys
            # depending on whether the value contains a single quote).
            # Try the other quoting.
            alt = '"' + en_key.replace('"', '\\"') + '"'
            idx = src.find(f"    {alt}: {{")
            if idx < 0:
                missed.append(en_key[:80])
                continue
            key_repr = alt
        # Find the matching closing '}' for this dict (next "\n},\n" or "\n}," or "\n}")
        # Easiest: scan for the next "},\n" or "},$"
        end = src.find('\n},', idx)
        if end < 0:
            end = src.find('\n}', idx)
            if end < 0:
                missed.append(en_key[:80])
                continue
        # Already has 'vi'?
        block = src[idx:end]
        if "'vi':" in block or '"vi":' in block:
            continue
        # Splice the vi line before the closing brace.
        # Use repr() for vi_val to handle quoting consistently with the source.
        vi_line = f"\n        'vi':    {repr(vi_val)},"
        # If vi_val contains a single quote, repr() will use double quotes — fine.
        src = src[:end] + vi_line + src[end:]

    open(path, 'w', encoding='utf-8').write(src)

    print(f"Patched _localize.py: added '{NEW_LANG}' to LANGS, LANG_LABELS, and {len(T) - len(missed)} STRINGS entries.")
    if missed:
        print(f"WARN: {len(missed)} keys not found in _localize.py:")
        for k in missed:
            print(f"  - {k}")


if __name__ == '__main__':
    patch()
