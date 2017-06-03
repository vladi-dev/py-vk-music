import ast
import requests
from bs4 import BeautifulSoup


class AuthError(Exception):
    pass


class ParseError(Exception):
    pass


class VKAudioInfo(object):
    def __init__(self, artist, track, url):
        self.artist = artist
        self.track = track
        self.url = url

    def get_filename(self):
        return '{} - {}.mp3'.format(self.artist, self.track)


class VK(object):
    def __init__(self, email, password):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                          'AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        self.remixsid = self._get_auth_cookie(email, password)

    def _get_auth_cookie(self, email, password):
        r = requests.get('https://vk.com', headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        lg_h = soup.find('input', {'name': 'lg_h'})[
            'value']  # POST data required to do auth
        remixlhk = r.cookies['remixlhk']  # cookie required to do auth
        data = {
            'email': email,
            'pass': password,
            'lg_h': lg_h,
            'role': 'al_frame'
        }
        cookies = {
            'remixlhk': remixlhk,
        }
        r = requests.post('https://login.vk.com?act=login', data=data,
                          headers=self.headers, cookies=cookies, allow_redirects=False)
        redirect_to = r.headers['Location']
        r = requests.get(redirect_to, cookies=r.cookies, headers=self.headers,
                         allow_redirects=False)
        if 'remixsid' not in r.cookies:
            raise AuthError('Authorization failed')
        return r.cookies['remixsid']

    def _request_get_with_auth(self, url, **kwargs):
        cookies = {
            'remixsid': self.remixsid
        }
        return requests.get(url, cookies=cookies, headers=self.headers, **kwargs)

    def _request_post_with_auth(self, url, **kwargs):
        cookies = {
            'remixsid': self.remixsid
        }
        return requests.post(url, cookies=cookies, headers=self.headers, **kwargs)

    def get_audio_ids(self, wall_url):
        r = self._request_get_with_auth(wall_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        audio_rows = soup.find_all('div', {'class': 'audio_row'})
        audio_ids = []
        for row in audio_rows:
            audio_ids.append(row['data-full-id'])
        return audio_ids

    def get_audio_info(self, audio_id):
        data = {
            'act': 'reload_audio',
            'al': '1',
            'ids': audio_id
        }
        r = self._request_post_with_auth('https://vk.com/al_audio.php', data=data)
        answers = r.text.split('<!>')
        audio_info = None
        for answer in answers:
            if answer.startswith('<!json>'):
                audio = answer[len('<!json>'):]
                audio_info = ast.literal_eval(audio)
                break
        if audio_info is None:
            raise ParseError('Audio info not found')
        if len(audio_info) > 1:
            raise ParseError('Found more than 1 audio info response, expected one')
        inf = audio_info[0]
        audio_url = inf[2].replace('\/', '/').split('?')[0]
        track = inf[3]
        artist = inf[4]
        return VKAudioInfo(artist, track, audio_url)
