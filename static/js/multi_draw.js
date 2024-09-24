/** multi_draw.js

This file is used to manage the user’s interaction with the canvas/webpage when
drawing characters with other users (url extension /create-training).

required packages:
io
*/

// initially assigns the variable 'canvas' the value false.
var canvas = false;
var ctx = false;
var drawing_ = false;
// the mouse position
var prevX = 0;
var currX = 0;
var prevY = 0;
var currY = 0;
// the colour and width of the lines
var line_colour = "black";
var line_width = 20;
// the object that will store the data URL of the character after each stroke.
// this is the object that is converted to a JSON string and returned for the program to interpret
var snapshots = {};
// the number of strokes that the user has drawn.
var strokeNum = 0;
var socket = io();
var waiting = true;
var room = 0;
var own_id = 0;
// the object is defined here
let status = {yourself:
                    {submitted: false,
                        result: false,
                        user_id: 0,
                        ready: false,
                        points: 0},
                other_user:
                    {submitted: false,
                        result: false,
                        user_id: 0,
                        ready: false,
                        points: 0}
};
var kana = '';
var sound = '';
var sound_num = 0;


socket.on('connect', function() {
        // when the user connects
        socket.emit('message', {EventType:'check_allowed'});
        data = {EventType: 'connected'};
        socket.emit('message', data);
    });


socket.on('move_user', function(data) {
    /**
    Moves the user to the url associated with the key 'url' in the dictionary 'data'.

    Parameters
    ----------
    data (dictionary)

    Returns
    -------
    None
    */
    window.location.replace(data['url']);
});

socket.on('allowed_check', function(data) {
    /**
    Determines whether the user is allowed in this game.

    When the socket event 'allowed_check' is received, if 'allowed' within the dictionary 'data' is the boolean
    value 'false', then the user is shown the 'not allowed' screen and is directed away from the page.
    Otherwise, the event has no effect.

    Parameters
    ----------
    data: dictionary
        Contains the key 'allowed' which determines whether the user is allowed in the game or not.

    Returns
    -------
    None
    */
    if (data['allowed'] == false) {
        var overlay = document.getElementById('not_allowed');
        overlay.style.display = 'block';
    } else {}
});


socket.on('info', function(data) {
    /**
    Receives and stores the data about the user.

    When the socket event 'info' is received,  the room and ID of the user are stored in variables,
    and the events 'join' and 'waiting' are emitted (with the appropriate data dictionaries).

    parameters
    ----------
    data: dictionary
        Contains 'room' (int) and 'UserID' (int) corresponding to data about the user and the current location.

    Returns
    -------
    None
    */
    room = data['room'];
    own_id = data['UserID'];
    data = {username: own_id, room: room};
    socket.emit('join', data);
    status['yourself']['user_id'] = own_id;
    data = {UserID: own_id, room: room, EventType: 'waiting'};
    socket.emit('message', data);
    }
);

socket.on('recv_img', function(data) {
    /**
    Deals with the other user's image when it is received.

    When the socket event 'allowed_check' is received, if 'allowed' within the dictionary 'data' is the boolean
    value 'false', then the user is shown the 'not allowed' screen and is directed away from the page.
    Otherwise, the event has no effect.

    parameters
    ----------
    data: dictionary
        Contains 'image' (str) the data URL that is teh other user's final drawing.

    Returns
    -------
    None
    */

    // draws the drawing on the canvas
    var canvas = document.getElementById("other_canvas");
    var context = canvas.getContext("2d");
    var img = new Image();
    img.onload = function() {
        context.drawImage(img, 0, 0);
    };
    // indicates that the other user has submitted their drawing.
    status['other_user']['submitted'] = true;
    img.src = data['image'];
    if (status['yourself']['submitted'] === false) {
    // don't show the image if the user hasn't submitted theirs.
    canvas.style.display = 'none';
    }
    });


socket.on('other_connection', function(data) {
    /**
    Sets the variables related to the other user that has joined.

    When the socket event 'other_connection' is received (when another user is in the game),
    the overlay telling the user to wait is hidden, and the username of the other user is shown
    on screen. The userid is set within the 'status' dictionary.

    Parameters
    ----------
    data: dictionary
        Contains 'username' (Str) and 'UserID' (int), giving information about the other user in the room.

    returns
    -------
    None
    */
    document.getElementById("overlay").style.display = "none";
    document.getElementById("other-user").innerHTML = data['username'];
    status['other_user']['user_id'] = data['UserID'];
    waiting = false;
});


socket.on('wait', function() {
    /**
    Sends a message to check that another user hasn't joined.

    When the 'wait' socket event is received, the user is shown the waiting screen and the 'waiting'
    socket event is sent again to check that the user is still alone in the game.

    No required parameters.

    returns
    -------
    None
    */
    document.getElementById("overlay").style.display = "block";
    data = {UserID: own_id, EventType: 'waiting', room: room};
    socket.emit('message', data);
});



socket.on('result_img', function(data) {
    /**
    When an image has been marked, the appropriate result is shown to the user.

    When the socket event 'result_img' is received.
    The user who's result it is receives points if they got it right, the total points
    are stored in the 'status' dictionary.

    Parameters
    ----------
    data: dictionary


    returns
    -------
    None
    */
    user = data['UserID'];
    // if the drawing was by THIS user...
    if (user == own_id) {
        status['yourself']['result'] = data['result'];
        // if the user got it right, add points to the total
        if (data['result']) {
            status['yourself']['points'] = status['yourself']['points'] + data['points'];
            document.getElementById('you_points').innerHTML = status['yourself']['points'] + " POINTS";
    }
    }
    else {
        // if the drawing is by the other user
        status['other_user']['result'] = data['result'];
        if (data['result']) {
            // if the user got it right, add points to the total
            status['other_user']['points'] = status['other_user']['points'] + data['points'];
            document.getElementById('other_points').innerHTML = status['other_user']['points'] + " POINTS";
        }
    }
    // change the colour of the canvases.
    colour_results()
});

socket.on('other_ready', function(data) {
    /**
    Sets the boolean value 'ready' within the other user's 'status' dictionary to 'True'.

    This is called when the 'other_ready' socket event is received.

    Parameters
    ----------
    data: dictionary
        Contains 'UserID' (int) to indicate who has clicked ready.

    returns
    -------
    None
    */
    if (data['UserID'] == status['other_user']['user_id']) {
        status['other_user']['ready'] = true;
    }

})

socket.on('recv_challenge', function(data) {
    /**
    Sets the game back up for the next round, receiving the next character to draw.

    When the socket event 'recv_challenge' is received, the screen is reset to its original state,
    as is the 'status' dictionary (except userIDs and usernames). The new 'kana', 'sound', and 'sound_num's are recorded,
    and the user is told to draw that character.

    Parameters
    ----------
    data: dictionary
        Contains 'kana' (str), 'sound' (str) and 'sound_num' (int)
        giving information about the new character to draw.

    returns
    -------
    None
    */

    // clears both of the canvases
    erase();
    document.getElementById('drawing_canvas').style.backgroundColor = "white";
    clear_other();

    // resets which buttons should be displayed to the user before submission.
    document.getElementById('clr').style.display = "inline";
    document.getElementById('submit').style.display = "inline";
    document.getElementById('ready').style.display = "none";
    document.getElementById('ready_message').style.display = "none";
    // resets the status of both users.
    status['yourself']['submitted'] = false;
    status['yourself']['result'] = false;
    status['yourself']['ready'] = false;
    status['other_user']['submitted'] = false;
    status['other_user']['result'] = false;
    status['other_user']['ready'] = false;
    // kana, sound, number,
    kana = data['kana'];
    sound = data['sound'];
    sound_num = data['sound_num'];
    // shows the character to draw to the user.
    document.getElementById('draw-statement').innerHTML = "Draw the character for \'"+ sound + "\'";
});

function leave_game() {
    /**

    When the user clicks 'leave game', a socket event is sent that ends the game for all users.

    No required parameters.

    returns
    -------
    None
    */
    socket.emit('message', {EventType: "leave_room", room:room});
};


function init() {
    /**
    Canvas setup.

    Initialises the canvas and allows mouse movement/clicks on the canvas to be recognised.
    Called when the page is first loaded.

    No required parameters.

    returns
    -------
    None
    */
    // defines the variable 'canvas' to be the canvas HTML element
    canvas = document.getElementById('drawing_canvas');
    ctx = canvas.getContext("2d");
    w = canvas.width;
    h = canvas.height;
    // adds event listeners to the canvas to detect when certain actions are performed.
    // the appropriate function is associated to the action.
    canvas.addEventListener("mousemove", function (event) {
        findcoords('move', event)
    }, false);
    canvas.addEventListener("mousedown", function (event) {
        findcoords('down', event)
    }, false);
    canvas.addEventListener("mouseup", function (event) {
        findcoords('up', event)
    }, false);canvas.addEventListener("mouseout", function (event) {
        findcoords('out', event)
    }, false);
}

function draw() {
    /**
    draws a line between detected mouse positions while the left mouse button is pressed down..

    No required parameters.

    returns
    -------
    None.
    */
    // begins a new path.
    ctx.beginPath();
    // the line type - this makes the line smooth.
    ctx.lineCap = 'round';
    // the coordinates of where the line is drawn from
    ctx.moveTo(prevX, prevY);
    // the coordinates of the endpoint of the line.
    ctx.lineTo(currX, currY);
    // the colour of the line is set.
    ctx.strokeStyle = line_colour;
    // the width of the line is set.
    ctx.lineWidth = line_width;
    // outlines the path specified in the function
    ctx.stroke();
    // ensures that the path is closed.
    ctx.closePath();
}


// the erase button may not be kept within the functioning website to promote accurate
// character drawing - however for now it clears the canvas.
function erase() {
    /**
    Clears the currently stored canvas 'snapshots', and clears the canvas.

    Called when the user clicks the 'clear' button below their canvas'

    No required parameters.

    returns
    -------
    None
    */
    snapshots = {};
    strokeNum = 0;
    ctx.clearRect(0, 0, w, h);
}

function clear_other() {
    /**
    Clears the other user's canvas.

    Called when a new challenge is given. Resets the other user's canvas.
    */
    document.getElementById('other_canvas').style.backgroundColor = "white";
    var canvas = document.getElementById("other_canvas");
    var context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
    }


function save() {
    /**
    Sends a socket event containing the canvas 'snapshots' to be marked and sent to the other user.

    Checks that the user is not still waiting for another to join (it should be impossible to submit
    in this case anyway). Hides some of the buttons and sends the dictionary of snapshots as a JSON string.
    */
    // only submits the image if the user is not still waiting for another player
    if (waiting === false) {
        document.getElementById('clr').style.display = 'none';
        document.getElementById('submit').style.display = 'none';
        // the snapshots object is converted to a string using JSON.
        image = JSON.stringify(snapshots);
        data = {UserID: own_id, EventType: 'image_submit', image_data:image, room:room, sound_num:sound_num};
        socket.emit('message', data);
        // the value assigned to the image_holder form field becomes the JSON string.
        status['yourself']['submitted'] = true;
        document.getElementById("other_canvas").style.display = "inline";
        // stops the page from being reloaded
        return false;
    }
    else {
        erase();
        return false;
    }

}

function colour_results() {
    /**
    Colours the canvases depending on whether each user got the drawing right or not.

    Checks that both users have submitted their drawings first. Called when a result is received
    (only completes actions when both users have submitted their drawings.

    No required parameters.

    returns
    -------
    None.
    */
    if ((status['yourself']['submitted'] === true) && (status['other_user']['submitted'] === true)) {
                document.getElementById('ready').style.display = "block";
        if (status['other_user']['result'] === false) {
            document.getElementById('other_canvas').style.backgroundColor = "red"
        }
        else {
            document.getElementById('other_canvas').style.backgroundColor = "#67e088"
    }

    if (status['yourself']['result'] === false) {
        document.getElementById('drawing_canvas').style.backgroundColor = "red"
    }
    else {
        document.getElementById('drawing_canvas').style.backgroundColor = "#67e088"
    }
    }

}


function ready() {
    /**
    Sends a socket event to indicate that the user is ready to continue.

    Determines whether the other user is already ready, if so then 'both' in the data dictionary set to true,
    prompting the reset of the game (the next character to be selected).

    No required parameters.

    returns
    -------
    None.
    */
    document.getElementById("ready_message").style.display = "block";
    status['yourself']['ready'] = true;
    if (status['other_user']['ready'] == true) {
        data = {EventType:"user_ready", UserID:status['yourself']['user_id'],
        OtherID:status['other_user']['user_id'], both:true, room:room}
    } else {
        data = {EventType:"user_ready", UserID:status['yourself']['user_id'],
        OtherID:status['other_user']['user_id'], both:false, room:room}
    }
    socket.emit('message', data);

}

function findcoords(res, event) {
    /**
    Called when an event is detected on the canvas. Depending on the event detected, gets the mouse position and
    starts/stops drawing or continues drawing to a different point.

    parameters:- res (the event type detected), event (the event detected by the listener)

    returns
    -------
    None
    */
    if (res === 'down') {
        strokeNum = strokeNum + 1;
        prevX = currX;
        prevY = currY;
        currX = event.clientX - canvas.offsetLeft;
        currY = event.clientY - canvas.offsetTop;

        drawing_ = true;
    }
    if (res === 'up') {
        var image = new Image();
        image.src = canvas.toDataURL();
        var tmp = 'stroke' + strokeNum;
        snapshots[tmp] = image.src;
        drawing_ = false;
    }

    if (res === 'out') {
        drawing_ = false
    }

    if (res === 'move') {
        if (drawing_) {
            prevX = currX;
            prevY = currY;
            currX = event.clientX - canvas.offsetLeft;
            currY = event.clientY - canvas.offsetTop;
            draw();
        }
    }
}


