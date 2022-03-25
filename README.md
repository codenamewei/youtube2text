
## Converts Youtube URLs to Text with Speech Recognition 

<p>
  <p align="center">
<img alt="project status: active" src="https://img.shields.io/badge/Project%20Status-%F0%9F%94%A5Active-brightgreen"> <img alt="supported language: english" src="https://img.shields.io/badge/Supported%20Language-English-blueviolet">

</p>



<div align="center">
  <img alt="banner" src="https://user-images.githubusercontent.com/33477318/147850310-902fa3c3-910c-48de-815a-9e8f54487d73.jpg" width="800"><br>
</div>

### What does the library does?

- **Youtube -> Text**: Translate youtube urls as text file (csv)
- **Youtube -> Audio**: Downloads youtube urls as audio file (wav, flac)
- **Audio -> Text**: Translate audio file (wav, flac) to text file (csv)


Three folders will be created to store the output files.  
```
<Own Path> or <HOME_DIRECTORY>/youtube2text
│
├── audio/
│   └── 2022Jan02_011802.flac
|
├── audio-chunks/
│   └── 2022Jan02_011802
│       ├── chunk1.flac
│       ├── chunk2.flac
│       └── chunk3.flac
│   
└── text/
    └── 2022Jan02_011802.csv
```


### How to install
Install and update using [pip](https://pypi.org/project/youtube2text/)
```
pip install youtube2text
```


### Build from source 
```
git clone <this_repo>
cd <this_repo>
python setup.py install
```

### How to use 
- Using the library requires **internet connection** for both downloading youtube videos and speech recognition operation
```
from youtube2text import Youtube2Text

converter = Youtube2Text()

converter.url2text(urlpath="https://www.youtube.com/watch?v=Ad9Q8rM0Am0&t=114s")
```

Check out more at [howtouse.ipynb](tests/howtouse.ipynb)

### Functions 
- Support audio output of   
    - wav
    - flac
- Support Automatic Speech Recognition with [speech-recognition library](https://pypi.org/project/SpeechRecognition/)

#### Youtube -> Text
```
def url2text(self, urlpath, outfile = None, audioformat = "flac", audiosamplingrate=16000):
    '''
    Convert youtube url to text

    Parameters:
        urlpath (str): Youtube url
        outfile (str, optional): File path/name of output file (.csv)
        audioformat (str, optional): Audioformat supported in self.__audioextension
        audiosamplingrate (int, optional): Audio sampling rate
    '''
```

#### Youtube -> Audio
```
def url2audio(self, urlpath, audiofile = None, audiosamplingrate=16000):
    '''
    Convert youtube url to audiofile

    Parameters:
        urlpath (str): Youtube url
        audiofile (str, optional): File path/name to save audio file
        audiosamplingrate (int, optional): Audio sampling rate
    '''
```

#### Audio -> Text
```
def audio2text(self, audiofile, textfile = None):
    '''
    Convert audio to csv file

    Parameters:
        audiofile (str): File path/name of audio file
        textfile (str, optional): File path/name of text file (*.csv)
    '''
```
## 📝 Article 

Read out the article below on how to use the repository. 

- [Youtube to Text with Speech Recognition in Python](https://towardsdatascience.com/youtube-to-text-with-speech-recognition-in-python-cd47d6d98b16?sk=be41e705c8b182795712a70419a5b8d0)


## 📩 Reach out to me  

This repository is created out from personal use to retrieve audio files for conversational speech recognition and audio classification.

For custom functionality development support, enterprise support and other related questions, reach out at  
<a href="mailto:codenamewei@gmail.com"><img src="https://img.shields.io/badge/-codenamewei@gmail.com-D14836?style=flat&logo=Gmail&logoColor=white"/></a>
