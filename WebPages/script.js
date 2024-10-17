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

