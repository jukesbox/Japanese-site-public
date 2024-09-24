/** forms.js

This file is used to manage the networking and button clicks/submissions from the user
when they are on a page that contains forms e.g. login, signup.


required packages:
io
*/

var socket = io();

socket.on('login_error', function(data) {
    /**
    If invalid data is found in the data that the user tried to login with,
    the errors are displayed on the page so that the user can modify the data that they entered.

    Parameters
    ----------
    data: dictionary
        Contains the key 'errors' (list) that is the list of error messages from the data that the user entered.

    Returns
    -------
    None
    */
    document.getElementById('errors').innerHTML = "";
    errors = data['errors'];
    // add the error message and a newline for each error that was found
    for (error in errors) {
        document.getElementById('errors').innerHTML += errors[error] + "<br>";
    }
});

socket.on('signup_errors', function(data) {
    /**
    If invalid data is found in the data that the user tried to sign up with,
    the errors are displayed on the page so that the user can modify the data that they entered.

    Parameters
    ----------
    data: dictionary
        Contains the key 'errors' (list) that is the list of error messages from the data that the user entered.

    Returns
    -------
    None
    */
    document.getElementById('errors').innerHTML = "";
    errors = data['errors'];
    // add the error message and a newline for each error that was found
    for (error in errors) {
        document.getElementById('errors').innerHTML += errors[error] + "<br>";
    }

});

socket.on('move_user', function(data) {
    /**
    Moves the user to the URL specified in the dictionary - 'url'

    Parameters
    ----------
    data: dictionary
        The dictionary containing the url to be moved to - 'url'

    Returns
    -------
    None
    */
    window.location = data['url'];
});

function login() {
    /**
    When the user clicks 'login', gets the values from the username and password fields,
    and sends a socket event to validate the entered details.

    No required parameters.

    Returns
    -------
    None
    */
    user = document.getElementById('usr').value;
    passwd = document.getElementById('passwd').value;
    data = {EventType:"login_data", username:user, password: passwd};
    socket.emit('message', data);
}

function signup() {
    /**
    When a user clicks the 'signup' button - gets all of the values from the fields that the user
    should have entered data into and sends a socket event to validate those details.

    No required parameters.

    Returns
    -------
    None
    */
    username = document.getElementById('usr').value;
    email = document.getElementById('email').value;
    password = document.getElementById('passwd').value;
    c_password = document.getElementById('c_passwd').value;
    data = {EventType:'sign_up_data', username:username, email:email, password:password, c_password:c_password};
    socket.emit('message', data);

}

function forgot() {
    /**
    When a user clicks 'forgot password', a socket event is sent to generate
    a one time pin for the user and send an email to them so that they can enter it.

    No required parameters.

    Returns
    -------
    None
    */
    // the div element that contains the 'login with pin' button and the field to enter the OTP.
    var this_element = document.getElementById('forgot_stuff');
    this_element.style.display = 'block';
    // the text that the user entered as their username.
    var username = document.getElementById('usr').value;
    data = {EventType: 'forgot_password', username:username};
    socket.emit('message', data);
}

function login_pin() {
    /**
    When the user has clicked 'login with pin', gets the value that they entered
    into the username and pin fields.

    Sends a socket event to validate the user's credentials.

    No required parameters.

    Returns
    -------
    None
    */
    var entered_pin = document.getElementById('enter_pin').value;
    var username = document.getElementById('usr').value;
    data = {EventType: 'login_otp', username:username, otp:entered_pin};
    socket.emit('message', data);
}