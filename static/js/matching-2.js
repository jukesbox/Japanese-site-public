/** chat.js

This file is used to manage the networking and button clicks/submissions from the user when they are
matching characters in the matching game.

required packages:
io
*/



var socket = io();
var characters = [];
var points = 0;
var selected = [];
var not_allowed = [];
var found = [];

socket.on('connect', function() {
    /**
    When the user connects to the page, check that they are allowed (have completed at least one level)

    No required parameters.

    Returns
    -------
    None
    */
    socket.emit('message', {EventType:'check_allowed'});
});

socket.on('allowed_check', function(data) {
    /**
    When the system has checked whether the user is allowed.
    Shows an overlay directing the user to the levels table if not allowed.
    If allowed, emits a socket event 'match_connect' to get the first set of characters/ sounds to match.

    Parameters
    ----------
    data: dictionary
        Contains the key 'allowed' (bool) showing whether the user is allowed or not.

    Returns
    -------
    None
    */
    if (data['allowed'] == false) {
        var overlay = document.getElementById('not_allowed');
        overlay.style.display = 'block';
    } else {
        socket.emit('message', {EventType: "match_connect"});
        }
});

socket.on('character_list', function(data) {
    /**
    Displays the characters to the user.

    Parameters
    ----------
    data: dictionary
        Contains the key 'list' (list) which is the list of characters/sounds for the user to match

    Returns
    -------
    None
    */
    characters = data['list'];
    x = 0;
    // for each of the characters in the list (each is a tuple (character/sound, sound))
    for (character in characters) {
        x += 1;
        // creates the card that is shown to the user that they can select.
        node = document.getElementById("card");
        clone = node.cloneNode(true);
        clone.id = "card_hold_" + x.toString();
        clone.style.display = 'block';
        // shows the character/sound to the user.
        clone.children[0].children[0].innerHTML = characters[character][0];
        clone.children[0].id = "card_" + x.toString();
        // selects the card when it is clicked.
        clone.children[0].onclick = function(){this_one(this.id);};
        document.getElementById('matching').appendChild(clone);
    }

});


function this_one(_id) {
    /**
    When the user selects a card, checks whether it has already been selected/matched and if not, selects it. Calls
    check to see whether the user has now selected two cards etc.

    Parameters
    ----------
    _id: str
        The ID of the HTML element that has been clicked on.

    Returns
    -------
    None
    */
    var this_card = document.getElementById(_id);
    index = parseInt(_id.replace("card_", ""));
    // returns the character sound.
    var this_char = characters[index - 1];
    // if the character has not already been clicked.
    if (not_allowed.indexOf(this_char) == -1) {
        // select the card
        selected.push(this_char);
        // stop this card from being selected again before it is deselected.
        this_card.className = "disabled_selected";
        not_allowed.push(this_char);
        check();
    }
}

function check() {
    /**
    When a new card has been selected. Disable the cards if they were correct and add points, deselect if not.
    Get new cards if the user has now matched all of the cards.

    No required parameters.

    Returns
    -------
    None
    */
    length = selected.length;
    // if two characters have now been selected
    if (length == 2) {
        // if the selected cards match
        // (the format of the item in selected is (character/sound, sound) so 'sound' is the same for
        // matching characters)
        if (selected[0][1] == selected[1][1]) {
            // tell the user that they got it correct.
            document.getElementById('result').innerHTML = 'Correct!';
            // add the two matched characters to the 'found' list.
            for (select in selected) {
            found.push(selected[select]);
            }
            // stop the characters from being selected again
            ind1 = characters.indexOf(selected[0]);
            ind2 = characters.indexOf(selected[1]);
            card_a = document.getElementById("card_" + (ind1 + 1).toString());
            card_b = document.getElementById("card_" + (ind2 + 1).toString());
            card_a.className = "disabled_correct";
            card_b.className = "disabled_correct";
            card_a.onclick = function() {};
            card_b.onclick = function() {};
            // add points to the user's total
            points += 2;
            document.getElementById('points').innerHTML = "Points: " + points.toString();
        }
        else {
            ind1 = characters.indexOf(selected[0]);
            ind2 = characters.indexOf(selected[1]);
            // tell the user that they got it incorrect
            document.getElementById('result').innerHTML = 'Incorrect!';
            card_a = document.getElementById("card_" + (ind1 + 1).toString());
            card_b = document.getElementById("card_" + (ind2 + 1).toString());
            card_a.className = "match_card";
            card_b.className = "match_card";
            // allow the user to select the card again
            card_a.onclick = function() {this_one(this.id)};
            card_b.onclick = function() {this_one(this.id)};
            index1 = not_allowed.indexOf(selected[0]);
            not_allowed.splice(index1, 1);
            index2 = not_allowed.indexOf(selected[1]);
            not_allowed.splice(index2, 1);
        }
    // deselect all cards
    selected = [];
    // if all of the character have now been matched
    if (found.length == 10) {
        // reset the lists
        characters = [];
        found = [];
        not_allowed = [];
        // send a socket event showing that the user has matched all cards.
        socket.emit('message', {EventType: "done_matches"});
        // remove all of the existing cards
        for (let z = 1; z < 11; z++) {
              document.getElementById("card_hold_"+ z.toString()).remove();
        }
        // get a new set of cards
        socket.emit('message', {EventType: "match_connect"});
    }
    }

}