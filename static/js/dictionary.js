/** dictionary.js

This file is used to manage the networking and button clicks/submissions from the user when they
are on the dictionary page.

required packages:
io
*/


var socket = io();
var current_index = 0;

socket.on('dictionary_results', function(data) {
    /**
    Displays the results from the database search to the user in a readable format.

    Parameters
    ----------
    data: dictionary
        The dictionary containing the list of search results ('results')

    Returns
    -------
    None
    */
    var parent = document.getElementById("search_results");
    var childr = parent.childNodes;
    // deletes all current search result boxes (from previous searches)
    for (let z = 1; z <= current_index; z++) {
      document.getElementById("search_result_"+ z.toString()).remove();
    }
    // current_index is 0 as there are no search results added
    current_index = 0;
    console.log('received dictionary results');
    var entries = data['results'];
    var x = current_index;
    // for each of the results (each different WordID found)
    for (entry in entries) {
        console.log(entry);
        // decides teh index of the current search result being made.
        x += 1;
        // clones the original (hidden) search result box.
        node = document.getElementById("search_result_");
        clone = node.cloneNode(true);
        clone.id = "search_result_" + x.toString();
        clone.style.display = 'block';
        // the primary reading
        clone.children[1].innerHTML = entries[entry]['PrimaryReading'];
        clone.children[1].id = "primary_" + x.toString();
        clone.children[2].id = "secondary_" + x.toString();
        clone.children[3].id = "meaning_" + x.toString();
        document.getElementById('search_results').appendChild(clone);
        var y = 0;
        var string = document.createElement('h2');
        string.innerHTML = "Other Readings:";
        document.getElementById("search_result_" + x.toString()).appendChild(string);
        // for each of the other readings, add them under the 'Other Readings' heading.
        for (item in entries[entry]['Readings']) {
            // decides the index of the reading in the readings section.
            y += 1;
            reading_node = document.getElementById("secondary_" + x.toString());
            reading_clone = reading_node.cloneNode(true);
            // id: secondary_(result index)(reading index)
            reading_clone.id = "secondary_" + x.toString() + y.toString();
            reading_clone.innerHTML = entries[entry]['Readings'][y - 1];
            document.getElementById("search_result_" + x.toString()).appendChild(reading_clone);
        }
        var string = document.createElement('h2');
        string.innerHTML = "Meanings:";
        document.getElementById("search_result_" + x.toString()).appendChild(string);
        var z = 0;
        // for each of the meanings, add them under the 'Meanings' heading.
        for (item in entries[entry]['Meanings']) {
            z += 1;
            meaning_node = document.getElementById("meaning_" + x.toString());
            meaning_clone = meaning_node.cloneNode(true);
            // id: secondary_(result index)(reading index)
            meaning_clone.id = "meaning_" + x.toString() + z.toString();
            meaning_clone.innerHTML = entries[entry]['Meanings'][z - 1];
            document.getElementById("search_result_" + x.toString()).appendChild(meaning_clone);
        }
    // the number of results added
    current_index = x;
    }

});

function find_word() {
    /**
    Sends a socket event to search the database for results relating to the user's input

    No required parameters.

    Returns
    -------
    None
    */
    word = document.getElementById('word_box').value;
    data = {EventType:'search_dictionary', search_term:word};
    socket.emit('message', data);
}
