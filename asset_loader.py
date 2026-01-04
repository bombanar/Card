import json
import glob
import os
from PIL import Image


def main():
    with open('config.json', 'r') as f:
        config = json.load(f)

    with open('cache/cache_info.json', 'r') as f:
        cache_info = json.load(f)

    if cache_info['loaded_width'] == config['screen_width']:
        return 0

    mp = config['screen_width']/1920
    card_width = mp*config['card_width']
    card_height = mp*config['card_height']

    size = (int(card_width), int(card_height))
    big_size = (int(1.2*card_width), int(1.2*card_height))


    folder_path = 'assets/card_imgs'

    for file_path in glob.glob(os.path.join(folder_path, '*.png')):
        key = os.path.splitext(os.path.basename(file_path))[0]
        img = Image.open(file_path)

        resized_img = img.resize(size, Image.LANCZOS)

        resized_img.save(f'cache/card_imgs/{key}.png')

        resized_img = img.resize(big_size, Image.LANCZOS)

        resized_img.save(f'cache/card_imgs/{key}_big.png')

    folder_path = 'assets'

    for file_path in glob.glob(os.path.join(folder_path, '*.png')):
        key = os.path.splitext(os.path.basename(file_path))[0]
        img = Image.open(file_path)

        original_width, original_height = img.size
        new_width = int(original_width * mp)
        new_height = int(original_height * mp)
        new_size = (new_width, new_height)

        resized_img = img.resize(new_size, Image.LANCZOS)

        resized_img.save(f'cache//{key}.png')

    with open('cache/cache_info.json', 'w') as f:
        temp = {'loaded_width': config['screen_width']}
        json.dump(temp, f)

    return 0