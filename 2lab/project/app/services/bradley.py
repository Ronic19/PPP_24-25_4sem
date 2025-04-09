from PIL import Image
import base64
from io import BytesIO
import numpy as np

def image_to_base64(path_to_image):
    with Image.open(path_to_image) as img:
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        byte_data = buffer.getvalue()
        img_str = base64.b64encode(byte_data).decode('utf-8')
    return img_str


def base64_to_image(img_str, path='2lab/project/app/services/decoded_img.png'):
    img = Image.open(BytesIO(base64.b64decode(img_str)))
    img.save(path)
    return path


def get_img_size(img_str):
    img = Image.open(BytesIO(base64.b64decode(img_str)))
    width, height = img.size
    return width, height


def grey_matrix(img_str):
    grey_coef = np.array([0.2125, 0.7154, 0.0721])
    img = Image.open(BytesIO(base64.b64decode(img_str)))

    img_arr = np.array(img)
    img_arr_grey = np.dot(img_arr[:, :, :3], grey_coef)

    return img_arr_grey


def get_integral_img(matrix):
    res = np.zeros(matrix.shape)
    res[0, 0] = matrix[0, 0]

    # находим значения в первом столбце
    for i in range(1, matrix.shape[0]):
        res[i, 0] = res[i - 1, 0] + matrix[i, 0]

    # значения в первой строке
    for i in range(1, matrix.shape[1]):
        res[0, i] = res[0, i - 1] + matrix[0, i]

    # все остальные пиксели
    for i in range(1, matrix.shape[0]):
        for j in range(1, matrix.shape[1]):
            res[i, j] = res[i - 1, j] + res[i, j - 1] + matrix[i, j] - res[i - 1, j - 1]

    return res


def bradley(img_str):
    img_grey = grey_matrix(img_str)
    integral_img = get_integral_img(img_grey)
    width, height = get_img_size(img_str)
    res_matrix = np.zeros((height, width, 4))

    s = width / 8
    s2 = int(s / 2)
    t = 0.15

    for i in range(height):
        for j in range(width):
            x1 = j - s2
            x2 = j + s2
            y1 = i - s2
            y2 = i + s2

            if x1 < 0:
                x1 = 0
            if x2 >= width:
                x2 = width - 1
            if y1 < 0:
                y1 = 0
            if y2 >= height:
                y2 = height - 1
            
            count = (x2 - x1) * (y2 - y1)
            area_sum = integral_img[y2, x2] - integral_img[y1, x2] - \
                integral_img[y2, x1] + integral_img[y1, x1]
            
            if img_grey[i, j] < area_sum * (1 - t) / count:
                res_matrix[i, j] = np.array([0, 0, 0, 255])
            else:
                res_matrix[i, j] = np.array([255, 255, 255, 255])

    res_img = Image.fromarray(res_matrix.astype(np.uint8))
    buffer = BytesIO()
    res_img.save(buffer, format='PNG')
    byte_data = buffer.getvalue()
    res_str = base64.b64encode(byte_data).decode('utf-8')

    return res_str

