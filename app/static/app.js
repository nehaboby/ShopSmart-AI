
/* =========================================
   SHOPSMART AI - JAVASCRIPT
   ========================================= */

document.addEventListener("DOMContentLoaded", function () {

    const chatbot = document.getElementById("chatbot");
    const chatMessages = document.getElementById("chatMessages");
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");

    // Initially hide the chatbot.
    if (chatbot) {
        chatbot.style.display = "none";
    }

    // Scroll chatbot messages to the bottom.
    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Add a message safely without inserting HTML from users.
    function addMessage(message, sender) {
        if (!chatMessages) return;

        const messageElement = document.createElement("div");

        messageElement.className =
            sender === "user" ? "user-message" : "bot-message";

        messageElement.textContent = message;

        chatMessages.appendChild(messageElement);

        scrollToBottom();

        return messageElement;
    }

    // Open chatbot.
    window.openChatbot = function () {
        if (!chatbot) return;

        chatbot.style.display = "flex";

        if (chatInput) {
            chatInput.focus();
        }

        scrollToBottom();
    };

    // Close chatbot.
    window.closeChatbot = function () {
        if (!chatbot) return;

        chatbot.style.display = "none";
    };

    // Send a message to the Flask chatbot API.
    async function sendMessage(message) {

        try {

            const response = await fetch("/api/chat", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: message
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || data.reply || "Unable to contact the AI assistant."
                );
            }

            if (data.reply) {
                addMessage(data.reply, "bot");
            } else {
                addMessage(
                    "I couldn't generate a response. Please try again.",
                    "bot"
                );
            }

        } catch (error) {

            console.error("Chatbot error:", error);

            addMessage(
                "Sorry, something went wrong. Please try again.",
                "bot"
            );

        }
    }

    // Handle chatbot form submission.
    if (chatForm && chatInput) {

        chatForm.addEventListener("submit", async function (event) {

            event.preventDefault();

            const message = chatInput.value.trim();

            if (!message) return;

            // Display user's message.
            addMessage(message, "user");

            // Clear input.
            chatInput.value = "";

            // Disable form while waiting for response.
            const submitButton = chatForm.querySelector(
                'button[type="submit"]'
            );

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = "Sending...";
            }

            await sendMessage(message);

            // Re-enable form.
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Send";
            }

            chatInput.focus();

        });

    }

});
