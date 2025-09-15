from database.models import CsMaps, GrenadeSide, GrenadeType


ICONS = {
    "cs_maps": {
        CsMaps.ANCIENT.value: '<emoji id="5404686042403991544">🗿</emoji>',
        CsMaps.ANUBIS.value: '<emoji id="5404329521463718271">🕌</emoji>',
        CsMaps.DUST2.value: '<emoji id="5404362279179282463">🏜</emoji>',
        CsMaps.INFERNO.value: '<emoji id="5404337449973344431">🔥</emoji>',
        CsMaps.MIRAGE.value: '<emoji id="5404639738361573745">🌴</emoji>',
        CsMaps.NUKE.value: '<emoji id="5404811275060406797">☢</emoji>',
        CsMaps.OVERPASS.value: '<emoji id="5404458250223512161">⛲</emoji>',
        CsMaps.VERTIGO.value: '<emoji id="5404546249808440530">🏢</emoji>',
        CsMaps.TRAIN.value: '<emoji id="5381841708357022374">🩹</emoji>',
    },
    "sides": {
        GrenadeSide.CT.value: '<emoji id="5404796874035062813">🔷</emoji>',
        GrenadeSide.T.value: '<emoji id="5404474356350875124">🔶</emoji>',
    },
    "grenades": {
        GrenadeType.FLASH.value: '<emoji id="5404373149741506819">👁️</emoji>',
        GrenadeType.HE.value: '<emoji id="5404879199968193379">💣</emoji>',
        GrenadeType.MOLOTOV.value: '<emoji id="5404704476403623530">🔥</emoji>',
        GrenadeType.SMOKE.value: '<emoji id="5404833995437401258">☁️</emoji>',
        GrenadeType.DECOY.value: '<emoji id="5404833995437401258">☁️</emoji>',  # TODO: Добавить
    },
    "difficult": {
        1: '<emoji id="5402536918078483565">🟢</emoji>',
        2: '<emoji id="5404824018228373756">🟠</emoji>',
        3: '<emoji id="5404408080710527916">🔴</emoji>',
    },
    "special": {
        "hashtags": '<emoji id="5404653658350577926">#️⃣</emoji>',
        "info": '<emoji id="5404521390537730625">ℹ️</emoji>',
        "timing": '<emoji id="5321110076222622107">⌛</emoji>',
        "favourite": '<emoji id="5469935490507493045">❤️</emoji>',
        "ru": '<emoji id="5435975050954035184">🇷🇺</emoji>',
        "eng": '<emoji id="5433714979033337544">🇬🇧</emoji>',
        "app": '<emoji id="5213143553408007250">📱</emoji>',
    },
}

NEW_LINE = "\n"
CS_ROUND_DURATION = 60 + 55  # 1 мин 55 сек
BOT_URL = "https://t.me/cs2education_bot"
CHANNEL_URL = "https://t.me/CS2_education"
