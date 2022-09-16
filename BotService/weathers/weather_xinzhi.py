
from typing import final, Tuple, List
from os import PathLike

from weather_base import WeatherBase

import pandas as pd
from urllib.parse import quote
import requests
from requests import get, Response


@final
class WeatherXinzhi(WeatherBase):

    """Xinzhi(心知) weather HTTP API class."""

    url_for_current = (
        "https://api.seniverse.com/v3/weather/now.json"
        "?key={key}&location={location}")
    url_for_daily = (
        "https://api.seniverse.com/v3/weather/daily.json"
        "?key={key}&location={location}&start={start}&days={days}")
    
    err_msgs_zh = {
        "default": "出现意外异常, 请稍后再试. 如有必要, 请联系开发者.",
        "timeout": "连接超时, 请稍后再试.",
        "loc_not_found": "未查到该地区的天气信息. 如果是我听错了, 请联系开发者.",
        "xinzhi_internal_error": "天气服务出现异常, 请稍后再试.",
        "too_frequent": "天气服务请求过于频繁, 请稍后再试.",
    }

    request_for_time = {
        "current": ["当前", "现在"],
        "daily": ["今天", "明天", "后天", "这几天"],
    }

    return_msg_zh_template = {
        "current": "{}当前的天气是: {}, 气温是{}摄氏度.",
        "daily_detail": (
            "{}的天气是: 白天{}, 晚上{}"
            ", 最高{}摄氏度, 最低{}摄氏度, 相对湿度百分之{}."),
    }

    def __init__(self,
            default_loc: str,
            api_key_path: PathLike,
            error_table_path: PathLike) -> None:
        super().__init__(default_loc=default_loc)
        with open(api_key_path) as f:
            self.api_key = f.read()
        self.error_table = pd.read_csv(error_table_path)
    
    def _handle_http_error(self, resp: Response) -> str:
        msg = self.err_msgs_zh["default"]
        if resp.status_code >= 400 and resp.status_code < 500:
            try:
                json_obj: dict = resp.json()
                xinzhi_status: str = json_obj["status"]
                xinzhi_status_code: str = json_obj["status_code"]
                if xinzhi_status_code == "AP010010":
                    # Location not found or error in formatting.
                    msg = self.err_msgs_zh["loc_not_found"]
                elif xinzhi_status_code == "AP010014":
                    # Request too frequent.
                    msg = self.err_msgs_zh["too_frequent"]
                elif xinzhi_status_code == "AP100001":
                    # Data missing in Xinzhi server.
                    msg = self.err_msgs_zh["xinzhi_internal_error"]
            except requests.exceptions.JSONDecodeError:
                pass
        else:
            # Internal Error from Xinzhi server.
            msg = self.err_msgs_zh["xinzhi_internal_error"]
        return msg
    
    def _get_current_weather(self, location_pinyin: str) -> \
            Tuple[Tuple[str, str, str], str]:
        request_url = self.url_for_current.format(
            key=self.api_key,
            location=location_pinyin,
            )
        print(request_url)
        try:
            resp: Response = get(quote(request_url, safe="/:=?&"))
        except requests.exceptions.ConnectionError:
            return ("", "", ""), self.err_msgs_zh["timeout"]
        if resp.status_code > 400:
            err_msg_zh = self._handle_http_error(resp)
            return ("", "", ""), err_msg_zh
        json_results: dict = resp.json()["results"][0]
        location_name_zh: str = json_results["location"]["name"]
        weather_text_zh: str = json_results["now"]["text"]
        temperature_digit: str = json_results["now"]["temperature"]
        temperature_zh: str = self.num_to_hanzi(temperature_digit)
        return (location_name_zh, weather_text_zh, temperature_zh), ""
    
    def _get_daily_weather(self, location_pinyin: str, start=0, days=3) -> \
            Tuple[Tuple[str, List[Tuple[str, str, str, str, str, str]]], str]:
        request_url = self.url_for_daily.format(
            key=self.api_key,
            location=location_pinyin,
            start=start,
            days=days,
        )
        print(request_url)
        try:
            resp: Response = get(quote(request_url, safe="/:=?&"))
        except requests.exceptions.ConnectionError:
            return ("", list()), self.err_msgs_zh["timeout"]
        if resp.status_code > 400:
            err_msg_zh = self._handle_http_error(resp)
            return ("", list()), err_msg_zh

        def parse_daily_data(data: dict) -> Tuple[str, str, str, str, str, str]:
            return (
                self.date_to_hanzi(data["date"]),
                data["text_day"], data["text_night"],
                self.num_to_hanzi(data["high"]),
                self.num_to_hanzi(data["low"]),
                self.num_to_hanzi(data["humidity"]),
            )

        json_results: dict = resp.json()["results"][0]
        location_name_zh: str = json_results["location"]["name"]
        weather_daily: list = [parse_daily_data(d) for d in json_results["daily"]]
        return (location_name_zh, weather_daily), ""
    
    def __call__(self, sentence_zh: str) -> str:
        loc, t = self.parse_location_and_time(sentence_zh)
        if t in self.request_for_time["daily"]:
            (location_zh, weathers_daily), err_msg_zh = self \
                ._get_daily_weather(self.hanzi_to_pinyin(loc))
            if err_msg_zh:
                return err_msg_zh
            else:
                if self.request_for_time["daily"].index(t) == 3:
                    ret_msg = f"{location_zh}"
                    for i in range(3):
                        ret_msg += self.return_msg_zh_template["daily_detail"] \
                            .format(*weathers_daily[i])
                    return ret_msg
                else:
                    return f"{location_zh}" \
                         + self.return_msg_zh_template["daily_detail"] \
                            .format(*weathers_daily[
                                self.request_for_time["daily"].index(t)])
        elif t in self.request_for_time["current"]:
            (location_zh, weather_current, temperature_current), err_msg_zh = self \
                ._get_current_weather(self.hanzi_to_pinyin(loc))
            if err_msg_zh:
                return err_msg_zh
            else:
                return self.return_msg_zh_template["current"].format(
                    location_zh, weather_current, temperature_current)
        else:
            return self.err_msgs_zh["default"]


if __name__ == "__main__":
    import time
    import os
    from pathlib import Path
    os.chdir(Path(__file__).parents[2])
    q_list = [
        # current
        "现在天气如何?",
        "广州天气如何?",
        "广州今天天气如何?",
        "浙江金华市的天气如何?",
        # daily-today
        "今天天气如何?",
        "今天北京天气如何?",
        # daily-tommorow
        "明天广西南宁的天气如何?",
        # daily-the day after tommorow.
        "后天山东青岛的天气如何?",
        # daily-three days
        "这几天江西南昌的天气如何?",
    ]
    weather_provider = WeatherXinzhi(
        "广州", "XinzhiResources/private_key.txt", "XinzhiResources/errors.csv")
    for q in q_list:
        print(q)
        a = weather_provider(q)
        print(a, "\n")
        time.sleep(0.5)
