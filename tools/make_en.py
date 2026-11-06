"""Builds en/index.html from index.html (Russian master).
Official wording from the previous English landing (redpanda-ai.net/en/) is reused where it exists.
Run from the site folder:  python3 tools/make_en.py"""
import re

src = open('index.html', encoding='utf-8').read()

# 1) structural blocks (order matters: replace whole blocks before single words)
BLOCKS = [
    ('<html lang="ru">', '<html lang="en">'),
    ('h1{font-family:var(--display);', 'html[lang=en] h1{font-size:clamp(34px,4.9vw,74px)}\nh1{font-family:var(--display);'),
    ('content="RedPanda — ИИ-платформа поддержки восстановления от зависимости. Концепт редизайна."',
     'content="RedPanda — an AI platform for addiction recovery support. Redesign concept."'),
    ('<span class="line"><span>Зависимость</span></span>\n          <span class="line"><span>касается</span></span>\n          <span class="line"><span class="accent">тебя или близкого?</span></span>',
     '<span class="line"><span>Is addiction</span></span>\n          <span class="line"><span>affecting you</span></span>\n          <span class="line"><span class="accent">or a loved one?</span></span>'),
    ('<strong>RedPanda</strong> — ИИ-платформа поддержки восстановления от зависимости. Сейчас в разработке.',
     '<strong>RedPanda</strong> is an AI platform for addiction recovery support. Currently in development.'),
    ('''<span class="row"><span class="w">Знание</span> <span class="w cy">рядом.</span></span>
        <span class="row"><span class="w">Решение</span> <span class="w">за</span> <span class="w or">тобой.</span></span>
        <span class="row"><span class="w">Ещё</span> <span class="w">один</span> <span class="w">шаг.</span></span>''',
     '''<span class="row"><span class="w">Knowledge</span> <span class="w cy">within</span> <span class="w cy">reach.</span></span>
        <span class="row"><span class="w">The</span> <span class="w">decision</span> <span class="w">is</span> <span class="w or">yours.</span></span>
        <span class="row"><span class="w">One</span> <span class="w">more</span> <span class="w">step.</span></span>'''),
    ('Разобраться. Действовать.<br><span class="soft">Видеть изменения.</span>', 'Understand. Take action.<br><span class="soft">See changes.</span>'),
    ('Коротко<br><span class="soft">о главном</span>', 'In short:<br><span class="soft">the essentials</span>'),
    ('Ещё один<br><span class="accent">шаг.</span>', 'One more<br><span class="accent">step.</span>'),
    ('<span>Знание рядом</span><span>Решение за тобой</span><span>Ещё один шаг</span><span>Набор в пилот открыт</span><span>Для себя и для близких</span>',
     '<span>Knowledge within reach</span><span>The decision is yours</span><span>One more step</span><span>Pilot applications open</span><span>For you and your loved ones</span>'),
    ('<span>Сайт разработан компанией<b>SkyMarketing ↗</b></span>', '<span>Website developed by<b>SkyMarketing ↗</b></span>'),
    ('aria-label="Сайт разработан компанией SkyMarketing"', 'aria-label="Website developed by SkyMarketing"'),
]
# 2) sentences / labels (longest first)
TEXT = {
    'Поддержка при зависимости': 'Addiction recovery support',
    'После лечения или когда хотите разобраться в употреблении и двигаться к трезвой жизни.':
        'After treatment, or when you want to understand your substance use and work towards sobriety.',
    'Поддержка для себя, личные границы и общение с близким человеком.':
        'Support for yourself, personal boundaries and communication with someone close to you.',
    'Имя и фамилия не нужны — оставьте контакт, чтобы мы могли ответить.': 'No first or last name needed — leave a contact so we can reply.',
    'RedPanda разрабатывается Nonsense Labs. Готовим пилот платформы и приглашаем в него людей с зависимостью и их близких.':
        'RedPanda is being developed by Nonsense Labs. We’re preparing the platform’s pilot and welcome people with addiction and those close to them.',
    'Три шага, которые помогают перейти от самоанализа к практике — в своём темпе.': 'Three steps that help you move from reflection to practice — at your own pace.',
    'ИИ помогает разобраться в происходящем с опорой на базу клинических знаний и историю общения: замечать повторяющиеся реакции, возможные триггеры и противоречия, которые трудно увидеть самостоятельно.':
        'AI helps you explore your situation using a clinical knowledge base and your conversation history, identifying recurring reactions, possible triggers and contradictions that can be difficult to notice on your own.',
    'Предлагает действия для поддержки восстановления с учётом вашей ситуации. Помогает перейти от самоанализа к практике.':
        'Suggests recovery-supporting actions tailored to your situation, helping you move from reflection to practice.',
    'Показывает динамику состояния и выполненных действий, подводит итоги и помогает подготовиться к разговору со специалистом.':
        'Tracks changes in your state and the actions you complete, summarises patterns and helps you prepare for a conversation with a specialist.',
    'На этапе пилота поможем организовать очную консультацию со специалистом.': 'During the pilot, our team can help arrange an in-person consultation with a specialist.',
    'Кликабельная демонстрация интерфейса: как выглядит разговор, следующий шаг и динамика изменений.':
        'An interactive interface demo: what a conversation, the next step and progress over time look like.',
    'Привет. Как прошёл день? Можно коротко.': 'Hi. How was your day? A few words is enough.',
    'Вечером снова тянуло. Не сорвался, но тяжело.': 'The cravings came back this evening. I held on, but it was hard.',
    'Вы справились — это важно. Похоже, вечер после работы повторяется уже третий раз. Разберём, что ему предшествует?':
        'You made it through — that matters. Evenings after work have come up three times now. Shall we look at what leads up to them?',
    'Платформа в разработке. Сейчас собираем заявки для отбора участников пилота.':
        'The platform is in development. We are accepting applications to select participants for the pilot.',
    'Оставьте контакт и коротко расскажите, почему хотите участвовать. Мы свяжемся с вами и обсудим условия.':
        'Leave your contact details and briefly tell us why you would like to participate. We’ll get in touch to discuss the details.',
    'Нет. Платформа создаётся как дополнительный инструмент поддержки, а не замена врачу или психотерапии.':
        'No. It is being developed as an additional source of support, not a replacement for medical care or therapy.',
    'Да. Заявки принимаем и от близких людей с зависимостью. Формат участия и доступные функции обсудим при отборе.':
        'Yes. We also welcome applications from those close to someone with addiction. We’ll discuss the participation format and available features during selection.',
    'Можно подать заявку, если проблема у близкого?': 'Can I apply if someone close to me has an addiction?',
    'RedPanda заменяет специалиста?': 'Does RedPanda replace a specialist?',
    'RedPanda уже доступна?': 'Is RedPanda available yet?',
    'Как попасть в пилот?': 'How can I join the pilot?',
    'Разрешить аналитические cookie для учёта посещений и заявок? Контакты и текст сообщений не передаются.':
        'Allow analytics cookies to count visits and applications? Contact details and message text are not shared.',
    'RedPanda не заменяет врача или психотерапию.': 'RedPanda is not a substitute for professional medical care or therapy.',
    'Это макет — заявка никуда не отправлена.': 'This is a mock-up — the application was not sent.',
    'В рабочей версии здесь подключается форма сайта.': 'In the live version the site form is connected here.',
    'Согласен на обработку данных согласно': 'I agree to the processing of my data under the',
    'Почему хотите участвовать в пилоте': 'Why would you like to join the pilot?',
    'Email, телефон или Telegram': 'Email, phone or Telegram',
    'Посмотрите, каким будет RedPanda': 'See what RedPanda will look like',
    'Непредвзятый анализ вашей ситуации': 'An unbiased look at your situation',
    'Прогулка 20 минут после работы': 'A 20-minute walk after work',
    'Конкретный следующий шаг': 'A concrete next step',
    'Заявка в пилот RedPanda': 'Apply for the RedPanda pilot',
    'Как работает RedPanda': 'How RedPanda works',
    'Подать заявку в пилот': 'Apply for the pilot',
    'Посмотреть прототип ↗': 'Explore the prototype ↗',
    'Политика конфиденциальности': 'Privacy Policy',
    'политике конфиденциальности': 'Privacy Policy',
    'Условия использования': 'Terms of Use',
    'условия использования': 'Terms of Use',
    'Приложение в разработке': 'In development',
    'Настройки аналитики': 'Analytics settings',
    'Или напишите напрямую': 'Or write to us directly',
    'Последние 7 дней': 'Last 7 days',
    'Отправить запрос': 'Send request',
    'Видеть изменения': 'See changes over time',
    'Открыть прототип': 'Open the prototype',
    'Вопросы о пилоте': 'Pilot FAQ',
    'Послушать панду': 'Hear the panda',
    'Следующий шаг': 'Next step',
    'Конфиденциальность': 'Privacy',
    'Ранний доступ': 'Early access',
    'Как работает': 'How it works',
    'Для близкого': 'For someone close to me',
    'Разобраться': 'Understand',
    'Действовать': 'Take action',
    'Инвесторам': 'For investors',
    'Остановить': 'Stop',
    'О компании': 'Company overview',
    'и принимаю': 'and accept the',
    '● на связи': '● online',
    'О проекте': 'About',
    'Отклонить': 'Decline',
    'Разрешить': 'Allow',
    'Написать…': 'Message…',
    'Компании': 'Companies',
    'Динамика': 'Progress',
    'Прототип': 'Prototype',
    'Для себя': 'For myself',
    'Для кого': 'Audience',
    'Связь ↗': 'Contact ↗',
    'Вопросы': 'FAQ',
    'Разделы': 'Sections',
    'Закрыть': 'Close',
    'Спасибо!': 'Thank you!',
    'Видеть': 'Track',
    'Давай': 'Let’s do it',
}

out = src
for a, b in BLOCKS:
    assert out.count(a) >= 1, ('block not found', a[:60]); out = out.replace(a, b)
for a in sorted(TEXT, key=len, reverse=True):
    assert a in out, ('text not found', a); out = out.replace(a, TEXT[a])

# 3) paths (page lives in /en/), language switch, English legal pages, English talking panda
out = out.replace('href="fonts/fonts.css"', 'href="../fonts/fonts.css"')
out = re.sub(r'(["(])assets/', r'\1../assets/', out)
out = out.replace('../assets/panda-talk.mp4', '../assets/panda-talk-en.mp4')
out = out.replace('https://redpanda-ai.net/privacy.html', 'https://redpanda-ai.net/privacy-en.html').replace('https://redpanda-ai.net/terms.html', 'https://redpanda-ai.net/terms-en.html')
out = out.replace('<div class="lang"><a class="on" href="./" aria-current="page">RU</a><a href="en/" hreflang="en">EN</a></div>',
                  '<div class="lang"><a href="../" hreflang="ru">RU</a><a class="on" href="./" aria-current="page">EN</a></div>')
out = out.replace('<link rel="alternate" hreflang="ru" href="/"><link rel="alternate" hreflang="en" href="/en/">', '<link rel="alternate" hreflang="ru" href="/"><link rel="alternate" hreflang="en" href="/en/">')

left = sorted(set(re.findall(r'[А-Яа-яЁё][А-Яа-яЁё ,.—\-]*', out)))
assert not left, ('untranslated', left)
import os; os.makedirs('en', exist_ok=True)
open('en/index.html', 'w', encoding='utf-8').write(out)
print('en/index.html written, no Cyrillic left')
