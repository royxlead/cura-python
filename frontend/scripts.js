const chatBox = document.getElementById("chat-box");
const inputField = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

inputField.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendMessage();
    }
});

async function sendMessage() {
    const userMessage = inputField.value.trim();
    if (!userMessage) return;

    // Disable input while processing
    inputField.disabled = true;
    sendButton.disabled = true;

    appendMessage("user", userMessage);
    inputField.value = "";

    // Add loading indicator
    const loadingDiv = document.createElement("div");
    loadingDiv.classList.add("bot-msg", "loading");
    loadingDiv.textContent = "Cura is thinking...";
    chatBox.appendChild(loadingDiv);

    try {
        const response = await fetch("http://localhost:8000/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: userMessage })
        });

        const data = await response.json();
        // Remove loading indicator
        chatBox.removeChild(loadingDiv);

        if (data.answer) {
            appendMessage("bot", data.answer);
        } else {
            appendMessage("bot", "Sorry, I couldn't process your request.");
        }
    } catch (error) {
        // Remove loading indicator
        chatBox.removeChild(loadingDiv);
        appendMessage("bot", "Error connecting to server. Please try again.");
    } finally {
        // Re-enable input
        inputField.disabled = false;
        sendButton.disabled = false;
        inputField.focus();
    }
}

function appendMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add(sender === "user" ? "user-msg" : "bot-msg");
    
    const emoji = sender === "user" ? "👤" : "🤖";
    msgDiv.textContent = `${emoji} ${message}`;
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
