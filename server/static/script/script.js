// === Настройки ===
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

    btn.classList.toggle('off', !enabled);
}

// === Работа с прочитанными ===
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

// === Очередь воспроизведения ===
let audioQueue = [];
let isPlaying = false;

function playNextInQueue() {
    if (audioQueue.length === 0) {
        isPlaying = false;
        return;
    }

    isPlaying = true;
    const { audio, filename, div } = audioQueue.shift();

    audio.play().then(() => {
        markAsRead(filename);
        div.classList.remove('unread');
        div.classList.add('read');
    }).catch(err => {
        console.warn("Не удалось воспроизвести:", err);
        playNextInQueue(); // пропустить ошибочный и продолжить
    });

    audio.addEventListener('ended', () => {
        playNextInQueue();
    }, { once: true });
}

// === Получение сообщений с сервера ===
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

    // Формируем HTML в зависимости от наличия файла
        let audioHTML = '';
        if (msg.url) {
            audioHTML = `<audio controls src="${msg.url}"></audio><br>`;
        } else {
            audioHTML = `<div class="no-audio">🔇 Аудиофайл недоступен</div>`;
        }

        div.innerHTML = `
            <p class="preview" style="cursor:pointer;">${msg.preview}</p>
            <p class="full-message" style="display:none;">${msg.full_message}</p>
            ${audioHTML}
            <span class="date">ID: ${msg.id} | Добавлено: ${msg.date} | Источник: ${msg.source || 'Неизвестно'}</span>
        `;

        container.appendChild(div);

        const previewEl = div.querySelector('.preview');
        const fullEl = div.querySelector('.full-message');
        const audio = div.querySelector('audio');

        // Раскрытие полного текста
        previewEl.addEventListener('click', () => {
            const isVisible = fullEl.style.display === 'block';
            fullEl.style.display = isVisible ? 'none' : 'block';
            previewEl.style.fontWeight = isVisible ? 'normal' : 'bold';
        });

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
    
    // Стартуем воспроизведение очереди, если ещё не начали
    if (isAutoplayEnabled() && !isPlaying) {
        playNextInQueue();
    }
}

// === SSE — Получение уведомлений о новых сообщениях ===
const eventSource = new EventSource('/events');
eventSource.onmessage = function(event) {
    if (event.data === 'new_message') {
        fetchMessages();
    }
};

// === PWA — Service Worker ===
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js')
        .then(() => console.log('✅ Service Worker зарегистрирован'))
        .catch(console.error);
}

// === Обработка кнопки ===
document.getElementById('autoplay-toggle').addEventListener('click', toggleAutoplay);

// === Первая загрузка ===
updateAutoplayButton();
fetchMessages();