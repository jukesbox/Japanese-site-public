""" Japanese Flask Application - main_app.py

This file is used to run the application on Flask, allowing a user to access the site.

This script is not imported in other files within this system, as it is the main file to be run.

The packages that should be installed to be able to run this file are:
flask, os, datetime, json, random, flask_socketio

The files within the system that must also be available are:
databases.py, image_processing.py and sending_emails.py
"""

from flask import Flask, render_template, redirect, request, session, url_for, flash
import os
from databases import *
from datetime import timedelta
import json
import image_processing
from random import choice, shuffle
from flask_socketio import SocketIO, emit, join_room
from sending_emails import *
import dictionary

# creates an instance of each of the database tables for easier access than defining it each time
user_table = UserTable()
user_playing_table = UserPlayingTable()
friends_table = FriendsTable()
email_setting_table = EmailSettingTable()
user_awards_table = UserAwardsTable()
awards_table = AwardsTable()
user_levels_table = UserLevelsTable()
levels_table = LevelsTable()
char_table = CharTable()
game_table = GameTable()
game_user_table = GameUserTable()
dict_queries = dictionary.Entry()
chatroom_table = ChatroomTable()
chat_message_table = ChatMessageTable()
# There are 3 additional tables in the database, but none need to be accessed from within this file

# creates an instance of the flask class
app = Flask(__name__)
# generates a random secret key that is needed for sessions.
app.config['SECRET_KEY'] = os.urandom(24)
# sets the length of the session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
# instance of the class SocketIO to deal with socket events.
socketio = SocketIO(app)
login_data_dict = {}
current_room = 0


# when a user joins a room in either multiplayer match or a chat room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)


@socketio.on('message')
def handle_message(data):
    """
    This function handles any socket message events that are sent.

    There are many different 'EventType's that can be sent in the message data, for different actions to be performed
    I will treat each if/elif statement within this function as an individual 'function'
    with regards to written documentation.

    parameters
    ----------
    data: dict

    Returns
    -------
    None
    """
    global login_data_dict
    global current_room
    # this is when the user has submitted their drawing from a multiplayer game
    if data['EventType'] == "image_submit":
        # loads the json object containing the dictionary with the image data for each stroke.
        img_data = json.loads(data['image_data'])
        # the current stroke number
        current_num = data['sound_num']
        # the points that will be added if the user is correct
        points = char_table.get_char_level(current_num) * 2
        # the username of the user
        username = session['username']
        sending = ""
        for stroke in img_data:
            sending = img_data[stroke]
        # sends the image (of the final stroke) to the room, associating it with the user's ID
        send = {"UserID": data['UserID'], "image": sending}
        emit('recv_img', send, room=data['room'], include_self=False)
        # passes the image data to the neural network and
        correct, incorrect, result, mistaken_for = image_processing.process_all(img_data, username, current_num, "game")
        # if every stroke is correct, add the points to the user's total in the database
        if result:
            user_playing_table.add_playing_points(data['UserID'], points)
        # send the results to the other user in the game
        sending = {"result": result, "UserID": data['UserID'], "points": points}
        emit('result_img', sending, room=data['room'], include_self=True)

    # this is when the user is waiting for another user to join the multiplayer game
    elif data['EventType'] == "waiting":
        room = data['room']
        current_room = room
        user_id = data['UserID']
        # returned will be None or (user_id, username)
        # (there is no other user in the game / there is another user in the game)
        returned = game_user_table.others_in_room(room, user_id)
        if not returned:
            # tells the user in the room (a certain game) that they are still waiting for another user.
            game_table.check_active_games()
            active = game_table.game_active(room)
            if active:
                emit('wait', room=room)
            else:
                login_data_dict['flash'] = 'Nobody joined!'
                emit('move_user', {'url': url_for('select_game')})
        else:
            # sends the information about the other user to the room
            data_send = {"UserID": returned[0], "username": returned[1]}
            emit('other_connection', data_send)
            # finds the characters that each of the users has learned
            options_user1 = user_levels_table.get_allowed_chars(session['UserID'])
            options_user2 = user_levels_table.get_allowed_chars(returned[0])
            # finds the characters that both of them have learned
            options_user2 = set(options_user2)
            options = list(options_user2.intersection(options_user1))
            # picks a random character from the list.
            num = choice(options)
            # returns the sound and kana character that correspond with the ID selected by the random number
            sound, kana = char_table.find_char(num)
            data = {"kana": kana, "sound": sound, "sound_num": num}
            emit('recv_challenge', data, room=room)

    elif data['EventType'] == "connected":
        # sends the room id and user_id to be saved as variables within the JS.
        data_sent = {"room": session['room'], "UserID": session['UserID']}
        emit('info', data_sent)

    elif data['EventType'] == "request_info":
        # sends the user's userid so that it can  be used in various js functions
        emit('info', {"UserID": session['UserID']})

    # this is called when a user (in single player mode or creating training data)
    elif data['EventType'] == "ask_for_challenge":
        # gets the characters that the user has learned
        options = user_levels_table.get_allowed_chars(session['UserID'])
        # picks a pseudo-random character from the list
        num = choice(options)
        # returns the sound and kana character that correspond with the ID selected by the random number
        sound, kana = char_table.find_char(num)
        data = {"kana": kana, "sound": sound, "sound_num": num}
        # sends the challenge to the user
        emit('recv_challenge', data)

    # when a user in single player mode submits a drawing
    elif data['EventType'] == "image_submit_single":
        draw = json.loads(data['image_data'])
        current_num = data['sound_num']
        # the number of points available if they answer correctly
        points = char_table.get_char_level(current_num) * 2
        username = session['username']
        # process_all parameters: (list_of_strokes, username, char_num, submission_type)
        correct, incorrect, result, mistaken_for = image_processing.process_all(draw, username, current_num, "game")
        mistakes = []
        for item in mistaken_for:
            mistakes.append(char_table.find_char(item)[0])
        # if the user was correct, the points are added to the user's total in the database
        if result:
            user_playing_table.add_playing_points(session['UserID'], points)
            # sends the result and the number of points earned to the user,
            # so they are added to the total on screen
            data = {"result": result, "points": points}
        else:
            sound, kana = char_table.find_char(data['sound_num'])
            data = {"result": result, "points": points, "mistaken_for": mistakes, "incorrect_strokes": incorrect,
                    "char_animation": url_for('static',
                                              filename='character_images/animations/animation-' + sound + '.gif')}
        emit('result_single', data)

    # when the user submits a drawing from the training data page (this will be restricted)
    elif data["EventType"] == "image_submit_train":
        # list_of_strokes, username, char_num, current_sound, submission_type
        strokes = json.loads(data["image_data"])
        username = session["username"]
        char_num = data['sound_num']
        # processes the training data image and saves it to a csv to be used by the neural network
        image_processing.process_all(strokes, username, char_num, "train")

    # when the user accesses a profile (theirs or a friend's)
    elif data['EventType'] == "get_profile_data":
        try:
            # if the user is on another user's profile, their userid is used
            usernme = data['OtherUsername']
            user_id = user_table.find_id(usernme)
            # if the userid is not found (i.e. there is no user with that username)
            if user_id == 0:
                user_id = session['UserID']
        except:
            # if they are on their own profile
            # (or no such username exists), theirs is used
            user_id = session['UserID']
        # get the data for each of the elements that will be displayed on the user's progress screen
        streak = user_playing_table.get_streak(user_id)
        points = user_table.get_user_points(user_id)
        friends = friends_table.get_user_friends(user_id)
        friend_requests = friends_table.find_all_requested(user_id)
        awards = user_awards_table.get_user_awards(user_id)
        if session['UserID'] != user_id:
            new_awards = []
            for award in awards:
                award = award.replace("You", "They")
                new_awards.append(award)
            awards = new_awards
        characters = str(len(user_levels_table.get_allowed_chars(user_id))) + "/46"
        questions = str(user_playing_table.get_rounds(user_id))
        next_steps = "Complete Level " + str(user_table.get_user_level(user_id) + 1) + "!"
        # sends the user data to the user's profile page
        data = {"points": points, "streak": streak, "friends": friends, "friend_requests": friend_requests,
                "awards": awards, "characters": characters, "questions": questions, "next_steps": next_steps}
        emit('user_data', data)

    elif data['EventType'] == "user_ready":
        room = data['room']
        current_room = room
        # if both of the users are ready
        if data['both']:
            # finds the characters that each of the users have learned
            options_user1 = user_levels_table.get_allowed_chars(session['UserID'])
            options_user2 = user_levels_table.get_allowed_chars(data['OtherID'])
            # finds the common characters (ones that both of them know)
            options_user2 = set(options_user2)
            options = list(options_user2.intersection(options_user1))
            # selects a pseudo-random character from the list
            num = choice(options)
            # returns the sound and kana character that correspond with the ID selected by the random number
            sound, kana = char_table.find_char(num)
            data = {"kana": kana, "sound": sound, "sound_num": num}
            # sends the challenge to the room
            emit('recv_challenge', data, room=room)
        else:
            # if only one of the users are ready, then this is told to the other user's client,
            # so that it can be recorded as both when the other is ready.
            data = {"UserID": data['UserID']}
            emit('other_ready', data, room=room)

    # when a user attempts to login
    elif data['EventType'] == "login_data":
        # the errors that are found in the data submitted are added here,
        # so that these can be told to the user
        errors = []
        # validates whether the user has entered valid information
        if user_table.validate_login(data['username'], data['password']):
            # the session is set and the user is logged in'
            userid = user_table.find_id(data['username'])
            email = user_table.get_email(userid)
            # the info is added to the global dictionary variable and then set to
            # the session when the next page is reached, because the session is not retained otherwise
            login_data_dict['username'] = data['username']
            login_data_dict['UserID'] = userid
            login_data_dict['email'] = email
            # see whether the user has tried to access a different page
            # (they were redirected to the login page because they were not logged in)
            try:
                # if an argument needed to be passed for the url that the user tried to access
                if 'here_args' in login_data_dict:
                    # finds the correct url extension
                    url = url_for(login_data_dict['go_here'], parameter=login_data_dict['here_args'])
                    # removes the strings from the data, so the values (args especially) do not cause errors later
                    login_data_dict.pop('here_args')
                    login_data_dict.pop('go_here')
                else:
                    # if there were no arguments, then there are no parameters added
                    url = url_for(login_data_dict['go_here'])
                    login_data_dict.pop('go_here')
            except:
                # if the above code causes an error ('go_here' is not in login_data_dict)
                # then the automatic url to redirect to is the profile page
                url = url_for('profile')
            # sends the correct url so that the JS can move the window.
            data = {"url": url}
            emit("move_user", data)
        else:
            # if the username or password is incorrect, the error is set
            errors.append("Incorrect username or password")
            if (data['username'] == "") or (data['password'] == ""):
                errors.append("Fields cannot be blank!")
            data = {"errors": errors}
            # the errors are sent back to the user on the login page, and the user is not logged in
            emit("login_error", data)

    # if the user submits data to sign up to the website
    elif data['EventType'] == "sign_up_data":
        # any errors will be added to this list
        errors = []
        # if the email is not valid (there are other requirements for valid email addresses but these
        # are not necessary for the purpose of this form
        if "@" not in data['email']:
            # adds this error to the list
            errors.append('Email is invalid!')
        # check whether the username or email address is already in use
        result = user_table.validate_new_account((data['username'], data['email']))
        # if either of the values are already in use
        if "Username" in result:
            # adds this statement to the error that is shown to the user
            errors.append("Username already exists! Please try another!")
        # if the email is already in use
        if "Email" in result:
            # adds this statement to the error that is shown to the user
            errors.append("Email already in use! Please use another!")
        # if the password and confirm password fields do not match
        if data['password'] != data['c_password']:
            errors.append("Passwords must match!")
        # checks whether the user has entered a valid enough password
        decision, message = user_table.validate_password(data['password'])
        # for each of the errors raised when checking the password, these are added to the errors
        for mess in message:
            errors.append(mess)
        # if there are no errors, the details are assumed to be valid, and the
        # account is added to the database
        if errors == []:
            user_table.add_account(
                (data['username'], generate_password_hash(data['password']),
                 data['email'], False))
            # adds the user to the email settings table - with all values as false
            email_setting_table.new_row(user_table.find_id(data['username']))
            # sets the user's details within the signup dict (so that it can be added when redirected to profile)
            login_data_dict['UserID'] = user_table.find_id(data['username'])
            login_data_dict['username'] = data['username']
            login_data_dict['email'] = data['email']
            # moves the user to their profile
            emit('move_user', {"url": url_for('profile')})
        else:
            # if any errors were raised, these are returned to the signup page for the user to correct
            data = {"errors": errors}
            emit('signup_errors', data)

    # when the user tries to access their settings on the profile page
    elif data['EventType'] == "get_settings":
        # each of these return a boolean value, showing whether the user has
        # currently got these settings turned on
        info = email_setting_table.checked('EmailInfo', session['UserID'])
        remind = email_setting_table.checked('EmailReminders', session['UserID'])
        promo = email_setting_table.checked('EmailPromotion', session['UserID'])
        # these fields, along with the user's standard data are sent to the user to see on their profile page
        data = {"username": session['username'], "email": session['email'], "info": info, "remind": remind,
                "promo": promo}
        emit('current_settings', data)

    # when the user submits a change to their settings.
    elif data["EventType"] == "settings_change":
        # sets a list variable to hold any errors that are found when checking
        errors = []
        # if the username field has been changed
        if data['username'] != session['username']:
            # checks whether someone already has the username that they are trying to change it to
            exists = user_table.username_exists(data['username'])
            if exists:
                errors.append("This username already exists!")
        # if the email field has been changed
        if data['email'] != session['email']:
            # checks whether the email address is already used by someone
            exists = user_table.email_exists(data['email'])
            if exists:
                errors.append("This email address already exists!")
            if "@" not in data['email']:
                errors.append("Invalid email address")
        # checks whether the current password matches the one that is in the database
        valid = user_table.validate_login(session['username'], data['c_password'])
        if not valid:
            errors.append("Your current password is incorrect!")
        # checks the password that the user has entered
        decision, messages = user_table.validate_password(data['password'])
        for message in messages:
            errors.append(message)
        if errors != []:
            # if there are errors in the data that the user has entered
            emit('change_errors', {"errors": errors})
        else:
            # if all of the details are valid, then the details are changed in the database
            user_table.update_data((data['username'], generate_password_hash(data['password']),
                                   data['email'], session['UserID']))
            email_setting_table.change_settings([data['reminder'], data['info'], data['promo']], session['UserID'])
            # the current session is updated to reflect the updated details
            login_data_dict['username'] = data['username']
            login_data_dict['UserID'] = session['UserID']
            login_data_dict['email'] = data['email']
            # session['username'] = data['username']
            # session['email'] = data['email']
            # the user is redirected to their profile if all details are correct
            emit('move_user', {"url": url_for('profile')})

    # when the user searches for someone on the friends page
    elif data['EventType'] == 'look_for':
        username = data['name']
        # finds all users that have usernames that contain the searched term
        people = friends_table.get_similar_users(username, session['UserID'])
        # sends the people to the user
        emit('found_users', {'people': people})

    # when the user clicks the 'request' user button next to a user's name
    elif data['EventType'] == 'request_user':
        # adds the request to the database table
        friends_table.add_request(session['UserID'], data['UserID'])

    # if the user tries to view the profile of another user (through the link on the friends page)
    elif data['EventType'] == 'view_other_profile':
        # finds the url for the user's profile
        url = url_for('other_profile', parameter=data['OtherUsername'])
        # emits the socket event to move the user to the user's profile
        emit('move_user', {"url": url})

    # when the user clicks accept to a user's friend request
    elif data['EventType'] == 'accept':
        # accepts the request in the database
        friends_table.accept_request(data['UserID'], session['UserID'])

    # when the user clicks 'reject' next to a friend request
    elif data['EventType'] == 'reject':
        # removes the request from the database
        friends_table.reject_request(data['UserID'], session['UserID'])

    # when the user is on the homepage, the top 10 users (by points) should be found
    elif data['EventType'] == 'get_leaders':
        # finds the top users and sends them to the page
        emit('leaderboard', {"leaders": user_table.leaderboard()})

    # when the user starts a matching game
    elif data['EventType'] == 'match_connect':
        # selects 5 different characters
        items = char_table.select_some(5, session['UserID'])
        send_list = []
        for item in items:
            for char in item:
                # char is either the sound or the hiragana
                # item[0] is always the sound
                # makes it into a set of 10, where each character has two sets: (sound, sound) and (kana, sound)
                send_list.append([char, item[0]])
        # shuffles the list so it is in a random order
        shuffle(send_list)
        emit('character_list', {'list': send_list})

    # when the user has completed a screen of matching cards
    elif data['EventType'] == "done_matches":
        # add 10 points for the user
        user_playing_table.add_playing_points(session['UserID'], 10)

    elif data['EventType'] == 'get_level_data':
        # selects all of the data from the database about the level
        level_get = data['LevelNum']
        # gets the text and the number of points that are stored about the level in the database
        stuff = levels_table.get_level_stuff(level_get)
        # gets the characters that are going to be learned in the level
        chars = char_table.get_level_chars(level_get)
        sound = []
        kana = []
        for item in chars:
            sound.append(item[0])
            kana.append(item[1])
        char_list = []
        audios = []
        animations = []
        for x in range(len(sound)):
            char_list.append([sound[x], kana[x]])
            # gets the audio file associated with the sound
            audios.append(url_for('static', filename='character_images/audios/audio-' + sound[x] + '.mp3'))
            # gets the animation (gif) associated with the sound
            animations.append(url_for('static', filename='character_images/animations/animation-' + sound[x] + '.gif'))
        text, points = stuff
        # splits the text in to the paragraphs (indicated in the database by //)
        text_paras = text.split("//")
        # sends the data to the user to be displayed in the levels game.
        data = {'points': points, 'paragraphs': text_paras, 'char_list': char_list,
                'char_audios': audios, 'animations': animations}
        emit('level_data', data)

    elif data['EventType'] == 'finished_level':
        # when the user completes a level, this is added to the data held about the user in the database
        level_completed = data['LevelNum']
        user_levels_table.finish_level(session['UserID'], level_completed)
        # moves the user to the page where levels are selected
        emit('move_user', {'url': url_for("learn")})

    elif data['EventType'] == "forgot_password":
        # if the user has forgotten their password, a pseudo randomly selected pin is
        # associated to the user in the database, and the one time pin is sent to the user via the email
        # associated with the user
        pin, email = user_table.set_otp(data['username'])
        send_pin(pin, email)

    elif data['EventType'] == "login_otp":
        # when the user tries to log in with the pin
        # validates the pin/username entered
        success = user_table.login_otp(data['username'], data['otp'])
        # if the data is valid
        if success:
            # sets the pin to '0' so that it cannot be used again
            userid, email = user_table.clear_otp(data['username'])
            # adds the user data to the data dictionary, to be added to the session when the user reaches the next page
            login_data_dict['username'] = data['username']
            login_data_dict['UserID'] = userid
            login_data_dict['email'] = email
            # if the user went directly to the login page without accessing login restricted pages
            # the user is redirected to their settings page
            login_data_dict['change_password'] = "change"
            url = url_for('change_password')
            # the user is moved to their desired page
            emit('move_user', {'url': url})
        else:
            # if the data entered was not valid, then the error is returned to the user and they can't login
            emit('login_error', {'errors': ['Incorrect PIN or username']})

    elif data['EventType'] == 'search_dictionary':
        search = data['search_term']
        # gets all of the words that match with the searched term 'search'
        all_results = dict_queries.get_from_query(search)
        emit('dictionary_results', {'results': all_results})

    elif data['EventType'] == "who_are_we":
        # gets the users in the current room
        users = chatroom_table.get_users(session['room'])
        room = session['room']
        for user in users:
            if user != session['UserID']:
                other_user = user
        emit('you_are', {'you': session['UserID'], 'them': other_user, 'room': room})

    elif data['EventType'] == "send_message":
        message = data['mess']
        to_ = data['MessageTo']
        from_ = data['MessageFrom']
        room = session['room']
        time_now = chat_message_table.add_messages(from_, to_, room, message)
        emit('new_message', {'message': [message, time_now, from_]}, room=room)

    elif data['EventType'] == "get_messages":
        # (message, datetime, messageFrom)
        your_messages = chat_message_table.get_messages(session['UserID'], data['Other'])
        other_messages = chat_message_table.get_messages(data['Other'], session['UserID'])
        data = {'yours': your_messages, 'others': other_messages}
        emit('recv_previous', data)

    elif data['EventType'] == "check_allowed":
        chars = user_levels_table.get_allowed_chars(session['UserID'])
        if len(chars) == 0:
            emit("allowed_check", {'allowed': False})
        else:
            emit("allowed_check", {'allowed': True})

    elif data['EventType'] == "leave_room":
        game_table.deactivate_game(data['room'])
        login_data_dict['flash'] = 'A user left the game!'
        emit('move_user', {"url": url_for('select_game')}, room=data['room'])

    elif data['EventType'] == "check_pword_change":
        print("LOGIN DATA DICT: ", login_data_dict)
        if 'change_password' not in login_data_dict:
            emit('move_user', {"url": url_for('profile')})
        login_data_dict.pop('change_password')

    elif data['EventType'] == "submit_change":
        valid, message = user_table.validate_password(data['password'])
        if valid:
            user_table.update_data((session['username'], generate_password_hash(data['password']), session['email'], session['UserID']))
            emit('move_user', {"url": url_for('profile')})
        else:
            emit('password_errors', {"errors": message})


def log():
    """
    This function sets the user's session without them having to log in.
    It is used during development to save time when testing features.

    No required parameters.

    Returns
    -------
    None
    """
    # find the browser that the user is using
    browse = request.user_agent.browser
    # if the user is not already logged in
    if 'username' not in session:
        # if the browser is chrome
        if browse == 'chrome':
            # logs the user in as japanese_learner
            session['username'] = 'japanese_learner'
            session['UserID'] = 1
            session['email'] = 'japan@email.com'
        else:
            # logs the user in as user2
            session['username'] = 'user2'
            session['UserID'] = 2
            session['email'] = 'user.2@email.com'


@app.errorhandler(404)
def page_not_found(e):
    # if the user tries to access a page that doesn't exist
    # depending on their login status, they are prompted to go back to the homepage or to their profile
    if 'username' in session:
        message = 'Go back to your profile'
        link = 'profile'
    else:
        message = 'Go back home'
        link = 'home'
    return render_template('404.html', message=message, link=link), 404


@app.route('/')
@app.route('/home')
def home():
    # the homepage
    return render_template('home.html')


@app.route('/login')
def login():
    # if the user has viewed this page/ clicked a link to here but they are logged in, go to the profile
    # log()
    if 'username' in session:
        return redirect(url_for('profile'))
    # renders the HTML template
    return render_template('login2.html')


# the URL extension is mapped to the function
@app.route('/logout')
def logout():
    # all values that are in the session object are
    # removed, so the user is logged out
    session.clear()
    # the logout page is shown
    return render_template('logout.html')


# maps the URL extension to the function and allows both GET and POST requests.
@app.route('/signup')
def signup():
    # log()
    # if the user is already logged in, they are redirected to the profile page
    if 'username' in session:
        return redirect(url_for('profile'))
    # renders the HTML template
    return render_template('signup2.html')


@app.route('/profile')
def profile():
    # this section of code is present in every app route that requires a user to be logged in
    # so it will only be commented here

    # allows the data dictionary to be read and edited
    global login_data_dict
    # log()
    # if the user's session thinks they are not logged in
    if 'username' not in session:
        # if the data dictionary has not got any login data (i.e. the user has not logged in)
        if 'username' not in login_data_dict:
            flash('You must login to view this page!')
            # redirects the user to the login page
            return redirect(url_for('login'))
        else:
            # if the user has just logged in
            # fills the session data with the data from the user's login
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    else:
        try:
            # if the user has just changed their details - the new username/email will be in the
            # login_data_dict, so this is changes without the user logging out and back in again
            session['username'] = login_data_dict['username']
            session['email'] = login_data_dict['email']
        except:
            pass
    return render_template('progress.html', username=session['username'])


@app.route('/profile/progress')
def your_progress():
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            # clears the data dictionary
            login_data_dict = {}
    # sends the user to their progress page
    return render_template('progress.html', username=session['username'])


@app.route('/profile/friends')
def friend():
    # when the user wants to see a list of their friends and requests
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'friend'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    return render_template('friends.html', username=session['username'])


@app.route('/profile/settings')
def settings():
    # when the user accesses their settings
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'settings'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    return render_template('settings.html', username=session['username'])


@app.route('/profile/change-password')
def change_password():
    # when the user has just logged in with an OTP
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            # redirects to profile after login if not logged in
            login_data_dict['go_here'] = 'profile'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            # clears most data from the login_data_dict - leaving 'change_password' if
            # it is there.
            for x in ['username', 'email', 'UserID', 'go_here', 'here_args']:
                try:
                    login_data_dict.pop(x)
                except:
                    pass
    # shows the correct HTML template to the user.
    return render_template('change_password.html', username=session['username'])


@app.route('/other-profile/<parameter>')
def other_profile(parameter):
    # parameter is the username for the profile the user is trying to access
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'other_profile'
            login_data_dict['here_args'] = parameter
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    # gets the userid for the username that has been passed in as the parameter
    userid = user_table.find_id(parameter)
    if userid == 0:
        return redirect(url_for('profile'))
    # if the user is friends with the  person whose profile they are trying to access...
    if friends_table.check_friends(userid, session['UserID']):
        # shows the user their profile
        return render_template('other_user_profile.html', username=parameter.upper())
    else:
        # tells the user that they are not friends with the user
        return render_template('not_friends.html', userid=userid)


@app.route('/dictionary')
def dictionary():
    # when the user accesses the dictionary
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'dictionary'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    return render_template('dictionary.html')


@app.route('/games')
def games():
    # when the user is yet to select which type of game to play
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'games'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    return render_template('games.html')


@app.route('/games/single/drawing')
def single_drawing():
    # when the  user plays a single player version of drawing
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'single_drawing'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    return render_template('drawing_single.html')


# maps the URL to the function and allows both GET and POST requests.
@app.route('/create-training')
def training_data():
    # when the user wants to create more training data for the neural network (this should be restricted)
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'training_data'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    # directs the user to the page for creating training data
    # ideally this would have a restriction to admin users
    return render_template('drawing_createTraining.html')


@app.route('/single/match')
def single_match():
    # when the user plays a single player version of match
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'single_match'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    return render_template('match_single.html')


@app.route('/multiplayer/drawing/')
def select_game():
    # when the user has selected to do a multiplayer game of drawing - redirected to select the game
    # as explained in profile()
    global login_data_dict
    # log()
    if 'flash' in login_data_dict:
        flash(login_data_dict['flash'])
        login_data_dict.pop('flash')
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'select_game'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    # gets all of the 'drawing' games currently available that are made by friends
    available_private = game_user_table.get_available_private_games(session['UserID'])
    # gets all of the 'drawing' games that are currently available made public by anyone
    available_public = game_user_table.get_available_public_games(session['UserID'])
    return render_template('pick_game.html', public_games=available_public, private_games=available_private)


@app.route('/multiplayer/new-game/<parameter>', methods=["GET", "POST"])
def make_new_game(parameter):
    # when the user tries to create a new game
    # parameter is a boolean expression indicating whether the user wanted to make a private game
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'make_new_game'
            login_data_dict['here_args'] = parameter
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    if parameter == "False":
        private = False
    elif parameter == "True":
        private = True
    else:
        return redirect(url_for('page_not_found'))
    # creates a new (private/public) drawing game
    game_id = game_user_table.create_new_game(session['UserID'], private, 'drawing')
    return redirect(url_for('multi_drawing', parameter=game_id))


@app.route('/multiplayer/access/<int:parameter>', methods=['GET', 'POST'])
def multi_drawing_access(parameter):
    # this is called when a user clicks on an available game - parameter is the game id
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'multi_drawing_access'
            login_data_dict['here_args'] = parameter
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    # if the game that the usr has tried to access is not full
    if game_table.game_available(parameter):
        # the user is made a member of the group
        game_user_table.new_game_user(session['UserID'], parameter)
        # as this is only called when a user joins an existing game,
        # the game is now full (only 2 players for each game)
        # this removes it from the view of other users.
        game_table.make_full(parameter)
        return redirect(url_for('multi_drawing', parameter=parameter))
    else:
        # returns the user to the select game page
        return redirect(url_for('select_game'))


@app.route('/multiplayer/game/<int:parameter>', methods=['GET', 'POST'])
def multi_drawing(parameter):
    # when the user plays a multiplayer game of drawing
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'multi_drawing'
            login_data_dict['here_args'] = parameter
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    # if this user is in the game
    if game_user_table.user_allowed(parameter, session['UserID']):
        if game_table.game_active(parameter):
            # find the username of the other user in the game
            user = game_user_table.others_in_room(parameter, session['UserID'])
            # the room id is set to the room session
            session['room'] = parameter
            return render_template('drawing_multi.html')
        else:
            flash('That game is no longer active!')
            return redirect(url_for('select_game'))
    else:
        # the user is returned to the select game page if they are not allowed in the game
        flash('That game is not available to you!')
        return redirect(url_for('select_game'))


@app.route('/learn')
def learn():
    # shows the user all of the levels that they can access (as well as the dictionary)
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'learn'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    # finds the list of all levels
    levels = levels_table.get_levels()
    # list of lists including the level name, and it's ID
    lvls = []
    for lvl in levels:
        lvls.append([lvl[0], lvl[1]])
    # passes the levels to the html page
    return render_template('levelchoose.html', levels=lvls)


@app.route('/level/<int:parameter>')
def level(parameter):
    # when the user is working through a level
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'level'
            login_data_dict['here_args'] = parameter
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    return render_template("levels.html", level="LEVEL " + str(parameter))


# a page with buttons where each button is one of the user's friends
@app.route('/chatrooms')
def chatrooms():
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'chatrooms'
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}

    friends = friends_table.get_user_friends(session['UserID'])
    return render_template('chatchoose.html', friends=friends)


# user is redirected here from chatrooms/clicking in profile to get the room where two users
@app.route('/access-chat/<int:parameter>')
def access_chat(parameter):
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'access_chat'
            login_data_dict['here_args'] = parameter
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}

    if friends_table.check_friends(parameter, session['UserID']):
        roomid = chatroom_table.get_room(session['UserID'], parameter)
        if roomid:
            # if a chat is found, send the user there
            return redirect(url_for('chat', parameter=roomid))
        else:
            # if the users haven't chatted yet, make a new chat room
            roomid = chatroom_table.new_chat(session['UserID'], parameter)
            return redirect(url_for('chat', parameter=roomid))
    return render_template('not_friends.html', userid=parameter)


# the actual chatroom
@app.route('/chat/<int:parameter>')
def chat(parameter):
    # as explained in profile()
    global login_data_dict
    # log()
    if 'username' not in session:
        if 'username' not in login_data_dict:
            login_data_dict['go_here'] = 'chat'
            login_data_dict['here_args'] = parameter
            flash('You must login to view this page!')
            return redirect(url_for('login'))
        else:
            session['username'] = login_data_dict['username']
            session['UserID'] = login_data_dict['UserID']
            session['email'] = login_data_dict['email']
            login_data_dict = {}
    if chatroom_table.check_chat(parameter, session['UserID']):
        session['room'] = parameter
        return render_template('chat.html')
    return redirect(url_for('chatrooms'))


if __name__ == "__main__":
    app.run()
