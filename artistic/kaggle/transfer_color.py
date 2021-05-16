import json
import os
from pathlib import Path
import random
import textwrap

from artistic.models import Image

ROOT = Path(__file__).parent.parent
KAGGLE_PATH = ROOT.joinpath('temp')
KAGGLE_USER = os.getenv('KAGGLE_USER')
BUCKET = os.getenv('STORAGE_BUCKET')
APP_URL = os.getenv('APP_URL')

# can get the palette from starting_image
def transfer_color(starting_image, palette, transfer_mapping, color_image_name):
    # transfer_mapping[0] -> palette
    # transfer_mapping[1] -> starting_image.palette

    # remove what is in transfer_mapping from their associated palettes
    # pair up randomly whatever is left
    # create sets
    starting_hex_set = set(starting_image.palette.hex_values)
    hex_set = set(palette.hex_values)
    remaining_starting_hex = list(starting_hex_set - set([h[1] for h in transfer_mapping]))
    remaining_hex = list(hex_set - set([h[0] for h in transfer_mapping]))
    # iterate through remaining_hex -> this is num_palettes we'll use in algorithm
    remaining_starting_hex_length = len(remaining_starting_hex) - 1
    for hex in remaining_hex:
        i = random.randint(0, remaining_starting_hex_length)
        transfer_mapping.append([hex, remaining_starting_hex[i]])
    # mapped_palette should contain the index of palette
    # its length should be palette.hex_values - it may have duplicates
    hex_values = palette.hex_values
    hex_values.sort()
    transfer_mapping.sort(key=lambda hexes: hexes[0])
    mapped_palette = []
    for hexes in transfer_mapping:
        idx = starting_image.palette.hex_values.index(hexes[1])
        mapped_palette.append(str(idx))

    kernel_metadata = {
        'id': f'{KAGGLE_USER}/297color-transfer',
        'title': '297color-transfer',
        'code_file': f'{KAGGLE_PATH.joinpath("transfer_color.py")}',
        'language': 'python',
        'kernel_type': 'script',
        'is_private': 'true',
        'enable_gpu': 'false',
        'enable_internet': 'true',
        'dataset_sources': [],
        'competition_sources': [],
        'kernel_sources': []
    }

    with open(f'{KAGGLE_PATH.joinpath("kernel-metadata.json")}', 'w') as file:
        json.dump(kernel_metadata, file)

    # set up variables
    palette_hex_values = ','.join(palette.hex_values)
    starting_image_hex_values = ','.join(starting_image.palette.hex_values)
    mapped_palette = ','.join(mapped_palette)
    starting_image_blob = f'starting/{starting_image.source_name}'
    starting_image_name = starting_image.source_name
    bucket_name = BUCKET
    color_image_name = f'{color_image_name}.png'
    destination_blob_name = f'artistic/{color_image_name}'

    # create image in DB, pass as an arg
    image = Image(
        user_id=starting_image.user_id,
        source_name=color_image_name,
        subdirectory='artistic',
        width=starting_image.width,
        height=starting_image.height,
        starting_image_id=starting_image.id,
        is_visible=False,
        )
    image.save()
    app_url = f'{APP_URL}/{image.id}/make_visible'

    # script
    with open(f'{KAGGLE_PATH.joinpath("transfer_color.py")}', 'w') as file:
        file.write(textwrap.dedent('''\
            import numpy as np
            import pandas as pd
            from skimage import color as converter
            from skimage.io import imread
            from skimage.transform import resize
            from sklearn.cluster import KMeans
            from matplotlib.colors import to_hex
            from google.cloud import storage
            from kaggle_secrets import UserSecretsClient
            import cv2
            import requests

            user_secrets = UserSecretsClient()
            user_credential = user_secrets.get_gcloud_credential()
            user_secrets.set_tensorflow_credential(user_credential)
            storage_client = storage.Client(user_credential)

            palette_hex_values = "%s".split(',')
            starting_image_hex_values = "%s".split(',')
            mapped_palette = [int(i) for i in "%s".split(',')]
            palette = []
            # convert palette to rgb
            for hex_value in palette_hex_values:
                rgb = list(int(hex_value[1:][i:i+2], 16) for i in (0, 2, 4))
                palette.append(rgb)
            palette = np.asarray(palette)
            palette = palette / 255

            # convert starting_image_palette to rgb
            starting_image_palette = []
            for hex_value in starting_image_hex_values:
                rgb = list(int(hex_value[1:][i:i+2], 16) for i in (0, 2, 4))
                starting_image_palette.append(rgb)
            starting_image_palette = np.asarray(starting_image_palette)
            starting_image_palette = starting_image_palette / 255

            starting_image_blob = "%s"
            starting_image_name = "%s"
            bucket_name = "%s"

            # download the photo from GCP
            bucket = storage_client.bucket(bucket_name)
            download_blob = bucket.blob(starting_image_blob)
            download_blob.download_to_filename(starting_image_name)

            num_palettes = len(palette_hex_values)
            image_size = 100

            # use the image to define `kmeans` - this will be used later to see which palette a pixel is assigned
            starting_image = imread(starting_image_name)
            if starting_image.shape[-1] == 4:
                # check if there is a transparent (alpha) layer
                starting_image = converter.rgba2rgb(starting_image)
            reduced_image = resize(starting_image, (200, 200))
            data = pd.DataFrame(reduced_image.reshape(-1, 3), columns=['R', 'G', 'B'])
            kmeans = KMeans(n_clusters=num_palettes, random_state=0)
            kmeans.fit_predict(data)

            color_image = starting_image.copy()
            color_image = resize(color_image, (color_image.shape[0], color_image.shape[1]))
            for idx, i in enumerate(color_image):
                for jdx, current_pixel in enumerate(i):
                    data = pd.DataFrame(current_pixel.reshape(-1, 3), columns=['R', 'G', 'B'])
                    cluster = kmeans.predict(data)
                    # cluster[0] represents the index of the starting_image_palette
                    # use mapping to find rgb of palette
                    palette_pixel = palette[mapped_palette[cluster[0]]]
                    # get the percentage change of current_pixel and starting_image_palette[cluster[0]]
                    starting_image_palette_pixel = starting_image_palette[cluster[0]]
                    percentage = (np.sum(starting_image_palette_pixel) - np.sum(current_pixel))/np.sum(starting_image_palette_pixel)
                    changed_pixel = palette_pixel + (palette_pixel * percentage)
                    color_image[idx][jdx] = changed_pixel

            color_image = color_image * 255
            color_image = np.asarray(color_image, dtype='float32')

            color_image_name = "%s"
            # cv2 will reverse rgb when saving because it assumes the image is bgr
            color_image_bgr = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(color_image_name, color_image_bgr)

            destination_blob_name = "%s"
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(color_image_name)

            key = user_secrets.get_secret("API")
            headers = {'Token': key}
            requests.put("%s", headers=headers)
            ''' % (
                palette_hex_values,
                starting_image_hex_values,
                mapped_palette,
                starting_image_blob,
                starting_image_name,
                bucket_name,
                color_image_name,
                destination_blob_name,
                app_url,
                )
            ))

        return image
