
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
├── wav/
│   └── 2022Jan02_011802.wav
|
├── audio-chunks/
│   └── 2022Jan02_011802
│       ├── chunk1.wav
│       ├── chunk2.wav
│       └── chunk3.wav
│   
└── wav/
    └── 2022Jan02_011802.csv
```


### How to install
```
pip install youtube2text
```

### Build from source 
```
git clone <this_repo>
python setup.py install
```

### How to use 
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
- Support Automatic Speech Recognition with backend
    - Native Python backend 
    - Huggingface

#### Youtube -> Text
```
def url2text(self, urlpath, outfilename = None):
    '''
    Convert youtube url to text

    Parameters:
        urlpath (str): Youtube url
        outfilename (str, optional): Filename of output file (.wav, *.csv)
    '''
```

#### Youtube -> Audio
```
def url2audio(self, urlpath, audiofilename, audiofilepath = None):
    '''
    Convert youtube url to audiofile

    Parameters:
        urlpath (str): Youtube url
        audiofilename (str): Filename of audio file (*.wav)
        audiofilepath (str, optional): Absolute / relative path to save audio file
    '''
```

#### Audio -> Text
```
def audio2text(self, audiofilename, audiofilepath = None, textfilename = None, textfilepath = None):
    '''
    Convert audio to csv file

    Parameters:
        audiofilename (str): Filename of audio file (*.wav)
        audiofilepath (str, optional): Absolute / relative path to save audio file
        textfilename (str, optional): Filename of text file (*.csv)
        textfilepath (str, optional): Absolute / relative path to save text file
    '''
```
