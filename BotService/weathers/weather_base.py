
from typing import Tuple

from pypinyin import lazy_pinyin
from cn2an import an2cn
import jieba
import jieba.posseg as pseg


class WeatherBase:

    def __init__(self, default_loc: str) -> None:
        jieba.suggest_freq(("今天", "天气"), True)
        self.default_loc = default_loc
        self.default_time = "今天"

    def parse_location_and_time(self, sentence: str) -> Tuple[str, str]:
        loc, t = self.default_loc, self.default_time
        cutted = pseg.cut(sentence)
        words: Tuple[str]
        flags: Tuple[str]
        words, flags = list(zip(*cutted))
        i_t = flags.index("t")
        i_ns_list = list()
        for i, flag in enumerate(flags):
            if flag == "ns":
                i_ns_list.append(i)
        ns_list = [words[i] for i in i_ns_list]
        loc = " ".join(ns_list) if i_ns_list else loc
        t = words[i_t] if i_t != -1 else t
        return loc, t
    
    @staticmethod
    def hanzi_to_pinyin(hanzi: str) -> str:
        return "".join(lazy_pinyin(hanzi))
    
    @staticmethod
    def num_to_hanzi(digit: str) -> str:
        if digit.isdigit():
            result = an2cn(digit)
            if result.startswith("负"):
                result = result.replace("负", "零下", 1)
            return result
        else:
            raise ValueError(
                f"argument `digit` expects string of digits, "
                f"got {digit}"
            )
    
    @staticmethod
    def is_for_weather(sentence: str) -> bool:
        return all((
            "天气" in sentence,
            "好" not in sentence,
            "错" not in sentence,
        ))
