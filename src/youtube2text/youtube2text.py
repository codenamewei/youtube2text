import pandas as pd
from pytube import YouTube
import ffmpeg
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from datetime import datetime
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
    '''Youtube2Text Class to translates audio to text file'''

    def __init__(self, outputpath = None):
        '''
        Youtube2Text constructor

        Parameters:
            outputpath (str): Output directory to save *.wav, *.csv
        '''

        if outputpath is None: 

            outputpath = os.path.join(os.path.expanduser('~'), 'youtube2text')

        logger.info(f"Youtube2Text content file saved at path {outputpath}")

        # create a speech recognition object
        self.recognizer = sr.Recognizer()

        self.textpath = os.path.join(outputpath, "text")
        self.wavpath = os.path.join(outputpath, "wav")
        self.audiochunkpath = os.path.join(outputpath, "audio-chunks")
        
        self.__createdir(self.textpath)
        self.__createdir(self.wavpath)
        self.__createdir(self.audiochunkpath)

    def url2text(self, urlpath, filetitle = None):
        '''
        Convert youtube url to text

        Parameters:
            urlpath (str): Youtube url
            filetitle (str, optional): Filename of output file (.wav, *.csv)
        '''

        if filetitle is None:

            now = datetime.now()
            filetitle = now.strftime("%Y%h%d_%H%M%S")

        # Write the audio buffer to file for testing
        wavfullpath = os.path.join(self.wavpath, filetitle + ".wav")

        self.url2wav(urlpath, filetitle)

        self.wav2text(wavfullpath)

    def url2wav(self, urlpath, wavfullpath):
        '''
        Convert youtube url to wav

        Parameters:
            urlpath (str): Youtube url
            wavfullpath (str, optional): Full path to output wav file (.wav)
        '''

        if os.path.exists(wavfullpath):
            logger.info(f'Audio file exists. Skip downloading')
        else:
            logger.info(f'Audio file not exists. Start downloading')

            return

        yt = YouTube(urlpath)

        stream_url = yt.streams[0].url

        audio, err = (
            ffmpeg
            .input(stream_url)
            .output("pipe:", format='wav', acodec='pcm_s16le')  # Select WAV output format, and pcm_s16le auidio codec. My add ar=sample_rate
            .run(capture_stdout=True)
        )

        with open(wavfullpath, 'wb') as f:
            f.write(audio)


    def wav2text(self, wavpath):
        '''
        Convert wav to csv file

        Parameters:
            wavpath (str): Full path to wav file
        '''
        wavfile = wavpath.split(os.sep)[-1]

        wavfilename = wavfile.split(".")[0]

        csvfilename = wavfilename + ".csv"
        
        csvfullpath = os.path.join(self.textpath, csvfilename)

        if os.path.exists(csvfullpath): 

            logger.info(f"{csvfilename} exists. Conversion of speech -> text skipped")

        else:

            audiochunkfullpath = os.path.join(self.audiochunkpath, wavfilename)

            if not os.path.isdir(audiochunkfullpath):
                os.mkdir(audiochunkfullpath)

            df = self._get_large_audio_transcription(wavpath, audiochunkfullpath)

            df.to_csv(csvfullpath, index = False)

            logger.info(f"Output text file saved at {csvfullpath}")

    def _get_large_audio_transcription(self, wavpath, audiochunkfullpath):
        '''
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks
        '''
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
    

    def __createdir(self, path):
        '''
        Create directory
        '''
        if not os.path.exists(path):

            os.makedirs(path)
    