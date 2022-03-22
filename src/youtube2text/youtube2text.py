import pandas as pd
from pytube import YouTube
import speech_recognition as sr
import ffmpeg
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
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

    __audioextension = ["flac", "wav"]
    __textextension = "csv"
    __asrmode = ["default"]

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
        self.audiopath = os.path.join(outputpath, "audio")
        self.audiochunkpath = os.path.join(outputpath, "audio-chunks")
        
        self.__createdir(self.textpath)
        self.__createdir(self.audiopath)
        self.__createdir(self.audiochunkpath)

    def url2text(self, urlpath, outfile = None, audioformat = "flac", audiosamplingrate=16000, asrmode = 'default'):
        '''
        Convert youtube url to text

        Parameters:
            urlpath (str): Youtube url
            outfile (str, optional): File path/name of output file (.csv)
            audioformat (str, optional): Audioformat supported in self.__audioextension
            audiosamplingrate (int, optional): Audio sampling rate
            asrmode (str, optional): ASR mode in self.__asrmode
        '''
        
        outfilepath = None
        audiofile = None

        if outfile is not None:

            if outfile.endswith(self.__textextension) is False:

                logger.warning("Text file poorly defined. outfile have to ends with .csv")
                
                outfile = None

            elif((outfile.find(os.sep) != -1) and (outfile.endswith(self.__textextension))):
                textfile = outfile.split(os.sep)[-1]
                outfilepath = outfile[0:len(outfile)  - len(textfile) - 1]

            else:
                if(outfile.endswith(self.__textextension)):
                    
                    rawfilename = outfile.split(".")[0]
                    filename = self.__removeinvalidcharacter(rawfilename)
                    textfile =  filename + "." + self.__textextension
                    
                else:    
                    filename = self.__generatefiletitle()
                    textfile = filename + "." + self.__textextension
        
                if audioformat not in self.__audioextension:

                    defaultaudioformat = self.__audioextension[0]
                    logger.warning(f"Selected audio format not permitted: {audioformat}. Fall back to default: {defaultaudioformat}")
                    audioformat = self.__audioextension[0]

                audiofile = filename + "." + audioformat

        else:

            filename = self.__generatefiletitle()
            audiofile = filename + "." + self.__audioextension[0]
            textfile = filename + "." + self.__textextension
        
        audiofile = self.__configurepath(audiofile, outfilepath, self.audiopath)
        textfile = self.__configurepath(textfile, outfilepath, self.textpath)

        self.url2audio(urlpath, audiofile = audiofile, audiosamplingrate = audiosamplingrate)
        self.audio2text(audiofile = audiofile, textfile = textfile, asrmode = asrmode)

    def url2audio(self, urlpath, audiofile = None, audiosamplingrate=16000):
        '''
        Convert youtube url to audiofile

        Parameters:
            urlpath (str): Youtube url
            audiofile (str, optional): File path/name to save audio file
            audiosamplingrate (int, optional): Audio sampling rate
        '''
        
        audioformat = self.__audioextension[0]
        outfilepath = None

        if(audiofile is not None) and (audiofile.find(".") != -1):

            audioformat = audiofile.split(".")[-1]
            if audioformat in self.__audioextension:
                
                if audiofile.find(os.sep) != -1:
                    buffer = audiofile.split(os.sep)[-1]
                    outfilepath = audiofile[:len(audiofile) - len(buffer) - 1]
                    audiofile = buffer
            
            else:
                audiofile = self.__generatefiletitle() + "." + self.audiofilename[0]

        else:

            audiofile = self.__generatefiletitle() + "." +  self.__audioextension[0]

        audiofile = self.__configurepath(audiofile, outfilepath, self.audiopath)

        if os.path.exists(audiofile):

            logger.info(f"Audio file exist at {audiofile}. Download skipped")

        else:

            yt = YouTube(urlpath)

            stream_url = yt.streams[0].url

            acodec = 'pcm_s16le' if audioformat == 'wav' else audioformat
            
            audio, err = (
                ffmpeg
                .input(stream_url)
                .output("pipe:", format=audioformat,  **{'ar': str(audiosamplingrate),'acodec': acodec})
                .run(capture_stdout=True)
            )

            with open(audiofile, 'wb') as f:
                f.write(audio)

            logger.info(f"Download completed at {audiofile}")


    def audio2text(self, audiofile, textfile = None, asrmode = 'default'):
        '''
        Convert audio to csv file

        Parameters:
            audiofile (str): File path/name of audio file
            textfile (str, optional): File path/name of text file (*.csv)
            asrmode (str, optional): ASR mode in self.__asrmode
        '''

        ext = audiofile.split(".")[-1]
        audiochunkpath = None
        audiochunkfolder = None

        if ext not in self.__audioextension:

            logger.error(f"Audio file has to end with extension in {self.__audioextension}. Operation abort.")
 
            return

        if os.path.exists(audiofile) is False:

            logger.error(f"Audio file not exist: {audiofile}. Execution abort.")

            return

        if (textfile is not None) and (os.path.exists(textfile)):

            logger.info(f"{textfile} exists. Conversion of speech -> text skipped")
            return

        elif textfile is not None and textfile.find(os.sep) != -1:

            textfilewithext = textfile.split(os.sep)[-1]
            textfilepath = textfile[:len(textfile) - len(textfilewithext) - 1]
            
            if not os.path.exists(textfilepath):
                logger.warning(f"Text file path {textfilepath} do not exist. Fall back to default")
                textfile = None
            else:

                audiochunkfolder = textfilewithext.split(".")[0]

                if textfile.find(self.textpath) != -1:
                
                    audiochunkfolder = textfilewithext.split(".")[0]
                    audiochunkpath = self.audiochunkpath
                else: 
                    audiochunkpath = textfile[:len(textfile) - len(textfilewithext)]
                    

        if textfile is None:

            textfilename = self.__generatefiletitle()
            audiochunkfolder = textfilename #both audio chunk folder and csv possess the same name
            textfile = self.__configurepath(audiochunkfolder + "." + self.__textextension, None, self.textpath)
    

        df = self._get_large_audio_transcription(audiofile, audiochunkfolder = audiochunkfolder , asrmode = asrmode, audiochunkpath = audiochunkpath)

        df.to_csv(textfile, index = False)

        logger.info(f"Output text file saved at {textfile}")

    def _get_large_audio_transcription(self, audiofullpath, audiochunkfolder, asrmode, audiochunkpath = None):
        '''
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks

        1Parameters:
            audiofullpath (str): Absolute/relative path to text file
            audiochunkfolder (str): folder name of audio chunk
            asrmode (str): ASR mode in self.__asrmode
            audiochunkpath (str, optional): Absolute/relative path to save snippet of audio file
        
        Returns:
            DataFrame: df with rows of texts
        '''


        logger.info(f"Loading {asrmode} audio2text mode")

        audiochunkpath = self.__configurepath(audiochunkfolder, audiochunkpath, self.audiochunkpath)

        if not os.path.isdir(audiochunkpath):
            os.mkdir(audiochunkpath)

        # open the audio file using pydub
        logger.info(f'Audio -> Text: {audiofullpath}')
        #logger.info(f"Audio chunk path: {audiochunkpath}")

        audioformat = audiofullpath.split(".")[-1]

        sound = None
        if audioformat == "wav":

            sound = AudioSegment.from_wav(audiofullpath)
    
        elif audioformat == "flac":

            sound = AudioSegment.from_file(audiofullpath, audioformat)
        
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
        audio_file = []

        # process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunkfilename = f"chunk{i}." + audioformat 
            chunkfilepath = os.path.join(audiochunkpath, chunkfilename)
            audio_chunk.export(chunkfilepath, format=audioformat)

            if asrmode == 'default':
                
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
            else:

                logger.critical(f"Audio to text mode not recognizable. Input: {asrmode}. .")

            audio_file.append(os.path.join(audiochunkfolder, chunkfilename))
                


        # return as df
        df = pd.DataFrame({"text": whole_text, "file": audio_file})

        return df
    

    def __removeinvalidcharacter(self, strin):
        '''
        Removal of invalid character when creating folder/filename

        Parameters:
            strin (str): Input string

        Returns:
            str: Processed valid string
        '''
        
        removal_list= [i for i in r"\/:*?<>|\""]

        strout = strin

        for i in removal_list: 
            strout = strout.replace(i, "_")

        return strout



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