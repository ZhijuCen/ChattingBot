
from asr.stt_zh_citrinet import STTCitrinet
from tts.tts_mtts import MTTSInferencer
from weathers import WeatherXinzhi

from flask import Flask, request, send_file, abort, jsonify
import numpy as np
from scipy.io import wavfile

from typing import Dict, List
from hashlib import sha384
from pathlib import Path
import json
import re



def create_app(
    asr_provider: STTCitrinet,
    tts_provider: MTTSInferencer,
    weather_provider: WeatherXinzhi,
):
    tmp_dir = Path(__file__).parents[2].absolute() / "tmp" / "server"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    app = Flask(__name__, instance_relative_config=True)

    def read_or_create_allowed_wavfile() -> Dict[str, List[str]]:
        nonlocal tmp_dir
        if not (tmp_dir / "allowed_wavfile.json").exists():
            with open(tmp_dir / "allowed_wavfile.json", "w") as f:
                json.dump({}, f)
        with open(tmp_dir / "allowed_wavfile.json") as f:
            allowed_wavfile_dict = json.load(f)
        return allowed_wavfile_dict
    
    def write_allowed_wavfile(allowed_wavfile_dict: dict):
        nonlocal tmp_dir
        with open(tmp_dir / "allowed_wavfile.json", "w") as f:
            json.dump(allowed_wavfile_dict, f)
    
    allowed_wavfile: Dict[str, List[str]] = read_or_create_allowed_wavfile()

    @app.route("/", methods=["POST", "GET"])
    def wave_to_wave():
        """
        Required form data: {
            wave: wav(16bit, int16) file,
            client_mac: MAC Address of client(bot),
        }
        Returns json: {
            wave_url_path: the URL(route part startswith `/`)
                to generated wave(16bit, int16) file,
            service_type: inform which service was provided,
        }
        """
        # Read Only Variables
        nonlocal asr_provider, tts_provider
        nonlocal weather_provider
        nonlocal tmp_dir, allowed_wavfile

        if request.method == "POST":
            wave_file = request.files["wave"]
            client_mac = request.form["client_mac"]
            # asr
            fname = sha384(wave_file.stream.read()).hexdigest()
            fpath = str(tmp_dir / f"{fname}.wav")
            wave_file.stream.seek(0)
            wave_file.save(fpath)
            transcribed_zh = asr_provider.from_file(fpath)
            print("Transcribed voice as:", transcribed_zh)
            # service
            answer_zh: str = "不好意思,我不明白这句话的意思."
            service_type = "not_served"
            if weather_provider.is_for_weather(transcribed_zh):
                answer_zh = weather_provider(transcribed_zh)
                service_type = "weather"
            else:
                pass
            # tts
            answer_zh_wave, ans_sample_rate = tts_provider \
                .string_to_numpy_wave(answer_zh)
            fname_ans = sha384(answer_zh_wave.tobytes()).hexdigest()
            fpath_ans = str(tmp_dir / f"{fname_ans}.wav")
            wavfile.write(fpath_ans, ans_sample_rate, answer_zh_wave)
            wave_url_path = f"/wave/{fname_ans}"
            # finalize or continue session
            if client_mac not in allowed_wavfile:
                allowed_wavfile[client_mac] = [fname_ans]
            else:
                allowed_wavfile[client_mac].append(fname_ans)
            write_allowed_wavfile(allowed_wavfile)
            return jsonify({
                "wave_url_path": wave_url_path,
                "answer_text": answer_zh,
                "service_type": service_type,
            })
        else:
            return "<p>USE POST METHOD</p>"
    
    @app.route("/wave/<wave_name>", methods=["POST"])
    def send_wave(wave_name):
        """
        Required form data: {
            client_mac: MAC Address of client(bot),
        }
        Returns wave file if the file is found the client can access,
            else denies access(403) if client cannot access,
            or file not found(404).
        """
        nonlocal allowed_wavfile, tmp_dir
        if request.method == "POST":
            client_mac = request.form["client_mac"]
            if (not re.fullmatch(r"^[0-9A-Fa-f]+$", wave_name)) or \
                    (not re.fullmatch(r"^[0-9A-Fa-f:]+$", client_mac)):
                abort(401)
            if client_mac in allowed_wavfile and \
                    wave_name in allowed_wavfile[client_mac]:
                return send_file(f"{tmp_dir}/{wave_name}.wav")
            else:
                abort(403)
        else:
            return "<p>USE POST METHOD</p>"

    return app
