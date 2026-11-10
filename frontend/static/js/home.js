const modal = document.getElementById("guestModal");
const openButtons = [
    document.getElementById("openGuestModal"),
    document.getElementById("openGuestModalBottom"),
    document.getElementById("openGuestModalNav")
].filter(Boolean); // Filter out any elements that don't exist in the DOM

const closeButton = document.getElementById("closeGuestModal");
const startButton = document.getElementById("startGuest");
const message = document.getElementById("guestMessage");

const durationOptions = document.querySelectorAll(".duration-option");

const timerBox = document.getElementById("guestTimer");
const countdown = document.getElementById("countdown");
const endButton = document.getElementById("endGuest");

let selectedDuration = 20;
let timerInterval = null;
let expiresAt = null;

// Open modal
openButtons.forEach(button => {
    button.addEventListener("click", () => {
        if (modal) modal.classList.add("active");
    });
});

// Close modal
if (closeButton && modal) {
    closeButton.addEventListener("click", () => {
        modal.classList.remove("active");
    });
}

if (modal) {
    modal.addEventListener("click", event => {
        if (event.target === modal) {
            modal.classList.remove("active");
        }
    });
}

// Select duration
durationOptions.forEach(option => {
    option.addEventListener("click", () => {
        durationOptions.forEach(item => {
            item.classList.remove("selected");
        });

        option.classList.add("selected");
        selectedDuration = Number(option.dataset.duration) || 20;
        if (message) message.textContent = "";
    });
});

// Start guest session
if (startButton) {
    startButton.addEventListener("click", async () => {
        startButton.disabled = true;
        startButton.textContent = "Starting...";
        if (message) message.textContent = "";

        try {
            const response = await fetch("/api/guest/start", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    duration: selectedDuration
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "Unable to start guest session.");
            }

            // Normalise to seconds in case backend returns milliseconds
            expiresAt = data.expires_at > 1e11 ? Math.floor(data.expires_at / 1000) : data.expires_at;

            if (modal) modal.classList.remove("active");
            startTimer();

        } catch (error) {
            if (message) message.textContent = error.message;
        } finally {
            startButton.disabled = false;
            startButton.textContent = "Start Guest Session";
        }
    });
}

// Timer
function startTimer() {
    if (!timerBox) return;

    timerBox.classList.add("active");

    if (timerInterval) {
        clearInterval(timerInterval);
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    if (!expiresAt) return;

    const currentTime = Math.floor(Date.now() / 1000);
    const remaining = expiresAt - currentTime;

    if (remaining <= 0) {
        clearInterval(timerInterval);
        timerInterval = null;
        expiresAt = null;

        if (timerBox) timerBox.classList.remove("active");

        alert("Your guest session has expired. Start another session to continue exploring.");
        window.location.reload();
        return;
    }

    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;

    if (countdown) {
        countdown.textContent =
            String(minutes).padStart(2, "0") + ":" +
            String(seconds).padStart(2, "0");
    }
}

// Check existing guest session
async function checkGuestSession() {
    try {
        const response = await fetch("/api/guest/status");
        if (!response.ok) return;

        const data = await response.json();

        if (data.active && data.expires_at) {
            expiresAt = data.expires_at > 1e11 ? Math.floor(data.expires_at / 1000) : data.expires_at;
            startTimer();
        }
    } catch (error) {
        console.error("Could not check guest session:", error);
    }
}

// End guest session
if (endButton) {
    endButton.addEventListener("click", async () => {
        try {
            await fetch("/api/guest/end", {
                method: "POST"
            });

            clearInterval(timerInterval);
            timerInterval = null;
            expiresAt = null;

            if (timerBox) timerBox.classList.remove("active");
            window.location.reload();

        } catch (error) {
            alert("Unable to end the guest session. Please refresh the page.");
        }
    });
}

checkGuestSession();

/* =====================================
   CARD AUDIO & HOVER/TOUCH HANDLING
===================================== */

const imageCards = document.querySelectorAll(".image-card");

let activeAudio = null;
let activeCard = null;

function stopCardAudio() {
    if (activeAudio) {
        activeAudio.pause();
        activeAudio.currentTime = 0;
    }

    if (activeCard) {
        activeCard.classList.remove("touch-active");
    }

    activeAudio = null;
    activeCard = null;
}

async function activateCard(card) {
    if (activeCard === card) {
        return;
    }

    stopCardAudio();

    card.classList.add("touch-active");

    const audioPath = card.dataset.audio;
    if (!audioPath) return;

    const audio = new Audio(audioPath);
    activeAudio = audio;
    activeCard = card;

    try {
        await audio.play();
    } catch (error) {
        console.log("Audio playback blocked:", error);
    }

    audio.addEventListener("ended", () => {
        if (activeAudio === audio) {
            stopCardAudio();
        }
    });
}

imageCards.forEach(card => {
    // Desktop hover
    card.addEventListener("mouseenter", () => {
        if (window.matchMedia("(hover: hover)").matches) {
            activateCard(card);
        }
    });

    card.addEventListener("mouseleave", () => {
        if (window.matchMedia("(hover: hover)").matches) {
            stopCardAudio();
        }
    });

    // Touch devices
    card.addEventListener("click", event => {
        if (window.matchMedia("(hover: none)").matches) {
            if (!card.classList.contains("touch-active")) {
                event.preventDefault();
                activateCard(card);
            }
        }
    });
});

// Stop audio/reset card when tapping anywhere outside active card on mobile
document.addEventListener("click", event => {
    if (activeCard && !activeCard.contains(event.target)) {
        stopCardAudio();
    }
});