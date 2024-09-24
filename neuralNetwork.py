""" Japanese Flask Application - neuralNetwork.py

This file is used to test and train the neural network with data from CSV files.

This script is imported by image_processing.py when the main_app.py file is running

The packages that must be available to use this file are:
numPy, sciPy
"""


import numpy as np
from scipy import special


class NeuralNetwork:
    """
    Neural Network class

    Attributes
    ----------
    sec_s: list
        The CharIDs of the characters with two or more strokes
    third_s: list
        The CharIDs of the characters with three or more strokes
    fourth_s: list
        The CharIDs of the characters with four strokes
    in_nodes: int
        The number of input nodes
    hidden_nodes: int
        The number of nodes in the hidden layer.
    out_nodes: int
        The number of output nodes (the number of possible characters).
    level: int
        Should be 9 - used during development to test less characters.
    stroke_num: int
        The stroke that is being tested (integer 1-4)
    learn_rate: float
        Float between 0 and 1 - how much the weights are adjusted during training.
    testing_data: list
    training_data: list
    wih: object
    who: object

    # ^^ wih and who are numPy arrays

    Methods
    -------
    def_files()
        Loads the weights and testing/training data for the appropriate stroke.

    activation(x)

    train_levels(list_inputs, list_targets)
        Trains the neural network from a single set of data.

    query(inputs)
    """
    def __init__(self, inputs, hidden, outputs, learn_rate, level, stroke_num):
        self.sec_s = [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15,
                      17, 18, 21, 22, 23, 24, 25, 27, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 43, 45, 46]
        self.third_s = [2, 6, 7, 8, 10, 15, 17, 22, 23, 27, 29, 31, 32, 34, 36, 37, 46]
        self.fourth_s = [17, 22, 31]
        # the number of input nodes (in this case the number of pixels)
        self.in_nodes = inputs
        self.hidden_nodes = hidden
        # The number of possible categories that could be the output.
        self.out_nodes = outputs
        self.level = level
        self.stroke_num = stroke_num
        self.learn_rate = learn_rate

        self.testing_data = None
        self.training_data = None

        self.wih = None
        self.who = None

    def def_files(self):
        """
        Loads the weights and testing/training data for the appropriate stroke.

        If no weights exist, then they are randomly generated from a normal distribution.

        No required parameters.

        Returns
        -------
        None
        """
        try:
            self.wih = np.load("static/neural_weights/input-hidden-All-" + str(self.stroke_num) + ".npy")
            self.who = np.load("static/neural_weights/hidden-output-All-" + str(self.stroke_num) + ".npy")
        except:
            # draws random samples from a normal distribution with mean 0,
            # standard deviation of (the number of in_nodes)^-0.5
            # returns an array of size (self.hidden_nodes, self.in_nodes)
            self.wih = np.random.normal(0.0, pow(self.in_nodes, -0.5), (self.hidden_nodes, self.in_nodes))
            # draws random samples from a normal distribution with mean 0,
            # standard deviation of (the number of hidden_nodes)^-0.5,
            # returns ann array of size (self.out_nodes, self.hidden_nodes)
            self.who = np.random.normal(0.0, pow(self.hidden_nodes, -0.5), (self.out_nodes, self.hidden_nodes))
        # creates lists of testing and training data for the stroke from the appropriate CSV files
        training_file = open("images/TTImages/All-Stroke" + str(self.stroke_num) + ".csv", "r")
        self.training_data = training_file.readlines()
        training_file.close()
        testing_file = open("images/TTImages/All-Stroke" + str(self.stroke_num) + "-test.csv", "r")
        self.testing_data = testing_file.readlines()
        testing_file.close()

    def activation(self, x):
        """
        Applies the logistic sigmoid function to a numPy ndarray.

        Parameters
        ----------
        x: object
            The numPy ndarray to apply the logistic sigmoid function to.

        Returns
        -------
        object
        """
        # a sigmoid function is used - to make the threshold for determining a value smoother and more 'natural'.
        return special.expit(x)

    def train_levels(self, list_inputs, list_targets):
        """
        Trains the neural network from a single set of data.

        Adjusts the attributes wih and who depending on the error from the calculation.


        Parameters
        ----------
        list_inputs: list
            The list of pixel values for a drawing taken from a CSV file (len 784)

        list_targets: list
            The list (len 46) with values 0.01 except the target character with value 0.99

        Returns
        -------
        None
        """
        # creates a 2d array of the list of inputs and transposes it to swap the rows and columns
        inputs = np.array(list_inputs, ndmin=2).T
        # creates a 2d array of the list of targets and transposes it to swap the rows and columns
        targets = np.array(list_targets, ndmin=2).T

        # does dot product matrix multiplication on the array of weights between the input and hidden layers
        # this is the signals that are fed into the hidden layer
        hidden_in = np.dot(self.wih, inputs)
        # uses the sigmoid function to calculate the new values within the hidden nodes
        # these are the values taken out of the hidden layer
        hidden_out = self.activation(hidden_in)

        # does dot product matrix multiplication on the array of weights between the hidden and output layers
        # and the array of outputs to calculate the signals fed into the final layer
        final_in = np.dot(self.who, hidden_out)

        # uses the sigmoid function to calculate the new values that will be outputted from the output layer
        final_out = self.activation(final_in)

        # calculates the error for each value within the array -> the difference between the target (0.01 or 0.99) and
        # the actual output (somewhere between these values)
        out_errors = targets - final_out

        # matrix dot product multiplication between the transposed array of weights between the hidden and output layer
        # and the array of output errors
        hidden_error = np.dot(self.who.T, out_errors)

        # the weights are adjusted based on the error
        # the learn rate is a number between 0 and 1 to determine what percentage of the error a single
        # image will change the weighting by.
        # dot product matrix multiplication is done on the transposed array of the hidden_out array and
        # the errors, these will be small numbers, the weighting is not changed by much each time
        # this also means that the adjustments will be proportional to the error rate, as smaller changes are made
        # as the amount of error becomes smaller
        self.who += self.learn_rate * np.dot((out_errors * final_out * (1.0 - final_out)),
                                             np.ndarray.transpose(hidden_out))
        # this is the same concept as generating the change in self.who
        self.wih += self.learn_rate * np.dot((hidden_error * hidden_out * (1.0 - hidden_out)),
                                             np.ndarray.transpose(inputs))

    def query(self, inputs):
        """
        Passes the inputs through the neural network and returns the array of outputs.


        Parameters
        ----------
        inputs: list
            The list of input pixel values from the CSV file (len 784).

        Returns
        -------
        object
        """
        self.def_files()
        inputs = np.array(inputs, ndmin=2).T

        # does dot product matrix multiplication on the two matrices self.wih and inputs
        # to calculate the signals fed into the hidden layer
        hidden_in = np.dot(self.wih, inputs)
        # applies the sigmoid function to the array, to calculate the output values from the hidden layer.
        hidden_out = self.activation(hidden_in)

        # dot product matrix multiplication to calculate signals into the output layer
        final_in = np.dot(self.who, hidden_out)
        # uses sigmoid function to calculate the final values from the output layer
        final_out = self.activation(final_in)

        # returns the array
        return final_out


class Run(NeuralNetwork):
    """
    Run class

    Imports from superclass NeuralNetwork

    Methods
    -------
    set_vars(stroke: int)
        Sets the values of the attributes stroke_num and out_nodes.

    training_levels(stroke_num: int)
        Uses all of the training data for the specified stroke to train the neural network.

    test_from_drawing(csv_name: str)
        Tests a specified user's drawing - for each stroke in the drawing.

    test_level(stroke_num: int)
        Tests the neural network in its current state to see how accurate it is.
    """
    def __init__(self):
        # the input, hidden and output nodes
        inodes = 784
        hnodes = 100
        onodes = None
        # set to None so that they can have value when the stroke is decided
        stroke_num = None
        level = None

        # The learning rate of the neural network
        learn_rate = 0.25
        super().__init__(inodes, hnodes, onodes, learn_rate, level, stroke_num)

    def set_vars(self, stroke):
        """
        Sets the values of the attributes stroke_num and out_nodes.

        Parameters
        ----------
        stroke: int
            The stroke number of the data that is being tested/used for training.

        Returns
        -------
        None
        """
        self.stroke_num = stroke
        # finds the number of out nodes depending on how many characters have at least that many strokes.
        if self.stroke_num == 1:
            self.out_nodes = 46
        elif self.stroke_num == 2:
            self.out_nodes = len(self.sec_s)
        elif self.stroke_num == 3:
            self.out_nodes = len(self.third_s)
        else:
            self.out_nodes = len(self.fourth_s)

    def training_levels(self, stroke_num):
        """
        Uses all of the training data for the specified stroke to train the neural network.

        Calls train_levels for each item in the training_data list.
        Parameters
        ----------
        stroke_num: int
            The stroke number of the data that will be used.

        Returns
        -------
        None
        """
        self.set_vars(stroke_num)
        self.def_files()
        for record in self.training_data:
            print("next")
            # creates a list of the target number followed by each of the pixel values
            all_values = record.split(",")
            # takes all values in the list
            # (apart from the target number) and converts
            # them to an array where all of the
            # values are a float values from 0-255.
            # then they are divided by 255 and
            # multiplied by 0.99, to obtain values between 0 and 0.99.
            # 0.1 is added so that 0 is never a value in the array.
            inputs = (np.asfarray(all_values[1:]) / 255.0 * 0.99) + 0.01
            # all of the targets (possible outcomes) are set collectively as an array,
            # with each value being 0.01.
            targets = np.zeros(self.out_nodes) + 0.01
            # the target that is the CORRECT value is set to 0.99
            try:
                # finds the index of the correct character.
                if self.stroke_num == 1:
                    inside = int(all_values[0]) - 1
                elif self.stroke_num == 2:
                    inside = int(self.sec_s.index(int(all_values[0])))
                elif self.stroke_num == 3:
                    inside = int(self.third_s.index(int(all_values[0])))
                else:
                    inside = int(self.fourth_s.index(int(all_values[0])))
                targets[inside] = 0.99
                # the instance of the neural network is trained with
                # the array of input values and the target array
                self.train_levels(inputs, targets)
            except:
                pass
        np.save('static/neural_weights/input-hidden-All-' + str(self.stroke_num) + '.npy', self.wih)
        np.save('static/neural_weights/hidden-output-All-' + str(self.stroke_num) + '.npy', self.who)

    def test_from_drawing(self, csv_name):
        """
        Tests a specified user's drawing - for each stroke in the drawing.

        Returns the list of boolean values (whether each stroke was correct) and the list of strings
        indicating which character each stroke was mistaken for.

        Parameters
        ----------
        csv_name: str
            The name of the CSV file to get the data from

        Returns
        -------
        tuple[list[bool], list[str]]
        """
        # reads the CSV file to get a list of the image pixels after each stroke.
        open_csv = open(csv_name, "r")
        strokes = open_csv.readlines()
        this_stroke = 0
        results_list = []
        thoughts = []
        for stroke in strokes:
            errors = 0
            this_stroke += 1
            # if this is a valid drawing.
            if this_stroke < 5:
                self.set_vars(this_stroke)
                # make a list of the values in the csv line
                all_values = stroke.split(",")
                # executes the function query() within the instance of the neural network
                # with the array of the pixel values of the 'images' that are converted to values
                # between 0.01 and 0.99
                # This returns the array of the output
                results = self.query(((np.asfarray(all_values[1:]) / 255.0 * 0.99) + 0.01))

                # finds the index of the most likely character as determined by the neural network.
                result = np.where(results == np.max(results))[0][0]
                print(result)

                # adjusts the index depending on which stroke it is, to get the
                # character that corresponds with the index
                if self.stroke_num == 1:
                    result = result + 1
                elif self.stroke_num == 2:
                    result = self.sec_s[result]
                elif self.stroke_num == 3:
                    result = self.third_s[result]
                elif self.stroke_num == 4:
                    result = self.fourth_s[result]

                # lists of lists of characters that are near-identical after 1 or 2 strokes
                # so that the drawing can be accepted if both the most likely character and
                # the actual character are in the same list
                similar_characters_1 = [[45, 27, 23, 43, 3, 25, 10, 31], [40, 4, 5,
                                        32, 22, 17, 12, 2, 18, 8, 34, 14, 15, 11, 6, 46], [36, 39, 29], [24, 35]]
                similar_characters_2 = [[32, 36, 8], [17, 22], [27, 31, 23, 31]]
                found = False
                # if the stroke being tested is the first, check whether the character has
                # been identified as one with a near-identical first stroke.
                if self.stroke_num == 1:
                    for sets in similar_characters_1:
                        if result in sets:
                            found = True
                            if int(all_values[0]) not in sets:
                                errors += 1
                                thoughts.append(result)
                # if the stroke being tested is the second, check whether the character has
                # been identified as one with a near-identical appearance after the second stroke.
                elif self.stroke_num == 2:
                    for sets in similar_characters_2:
                        if result in sets:
                            found = True
                            if int(all_values[0]) not in sets:
                                errors += 1
                                thoughts.append(result)
                if not found:
                    # if the identified character was not a similar character to the
                    # required result, or the stroke was 3 or 4
                    if str(result) != str(all_values[0]):
                        # if the identified character wasn't the right one...
                        print("The number was:" + str(all_values[0]))
                        # print(results) - this is used to print the array of the
                        # probability of each number being the correct output.
                        print("I thought it was: " + str(result) + "\n")
                        thoughts.append(result)
                        # adds one to the number of errors
                        errors += 1
            else:
                # if the user has drawn more than 4 strokes
                return "Invalid", 0
            if errors != 0:
                # show that this stroke was marked incorrect.
                results_list.append(False)
            else:
                # show that this stroke was marked correct.
                results_list.append(True)
        print("results list: ", results_list)
        # return all of the results and the characters they were mistaken for.
        return results_list, thoughts

    def test_level(self, stroke_num):
        """
        Tests the neural network in its current state to see how accurate it is.

        Used to determine the neural network's accuracy, tests the network with the
        testing data for a stroke, and prints the correct/incorrect and probability so
        that the accuracy can be determined.

        Parameters
        ----------
        stroke_num: int
            The stroke number that is being tested.

        Returns
        -------
        None
        """
        self.set_vars(stroke_num)
        self.def_files()
        tested = 0
        correct = 0
        incorrect = 0
        connections = {}
        for line in self.testing_data:
            tested += 1
            # make a list of the values in the csv line
            all_values = line.split(",")
            # executes the function query() within the instance of the neural network
            # with the array of the pixel values of the 'images' that are converted to values
            # between 0.01 and 0.99
            # This returns the array of the output
            results = self.query(((np.asfarray(all_values[1:]) / 255.0 * 0.99) + 0.01))
            result = np.where(results == np.max(results))[0][0]

            # adjusts the index depending on which stroke it is, to get the
            # character that corresponds with the index
            if self.stroke_num == 1:
                result = result + 1
            elif self.stroke_num == 2:
                result = self.sec_s[result]
            elif self.stroke_num == 3:
                result = self.third_s[result]
            elif self.stroke_num == 4:
                result = self.fourth_s[result]
            # lists of lists of characters that are near-identical after 1 or 2 strokes
            # so that the drawing can be accepted if both the most likely character and
            # the actual character are in the same list
            similar_characters_1 = [[45, 27, 23, 43, 3, 25, 10, 31], [40, 4, 5,
                                    32, 22, 17, 12, 2, 18, 8, 34, 14, 15, 11, 6, 46], [36, 39, 29], [24, 35]]
            similar_characters_2 = [[32, 36, 8], [17, 22], [27, 31, 23, 31]]
            found = False
            if self.stroke_num == 1:
                for sets in similar_characters_1:
                    if result in sets:
                        found = True
                        if int(all_values[0]) not in sets:
                            incorrect += 1
                            print("The number was:" + str(all_values[0]))
                            print("I thought it was: " + str(result) + "\n")
                        else:
                            correct += 1
            elif self.stroke_num == 2:
                for sets in similar_characters_2:
                    if result in sets:
                        found = True
                        if int(all_values[0]) not in sets:
                            incorrect += 1
                            print("The number was:" + str(all_values[0]))
                            print("I thought it was: " + str(result) + "\n")
                        else:
                            correct += 1
            if not found:
                # This if statement just allows me to determine whether
                # there is a specific problem with
                # certain characters being recognised during testing -
                # this condition is met if the network's 'guess'
                # is not the right answer.
                if str(result) != str(all_values[0]):
                    print("The number was:" + str(all_values[0]))
                    # print(results) - this is used to print the array of the
                    # probability of each number being the correct output.
                    print("I thought it was: " + str(result) + "\n")
                    # adds one to the number of errors
                    incorrect += 1
                    # adds to the dictionary of incorrect guesses to show where the neural network is going wrong.
                    try:
                        connections[str(result) + "-" + str(all_values[0])] += 1
                    except:
                        connections[str(result) + "-" + str(all_values[0])] = 1
                else:
                    correct += 1
        print("correct = ", correct)
        print("incorrect = ", incorrect)
        print("tested = ", tested)
        print("probability correct = ", correct/tested)
        print(connections)


if __name__ == "__main__":
    r = Run()
    for y in range(4):
        r.training_levels(1)
        r.training_levels(2)
        r.training_levels(3)
        r.training_levels(4)
    r.test_level(1)
    r.test_level(2)
    r.test_level(3)
    r.test_level(4)
