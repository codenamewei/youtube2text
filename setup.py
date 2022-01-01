from setuptools import find_packages
from setuptools import setup

with open("readme.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name='youtube2text',
    version='0.0.3',
    install_requires=[
        'pytube==11.0.1',
        'pydub==0.25.1',
        'SpeechRecognition==3.8.1',
        'ffprobe==0.5',
        'pandas>=1.1.5',
        'ffmpeg-python==0.2.0'
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    url='https://github.com/codenamewei/youtube2text',
    license='MIT',
    author='codenamewei',
    author_email='codenamewei@gmail.com',
    description='Convert youtube urls to text with speech recognition.',
    long_description=long_description,
    include_package_data=True
    long_description_content_type="text/markdown",
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ]
)
