/** create_training.js

This file is used to manage the networking, canvas events and button clicks/submissions from the
user when they are creating training data.

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
var snapshots = {}
// the number of strokes that the user has drawn.
var strokeNum = 0;
var socket = io();
var own_id = 0;
var kana = '';
var sound = '';
var sound_num = 0;


socket.on('connect', function() {
    /**
    When the user connects to the page, get the room and userid of the user.

    No required parameters.

    Returns
    -------
    None
    */
    console.log('connected')
    data = {EventType:"request_info"}
    socket.emit('message', data)

})

socket.on('info', function(data) {
    /**
    Receives and stores the user's UserID, sends a socket event to get the first challenge.

    Parameters
    ----------
    data: dictionary
        Contains the key UserID (int) which is the user's ID.

    Returns
    -------
    None
    */
    var own_id = data['UserID'];
    data = {EventType:'ask_for_challenge'};
    socket.emit('message', data);
});

socket.on('recv_challenge', function(data) {
    /**
    Receives the next character to draw.

    When the socket event 'recv_challenge' is received, the screen is reset to its original state,
    The new 'kana', 'sound', and 'sound_num's are recorded, and the user is told to draw that character.

    Parameters
    ----------
    data: dictionary
        Contains 'kana' (str), 'sound' (str) and 'sound_num' (int)
        giving information about the new character to draw.

    returns
    -------
    None
    */
    console.log(data);
    kana = data['kana'];
    sound = data['sound'];
    sound_num = data['sound_num'];
    document.getElementById("draw_message").innerHTML = "Draw the character for: "+ sound;
    document.getElementById('clr').style.display = 'block';
    document.getElementById('submit').style.display = 'block';
    document.getElementById('continue').style.display = 'none';

    var canvas = document.getElementById("image");
    var context = canvas.getContext("2d");
    var img = new Image();
    img.onload = function() {
        console.log('loaded');
        context.drawImage(img, 0, 0);
    };
    img.src = "../../static/character_images/kana/chara-"+ sound + ".jpg";
    });


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
    canvas = document.getElementById('canvas');
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

// when the user clicks the button to indicate that they have finished drawing.
function save() {
    /**
    Sends a socket event containing the canvas 'snapshots' to be added to the testing data.

    No required parameters.

    Returns
    -------
    None
    */
    document.getElementById('clr').style.display = 'none';
    document.getElementById('submit').style.display = 'none';
    document.getElementById('continue').style.display = 'block';
    image = JSON.stringify(snapshots);
    data = {UserID: own_id, EventType: 'image_submit_train', image_data:image, sound_num:sound_num, sound:sound};
    socket.emit('message', data);
}

// when the user is ready for the next challenge
function next() {
    /**
    When the user clicks next, and is ready to see the next challenge, sends a socket event to get the next challenge.

    No required parameters.

    Returns
    -------
    None
    */
    data = {EventType:'ask_for_challenge'};
    socket.emit('message', data);
    document.getElementById("continue").style.display = "none";
    erase();
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
    // if the event type (as defined by the function parameters in the event listener)
    // is mousedown...
    if (res == 'down') {
        // the current stroke number is incremented by 1
        strokeNum = strokeNum + 1;
        // the previous coordinates are set to the previous current coordinates.
        prevX = currX;
        prevY = currY;
        // the current coordinates are set to the offset of the muse within the canvas
        // this is done by calculating the offset of the canvas from the edge of the window,
        // and calculating the mouse position on the screen.
        currX = event.clientX - canvas.offsetLeft;
        currY = event.clientY - canvas.offsetTop;


        // the program is allowing drawing to happen, because it is valid.
        drawing_ = true;
    }
    // if the event detected was mouseup...
    if (res == 'up') {
        // creates a HTML Image element and
        // assigns its value to the variable image.
        var image = new Image();
        // converts the state of the canvas to a
        // data URL and stores it in image.src
        image.src = canvas.toDataURL();
        var last_stroke = strokeNum - 1
        // creates a key which indicates the stroke number
        // and assigns to it the image data URL.
        snapshots["Stroke" + strokeNum.toString()] = image.src;
        // stops drawing the line
        drawing_ = false
    }
    // if the user's mouse moves outside of the canvas
    // the line stops being drawn.
    if (res == 'out'){
        drawing_ = false;
    }
    // if the event detected was the mouse moving...
    if (res == 'move') {
        // if the mouse is also pressed down.
        if (drawing_) {
            // the previous coordinates are set to what is
            // currently considered to be the current coordinates
            prevX = currX;
            prevY = currY;
            // the current coordinates are calculated by working out
            // the mouse position on the whole screen,
            // minus the offset of the canvas itself.
            currX = event.clientX - canvas.offsetLeft;
            currY = event.clientY - canvas.offsetTop;
            // the function 'draw' is called, so that the line can be drawn.
            draw();
        }
    }
}