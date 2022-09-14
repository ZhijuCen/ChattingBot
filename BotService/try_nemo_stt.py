
from nemo.collections.asr.models import EncDecCTCModel, EncDecRNNTModel
from typing import List

if __name__ == "__main__":
    device = "cuda"

    # print(EncDecCTCModel.list_available_models())
    # stt_zh_citrinet_1024_gamma_0_25 transcribes less incorrect chars than belows.
    asr_mandarin_model = EncDecCTCModel \
        .from_pretrained("stt_zh_citrinet_1024_gamma_0_25")
    # stt_zh_citrinet_512 transcribes more incorrect chars
    # asr_mandarin_model = EncDecCTCModel \
    #     .from_pretrained("stt_zh_citrinet_512")
    asr_mandarin_model: EncDecCTCModel = asr_mandarin_model.to(device)

    # EncDecRNNTModel transcribes 2 string of list for 1 audio file.
    # print(EncDecRNNTModel.list_available_models())
    # asr_mandarin_model: EncDecRNNTModel = EncDecRNNTModel \
    #     .from_pretrained("stt_zh_conformer_transducer_large")
    # asr_mandarin_model: EncDecRNNTModel = asr_mandarin_model.to(device)

    transcribed: List[str] = asr_mandarin_model.transcribe(["AudioFiles/hello.wav"])
    print(transcribed)
    