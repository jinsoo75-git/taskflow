const apiBase = "/api";

const authView = document.getElementById("auth-view");
const boardView = document.getElementById("board-view");
const authForm = document.getElementById("auth-form");
const authUsername = document.getElementById("auth-username");
const authPassword = document.getElementById("auth-password");
const authError = document.getElementById("auth-error");
const loginBtn = document.getElementById("login-btn");
const registerBtn = document.getElementById("register-btn");
const currentUserLabel = document.getElementById("current-user");
const logoutBtn = document.getElementById("logout-btn");

const taskForm = document.getElementById("task-form");
const taskIdInput = document.getElementById("task-id");
const titleInput = document.getElementById("title");
const descriptionInput = document.getElementById("description");
const statusInput = document.getElementById("status");
const assigneeInput = document.getElementById("assignee");
const taskList = document.getElementById("task-list");
const cancelEditBtn = document.getElementById("cancel-edit");

const statusLabels = { todo: "할 일", in_progress: "진행 중", done: "완료" };
const statusColors = {
  todo: "bg-gray-200 text-gray-800",
  in_progress: "bg-yellow-200 text-yellow-800",
  done: "bg-green-200 text-green-800",
};

let token = localStorage.getItem("taskflow_token");
let currentUsername = localStorage.getItem("taskflow_username");

function authHeaders() {
  return { Authorization: `Bearer ${token}` };
}

function showAuthError(message) {
  authError.textContent = message;
  authError.classList.remove("hidden");
}

function setSession(newToken, username) {
  token = newToken;
  currentUsername = username;
  localStorage.setItem("taskflow_token", token);
  localStorage.setItem("taskflow_username", username);
}

function clearSession() {
  token = null;
  currentUsername = null;
  localStorage.removeItem("taskflow_token");
  localStorage.removeItem("taskflow_username");
}

function showBoard() {
  authView.classList.add("hidden");
  boardView.classList.remove("hidden");
  currentUserLabel.textContent = `${currentUsername}님`;
  loadUsers();
  fetchTasks();
}

function showAuth() {
  boardView.classList.add("hidden");
  authView.classList.remove("hidden");
}

async function submitAuth(endpoint) {
  authError.classList.add("hidden");
  const res = await fetch(`${apiBase}/auth/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: authUsername.value, password: authPassword.value }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    showAuthError(err.detail || "요청에 실패했습니다");
    return;
  }

  const data = await res.json();
  setSession(data.token, data.user.username);
  showBoard();
}

authForm.addEventListener("submit", (event) => {
  event.preventDefault();
  submitAuth("login");
});

registerBtn.addEventListener("click", () => submitAuth("register"));

logoutBtn.addEventListener("click", () => {
  clearSession();
  showAuth();
});

async function loadUsers() {
  const res = await fetch(`${apiBase}/users`, { headers: authHeaders() });
  if (!res.ok) return;
  const users = await res.json();
  assigneeInput.innerHTML = '<option value="">미지정</option>';
  for (const user of users) {
    const option = document.createElement("option");
    option.value = user.id;
    option.textContent = user.username;
    assigneeInput.appendChild(option);
  }
}

async function fetchTasks() {
  const res = await fetch(`${apiBase}/tasks`, { headers: authHeaders() });
  if (res.status === 401) {
    clearSession();
    showAuth();
    return;
  }
  const tasks = await res.json();
  renderTasks(tasks);
}

function renderTasks(tasks) {
  taskList.innerHTML = "";
  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = "bg-white rounded-lg shadow p-4 flex justify-between items-start";
    li.innerHTML = `
      <div>
        <div class="flex items-center gap-2 mb-1">
          <h3 class="font-semibold text-gray-800">${escapeHtml(task.title)}</h3>
          <span class="text-xs px-2 py-0.5 rounded-full ${statusColors[task.status]}">${statusLabels[task.status]}</span>
        </div>
        <p class="text-sm text-gray-600">${escapeHtml(task.description)}</p>
        <p class="text-xs text-gray-500 mt-1">
          작성자: ${escapeHtml(task.creator_username)} · 담당자: ${task.assignee_username ? escapeHtml(task.assignee_username) : "미지정"}
        </p>
      </div>
      <div class="flex gap-2 shrink-0">
        <button class="edit-btn text-blue-600 hover:underline text-sm" data-id="${task.id}">수정</button>
        <button class="delete-btn text-red-600 hover:underline text-sm" data-id="${task.id}">삭제</button>
      </div>
    `;
    taskList.appendChild(li);
  }

  taskList.querySelectorAll(".edit-btn").forEach((btn) => {
    btn.addEventListener("click", () => startEdit(btn.dataset.id, tasks));
  });
  taskList.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", () => deleteTask(btn.dataset.id));
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function startEdit(id, tasks) {
  const task = tasks.find((t) => String(t.id) === String(id));
  if (!task) return;
  taskIdInput.value = task.id;
  titleInput.value = task.title;
  descriptionInput.value = task.description;
  statusInput.value = task.status;
  assigneeInput.value = task.assignee_id ?? "";
  cancelEditBtn.classList.remove("hidden");
}

function resetForm() {
  taskForm.reset();
  taskIdInput.value = "";
  cancelEditBtn.classList.add("hidden");
}

cancelEditBtn.addEventListener("click", resetForm);

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    title: titleInput.value,
    description: descriptionInput.value,
    status: statusInput.value,
    assignee_id: assigneeInput.value ? Number(assigneeInput.value) : null,
  };

  const id = taskIdInput.value;
  const url = id ? `${apiBase}/tasks/${id}` : `${apiBase}/tasks`;
  const method = id ? "PUT" : "POST";

  await fetch(url, {
    method,
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload),
  });

  resetForm();
  fetchTasks();
});

async function deleteTask(id) {
  if (!confirm("이 업무를 삭제하시겠습니까?")) return;
  await fetch(`${apiBase}/tasks/${id}`, { method: "DELETE", headers: authHeaders() });
  fetchTasks();
}

if (token && currentUsername) {
  showBoard();
} else {
  showAuth();
}
