document.addEventListener('DOMContentLoaded', () => {
    const room = document.querySelector("#room").innerHTML;
    localStorage.setItem('room', room);

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', () => {
        // connect user to this room when page is loaded
        socket.emit('join', {'room': room});

        // send new message by press button
        document.querySelector('#send_msg').onsubmit = () => {
                const text_msg = document.querySelector("#text_msg").value;
                socket.emit('send_msg', {'text_msg': text_msg, 'room': room});

                // Clear input field
                document.querySelector('#text_msg').value = '';

                // Stop form from submitting
                return false;
        };
    });

    // When a new message is received, add it to the chat
    socket.on('new_row', data => {
        // Create new row for chat
        const row = document.createElement('div');

        const time = document.createElement('span');
        time.className = "row_time";
        time.innerHTML = data.row[0];
        row.append(time);

        const user = document.createElement('span');
        user.className = "row_user";
        user.innerHTML = ` ${data.row[1]}: `;
        row.append(user);

        row.append(data.row[2]);

        // add row to chat
        document.querySelector("#chat").append(row);
        scroll_to_bot();
    });


    // join new user
    socket.on('new_user', data => {
        // create and post new row to chat
        const row = document.createElement('div');
        row.className = 'system_msg';
        row.innerHTML = `${data.time} Join ${data.user} to room`;
        document.querySelector("#chat").append(row);

        update_users(data);
        scroll_to_bot();
    });


    // Leave user
    socket.on('leave_user', data => {
        // create and post new row to chat
        const row = document.createElement('div');
        row.className = 'system_msg';
        row.innerHTML = `${data.time} ${data.user} leave the room`;
        document.querySelector("#chat").append(row);

        update_users(data);
        scroll_to_bot();
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


    // Close button (leave room)
    document.querySelector('#close_room').onclick = () => {
        // not work in Firefox without timeout
        setTimeout(() => { socket.emit('leave', {'room': room}); }, 20)
        localStorage.setItem('room', '');
        window.location.href = "/";
    };


    // Logout link
    document.querySelector('#logout').onclick = () => {
        // not work in Firefox without timeout
        setTimeout(() => { socket.emit('leave', {'room': room}); }, 20)
        localStorage.setItem('room', '');
    };
});


function update_users(data) {
    // Refresh users list
    document.querySelector("#list_users").innerHTML = '';
    for (const i in data.users) {
        const li = document.createElement('li');
        li.className = "list-group-item p-0 m-0  bg-light";
        li.innerHTML = data.users[i];
        document.querySelector("#list_users").append(li);
    }
    document.querySelector("#total_users").innerHTML = data.users.length;
}


function scroll_to_bot() {
    // scroll chat-windows to last message
    var objDiv = document.getElementById("chat");
    objDiv.scrollTop = objDiv.scrollHeight;
}


