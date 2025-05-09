document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const modal = document.getElementById('task-modal');
    const addBtn = document.getElementById('add-task-btn');
    const closeBtn = document.querySelector('.close');
    const taskForm = document.getElementById('task-form');
    const columns = document.querySelectorAll('.column');
    
    // Drag and Drop Variables
    let draggedTask = null;
    
    // Modal Handling
    addBtn.addEventListener('click', () => modal.style.display = 'block');
    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    taskForm.addEventListener('submit', async function(e) {
        e.preventDefault(); // Critical: Prevent default form submission
        
        const formData = new FormData(this);
        try {
            const response = await fetch('/add_task', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Network error');
            
            const data = await response.json();
            
            if (data.success) {
                const todoColumn = document.getElementById('todo-tasks');
                const newTask = createTaskElement(data.task, 'todo');
                todoColumn.appendChild(newTask);
                updateTaskCount('todo');
                modal.style.display = 'none';
                taskForm.reset();
            }
        } catch (error) {
            console.error('Error adding task:', error);
            alert('Failed to add task. Check console for details.');
        }
    });   
    // Replace your current delete event listener with this:
    document.addEventListener('click', async function(e) {
        if (e.target.classList.contains('delete-task')) {
            if (confirm('Are you sure you want to delete this task?')) {
                const status = e.target.dataset.status
                const taskId = parseInt(e.target.dataset.taskId);
                const taskCard = e.target.closest('.task-card');
                console.log('dataset',e.target.dataset)
                console.log('taskCard',taskCard)
                try {
                    const response = await fetch('/delete_task', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ task_id: taskId })
                    });
                    
                    const data = await response.json();
                    console.log('data', data)
                    if (data.success) {
                        
                        // Remove task from UI
                        taskCard.remove();
                        
                        // Update task count
                        updateTaskCount(data.collumn);
                        
                     
                        
                       
                    } else {
                        throw new Error(data.error || 'Failed to delete task');
                    }
                } catch (error) {
                    console.error('Delete error:', error);
                    alert(`Delete failed: ${error.message}`);
                }
            }
        }
    });
    
    // Drag and Drop Events
    document.querySelectorAll('.task-card').forEach(task => {
        task.addEventListener('dragstart', dragStart);
        task.addEventListener('dragend', dragEnd);
    });
    
    columns.forEach(column => {
        column.addEventListener('dragover', dragOver);
        column.addEventListener('dragenter', dragEnter);
        column.addEventListener('dragleave', dragLeave);
        column.addEventListener('drop', drop);
    });
    
    // Drag and Drop Functions
    function dragStart() {
        draggedTask = this;
        this.classList.add('dragging');
        setTimeout(() => this.classList.add('ghost'), 0);
    }
    
    function dragEnd() {
        this.classList.remove('dragging', 'ghost');
    }
    
    function dragOver(e) {
        e.preventDefault();
    }
    
    function dragEnter(e) {
        e.preventDefault();
        this.classList.add('drop-target');
    }
    
    function dragLeave() {
        this.classList.remove('drop-target');
    }
    
    function drop() {
        this.classList.remove('drop-target');
        console.log(draggedTask)
        if (draggedTask) {
            const newStatus = this.dataset.status;
            const taskId = draggedTask.dataset.taskId;
            
            // Update server
            const formData = new FormData();
            formData.append('task_id', taskId);
            formData.append('new_status', newStatus);
            
            fetch('/update_task', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    // Update UI
                    const tasksContainer = this.querySelector('.tasks');
                    tasksContainer.appendChild(draggedTask);
                    
                    // Update task counts
                    updateTaskCount(newStatus);
                    const oldColumn = document.querySelector(`.column[data-status="${draggedTask.dataset.status}"]`);
                    if (oldColumn) updateTaskCount(draggedTask.dataset.status);
                    console.log('draggedTask.dataset.status', draggedTask.dataset.status)
                    
                    // Update task's data-status
                    draggedTask.dataset.status = newStatus;
                }
            });
        }
    }
    
    // Helper Functions
    function createTaskElement(task, status) {
        const taskCard = document.createElement('div');
        taskCard.className = 'task-card';
        taskCard.draggable = true;
        taskCard.dataset.taskId = task.id;
        taskCard.dataset.status = status
        taskCard.innerHTML = `
            <div class="task-title">${task.title}</div>
            <div class="task-due">Due: ${task.due_date}</div>
            <div class="task-description">${task.description}</div>
            <button class="delete-task" data-task-id="${task.id}">×</button>
        `;
        
        taskCard.addEventListener('dragstart', dragStart);
        taskCard.addEventListener('dragend', dragEnd);
        
        return taskCard;
    }
    
    function updateTaskCount(status) {
        const column = document.querySelector(`.column[data-status="${status}"]`);
        if (column) {
            const count = column.querySelector('.tasks').children.length;
            column.querySelector('.task-count').textContent = count;
        }
    }
});