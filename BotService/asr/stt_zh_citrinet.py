
from asr_base import ASRBase

from nemo.collections.asr.models import EncDecCTCModel

from typing import Union
from pathlib import Path


class STTCitrinet(ASRBase):
    
    def __init__(self, device: str = "cpu") -> None:
        super().__init__()
        self.model: EncDecCTCModel = EncDecCTCModel \
            .from_pretrained("stt_zh_citrinet_1024_gamma_0_25")
        self.model = self.model.to(device)
    
    def from_file(self, fpath: Union[str, Path]):
        """Return single transcribed string from single wav file."""
        return self.model.transcribe([str(fpath)])[0]
