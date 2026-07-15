const apiBase = "/api/tasks";

const taskForm = document.getElementById("task-form");
const taskIdInput = document.getElementById("task-id");
const titleInput = document.getElementById("title");
const descriptionInput = document.getElementById("description");
const statusInput = document.getElementById("status");
const taskList = document.getElementById("task-list");
const cancelEditBtn = document.getElementById("cancel-edit");

const statusLabels = {
  todo: "할 일",
  in_progress: "진행 중",
  done: "완료",
};

const statusColors = {
  todo: "bg-gray-200 text-gray-800",
  in_progress: "bg-yellow-200 text-yellow-800",
  done: "bg-green-200 text-green-800",
};

async function fetchTasks() {
  const res = await fetch(apiBase);
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
  };

  const id = taskIdInput.value;
  if (id) {
    await fetch(`${apiBase}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } else {
    await fetch(apiBase, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }

  resetForm();
  fetchTasks();
});

async function deleteTask(id) {
  if (!confirm("이 업무를 삭제하시겠습니까?")) return;
  await fetch(`${apiBase}/${id}`, { method: "DELETE" });
  fetchTasks();
}

fetchTasks();
