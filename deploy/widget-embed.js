/**
 * Crelec Blower Selection Widget Embed Script
 * This script creates a floating chat widget on the customer's website
 */

(function() {
    'use strict';

    // Configuration
    const WIDGET_URL = 'https://blower-chatbot-n3h6j556t-brphobostgmailcoms-projects.vercel.app'; // Your Vercel URL
    const WIDGET_POSITION = 'bottom-right'; // Options: bottom-right, bottom-left

    // Create widget container
    function createWidget() {
        // Create main container
        const container = document.createElement('div');
        container.id = 'crelec-chat-widget';
        container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 99999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;

        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.id = 'crelec-toggle-btn';
        toggleButton.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
            </svg>
            <span style="margin-left: 8px;">Get Blower Quote</span>
        `;
        toggleButton.style.cssText = `
            background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
            color: white;
            border: none;
            border-radius: 30px;
            padding: 15px 25px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,102,204,0.3);
            display: flex;
            align-items: center;
            transition: all 0.3s ease;
        `;

        toggleButton.onmouseover = function() {
            this.style.transform = 'scale(1.05)';
            this.style.boxShadow = '0 6px 20px rgba(0,102,204,0.4)';
        };

        toggleButton.onmouseout = function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 4px 15px rgba(0,102,204,0.3)';
        };

        // Create chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'crelec-chat-window';
        chatWindow.style.cssText = `
            display: none;
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 400px;
            height: 600px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            overflow: hidden;
            transition: all 0.3s ease;
        `;

        // Create header for chat window
        const chatHeader = document.createElement('div');
        chatHeader.style.cssText = `
            background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;
        chatHeader.innerHTML = `
            <div style="display: flex; align-items: center;">
                <img src="${WIDGET_URL}/assets/crelec.png" style="height: 25px; margin-right: 10px; filter: brightness(0) invert(1);">
                <span style="font-weight: 500;">Blower Assistant</span>
            </div>
            <button id="crelec-close-btn" style="background: none; border: none; color: white; font-size: 24px; cursor: pointer; padding: 0; width: 30px; height: 30px;">×</button>
        `;

        // Create iframe for chat interface
        const iframe = document.createElement('iframe');
        iframe.src = `${WIDGET_URL}/widget.html`;
        iframe.style.cssText = `
            width: 100%;
            height: calc(100% - 50px);
            border: none;
        `;

        // Assemble widget
        chatWindow.appendChild(chatHeader);
        chatWindow.appendChild(iframe);
        container.appendChild(toggleButton);
        container.appendChild(chatWindow);

        // Add to page
        document.body.appendChild(container);

        // Set up event handlers
        let isOpen = false;

        toggleButton.onclick = function() {
            isOpen = !isOpen;
            if (isOpen) {
                chatWindow.style.display = 'block';
                toggleButton.style.display = 'none';
                // Animate opening
                setTimeout(() => {
                    chatWindow.style.transform = 'translateY(0)';
                    chatWindow.style.opacity = '1';
                }, 10);
            }
        };

        // Close button handler
        setTimeout(() => {
            const closeBtn = document.getElementById('crelec-close-btn');
            if (closeBtn) {
                closeBtn.onclick = function() {
                    isOpen = false;
                    chatWindow.style.transform = 'translateY(20px)';
                    chatWindow.style.opacity = '0';
                    setTimeout(() => {
                        chatWindow.style.display = 'none';
                        toggleButton.style.display = 'flex';
                    }, 300);
                };
            }
        }, 100);

        // Handle responsive design
        function adjustForMobile() {
            if (window.innerWidth < 500) {
                chatWindow.style.width = '100%';
                chatWindow.style.height = '100%';
                chatWindow.style.bottom = '0';
                chatWindow.style.right = '0';
                chatWindow.style.left = '0';
                chatWindow.style.borderRadius = '0';
            } else {
                chatWindow.style.width = '400px';
                chatWindow.style.height = '600px';
                chatWindow.style.bottom = '80px';
                chatWindow.style.right = '20px';
                chatWindow.style.left = 'auto';
                chatWindow.style.borderRadius = '15px';
            }
        }

        window.addEventListener('resize', adjustForMobile);
        adjustForMobile();
    }

    // Initialize widget when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createWidget);
    } else {
        createWidget();
    }
})();