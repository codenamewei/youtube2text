import pandas as pd
from pytube import YouTube
import ffmpeg
import os
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
from datetime import datetime
import pandas as pd
import logging
import sys

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

class Youtube2Text:
    """Youtube2Text Class to translates audio to text file"""

    def __createdir(path):

        if not os.path.exists(path):

            os.makedirs(path)

    def __init__(self, rootpath = None):


        if rootpath is None: 

            rootpath = os.path.join(os.path.expanduser('~'), 'youtube2text')

        logger.info(f"Youtube2Text content file saved at path {rootpath}")

        # create a speech recognition object
        self.recognizer = sr.Recognizer()

        self.textpath = os.path.join(rootpath, "text")
        self.wavpath = os.path.join(rootpath, "wav")
        self.audiochunkpath = os.path.join(rootpath, "audio-chunks")
        
        self.__createdir(self.textpath)
        self.__createdir(self.wavpath)
        self.__createdir(self.audiochunkpath)

    def url2text(self, urlpath, filetitle = None):

        if filetitle is None:

            now = datetime.now()
            filetitle = now.strftime("%Y%h%d_%H%M``````%S")

        # Write the audio buffer to file for testing
        wavfullpath = os.path.join(self.wavpath, filetitle + ".wav")

        if os.path.exists(wavfullpath):
            logger.info(f'Audio file of {filetitle} exists. Skip downloading')
        else:
            logger.info(f'File: {filetitle} not exists. Start downloading')

            self.url2wav(urlpath, wavfullpath)

        self.wav2text(wavfullpath)

    def url2wav(self, urlpath, wavpath):
        
        yt = YouTube(urlpath)

        stream_url = yt.streams.all()[0].url

        audio, err = (
            ffmpeg
            .input(stream_url)
            .output("pipe:", format='wav', acodec='pcm_s16le')  # Select WAV output format, and pcm_s16le auidio codec. My add ar=sample_rate
            .run(capture_stdout=True)
        )

        with open(wavpath, 'wb') as f:
            f.write(audio)


    def wav2text(self, wavpath):

        wavfile = wavpath.split(os.sep)[-1]

        filename = wavfile.split(".")[0]
        
        csvfullpath = os.path.join(self.textpath, filename + ".csv")

        if os.path.exists(csvfullpath): 

            logger.info(f"{csvfullpath} exist. Conversion of speech -> text skipped")

        else:

            audiochunkfullpath = os.path.join(self.audiochunkpath, filename)

            if not os.path.isdir(audiochunkfullpath):
                os.mkdir(audiochunkfullpath)

            df = self._get_large_audio_transcription(wavpath, audiochunkfullpath)

            df['label'] = 0

            df.to_csv(csvfullpath, index = False)

            logger.info(f"Output text file saved at {csvfullpath}")


    # a function that splits the audio file into chunks
    # and applies speech recognition
    def _get_large_audio_transcription(self, wavpath, audiochunkfullpath):
        """
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks
        """
        # open the audio file using pydub
        logger.info(f'Wav -> Text: {wavpath.split(os.sep)[-1]}')
        sound = AudioSegment.from_wav(wavpath)
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks = split_on_silence(sound,
            # experiment with this value for your target audio file
            min_silence_len = 500,
            # adjust this per requirement
            silence_thresh = sound.dBFS-14,
            # keep the silence for 1 second, adjustable as well
            keep_silence=500,
        )

        whole_text = []
        wav_info = []

        # process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunkfilename = f"chunk{i}.wav"
            chunkfilepath = os.path.join(audiochunkfullpath, chunkfilename)
            audio_chunk.export(chunkfilepath, format="wav")
            # recognize the chunk
            with sr.AudioFile(chunkfilepath) as source:
                audio_listened = self.recognizer.record(source)
                # try converting it to text
                try:
                    text = self.recognizer.recognize_google(audio_listened)
                except sr.UnknownValueError as e:
                    whole_text.append("None")
                else:
                    text = f"{text.capitalize()}. "
                    whole_text.append(text)

                wav_info.append(chunkfilename)

        # return as df
        df = pd.DataFrame({"text": whole_text, "wav": wav_info})


        return df
    

    