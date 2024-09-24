/** chat.js

This file is used to manage the networking and button clicks/submissions from the user when they are within a chatroom.

required packages:
io
*/

var socket = io();
var info = {yours: {id_: 0, messages: []},
            others: {id_: 0, messages: []}};
var your_ind = 0;
var other_ind = 0;
var room = 0;

socket.on('connect', function() {
    /**
    When the user connects, this emits a socket event to determine who the two users in the chatroom are.

    No required parameters.

    returns
    -------
    None
    */
    socket.emit('message', {EventType: 'who_are_we'});
});

socket.on('you_are', function(data) {
    /**
    Sets up the page to hold the right information.

    Called when the 'you_are' socket event is received.
    Assigns the correct values to the variables storing the userids. Sends a socket event to join
    the room and get all previous messages from the chatroom.

    Parameters
    ----------
    data: dictionary
        The dictionary containing 'you', 'them' (UserIDs) and 'room' (ChatID).

    Returns
    -------
    None
    */
    // sets the id values in the object for the IDs of each of the users.
    info.yours.id_ = data['you'];
    info.others.id_ = data['them'];
    // sets the id for the room in the variable
    room = data['room'];
    // joins the room that is returned to the user from 'data'
    data = {username: info.yours.id_, room: room};
    socket.emit('join', data);
    // sends a socketio event to retrieve the messages sent between these users
    data = {EventType: 'get_messages', Other:info.others.id_};
    socket.emit('message', data);
});

socket.on('recv_previous', function(data) {
    /**
    Adds the messages previously sent between members of this chat.

    Parameters
    ----------
    data: dictionary
        The dictionary containing 'yours' and 'others' (lists of messages)

    Returns
    -------
    None
    */
    // adds the messages sent by each of the users to the info object accordingly
    info.yours.messages = data['yours'];
    info.others.messages = data['others'];
    // orders the messages that have been added to the info object
    message_order();
});

socket.on('new_message', function(data) {
    /**
    Adds a new message to the chat that was sent by the other user.

    Parameters
    ----------
    data: dictionary
        The dictionary containing 'message' (str) - the message that was sent.

    Returns
    -------
    None
    */
    console.log(data);
    if (data['message'][1] == info.yours.id_) {
        info.yours.messages.push(data['message'])
    } else {
        info.others.messages.push(data['message'])

    }
    console.log('messages: ', info.yours.messages, info.others.messages);
    message_order();
});

function message_order() {
    /**
    Orders and displays all of the messages in the chat by time sent.

    No required parameters.

    Returns
    -------
    None
    */
    // clears the current messages from the HTML that is shown
    for (let z = 1; z <=your_ind; z++) {
      document.getElementById("your_message_"+ z.toString()).remove();
    }
    your_ind = 0;
    for (let z = 1; z <=other_ind; z++) {
      document.getElementById("other_message_"+ z.toString()).remove();
    }
    other_ind = 0;
    // each of the messages have the tuple ('message', datetime, userid)
    var to_add = {};
    // defines a variable to hold the user's messages
    var messages = info.yours.messages;

    for (messge in messages) {
        // creates a new key-value pair in the dictionary 'to_add'
        // associating the message and ID of who it was from with it's unix time value.
        to_add[messages[messge][1]] = [messages[messge][0], messages[messge][2]];
    }
    // for each of the messages sent by the other user.
    var messages = info.others.messages;
    for (messge in messages) {
        // creates a new key-value pair in the dictionary 'to_add'
        // associating the message and ID of who it was from with it's unix time value.
        to_add[messages[messge][1]] = [messages[messge][0], messages[messge][2]];
    }
    // performs a bubble sort on the dictionary
    sorted_add = bubble(to_add);
    var message_order_list = [];
    for (item in sorted_add) {
        // adds the [message, messageSenderID] to 'message_order_list'
        message_order_list.push(sorted_add[item]);
    }
    // displays the messages on the page.
    display_messages(message_order_list);
}

function bubble(to_sort) {
    /**
    Uses a bubble sort to sort all of the messages in the dictionary to_sort

    Parameters
    ----------
    to_sort: dictionary
        The dictionary containing all of the messages to sort.

    Returns
    -------
    Array
    */
    // finds the number of items in the object
    length = to_sort.length;
    // for each item in the object
    for (x=0; x<length; x++) {
        flag = false;
        for (y=0; y<length; y--) {
            if (to_sort[y] > to_sort[y + 1]) {
                flag = true;
                tmp = to_sort[y];
                to_sort[y] = to_sort[y + 1];
                to_sort[y + 1] = tmp;
            }
        }
        if (flag == false) {
        break;
        }
    }
    // reverses the array so that the newest messages will appear at the bottom with
    // the flex-direction:column-reverse; CSS.
    var sorted = [];
    for (message in to_sort) {
        // inserts each item into position 0 of the array.
        sorted.splice(0, 0, to_sort[message]);
    }
    // returns the ordered array
    return sorted;
}

function display_messages(message_list) {
    /**
    Displays all of the messages on the page

    Parameters
    ----------
    message_list: array
        The array containing each of the messages [message: str, UserID: int]

    Returns
    -------
    None
    */
    for (mess in message_list) {
        // if the message is from this user, add it to this user's side, otherwise add it to the
        // other user's side.
        if (message_list[mess][1] == info.yours.id_) {
            your_ind += 1;
            // creates HTML elements to display the message
            your_ele = document.getElementById('your_message');
            your_clone = your_ele.cloneNode(true);
            your_clone.style = "display:block;";
            your_clone.id = "your_message_" + your_ind.toString();
            your_clone.children[0].children[0].innerHTML = message_list[mess][0];
            document.getElementById('messages_container').appendChild(your_clone);
        }
        else {
            other_ind += 1;
            // creates HTML elements to display the message
            other_ele = document.getElementById('other_message');
            other_clone = other_ele.cloneNode(true);
            other_clone.style = "display:block;";
            other_clone.id = "other_message_" + other_ind.toString();
            other_clone.children[0].children[0].innerHTML = message_list[mess][0];
            document.getElementById('messages_container').appendChild(other_clone);
        }
    }

}

function send_message() {
    /**
    Sends the message that the user has entered into the message box.

    No required parameters.

    Returns
    -------
    None
    */
    var mess = document.getElementById('mess_input').value;
    data = {EventType: 'send_message', mess:mess,
            MessageTo:info.others.id_, MessageFrom:info.yours.id_}
    socket.emit('message', data);
    // clears the message box to reinstate default text.
    document.getElementById('mess_input').value = "";
}
