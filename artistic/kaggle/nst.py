import json
import os
from pathlib import Path
import textwrap

ROOT = Path(__file__).parent
KAGGLE_PATH = ROOT.joinpath('temp')
KAGGLE_USER = os.getenv('KAGGLE_USER')
KAGGLE_SLUG = os.getenv('KAGGLE_SLUG')
KAGGLE_GPU_ENABLED = os.getenv('KAGGLE_GPU_ENABLED')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')


def nst(content_name, style_name, start_as):
    kernel_metadata = {
        'id': f'{KAGGLE_USER}/{KAGGLE_SLUG}',
        'title': KAGGLE_SLUG,
        'code_file': f'{KAGGLE_PATH.joinpath("nst.py")}',
        'language': 'python',
        'kernel_type': 'script',
        'is_private': 'true',
        'enable_gpu': KAGGLE_GPU_ENABLED,
        'enable_internet': 'true',
        'dataset_sources': [],
        'competition_sources': [],
        'kernel_sources': []
    }

    with open(f'{KAGGLE_PATH.joinpath("kernel-metadata.json")}', 'w') as file:
        json.dump(kernel_metadata, file)

    image_id = content_name.split('-')[0]
    content_name = f'starting/{content_name}'
    style_name = f'style/{style_name}'
    img_name = f'{image_id}.png'
    destination_blob_name = f'generated/{img_name}'
    upload_from_filename = f'./{img_name}'

    with open(f'{KAGGLE_PATH.joinpath("nst.py")}', 'w') as file:
        file.write(textwrap.dedent('''\
            import tensorflow as tf
            from tensorflow import keras
            from keras import Model
            from keras.layers import MaxPooling2D, AveragePooling2D
            from keras.preprocessing import image
            from keras.applications import vgg19
            import numpy as np
            import os, binascii
            from google.cloud import storage

            from kaggle_secrets import UserSecretsClient
            user_secrets = UserSecretsClient()
            user_credential = user_secrets.get_gcloud_credential()
            user_secrets.set_tensorflow_credential(user_credential)
            CONTENT_WEIGHT = 1e3
            STYLE_WEIGHT = 1e-2
            CONTENT_LAYER_NAME = 'block5_conv2'
            STYLE_LAYER_NAMES = [
                "block1_conv1",
                "block2_conv1",
                "block3_conv1",
                "block4_conv1",
                "block5_conv1",
                ]
            content_name = "%s"
            style_name = "%s"
            bucket_name = "%s"
            storage_client = storage.Client(user_credential)
            bucket = storage_client.bucket(bucket_name)
            for file_name in [content_name, style_name]:
                download_blob = bucket.blob(file_name)
                name = '-'.join(file_name.split('/'))
                download_blob.download_to_filename(name)

            STYLE_PATH = '-'.join(style_name.split('/'))
            CONTENT_PATH = '-'.join(content_name.split('/'))
            CHANNELS = 3
            ITERATIONS = 2

            width, height = keras.preprocessing.image.load_img(CONTENT_PATH).size
            img_width = 600
            img_height = int(width * img_width / height)

            def preprocess_image(image_path):
                img = image.load_img(
                    image_path, target_size=(img_width, img_height)
                    )
                img = image.img_to_array(img)
                img = np.expand_dims(img, axis=0)
                img = vgg19.preprocess_input(img)
                return tf.convert_to_tensor(img)

            def deprocess_image(image):
                img = image.reshape((img_width, img_height, CHANNELS))

                # Remove zero-center by mean pixel
                img[:, :, 0] += 103
                img[:, :, 1] += 116
                img[:, :, 2] += 123
                # 'BGR'->'RGB'
                img = img[:, :, ::-1]
                return np.clip(img, 0, 255).astype("uint8")

            def replace_max_by_avg_pooling(model):
                input_layer, *layers = model.layers

                output = input_layer.output
                for layer in layers:
                    if isinstance(layer, MaxPooling2D):
                        layer = AveragePooling2D(
                            pool_size=layer.pool_size,
                            strides=layer.strides,
                            padding=layer.padding,
                            data_format=layer.data_format,
                            name = layer.name + "_avg",
                        )
                    output = layer(output)

                return keras.models.Model(inputs=input_layer.input, outputs=output)

            def create_model():
                vgg = vgg19.VGG19(weights='imagenet', include_top=False)
                vgg_avg = replace_max_by_avg_pooling(vgg)
                vgg_avg.trainable = False
                outputs = {}
                for layer_name in STYLE_LAYER_NAMES + [CONTENT_LAYER_NAME]:
                    outputs[layer_name] = vgg.get_layer(layer_name).get_output_at(1)

                return Model(vgg_avg.inputs, outputs)

            def gramify(matrix):
                channels = int(matrix.shape[-1])
                m = tf.reshape(matrix, [-1, channels])
                n = tf.shape(m)[0]
                gram = tf.matmul(m, m, transpose_a=True)
                return gram / tf.cast(n, tf.float32)

            def compute_style_loss(style, generated):
                gram_style = gramify(style)
                gram_generated = gramify(generated)

                return tf.reduce_mean(tf.square(gram_style - gram_generated))

            def compute_loss(style_image, content_image, generated_image):
                model = create_model()
                for layer in model.layers:
                    layer.trainable = False
                style_outputs = model(style_image)
                content_feature = model(content_image)[CONTENT_LAYER_NAME]
                generated_outputs = model(generated_image)
                generated_feature = generated_outputs[CONTENT_LAYER_NAME]

                content_sum = tf.reduce_mean(tf.square(content_feature - generated_feature))
                content_loss = CONTENT_WEIGHT * content_sum

                style_losses = tf.zeros(shape=())
                for name in STYLE_LAYER_NAMES:
                    style_feature = style_outputs[name]
                    generated_feature = generated_outputs[name]
                    style_sum = compute_style_loss(style_feature, generated_feature)
                    style_losses += STYLE_WEIGHT * (style_sum / len(STYLE_LAYER_NAMES))

                total_loss = content_loss + style_losses
                return (total_loss, content_loss, style_losses)

            def run_nst():
                style_image = preprocess_image(STYLE_PATH)
                content_image = preprocess_image(CONTENT_PATH)
                if "%s" == 'random':
                    generated_image = tf.Variable(tf.random.uniform(content_image.shape))
                else:
                    generated_image = tf.Variable(
                        preprocess_image(CONTENT_PATH),
                        dtype=tf.float32
                        )
                optimizer = tf.keras.optimizers.Adam(
                    learning_rate=5,
                    beta_1=0.99,
                    beta_2=0.999,
                    epsilon=1e-1,
                    amsgrad=False,
                    name="Adam",
                    )

                for _ in range(ITERATIONS):
                    with tf.GradientTape() as tape:
                        (total_loss, _, _) = compute_loss(
                            style_image,
                            content_image,
                            generated_image,
                            )
                    gradients = tape.gradient(total_loss, generated_image)
                    optimizer.apply_gradients([(gradients, generated_image)])

                img = deprocess_image(generated_image.numpy())
                random_name = binascii.b2a_hex(os.urandom(5)).decode('utf-8')
                img_name = "%s"
                image.save_img(img_name, img)

                destination_blob_name = "%s"
                blob = bucket.blob(destination_blob_name)
                blob.upload_from_filename("%s")

            run_nst()
            ''' % (
                content_name,
                style_name,
                STORAGE_BUCKET,
                start_as,
                img_name,
                destination_blob_name,
                upload_from_filename,
                )
            ))
