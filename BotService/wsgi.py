
from flaskr import create_app
from asr.stt_zh_citrinet import STTCitrinet
from tts.tts_mtts import MTTSInferencer
from weathers import WeatherXinzhi

from gevent.pywsgi import WSGIServer

from argparse import ArgumentParser, Namespace


def main(args: Namespace):
    # init ASR and TTS models
    asr_provider = STTCitrinet(args.device)
    tts_provider = MTTSInferencer(
        args.tts_config_path,
        args.tts_state_dict_path,
        args.device)
    # init weather provider
    weather_provider = WeatherXinzhi(
        args.weather_default_location,
        args.weather_api_key_path,)
    app = create_app(
        asr_provider,
        tts_provider,
        weather_provider,
    )
    http_server = WSGIServer(("0.0.0.0", args.port), app)
    print(f"Ready to serve with port {args.port}.")
    http_server.serve_forever()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--device", "-d",
        default="cpu", choices=["cpu", "cuda"],
        help="Device for torch neural network models.")
    parser.add_argument("--port", "-p",
        default=18080, type=int,
        help="The port for http server.")
    parser.add_argument("--tts-config-path", "--tc",
        default="./BotService/fs2_model-aishell3-config.yaml",
        help="File location of mtts config file.")
    parser.add_argument("--tts-state-dict-path", "--ts",
        default="./BotService/mtts-weights/checkpoint_1350000.pth.tar",
        help="File location of state dict for mtts FastSpeech2 model.")
    parser.add_argument("--weather-default-location", "--wd",
        default="北京",
        help="The default city(or ProvinceCity) to provide weather service"
            " when speaker does not tell the city to request.")
    parser.add_argument("--weather-api-key-path", "--wa",
        default="./XinzhiResources/private_key.txt",
        help="File location of Xinzhi API private key.")
    main(parser.parse_args())
