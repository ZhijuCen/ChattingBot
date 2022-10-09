
from cn2an import an2cn

import datetime as dt
from typing import Tuple


class DatetimeBase:
    
    def __init__(self):
        pass

    def num_to_hanzi(self, digit: str) -> str:
        if digit.isdigit():
            result = an2cn(digit)
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
    
    def HHMM_to_hanzi(self, HHMM: str) -> str:
        """from HH:MM to hanzi."""
        Hh, Mm = HHMM.split(":")
        HH_zh = self.num_to_hanzi(Hh) + "时"
        MM_zh = self.num_to_hanzi(Mm) + "分"
        return f"{HH_zh}{MM_zh}"
    
    def get_date_today(self):
        return f"今天是{self.get_datetime_now()[0]}"
    
    def get_time_now(self):
        return f"现在是{self.get_datetime_now()[1]}"

    def get_datetime_now(self) -> Tuple[str, str]:
        dt_now: dt.datetime = dt.datetime.now()
        d, t = str(dt_now).split(" ")
        t = ":".join(t.split(":")[:2])
        d_zh = self.date_to_hanzi(d)
        t_zh = self.HHMM_to_hanzi(t)
        return d_zh, t_zh
    
    def is_asked_for_time_now(self, sentence_zh: str):
        return all((
            "现在" in sentence_zh,
            "时间" in sentence_zh or "几点" in sentence_zh,
        ))
    
    def is_asked_for_date_today(self, sentence_zh: str):
        return all((
            "今天" in sentence_zh,
            "日期" in sentence_zh or "几号" in sentence_zh,
        ))
