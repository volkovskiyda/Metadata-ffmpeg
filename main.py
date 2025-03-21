import os, ffmpeg, difflib
from dotenv import load_dotenv

load_dotenv()

def main():
    base_path = os.getenv('BASE_PATH') or '/'
    artist = os.getenv('ARTIST') or ''
    season = os.getenv('SEASON') or 'S01'

    input = f'{base_path}/data/{season}'
    output = f'{base_path}/output/{season}'
    os.makedirs(output, exist_ok=True)

    episodes = episode_list(f'{input}.md')
    episode_titles = titles_of_episodes(episodes)
    for f in sorted(os.listdir(input)):
        file = os.path.join(input, f)
        probe = ffmpeg.probe(file)
        probe_title_full = probe['format']['tags']['title']
        probe_title = probe_title_full.split(' – ', 1)[1]
        closest_names = difflib.get_close_matches(probe_title, episode_titles, 2)
        episode = find_episode(episodes, closest_names)
        episode_key = episode['key']
        episode_date = episode['date']
        episode_description = episode['description']
        episode_title = episode['title']
        episode_title_formatted = episode_title.replace(' ', '.').replace('&', '').replace('-', '.').replace('\'', '').replace('...', '.').replace('..', '.')
        file_name = f'{artist}.{episode_key}.{episode_title_formatted}.mkv'
        new_file = os.path.join(output, file_name)
        metadata_list = [f'artist={artist}', f'title={artist} {episode_key} - {episode_title}', f'date={episode_date}', f'comment={episode_key}', f'description={episode_description}',]
        metadata_dict = {f'metadata:g:{i}': e for i, e in enumerate(metadata_list)}
        ffmpeg.input(file).output(new_file, codec='copy', map='0', **metadata_dict).run()
        print('\n', new_file, '\n')

def find_episode(episodes: list, titles: list):
    for episode in episodes:
        if episode['title'] == titles[0]:
            return episode
    for episode in episodes:
        if episode['title'] == titles[1]:
            return episode
    return None

def titles_of_episodes(episodes: list):
    titles = []
    for episode in episodes:
        titles.append(episode['title'])
    return titles

def episode_list(file_path: str) -> list:
    episodes = []
    file = open(file_path, 'r')
    for line in file:
        line = line.strip()
        if not line: continue
        date = file.readline().strip()
        description = file.readline().strip()
        title = line.split(' - ', 1)
        episodes.append({'key': title[0], 'title': title[1], 'date': date, 'description': description})
    file.close()
    return episodes

if __name__ == '__main__':
    main()