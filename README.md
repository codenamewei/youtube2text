
## Converts Youtube URLs to Text with Speech Recognition 

<p>
  <p align="center">
<img alt="project status: active" src="https://img.shields.io/badge/Project%20Status-%F0%9F%94%A5Active-brightgreen"> <img alt="supported language: english" src="https://img.shields.io/badge/Supported%20Language-English-blueviolet">

</p>



<div align="center">
  <img alt="banner" src="https://user-images.githubusercontent.com/33477318/147850310-902fa3c3-910c-48de-815a-9e8f54487d73.jpg" width="800"><br>
</div>

### What does the library does?

- Youtube -> Text: Translate youtube urls as text file (.csv)
- Youtube -> Audio: Downloads youtube urls as audio file (.wav)
- Audio -> Text: Translate audio file (.wav) to text file (.csv)


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
├── wav/
    └── 2022Jan02_011802.csv
```


### How to install
```
pip install youtube2text
```

### How to use 
```
from youtube2text import Youtube2Text

converter = Youtube2Text()

converter.url2text(urlpath="https://www.youtube.com/watch?v=Ad9Q8rM0Am0&t=114s")
```

### Functions 

### Youtube -> Text
```
def url2text(self, urlpath, filetitle = None):
        '''
        Convert youtube url to text

        Parameters:
            urlpath (str): Youtube url
            filetitle (str, optional): Filename of output file (.wav, *.csv)
        '''
```


### Youtube -> Audio
```
def url2wav(self, urlpath, wavfullpath):
    '''
    Convert youtube url to wav

    Parameters:
        urlpath (str): Youtube url
        wavfullpath (str, optional): Full path to output wav file (.wav)
    '''
```

### Audio -> Text
```
def wav2text(self, wavfullpath):
    '''
    Convert wav to csv file

    Parameters:
        wavpath (str): Full path to wav file
    '''
```
