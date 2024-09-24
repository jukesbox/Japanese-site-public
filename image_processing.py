""" Japanese Flask Application - image_processing.py

This file is used to deal with the CSV files holding testing and training data for the neural network.
It also deals with new drawings that a user has drawn on the website.

The packages that should be installed to be able to run this file are:
PIL, numPy, base64, copy, csv, itertools

The files within the system that must also be available are:
neuralNetwork.py
"""


from PIL import Image
import numpy as np
from neuralNetwork import Run
import base64
import copy
import csv
from itertools import chain

run_neural = Run()


def check(csv_file):
    """
    Shows the first line of the CSV file as a RGB image
    Parameters
    ----------
    csv_file: str
        The path to the CSV file that will have the data to be checked.
    :return:
    """
    # opens the CSV file and writes all of the data to a list - 'data-list'
    data_file = open(csv_file, "r")
    data_list = data_file.readlines()
    data_file.close()

    # splits the first item in the list of CSV lines into a list of individual pixels
    all_values = data_list[0].split(",")
    # reshapes the list into an array to correctly align the pixels
    image_arr = np.asfarray(all_values[1:]).reshape((28, 28))
    img = Image.new('RGB', (28, 28), "white")
    # creates an array of all of the pixels
    pixels = img.load()
    # for each pixel in the image
    for i in range(28):
        for j in range(28):
            # get the rgb values of the current pixel
            # alter the values to be all the same - making a grey colour
            pixels[i, j] = (int(255 - image_arr[j][i]), int(255 - image_arr[j][i]), int(255 - image_arr[j][i]))
    # displays the image
    img.show()


# used when single + training data is submitted
def process_all(list_of_strokes, username, char_num, submission_type):
    """
    Processes the data url taken from the HTML canvas of the user's drawing.

    Makes the image less detailed by reducing it from 420x420 to 28x28 so that the neural network can manage it.
    Converts the image array to CSV values to add to the training data/ user's drawing CSV so that it can be
    used for training or tested by the neural network.

    Returns None if submission_type is "train" - since the submission is not tested by the neural network in this case.


    Parameters
    ----------
    list_of_strokes: list
        The list containing strings of the image data after each stroke.
    username: str
        The username of the user who submitted the drawing
    char_num: int
        The CharID of the character that was drawn
    submission_type: str
        Whether the drawing was submitted in a "game" or to "train"

    Returns
    -------
    tuple[list[int], list[int], bool, list[int]]
    """

    x = 0
    for stroke in list_of_strokes:
        filename = "images/tmp_file_" + username + ".png"
        # increments the stroke number
        x += 1
        # the string data URL is passed into this variable
        stroke_url = list_of_strokes[stroke]
        # Removing the useless part of the url.
        img_data = stroke_url[21:]
        # writes the image data from the data URL to a png by using base64 decoding
        # on the data URL
        with open(filename, "wb") as fh:
            fh.write(base64.b64decode(img_data))
        # processes the png to make the smaller image. This also adds the
        # character to the CSV file for the training data for the specific
        # stroke number.
        image = Image.open(filename)
        text = str(char_num)
        new_img = Image.new('RGB', (28, 28), "white")
        # creates an array of the pixels
        pixels = new_img.load()
        # creates a string with just the correct number (this string will contain the csv for the image)
        # for each pixel in the original image, taking the correct number of steps each time
        # to correctly fit the original image into a 28x28 pixel image
        step = image.size[0] // 28
        for i in range(0, image.size[0], step):
            for j in range(0, image.size[1], step):
                # the average colour of the collection of pixels
                average = 0
                # for each pixel within the larger block
                for a in range(i, i + step):
                    for b in range(j, j + step):
                        # this fixes the orientation of the image by changing the order
                        # but actually gets the colour value
                        original_rgb = image.getpixel((b, a))
                        if original_rgb[3] != 255:
                            original_rgb = (255, 255, 255, 0)
                        # as the image is greyscale, it doesnt matter which value from the tuple is taken
                        # the colour value is added to the average
                        average += original_rgb[0]
                # the total average is divided by the number of pixels.
                average = average // 225
                # assigns the new image's pixel rgb value for the original pixels from this area
                pixels[j / step, i / step] = (255 - average, 255 - average, 255 - average)
                # adds the value to the text string - creating the csv string
                text += "," + str(255 - average)
        # if the drawing is training data, add it to the training data CSV file for the stroke.
        if submission_type == "train":
            file_nm = open("images/TTImages/Level9-Stroke" + str(x) + ".csv", "a")
            file_nm.write(text + "\n")
            file_nm.close()
        else:
            # add the stroke CSV to the user's drawing CSV file.
            csv_file = "images/userGuesses/" + username + ".csv"
            if x == 1:
                # overwrites what is in the file if this is the first stroke
                csv_open = open(csv_file, "w+")
            else:
                # appends to the file if not
                csv_open = open(csv_file, "a")
            csv_open.write(text + "\n")
            csv_open.close()
    # if the user has submitted the drawing as part of a game (it needs to be marked)...
    if submission_type == "game":
        # run the neural network to check the drawing
        csv_fle = "images/userGuesses/" + username + ".csv"
        results, thought = run_neural.test_from_drawing(csv_fle)
        # if the user has drawn a valid number of strokes (<5)
        if results != "Invalid":
            x = 0
            incorrect = []
            correct = []
            success = True
            # for each of the boolean values representing the correctness of the strokes
            for result in results:
                x += 1
                if not result:
                    # the overall drawing is marked incorrect
                    success = False
                    # adds this stroke num to the incorrect strokes
                    incorrect.append(x)
                else:
                    # adds this stroke num to the correct strokes
                    correct.append(x)
            # returns the list of correct strokes, the list of incorrect strokes, whether they got it right overall
            # (bool) and the list of CharIDs that the drawing was mistaken for.
            return correct, incorrect, success, thought
        else:
            return [], [], False, []


def shift_image():
    """
    For each line currently in the testing CSV files, find out how far up/left/down/right the image can go
    before going off the canvas so that the dataset can be greatly increased. Adds all new lines to the CSVs.

    No required parameters

    Returns
    -------
    None
    """

    # a dictionary of all of the CharIDs and the number of strokes the character associated with it has.
    characters_strokes = {"1": 1, "2": 3, "3": 2, "4": 2, "5": 2, "6": 3, "7": 3, "8": 3, "9": 1, "10": 3, "11": 2,
                          "12": 2, "13": 1, "14": 2, "15": 3, "16": 1, "17": 4, "18": 2, "19": 1, "20": 1, "21": 2,
                          "22": 4, "23": 3, "24": 2, "25": 2, "26": 1, "27": 3, "28": 1, "29": 3, "30": 1, "31": 4,
                          "32": 3, "33": 2, "34": 3, "35": 2, "36": 3, "37": 3, "38": 2, "39": 2, "40": 2, "41": 1,
                          "42": 1, "43": 2, "44": 1, "45": 2, "46": 3}
    each_char = {}

    strokes_dict = {"1": 0, "2": 0, "3": 0, "4": 0}

    second = []
    third = []
    fourth = []

    # adds the CharID of each of the characters with at least 2, 3, 4 strokes to the appropriate lists.
    for entry in characters_strokes:
        if characters_strokes[entry] > 1:
            second.append(int(entry))
        if characters_strokes[entry] > 2:
            third.append(int(entry))
        if characters_strokes[entry] == 4:
            fourth.append(int(entry))

    # adds entries to the dictionary with key CharID and value 0 (the number of times that character has appeared)
    for x in range(1, 47):
        each_char[x] = 0

    # for each of the files containing training data, open and write the lines to a list
    file1 = open("images/old_images/Level9-Stroke1.csv", "r")
    images_1 = file1.readlines()
    file1.close()
    file2 = open("images/old_images/Level9-Stroke2.csv", "r")
    images_2 = file2.readlines()
    file2.close()
    file3 = open("images/old_images/Level9-Stroke3.csv", "r")
    images_3 = file3.readlines()
    file3.close()
    file4 = open("images/old_images/Level9-Stroke4.csv", "r")
    images_4 = file4.readlines()
    file4.close()
    # for each item in each of the lists
    for tm_strokes in [images_1, images_2, images_3, images_4]:
        for image_csv in tm_strokes:
            lines_to_write = []
            # create a list of values in the CSV line
            separated = image_csv.split(",")
            # as the charID is always the first value in the CSV line
            char_num = int(separated[0])
            # the number of strokes that the current character has.
            no = str(characters_strokes[str(char_num)])

            # gets the CSV line of the final image of the current drawing
            # (so that when the current stroke is moved, it only moves as much as the final image can
            # before it moves off the canvas)
            if no == "2":
                separated = images_2[strokes_dict["2"]].split(",")
            elif no == "3":
                separated = images_3[strokes_dict["3"]].split(",")
            elif no == "4":
                separated = images_4[strokes_dict["4"]].split(",")

            # reshapes the CSV line to an array representing the 28x28 image
            image_arr_np = np.asfarray(np.reshape(separated[1:], (28, 28)))

            strokes_dict[no] += 1
            # image_arr = [rows][columns]
            each_char[char_num] += 1
            # how many places the array can go 'up' before the image goes off the canvas.

            # index at the top
            i_t = -1
            end = False
            while not end:
                i_t += 1
                # check that all of the 'pixels' on the top row are white
                for item in image_arr_np[i_t]:
                    # if they're not, the image can't move any further up.
                    if item != 0:
                        end = True
            i_t = abs(i_t)

            # how many places the array can go 'down' before the image goes off the canvas.
            i_b = 1
            end = False
            while not end:
                i_b -= 1
                # check that all of the 'pixels' on the current row are white
                for item in image_arr_np[i_b]:
                    # if not, they can't move any further down.
                    if item != 0:
                        end = True
            i_b = abs(i_b)

            # how many places the array can go 'left' before the image goes off the canvas.
            i_l = -1
            end = False
            while not end:
                i_l += 1
                # check that all of the 'pixels' on the current column are white
                for j in range(len(image_arr_np)):
                    # if not, the image can't go any further left.
                    if image_arr_np[j][i_l] != 0:
                        end = True
            i_l = abs(i_l)

            # how many places the array can go 'right' before the image goes off the canvas.
            i_r = 0
            end = False
            while not end:
                i_r -= 1
                # check that all of the 'pixels' on the current row are white
                for j in range(len(image_arr_np)):
                    # if not, the image can't go any further right
                    if image_arr_np[j][i_r] != 0:
                        end = True
            i_r = abs(i_r)


            # (the abs at the end of each calculation makes the value positive)

            # adjusts the found values so that the maximum that the drawing can go in any direction is 4 pixels
            # this speeds up the algorithm slightly
            if i_t > 4:
                i_t = 4
            if i_b > 4:
                i_b = 4
            if i_l > 4:
                i_l = 4
            if i_l > 4:
                i_l = 4

            # the total that the image can move in the x direction
            total_y = i_l + i_r
            # the total that the image can move in the y direction
            total_x = i_t + i_b

            # gets the current CSV value (not the final stroke of this character anymore)
            separated = image_csv.split(",")
            image_arr_np = np.asfarray(np.reshape(separated[1:], (28, 28)))
            image_arr = image_arr_np.tolist()

            # moves the image the furthest down and left that it can go reaching the found limit.
            for x in range(i_b):
                tmp = image_arr.pop(-1)
                image_arr.insert(0, tmp)
            for y in range(i_l + 1):
                for a in range(len(image_arr)):
                    tmp2 = image_arr[a].pop(0)
                    image_arr[a].append(tmp2)

            # recreates the list with the new position - from array
            lis = list(chain.from_iterable(image_arr))
            lis.insert(0, int(char_num))
            # creates an array of the newly created list and adds it to the lines to write to the CSV file
            array = np.asfarray(lis)
            lines_to_write.append(array.astype(int))

            # creates a copy of the current array to keep as the array changes.
            tmp_image_arr = copy.deepcopy(image_arr)

            rep = 0
            # move the array as far up as possible (by the found values earlier)
            for c in range(total_x + 1):
                rep += 1
                # move the array as far right as possible (by the found values)
                for d in range(total_y):
                    # for each of the arrays in the array, pop the final value and add it to the
                    # beginning of the array
                    for a in range(len(tmp_image_arr)):
                        tmp3 = tmp_image_arr[a].pop(-1)
                        tmp_image_arr[a].insert(0, tmp3)
                    # converts the new array to a list and inserts the char_num -
                    # so that it matches the format of the CSV values
                    lis = list(chain.from_iterable(tmp_image_arr))
                    lis.insert(0, int(char_num))
                    array = np.asfarray(lis)
                    # add the new position to the lines to write.
                    lines_to_write.append(array.astype(int))
                tmp_image_arr = copy.deepcopy(image_arr)
                # moves it back to the original position (far left) so that it can be moved up slightly again
                for re in range(rep):
                    tmp1 = tmp_image_arr.pop(0)
                    tmp_image_arr.append(tmp1)

            # in the correct file for the stroke, add all of the new CSV lines.
            if tm_strokes == images_1:
                with open("images/TTImages/character_copies_1.csv", "a", newline='') as fle:
                    writer = csv.writer(fle)
                    writer.writerows(lines_to_write)
            elif tm_strokes == images_2:
                with open("images/TTImages/character_copies_2.csv", "a", newline='') as fle:
                    writer = csv.writer(fle)
                    writer.writerows(lines_to_write)
            elif tm_strokes == images_3:
                with open("images/TTImages/character_copies_3.csv", "a", newline='') as fle:
                    writer = csv.writer(fle)
                    writer.writerows(lines_to_write)
            else:
                with open("images/TTImages/character_copies_4.csv", "a", newline='') as fle:
                    writer = csv.writer(fle)
                    writer.writerows(lines_to_write)


def show_image(arr):
    """
    Shows how an image looks from an array.

    This is used to check that image data/CSVs etc. have been processed correctly.

    Parameters
    ----------
    arr: the array to use to display the image.

    Returns
    -------
    None
    """
    image = Image.fromarray(arr)
    image.show()


def copies(level_num, test=False):
    """
    Rotates each image in a testing/training image file a number of times to create more similar byt not identical
    data in the dataset.

    Note:
    This function was only used during development when characters from different
    levels were in different CSV files (hence the level_num parameter).

    Parameters
    ----------
    level_num: int
        The level of characters that are being duplicated.
    test: bool
        Default false, whether it is the testing data that is being duplicated.

    Returns
    -------
    None
    """
    # for each of the 4 strokes.
    for y in range(1, 5):
        try:
            # open the appropriate file for what is being duplicated.
            if test:
                image_file = open("images/TTImages/Level" + str(level_num) + "-Stroke" + str(y) + "-test.csv")
            else:
                image_file = open("images/TTImages/Level" + str(level_num) + "-Stroke" + str(y) + ".csv")
            images = image_file.readlines()
            image_file.close()
            lines_to_add = []
            # for each of the images, rotate the image by 5 degrees each direction.
            for image_csv in images:
                for x in range(-5, 5):
                    separated = image_csv.split(",")
                    # remove the char_num before rotating the array.
                    char_num = str(separated[0])
                    image_arr_np = np.asfarray(np.reshape(separated[1:], (28, 28)))
                    original = Image.fromarray(image_arr_np)
                    rotated = original.rotate(x)
                    array = np.asfarray(rotated)
                    # convert the array back to a list and add the char_num at index 0
                    lis = list(chain.from_iterable(array))
                    lis.insert(0, int(char_num))
                    # single dimensional array
                    array = np.asfarray(lis)
                    # add the array to the CSV lines to add
                    lines_to_add.append(array.astype(int))
            # add the lines to the appropriate testing/training file.
            if test:
                with open("images/TTImages/Level" + str(level_num) + "-Stroke" + str(y) + "-test.csv", "a", newline='') as fle:
                    writer = csv.writer(fle)
                    writer.writerows(lines_to_add)
            else:
                with open("images/TTImages/Level" + str(level_num) + "-Stroke" + str(y) + ".csv", "a", newline='') as fle:
                    writer = csv.writer(fle)
                    writer.writerows(lines_to_add)
        except:
            pass


def get(level_make, numbers):
    """
    This function was used to separate the file containing all of the characters for a certain stroke into
    files separated by level.

    Parameters
    ----------
    level_make: int
        The level of the characters to add to the file
    numbers: list
        The list of CharIDs of the characters to add to the file.

    Returns
    -------
    None
    """
    # for each stroke 1-4
    for x in range(1, 5):
        try:
            # add all lines in the CSV file to a list
            with open("images/TTImages/character-Stroke" + str(x) + ".csv", "r") as fle:
                characters = fle.readlines()
            adding = []
            # for each line in the CSV, if the charID of the image in the line is in the list of
            # CharIDs passed into the function, add the line to the list that will be added into the file.
            for char in characters:
                split = char.split(",")
                if int(split[0]) in numbers:
                    array = np.asfarray(split)
                    adding.append(array.astype(int))

            # insert all appropriate lines into the new file.
            with open("images/TTImages/Level" + str(level_make) + "-Stroke" + str(x) + ".csv", "a", newline='') as fle:
                writer = csv.writer(fle)
                writer.writerows(adding)
        except:
            pass


if __name__ == "__main__":
    shift_image()
    pass
