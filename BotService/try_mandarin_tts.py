

import mtts.models.fs2_model as fs2_model
from mtts.synthesize import build_vocoder, normalize, to_int16, TextProcessor
from mtts.text.gp2py import TextNormal

import torch

from scipy.io import wavfile
import yaml

if __name__ == "__main__":
    duration = 1.0
    device = "cuda"
    with open("BotService/fs2_model-aishell3-config.yaml", "rt") as f:
        config = yaml.safe_load(f)
    model = fs2_model.FastSpeech2(config)
    state_dict = torch.load("BotService/mtts-weights/checkpoint_1350000.pth.tar", map_location=device)
    if "model" in state_dict.keys():
        state_dict = state_dict["model"]
    model.load_state_dict(state_dict)
    model = model.to(device)
    vocoder = build_vocoder(device, config)

    text_normalizer = TextNormal(
        config["hanzi_embedding"]["vocab"],
        config["pinyin_embedding"]["vocab"],
        add_sp1=True, fix_er=True
    )
    text_processor = TextProcessor(config)

    torch.set_grad_enabled(False)

    sr = config["fbank"]["sample_rate"]
    line = "耽误太多时间,事情可就做不完了.劳逸结合是不错,但也别放松过头.无论是冒险还是做生意,机会都稍纵即逝."
    list_py, list_gp  = text_normalizer.gp2py(line)
    line = "|".join(["hello", " ".join(list_py), " ".join(list_gp), "217"])
    # line = "hello|sil ni2 hao3 shi4 jie4 sil|sil 你 好 世 界 sil|0"
    name, tokens = text_processor(line)
    tokens = tokens.to(device)
    seq_len = torch.tensor([tokens.shape[1]])
    tokens = tokens.unsqueeze(1)
    seq_len = seq_len.to(device)
    max_src_len = torch.max(seq_len)
    output = model(tokens, seq_len, max_src_len=max_src_len, d_control=duration)
    # mel_pred, mel_postnet, d_pred, src_mask, mel_mask, mel_len = output
    _, mel_postnet, _, _, _, _ = output

    # convert to waveform using vocoder
    mel_postnet = mel_postnet[0].transpose(0, 1).detach()
    mel_postnet += config['fbank']['mel_mean']
    wav = vocoder(mel_postnet)
    if config['synthesis']['normalize']:
        wav = normalize(wav)
    else:
        wav = to_int16(wav)
    dst_file = f'./AudioFiles/{name}.wav'
    wavfile.write(dst_file, sr, wav)
