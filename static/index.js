document.addEventListener('DOMContentLoaded', () => {
    const room = document.querySelector("#room").innerHTML;

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        // connect user to this room when page is loaded
        socket.emit('join', {'room': room});

        // send new message by press button
        document.querySelector('#send_msg').onsubmit = () => {
                const text_msg = document.querySelector("#text_msg").value;
                socket.emit('send_msg', {'text_msg': text_msg, 'room': room});


                // Create new item for list
                const li = document.createElement('li');
                li.className = "list-group-item p-0 m-0";
                li.innerHTML = document.querySelector('#text_msg').value;

                // add li to chat
                document.querySelector("#chat").append(li);

                // Clear input field
                document.querySelector('#text_msg').value = '';

                // Stop form from submitting
                return false;
        };
    });

    // When a new message is received, add it to the chat
    socket.on('new_row', data => {
        const p = document.createElement('p');
        p.innerHTML = data.row;
        document.querySelector("#chat").append(p);
    });

    // join new user
    socket.on('new_user', data => {
        // const li = document.createElement('li');
        // li.className = "list-group-item p-0 m-0  bg-light";
        // li.innerHTML = data.user;

        // document.querySelector("#list_users").append(li);
        document.querySelector("#list_users").innerHTML = ''
        for (const i in data.users) {
            const li = document.createElement('li');
            li.className = "list-group-item p-0 m-0  bg-light";
            li.innerHTML = data.users[i];

            document.querySelector("#list_users").append(li);
        }

    });

    // By default, submit button is disabled
    document.querySelector('#sbm').disabled = true;

    // Enable button only if there is text in the input field
    document.querySelector('#text_msg').onkeyup = () => {
        if (document.querySelector('#text_msg').value.length > 0)
            document.querySelector('#sbm').disabled = false;
        else
            document.querySelector('#sbm').disabled = true;
    };

});



