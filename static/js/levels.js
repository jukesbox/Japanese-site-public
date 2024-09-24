/** levels.js

This file is used to manage the networking and button clicks/submissions from the user when they are
completing a level.

required packages:
io
*/


var socket = io();

socket.on('connect', function() {
    /**
    Gets the characters/audios/animations for the current level.

    No required parameters.

    Returns
    -------
    None
    */
    // gets the number at the end of the URL to be LevelNum in the dictionary to be sent in the socket event.
    var wndw = window.location.href;
    var level = wndw.split("/");
    data = {EventType: 'get_level_data', LevelNum: level[level.length - 1]};
    socket.emit('message', data)
});

socket.on('level_data', function(data) {
    /**
    Sets up the page to show the data related to the level that the user is on.

    Parameters
    ----------
    data: dictionary
        Contains the lists 'char_list', 'char_audios', 'animations' and 'paragraphs' which
        make up the level content.

    Returns
    -------
    None

    */
    var characters = data['char_list'];
    var char_audios = data['char_audios'];
    var char_animate = data['animations'];
    var para_num = 1;
    // add the text in each paragraph to the paragraph in the HTML.
    for (item in data['paragraphs']) {
        console.log(item);
        document.getElementById('paragraph_'+ para_num.toString()).innerHTML = data['paragraphs'][item];
        para_num += 1;
    }
    // for each of the audios.
    for (audio in char_audios) {
        // creates a button for each of the characters so that they can be
        // pressed to play the corresponding audios
        node = document.getElementById("audio");
        clone = node.cloneNode(true);
        clone.id = "audio-" + characters[audio][0];
        clone.style.display = 'block';
        clone.children[0].innerHTML = characters[audio][1];
        clone.children[0].id = "audio-char-" + characters[audio][0];
        clone.onclick = function(){play_audio(this.id);};
        document.getElementById('audios').appendChild(clone);

        // creates the hidden elements that actually contain the audio to be played
        node = document.getElementById("audio-audio");
        clone = node.cloneNode(true);
        clone.id = "audio-" + characters[audio][0] + "-audio";
        clone.children[0].src = char_audios[audio];
        document.getElementById('recordings').appendChild(clone);
    }
    // for each of the animations, display them on the screen
    for (animation in char_animate) {
        node = document.getElementById("animate-card");
        clone = node.cloneNode(true);
        clone.style = "display:block;"
        clone.id = "animate-card-" + characters[animation][0];
        clone.children[0].src = char_animate[animation];
        // text next to each character telling the user which character it is.
        clone.children[1].innerHTML = "This is the character '" + characters[animation][0] + "'";
        document.getElementById('animations').appendChild(clone);

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
    window.location.replace(data['url']);
});

function finished_level() {
    /**
    Sends a socket event to show that the user has finished the level.

    No required parameters.

    Returns
    -------
    None
    */
    // gets the last part of the URL for the level number to add to the dictionary sent in the socket event
    var wndw = window.location.href;
    var level = wndw.split("/");
    data = {EventType: 'finished_level', LevelNum:level[level.length - 1]}
    socket.emit('message', data);

}

function play_audio(_id) {
    /**
    Plays the audio that corresponds with the character that was clicked.

    Parameters
    ----------
    _id: str
        The ID of the HTML element that was clicked.

    Returns
    -------
    None

    */
    var audio = document.getElementById(_id + "-audio");
    console.log(audio)
    // plays the audio in the HTML element with ID (_id)-audio
    audio.play();
}