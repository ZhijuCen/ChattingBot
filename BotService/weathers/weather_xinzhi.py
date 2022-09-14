
from typing import final, Tuple, List
from os import PathLike

from .weather_base import WeatherBase

import pandas as pd
from urllib.parse import urlencode
import requests
from requests import get, Response


@final
class WeatherXinzhi(WeatherBase):

    """Xinzhi(心知) weather API class."""

    url_for_current = (
        "https://api.seniverse.com/v3/weather/now.json"
        "?key={key}&location={location}")
    url_for_daily = (
        "https://api.seniverse.com/v3/weather/daily.json"
        "?key={key}&location={location}&start={start}&days={days}")

    def __init__(self,
            default_loc: str,
            api_key_path: PathLike,
            error_table_path: PathLike) -> None:
        super().__init__(default_loc=default_loc)
        with open(api_key_path) as f:
            self.api_key = f.read()
        self.error_table = pd.read_csv(error_table_path)
    
    def _handle_http_error(self, resp: Response) -> str:
        if resp.status_code >= 400 and resp.status_code < 500:
            try:
                json_obj: dict = resp.json()
                xinzhi_status: str = json_obj["status"]
                xinzhi_status_code: str = json_obj["status_code"]
                if xinzhi_status_code == "AP010010":
                    # Location not found or error in formatting.
                    pass
                elif xinzhi_status_code == "AP010014":
                    # Request too frequent.
                    pass
                elif xinzhi_status_code == "AP100001":
                    # Data missing in Xinzhi server.
                    pass
                else:
                    pass
            except requests.exceptions.JSONDecodeError:
                pass
        else:
            # Internal Error from Xinzhi server.
            pass
    
    def _get_current_weather(self, location_pinyin: str) -> \
            Tuple[Tuple[str, str, str], str]:
        request_url = self.url_for_current.format(
            key=self.api_key,
            location=location_pinyin,
            )
        resp: Response = get(urlencode(request_url))
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
        resp: Response = get(urlencode(request_url))
        if resp.status_code > 400:
            err_msg_zh = self._handle_http_error(resp)
            return ("", [], err_msg_zh)
        def parse_daily_data(data: dict) -> Tuple[str, str, str, str, str, str]:
            return (
                data["date"],
                data["text_day"], data["text_night"],
                self.num_to_hanzi(data["high"]),
                self.num_to_hanzi(data["low"]),
                self.num_to_hanzi(data["humidity"]),
            )
        json_results: dict = resp.json()["results"][0]
        location_name_zh: str = json_results["location"]["name"]
        weather_daily: list = [parse_daily_data(d) for d in json_results["daily"]]
        return (location_name_zh, weather_daily), ""
