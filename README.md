# py-vk-music
Simple script to download audio files from VK social wall posts

Usage


```
$ git clone https://github.com/vladi-dev/py-vk-music
$ cd py-vk-music
$ python main.py download_from_post --help
Usage: main.py download_from_post [OPTIONS]

Options:
  --post-url TEXT    VK post url  [required]
  --output-dir PATH  Directory to which audio files will be copied  [required]
  --login TEXT       Input your login
  --password TEXT
  --help             Show this message and exit.
  
python main.py download_from_post --login=mylogin --password=mypassword --post-url=https://vk.com/some-wall-post --output-dir=./DownloadedAlbum
```
