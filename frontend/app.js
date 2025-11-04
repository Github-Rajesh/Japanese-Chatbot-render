// API Configuration
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : '/api';  // Use /api prefix in production with reverse proxy

class ChatApp {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        
        this.isProcessing = false;
        this.messages = [];
        
        this.init();
    }
    
    init() {
        // Auto-resize textarea
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = this.userInput.scrollHeight + 'px';
        });
        
        // Send on Enter (Shift+Enter for new line)
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
    }
    
    async sendMessage() {
        const query = this.userInput.value.trim();
        
        if (!query || this.isProcessing) return;
        
        // Add user message
        this.addMessage('user', query);
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        
        // Remove welcome message if exists
        const welcomeMsg = this.chatContainer.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        // Set processing state
        this.isProcessing = true;
        this.sendButton.disabled = true;
        
        // Add loading indicator
        const loadingElement = this.addLoadingMessage();
        
        try {
            // Stream response
            await this.streamResponse(query, loadingElement);
        } catch (error) {
            console.error('Error:', error);
            loadingElement.remove();
            this.addMessage('assistant', 'エラーが発生しました。もう一度お試しください。');
        } finally {
            this.isProcessing = false;
            this.sendButton.disabled = false;
        }
    }
    
    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = this.formatMessage(content);
        
        messageDiv.appendChild(contentDiv);
        this.chatContainer.appendChild(messageDiv);
        
        this.scrollToBottom();
        
        return contentDiv;
    }
    
    formatMessage(text) {
        if (!text) return '';
        
        // Escape HTML to prevent XSS, then process formatting
        const escapeHtml = (str) => {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        };
        
        // First, escape the text
        let formatted = escapeHtml(text);
        
        // Convert numbered lists (e.g., "1.**Topic**: description")
        // Pattern: number followed by period, optional space, optional bold text, colon
        // Match until next number pattern or end of string
        formatted = formatted.replace(/(\d+)\.\s*\*\*([^*]+)\*\*:([^0-9]*?)(?=\d+\.|$)/g, '<li><strong>$2</strong><span class="list-description">$3</span></li>');
        
        // Also handle numbered lists without bold (e.g., "1. Topic: description")
        // Only match if it doesn't contain ** (already processed above) and doesn't contain <li> (already converted)
        formatted = formatted.replace(/(\d+)\.\s*([^:]+):([^0-9]*?)(?=\d+\.|$)/g, (match, num, title, desc) => {
            // Skip if already converted to HTML or contains bold markdown (double asterisks)
            if (match.includes('<li>') || match.includes('**')) {
                return match;
            }
            return `<li><strong>${title}</strong><span class="list-description">${desc}</span></li>`;
        });
        
        // Wrap consecutive list items in <ol> tags
        formatted = formatted.replace(/(<li>.*?<\/li>(?:\s*<li>.*?<\/li>)*)/g, '<ol>$1</ol>');
        
        // Convert bold markdown (**text**)
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks to <br> tags
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Split by double line breaks to create paragraphs
        const paragraphs = formatted.split('<br><br>');
        formatted = paragraphs.map(p => {
            // If paragraph contains list, don't wrap in <p>
            if (p.includes('<ol>') || p.includes('<li>')) {
                return p;
            }
            // Otherwise wrap in <p> tag
            return p.trim() ? `<p>${p}</p>` : '';
        }).join('');
        
        return formatted;
    }
    
    updateFormattedContent(element, newText) {
        // Format the entire accumulated text
        element.innerHTML = this.formatMessage(newText);
    }
    
    addLoadingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-assistant';
        
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message-loading';
        loadingDiv.innerHTML = `
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        `;
        
        messageDiv.appendChild(loadingDiv);
        this.chatContainer.appendChild(messageDiv);
        
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    async streamResponse(query, loadingElement) {
        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    stream: true
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Remove loading indicator
            loadingElement.remove();
            
            // Create message element for streaming content
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message message-assistant';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = '';
            
            messageDiv.appendChild(contentDiv);
            this.chatContainer.appendChild(messageDiv);
            
            // Accumulate text for streaming
            let accumulatedText = '';
            
            // Read stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        
                        if (data === '[DONE]') {
                            break;
                        }
                        
                        try {
                            const parsed = JSON.parse(data);
                            if (parsed.text) {
                                accumulatedText += parsed.text;
                                // Update formatted content
                                this.updateFormattedContent(contentDiv, accumulatedText);
                                this.scrollToBottom();
                            }
                        } catch (e) {
                            // Skip invalid JSON
                        }
                    }
                }
            }
            
        } catch (error) {
            console.error('Streaming error:', error);
            throw error;
        }
    }
    
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

