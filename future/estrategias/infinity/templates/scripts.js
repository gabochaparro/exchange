document.addEventListener("DOMContentLoaded", function() {
    const playPauseBtn = document.getElementById("playPauseBtn");
    const statusText = document.getElementById("statusText");
    let isPaused = true;

    playPauseBtn.addEventListener("click", function() {
        isPaused = !isPaused;
        statusText.textContent = isPaused ? "Pausa" : "Reproduciendo";
        playPauseBtn.textContent = isPaused ? "⏯️" : "⏸️";
    });
});
