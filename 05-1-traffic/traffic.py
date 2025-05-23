import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    images, labels = load_data(sys.argv[1])

    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    model = get_model()

    model.fit(x_train, y_train, epochs=EPOCHS)

    model.evaluate(x_test,  y_test, verbose=2)

    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")

def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []

    for category in range(NUM_CATEGORIES):
        folder_path = os.path.join(data_dir, str(category))

        if not os.path.isdir(folder_path):
            continue

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            try:
                img = cv2.imread(file_path)
                if img is None:
                    raise ValueError("Could not read image.")

                img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                images.append(img)
                labels.append(int(category))

            except Exception as e:
                print(f"Failed to load {file_path}: {e}")

    return images, labels 


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.models.Sequential()

    model.add(tf.keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(30, 30, 3)))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))


    model.add(tf.keras.layers.Conv2D(64, (3, 3), activation="relu"))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))

    model.add(tf.keras.layers.Flatten())

    model.add(tf.keras.layers.Dense(128, activation="relu"))

    model.add(tf.keras.layers.Dropout(0.3))

    model.add(tf.keras.layers.Dense(43, activation="softmax"))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model


if __name__ == "__main__":
    main()
