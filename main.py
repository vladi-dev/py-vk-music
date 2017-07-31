from __future__ import division

import os
import requests

import click
from click.exceptions import Abort

from vk import VK


@click.group()
def cli():
    pass


@cli.command()
@click.option('--post-url', prompt=True, type=click.STRING, required=True,
              help='VK post url')
@click.option('--output-dir', prompt=True, type=click.Path(), required=True,
              help='Directory to which audio files will be copied')
@click.option('--login', prompt=True, help='Input your login')
@click.password_option(confirmation_prompt=False)
def download_from_post(post_url, output_dir, login, password):
    click.echo('Logging in...')
    vk_ = VK(login, password)
    click.echo('Logged in successful')
    audio_ids = vk_.get_audio_ids(post_url)

    click.echo('Extracting audio info from VK post...')
    audios = []
    for audio_id in audio_ids:
        audio = vk_.get_audio_info(audio_id)
        audios.append(audio)

    click.echo('Found {} audio files'.format(len(audios)))
    for audio in audios:
        click.echo(audio.get_filename())

    click.confirm('Do you want to download these audio files?', abort=True)

    if not os.path.exists(output_dir):
        click.echo('Directory {} does not exist'.format(output_dir))
        click.confirm('Do you want to create it?', abort=True)
        try:
            os.mkdir(output_dir, 0o766)
        except OSError as e:
            click.echo('Failed to create directory {}'.format(output_dir))
            click.echo(str(e))
            raise Abort()

    for audio in audios:
        audio_filepath = '{}/{}'.format(output_dir, audio.get_filename())

        r = requests.get(audio.url, stream=True)
        content_length = int(r.headers.get('content-length'))
        filesize_mb = content_length / 1024 / 1024

        click.echo('{} ({:.2f} Mb)'.format(audio.get_filename(), filesize_mb))

        with open(audio_filepath, 'wb') as f:
            with click.progressbar(length=content_length) as bar:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

    click.echo('Enjoy')


if __name__ == '__main__':
    cli()
