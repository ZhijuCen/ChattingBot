
from typing import Tuple

from pypinyin import lazy_pinyin
from cn2an import an2cn
import jieba
import jieba.posseg as pseg


class WeatherBase:

    def __init__(self, default_loc: str) -> None:
        jieba.suggest_freq(("今天", "天气"), True)
        jieba.suggest_freq(("广西", "南宁"), True)
        self.default_loc = default_loc
        self.default_time = "现在"

    def parse_location_and_time(self, sentence_zh: str) -> Tuple[str, str]:
        """
        returns: Tuple[str, str], location and time.
        """
        loc, t = self.default_loc, self.default_time
        cutted = pseg.cut(sentence_zh)
        words: Tuple[str]
        flags: Tuple[str]
        words, flags = list(zip(*cutted))
        if "t" in flags:
            i_t = flags.index("t")
        else:
            i_t = -1
        i_ns_list = list()
        for i, flag in enumerate(flags):
            if flag == "ns":
                i_ns_list.append(i)
        ns_list = [words[i] for i in i_ns_list]
        loc = " ".join(ns_list) if i_ns_list else loc
        if "这几天" in sentence_zh:
            t = "这几天"
        else:
            t = words[i_t] if i_t != -1 else t
        loc = loc.replace("省", "")
        loc = loc.replace("自治区", "")
        loc = loc.replace("壮族", "")
        loc = loc.replace("维吾尔族", "")
        loc = loc.replace("市", "")
        return loc, t
    
    def hanzi_to_pinyin(self, hanzi: str) -> str:
        return "".join(lazy_pinyin(hanzi))
    
    def num_to_hanzi(self, digit: str) -> str:
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
    
    def date_to_hanzi(self, date_: str) -> str:
        """from yyyy-mm-dd to hanzi."""
        yy, mm, dd = date_.split("-")
        yy_zh = "".join([self.num_to_hanzi(c) for c in yy]) + "年"
        mm_zh = self.num_to_hanzi(mm) + "月"
        dd_zh = self.num_to_hanzi(dd) + "日"
        return f"{yy_zh}{mm_zh}{dd_zh}"
    
    def is_asked_for_weather(self, sentence: str) -> bool:
        return all((
            "天气" in sentence,
            "好" not in sentence,
            "错" not in sentence,
        ))
