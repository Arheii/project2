document.addEventListener('DOMContentLoaded', function() {
  document.querySelector('#send_msg').onsubmit = send_message;
//   document.querySelector('#send_msg').pre = send_message;
});

function send_message() {
    const message = document.querySelector("text_msg").value;
    alert('${message!');

}

function hello() {
                  alert('Hello!');
}