
from tts_base import TTSBase

import mtts.models.fs2_model as fs2_model
from mtts.synthesize import build_vocoder, normalize, to_int16, TextProcessor
from mtts.text.gp2py import TextNormal

import torch
import numpy as np

import yaml
from typing import Tuple


class MTTSInferencer(TTSBase):

    def __init__(self, config_path: str, state_dict_path: str,
            device: str = "cpu") -> None:
        super().__init__()
        self.device = device
        with open(config_path, "rt") as f:
            self.config = yaml.safe_load(f)
        self.model: fs2_model.FastSpeech2 = fs2_model.FastSpeech2(self.config)
        state_dict = torch.load(state_dict_path, map_location=self.device)
        if "model" in state_dict.keys():
            state_dict = state_dict["model"]
        self.model.load_state_dict(state_dict)
        del state_dict
        self.model = self.model.to(self.device)
        self.vocoder = build_vocoder(self.device, self.config)

        self.text_normalizer = TextNormal(
            self.config["hanzi_embedding"]["vocab"],
            self.config["pinyin_embedding"]["vocab"],
            add_sp1=True, fix_er=True
        )
        self.text_processor = TextProcessor(self.config)

        self.sample_rate = self.config["fbank"]["sample_rate"]
    
    @torch.no_grad()
    def _string_to_token(self, string_zh: str,
            speaker_index: str) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        list_py, list_gp  = self.text_normalizer.gp2py(string_zh)
        line = "|".join([
            "undefined", " ".join(list_py), " ".join(list_gp), speaker_index])
        _, tokens = self.text_processor(line)
        tokens = tokens.to(self.device)
        seq_len = torch.tensor([tokens.shape[1]])
        tokens = tokens.unsqueeze(1)
        seq_len = seq_len.to(self.device)
        max_src_len = torch.max(seq_len)
        return tokens, seq_len, max_src_len
    
    @torch.no_grad()
    def string_to_numpy_wave(self, string_zh: str,
            speaker_index: str = "0") -> Tuple[np.ndarray, int]:
        tokens, seq_len, max_src_len = self._string_to_token(
            string_zh, speaker_index)
        out = self.model(tokens, seq_len,
            max_src_len=max_src_len, d_control=1.)
        # mel_pred, mel_postnet, d_pred, src_mask, mel_mask, mel_len = out
        _, mel_postnet, _, _, _, _ = out

        # convert to waveform
        mel_postnet = mel_postnet[0].transpose(0, 1).detach()
        mel_postnet += self.config["fbank"]["mel_mean"]
        wav = self.vocoder(mel_postnet)
        if self.config["synthesis"]["normalize"]:
            wav = normalize(wav)
        else:
            wav = to_int16(wav)
        return wav, self.sample_rate
    
    def string_to_bytes(self, string_zh: str,
            speaker_index: str = "0") -> Tuple[bytes, int]:
        wav, sample_rate = self.string_to_numpy_wave(string_zh, speaker_index)
        return self.to_bytes(wav, sample_rate)
