
import numpy as np
from scipy.io import wavfile
from typing import Union, Tuple
from pathlib import Path


class TTSBase:

    """To final transformed voice(wave)."""

    def to_bytes(self, data: np.ndarray,
            sample_rate_hz: int) -> Tuple[bytes, int]:
        """Returns (bytes, int): (wavdata, sample_rate)."""
        return data.tobytes(), sample_rate_hz

    def to_wavfile(self,
            fpath: Union[str, Path],
            data: np.ndarray,
            sample_rate_hz: int) -> None:
        wavfile.write(str(fpath), sample_rate_hz, data)
