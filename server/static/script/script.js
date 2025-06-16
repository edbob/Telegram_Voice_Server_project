// Получаем статус автопрослушивания
function isAutoplayEnabled() {
    return localStorage.getItem('autoplayEnabled') !== 'false'; // по умолчанию включено
}

function toggleAutoplay() {
    const current = isAutoplayEnabled();
    localStorage.setItem('autoplayEnabled', (!current).toString());
    updateAutoplayButton();
}

function updateAutoplayButton() {
    const btn = document.getElementById('autoplay-toggle');
    const enabled = isAutoplayEnabled();

    btn.textContent = enabled
        ? '🔊 Автопрослушивание: ВКЛ'
        : '🔇 Автопрослушивание: ВЫКЛ';

    // Добавим/удалим класс 'off' для изменения внешнего вида кнопки
    btn.classList.toggle('off', !enabled);
}

// Работа с прочитанными
function getReadMessages() {
    const stored = localStorage.getItem('readMessages');
    return stored ? JSON.parse(stored) : [];
}

function markAsRead(filename) {
    const read = getReadMessages();
    if (!read.includes(filename)) {
        read.push(filename);
        localStorage.setItem('readMessages', JSON.stringify(read));
    }
}

async function fetchMessages() {
    const res = await fetch('/api/messages');
    const data = await res.json();

    const container = document.getElementById('messages');
    container.innerHTML = '';

    const readMessages = getReadMessages();

    data.forEach((msg, index) => {
        const isRead = readMessages.includes(msg.filename);

        const div = document.createElement('div');
        div.className = 'message ' + (isRead ? 'read' : 'unread');

        div.innerHTML = `
            <audio controls src="${msg.url}"></audio><br>
            <span class="date">Добавлено: ${msg.date} | Источник: ${msg.source || 'Неизвестно'}</span>
        `;

        container.appendChild(div);

        const audio = div.querySelector('audio');

        // Автовоспроизведение первого непрочитанного
        if (index === 0 && !isRead && isAutoplayEnabled()) {
            audio.play().then(() => {
                markAsRead(msg.filename);
                div.classList.remove('unread');
                div.classList.add('read');
            }).catch(err => {
                console.warn("Не удалось воспроизвести:", err);
            });
        }

        // Ручное воспроизведение
        audio.addEventListener('play', () => {
            if (!readMessages.includes(msg.filename)) {
                markAsRead(msg.filename);
                div.classList.remove('unread');
                div.classList.add('read');
            }
        });
    });
}

// SSE
const eventSource = new EventSource('/events');
eventSource.onmessage = function(event) {
    if (event.data === 'new_message') {
        fetchMessages();
    }
};

// Обработка кнопки
document.getElementById('autoplay-toggle').addEventListener('click', toggleAutoplay);

// Первая загрузка
updateAutoplayButton();
fetchMessages();