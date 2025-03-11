import os, ffmpeg, difflib

def main():
    season = 'S01'
    artist = 'artist'
    episodes = episode_dict(f"{season}.md")
    episode_titles = titles_of_episodes(episodes)
    for f in sorted(os.listdir(season)):
        file = os.path.join(season, f)
        probe = ffmpeg.probe(file)
        probe_title_full = probe['format']['tags']['title']
        probe_title = probe_title_full.split(' – ', 1)[1]
        closest_names = difflib.get_close_matches(probe_title, episode_titles, 2)
        episode_key = find_episode(episodes, closest_names)
        episode = episodes[episode_key]
        episode_title = episode['title']
        episode_title_formatted = episode_title.replace(' ', '.').replace('&', '').replace('-', '.').replace('\'', '').replace('...', '.').replace('..', '.')
        episode_date = episode['date']
        episode_description = episode['description']
        file_name = f"{artist}.{episode_key}.{episode_title_formatted}.mkv"
        new_file = os.path.join(season, file_name)
        metadata_list = [f"artist={artist}", f"title={artist} {episode_key} - {episode_title}", f"date={episode_date}", f"comment={episode_key}", f"description={episode_description}",]
        metadata_dict = {f"metadata:g:{i}": e for i, e in enumerate(metadata_list)}
        ffmpeg.input(file).output(new_file, codec="copy", map="0", loglevel="quiet", **metadata_dict).run()
        print('\n', new_file, '\n')

def find_episode(episodes: dict, titles: list):
    for episode in episodes:
        if episodes[episode]['title'] == titles[0]:
            return episode
    for episode in episodes:
        if episodes[episode]['title'] == titles[1]:
            return episode
    return None

def titles_of_episodes(episodes: dict):
    titles = []
    for episode in episodes:
        titles.append(episodes[episode]['title'])
    return titles

def episode_dict(file_path: str) -> dict:
    episodes = {}
    file = open(file_path, "r")
    for line in file:
        line = line.strip()
        if line == "":
            continue
        date = file.readline().strip()
        description = file.readline().strip()
        title = line.split(' - ', 1)
        episodes[title[0]] = {'title': title[1], 'date': date, 'description': description}
    file.close()
    return episodes

if __name__ == "__main__":
    main()