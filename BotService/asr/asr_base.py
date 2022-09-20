
import numpy as np
from typing import Union
from pathlib import Path


class ASRBase:
    """To final transcribed string."""

    def from_file(self, fpath: Union[str, Path]):
        pass

    def from_bytes(self, bytes_data: bytes, sample_rate_hz=16000):
        pass

    def from_array(self, array: np.ndarray, sample_rate_hz=16000):
        pass
