
from requests import post, Response, exceptions as rexc

import uuid
from typing import Tuple, Dict, Any


class NetWorker:

    def __init__(self, remote_url: str, speaker_index: str = "0") -> None:
        self.remote_url = remote_url.rstrip("/")
        self.mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        self.speaker_index = speaker_index
    
    def send_speech(self, fpath: str) -> Tuple[bool, Dict[str, Any]]:
        flag: bool = False
        data: Dict[str, Any] = dict()
        try:
            files = {"wave": open(fpath, "rb")}
            form = {"client_mac": self.mac, "speaker_index": self.speaker_index}
            resp: Response = post(self.remote_url, data=form, files=files)
            if resp.status_code < 400:
                data = resp.json()
                flag = True
            else:
                print(f"Status Code: {resp.status_code}")
        except rexc.ConnectionError:
            pass
        return flag, data
    
    def get_speech(self, url_route: str) -> Tuple[bool, bytes]:
        flag: bool = False
        data: bytes = bytes()
        try:
            form = {"client_mac": self.mac,}
            resp: Response = post(
                self.remote_url + url_route,
                data=form,
                stream=True)
            data = resp.content
            flag = True
        except rexc.ConnectionError:
            pass
        return flag, data
