
import nemo.collections.asr as nemo_asr

if __name__ == "__main__":
    # print(nemo_asr.models.EncDecCTCModel.list_available_models())
    asr_mandarin_model = nemo_asr \
                            .models \
                            .EncDecCTCModel \
                            .from_pretrained("stt_zh_citrinet_1024_gamma_0_25")
    