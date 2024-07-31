// Front/static/js/websocket.js

document.addEventListener('DOMContentLoaded', function() {
    var userId = document.getElementById('coins-count').getAttribute('data-user-id');
    var ws = new WebSocket('ws://' + window.location.host + '/ws/user/' + userId + '/');

    ws.onmessage = function(event) {
        var data = JSON.parse(event.data);
        document.getElementById('coins-count').innerText = data.coins;
    };
});
