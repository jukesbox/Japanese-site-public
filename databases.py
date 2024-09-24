""" Japanese Flask Application - databases.py

This file is used to deal with most SQL queries and data within the database.

This script is imported by main_app.py when the main program is run.

The packages that should be installed to be able to run this file are:
werkzeug.security, sqlite3, time, random
"""

import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import time
import random


# the main database class that is used to execute queries, and return results
class Database:
    """
    Database class

    The class that connects to the database to execute all SQL queries.

    Attributes
    ---------
    db: str
        The path to the database that is to be accessed for all queries.

    Methods
    ---------
    execute_query(sql: str, tup: tuple)
        Connects to the database and executes the SQL query passed in.

    execute_single_response(sql: str, tup: tuple)
        Connects to the database, executes the SQL query, and returns a single row.

    execute_return_id(sql: str, tup: tuple))
        Connects to the database, executes the SQL query and returns the primary key of the row just added.

    execute_multiple_responses(sql: str, tup: tuple))
        Connects to the database, executes the SQL query, and returns all responses.

    drop_table(table_name: str)
        Deletes the table with the name 'table_name'

    """

    def __init__(self):
        # defines the database that will be used for all queries
        self.db = "databases/website_database2.db"

    # used when something is added to/deleted from the database
    def execute_query(self, sql, tup):
        """
        Connects to the database and executes the SQL query passed in.

        Used for INSERT and DELETE queries - no values are returned from this method.

        parameters
        ---------
        sql: str
            the SQL query to be executed
        tup: tuple
            additional variables to be added into the SQL query, can be empty tuple.

        returns
        --------
        None
        """
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tup)
            conn.commit()

    def execute_single_response(self, sql, tup):
        """
        Connects to the database, executes the SQL query, and returns a single row.

        This is used for SELECT queries, when only one returned row is expected,
        or to just get the first result.

        parameters
        ---------
        sql: str
            the SQL query to be executed
        tup: tuple
            additional variables to be added into the SQL query, can be empty tuple.

        returns
        --------
        tuple
        """
        with sqlite3.connect(self.db) as db:
            cursor = db.cursor()
            cursor.execute(sql, tup)
            result = cursor.fetchone()
            return result

    def execute_return_id(self, sql, tup):
        """
        Connects to the database, executes the SQL query and returns the primary key of the row just added.

        Used when a new chat/game is added and the system needs to know the ID of the game/chat
        for the user to be admitted.

        parameters
        ---------
        sql: str
            the SQL query to be executed
        tup: tuple
            additional variables to be added into the SQL query, can be empty tuple.

        returns
        --------
        integer
        """
        with sqlite3.connect(self.db) as db:
            cursor = db.cursor()
            cursor.execute(sql, tup)
            return cursor.lastrowid

    def execute_multiple_responses(self, sql, tup):
        """
        Connects to the database, executes the SQL query, and returns all responses.

        Used for SELECT queries where one or more responses are expected.

        parameters
        ----------
        sql: str
            the SQL query to be executed
        tup: tuple
            additional variables to be added into the SQL query, can be empty tuple.

        returns
        --------
        list
        """
        with sqlite3.connect(self.db) as db:
            cursor = db.cursor()
            cursor.execute(sql, tup)
            result = cursor.fetchall()
            return result

    # deletes a database table
    def drop_table(self, table_name):
        """
        Used during development to delete tables that don't have the correct columns/contents

        parameters
        ---------
        table_name: string
            the name of the table to be dropped.

        returns
        --------
        None
        """
        sql = "DROP TABLE " + table_name
        self.execute_query(sql, ())


# the UserTable deals with data directly associated to the user - such as their email or password
# A subclass of Database - meaning that all SQL queries can be executed from the parent class
class UserTable(Database):
    """
    UserTable Class

    Inherits from the superclass Database.

    Deals with data associated to the user themself, and the UserTable in the database.

    Methods
    -------
    create_table()
        Creates the table in the database.

    update_data(values: tuple)
        Updates the user's record in the database with their details.

    get_user_level(userid: int)
        Gets the user's current level from the database.

    set_otp(username: str)
         Generates a new OTP for the user and adds it to the user's record.

    login_otp(username: str, otp: str)
        Validates the details that the user has entered using the OTP.

    clear_otp(username: str)
        Ensures that an OTP cannot be used again.

    get_email_name(username: str)
        Gets a user's email address, given their name.

    get_email(user_id: int)
        Gets a user's email address, given their UserID.

    leaderboard()
        Returns the top 10 users by TotalPoints earned.

    add_total_points(user: int, points: int)
        Adds points to the user's TotalPoints

    username_exists(username: str)
        Checks if a username is already being used.

    email_exists(email: str)
        Checks if an email address is already being used.

    find_id(username: str)
        Gets the UserID associated with a username.

    find_username(user: int)
        Gets the Username associated with a UserID

    validate_password(password: str)
        Checks whether a password is secure enough.

    validate_new_account(details: tup)
        Checks whether the username and password are unique.

    add_account(set_: tup)
        Adds a new record to the UserTable with the specified details.

    validate_login(user: str, password: str)
        When a user tries to log in, the username and password are checked in the database.

    get_user_points(user_id: int)
        Returns the TotalPoints that a user has earned.

    delete_users(username: str)
        Used to delete incorrectly recorded users during development.

    user_stats(userid: int)
        Returns the user's stats.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the table in the database.

        No parameters.

        returns
        -------
        None
        """
        # SQL query to create the database table
        sql = "CREATE TABLE IF NOT EXISTS UserTable(" \
              "UserID INTEGER," \
              "Username TEXT," \
              "Password TEXT," \
              "EmailAddress TEXT," \
              "TotalPoints INTEGER," \
              "GoldPieces INTEGER," \
              "UserLevel INTEGER," \
              "UserStreak INTEGER," \
              "OTP INTEGER," \
              "EmailPermission BOOLEAN," \
              "primary key(UserID)" \
              ")"
        self.execute_query(sql, ())

    # when the user has tried to change their details, and it is valid
    def update_data(self, values):
        """
        Updates the user's record in the database with their details.

        Parameters
        -------
        values: tuple[str, str, str, int]
            A tuple containing the user's username, password, email and userid.

        returns
        --------
        None
        """
        username, password, email, userid = values
        sql = "UPDATE UserTable SET Username = '" + str(username) + "', Password = '" + str(password) + \
              "', EmailAddress = '" + str(email) + "' WHERE UserID = '" + str(userid) + "'"
        self.execute_query(sql, ())

    def get_user_level(self, userid):
        """
        Gets the user's current level from the database.

        Parameters
        ----------
        userid: integer
            The user's UserID as it is held in the database table.

        returns
        --------
        integer
        """
        sql = "SELECT UserLevel FROM UserTable WHERE UserID = '" + str(userid) + "'"
        return self.execute_single_response(sql, ())[0]

    def set_otp(self, username):
        """
        Generates a new OTP for the user and adds it to the user's record.

        Returns the OTP and the email address of the user so that an email #
        can be sent with the OTP.

        Parameters
        ----------
        username: str
            The user's Username as stored in the database.

        returns
        --------
        (str, str)
        """
        random_otp = ""
        # creates a pseudorandom 6 digit string that will be sent to the user, and they must enter it to login
        for num in range(6):
            random_otp += str(random.randint(0, 9))
        # updates the database to hold the correct pin
        sql = "UPDATE UserTable SET OTP = '" + generate_password_hash(random_otp) + "' WHERE Username = '" \
              + str(username) + "'"
        self.execute_query(sql, ())
        # gets the user's email so that this can be returned along with the pin to send to the user.
        email = self.get_email_name(username)
        return random_otp, email

    def login_otp(self, username, otp):
        """
        Validates the details that the user has entered using the OTP.

        Parameters
        ---------
        username: str
            The user's username as it is stored in the database.
        otp: str
            The OTP that the user has entered.

        returns
        --------
        boolean
        """
        # gets the user's current pin as stored in the database
        sql = "SELECT OTP FROM UserTable WHERE Username = '" + str(username) + "'"
        response = self.execute_single_response(sql, ())
        if not response:
            # i.e. the username doesn't exist
            return False
        else:
            # if the user has a valid pin stored in the database
            if str(otp) != "0":
                # checks whether the pin stored in the database is the same as the pin that has been entered
                # (the pin is hashed in the database for security)
                if check_password_hash(response[0], otp):
                    # the user can be logged in
                    return True
            # the user is can't be logged in
            return False

    def clear_otp(self, username):
        """
        Ensures that an OTP cannot be used again.

        Sets the OTP to 0 (an invalid value) and returns the user's UserID and email address
        to be stored in the session.

        Parameters
        ----------
        username: str
            The user's Username as it appears in the database.

        returns
        --------
        tuple[int, str]
        """
        # when the user has logged in using the pin, the pin is reset to be '0' which is not accepted when
        # a user tries to login with it. This ensures that the user cannot log in more than once with the same pin
        sql = "UPDATE UserTable SET OTP = '" + str(0) + "' WHERE Username = '" + username + "'"
        self.execute_query(sql, ())
        # gets the user's id and email to return to log in the user's session
        sql = "SELECT UserID, EmailAddress FROM UserTable WHERE Username = '" + username + "'"
        return self.execute_single_response(sql, ())

    def get_email_name(self, username):
        """
        Returns a user's email address, given their username

        Parameters
        ----------
        username: str
            The user's Username as it should appear in the database.

        returns
        --------
        str
        """

        sql = "SELECT EmailAddress FROM UserTable WHERE Username = '" + str(username) + "'"
        return self.execute_single_response(sql, ())[0]

    def get_email(self, user_id):
        """
        Returns a user's email address, given their user_id

        Parameters
        ----------
        user_id: int
            The user's UserID as it should appear in the database.

        returns
        --------
        str
        """
        sql = "SELECT EmailAddress FROM UserTable WHERE UserID = '" + str(user_id) + "'"
        result = self.execute_single_response(sql, ())
        return result[0]

    def leaderboard(self):
        """
        Returns the top 10 users by TotalPoints earned.

        No required parameters.

        returns
        --------
        list
        """
        sql = "SELECT Username, TotalPoints FROM UserTable ORDER BY TotalPoints DESC LIMIT 10"
        result = self.execute_multiple_responses(sql, ())
        return result

    def add_total_points(self, user, points):
        """
        Adds points to the user's TotalPoints.

        Parameters
        ----------
        user: int
            The user's UserID as it appears in the database
        points: int
            The number of points to be added.

        returns
        --------
        None.
        """
        # adds the points that a user has earned while playing a round of a game
        sql = "UPDATE UserTable SET TotalPoints = TotalPoints + '" + str(points) + "' WHERE UserID = '" + str(
            user) + "'"
        self.execute_query(sql, ())

    def username_exists(self, username):
        """
        Checks whether a username is already being used.

        Parameters
        ----------
        username: str
            The username to check the database for.

        returns
        --------
        Boolean
        """
        sql = "SELECT * FROM UserTable WHERE Username = '" + str(username) + "'"
        result = self.execute_single_response(sql, ())
        # return whether a row was returned or not
        if result:
            return True
        else:
            return False

    def email_exists(self, email):
        """
        Checks whether an email address is already being used.

        Parameters
        ----------
        email: str
            The email address to check the database for.

        returns
        --------
        Boolean
        """
        sql = "SELECT * FROM UserTable WHERE EmailAddress = '" + email + "'"
        response = self.execute_single_response(sql, ())
        if response:
            return True
        else:
            return False

    def find_id(self, username):
        """
        Gets the UserID associated with a username.
        Returns False if no record with that Username exists.

        Parameters
        ----------
        username: str
            The Username to get the UserID for.

        returns
        --------
        int
        """
        sql = "SELECT UserID FROM UserTable WHERE Username = '" + username + "'"
        user_id = self.execute_single_response(sql, ())
        try:
            return user_id[0]
        except:
            return 0

    def find_username(self, user):
        """
        Gets the Username associated with a UserID.
        Returns False if no record with that UserID exists.

        Parameters
        ----------
        user: int
            The UserID to get the Username for.

        Returns
        -------
        str
        """
        sql = "SELECT Username FROM UserTable WHERE UserID = '" + str(user) + "'"
        result = self.execute_single_response(sql, ())
        try:
            return result[0]
        except:
            return ""

    def validate_password(self, password):
        """
        Checks whether a password is secure enough.

        If a condition is not met, the error message is added and it will be added to the
        string that will be shown to the user.

        Parameters
        ----------
        password: str

        Returns
        -------
        tuple[bool, list]
        """
        message = []
        char = False
        # Checks password length
        if len(password) > 7:
            # checks for special characters.
            for character in "@!£$%&*#":
                if character in password:
                    char = True
            if char:
                # Checks if there are different cases of letters.
                if password.lower() != password and password.upper() != password:
                    # the password is valid - the message will be empty.
                    return True, message
                else:
                    message.append("Your password can't be all one case!")
            else:
                message.append("Your password must contain a special character!")
        else:
            message.append("Your password must be at least 8 character long!")
        # the password is invalid as it does not meet at least one of the requirements.
        return False, message

    def validate_new_account(self, details):
        """
        Checks whether the username ans password are unique

        Parameters
        ----------
        details: tuple[str, str]
            Contains the entered Username and Email.

        returns
        --------
        list
        """
        # when a user tries to create a new account
        # list to hold the errors
        invalidStuff = []
        username = details[0]
        email = details[1]
        # checks whether the email and/or username are already in use
        userInvalid = self.username_exists(username)
        emailInvalid = self.email_exists(email)
        if userInvalid is True:
            invalidStuff.append("Username")
        if emailInvalid is True:
            invalidStuff.append("Email")
        # returns the list of errors
        return invalidStuff

    def add_account(self, set_):
        """
        Adds a new record to the UserTable with the specified details

        Parameters
        ----------
        set_: tup[str, str, str, bool]
            The set of values specific to the user to be added into the new record.

        Returns
        --------
        None
        """
        # when an account is deemed to be valid, the data can be added to the database
        user, passwd, email, emails = set_
        # the user's personal details as well as some default values are added to the database
        values = (user, passwd, email, 0, 0, emails, 0, 0, 0)
        sql = "INSERT INTO UserTable(Username, Password, EmailAddress, " \
              "TotalPoints, GoldPieces, EmailPermission, UserLevel, UserStreak, OTP) VALUES (?,?,?,?,?,?,?,?,?)"
        self.execute_query(sql, values)

    def validate_login(self, user, password):
        """
        When a user tries to log in, the username and password are checked in the database.

        Parameters
        ----------
        user: str
            The user's username as it appears in the database.
        password: str
            The password that the user entered to login.

        returns
        -------
        bool
        """
        sql = "SELECT Password FROM UserTable WHERE Username = '" + str(user) + "'"
        response = self.execute_single_response(sql, ())
        if not response:
            # if the username doesn't exist
            return False
        else:
            if check_password_hash(response[0], password):
                # if the password matches the password held for the username entered, then the login is valid
                return True
            return False

    def get_user_points(self, user_id):
        """
        Returns the TotalPoints that a user has earned.

        Parameters
        ----------
        user_id: int
            The user's UserID in the database.

        returns
        -------
        int
        """
        sql = "SELECT TotalPoints FROM UserTable WHERE UserID = '" + str(user_id) + "'"
        result = self.execute_single_response(sql, ())[0]
        return result

    def delete_users(self, username):
        """
        Used to delete incorrectly recorded users during development.

        username: str
            The Username of the user to be deleted.

        returns
        -------
        None
        """
        sql = "DELETE FROM UserTable WHERE Username = '" + str(username) + "' OR Username = 'user6'"
        self.execute_query(sql, ())

    def user_stats(self, userid):
        """
        Returns all of the user's stats.

        parameters
        ----------
        userid: int
            The UserID of the user with the stats to be returned.

        returns
        -------
        tuple[int, int, int, int]
        """
        sql = "SELECT TotalPoints, GoldPieces, UserLevel, UserStreak FROM UserTable WHERE UserID = '" + str(
            userid) + "'"
        return self.execute_single_response(sql, ())


# this class manages the relationships between users
class FriendsTable(UserTable):
    """
    FriendsTable Class.

    Inherits from superclass UserTable.

    Deals with data associated to the FriendsTable and the users within it.

    Methods
    -------
    create_table()
        Creates the FriendsTable in the database.

    add_request(requested: int, received: int)
        Adds a record to the table, indicating a new friend request.

    accept_request(requested: int, received: int)
        Sets Accepted to be True in the friend record between these two users.

    reject_request(requested: int, received: int)
        Deletes the row containing the friend request for two users when
        the recipient rejects the request.

    find_all_requested(user: int)
        Gets all of the pending friend requests for the user.

    get_similar_users(username: str, userid: int)
        Returns a list of users that have usernames that are similar to 'username'.

    get_user_friends(user: int, just_ids:bool)
        Returns a list of the user's friends (their UserIDs and Usernames).

    check_friends(other_user: int, you: int)
        Checks that two users are friends.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the FriendsTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS FriendsTable(" \
              "FriendsID INTEGER," \
              "UserRequested INTEGER," \
              "UserReceived INTEGER," \
              "Accepted BOOLEAN," \
              "primary key(FriendsID)" \
              "foreign key(UserRequested) references UserTable(UserID)" \
              "foreign key(UserReceived) references UserTable(UserID)" \
              ")"
        self.execute_query(sql, ())

    def add_request(self, requested, received):
        """
        Adds a record to the table, indicating a new friend request.

        Parameters
        ----------
        requested: int
            The UserID of the user that made the friend request.
        received: int
            The UserID of the user that the request is made to.

        returns
        -------
        None
        """
        if not self.check_friends(requested, received):
            # adds a row to the table, keeping accepted to be False so that it shows up in
            # friend requests.
            sql = "INSERT INTO FriendsTable(UserRequested, UserReceived, Accepted) VALUES (?,?,?)"
            tup = (requested, received, False)
            self.execute_query(sql, tup)

    def accept_request(self, requested, received):
        """
        Sets Accepted to be True in the friend record between these two users.

        Parameters
        ----------
        requested: int
            The UserID of the user that made the friend request.
        received: int
            The UserID of the user that the request is made to.

        returns
        -------
        None
        """
        # finds the specific row where the user sending the request and the user receiving the
        # request - then sets the Accepted column to True - the users are now friends.
        sql = "UPDATE FriendsTable SET Accepted = True " \
              "WHERE UserRequested = " + str(requested) + " AND UserReceived = " + str(received)
        self.execute_query(sql, ())

    def reject_request(self, requested, received):
        """
        Deletes the row containing the friend request for two users when
        the recipient rejects the request.

        Parameters
        ----------
        requested: int
            The UserID of the user that made the friend request.
        received: int
            The UserID of the user that the request is made to.

        returns
        -------
        None
        """
        # When the user rejects a request, the row in the friends table is deleted when the user requested
        # and received matches the requests.
        sql = "DELETE FROM FriendsTable WHERE UserRequested = '" + \
              str(requested) + "' AND UserReceived = '" + str(received) + "'"
        self.execute_query(sql, ())

    def find_all_requested(self, user):
        """
        Gets all of the pending friend requests for the user.

        Parameters
        ----------
        user: int
            The user that has received the friend requests.

        returns
        -------
        list[tuple[int, str]]
        """
        # gets the UserID and Username of each user that has requested to be friends with this user.
        sql = "SELECT FriendsTable.UserRequested, UserTable.Username " \
              "FROM FriendsTable " \
              "INNER JOIN UserTable ON UserTable.UserID = FriendsTable.UserRequested " \
              "WHERE FriendsTable.UserReceived = '" + str(user) + "' AND Accepted = False"
        requested_users = self.execute_multiple_responses(sql, ())
        return requested_users

    def get_similar_users(self, username, userid):
        """
        Returns a list of users that have usernames that are similar to 'username'.

        Parameters
        ----------
        username: str
            The username that the user searched for.

        userid: int
             The user's UserID as it should appear in the database.

        returns
        --------
        list[tuple[int, str]]
        """
        # gets all users with a username that contains 'username' as searched by the user.
        sql = "SELECT UserID, Username FROM UserTable WHERE Username LIKE '%" + username + "%' LIMIT 8"
        results = self.execute_multiple_responses(sql, ())
        friends = self.get_user_friends(userid)
        results = set(results)
        # gets only the users that the user is not already friends with
        overlap = list(results.intersection(friends))
        results = list(results)
        for item in overlap:
            results.remove(item)
        return results

    def get_user_friends(self, user, just_ids=False):
        """
        Returns the list of all of the user's friends (their UserIDs and Usernames).

        Parameters
        ----------
        user: int
            The user's UserID
        just_ids: bool
            Boolean whether the username of the friends are required,
            defaults to False - if True, only UserIDs are returned

        returns
        -------
        List[tuple[int, str]]
        """
        # gets all of the users that the user is friends with (where the user made the friend request)
        sql = "SELECT UserReceived FROM FriendsTable where UserRequested = '" + str(user) + "' AND Accepted = True"
        tmp = self.execute_multiple_responses(sql, ())
        found = []
        for friend in tmp:
            friend_id = friend[0]
            # if the program needs to return the username as well as ids, added as a tuple
            if not just_ids:
                found.append((friend_id, self.find_username(friend_id)))
            else:
                found.append(friend_id)
        # gets all of the users that the user is friends with (where the user didn't make the friend request)
        sql = "SELECT UserRequested FROM FriendsTable where UserReceived = '" + str(user) + "' AND Accepted = True"
        tmp = self.execute_multiple_responses(sql, ())
        for friend in tmp:
            # the UserID of the friend
            friend_id = friend[0]
            if not just_ids:
                # adds the tuple with the friend's UserID and Username
                found.append((friend_id, self.find_username(friend_id)))
            else:
                found.append(friend_id)

        # returns a list of all the found users.
        return found

    def check_friends(self, other_user, you):
        """
        Checks that two users are friends so that a user can access another user's page.

        Parameters
        ----------
        other_user: int
            The UserID of the user whose page is being accessed
        you: int
            The UserID of the user who is accessing the page.

        returns
        -------
        bool
        """
        # when a user tries to access the page of another user, they must first check whether the users are friends
        other_user = str(other_user)
        you = str(you)
        # checks whether the user made a request to the user and it has been accepted
        sql = "SELECT * FROM FriendsTable where UserRequested = '" + other_user + "' AND UserReceived = '" \
              + you + "' AND Accepted = True"
        tmp = self.execute_single_response(sql, ())
        result = tmp
        if tmp is None:
            # if nothing was found in the first case, checks whether the other user had made a request
            # to the user that was accepted
            sql = "SELECT * FROM FriendsTable where UserReceived = '" + other_user + "' AND UserRequested = '" \
                  + you + "' AND Accepted = True"
            result = self.execute_single_response(sql, ())

        if result is None:
            # if the users are not friends
            return False
        else:
            # if the users are friends
            return True


class EmailSettingTable(UserTable):
    """
    EmailSettingTable class

    Inherits from superclass UserTable.

    Deals with the data related to email permissions for each user.

    Methods
    -------
    create_table()
        Creates the EmailSettingTable table in the database.

    new_row(userid: int)
        Automatically sets a new user's email permissions.

    change_settings(values: list, userid: int)
        Updates a user's email permissions.

    checked(field: str, userid: int)
        Returns whether the user has given permission for a
        particular type of email.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the EmailSettingTable table in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS EmailSettingTable(" \
              "EmailID INTEGER," \
              "EmailReminders BOOLEAN," \
              "EmailInfo BOOLEAN," \
              "EmailPromotion BOOLEAN," \
              "UserID INTEGER," \
              "primary key(EmailID)," \
              "foreign key(UserID) references UserTable(UserID)" \
              ")"
        self.execute_query(sql, ())

    def new_row(self, userid):
        """
        Automatically sets a new user's email permissions.

        Parameters
        ----------
        userid: int
            The UserID of the user whose email permissions are being added.

        returns
        -------
        None
        """
        # creates a row in the table for a new user
        sql = "INSERT INTO EmailSettingTable(EmailReminders, EmailInfo, EmailPromotion, UserID) VALUES" \
              "(?, ?, ?, ?)"
        # automatically sets all values to false - so the user cannot receive any emails (except password reset)
        tup = (False, False, False, userid)
        self.execute_query(sql, tup)

    def change_settings(self, values, userid):
        """
        Updates a user's email permissions.

        Parameters
        ----------
        values: list[bool]
            The list of boolean values indicating for each email type
            whether the user wants them.
        userid: int
            The UserID of the user whose email permissions are being changed.

        returns
        -------
        None
        """
        # when the user changes their settings, the table is updated to reflect their preferences
        sql = "UPDATE EmailSettingTable SET EmailReminders = " + str(values[0]) + ", EmailInfo = " \
              + str(values[1]) + ", EmailPromotion = " + str(values[2]) + " WHERE UserID = " + str(userid)
        self.execute_query(sql, ())

    def checked(self, field, userid):
        """
        Returns whether the user has given permission for a particular type of email.

        Parameters
        ----------
        field: str
            The name of the field in the database.
        userid: int
            the UserID of the user's whose permissions are being checked.

        returns
        -------
        bool
        """
        sql = "SELECT " + field + " FROM EmailSettingTable WHERE UserID = " + str(userid)
        result = self.execute_single_response(sql, ())[0]
        return result


class AwardsTable(Database):
    """
    AwardsTable Class

    Inherits from superclass Database.

    Deals with the user's awards.

    Methods
    -------
    create_table()
        Creates the AwardsTable table in the database.
    create_records()
        Populates the AwardsTable table.
    award_details(award: int)
        Returns the AwardDescription, given an award's AwardID.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the AwardsTable in the database.

        No parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS AwardsTable(" \
              "AwardID INTEGER," \
              "AwardDescription TEXT," \
              "PointsNeeded INTEGER," \
              "StreakNeeded INTEGER," \
              "LevelNeeded INTEGER," \
              "RewardGold INTEGER," \
              "RewardPoints INTEGER," \
              "primary key(AwardID)" \
              ")"
        self.execute_query(sql, ())

    def create_records(self):
        """
        Populates the AwardsTable

        No parameters.

        returns
        -------
        None
        """
        description = ["You earned 100 Points!", "You earned 500 Points!", "You earned 1000 Points!",
                       "You earned 2000 Points!", "You earned 5000 Points!", "You kept a 1 day streak!",
                       "You kept a 7 day streak!", "You kept a 14 day streak!", "You kept a 28 day streak!",
                       "You kept a 365 day streak!", "You completed level 1!", "You completed level 2!",
                       "You completed level 3!", "You completed level 4!", "You completed level 5!"]
        points = [100, 500, 1000, 2000, 5000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        streak = [0, 0, 0, 0, 0, 1, 7, 14, 28, 365, 0, 0, 0, 0, 0]
        level = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5]
        reward_gold = [10, 20, 23, 40, 50, 10, 20, 30, 40, 50, 10, 20, 30, 40, 50]
        reward_point = [100, 200, 300, 400, 500, 100, 200, 300, 400, 500, 100, 200, 300, 400, 500]
        # populating the table with the values defined above - each with descriptions, requirements and rewards
        for x in range(len(points)):
            sql = "INSERT INTO AwardsTable(AwardDescription, PointsNeeded, StreakNeeded, " \
                  "LevelNeeded, RewardGold, RewardPoints) VALUES (?,?,?,?,?,?)"
            tup = (description[x], points[x], streak[x], level[x], reward_gold[x], reward_point[x])
            self.execute_query(sql, tup)

    def award_details(self, award):
        """
        Returns the AwardDescription, given an award's AwardID.

        Parameters
        ----------
        award: int
            The AwardID of an award.

        returns
        -------
        str
        """
        # selects the description of the award based on its id
        sql = "SELECT AwardDescription FROM AwardsTable WHERE AwardID = '" + str(award) + "'"
        result = self.execute_single_response(sql, ())[0]
        return result


class UserAwardsTable(AwardsTable, UserTable):
    """
    UserAwardsTable Class

    Inherits from superclasses AwardsTable and UserTable

    Deals with data in the UserAwardsTable of the database.

    Methods
    -------
    create_table()
        Creates the UserAwardsTable in the database.

    get_user_awards(userid: int)
        Gets the list of names of awards that the user has earned.

    get_award_ids(userid: int, limit: bool)
        Gets the list of IDs of awards that a user has earned.

    check_awards(userid: int)
        Checks whether a user has earned any more awards that have not been added ot the table.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the UserAwardsTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS UserAwardsTable(" \
              "AwardGivenID INTEGER," \
              "UserID INTEGER," \
              "AwardID INTEGER," \
              "AwardDate INTEGER," \
              "primary key(AwardGivenID)" \
              "foreign key(UserID) references UserTable(UserID)" \
              "foreign key(AwardID) references AwardsTable(AwardID)" \
              ")"
        self.execute_query(sql, ())

    def get_user_awards(self, userid):
        """
        Gets the list of names of awards that the user has earned.

        Parameters
        ----------
        userid: int
            The UserID of the user whose awards are being found

        returns
        -------
        list[str]
        """
        # before finding the awards, update them to check that the user hasn't earned more
        self.check_awards(userid)
        # finds the list of awards that the user has
        awards = self.get_award_ids(userid, True)
        name_list = []
        for item in awards:
            name_list.append(self.award_details(item))
        # returns the list of names of the awards that the user has earned
        return name_list

    def get_award_ids(self, userid, limit=False):
        """
        Gets the list of names of awards that the user has earned.

        Parameters
        ----------
        userid: int
            The UserID of the user whose awards are being found
        limit: bool
            Boolean value, whether a maximum of 3 AwardIDs should be returned (default False).

        returns
        -------
        list[int]
        """
        # gets the IDs of the awards that the user has earned so far, to be used for processing
        sql = "SELECT AwardID FROM UserAwardsTable WHERE UserID = '" + str(userid) + "'"
        got_award_list = self.execute_multiple_responses(sql, ())
        # if there isn't a limit to how many results can be returned
        if not limit:
            # adds all of the AwardIDs to the list and returns it
            award_list = []
            for item in got_award_list:
                award_list.append(item[0])
            return award_list
        else:
            # orders all of the awards in the database by value highest to lowest.
            sql = "SELECT AwardID FROM AwardsTable ORDER BY RewardPoints DESC"
            award_list = self.execute_multiple_responses(sql, ())
            # if the number of awards that the user has is > 3
            if len(got_award_list) > 3:
                value_dict = {}
                for item in got_award_list:
                    # new key: AwardID, value: rank of award
                    value_dict[item[0]] = award_list.index(item)

                to_return = []
                # get top 3 awards
                for x in range(3):
                    # sets smallest to a large number that a rank cannot be bigger than.
                    smallest = 100000
                    smallest_id = 0
                    # find the lowest rank number in the value_dict
                    for award in value_dict:
                        if value_dict[award] < smallest:
                            # smallest is the current smallest rank number
                            smallest = value_dict[award]
                            smallest_id = award
                    # add the ID of the best award in the dictionary to the values to return
                    to_return.append(smallest_id)
                    # removes it from the dictionary so it can't be picked again
                    value_dict.pop(smallest_id)
                return to_return
            lst = []
            for item in got_award_list:
                lst.append(item[0])
            got_award_list = lst
            return got_award_list

    # this function checks whether the user has earned any new awards
    def check_awards(self, userid):
        """
        Checks whether a user has earned any more awards that have not been added to the table.

        Parameters
        ----------
        userid: int

        returns
        -------
        None
        """
        # gets the current stats and points for the user
        current_stats = self.user_stats(userid)
        c_points, c_gold, c_level, c_streak = current_stats
        current = self.get_award_ids(userid)
        current_ids = []
        for item in current:
            current_ids.append(item)
        # gets all of the awards from the awards table and their requirements
        sql = "SELECT AwardID, PointsNeeded, StreakNeeded, LevelNeeded FROM AwardsTable"
        all_awards = self.execute_multiple_responses(sql, ())
        awards_to_add = []
        # for each award
        for award in all_awards:
            id_, points, streak, level = award
            # if the user doesn't already have the award
            if id_ not in current_ids:
                # if the user meets all of the requirements...
                if c_points >= points:
                    if c_level >= level:
                        if c_streak >= streak:
                            awards_to_add.append(id_)
        # for each of the awards that have to be added
        for awd in awards_to_add:
            tup = (userid, awd, str(round(time.time())))
            sql = "INSERT INTO UserAwardsTable(UserID, AwardID, AwardDate) VALUES (?,?,?)"
            self.execute_query(sql, tup)


class UserLevelsTable(UserTable):
    """
    UserLevelsTable Class

    Inherits from superclass UserTable.

    Deals with data related to the UserLevelsTable table in the database.

    Methods
    -------
    create_table()
        Creates the UserLevelsTable table in the database.

    finish_level(userid: int, level_complete: int)
        Adds the completed level to the user's record.

    get_levels(userid: int)
        Returns the list of LevelIDs of the levels that the user has completed.

    get_allowed_chars(userid: int)
        Gets the list of CharIDs of the characters that the user knows.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the UserLevelsTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS UserLevelsTable(" \
              "UserLevelID INTEGER," \
              "UserID INTEGER," \
              "LevelID INTEGER," \
              "DateCompleted INTEGER," \
              "primary key(UserLevelID)," \
              "foreign key(UserID) references UserTable(UserID)," \
              "foreign key(LevelID) references LevelsTable(LevelID)" \
              ")"
        self.execute_query(sql, ())

    def finish_level(self, userid, level_complete):
        """
        Adds the completed level to the user's record.

        Updates the user's Level in the UserTable to be the highest number that they have completed.

        Parameters
        ----------
        userid: int
            The UserID of the user that has completed the level

        level_complete: int
            The LevelID of the level that the user has completed.

        returns
        -------
        None
        """
        # when the user has completed a level
        # adds the level to the user's completed levels
        current_levels = self.get_levels(userid)
        if level_complete not in current_levels:
            sql = "INSERT INTO UserLevelsTable(UserID, LevelID, DateCompleted) VALUES (?,?,?)"
            tup = (userid, level_complete, str(round(time.time())))
            self.execute_query(sql, tup)
        # updates the user's level to be the most recent one completed
        max_level = max(self.get_levels(userid))
        sql = "UPDATE UserTable SET UserLevel = '" + str(max_level) + "' WHERE UserID = '" + str(userid) + "'"
        self.execute_query(sql, ())
        level_complete = int(level_complete)
        add_points = level_complete * 10
        # adds points to the user's total
        sql = "UPDATE UserTable SET TotalPoints = TotalPoints + '" + str(add_points) + "' WHERE UserID = '" \
              + str(userid) + "'"
        self.execute_query(sql, ())

    def get_levels(self, userid):
        """
        Returns the list of LevelIDs of the levels that the user has completed.

        Parameters
        ----------
        userid: int
            The UserID of the user whose completed levels are to be found

        returns
        -------
        list[int]
        """
        sql = "SELECT LevelID FROM UserLevelsTable WHERE UserID = '" + str(userid) + "'"
        result = self.execute_multiple_responses(sql, ())
        returns = []
        for item in result:
            returns.append(item[0])
        return returns

    def get_allowed_chars(self, userid):
        """
        Gets the list of CharIDs of the characters that the user knows.

        Parameters
        ----------
        userid: int
            The UserID of the user whose allowed characters are to be found.

        returns
        -------
        list[int]
        """
        # gets the CharIDs of the characters that are in the levels that the user has completed.
        sql = "SELECT CharTable.CharID " \
              "FROM UserLevelsTable " \
              "INNER JOIN CharTable ON UserLevelsTable.LevelID = CharTable.CharLevel " \
              "WHERE UserLevelsTable.UserID = '" + str(userid) + "'"
        result = self.execute_multiple_responses(sql, ())
        returns = []
        for item in result:
            if item[0] not in returns:
                returns.append(item[0])
        return returns


class LevelsTable(Database):
    """
    LevelsTable Class

    Inherits from superclass Database.

    Deals with data related to the LevelsTable in the database.

    Methods
    -------
    create_table()
        Creates the LevelsTable table in the database.

    populate_levels()
        Resets the LevelsTable table in the database and populates with all data.

    get_level_stuff(level: int)
        Gets the LevelText and LevelPoints from the database for a specified level.

    get_levels()
        Gets the LevelID and LevelName from the database for all levels.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the LevelsTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS LevelsTable(" \
              "LevelID INTEGER," \
              "LevelName TEXT," \
              "LevelText TEXT," \
              "LevelPoints INTEGER," \
              "primary key(LevelID)" \
              ")"
        self.execute_query(sql, ())

    def populate_levels(self):
        """
        Resets the LevelsTable table in the database and populates with all data.

        No required parameters.

        Returns
        -------
        None
        """
        self.drop_table("LevelsTable")
        self.create_table()
        # some primitive text to populate the levels table. In a real situation where this app is used,
        # a lot more data would be added to aide the user's learning
        levels = {"Level 1": "In this lesson you will learn the characters　ん,あ,い,う,え and お."
                             "//In Japanese, the sounds of the characters stay the same, regardless of the word or "
                             "characters around it.//The character system used in these lessons is Hiragana - "
                             "which can together spell any Japanese word.//"
                             "Make sure you have memorised the characters before moving on!",
                  "Level 2": "In this lesson you will learn the characters か,き,く,け and こ."
                             "//There are 46 Hiragana characters in total, but the number is increased "
                             "when Dakuten are used.//Adding Dakuten to ka, ki, ku, ke and ko make the sounds "
                             "ga, gi, gu, ge and go. The characters with dakuten look like this: が, ぎ, ぐ, げ, ご."
                             "//Make sure you have memorised the characters before moving on!.",
                  "Level 3": "In this lesson you will learn the characters さ,し,す,せ and そ"
                             "//This is where the first part of lesson content will be.//Some more info.//Final notes.",
                  "Level 4": "In this lesson you will learn the characters た,ち,つ,て and と"
                             "//This is where the first part of lesson content will be.//Some more info.//Final notes.",
                  "Level 5": "In this lesson you will learn the characters な,に,ぬ,ね and の"
                             "//This is where the first part of lesson content will be.//Some more info.//Final notes.",
                  "Level 6": "In this lesson you will learn the characters は,ひ,ふ,へ and ほ"
                             "//This is where the first part of lesson content will be.//Some more info.//Final notes.",
                  "Level 7": "In this lesson you will learn the characters ま,み,む,め and も"
                             "//This is where the first part of lesson content will be.//Some more info.//Final notes.",
                  "Level 8": "In this lesson you will learn the characters や,ゆ,よ,わ and を"
                             "//This is where the first part of lesson content will be.//Some more info.//Final notes.",
                  "Level 9": "In this lesson you will learn the characters ら,り,る,れ and ろ"
                             "//This is where the first part of lesson content will be.//Some more info.//Final notes."}
        points = 0
        # for each of the levels, add it to the database
        for level in levels:
            points += 10
            sql = "INSERT INTO LevelsTable(LevelName, LevelText, LevelPoints) VALUES (?,?,?)"
            tup = (level, levels[level], points)
            self.execute_query(sql, tup)

    def get_level_stuff(self, level):
        """
        Gets the LevelText and LevelPoints from the database for a specified level.

        Parameters
        ----------
        level: int
            The level that the information should be obtained for.

        Returns
        -------
        tuple[str, int]
        """
        # get all of the information for the level and return it
        sql = "SELECT LevelText, LevelPoints FROM LevelsTable WHERE LevelID = '" + str(level) + "'"
        return self.execute_single_response(sql, ())

    def get_levels(self):
        """
        Gets the LevelID and LevelName from the table for all levels.

        No required parameters.

        Returns
        -------
        tuple[str, int]
        """
        sql = "SELECT LevelID, LevelName FROM LevelsTable"
        return self.execute_multiple_responses(sql, ())


class CharTable(UserLevelsTable):
    """
    CharTable Class

    Inherits from superclass UserLevelsTable.

    Deals with data related to the CharTable in the database.

    Methods
    -------
    create_table()
        Creates the CharTable in the database.

    populate_table()
        Populates the CharTable in the database.

    get_char_level(sound_id: int)
        Gets the level of a specified character from the table.

    get_level_chars(level: int)
        Gets the list of characters that are a certain level.
    find_char(num: int)
        Gets the sound and kana of a character from its CharID.

    select_some(number, userid)
        Selects a specified number of characters from the characters that a user has learned.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the CharTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS CharTable(" \
              "CharID INTEGER," \
              "CharSound TEXT," \
              "CharKana TEXT," \
              "CharLevel INTEGER," \
              "primary key(CharID)" \
              "foreign key(CharLevel) references LevelsTable(LevelID)" \
              ")"
        self.execute_query(sql, ())

    def populate_table(self):
        """
        Populates the CharTable in the database.

        No required parameters.

        Returns
        -------
        None
        """
        # the characters in the correct order for populating the database table
        sounds = ['n', 'a', 'i', 'u', 'e', 'o', 'ka', 'ki', 'ku', 'ke', 'ko',
                  'sa', 'shi', 'su', 'se', 'so', 'ta', 'chi', 'tsu', 'te', 'to',
                  'na', 'ni', 'nu', 'ne', 'no', 'ha', 'hi', 'fu', 'he', 'ho', 'ma',
                  'mi', 'mu', 'me', 'mo', 'ya', 'yu', 'yo', 'ra', 'ri', 'ru', 're',
                  'ro', 'wa', 'wo']
        chars = "んあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわを"
        level = "1111112222233333444445555566666777778889999988"
        # populates the database table with each character and it's corresponding information
        for x in range(len(sounds)):
            sql = "INSERT INTO CharTable(CharSound, CharKana, CharLevel) values (?,?,?)"
            tup = (sounds[x], chars[x], int(level[x]))
            self.execute_query(sql, tup)

    def get_char_level(self, sound_id):
        """
        Gets the level of a specified character from the table.

        Parameters
        ----------
        sound_id: int
            The CharID of the character whose level is to be found.

        returns
        -------
        int
        """
        # gets the level of a specified character from the table, given it's sound
        sql = "SELECT CharLevel FROM CharTable WHERE CharID = '" + str(sound_id) + "'"
        level = self.execute_single_response(sql, ())[0]
        return level

    def get_level_chars(self, level):
        """
        Gets the list of characters that are a certain level.

        Parameters
        ----------
        level: int
            The level that the characters are to be selected from

        Returns
        -------
        list[tuple[str, str]]
        """
        sql = "SELECT CharSound, CharKana FROM CharTable WHERE CharLevel = '" + str(level) + "'"
        characters = self.execute_multiple_responses(sql, ())
        return characters

    def find_char(self, num):
        """
        Gets the sound and kana of a character from its CharID

        Parameters
        ----------
        num: int
            The CharID of the character to be selected.

        Returns
        -------
        tuple[str, str]
        """
        sql = "SELECT CharSound, CharKana FROM CharTable WHERE CharID = " + str(num)
        returned = self.execute_single_response(sql, ())
        return returned

    def select_some(self, number, userid):
        """
        Selects a specified number of characters from the characters that a user has learned.

        Parameters
        ----------
        number: int
            The number of characters to be selected.
        userid: int
            The UserID of the user to select the characters for.

        Returns
        -------
        List[tuple[str, str]]
        """
        to_return = []
        done = []
        allowed = self.get_allowed_chars(userid)
        while len(done) < number:
            # selects a random CharID
            rand = random.randint(1, 46)
            # if the user has learned that character
            if rand in allowed:
                # if the character hasn't already been selected
                if rand not in done:
                    # adds the charID to the list of selected values
                    done.append(rand)
                    # get the sound and kana related to the selected CharID
                    sql = "SELECT CharSound, CharKana FROM CharTable WHERE CharID = '" + str(rand) + "'"
                    result = self.execute_single_response(sql, ())
                    # adds the tuple to the values to return
                    to_return.append(result)
        return to_return


class GameTable(FriendsTable):
    """
    GameTable Class.

    Inherits from superclass FriendsTable

    Deals with data/SQL Queries related to the GameTable.

    Methods
    -------
    create_table()
        Creates the GameTable table in the database.

    check_active_games()
        Checks that all not-full games were created <5 mins ago

    game_active(game_id: int)
        Checks whether a specified game is active.

    new_game_row(private: bool, g_type: str)
        Inserts a new record to GameTable to create a new game.

    deactivate_game(room: int)
        Deactivates a specified game in the GameTable

    make_full(game_id: int)
        Makes a specified game full so tht other users can't join.

    game_available(game_id)
        Checks whether a game is available to a user.
    """

    def __init__(self):
        super().__init__()
        pass

    def create_table(self):
        """
        Creates the GameTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        self.drop_table('GameTable')
        sql = "CREATE TABLE IF NOT EXISTS GameTable(" \
              "GameID INTEGER," \
              "GameType TEXT," \
              "Full BOOLEAN," \
              "Active BOOLEAN," \
              "Private BOOLEAN," \
              "TotalRounds INTEGER," \
              "Created INTEGER," \
              "primary key(GameID)" \
              ")"
        self.execute_query(sql, ())

    def check_active_games(self):
        """
        Checks that all not-full games were created <5 mins ago

        Deactivates the game if they were created before then.

        No required parameters.

        Returns
        -------
        None
        """
        # if no one has joined the game within 5 minutes, deactivate the game
        time_now = round(time.time())
        # five minutes ago
        five_mins = time_now - 300
        sql = "UPDATE GameTable SET Active = False WHERE Created < '" + str(five_mins) + "' AND Full = False"
        self.execute_query(sql, ())

    def game_active(self, game_id):
        """
        Checks whether a specified game is active.

        Parameters
        ----------
        game_id: int
            The GameID of the game to check.

        Returns
        -------
        bool
        """
        sql = "SELECT Active FROM GameTable WHERE GameID = '" + str(game_id) + "'"
        active = self.execute_single_response(sql, ())
        return active[0]

    def new_game_row(self, private, g_type):
        """
        Inserts a new record to GameTable to create a new game.

        Returns the ID of the new record created.

        Parameters
        ----------
        private: bool
            Whether the gae to be created is public or private.

        g_type: str
            The game type (e.g. "drawing")

        Returns
        -------
        int
        """
        sql = "INSERT INTO GameTable(GameType, Full, Active, Private, TotalRounds, Created) VALUES (?,?,?,?,?,?)"
        # the required values to insert a new row
        tup = (g_type, False, True, private, 0, round(time.time()))
        game_id = self.execute_return_id(sql, tup)
        return game_id

    def deactivate_game(self, room):
        """
        Deactivates a specified game in the GameTable

        Parameters
        ----------
        room: int
            The GameID of the game to be deactivated.

        Returns
        -------
        None
        """
        sql = "UPDATE GameTable SET Active = False WHERE GameID = '" + str(room) + "'"
        self.execute_query(sql, ())

    def make_full(self, game_id):
        """
        Makes a specified game full so tht other users can't join.

        Parameters
        ----------
        game_id: int
            The GameID of the game to make full

        Returns
        -------
        None
        """
        sql = "UPDATE GameTable SET Full = ? WHERE GameID = ?"
        tup = (True, game_id)
        self.execute_query(sql, tup)

    def game_available(self, game_id):
        """
        Checks whether a game is available to a user.

        determines whether a game that a user tries to access is still available
        (since the page loaded, someone else could have taken the spot)

        Parameters
        ----------
        game_id: int
            The GameID of the game to check

        Returns
        -------
        bool
        """
        sql = "SELECT * FROM GameTable WHERE GameID = ? AND Full = ?"
        tup = (game_id, False)
        returned = self.execute_single_response(sql, tup)
        if returned:
            return True
        else:
            return False


class UserPlayingTable(UserTable):
    """
    UserPlayingTable class.

    Inherits from superclass UserTable

    Methods
    -------
    create_table()
        Creates the UserPlayingTable table in the database.

    get_rounds(userid: int)
        Returns the total number of rounds that the user has played
        on the drawing game.

    get_streak(userid: int)
        Returns the user's current streak

    streak(user: int)
        Checks whether the user' streak should be incremented/ reset to 0.

    add_playing_points(userid: int, points: int)
        Adds a new record to the UserPlayingTable to show that the user has earned more points.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the UserPlayingTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS UserPlayingTable(" \
              "PlayingID INTEGER," \
              "UserID INTEGER," \
              "PointsEarned INTEGER," \
              "DateEarned INTEGER," \
              "primary key(PlayingID)" \
              "foreign key(UserID) references UserTable(UserID)" \
              ")"
        self.execute_query(sql, ())

    def get_rounds(self, userid):
        """
        Returns the total number of rounds that the user has completed of the drawing game.

        Parameters
        ----------
        userid: int
            The UserID of the user to check the rounds of.

        Returns
        -------
        int
        """
        sql = "SELECT * FROM UserPlayingTable WHERE UserID = '" + str(userid) + "'"
        result = self.execute_multiple_responses(sql, ())
        return len(result)

    def get_streak(self, userid):
        """
        Returns the user's current streak

        Parameters
        ----------
        userid: int
            The UserID of the user to get the streak of.

        Returns
        -------
        int
        """
        self.streak(userid)
        sql = "SELECT UserStreak FROM UserTable WHERE UserID = '" + str(userid) + "'"
        result = self.execute_single_response(sql, ())[0]
        return result

    def streak(self, user):
        """
        Checks whether the user' streak should be incremented/ reset to 0.

        Sees if the user has earned at least 40 points in the last 24 hours.

        Parameters
        ----------
        user: int
            The UserID of the user to check the streak of.

        Returns
        -------
        int
        """
        sql = "SELECT DateEarned FROM UserPlayingTable WHERE UserID = '" + str(user) + "' LIMIT 1"
        earliest = self.execute_single_response(sql, ())
        try:
            # the first datetime that the user earned points
            earliest = earliest[0]
            streak = 0
            now = round(time.time())
            # until the value of earliest reaches now.
            while earliest < int(now):
                # select all of the points earned in a 24 hour period
                sql = "SELECT PointsEarned FROM UserPlayingTable WHERE UserID = '" + str(
                    user) + "' AND DateEarned BETWEEN '" + str(earliest) + "' AND '" + str(earliest + 86400) + "'"
                results = self.execute_multiple_responses(sql, ())
                # adds up the points to see whether there are more than 40, and if not, the streak is set to 0
                total = 0
                for result in results:
                    total += result[0]
                if total < 40:
                    streak = 0
                else:
                    streak += 1
                # increases 'earliest' by 86400 seconds (one day)
                earliest += 86400
            # sets the new streak
            sql = "UPDATE UserTable SET UserStreak = '" + str(streak) + "' WHERE UserID = '" + str(user) + "'"
            self.execute_query(sql, ())
        except:
            # if the user has never earned any points, set their streak to 0.
            streak = 0
            sql = "UPDATE UserTable SET UserStreak = '" + str(streak) + "' WHERE UserID = '" + str(user) + "'"
            self.execute_query(sql, ())

    def add_playing_points(self, userid, points):
        """
        Adds a new record to the UserPlayingTable to show that the user has earned more points.

        Parameters
        ----------
        userid: int
            The UserID of the user who has earned the points
        points: int
            The number of points that the user has earned.

        Returns
        -------
        None
        """
        # adds a record to the table that records the points that the user earned in a turn
        sql = "INSERT INTO UserPlayingTable(UserID, PointsEarned, DateEarned) VALUES (?,?,?)"
        tup = (userid, points, int(time.time()))
        self.execute_query(sql, tup)
        # adds the points to the user's total points too
        self.add_total_points(userid, points)
        self.add_total_points(userid, points)


class GameUserTable(GameTable, UserTable):
    """
    GameUserTable class

    Inherits from superclasses GameTable and UserTable.

    Deals with data and SQL queries related to the GameUserTable in the database.

    Methods
    -------
    create_table()
        Creates the GameUserTable in the database.

    user_allowed(game_id: int, user: int)
        Checks whether the user is a member of the game.

    others_in_room(game_id: int, user: int)
        Gets the ID and username of the other user that is in the game.
        (or returns none)

    room_creator(game_id: int)
        Gets the UserID of the user who created the game.

    create_new_game(userID: int, private: bool, g_type: str)
        Creates a new game in the GameTable and GameUserTable.

    new_game_user(userID: int, game_id: int)
        Adds the user to the game.

    get_available_private_games(user: int)
        Returns a list of private games that the user can join.

    get_available_public_games(user: int)
        Returns a list of public games that the user can join.
    """

    def __init__(self):
        super().__init__()
        pass

    def create_table(self):
        """
        Creates the GameUserTable table in the database.

        No required parameters.

        returns
        -------
        None
        """
        self.drop_table('GameUserTable')
        sql = "CREATE TABLE IF NOT EXISTS GameUserTable(" \
              "GameUserID INTEGER," \
              "GameID INTEGER," \
              "PlayerID INTEGER," \
              "Points INTEGER," \
              "Correct INTEGER," \
              "primary key(GameUserID)" \
              "foreign key(PlayerID) references UserTable(UserID)" \
              "foreign key(GameID) references GameTable(GameID)" \
              ")"
        self.execute_query(sql, ())

    def user_allowed(self, game_id, user):
        """
        Checks whether the user is a member of the game.

        Parameters
        ----------
        game_id: int
            The GameID of the game to check for the user's membership
        user:
        :return:
        """
        sql = "SELECT * FROM GameUserTable WHERE GameID = ? AND PlayerID = ?"
        tup = (game_id, user)
        result = self.execute_single_response(sql, tup)
        # if the user is not a member of the game (if they directly try to get to the room)
        if result is None:
            return False
        else:
            return True

    def others_in_room(self, game_id, user):
        """
        Gets the ID and username of the other user that is in the game.
        (or returns none)

        Parameters
        ----------
        game_id: int
            The GameID of the game to select the user from.
        user: int
            The UserID of the user (excludes this from results)

        Returns
        -------
        tuple[int, str] or None
        """
        sql = "SELECT PlayerID FROM GameUserTable WHERE GameID = " + str(game_id) + " AND PlayerID != " + str(user)
        tmp = self.execute_single_response(sql, ())
        if tmp:
            found = self.find_username(tmp[0])
            found_tup = (tmp[0], found)
            # returns the (UserID, Username) of the other user in the room
            return found_tup
        else:
            return None

    def room_creator(self, game_id):
        """
        Gets the UserID of the user who created the game.

        Parameters
        ----------
        game_id: int
            The GameID for the game.

        returns
        -------
        int
        """
        sql = "SELECT PlayerID FROM GameUserTable WHERE GameID = " + str(game_id)
        found = self.execute_single_response(sql, ())[0]
        return found

    def create_new_game(self, userID, private, g_type):
        """
        Creates a new game in the GameTable and GameUserTable

        Parameters
        ----------
        userID: int
            The UserID of the user that created the new game

        private: bool
            Whether the game is just for friends or not.

        g_type: str
            The type of game that it is (e.g. "drawing")

        Returns
        -------
        int
        """
        game_id = self.new_game_row(private, g_type)
        self.new_game_user(userID, game_id)
        return game_id

    def new_game_user(self, userID, game_id):
        """
        Adds the user to the game.

        Parameters
        ----------
        userID: int
            The UserID of the user who is being added to the game.
        game_id: int
            The GameID of the game that the user is being added to.

        Returns
        -------
        None
        """
        # if the user is not already a member of the game
        if not self.user_allowed(userID, game_id):
            sql = "INSERT INTO GameUserTable(GameID, PlayerID, Points, Correct) VALUES (?, ?, ?, ?)"
            tup = (game_id, userID, 0, 0)
            self.execute_query(sql, tup)

    def get_available_private_games(self, user):
        """
        Returns a list of private games that the user can join.

        Up to 10 active but not full private games (created by their friends)
        are returned for the user to choose from.

        Parameters
        ----------
        user: int
            The UserID of the user looking for a game.

        Returns
        -------
        list[tuple[int, int, str]]
        """
        # get all of the user's that they are friends with
        friends = self.get_user_friends(user, True)
        # if the user has at least one friend
        if friends != []:
            try:
                # select the GameIDs where the game is made by on of the user's friend
                sql = "SELECT GameID FROM GameUserTable WHERE PlayerID IN '" + str(tuple(friends)) + "'"
                found = self.execute_multiple_responses(sql, ())
            except Exception as e:
                # if the user only has one friend, select GameIDs where the game is made by their friend
                friend = friends[0]
                sql = "SELECT GameID FROM GameUserTable WHERE PlayerID = '" + str(friend) + "'"
                found = self.execute_multiple_responses(sql, ())
            tmp = []
            # make tmp the list of GameIDs
            for item in found:
                tmp.append(item[0])
            found = tmp
            try:
                if len(found) > 1:
                    # if more than 1 GameID is found, get up to 10 games where the user is allowed to join
                    sql = "SELECT * FROM GameTable WHERE GameID IN " + str(tuple(found)) + \
                          " AND Full = False AND Active = True AND Private = True AND GameType = 'drawing' " \
                          "ORDER BY GameID LIMIT 10"
                    found_games = self.execute_multiple_responses(sql, ())
                else:
                    # if only one GameID is found, see whether that game is available
                    sql = "SELECT * FROM GameTable WHERE GameID = " + str(found[0]) + \
                          " AND Full = False AND Active = True AND Private = True AND GameType = 'drawing'"
                    found_games = self.execute_multiple_responses(sql, ())
            except Exception as e:
                # if no GameIDs were found
                found_games = []
        else:
            # return no games if the user doesn't have any friends
            found_games = []
        users = []
        usernames = []
        game_id = []
        for game in found_games:
            # if the user isn't already in the game
            if not self.user_allowed(game[0], user):
                # for each of the returned games, find the user who made the game
                user_id = self.room_creator(game[0])
                game_id.append(game[0])
                users.append(user_id)
                usernames.append(self.find_username(user_id))
        lists = []
        # for each game found, add the tuple of (GameID, UserID of creator, Username of creator)
        for x in range(len(users)):
            tup = (game_id[x], users[x], usernames[x])
            lists.append(tup)
        # a list of tuples that contain the userid, username and room id for each of the rooms
        # that fit the criteria
        return lists

    def get_available_public_games(self, user):
        """
        Returns a list of public games that the user can join.

        Up to 10 active but not full public games are returned for the user to choose from.

        Parameters
        ----------
        user: int
            The UserID of the user looking for a game.

        Returns
        -------
        list[tuple[int, int, str]]
        """
        # find all of the available public games.
        sql = "SELECT * FROM GameTable WHERE Full = 0 AND Active = 1 " \
              "AND Private = 0 AND GameType = 'drawing' ORDER BY GameID LIMIT 10"
        found = self.execute_multiple_responses(sql, ())
        users = []
        usernames = []
        game_id = []
        for game in found:
            # if the user si not already in the game
            if not self.user_allowed(game[0], user):
                # for each of the returned games, find the user who made the game
                user_id = self.room_creator(game[0])
                game_id.append(game[0])
                users.append(user_id)
                usernames.append(self.find_username(user_id))
        lists = []
        # for each game found, add the tuple of (GameID, UserID of creator, Username of creator)
        for x in range(len(users)):
            tup = (game_id[x], users[x], usernames[x])
            lists.append(tup)
        # a list of tuples that contain the userid, username and room id for each of the rooms
        # that fit the criteria
        return lists


class ChatroomTable(FriendsTable):
    """
    ChatroomTable class

    Inherits from superclass FriendsTable

    Deals with data/SQL queries related to the ChatroomTable.

    Methods
    -------
    create_table()
        Creates the ChatroomTable in the database.

    get_room(userA: int, userB: int)
        Finds the ChatID of the chatroom that two users are in together.

    is_allowed(userid: int, room: int)
        Checks whether a user is a member of a chatroom.

    get_users(room: int)
        Selects the UserIDs of the two users in a chatroom.

    new_chat(userA: int, userB: int)
        Creates a new chatroom between two users.

    check_chat(chatid: int, userid: int)
        Checks whether a user is a member of a specified chat.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the ChatroomTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS ChatroomTable(" \
              "ChatID INTEGER," \
              "UserA INTEGER," \
              "UserB INTEGER," \
              "primary key(ChatID)" \
              "foreign key(UserA) references UserTable(UserID)" \
              "foreign key(UserB) references UserTable(UserID)" \
              ")"
        self.execute_query(sql, ())

    def get_room(self, userA, userB):
        """
        Finds the ChatID of the chatroom that two users are in together.

        Returns False if no chatroom is found, otherwise returns the ChatID.

        Parameters
        ----------
        userA: int
            One of the users in the chatroom
        userB: int
            The other user in the chatroom

        Returns
        -------
        int or False
        """
        sql = "SELECT ChatID FROM ChatroomTable WHERE (UserA = '" + str(userA) + \
              "' AND UserB = '" + str(userB) + "') OR (UserA = '" + str(userB) + \
              "' AND UserB = '" + str(userA) + "')"
        result = self.execute_single_response(sql, ())
        if not result:
            return False
        return result[0]

    def is_allowed(self, userid, room):
        """
        Checks whether a user is a member of a chatroom.

        Parameters
        ----------
        userid: int
            The UserID of the user being checked.
        room: int
            The ChatID of the chatroom that teh user should be in.

        Returns
        -------
        bool
        """
        sql = "SELECT * FROM ChatroomTable WHERE ChatID = '" + str(room) + \
              "' AND (UserA = '" + str(userid) + "' OR UserB = '" + str(userid) + "')"
        result = self.execute_multiple_responses(sql, ())
        if not result:
            return False
        return True

    def get_users(self, room):
        """
        Selects the UserIDs of the two users in a chatroom.

        Parameters
        ----------
        room: int
            The ChatID of the chatroom to find the users for.

        Returns
        -------
        tuple[int, int]
        """
        sql = "SELECT UserA, UserB FROM ChatroomTable WHERE ChatID = '" + str(room) + "'"
        return self.execute_single_response(sql, ())

    def new_chat(self, userA, userB):
        """
        Creates a new chatroom between two users.

        Parameters
        ----------
        userA: int
            The UserID of one of the users to be in the new chatroom.
        userB: int
            The UserID of the other user to be in the new chatroom.

        Returns
        -------
        int
        """
        allowed = self.check_friends(userB, userA)
        if not allowed:
            return False
        sql = "INSERT INTO ChatroomTable(UserA, UserB) VALUES (?,?)"
        tup = (userA, userB)
        return self.execute_return_id(sql, tup)

    def check_chat(self, chatid, userid):
        """
        Checks whether a user is a member of a specified chat.

        Parameters
        ----------
        chatid: int
            The ChatID of the chatroom to check.
        userid: int
            The UserID of the user.

        Returns
        -------
        bool
        """
        sql = "SELECT * FROM ChatroomTable WHERE ChatID = '" + str(chatid) + "' AND (UserA = '" \
              + str(userid) + "' OR UserB = '" + str(userid) + "')"
        result = self.execute_single_response(sql, ())
        if not result:
            return False
        return True


class ChatMessageTable(ChatroomTable):
    """
    ChatMessageTable class

    Inherits from superclass ChatroomTable.

    Methods
    -------
    create_table()
        Creates the ChatMessageTable table in the database.

    get_messages(userFrom: int, userTo: int)
        Gets all of the messages from and to a specific user.

    add_messages(sender: int, recipient: int, room: int, message: str)
        Adds a new record to the table, with a new message between two users.
    """

    def __init__(self):
        super().__init__()

    def create_table(self):
        """
        Creates the ChatMessageTable in the database.

        No required parameters.

        returns
        -------
        None
        """
        sql = "CREATE TABLE IF NOT EXISTS ChatMessageTable(" \
              "MessageID INTEGER," \
              "MessageTo INTEGER," \
              "MessageFrom INTEGER," \
              "ChatID INTEGER," \
              "Message TEXT," \
              "DateTime INTEGER," \
              "primary key(MessageID)," \
              "foreign key(MessageTo) references UserTable(UserID)," \
              "foreign key(MessageFrom) references UserTable(UserID)," \
              "foreign key(ChatID) references ChatroomTable(ChatID)" \
              ")"
        self.execute_query(sql, ())

    def get_messages(self, userFrom, userTo):
        """
        Gets all of the messages to and from a specific user.

        Parameters
        ----------
        userFrom: int
            The UserID of the user who sent the messages
        userTo: int
            The UserID of the user who received the messages

        Returns
        -------
        list[tuple[str, int, int]]
        """
        sql = "SELECT Message, DateTime, MessageFrom FROM ChatMessageTable WHERE MessageFrom = '" + str(userFrom) + \
              "' AND MessageTo = '" + str(userTo) + "'"
        return self.execute_multiple_responses(sql, ())

    def add_messages(self, sender, recipient, room, message):
        """
        Adds a new record to the table with a message between two users.

        Returns the current UNIX time.

        Parameters
        ----------
        sender: int
            The UserID of the user who sent the message.
        recipient: int
            The UserID of the user who received the message.
        room: int
            The ChatID of the room that the message was sent in.
        message: str
            The message that was sent

        Returns
        -------
        int
        """
        sql = "INSERT INTO ChatMessageTable(MessageTo, MessageFrom, ChatID, Message, DateTime) VALUES (?,?,?,?,?)"
        time_now = round(time.time())
        tup = (recipient, sender, room, message, time_now)
        self.execute_query(sql, tup)
        return time_now


if __name__ == "__main__":
    pass
