from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Banco de dados em memória temporário
tasks = [
    {"id": 1, "title": "Analisar dados de mercado", "category": "Finanças", "done": False},
    {"id": 2, "title": "Atualizar relatório mensal", "category": "Gestão", "done": True},
    {"id": 3, "title": "Otimizar código Python", "category": "Desenvolvimento", "done": False}
]

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Workspace - Full-Stack</title>
    <style>
        :root {
            --bg: #090d16;
            --card-bg: #111827;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --danger: #ef4444;
            --border: #1f2937;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg); color: var(--text); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .app-container { width: 100%; max-width: 550px; display: flex; flex-direction: column; gap: 20px; }
        .app-header { text-align: center; margin-bottom: 5px; }
        .app-header h1 { font-size: 1.4rem; font-weight: 700; color: #fff; }
        .app-header p { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }
        .card { background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); }
        .card h2 { font-size: 0.95rem; font-weight: 600; margin-bottom: 12px; color: #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px; }
        form { display: flex; gap: 10px; flex-wrap: wrap; }
        input[type="text"], select { flex: 1; padding: 10px 14px; background: #090d16; border: 1px solid var(--border); border-radius: 10px; color: #fff; font-size: 0.85rem; outline: none; transition: border-color 0.2s; }
        input[type="text"]:focus, select:focus { border-color: var(--primary); }
        .btn-primary { background-color: var(--primary); color: white; border: none; padding: 10px 18px; border-radius: 10px; font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: background 0.2s; }
        .btn-primary:hover { background-color: var(--primary-hover); }
        .search-box { margin-bottom: 12px; }
        .search-box input { width: 100%; }
        ul { list-style: none; display: flex; flex-direction: column; gap: 8px; max-height: 280px; overflow-y: auto; padding-right: 4px; }
        li { display: flex; justify-content: space-between; align-items: center; background: #090d16; padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border); transition: border-color 0.2s; }
        li:hover { border-color: #374151; }
        .task-info { display: flex; flex-direction: column; gap: 4px; }
        .task-title { font-size: 0.85rem; font-weight: 500; color: #f1f5f9; }
        .task-cat { font-size: 0.65rem; background: #1e293b; padding: 2px 6px; border-radius: 4px; width: fit-content; color: var(--text-muted); font-weight: 500; }
        .btn-delete { background: transparent; border: none; color: var(--danger); cursor: pointer; font-size: 0.95rem; opacity: 0.8; transition: opacity 0.2s; }
        .btn-delete:hover { opacity: 1; }
    </style>
</head>
<body>
    <div class="app-container">
        <header class="app-header">
            <h1>🚀 Nexus Workspace</h1>
            <p>Gerenciamento Dinâmico com Python, JS, HTML e CSS</p>
        </header>
        
        <main class="main-content">
            <section class="card">
                <h2>Adicionar Nova Tarefa</h2>
                <form id="taskForm">
                    <input type="text" id="taskTitle" placeholder="O que precisa ser feito?" required autocomplete="off">
                    <select id="taskCategory">
                        <option value="Finanças">Finanças</option>
                        <option value="Gestão">Gestão</option>
                        <option value="Desenvolvimento">Desenvolvimento</option>
                    </select>
                    <button type="submit" class="btn-primary">Adicionar</button>
                </form>
            </section>

            <section class="card" style="margin-top: 15px;">
                <h2>Tarefas Ativas</h2>
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="🔍 Filtrar tarefas por nome ou categoria...">
                </div>
                <ul id="taskList"></ul>
            </section>
        </main>
    </div>

    <script>
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
                    taskList.innerHTML = '<li style="justify-content: center; color: #64748b; font-size: 0.8rem; background: transparent; border: none;">Nenhuma tarefa encontrada.</li>';
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
                        searchInput.value = '';
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
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/api/tasks', methods=['GET', 'POST'])
def manage_tasks():
    global tasks
    if request.method == 'POST':
        data = request.json
        new_task = {
            "id": len(tasks) + 1,
            "title": data.get("title"),
            "category": data.get("category", "Geral"),
            "done": False
        }
        tasks.append(new_task)
        return jsonify({"status": "success", "task": new_task})
    return jsonify(tasks)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    print("🚀 Servidor rodando em http://127.0.0.1:5000")
    app.run(debug=True, port=5000)