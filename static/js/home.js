/** home.js

This file is used to manage the networking and button clicks/submissions from the user when they are on the homepage.
required packages:
io
*/


var socket = io();

socket.on('connect', function() {
    /**
    When the user connects, get the top 10 scorers from the database
    (sends socket event).

    No required parameters.

    Returns
    -------
    None
    */
    console.log('connected');
    data = {EventType: "get_leaders"};
    socket.emit('message', data);

});

socket.on('leaderboard', function(data) {
    /**
    Add the top 10 users to the leaderboard.

    Parameters
    ----------
    data: dictionary
        The dictionary containing 'leaders' - a list of tuples with each of the
        top user's Usernames and totalPoints

    Returns
    -------
    None
    */
    // list of tuples
    users = data['leaders'];
    x = 0;
    // for each of the users in the top 10
    for (user in users) {
            x += 1;
            // adds a new row in the table.
            var leaderboard = document.getElementById("leaderboard");
            var new_row = leaderboard.insertRow();
            var number = new_row.insertCell(0);
            var username = new_row.insertCell(1);
            var points = new_row.insertCell(2);
            // the ranking of the user
            number.innerHTML = "#" + x.toString();
            // the user's username
            username.innerHTML = users[user][0];
            // the user's total points
            points.innerHTML = users[user][1];
        }

});