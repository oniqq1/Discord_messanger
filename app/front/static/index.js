document.addEventListener('DOMContentLoaded', function() {
    let lastScrollTop = 0;
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        lastScrollTop = scrollTop;
    });

    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });

    const channelItems = document.querySelectorAll('.channel-item');
    channelItems.forEach(item => {
        item.addEventListener('click', function() {
            channelItems.forEach(ch => ch.classList.remove('active'));
            this.classList.add('active');
            const chatHeader = document.querySelector('.chat-header h3');
            if (chatHeader && this.textContent.trim()) {
                chatHeader.textContent = this.textContent.trim();
            }
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.innerHTML = `
                    <div class="message">
                        <div class="message-avatar">S</div>
                        <div class="message-content">
                            <div class="message-header">
                                <span class="username">System</span>
                                <span class="timestamp">Сейчас</span>
                            </div>
                            <div class="message-text">Добро пожаловать в канал ${this.textContent.trim()}! 🎉</div>
                        </div>
                    </div>
                `;
            }
        });
    });

    const serverItems = document.querySelectorAll('.server-item');
    serverItems.forEach(item => {
        item.addEventListener('click', function() {
            serverItems.forEach(server => server.classList.remove('active'));
            this.classList.add('active');
        });
    });

    function createMobileToggle() {
        if (window.innerWidth <= 480) {
            const chatHeader = document.querySelector('.chat-header');
            if (chatHeader && !chatHeader.querySelector('.mobile-toggle')) {
                const toggleBtn = document.createElement('button');
                toggleBtn.className = 'mobile-toggle control-btn';
                toggleBtn.innerHTML = '☰';
                toggleBtn.addEventListener('click', function() {
                    const sidebar = document.querySelector('.chat-sidebar');
                    sidebar.classList.toggle('open');
                });
                chatHeader.insertBefore(toggleBtn, chatHeader.firstChild);
            }
        }
    }
    createMobileToggle();
    window.addEventListener('resize', createMobileToggle);

    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#8b5cf6'};
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    };

    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .form-group.focused label {
            color: #8b5cf6;
            transform: translateY(-2px);
        }
        .message:hover {
            background: rgba(139, 92, 246, 0.05);
            border-radius: 8px;
        }
        .channel-item:hover {
            transform: translateX(5px);
        }
        .user-item:hover {
            background: rgba(139, 92, 246, 0.1);
            border-radius: 5px;
        }
    `;
    document.head.appendChild(style);

    const addRoomBtn = document.getElementById('addRoomBtn');
    const roomModal = document.getElementById('roomModal');
    const closeModal = document.getElementById('closeModal');
    const joinRoomBtn = document.getElementById('joinRoomBtn');
    const roomInput = document.getElementById('roomInput');

    if (addRoomBtn && roomModal && closeModal && joinRoomBtn && roomInput) {
        addRoomBtn.addEventListener('click', () => {
            roomModal.style.display = 'flex';
            roomInput.value = '';
            roomInput.focus();
        });
        closeModal.addEventListener('click', () => {
            roomModal.style.display = 'none';
        });
        roomModal.addEventListener('click', (e) => {
            if (e.target === roomModal) roomModal.style.display = 'none';
        });
        joinRoomBtn.addEventListener('click', () => {
            const room = roomInput.value.trim();
            if (room) {
                joinRoom(room);
                roomModal.style.display = 'none';
            }
        });
        roomInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') joinRoomBtn.click();
        });
    }

    window.onload = function() {
        const params = new URLSearchParams(window.location.search);
        const roomFromUrl = params.get('room');
        if (roomFromUrl) {
            currentRoom = roomFromUrl;
        }
        joinRoom(currentRoom);
    };
});