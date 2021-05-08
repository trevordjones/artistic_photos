import binascii
import json
import os
from pathlib import Path
import textwrap

ROOT = Path(__file__).parent.parent
KAGGLE_PATH = ROOT.joinpath('temp')
KAGGLE_USER = os.getenv('KAGGLE_USER')
KAGGLE_SLUG = os.getenv('KAGGLE_BLUR_SLUG')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')


def blur(outline_image, starting_image):
    kernel_metadata = {
        'id': f'{KAGGLE_USER}/{KAGGLE_SLUG}',
        'title': KAGGLE_SLUG,
        'code_file': f'{KAGGLE_PATH.joinpath("blur.py")}',
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

    starting_image_blob = f'starting/{starting_image.source_name}'
    outline_image_blob = f'starting/{outline_image.source_name}'
    starting_image_name = starting_image.source_name
    outline_image_name = outline_image.source_name
    bucket_name = STORAGE_BUCKET
    saved_image_name = f'{binascii.b2a_hex(os.urandom(5)).decode("utf-8")}.png'
    destination_blob_name = f'artistic/{saved_image_name}'
    upload_file_name = f'./{saved_image_name}'

    with open(f'{KAGGLE_PATH.joinpath("blur.py")}', 'w') as file:
        file.write(textwrap.dedent('''\
            import cv2
            import numpy as np
            from google.cloud import storage
            from kaggle_secrets import UserSecretsClient

            user_secrets = UserSecretsClient()
            user_credential = user_secrets.get_gcloud_credential()
            user_secrets.set_tensorflow_credential(user_credential)
            storage_client = storage.Client(user_credential)

            starting_image_blob = "%s"
            outline_image_blob = "%s"
            starting_image_name = "%s"
            outline_image_name = "%s"

            bucket_name = "%s"
            bucket = storage_client.bucket(bucket_name)
            download_blob = bucket.blob(starting_image_blob)
            download_blob.download_to_filename(starting_image_name)

            download_blob = bucket.blob(outline_image_blob)
            download_blob.download_to_filename(outline_image_name)

            starting_image = cv2.imread(starting_image_name)
            outline = cv2.imread(outline_image_name)
            outline = cv2.cvtColor(outline, cv2.COLOR_BGR2RGB)
            starting_image = cv2.resize(starting_image, (outline.shape[1], outline.shape[0]))

            lower = np.array([255, 0, 0], dtype = "uint8")
            upper = np.array([255, 0, 0], dtype = "uint8")
            mask = cv2.inRange(outline, lower, upper)
            traced = cv2.bitwise_and(outline, outline, mask = mask)
            grayed = cv2.cvtColor(traced, cv2.COLOR_RGB2GRAY)

            filled = grayed.copy()
            contours,_ = cv2.findContours(filled, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            image_binary = np.zeros((filled.shape[0], filled.shape[1], 1), dtype=np.uint8)
            filled = cv2.drawContours(image_binary, [max(contours, key = cv2.contourArea)], -1, 255, thickness=-1)

            blurred = cv2.blur(starting_image,(30,30))
            for ridx, row in enumerate(starting_image):
                for cidx, column in enumerate(row):
                    if filled[ridx][cidx][0] == 255:
                        blurred[ridx][cidx] = starting_image[ridx][cidx]


            saved_image_name = "%s"
            cv2.imwrite(saved_image_name, blurred)
            destination_blob_name = "%s"
            blob = bucket.blob(destination_blob_name)
            upload_file_name = "%s"
            blob.upload_from_filename(upload_file_name)
        ''' % (
            starting_image_blob,
            outline_image_blob,
            starting_image_name,
            outline_image_name,
            bucket_name,
            saved_image_name,
            destination_blob_name,
            upload_file_name
            )
        ))
