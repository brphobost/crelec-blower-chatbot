/**
 * Crelec Blower Selection Chat Interface
 * Handles user interaction and API communication
 */

class BlowerChat {
    constructor() {
        // API configuration - Works for both local and production
        this.apiUrl = window.location.hostname === 'localhost'
            ? 'http://localhost:8000'
            : '';

        // Generate or retrieve session ID
        this.sessionId = this.getSessionId();

        // DOM elements
        this.messagesContainer = document.getElementById('chat-messages');
        this.inputField = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');

        // Initialize quote generator
        this.quoteGenerator = null;
        try {
            this.quoteGenerator = new QuoteGenerator();
        } catch (e) {
            console.log('Quote generator not available:', e);
        }

        // Initialize
        this.init();
    }

    init() {
        // Set up event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Quick action buttons
        document.querySelectorAll('.quick-action').forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleQuickAction(e.target.dataset.action);
            });
        });

        // Send initial greeting
        this.addMessage('bot',
            "Hi! I'll help you select the right blower for your needs. " +
            "Let's start with your tank dimensions. " +
            "Please enter the length, width, and height in meters (e.g., '6 3 2'):"
        );

        // Focus input
        this.inputField.focus();
    }

    getSessionId() {
        // Check if session exists in localStorage
        let sessionId = localStorage.getItem('blower_chat_session');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('blower_chat_session', sessionId);
        }
        return sessionId;
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);

        // Clear input
        this.inputField.value = '';
        this.inputField.focus();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to API
            const response = await fetch(`${this.apiUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message,
                    context: {}
                })
            });

            const data = await response.json();

            // Remove typing indicator
            this.hideTypingIndicator();

            // Add bot response
            this.addMessage('bot', data.message);

            // If we need to send email with quote
            if (data.send_email && data.email_data) {
                this.handleQuoteGeneration(data.email_data);
            }

            // If calculation is complete, show results (legacy)
            if (data.calculation && data.products && !data.send_email) {
                this.showResults(data.calculation, data.products, data.quote_id);
            }

        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.addMessage('bot',
                'Sorry, I encountered an error. Please try again or contact support.'
            );
        }
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        // Process text for better formatting
        if (sender === 'bot') {
            text = this.formatBotMessage(text);
        }

        messageDiv.innerHTML = text;

        // Add timestamp
        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        messageDiv.appendChild(timestamp);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatBotMessage(text) {
        // Convert escaped newlines (\n) to HTML breaks
        text = text.replace(/\\n/g, '<br>');

        // Convert markdown-style formatting
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Keep emoji support
        text = text.replace(/✅/g, '✅');
        text = text.replace(/📧/g, '📧');

        // Convert numbered lists (already has line break)
        text = text.replace(/^(\d+)\.\s/gm, '$1. ');

        return text;
    }

    showResults(calculation, products, quoteId) {
        const results = calculation.results;

        // Create results card
        const resultCard = document.createElement('div');
        resultCard.className = 'result-card';

        let html = `
            <h3>📊 Calculation Results</h3>
            <p><strong>Quote ID:</strong> ${quoteId}</p>
            <div class="specs">
                <p>📐 Tank Volume: ${results.tank_volume} m³</p>
                <p>💨 Required Airflow: ${results.airflow_required} m³/hr</p>
                <p>🎯 Required Pressure: ${results.pressure_required} mbar</p>
                <p>⚡ Estimated Power: ${results.power_estimate} kW</p>
            </div>
        `;

        if (products && products.length > 0) {
            html += '<h3>🔧 Recommended Products</h3>';

            products.forEach((product, index) => {
                const stockClass = product.stock === 'In Stock' ? 'in-stock' : 'delivery';
                html += `
                    <div class="product-item">
                        <div class="model">${index + 1}. ${product.model}</div>
                        <div class="specs">
                            Power: ${product.power} kW | Price: ${product.price}
                        </div>
                        <span class="stock ${stockClass}">${product.stock}</span>
                    </div>
                `;
            });
        }

        html += `
            <div style="margin-top: 15px;">
                <button onclick="blowerChat.downloadQuote('${quoteId}')"
                        style="padding: 8px 15px; background: #0066cc; color: white;
                               border: none; border-radius: 5px; cursor: pointer;">
                    Download Quote PDF
                </button>
            </div>
        `;

        resultCard.innerHTML = html;
        this.messagesContainer.appendChild(resultCard);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message bot typing-indicator';
        indicator.innerHTML = '<div class="loading"></div> Thinking...';
        indicator.id = 'typing-indicator';
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    handleQuickAction(action) {
        switch(action) {
            case 'new':
                // Reset session and start new calculation
                this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('blower_chat_session', this.sessionId);
                this.messagesContainer.innerHTML = '';
                this.addMessage('bot',
                    "Starting a new calculation. " +
                    "Please enter your tank dimensions in meters (length width height):"
                );
                break;

            case 'help':
                this.addMessage('user', 'I need help');
                this.addMessage('bot',
                    "I can help you with:\n" +
                    "• Calculating blower requirements\n" +
                    "• Understanding specifications\n" +
                    "• Product recommendations\n" +
                    "• Getting quotes\n\n" +
                    "For immediate assistance, contact:\n" +
                    "📞 Phone: +27 (0) 12 345 6789\n" +
                    "📧 Email: support@crelec.co.za"
                );
                break;
        }
    }

    async handleQuoteGeneration(emailData) {
        if (!this.quoteGenerator) {
            // Fallback if quote generator not available
            console.error('Quote generator not initialized');
            this.addMessage('bot',
                '⚠️ PDF generation is temporarily unavailable. ' +
                'Please contact crelec@live.co.za directly with quote #' + emailData.quote_id
            );
            return;
        }

        try {
            // Generate PDF but DON'T download automatically
            const pdf = this.quoteGenerator.generatePDF(emailData);

            // Store PDF for email but don't download
            this.lastGeneratedPDF = pdf;

            // Show success message without mentioning download
            this.addMessage('bot',
                '✅ **Quote Generated Successfully!**\n\n' +
                'We\'re sending your detailed quote to your email address.'
            );

            // Try to send email via API
            this.sendQuoteEmail(emailData);

            // Save quote to database
            this.saveQuoteToDatabase(emailData);

        } catch (error) {
            console.error('Error generating quote:', error);
            this.addMessage('bot',
                '❌ Error generating quote. Please contact support at crelec@live.co.za'
            );
        }
    }

    async sendQuoteEmail(emailData) {
        try {
            // Use the already generated PDF
            const pdf = this.lastGeneratedPDF || this.quoteGenerator.generatePDF(emailData);
            const pdfBlob = pdf.output('blob');
            const pdfBase64 = await this.blobToBase64(pdfBlob);

            // Send email via our API
            const response = await fetch('/api/send_email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    to_email: emailData.customer_data.email,
                    quote_id: emailData.quote_id,
                    customer_data: emailData.customer_data,
                    calculation: emailData.calculation,
                    products: emailData.products,
                    pdf_attachment: pdfBase64
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.addMessage('bot',
                    `📧 We're processing your email to ${emailData.customer_data.email}. ` +
                    `A copy will also be sent to our sales team.`
                );
            }
        } catch (error) {
            console.error('Error sending email:', error);
            // Silently fail - PDF download is the primary method
        }
    }

    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    async saveQuoteToDatabase(emailData) {
        try {
            // Add session ID to the data
            emailData.session_id = this.getSessionId();

            // Save to flexible logger (adapts to any data structure)
            const response = await fetch('/api/flexible_logger', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(emailData)
            });

            const result = await response.json();
            console.log('Quote saved:', result);

            // Optionally save to Google Sheets if configured
            fetch('/api/sheets_storage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(emailData)
            }).catch(err => console.log('Sheets logging failed:', err));

        } catch (error) {
            console.error('Error saving quote:', error);
            // Don't show error to user - this is background logging
        }
    }

    async downloadQuote(quoteId) {
        // This function can be used for downloading existing quotes
        console.log('Downloading quote:', quoteId);
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.blowerChat = new BlowerChat();
});