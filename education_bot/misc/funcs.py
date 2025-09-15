import random
from education_bot.misc.data import EMOJI_DICT


def get_random_emojis() -> tuple[list[tuple[str, str]], int]:
    random_keys = random.sample(list(EMOJI_DICT.keys()), 10)
    random_pairs = [(key, EMOJI_DICT[key]) for key in random_keys]
    selected_index = random.randint(0, 9)
    return random_pairs, selected_index
