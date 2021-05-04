import json
import os
from pathlib import Path
import textwrap

APP_URL = os.getenv('APP_URL')
ROOT = Path(__file__).parent.parent
KAGGLE_PATH = ROOT.joinpath('temp')
KAGGLE_USER = os.getenv('KAGGLE_USER')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')


def palette(image, user_id, image_id):
    kernel_metadata = {
        'id': f'{KAGGLE_USER}/297palette',
        'title': '297palette',
        'code_file': f'{KAGGLE_PATH.joinpath("palette.py")}',
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

    image_size = 100
    num_palettes = 6
    user_id
    image_id
    name = image.name
    app_url = APP_URL
    image_name = image.source_name
    image_blob = f'palette/{image_name}'
    image_path = f'./{image_name}'
    bucket_name = STORAGE_BUCKET

    with open(f'{KAGGLE_PATH.joinpath("palette.py")}', 'w') as file:
        file.write(textwrap.dedent('''\
            import numpy as np
            import pandas as pd
            from matplotlib import pyplot as plt
            from skimage import color as converter
            from skimage.io import imread
            from skimage.transform import resize
            from sklearn.cluster import KMeans
            from matplotlib.colors import to_hex
            import requests
            from google.cloud import storage

            from kaggle_secrets import UserSecretsClient
            user_secrets = UserSecretsClient()
            user_credential = user_secrets.get_gcloud_credential()
            user_secrets.set_tensorflow_credential(user_credential)
            storage_client = storage.Client(user_credential)
            secret_palette = user_secrets.get_secret("palettes")

            image_size = int("%s")
            num_palettes = int("%s")
            user_id = "%s"
            image_id = "%s"
            name = "%s"
            app_url = "%s"
            image_name = "%s"
            image_blob = "%s"
            image_path = "%s"
            bucket_name = "%s"

            bucket = storage_client.bucket(bucket_name)
            download_blob = bucket.blob(image_blob)
            download_blob.download_to_filename(image_name)

            img = imread(image_path)
            if img.shape[-1] == 4:
                img = converter.rgba2rgb(img)
            img = resize(img, (200, 200))
            data = pd.DataFrame(img.reshape(-1, 3), columns=['R', 'G', 'B'])
            kmeans = KMeans(n_clusters=num_palettes, random_state=0)
            data['Cluster'] = kmeans.fit_predict(data)
            palette = kmeans.cluster_centers_

            colors = np.zeros((num_palettes, image_size, image_size, 3))
            palette_list = []
            for idx, color in enumerate(palette):
                for i in range(image_size):
                    colors[idx][i] = color

            hex_values = []
            for idx, color in enumerate(colors):
                hex_values.append(to_hex(color[0][0]))

            payload = {'hex_values': hex_values, 'image_id': image_id, 'user_id': user_id, 'name': name}
            headers = {'Token': secret_palette}
            requests.post(app_url, json=payload, headers=headers)
        ''' % (
            image_size,
            num_palettes,
            user_id,
            image_id,
            name,
            app_url,
            image_name,
            image_blob,
            image_path,
            bucket_name,
            )
        ))
