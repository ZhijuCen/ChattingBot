
from networking import NetWorker
from speech import SpeechPlayer, SpeechRecoder

from argparse import ArgumentParser, Namespace
from pathlib import Path


class BotClient:

    def __init__(self, remote_url: str, volume_threshold: float = 0.5):
        self.tmp_dir = Path(__file__).parents[1] / "tmp" / "client"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.remote_url = remote_url
        self.sr = SpeechRecoder(self.tmp_dir, volume_threshold)
        self.sr.open_stream()
        self.sp = SpeechPlayer()
        self.networker = NetWorker(remote_url=self.remote_url)

    def loop(self):
        try:
            while True:
                while self.sr.append_frame():
                    print("appended chunk.")
                saved, wav_path = self.sr.try_save_speech()
                if saved:
                    success, responsed_json = self.networker.send_speech(wav_path)
                    if success:
                        got, wav_bytes = self.networker.get_speech(
                            responsed_json["wave_url_path"])
                        if got:
                            fpath = str(self.tmp_dir /
                                f"{responsed_json['wave_url_path'].split('/')[-1]}.wav")
                            with open(fpath, "wb") as f:
                                f.write(wav_bytes)
                            print("Ready to answer with text:", responsed_json["answer_text"])
                            self.sp.play_speech(fpath)
                            print("End of answer.")
                else:
                    print("No voice to send.")
        except KeyboardInterrupt:
            pass
        finally:
            self.sr.close()
            self.sp.close()


def main(args: Namespace):
    bot = BotClient(args.url, args.volume_threshold)
    bot.loop()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--url", "-u",
        required=True, help="The link to compute center.")
    parser.add_argument("--volume-threshold", "--vt",
        default=0.5, type=float,
        help="The volume threshold that treat wave form as speech.")
    main(parser.parse_args())
