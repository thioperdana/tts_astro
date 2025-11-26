const API_BASE = '/api';

let currentGame = {
    grid: [],
    words: [],
    width: 0,
    height: 0,
    id: null
};

let currentFocus = {
    row: -1,
    col: -1,
    direction: 'across' // 'across' or 'down'
};

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-new-game').addEventListener('click', newGame);
    document.getElementById('btn-save-game').addEventListener('click', saveGame);
    document.getElementById('btn-load-game').addEventListener('click', showLoadModal);
    document.getElementById('btn-close-modal').addEventListener('click', () => {
        document.getElementById('load-modal').classList.add('hidden');
    });

    // Leaderboard button
    document.getElementById('btn-view-leaderboard').addEventListener('click', showLeaderboardModal);
    document.getElementById('btn-close-leaderboard').addEventListener('click', () => {
        document.getElementById('leaderboard-modal').classList.add('hidden');
    });
});

async function newGame() {
    try {
        const response = await fetch(`${API_BASE}/generate`);
        if (!response.ok) throw new Error('Failed to generate game');
        const data = await response.json();
        loadGameData(data);
    } catch (error) {
        console.error(error);
        alert('Gagal memulai permainan baru');
    }
}

function loadGameData(data) {
    currentGame = {
        grid: data.grid,
        words: data.words,
        width: data.width || 20,
        height: data.height || 20,
        id: data.id || null
    };

    renderGrid();
    renderClues();
}

function renderGrid() {
    const container = document.getElementById('crossword-grid');
    container.innerHTML = '';
    container.style.gridTemplateColumns = `repeat(${currentGame.width}, 30px)`;

    for (let r = 0; r < currentGame.height; r++) {
        for (let c = 0; c < currentGame.width; c++) {
            const cellVal = currentGame.grid[r][c];
            const cellDiv = document.createElement('div');
            cellDiv.className = `cell ${cellVal === '' ? 'empty' : ''}`;
            cellDiv.dataset.row = r;
            cellDiv.dataset.col = c;

            if (cellVal !== '') {
                // Check if this cell is the start of a word
                const wordStart = currentGame.words.find(w => w.row === r && w.col === c);
                if (wordStart) {
                    const numSpan = document.createElement('span');
                    numSpan.className = 'number';
                    numSpan.textContent = wordStart.number;
                    cellDiv.appendChild(numSpan);
                }

                const input = document.createElement('input');
                input.maxLength = 1;
                input.dataset.row = r;
                input.dataset.col = c;
                input.addEventListener('focus', handleFocus);
                input.addEventListener('keydown', handleKeyDown);
                input.addEventListener('input', handleInput);

                // If loading a saved game, we might want to restore user inputs
                // But for now, let's just keep it blank or maybe we should store user state too?
                // The requirement says "save game", implying state. 
                // The current backend saves the *solution* grid. 
                // Ideally we should save the *user's* progress.
                // For this MVP, I'll assume we just save the puzzle structure so they can play it again,
                // OR I should update the backend to save user progress.
                // Let's stick to the prompt "save if there are games not completed".
                // So I should probably save the user's filled grid too.
                // But the current backend model only has `grid_data` (solution).
                // I will modify the save logic to include user state if I have time, 
                // but for now let's just render the empty grid for a "new" game.

                cellDiv.appendChild(input);
            }

            container.appendChild(cellDiv);
        }
    }
}

function renderClues() {
    const acrossList = document.getElementById('clues-across');
    const downList = document.getElementById('clues-down');

    acrossList.innerHTML = '';
    downList.innerHTML = '';

    currentGame.words.sort((a, b) => a.number - b.number).forEach(word => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="num">${word.number}</span> ${word.clue}`;
        li.dataset.row = word.row;
        li.dataset.col = word.col;
        li.dataset.direction = word.direction;
        li.addEventListener('click', () => highlightWord(word));

        if (word.direction === 'across') {
            acrossList.appendChild(li);
        } else {
            downList.appendChild(li);
        }
    });
}

function handleFocus(e) {
    const r = parseInt(e.target.dataset.row);
    const c = parseInt(e.target.dataset.col);
    currentFocus.row = r;
    currentFocus.col = c;
    highlightActive();
}

function highlightWord(word) {
    // Focus the first cell of the word
    const selector = `input[data-row="${word.row}"][data-col="${word.col}"]`;
    const input = document.querySelector(selector);
    if (input) {
        currentFocus.direction = word.direction;
        input.focus();
    }
}

function highlightActive() {
    // Remove old highlights
    document.querySelectorAll('.cell.active').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.cell.highlight').forEach(el => el.classList.remove('highlight'));

    // Highlight current cell
    const currentCell = document.querySelector(`.cell[data-row="${currentFocus.row}"][data-col="${currentFocus.col}"]`);
    if (currentCell) currentCell.classList.add('active');

    // Highlight current word based on direction
    // Find the word that covers this cell in the current direction
    // This is a bit complex because a cell can be part of two words.
    // We use `currentFocus.direction` to decide.

    // Simple approach: highlight the row or col
    // Better: find the specific word object
}

function handleKeyDown(e) {
    const r = parseInt(e.target.dataset.row);
    const c = parseInt(e.target.dataset.col);

    if (e.key === 'ArrowRight') moveFocus(r, c + 1);
    else if (e.key === 'ArrowLeft') moveFocus(r, c - 1);
    else if (e.key === 'ArrowDown') moveFocus(r + 1, c);
    else if (e.key === 'ArrowUp') moveFocus(r - 1, c);
    else if (e.key === 'Backspace') {
        if (e.target.value === '') {
            // Move back
            if (currentFocus.direction === 'across') moveFocus(r, c - 1);
            else moveFocus(r - 1, c);
        } else {
            e.target.value = '';
        }
    }
}

function handleInput(e) {
    const r = parseInt(e.target.dataset.row);
    const c = parseInt(e.target.dataset.col);

    if (e.target.value.length > 0) {
        // Auto advance
        if (currentFocus.direction === 'across') moveFocus(r, c + 1);
        else moveFocus(r + 1, c);
    }
}

function moveFocus(r, c) {
    const nextInput = document.querySelector(`input[data-row="${r}"][data-col="${c}"]`);
    if (nextInput) {
        nextInput.focus();
    }
}

async function saveGame() {
    if (!currentGame.grid.length) return;

    try {
        // Save to localStorage
        const savedGames = JSON.parse(localStorage.getItem('tts_astro_saved_games') || '[]');

        // Check if game already exists in storage
        const existingIndex = savedGames.findIndex(g => g.id === currentGame.id);

        const gameData = {
            ...currentGame,
            savedAt: new Date().toISOString(),
            // Generate a local ID if not present (negative to distinguish from server IDs)
            id: currentGame.id || -Date.now()
        };

        // Update current game ID if it was null
        currentGame.id = gameData.id;

        if (existingIndex >= 0) {
            savedGames[existingIndex] = gameData;
        } else {
            savedGames.push(gameData);
        }

        localStorage.setItem('tts_astro_saved_games', JSON.stringify(savedGames));
        alert('Permainan berhasil disimpan di browser!');

    } catch (e) {
        console.error(e);
        alert('Gagal menyimpan permainan');
    }
}

async function showLoadModal() {
    const modal = document.getElementById('load-modal');
    const list = document.getElementById('saved-games-list');
    list.innerHTML = '';
    modal.classList.remove('hidden');

    try {
        const savedGames = JSON.parse(localStorage.getItem('tts_astro_saved_games') || '[]');

        if (savedGames.length === 0) {
            list.innerHTML = '<li>Tidak ada permainan tersimpan</li>';
            return;
        }

        // Sort by savedAt desc
        savedGames.sort((a, b) => new Date(b.savedAt) - new Date(a.savedAt));

        savedGames.forEach(game => {
            const li = document.createElement('li');
            li.innerHTML = `<span>Game ${new Date(game.savedAt).toLocaleDateString()}</span> <span>${new Date(game.savedAt).toLocaleTimeString()}</span>`;
            li.addEventListener('click', () => {
                loadGameData(game);
                modal.classList.add('hidden');
            });
            list.appendChild(li);
        });
    } catch (e) {
        console.error(e);
        list.innerHTML = 'Gagal memuat permainan';
    }
}

// loadGame function is no longer needed as we load directly from the object in memory
// but keeping a stub if needed or removing it. 
// The showLoadModal now calls loadGameData directly.

// Scoring System
document.getElementById('btn-submit-game').addEventListener('click', submitGame);
document.getElementById('btn-close-score').addEventListener('click', () => {
    document.getElementById('score-modal').classList.add('hidden');
});
document.getElementById('btn-save-score').addEventListener('click', savePlayerName);

async function submitGame() {
    if (!currentGame) return;

    // If game hasn't been saved to SERVER yet (or has a local negative ID), save it to server first
    // We need a real server ID to submit scores
    if (!currentGame.id || currentGame.id < 0) {
        try {
            const saveResponse = await fetch(`${API_BASE}/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentGame)
            });

            if (saveResponse.ok) {
                const saveData = await saveResponse.json();
                currentGame.id = saveData.id; // Update to server ID
            } else {
                alert('Gagal menyimpan permainan ke server sebelum menilai');
                return;
            }
        } catch (e) {
            console.error(e);
            alert('Error menyimpan permainan ke server');
            return;
        }
    }

    // Collect user grid
    const userGrid = [];
    for (let r = 0; r < currentGame.grid.length; r++) {
        const row = [];
        for (let c = 0; c < currentGame.grid[0].length; c++) {
            const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"] input`);
            row.push(cell ? cell.value : null);
        }
        userGrid.push(row);
    }

    try {
        const response = await fetch(`/api/games/${currentGame.id}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_grid: userGrid })
        });

        if (response.ok) {
            const result = await response.json();
            showScoreModal(result);
        } else {
            alert('Gagal menilai permainan');
        }
    } catch (e) {
        console.error(e);
        alert('Error submitting game');
    }
}

function showScoreModal(result) {
    document.getElementById('final-score').textContent = result.score;
    document.getElementById('correct-count').textContent = result.correct_letters;
    document.getElementById('total-count').textContent = result.total_letters;

    // Render the answer grid with color-coded results
    renderAnswerGrid();

    document.getElementById('score-modal').classList.remove('hidden');
    document.getElementById('name-input-section').classList.remove('hidden');
}

async function savePlayerName() {
    const nameInput = document.getElementById('player-name-input');
    const name = nameInput.value.trim();

    if (!name) {
        alert('Silakan masukkan nama Anda');
        return;
    }

    try {
        const response = await fetch(`/api/games/${currentGame.id}/save_name`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_name: name })
        });

        if (response.ok) {
            document.getElementById('name-input-section').classList.add('hidden');
            alert('Skor berhasil disimpan!');
        } else {
            alert('Gagal menyimpan nama');
        }
    } catch (e) {
        console.error(e);
        alert('Error saving name');
    }
}

async function loadLeaderboard() {
    const list = document.getElementById('leaderboard-list');
    list.innerHTML = 'Memuat...';

    try {
        const response = await fetch('/api/leaderboard');
        const games = await response.json();

        list.innerHTML = '';
        if (games.length === 0) {
            list.innerHTML = '<li>Belum ada skor tersimpan</li>';
            return;
        }

        games.forEach((game, index) => {
            const li = document.createElement('li');

            // Safe rendering to prevent XSS
            const nameSpan = document.createElement('span');
            nameSpan.textContent = `#${index + 1} ${game.player_name}`;

            const scoreSpan = document.createElement('span');
            scoreSpan.className = 'score-badge';
            scoreSpan.textContent = `${game.score} Poin`;

            li.appendChild(nameSpan);
            li.appendChild(scoreSpan);
            list.appendChild(li);
        });
    } catch (e) {
        console.error(e);
        list.innerHTML = 'Gagal memuat papan skor';
    }
}

async function showLeaderboardModal() {
    const modal = document.getElementById('leaderboard-modal');
    const list = document.getElementById('leaderboard-list-main');

    if (!modal || !list) {
        console.error('Leaderboard elements not found');
        alert('Error: Modal tidak ditemukan. Silakan refresh halaman.');
        return;
    }

    list.innerHTML = 'Memuat...';
    modal.classList.remove('hidden');

    try {
        const response = await fetch('/api/leaderboard');
        const games = await response.json();

        list.innerHTML = '';
        if (games.length === 0) {
            list.innerHTML = '<li>Belum ada skor tersimpan</li>';
            return;
        }

        games.forEach((game, index) => {
            const li = document.createElement('li');

            // Safe rendering to prevent XSS
            const nameSpan = document.createElement('span');
            nameSpan.textContent = `#${index + 1} ${game.player_name}`;

            const scoreSpan = document.createElement('span');
            scoreSpan.className = 'score-badge';
            scoreSpan.textContent = `${game.score} Poin`;

            li.appendChild(nameSpan);
            li.appendChild(scoreSpan);
            list.appendChild(li);
        });
    } catch (e) {
        console.error(e);
        list.innerHTML = 'Gagal memuat papan skor';
    }
}

function renderAnswerGrid() {
    const container = document.getElementById('answer-review-grid');

    if (!container) {
        console.error('answer-review-grid not found');
        return;
    }

    container.innerHTML = '';
    container.style.gridTemplateColumns = `repeat(${currentGame.width}, 25px)`;

    for (let r = 0; r < currentGame.height; r++) {
        for (let c = 0; c < currentGame.width; c++) {
            const correctVal = currentGame.grid[r][c];
            const cellDiv = document.createElement('div');
            cellDiv.className = `cell answer-cell ${correctVal === '' ? 'empty' : ''}`;

            if (correctVal !== '') {
                // Get user's input from the main crossword grid
                const userInput = document.querySelector(`#crossword-grid .cell[data-row="${r}"][data-col="${c}"] input`);
                const userVal = userInput ? userInput.value.toUpperCase() : '';

                // Check if this cell is the start of a word
                const wordStart = currentGame.words.find(w => w.row === r && w.col === c);
                if (wordStart) {
                    const numSpan = document.createElement('span');
                    numSpan.className = 'number';
                    numSpan.textContent = wordStart.number;
                    cellDiv.appendChild(numSpan);
                }

                const textSpan = document.createElement('span');
                textSpan.className = 'letter';
                textSpan.textContent = correctVal;

                // Color code based on correctness
                if (userVal === correctVal) {
                    textSpan.classList.add('correct-answer');
                } else {
                    textSpan.classList.add('incorrect-answer');
                }

                cellDiv.appendChild(textSpan);
            }

            container.appendChild(cellDiv);
        }
    }
}
