"""Product-style HTML interface for the board game club."""

# pylint: disable=line-too-long,too-many-lines

HOME_HTML = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Клуб настольных игр</title>
  <style>
    :root {
      --bg: #f4efe6;
      --panel: #fffaf2;
      --panel-strong: #2d332c;
      --ink: #20231f;
      --muted: #756d61;
      --line: #e2d6c4;
      --accent: #c84d32;
      --accent-dark: #963622;
      --sage: #55745b;
      --gold: #d99a2b;
      --cream: #fff6df;
      --shadow: 0 24px 70px rgba(64, 44, 24, 0.14);
    }

    * { box-sizing: border-box; }

    html { scroll-behavior: smooth; }

    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at 16% -4%, rgba(217, 154, 43, 0.28), transparent 34rem),
        radial-gradient(circle at 100% 6%, rgba(85, 116, 91, 0.22), transparent 28rem),
        linear-gradient(135deg, #f8f0df, var(--bg));
      font-family: Avenir, "Trebuchet MS", Verdana, sans-serif;
    }

    a { color: inherit; }

    .shell {
      width: min(1200px, calc(100% - 32px));
      margin: 0 auto;
    }

    .topbar {
      position: sticky;
      top: 0;
      z-index: 20;
      border-bottom: 1px solid rgba(45, 51, 44, 0.08);
      background: rgba(244, 239, 230, 0.82);
      backdrop-filter: blur(18px);
    }

    .topbar .shell {
      min-height: 72px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 900;
      letter-spacing: -0.03em;
      font-size: 22px;
    }

    .mark {
      width: 38px;
      height: 38px;
      display: grid;
      place-items: center;
      border-radius: 14px;
      color: #fffaf2;
      background: var(--panel-strong);
      font-weight: 900;
    }

    nav {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    nav a, .link-button {
      border: 1px solid transparent;
      border-radius: 999px;
      padding: 10px 14px;
      color: var(--muted);
      text-decoration: none;
      font-weight: 800;
      font-size: 14px;
    }

    nav a:hover, .link-button:hover {
      border-color: var(--line);
      color: var(--ink);
      background: rgba(255, 250, 242, 0.7);
    }

    .hero {
      padding: 54px 0 24px;
      display: grid;
      grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
      gap: 22px;
      align-items: stretch;
    }

    .hero-card {
      min-height: 390px;
      padding: 34px;
      border-radius: 36px;
      color: #fffaf2;
      background:
        linear-gradient(140deg, rgba(45, 51, 44, 0.94), rgba(65, 82, 61, 0.95)),
        radial-gradient(circle at 80% 10%, rgba(217, 154, 43, 0.35), transparent 18rem);
      box-shadow: var(--shadow);
      overflow: hidden;
      position: relative;
    }

    .hero-card::after {
      content: "";
      position: absolute;
      right: -80px;
      bottom: -130px;
      width: 320px;
      height: 320px;
      border-radius: 80px;
      border: 34px solid rgba(255, 250, 242, 0.09);
      transform: rotate(18deg);
    }

    h1 {
      margin: 0;
      max-width: 760px;
      font-size: clamp(42px, 7vw, 86px);
      line-height: 0.9;
      letter-spacing: -0.075em;
    }

    h2 {
      margin: 0 0 16px;
      font-size: clamp(26px, 3vw, 38px);
      letter-spacing: -0.045em;
    }

    h3 {
      margin: 0 0 10px;
      font-size: 20px;
      letter-spacing: -0.02em;
    }

    p {
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.6;
    }

    .hero-card p {
      max-width: 620px;
      margin-top: 18px;
      color: rgba(255, 250, 242, 0.78);
      font-size: 18px;
    }

    .panel {
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: 30px;
      background: rgba(255, 250, 242, 0.88);
      box-shadow: var(--shadow);
    }

    .quick-panel {
      display: grid;
      gap: 14px;
      align-content: start;
    }

    .status {
      min-height: 64px;
      padding: 14px 16px;
      border-radius: 20px;
      border: 1px solid var(--line);
      background: var(--cream);
      color: var(--ink);
      line-height: 1.45;
    }

    .ok { color: var(--sage); font-weight: 900; }
    .bad { color: var(--accent-dark); font-weight: 900; }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }

    button {
      min-height: 46px;
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      color: white;
      background: var(--accent);
      font: inherit;
      font-weight: 900;
      cursor: pointer;
      transition: transform 0.14s ease, filter 0.14s ease;
    }

    button:hover {
      transform: translateY(-1px);
      filter: brightness(0.96);
    }

    button.secondary { background: var(--sage); }
    button.dark { background: var(--panel-strong); }
    button.soft { background: #7a6d5b; }
    button.danger { background: var(--accent-dark); }
    button.small { min-height: 36px; padding: 8px 12px; font-size: 13px; }

    .section {
      padding: 24px 0;
    }

    .section-head {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: end;
      margin-bottom: 16px;
    }

    .section-head p { max-width: 620px; margin: 0; }

    .grid {
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 16px;
    }

    .col-4 { grid-column: span 4; }
    .col-5 { grid-column: span 5; }
    .col-6 { grid-column: span 6; }
    .col-7 { grid-column: span 7; }
    .col-8 { grid-column: span 8; }
    .col-12 { grid-column: span 12; }

    .stats {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-top: 26px;
    }

    .stat {
      padding: 18px;
      border-radius: 22px;
      background: rgba(255, 250, 242, 0.1);
      border: 1px solid rgba(255, 250, 242, 0.14);
    }

    .stat span {
      display: block;
      color: rgba(255, 250, 242, 0.68);
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .stat strong {
      display: block;
      margin-top: 8px;
      font-size: 34px;
      line-height: 1;
    }

    form {
      display: grid;
      gap: 12px;
    }

    label {
      display: grid;
      gap: 7px;
      color: var(--muted);
      font-size: 14px;
      font-weight: 900;
    }

    input, select, textarea {
      width: 100%;
      min-height: 46px;
      padding: 11px 13px;
      border: 1px solid var(--line);
      border-radius: 15px;
      background: #fffdf8;
      color: var(--ink);
      font: inherit;
      outline: none;
    }

    input:focus, select:focus, textarea:focus {
      border-color: var(--gold);
      box-shadow: 0 0 0 4px rgba(217, 154, 43, 0.14);
    }

    textarea {
      min-height: 92px;
      resize: vertical;
    }

    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .list {
      display: grid;
      gap: 12px;
    }

    .item {
      padding: 16px;
      border-radius: 22px;
      border: 1px solid var(--line);
      background: #fffdf8;
    }

    .item-top {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: start;
    }

    .item strong {
      display: block;
      font-size: 19px;
      margin-bottom: 4px;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 5px 10px;
      border-radius: 999px;
      background: #f0e6d5;
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
    }

    .empty {
      padding: 20px;
      border: 1px dashed var(--line);
      border-radius: 22px;
      color: var(--muted);
      background: rgba(255, 250, 242, 0.55);
    }

    .user-list {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .check-card {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: #fffdf8;
      color: var(--ink);
      font-size: 14px;
    }

    .check-card input {
      width: auto;
      min-height: auto;
    }

    .toast {
      position: fixed;
      left: 50%;
      bottom: 22px;
      z-index: 40;
      width: min(640px, calc(100% - 32px));
      padding: 14px 18px;
      border-radius: 999px;
      color: #fffaf2;
      background: rgba(45, 51, 44, 0.94);
      box-shadow: var(--shadow);
      transform: translate(-50%, 120px);
      transition: transform 0.2s ease;
    }

    .toast.show {
      transform: translate(-50%, 0);
    }

    footer {
      padding: 30px 0 50px;
      color: var(--muted);
      text-align: center;
    }

    @media (max-width: 960px) {
      .hero, .stats, .form-grid, .user-list { grid-template-columns: 1fr; }
      .col-4, .col-5, .col-6, .col-7, .col-8, .col-12 { grid-column: span 12; }
      .topbar .shell { align-items: start; flex-direction: column; padding: 14px 0; }
      nav { width: 100%; }
    }
  </style>
</head>
<body>
  <div class="topbar">
    <div class="shell">
      <div class="brand"><span class="mark">BG</span><span>Board Game Club</span></div>
      <nav>
        <a href="#dashboard">Обзор</a>
        <a href="#games">Игры</a>
        <a href="#sessions">Встречи</a>
        <a href="#recommend">Подбор</a>
        <a href="#reviews">Отзывы</a>
      </nav>
    </div>
  </div>

  <main class="shell">
    <section class="hero" id="dashboard">
      <div class="hero-card">
        <h1>Управляйте игровым вечером без суеты</h1>
        <p>
          Каталог игр, участники, встречи, отзывы и подбор подходящей игры
          собраны на одном экране.
        </p>
        <div class="actions">
          <button type="button" id="demoButton">Заполнить демо</button>
          <button type="button" class="secondary" id="refreshButton">Обновить</button>
        </div>
        <div class="stats">
          <div class="stat"><span>Игры</span><strong id="gamesCount">0</strong></div>
          <div class="stat"><span>Встречи</span><strong id="sessionsCount">0</strong></div>
          <div class="stat"><span>Игроки</span><strong id="usersCount">0</strong></div>
          <div class="stat"><span>Отзывы</span><strong id="reviewsCount">0</strong></div>
        </div>
      </div>

      <aside class="panel quick-panel">
        <h2>Профиль</h2>
        <p id="authState">Вы не вошли.</p>
        <form id="authForm">
          <div class="form-grid">
            <label>Логин
              <input id="username" value="alice" autocomplete="username">
            </label>
            <label>Email
              <input id="email" value="alice@example.com" autocomplete="email">
            </label>
          </div>
          <label>Пароль
            <input id="password" value="secret123" type="password">
          </label>
          <div class="actions">
            <button type="button" id="registerButton">Создать аккаунт</button>
            <button type="button" class="dark" id="loginButton">Войти</button>
          </div>
        </form>
        <div class="status" id="mainStatus">Выберите действие.</div>
      </aside>
    </section>

    <section class="section" id="games">
      <div class="section-head">
        <div>
          <h2>Каталог игр</h2>
          <p>Добавляйте игры в каталог. Новая игра сразу появится в подборе, встречах и отзывах.</p>
        </div>
      </div>
      <div class="grid">
        <div class="panel col-5">
          <h3>Новая игра</h3>
          <form id="gameForm">
            <label>Название
              <input id="gameName" value="Catan">
            </label>
            <div class="form-grid">
              <label>Издатель
                <input id="publisher" value="Kosmos">
              </label>
              <label>Жанр
                <input id="genre" value="Family">
              </label>
            </div>
            <div class="form-grid">
              <label>Минимум игроков
                <input id="minPlayers" value="1" type="number" min="1">
              </label>
              <label>Максимум игроков
                <input id="maxPlayers" value="4" type="number" min="1">
              </label>
            </div>
            <div class="form-grid">
              <label>Длительность, минут
                <input id="playTime" value="90" type="number" min="10">
              </label>
              <label>Сложность
                <input id="complexity" value="2.3" type="number" min="1" max="5" step="0.1">
              </label>
            </div>
            <button type="submit">Добавить игру</button>
          </form>
        </div>
        <div class="panel col-7">
          <h3>Все игры</h3>
          <div class="list" id="gamesList"></div>
        </div>
      </div>
    </section>

    <section class="section" id="sessions">
      <div class="section-head">
        <div>
          <h2>Встречи</h2>
          <p>Игры и участники выбираются из актуальных списков.</p>
        </div>
      </div>
      <div class="grid">
        <div class="panel col-5">
          <h3>Новая встреча</h3>
          <form id="sessionForm">
            <label>Название встречи
              <input id="sessionTitle" value="Friday game night">
            </label>
            <label>Игра
              <select id="sessionGameSelect"></select>
            </label>
            <label>Статус
              <select id="sessionStatus">
                <option value="planned">Запланирована</option>
                <option value="completed">Сыграна</option>
              </select>
            </label>
            <label>Участники
              <div class="user-list" id="participantsList"></div>
            </label>
            <button type="submit">Создать встречу</button>
          </form>
        </div>
        <div class="panel col-7">
          <h3>Расписание</h3>
          <div class="list" id="sessionsList"></div>
        </div>
      </div>
    </section>

    <section class="section" id="recommend">
      <div class="section-head">
        <div>
          <h2>Подбор игры</h2>
          <p>Сервис сравнит количество игроков, длительность, сложность и рейтинг.</p>
        </div>
      </div>
      <div class="grid">
        <div class="panel col-4">
          <form id="recommendForm">
            <label>Игроков
              <input id="recPlayers" value="2" type="number" min="1">
            </label>
            <label>До скольки минут
              <input id="recDuration" value="120" type="number" min="10">
            </label>
            <label>Максимальная сложность
              <input id="recComplexity" value="3" type="number" min="1" max="5" step="0.1">
            </label>
            <button type="submit">Подобрать игру</button>
          </form>
        </div>
        <div class="panel col-8">
          <h3>Рекомендации</h3>
          <div class="list" id="recommendations"></div>
        </div>
      </div>
    </section>

    <section class="section" id="reviews">
      <div class="section-head">
        <div>
          <h2>Отзывы</h2>
          <p>Оценки улучшают подбор: игры с хорошими отзывами поднимаются выше.</p>
        </div>
      </div>
      <div class="grid">
        <div class="panel col-5">
          <h3>Новый отзыв</h3>
          <form id="reviewForm">
            <label>Игра
              <select id="reviewGameSelect"></select>
            </label>
            <label>Оценка
              <input id="rating" value="9" type="number" min="1" max="10">
            </label>
            <label>Комментарий
              <textarea id="comment">Easy to explain and fun for a mixed group.</textarea>
            </label>
            <button type="submit">Сохранить отзыв</button>
          </form>
        </div>
        <div class="panel col-7">
          <h3>Все отзывы</h3>
          <div class="list" id="reviewsList"></div>
        </div>
      </div>
    </section>
  </main>

  <footer class="shell">
    <a href="/docs" target="_blank">API documentation</a>
  </footer>

  <div class="toast" id="toast"></div>

  <script>
    const state = {
      token: localStorage.getItem("token") || "",
      user: JSON.parse(localStorage.getItem("user") || "null"),
      games: [],
      sessions: [],
      users: [],
      reviews: []
    };

    const $ = (id) => document.getElementById(id);

    function headers(json = true) {
      const result = {};
      if (json) result["Content-Type"] = "application/json";
      if (state.token) result.Authorization = `Bearer ${state.token}`;
      return result;
    }

    function toast(message) {
      const box = $("toast");
      box.textContent = message;
      box.classList.add("show");
      window.clearTimeout(window.toastTimer);
      window.toastTimer = window.setTimeout(() => box.classList.remove("show"), 2600);
    }

    function show(message, ok = true) {
      $("mainStatus").innerHTML = ok
        ? `<span class="ok">Готово.</span> ${message}`
        : `<span class="bad">Не получилось.</span> ${message}`;
      toast(message);
    }

    async function request(path, options = {}) {
      const response = await fetch(path, options);
      const text = await response.text();
      let data = null;
      if (text) {
        try {
          data = JSON.parse(text);
        } catch {
          data = text;
        }
      }
      if (!response.ok) {
        const detail = data && data.detail ? data.detail : text || response.statusText;
        const message = Array.isArray(detail) ? detail.map((item) => item.msg).join("; ") : detail;
        throw new Error(message);
      }
      return data;
    }

    function saveAuth(token, user) {
      state.token = token;
      state.user = user;
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));
      $("authState").innerHTML = `Активный игрок: <b>${user.username}</b>`;
    }

    function option(value, label) {
      return `<option value="${value}">${label}</option>`;
    }

    function syncSelectors() {
      const gameOptions = state.games.length
        ? state.games.map((game) => option(game.id, `${game.name} · ${game.genre}`)).join("")
        : option("", "Сначала добавьте игру");
      $("sessionGameSelect").innerHTML = gameOptions;
      $("reviewGameSelect").innerHTML = gameOptions;

      $("participantsList").innerHTML = state.users.length
        ? state.users.map((user) => `
          <label class="check-card">
            <input type="checkbox" value="${user.id}" ${state.user && user.id === state.user.id ? "checked" : ""}>
            ${user.username}
          </label>
        `).join("")
        : `<div class="empty">Войдите или создайте демо, чтобы выбрать участников.</div>`;
    }

    function renderItems(target, items, empty, renderer) {
      target.innerHTML = items.length
        ? items.map(renderer).join("")
        : `<div class="empty">${empty}</div>`;
    }

    function renderGames() {
      renderItems($("gamesList"), state.games, "Каталог пока пуст.", (game) => `
        <article class="item">
          <div class="item-top">
            <div>
              <strong>${game.name}</strong>
              <div class="meta">
                <span class="pill">${game.genre}</span>
                <span class="pill">${game.min_players}-${game.max_players} игроков</span>
                <span class="pill">${game.play_time_minutes} минут</span>
                <span class="pill">сложность ${game.complexity}</span>
              </div>
            </div>
            <button class="small danger" data-delete-game="${game.id}">Удалить</button>
          </div>
        </article>
      `);
    }

    function userName(userId) {
      const user = state.users.find((item) => item.id === userId);
      return user ? user.username : `игрок ${userId}`;
    }

    function statusName(status) {
      const names = {
        planned: "запланирована",
        completed: "сыграна",
        cancelled: "отменена"
      };
      return names[status] || status;
    }

    function gameName(gameId) {
      const game = state.games.find((item) => item.id === gameId);
      return game ? game.name : `игра ${gameId}`;
    }

    function renderSessions() {
      renderItems($("sessionsList"), state.sessions, "Встреч пока нет.", (session) => `
        <article class="item">
          <div class="item-top">
            <div>
              <strong>${session.title}</strong>
              <div>${gameName(session.game_id)}</div>
              <div class="meta">
                <span class="pill">${statusName(session.status)}</span>
                <span class="pill">${session.participants.length} участников</span>
                ${session.participants.map((item) => `<span class="pill">${userName(item.user_id)}</span>`).join("")}
              </div>
            </div>
            <button class="small danger" data-delete-session="${session.id}">Удалить</button>
          </div>
        </article>
      `);
    }

    function renderReviews() {
      renderItems($("reviewsList"), state.reviews, "Отзывов пока нет.", (review) => `
        <article class="item">
          <div class="item-top">
            <div>
              <strong>${gameName(review.game_id)} · ${review.rating}/10</strong>
              <p>${review.comment}</p>
              <span class="pill">${userName(review.author_id)}</span>
            </div>
            <button class="small danger" data-delete-review="${review.id}">Удалить</button>
          </div>
        </article>
      `);
    }

    function updateStats() {
      $("gamesCount").textContent = state.games.length;
      $("sessionsCount").textContent = state.sessions.length;
      $("usersCount").textContent = state.users.length;
      $("reviewsCount").textContent = state.reviews.length;
    }

    function renderAll() {
      syncSelectors();
      renderGames();
      renderSessions();
      renderReviews();
      updateStats();
    }

    async function refreshAll() {
      state.games = await request("/games");
      state.sessions = await request("/sessions");
      state.reviews = await request("/reviews");
      if (state.token) {
        state.users = await request("/users", { headers: headers(false) });
      }
      renderAll();
    }

    async function loadMe() {
      if (!state.token) return;
      try {
        const user = await request("/auth/me", { headers: headers(false) });
        saveAuth(state.token, user);
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        state.token = "";
        state.user = null;
      }
    }

    function gamePayload() {
      return {
        name: $("gameName").value,
        publisher: $("publisher").value,
        genre: $("genre").value,
        min_players: Number($("minPlayers").value),
        max_players: Number($("maxPlayers").value),
        play_time_minutes: Number($("playTime").value),
        complexity: Number($("complexity").value)
      };
    }

    function selectedParticipants() {
      return [...$("participantsList").querySelectorAll("input:checked")]
        .map((item) => Number(item.value));
    }

    async function login() {
      const token = await request("/auth/login-json", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          username: $("username").value,
          password: $("password").value
        })
      });
      state.token = token.access_token;
      const user = await request("/auth/me", { headers: headers(false) });
      saveAuth(token.access_token, user);
      await refreshAll();
      show(`Вы вошли как ${user.username}.`);
    }

    $("demoButton").addEventListener("click", async () => {
      try {
        const demo = await request("/demo/seed", { method: "POST" });
        saveAuth(demo.access_token, demo.user);
        await refreshAll();
        $("sessionGameSelect").value = demo.game.id;
        $("reviewGameSelect").value = demo.game.id;
        [...$("participantsList").querySelectorAll("input")].forEach((input) => {
          input.checked = demo.participants.some((user) => user.id === Number(input.value));
        });
        show(`Демо готово: ${demo.game.name}, ${demo.session.title}.`);
      } catch (error) {
        show(error.message, false);
      }
    });

    $("refreshButton").addEventListener("click", async () => {
      try {
        await refreshAll();
        show("Данные обновлены.");
      } catch (error) {
        show(error.message, false);
      }
    });

    $("registerButton").addEventListener("click", async () => {
      try {
        await request("/auth/register", {
          method: "POST",
          headers: headers(),
          body: JSON.stringify({
            username: $("username").value,
            email: $("email").value,
            password: $("password").value
          })
        });
        await login();
      } catch (error) {
        if (error.message.includes("already exists")) {
          await login();
        } else {
          show(error.message, false);
        }
      }
    });

    $("loginButton").addEventListener("click", async () => {
      try {
        await login();
      } catch (error) {
        show(error.message, false);
      }
    });

    $("gameForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        const game = await request("/games", {
          method: "POST",
          headers: headers(),
          body: JSON.stringify(gamePayload())
        });
        await refreshAll();
        $("sessionGameSelect").value = game.id;
        $("reviewGameSelect").value = game.id;
        show(`${game.name} добавлена в каталог.`);
      } catch (error) {
        show(error.message, false);
      }
    });

    $("sessionForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        const userIds = selectedParticipants();
        const status = $("sessionStatus").value;
        const participants = userIds.map((userId, index) => ({
          user_id: userId,
          score: status === "completed" ? 10 - index : null,
          is_winner: status === "completed" && index === 0
        }));
        const session = await request("/sessions", {
          method: "POST",
          headers: headers(),
          body: JSON.stringify({
            title: $("sessionTitle").value,
            game_id: Number($("sessionGameSelect").value),
            scheduled_at: new Date(Date.now() + 86400000).toISOString(),
            status,
            notes: "",
            participants
          })
        });
        await refreshAll();
        show(`${session.title} добавлена в расписание.`);
      } catch (error) {
        show(error.message, false);
      }
    });

    $("recommendForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        const params = new URLSearchParams({
          players: $("recPlayers").value,
          max_duration: $("recDuration").value,
          max_complexity: $("recComplexity").value
        });
        const items = await request(`/analytics/recommendations?${params}`);
        renderItems($("recommendations"), items, "Подходящих игр пока нет.", (item) => `
          <article class="item">
            <strong>${item.game_name}</strong>
            <div class="meta">
              <span class="pill">оценка ${item.suitability_score}</span>
              <span class="pill">${item.reason}</span>
            </div>
          </article>
        `);
        show("Подбор обновлен.");
      } catch (error) {
        show(error.message, false);
      }
    });

    $("reviewForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        const review = await request("/reviews", {
          method: "POST",
          headers: headers(),
          body: JSON.stringify({
            game_id: Number($("reviewGameSelect").value),
            rating: Number($("rating").value),
            comment: $("comment").value
          })
        });
        await refreshAll();
        show(`Отзыв ${review.rating}/10 сохранен.`);
      } catch (error) {
        show(error.message, false);
      }
    });

    document.addEventListener("click", async (event) => {
      const gameId = event.target.dataset.deleteGame;
      const sessionId = event.target.dataset.deleteSession;
      const reviewId = event.target.dataset.deleteReview;
      if (!gameId && !sessionId && !reviewId) return;

      try {
        if (gameId) {
          await request(`/games/${gameId}`, { method: "DELETE", headers: headers(false) });
          show("Игра удалена.");
        }
        if (sessionId) {
          await request(`/sessions/${sessionId}`, { method: "DELETE", headers: headers(false) });
          show("Встреча удалена.");
        }
        if (reviewId) {
          await request(`/reviews/${reviewId}`, { method: "DELETE", headers: headers(false) });
          show("Отзыв удален.");
        }
        await refreshAll();
      } catch (error) {
        show(error.message, false);
      }
    });

    loadMe().then(refreshAll).catch((error) => show(error.message, false));
  </script>
</body>
</html>
"""
