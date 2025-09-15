from education_bot.misc.data import MAX_CAPTCHA_TRIES


def get_emoji_challenge_text(selected_emoji_name: str, language_code: str, tries: int):
    text = {
        "ru": "👋 Приветствуем!"
        f"\n\nℹ️ Поскольку мы хотим уменьшить количество ботов в комментариях, перед вступлением необходимо выполнить задание. "
        f"У тебя <i>{MAX_CAPTCHA_TRIES - tries}</i> попытка(и)."
        "\n\n❗ Выбери эмоджи, соответствующий этому текстовому описанию:"
        f"\n\n<code>{selected_emoji_name}</code>",
        "eng": "👋 You are welcome!"
        f"\n\nℹ️ Since we want to reduce the number of bots in the comments, you need to complete the task before joining. "
        f"You have <i>{MAX_CAPTCHA_TRIES - tries}</i> attempt(s)."
        "\n\n❗ Choose an emoji that matches this text description:"
        f"\n\n<code>{selected_emoji_name}</code>",
    }

    return text["ru"] if language_code == "ru" else text["eng"]


def get_join_request_reject_text(language_code: str, delta: int | None = None):
    text = {
        "ru": {"hour": " ч", "min": " мин", "day": " 1 день"},
        "eng": {"hour": " h", "min": " min", "day": " 1 day"},
    }

    code = "ru" if language_code == "ru" else "eng"
    text = text[code]

    if delta:
        hours = delta // 3600
        minutes = delta % 3600 // 60
        delta_str = (" " + str(hours) + text["hour"] if hours else "") + (
            " " + str(minutes) + text["min"] if minutes else ""
        )
    else:
        delta_str = text["day"]

    text = {
        "ru": "🚫 Ты был временно заблокирован за неверный ввод эмоджи-каптчи"
        f"\n\n⌛ Попробуй подать заявку через:<i>{delta_str}</i>"
        f'\n\n🆘 Если уверен, что произошла ошибка - пиши нам в <a href="https://t.me/+3Bn-S2viWRtlYTAy">тех. поддержку</a>',
        "eng": "🚫 You have been temporarily blocked for entering an incorrect emoji captcha"
        f"\n\n⌛ Try submitting a request after:<i>{delta_str}</i>"
        f'\n\n🆘 If you are sure that an error has occurred, write to our <a href="https://t.me/+3Bn-S2viWRtlYTAy">tech support</a>',
    }

    return text[code]
