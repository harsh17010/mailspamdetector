document.getElementById('checkBtn').addEventListener('click', async () => {
    const textInput = document.getElementById('emailText').value;
    const resultBox = document.getElementById('resultBox');
    const resultTitle = document.getElementById('resultTitle');
    const resultConfidence = document.getElementById('resultConfidence');
    const resultReason = document.getElementById('resultReason');

    if (!textInput.trim()) {
        alert("Please type or paste some text first!");
        return;
    }

    resultBox.classList.add('hidden');

    try {
        // Use localhost for the backend connection.
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: textInput })
        });

        const data = await response.json();

        resultBox.classList.remove('hidden', 'spam', 'safe');

        if (data.is_spam) {
            resultBox.classList.add('spam');
            resultTitle.innerText = "🚨 Alert: Phishing / Spam Detected!";
            resultTitle.style.color = "#dc3545";
        } else {
            resultBox.classList.add('safe');
            resultTitle.innerText = "✅ Safe: Legitimate Message detected";
            resultTitle.style.color = "#28a745";
        }

        resultConfidence.innerText = data.confidence;
        resultReason.innerText = data.reason;

    } catch (error) {
        alert("Error connecting to the backend server. Please make sure the Flask server is running.");
    }
});
