import pandas as pd
from pytube import YouTube
import ffmpeg
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from transformers import pipeline
from datetime import datetime
import librosa
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

    __audioextension = ".wav"
    __textextension = ".csv"

    def __init__(self, outputpath = None):
        '''
        Youtube2Text constructor

        Parameters:
            outputpath (str): Output directory to save audio and csv files
        '''

        if outputpath is None: 

            outputpath = os.path.join(os.path.expanduser('~'), 'youtube2text')

        logger.info(f"Youtube2Text content file saved at path {outputpath}")

        
        # create a speech recognition object
        self.recognizer = sr.Recognizer()

        self.textpath = os.path.join(outputpath, "text")
        self.audiopath = os.path.join(outputpath, "wav")
        self.audiochunkpath = os.path.join(outputpath, "audio-chunks")
        
        self.__createdir(self.textpath)
        self.__createdir(self.audiopath)
        self.__createdir(self.audiochunkpath)

    def url2text(self, urlpath, outfilename = None, mode = 'default'):
        '''
        Convert youtube url to text

        Parameters:
            urlpath (str): Youtube url
            outfilename (str, optional): Filename of output file (.wav, *.csv)
        '''

        if outfilename is None:

            outfilename = self.__generatefiletitle()

        elif outfilename.endswith(self.__audioextension):

            outfilename = outfilename.split(self.__audioextension)[0]
            
        elif outfilename.endswith(self.__textextension):

            outfilename = outfilename.split(self.__textextension)[0]

        self.url2audio(urlpath, audiofilename = outfilename)
        self.audio2text(audiofilename = outfilename, textfilename = outfilename, mode = mode)

    def url2audio(self, urlpath, audiofilename, audiofilepath = None):
        '''
        Convert youtube url to audiofile

        Parameters:
            urlpath (str): Youtube url
            audiofilename (str): Filename of audio file (*.wav)
            audiofilepath (str, optional): Absolute / relative path to save audio file
        '''

        audiofilename = self.__configurefilename(filename = audiofilename, ext = self.__audioextension)

        audiofullpath = self.__configurepath(filename = audiofilename, designatedpath = audiofilepath, fallbackpath = self.audiopath)

        if os.path.exists(audiofullpath):
            logger.info(f'Audio file exists at {audiofullpath}. Skip downloading')

            return
        else:
            logger.info(f'Audio file not exists. Start downloading')

        yt = YouTube(urlpath)

        stream_url = yt.streams[0].url

        audio, err = (
            ffmpeg
            .input(stream_url)
            .output("pipe:", format='wav', acodec='pcm_s16le')  # Select WAV output format, and pcm_s16le auidio codec. My add ar=sample_rate
            .run(capture_stdout=True)
        )

        with open(audiofullpath, 'wb') as f:
            f.write(audio)

        logger.info("Download completed")


    def audio2text(self, audiofilename, audiofilepath = None, textfilename = None, textfilepath = None, mode = 'default'):
        '''
        Convert audio to csv file

        Parameters:
            audiofilename (str): Filename of audio file (*.wav)
            audiofilepath (str, optional): Absolute / relative path to save audio file
            textfilename (str, optional): Filename of text file (*.csv)
            textfilepath (str, optional): Absolute / relative path to save text file
        '''

        audiofilename = self.__configurefilename(filename = audiofilename, ext = self.__audioextension)
        textfilename = self.__configurefilename(filename = textfilename, ext = self.__textextension)

        audiofullpath = self.__configurepath(filename = audiofilename, designatedpath = audiofilepath, fallbackpath = self.audiopath)
        textfullpath = self.__configurepath(filename = textfilename, designatedpath = textfilepath, fallbackpath = self.textpath)

        if os.path.exists(textfullpath): 

            logger.info(f"{textfullpath} exists. Conversion of speech -> text skipped")

        else:

            df = self._get_large_audio_transcription(audiofullpath, mode)

            df.to_csv(textfullpath, index = False)

            logger.info(f"Output text file saved at {textfullpath}")

    def _get_large_audio_transcription(self, audiofullpath, mode):
        '''
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks

        Parameters:
            audiofullpath (str): Absolute/relative path to  text file

        Returns:
            DataFrame: df with rows of texts
        '''


        logging.info(f"Loading {mode} audio2text mode")

        audiofilename = audiofullpath.split(os.sep)[-1].split(self.__audioextension)[0]

        audiochunkfullpath = os.path.join(self.audiochunkpath, audiofilename)

        if not os.path.isdir(audiochunkfullpath):
            os.mkdir(audiochunkfullpath)

        # open the audio file using pydub
        logger.info(f'Wav -> Text: {audiofilename}')
        sound = AudioSegment.from_wav(audiofullpath)

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

        if mode == "huggingface":

            pipe = pipeline("automatic-speech-recognition")


        # process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunkfilename = f"chunk{i}.wav"
            chunkfilepath = os.path.join(audiochunkfullpath, chunkfilename)
            audio_chunk.export(chunkfilepath, format="wav")

            pipe = pipeline("automatic-speech-recognition")

            if mode == 'default':
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

                    
            elif mode == 'huggingface':
                
                y, sr = librosa.load(chunkfilepath)
                audiojson = pipe(y)

                whole_text.append(f"{audiojson['text'].capitalize()}. ")#)

            else:

                logger.critical(f"Audio to text mode not recognizable. Input: {mode}. Select between \"default\" and \"huggingface\".")

            wav_info.append(chunkfilename)
                


        # return as df
        df = pd.DataFrame({"text": whole_text, "wav": wav_info})

        return df
    

    def __generatefiletitle(self):
        '''
        Generate filename according to time stamp if did not provided

        Returns:
            str: timestamp str
        '''
        
        now = datetime.now()

        return now.strftime("%Y%h%d_%H%M%S")

    def __createdir(self, path):
        '''
        Create directory resursively if directories do not exist
        '''
        if not os.path.exists(path):

            os.makedirs(path)
    
    def __configurefilename(self, filename, ext):
        '''
        Append extension to filename if not done

        Returns:
            str: filename with extension
        '''
        if filename is None:
            
            filename = self.__generatefiletitle()

        if not filename.endswith(ext):

            filename = filename + ext
            
        return filename

        
    def __configurepath(self, filename, designatedpath, fallbackpath):
        '''
        Configure path to follows designated path or fallbackpath if former doesnt exist

        Returns:
            str: Absolute path to a file
        '''
        if designatedpath is not None:

            if not os.path.exists(designatedpath):

                logger.warning(f'"{designatedpath}" not exist. Execution abort')
            else:
                return os.path.join(designatedpath, filename)
        else:
             return os.path.join(fallbackpath, filename)