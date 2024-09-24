/** profile.js

This file is used to manage the networking and button clicks/submissions from the user when they are
on one of the profile pages.

required packages:
io
*/

var socket = io();
var friends = [];

socket.on('connect', function() {
    /**
    When the user connects to the page, get information about the user/ the user's page they're accessing.

    No required parameters.

    Returns
    -------
    None
    */
    var wndow = window.location.href;
    // if the user is on another user's profile, get the other user's profile data.
    if (wndow.includes('other-profile')) {
        var usernme = wndow.split("/");
        data = {EventType: 'get_profile_data', OtherUsername: usernme[usernme.length - 1]};
    } else if (wndow.includes('change-password')) {
        data = {EventType: 'check_pword_change'};
    }
    else {
    // get the user's profile data and settings
    data = {EventType: 'get_profile_data'};
    socket.emit('message', {EventType:"get_settings"});
    }

    socket.emit('message', data);
});

socket.on('current_settings', function(data) {
    /**
    Displays the current settings of the user on the settings page according to the records in the database.

    Parameters
    ----------
    data: dictionary
        The dictionary containing the 'username', 'email' (strings) and email preferences
        ('info', 'remind', 'promo' (bools)) for the user from the database.

    Returns
    -------
    None
    */
    try {
    document.getElementById('username').value = data['username'];
    document.getElementById('email').value = data['email'];
    if (data['info']) {
        document.getElementById('info-choice').checked = true;
    }
    if (data['remind']) {
        document.getElementById('reminder-choice').checked = true;
    }
    if (data['promo']) {
        document.getElementById('promo-choice').checked = true;
    }
    } catch {}

});


socket.on('change_errors', function(data) {
    /**
    Displays all errors from the user trying to change their details on the settings page

    Parameters
    ----------
    data: dictionary
        The dictionary containing the list of errors - 'errors' #

    Returns
    -------
    None
    */
    document.getElementById('errors').innerHTML = "";
    for (message in data['errors']) {
        document.getElementById('errors').innerHTML += data['errors'][message] + "<br/>";
    }

});


// the returned values from the user searching for users.
socket.on('found_users', function(data) {
    /**
    Displays the returned values from a user searching for users.

    Parameters
    ----------
    data: dictionary
        The dictionary containing the list of found users - 'people'.

    Returns
    -------
    None
    */

    users = data['people'];

    if (users.length !== 0) {
    x = -1;
    }
    for (user in users) {
        x += 1;
        node = document.getElementById("request_results");
        clone = node.cloneNode(true);
        clone.id = "request_result_" + x.toString();
        clone.style.display = 'block';
        // innerHTML is Username, ID is final_req_(UserID)
        clone.children[0].innerHTML = users[user][1];
        clone.children[1].id = "final_req_" + users[user][0];
        document.getElementById('request_results_list').appendChild(clone);
    }
});

// finds the user's streaks, points etc.
socket.on('user_data', function(data)  {
    /**
    Adds the data returned from the database tot he page for the user to see.

    Parameters
    ----------
    data: dictionary
        Contains all of the values needed for the progress or friends page.

    Returns
    -------
    None
    */
    // each of the try statements will only work if the user is on specific extensions from the profile page
    // if an error is caught, the program will pass right over it.

    // will work if on the progress page
    try {
    points = data['points'];
    document.getElementById('points_holder').innerHTML = points;
    daily_streak = data['streak'];
    document.getElementById('streak_holder').innerHTML = daily_streak;
    characters = data['characters'];
    document.getElementById('character_holder').innerHTML = characters;
    questions = data['questions'];
    document.getElementById('total_holder').innerHTML = questions;
    next_steps = data['next_steps'];
    document.getElementById('next_steps_holder').innerHTML = next_steps;
    awards = data['awards'];
    for (award in awards) {
        document.getElementById('awards_holder').innerHTML += awards[award] + "<br>";
    }
    } catch(err) {}

    // will work if on the friends page
    try {
    // shows all friend requests to the user
    var friends = data['friend_requests'];
    if (friends.length !== 0) {
    x = 0;
    for (friend in friends) {
        x += 1;
        node = document.getElementById("request_friend_element");
        clone = node.cloneNode(true);
        clone.id = "request_element_" + x.toString();
        clone.style.display = 'block';
        // innerHTML is the the username, id is reject_(username) and accept_(username)
        clone.children[0].innerHTML = friends[friend][1];
        clone.children[1].id = "reject_" + friends[friend][0];
        clone.children[2].id = "accept_" + friends[friend][0];
        document.getElementById('request_friends_list').appendChild(clone);
    }
    }
    var friends = data['friends'];
    if (friends.length !== 0) {
    x = -1;
    // shows all friends to the user.
    for (friend in friends) {
        x += 1;
        node = document.getElementById("friend_element");
        clone = node.cloneNode(true);
        clone.id = "element_" + x.toString();
        clone.style.display = 'block';
        // innerHTML is the username, ID is friend_(Username)
        clone.children[0].innerHTML = friends[friend][1];
        clone.children[1].id = "friend_" + friends[friend][1];
        document.getElementById('friends_list').appendChild(clone);
    }
    }

    } catch(err) {}

});

socket.on('move_user', function(data) {
    /**
    Moves the user to the URL specified in the dictionary.

    Parameters
    ----------
    data: dictionary
        The dictionary containing the URL to redirect the user to - 'url'.

    Returns
    -------
    None
    */
    window.location.replace(data['url']);
});


function setting_changes() {
    /**
    Gets all of the HTML elements containing information that could have been changed by the user.

    Sends a socket event containing all of that data to validate and then update the database.

    No required parameters.

    Returns
    -------
    None
    */
    username = document.getElementById('username').value;
    password = document.getElementById('password').value;
    email = document.getElementById('email').value;
    c_password = document.getElementById('c_password').value;
    reminder = document.getElementById('reminder-choice').checked;
    info = document.getElementById('info-choice').checked;
    promo = document.getElementById('promo-choice').checked;
    data = {EventType:"settings_change", username:username, password:password,
            email:email, c_password:c_password, reminder:reminder, info:info, promo:promo};
    socket.emit('message', data);
}


function make_request() {
    /**
    Searches the database for usernames that are similar to what the user put in the 'search for a user' box.

    No required parameters.

    Returns
    -------
    None
    */
    name = document.getElementById('request_name').value;
    data = {EventType:'look_for', name:name};
    socket.emit('message', data);

}

function final_request(id_) {
    /**
    Makes a friend request to the user that they clicked 'request' on.

    Parameters
    ----------
    id_: str
        the id of the HTML element that the user clicked the 'request' button on.

    Returns
    -------
    None
    */
    // gets the actual userid of the user they have requested.
    var user = id_.replace('final_req_', '');
    data = {EventType:'request_user', UserID:user};
    socket.emit('message', data);
    btn = document.getElementById(id_)
    // stops the user from being able to request to follow the user again before the page reloads.
    btn.value = "Requested";
    btn.onclick = "";
}


function accept_user(id_) {
    /**
    Accepts the friend request of the user that they clicked 'accept' on.

    Parameters
    ----------
    id_: str
        the id of the HTML element that the user clicked the 'accept' button on.

    Returns
    -------
    None
    */
    var user = id_.replace('accept_', '');
    data = {EventType:'accept', UserID:user};
    socket.emit('message', data);
}

function reject_user(id_) {
    /**
    Rejects the friend request of the user that they clicked 'reject' on.

    Parameters
    ----------
    id_: str
        the id of the HTML element that the user clicked the 'reject' button on.

    Returns
    -------
    None
    */
    var user = id_.replace('reject_', '');
    data = {EventType:'reject', UserID:user};
    socket.emit('message', data);
}

function view_user(id_) {
    /**
    Sends a socket event for the user to be able to view the profile of the user that they clicked on.

    Parameters
    ----------
    id_: str
        the id of the HTML element that the user clicked the 'go to profile' button on.

    Returns
    -------
    None
    */
    var user = id_.replace('friend_', '');
    data = {EventType:"view_other_profile", OtherUsername:user};
    socket.emit('message', data);
}

function password_change() {
    var passwd = document.getElementById('password').value;
    data = {EventType: "submit_change", password: passwd}
    socket.emit('message', data);

}

socket.on('password_errors', function(data) {
    document.getElementById('errors').innerHTML = "";
    for (message in data['errors']) {
        document.getElementById('errors').innerHTML += data['errors'][message] + "<br/>";
    }

})

