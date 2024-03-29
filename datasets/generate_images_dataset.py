import os
import numpy as np
import PIL
import cv2
from tqdm import tqdm

from utils import save_list_to_pickle_file

ACTIONS = {
    0: {
        "name": "straight",
        "motors": (50, 50),
        "time": None
    },
    2: {
        "name": "left",
        "motors": (0, 40),
        "time": 100
    },
    4: {
        "name": "right",
        "motors": (40, 0),
        "time": 100
    },
    5: {
        "name": "nothing_seen_turn_right",
        "motors": (45, 0),
        "time": 450
    }
}


def labelling_testing(image):
    im_list = image.tolist()
    # im_list = im.tolist()

    horizontal_position = -1
    # Iterate through rows (from the bottom to  the topof the image,  it should recognize closer targets)
    for row_index in range(len(im_list) - 1, -1, -1):

        # Iterate through columns (meaning that each "column index" is the index of a pixel)
        for column_index in range(len(im_list[row_index])):
            # Pixel cell with r g b values
            pixel = im_list[row_index][column_index]
            # If the pixel is green look in the same row if there are other green pixels. If so, check what is the last
            # green pixel and save it. So, the average green pixel position on the horizontal axis is the average of these two
            if (pixel[0] < 165 and pixel[1] > 195 and pixel[2] < 175) or (
                    pixel[0] < 20 and pixel[1] > 150 and pixel[2] < 20):
                last_pixel = -1

                for other_pixels in range(column_index + 1, len(im_list[row_index])):
                    other_pixel = im_list[row_index][other_pixels]
                    if (other_pixel[0] < 165 and other_pixel[1] > 205 and other_pixel[2] < 175) or \
                            (other_pixel[0] < 20 and other_pixel[1] > 150 and other_pixel[2] < 20):
                        continue
                    last_pixel = other_pixels - 1
                    break

                if last_pixel == -1:
                    average_pixel = column_index

                else:
                    average_pixel = (last_pixel + column_index) / 2

                # the horizontal position is a perccentage between 0 (far left) and 1 (far right). This will be
                # divided in 5 slots which will be used for finding the labels of the 5 images.
                # If no green pixel was found, than the horiizontal_axis is -1 and the label will be "no target in the image"
                horizontal_position = average_pixel / len(im_list[row_index])
                break
        if horizontal_position != -1:
            break

    #     choose label for moving towards the block (which is in the picture)
    return generate_label(horizontal_position)


def generate_label(pixel_position):
    if pixel_position == -1:
        return 5
    elif pixel_position < 0.33:
        return 2
    elif 0.33 <= pixel_position < 0.66:
        return 0
    elif pixel_position > 0.66:
        return 4


def generate_dataset(folder="image/"):
    data = []
    labels = []
    images_names = []
    counter = 0
    index = 0
    # Walks through all images
    for _, _, names in os.walk(folder):
        # Iterates through every image in the folder
        for name in tqdm(names):
            counter += 1
            # Save partial images-labels results
            if counter % 1000 == 0:
                index += 1
                save_list_to_pickle_file(data, "data" + str(index))
                save_list_to_pickle_file(labels, "labels" + str(index))

            #         # Clean up data and labels
            #         # remove image files
                for im_name in images_names:
                    os.remove(folder + im_name)
                images_names = []

            # Retrieve image and transform it to list
            im = cv2.imread(folder + name, cv2.IMREAD_COLOR)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).tolist()
            image = PIL.Image.fromarray(np.array(im, dtype=np.uint8))
            image = image.convert("RGB")
            horizontal_position = -1
            # Iterate through rows (from the bottom to  the topof the image,  it should recognize closer targets)
            for row_index in range(len(im) - 1, -1, -1):

                # Iterate through columns (meaning that each "column index" is the index of a pixel)
                for column_index in range(len(im[row_index])):
                    # Pixel cell with r g b values
                    pixel = im[row_index][column_index]
                    # If the pixel is green look in the same row if there are other green pixels. If so, check what is the last
                    # green pixel and save it. So, the average green pixel position on the horizontal axis is the average of these two
                    if (pixel[0] < 165 and pixel[1] > 195 and pixel[2] < 175) or (
                            pixel[0] < 20 and pixel[1] > 150 and pixel[2] < 20):
                        last_pixel = -1

                        for other_pixels in range(column_index + 1, len(im[row_index])):
                            other_pixel = im[row_index][other_pixels]
                            if (other_pixel[0] < 165 and other_pixel[1] > 205 and other_pixel[2] < 175) or \
                                    (other_pixel[0] < 20 and other_pixel[1] > 150 and other_pixel[2] < 20):
                                continue
                            last_pixel = other_pixels - 1
                            break

                        if last_pixel == -1:
                            average_pixel = column_index

                        else:
                            average_pixel = (last_pixel + column_index) / 2

                        # the horizontal position is a perccentage between 0 (far left) and 1 (far right). This will be
                        # divided in 5 slots which will be used for finding the labels of the 5 images.
                        # If no green pixel was found, than the horiizontal_axis is -1 and the label will be "no target in the image"
                        horizontal_position = average_pixel / len(im[row_index])
                        break
                if horizontal_position != -1:
                    break

            #     choose label for moving towards the block (which is in the picture)
            label = generate_label(horizontal_position)

            data.append(image)
            labels.append(label)
            images_names.append(name)
            del im
            del image

    return data, labels
