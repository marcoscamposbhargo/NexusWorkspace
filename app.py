import threading
import sqlite3
import webview
import sys
import os
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Garante que o banco de dados seja salvo na mesma pasta do executável
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(BASE_DIR, "nexus_workspace.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            deadline TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM tasks')
    if cursor.fetchone()[0] == 0:
        initial_tasks = [
            ("Analisar dados de mercado", "Finanças", "18:00"),
            ("Atualizar relatório mensal", "Gestão", "12:30"),
            ("Otimizar código Python", "Desenvolvimento", "20:00")
        ]
        cursor.executemany('INSERT INTO tasks (title, category, deadline) VALUES (?, ?, ?)', initial_tasks)
        conn.commit()
    conn.close()

init_db()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Workspace</title>
    <style>
        :root {
            --bg: #090d16;
            --card-bg: #111827;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --danger: #ef4444;
            --warning: #f59e0b;
            --safe: #10b981;
            --border: #1f2937;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg); color: var(--text); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .app-container { width: 100%; max-width: 580px; display: flex; flex-direction: column; gap: 20px; }
        .app-header { text-align: center; margin-bottom: 5px; }
        .app-header h1 { font-size: 1.4rem; font-weight: 700; color: #fff; }
        .app-header p { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }
        .card { background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); }
        .card h2 { font-size: 0.95rem; font-weight: 600; margin-bottom: 12px; color: #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px; }
        
        form { display: flex; gap: 8px; flex-wrap: wrap; }
        input[type="text"], select, input[type="time"] { 
            padding: 10px 14px; background: #090d16; border: 1px solid var(--border); border-radius: 10px; color: #fff; font-size: 0.85rem; outline: none; transition: border-color 0.2s; 
        }
        input[type="text"] { flex: 2; min-width: 180px; }
        select { flex: 1; }
        input[type="time"] { flex: 1; color-scheme: dark; }
        input[type="text"]:focus, select:focus, input[type="time"]:focus { border-color: var(--primary); }
        
        .btn-primary { background-color: var(--primary); color: white; border: none; padding: 10px 18px; border-radius: 10px; font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: background 0.2s; width: 100%; }
        .btn-primary:hover { background-color: var(--primary-hover); }
        
        .search-box { margin-bottom: 12px; }
        .search-box input { width: 100%; }
        
        ul { list-style: none; display: flex; flex-direction: column; gap: 8px; max-height: 260px; overflow-y: auto; padding-right: 4px; }
        li { display: flex; justify-content: space-between; align-items: center; background: #090d16; padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border); transition: border-color 0.2s; }
        li:hover { border-color: #374151; }
        
        .task-info { display: flex; flex-direction: column; gap: 6px; }
        .task-title { font-size: 0.85rem; font-weight: 500; color: #f1f5f9; }
        
        .task-meta { display: flex; gap: 6px; align-items: center; }
        .task-cat { font-size: 0.65rem; background: #1e293b; padding: 2px 6px; border-radius: 4px; color: var(--text-muted); font-weight: 500; }
        
        .task-deadline { font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 600; display: flex; align-items: center; gap: 3px; border: 1px solid transparent; }
        .task-deadline.safe { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2); color: #34d399; }
        .task-deadline.warning { background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); color: #fbbf24; }
        .task-deadline.danger { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.2); color: #f87171; }
        
        .btn-delete { background: transparent; border: none; color: var(--danger); cursor: pointer; font-size: 0.95rem; opacity: 0.8; transition: opacity 0.2s; }
        .btn-delete:hover { opacity: 1; }
    </style>
</head>
<body>
    <div class="app-container">
        <header class="app-header">
            <h1>🚀 Nexus Workspace</h1>
            <p>Versão Definitiva</p>
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
                    <input type="time" id="taskDeadline" required title="Deadline Diário">
                    <button type="submit" class="btn-primary">Adicionar Tarefa</button>
                </form>
            </section>

            <section class="card" style="margin-top: 15px;">
                <h2>Tarefas Ativas</h2>
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="🔍 Filtrar tarefas...">
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
            const taskDeadlineInput = document.getElementById('taskDeadline');
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

            function getDeadlineStatus(deadlineStr) {
                if (!deadlineStr) return { className: 'safe', text: 'Sem prazo' };

                const now = new Date();
                const currentTotalMinutes = now.getHours() * 60 + now.getMinutes();

                const [hours, minutes] = deadlineStr.split(':').map(Number);
                const deadlineTotalMinutes = hours * 60 + minutes;

                const diffMinutes = deadlineTotalMinutes - currentTotalMinutes;

                if (diffMinutes < 0) {
                    return { className: 'danger', text: `⏰ ${deadlineStr} (Atrasado)` };
                } else if (diffMinutes <= 30) {
                    return { className: 'warning', text: `⏰ ${deadlineStr} (${diffMinutes}m restantes)` };
                } else {
                    return { className: 'safe', text: `⏰ ${deadlineStr}` };
                }
            }

            function renderTasks(tasksToRender) {
                taskList.innerHTML = '';
                if (tasksToRender.length === 0) {
                    taskList.innerHTML = '<li style="justify-content: center; color: #64748b; font-size: 0.8rem; background: transparent; border: none;">Nenhuma tarefa encontrada.</li>';
                    return;
                }

                tasksToRender.forEach(task => {
                    const deadlineStatus = getDeadlineStatus(task.deadline);
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <div class="task-info">
                            <span class="task-title">${escapeHtml(task.title)}</span>
                            <div class="task-meta">
                                <span class="task-cat">${escapeHtml(task.category)}</span>
                                <span class="task-deadline ${deadlineStatus.className}">${deadlineStatus.text}</span>
                            </div>
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
                const deadline = taskDeadlineInput.value;

                if (!title || !deadline) return;

                try {
                    const response = await fetch('/api/tasks', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title, category, deadline })
                    });

                    if (response.ok) {
                        taskTitleInput.value = '';
                        taskDeadlineInput.value = '';
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
                    t.category.toLowerCase().includes(term) ||
                    t.deadline.toLowerCase().includes(term)
                );
                renderTasks(filtered);
            });

            setInterval(fetchTasks, 30000);

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
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        title = data.get("title")
        category = data.get("category", "Geral")
        deadline = data.get("deadline", "00:00")
        
        cursor.execute('INSERT INTO tasks (title, category, deadline) VALUES (?, ?, ?)', (title, category, deadline))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"status": "success", "task": {"id": new_id, "title": title, "category": category, "deadline": deadline}})
    
    cursor.execute('SELECT * FROM tasks')
    rows = cursor.fetchall()
    tasks_list = [dict(row) for row in rows]
    conn.close()
    return jsonify(tasks_list)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    def run_flask():
        app.run(port=5000, debug=False, use_reloader=False)

    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    webview.create_window("Nexus Workspace", "http://127.0.0.1:5000", width=620, height=750)
    webview.start()