from matplotlib.colors import to_hex
import numpy as np
import pandas as pd
from pathlib import Path
from skimage import color as converter
from skimage.io import imread
from skimage.transform import resize
from sklearn.cluster import KMeans

ROOT = Path(__file__).parent
FILE_PATH = ROOT.joinpath('temp')

def palette(starting_path, num_palettes=6):
    image_size = 100

    img = imread(str(starting_path))
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

    return hex_values
