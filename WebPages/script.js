document.addEventListener("DOMContentLoaded", function() {
    const tbody = document.querySelector(".game-board tbody");

    for (let row = 0; row < 10; row++) {
        const tr = document.createElement("tr");
        for (let col = 0; col < 10; col++) {
            const td = document.createElement("td");
            td.className = (row + col) % 2 === 0 ? "even" : "odd";
            td.id = `cell-${row}-${col}`;
            tr.appendChild(td);
        }
        tbody.appendChild(tr);
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const addPlayerList = document.querySelector(".game-info pnth-of-type(1)");

    const socket = new WebSocket("ws://localhost:8080");
    socket.onmessage = function(event) {
        const message = JSON.parse(event.data);
        update_add_player_list(message);
    }

    function update_add_player_list(players) {
        layerList.innerHTML = "Players: " + players.map(p => p.username).join(", ");
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const removePlayerList = document.querySelector(".game-info pnth-of-type(2)");

    const socket = new WebSocket("ws://localhost:8080");
    socket.onmessage = function(event) {
        const message = JSON.parse(event.data);
        update_remove_player_list(message);
    }

    function update_remove_player_list(players) {
        removePlayerList.innerHTML = "Players: " + players.map(p => p.username).join(", ");
    }
});
