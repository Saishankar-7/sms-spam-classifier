document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predict-form');
    const button = form.querySelector('.glow-button');
    const buttonText = button.querySelector('.button-text');
    const spinner = button.querySelector('.spinner');
    
    const resultContainer = document.getElementById('result-container');
    const resultIcon = document.getElementById('result-icon');
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI Loading State
        button.disabled = true;
        buttonText.textContent = 'Analyzing...';
        spinner.style.display = 'block';
        resultContainer.classList.add('hidden');
        
        const text = document.getElementById('sms-text').value;

        try {
            const formData = new FormData();
            formData.append('text', text);

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Update UI with result
            resultContainer.classList.remove('hidden', 'is-spam', 'is-ham');
            
            if (data.result === 'Spam') {
                resultContainer.classList.add('is-spam');
                resultIcon.textContent = '🚨';
                resultTitle.textContent = 'Scam / Spam Detected';
                resultMessage.textContent = 'Caution! This message is classified as dangerous.';
            } else {
                resultContainer.classList.add('is-ham');
                resultIcon.textContent = '✅';
                resultTitle.textContent = 'Safe Message';
                resultMessage.textContent = 'This message appears to be normal (Ham).';
            }

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while analyzing the message. Please ensure the server is running properly.');
        } finally {
            // Restore UI state
            button.disabled = false;
            buttonText.textContent = 'Analyze Message';
            spinner.style.display = 'none';
        }
    });

    // Auto-resize textarea
    const textarea = document.getElementById('sms-text');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});
