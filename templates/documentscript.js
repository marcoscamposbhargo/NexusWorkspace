document.addEventListener('DOMContentLoaded', () => {
    const taskForm = document.getElementById('taskForm');
    const taskTitleInput = document.getElementById('taskTitle');
    const taskCategorySelect = document.getElementById('taskCategory');
    const taskList = document.getElementById('taskList');
    const searchInput = document.getElementById('searchInput');

    let allTasks = [];

    async function fetchTasks() {
        try {
            const response = await fetch('/api/tasks');
            allTasks = await response.json();
            renderTasks(allTasks);
        } catch (error) {
            console.error('Erro ao carregar tarefas:', error);
        }
    }

    function renderTasks(tasksToRender) {
        taskList.innerHTML = '';
        if (tasksToRender.length === 0) {
            taskList.innerHTML = `
                <li style="justify-content: center; padding: 20px; color: #64748b; font-size: 0.8rem; background: transparent; border: none;">
                    Nenhuma tarefa encontrada.
                </li>`;
            return;
        }

        tasksToRender.forEach(task => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div class="task-info">
                    <span class="task-title">${escapeHtml(task.title)}</span>
                    <span class="task-cat">${escapeHtml(task.category)}</span>
                </div>
                <button class="btn-delete" onclick="deleteTask(${task.id})" title="Excluir">🗑️</button>
            `;
            taskList.appendChild(li);
        });
    }

    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = taskTitleInput.value.trim();
        const category = taskCategorySelect.value;

        if (!title) return;

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, category })
            });

            if (response.ok) {
                taskTitleInput.value = '';
                searchInput.value = ''; // Limpa a busca ao adicionar
                fetchTasks();
            }
        } catch (error) {
            console.error('Erro ao salvar tarefa:', error);
        }
    });

    window.deleteTask = async function(id) {
        try {
            const response = await fetch(`/api/tasks/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                fetchTasks();
            }
        } catch (error) {
            console.error('Erro ao deletar tarefa:', error);
        }
    };

    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = allTasks.filter(t => 
            t.title.toLowerCase().includes(term) || 
            t.category.toLowerCase().includes(term)
        );
        renderTasks(filtered);
    });

    function escapeHtml(str) {
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    fetchTasks();
});