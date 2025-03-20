document.addEventListener("DOMContentLoaded", function () {
    // Add this inside the DOMContentLoaded event listener
document.getElementById("forwardBtn").addEventListener("click", function() {
    showForwardOptions();
});

    const username = localStorage.getItem("username");
    const usersList = document.getElementById("active-users");
    const chatBox = document.getElementById("chatBox");
    const messageInput = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");
    let selectedUser = null;
    let selectedMessageId = null;

    if (!username) {
        alert("Please log in first.");
        window.location.href = "login.html";
        return;
    }

    document.getElementById("username").innerText = username;

    function fetchActiveUsers() {
        fetch("http://127.0.0.1:5000/active-users")
            .then(response => response.json())
            .then(users => {
                usersList.innerHTML = "";
                users.forEach(user => {
                    if (user !== username) {
                        let li = document.createElement("li");
                        li.innerText = user;
                        li.classList.add("user-item");
                        li.onclick = () => startChat(user);
                        usersList.appendChild(li);
                    }
                });
            })
            .catch(err => console.error("Error loading active users:", err));
    }

    function startChat(user) {
        selectedUser = user;
        document.getElementById("chatHeader").innerText = `Chatting with: ${user}`;
        chatBox.innerHTML = `<h4>Chat with ${user}</h4>`;
        fetchMessages();
    }

    function fetchMessages() {
        if (!selectedUser) return;
        fetch(`http://127.0.0.1:5001/get-messages/${username}`)
            .then(response => response.json())
            .then(messages => {
                chatBox.innerHTML = ""; 
                messages.forEach(msg => {
                    if ((msg.sender === username && msg.receiver === selectedUser) ||
                        (msg.sender === selectedUser && msg.receiver === username)) {
    
                        let messageElement = document.createElement("p");
                        messageElement.classList.add("chat-message");
                        messageElement.setAttribute("data-message-id", msg.message_id);
                        messageElement.innerHTML = `<strong>${msg.sender}:</strong> ${msg.decrypted_message} <br>
                                                    <span class="encrypted-text">(Encrypted: ${msg.encrypted_message})</span>`;
                        
                        messageElement.onclick = function () {
                            selectMessage(msg.message_id, messageElement);
                        };

                        chatBox.appendChild(messageElement);
                    }
                });
            })
            .catch(err => console.error("Error loading messages:", err));
    }


    function selectMessage(messageId, messageElement) {
        document.querySelectorAll(".chat-message").forEach(msg => msg.classList.remove("selected-message"));
        messageElement.classList.add("selected-message");
        selectedMessageId = messageId;
        document.getElementById("forwardBtn").style.display = "block";
    }

    function showForwardOptions() {
        // Show a loading state
        const forwardBtn = document.getElementById("forwardBtn");
        forwardBtn.innerText = "Loading users...";
        forwardBtn.disabled = true;
        
        fetch("http://127.0.0.1:5000/active-users")
            .then(response => response.json())
            .then(users => {
                // Reset button state
                forwardBtn.innerText = "🔄 Forward";
                forwardBtn.disabled = false;
                
                // Filter out current user and chat partner
                const eligibleUsers = users.filter(user => 
                    user !== username && user !== selectedUser);
                    
                if (eligibleUsers.length === 0) {
                    alert("No other active users available to forward to.");
                    return;
                }
                
                // Create a modal for user selection instead of using prompt
                const modalHTML = `
                    <div id="forwardModal" class="forward-modal">
                        <div class="forward-modal-content">
                            <span class="close-modal">&times;</span>
                            <h3>Forward Message</h3>
                            <p>Select a user to forward this message to:</p>
                            <ul class="forward-user-list">
                                ${eligibleUsers.map(user => 
                                    `<li data-username="${user}">${user}</li>`
                                ).join('')}
                            </ul>
                        </div>
                    </div>
                `;
                
                // Add modal to the DOM
                const modalContainer = document.createElement("div");
                modalContainer.innerHTML = modalHTML;
                document.body.appendChild(modalContainer);
                
                // Show the modal
                const modal = document.getElementById("forwardModal");
                modal.style.display = "block";
                
                // Handle close button
                const closeBtn = document.querySelector(".close-modal");
                closeBtn.onclick = function() {
                    modal.style.display = "none";
                    document.body.removeChild(modalContainer);
                };
                
                // Handle user selection
                const userList = document.querySelectorAll(".forward-user-list li");
                userList.forEach(userItem => {
                    userItem.onclick = function() {
                        const newRecipient = this.getAttribute("data-username");
                        modal.style.display = "none";
                        document.body.removeChild(modalContainer);
                        forwardMessage(newRecipient);
                    };
                });
            })
            .catch(err => {
                console.error("Error fetching users:", err);
                forwardBtn.innerText = "🔄 Forward";
                forwardBtn.disabled = false;
                alert("Error loading users. Please try again.");
            });
    }

    // This function would be added to display forwarded messages differently
    function appendMessage(msg) {
        let messageElement = document.createElement("p");
        messageElement.classList.add("chat-message");
        messageElement.setAttribute("data-message-id", msg.message_id);
        
        // Check if the message is forwarded
        const isForwarded = msg.decrypted_message.startsWith("[Forwarded from");
        
        if (isForwarded) {
            // Extract original sender from forwarded message
            const originalSender = msg.decrypted_message.match(/\[Forwarded from (.*?)\]/)[1];
            const actualMessage = msg.decrypted_message.replace(/\[Forwarded from .*?\]/, "").trim();
            
            messageElement.innerHTML = `
                <div class="forwarded-message">
                    <div class="forwarded-header">
                        <i class="fas fa-share"></i> Forwarded from <strong>${originalSender}</strong>
                    </div>
                    <div class="message-content">
                        <strong>${msg.sender}:</strong> ${actualMessage || msg.decrypted_message}
                    </div>
                    <span class="encrypted-text">(Encrypted: ${msg.encrypted_message})</span>
                </div>
            `;
        } else {
            messageElement.innerHTML = `<strong>${msg.sender}:</strong> ${msg.decrypted_message} <br>
                                        <span class="encrypted-text">(Encrypted: ${msg.encrypted_message})</span>`;
        }
        
        messageElement.onclick = function() {
            selectMessage(msg.message_id, messageElement);
        };

        chatBox.appendChild(messageElement);
    }

    function forwardMessage(newRecipient) {
        if (!selectedMessageId) {
            alert("Please select a message first!");
            return;
        }
    
        // Show a loading indicator
        let originalButtonText = document.getElementById("forwardBtn").innerText;
        document.getElementById("forwardBtn").innerText = "Forwarding...";
        document.getElementById("forwardBtn").disabled = true;
    
        fetch("http://127.0.0.1:5001/re-encrypt-message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                sender: username, 
                original_receiver: selectedUser, 
                new_receiver: newRecipient, 
                message_id: selectedMessageId 
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(result => {
            alert(`Message forwarded to ${newRecipient}`);
            selectedMessageId = null;
            document.querySelectorAll(".chat-message").forEach(msg => 
                msg.classList.remove("selected-message"));
            document.getElementById("forwardBtn").style.display = "none";
        })
        .catch(err => {
            console.error("Error forwarding message:", err);
            alert("Error forwarding message: " + err.message);
        })
        .finally(() => {
            // Reset the button
            document.getElementById("forwardBtn").innerText = originalButtonText;
            document.getElementById("forwardBtn").disabled = false;
        });
    }

    sendBtn.addEventListener("click", function () {
        if (!selectedUser) {
            alert("Select a user to chat with first.");
            return;
        }

        let message = messageInput.value.trim();
        if (!message) return;

        fetch("http://127.0.0.1:5001/send-message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sender: username, receiver: selectedUser, message })
        })
        .then(response => response.json())
        .then(() => {
            messageInput.value = "";
            fetchMessages();
        })
        .catch(err => console.error("Error sending message:", err));
    });

    fetchActiveUsers();
    setInterval(fetchActiveUsers, 5000);
    setInterval(fetchMessages, 3000);
});

