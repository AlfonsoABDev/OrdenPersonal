from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

tasks = []
day_notes = {}
courses = []
course_tasks = {}
proyectos = []
proyectos_objetivos = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/tasks')
def index():
    # Generar eventos para el calendario
    events = []
    for idx, t in enumerate(tasks):
        if t.get('date'):
            events.append({
                'title': t['name'],
                'start': t['date'],
                'allDay': True,
                'color': '#6c63ff' if not t['done'] else '#bdbdbd',
                'id': idx
            })
    return render_template('index.html', tasks=tasks, events=json.dumps(events), day_notes=json.dumps(day_notes))

@app.route('/cursos')
def cursos():
    return render_template('cursos.html', courses=courses)

@app.route('/cursos/<int:course_id>')
def curso_detalle(course_id):
    course = courses[course_id] if 0 <= course_id < len(courses) else None
    tasks = course_tasks.get(course_id, [])
    return render_template('curso_detalle.html', course=course, tasks=tasks, course_id=course_id)

@app.route('/proyectos')
def proyectos_view():
    return render_template('proyectos.html', proyectos=proyectos)

@app.route('/proyectos/<int:proyecto_id>', methods=['GET', 'POST'])
def proyecto_detalle(proyecto_id):
    if proyecto_id < 0 or proyecto_id >= len(proyectos):
        return redirect(url_for('proyectos_view'))
    proyecto = proyectos[proyecto_id]
    objetivos = proyectos_objetivos.get(proyecto_id, [])
    if request.method == 'POST':
        objetivo = request.form.get('objetivo')
        if objetivo:
            if proyecto_id not in proyectos_objetivos:
                proyectos_objetivos[proyecto_id] = []
            proyectos_objetivos[proyecto_id].append({'texto': objetivo, 'cumplido': False})
    return render_template('proyecto_detalle.html', proyecto=proyecto, objetivos=objetivos, proyecto_id=proyecto_id)

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task')
    date = request.form.get('date')
    time = request.form.get('time')
    if task:
        # Combina fecha y hora en un solo string o datetime
        datetime_str = f"{date} {time}" if date and time else None
        tasks.append({'name': task, 'done': False, 'datetime': datetime_str, 'date': date})
        flash('Tarea agregada correctamente.', 'success')
    else:
        flash('Debes ingresar una tarea.', 'danger')
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    name = request.form.get('edit_name')
    date = request.form.get('edit_date')
    time = request.form.get('edit_time')
    if 0 <= task_id < len(tasks):
        if name:
            tasks[task_id]['name'] = name
        if date:
            tasks[task_id]['date'] = date
        if date and time:
            tasks[task_id]['datetime'] = f"{date} {time}"
        flash('Tarea editada correctamente.', 'success')
    else:
        flash('No se pudo editar la tarea.', 'danger')
    return redirect(url_for('index'))

@app.route('/done/<int:task_id>')
def mark_done(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]['done'] = not tasks[task_id]['done']
        flash('Estado de la tarea actualizado.', 'info')
    else:
        flash('No se pudo actualizar la tarea.', 'danger')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        flash('Tarea eliminada.', 'warning')
    else:
        flash('No se pudo eliminar la tarea.', 'danger')
    return redirect(url_for('index'))

@app.route('/tasks_by_date/<date>')
def tasks_by_date(date):
    filtered = [t for t in tasks if t.get('date') == date]
    return jsonify(filtered)

@app.route('/note/<date>', methods=['POST'])
def save_note(date):
    note = request.form.get('note')
    day_notes[date] = note
    return ('', 204)

@app.route('/get_note/<date>')
def get_note(date):
    return jsonify({'note': day_notes.get(date, '')})

@app.route('/cursos/add', methods=['POST'])
def add_curso():
    name = request.form.get('name')
    description = request.form.get('description')
    if name and description:
        courses.append({'name': name, 'description': description})
        flash('Curso agregado correctamente.', 'success')
    else:
        flash('Debes ingresar nombre y descripción.', 'danger')
    return redirect(url_for('cursos'))

@app.route('/cursos/<int:course_id>/add_task', methods=['POST'])
def add_curso_task(course_id):
    task = request.form.get('task')
    date = request.form.get('date')
    if task:
        if course_id not in course_tasks:
            course_tasks[course_id] = []
        course_tasks[course_id].append({'name': task, 'date': date, 'done': False})
        flash('Tarea agregada al curso.', 'success')
    else:
        flash('Debes ingresar una tarea.', 'danger')
    return redirect(url_for('curso_detalle', course_id=course_id))

@app.route('/cursos/<int:course_id>/done_task/<int:task_id>')
def done_curso_task(course_id, task_id):
    if course_id in course_tasks and 0 <= task_id < len(course_tasks[course_id]):
        course_tasks[course_id][task_id]['done'] = not course_tasks[course_id][task_id]['done']
        flash('Estado de la tarea del curso actualizado.', 'info')
    else:
        flash('No se pudo actualizar la tarea del curso.', 'danger')
    return redirect(url_for('curso_detalle', course_id=course_id))

@app.route('/proyectos/add', methods=['POST'])
def add_proyecto():
    name = request.form.get('name')
    description = request.form.get('description')
    if name and description:
        proyectos.append({'name': name, 'description': description})
        flash('Proyecto agregado correctamente.', 'success')
    else:
        flash('Debes ingresar nombre y descripción.', 'danger')
    return redirect(url_for('proyectos_view'))

@app.route('/proyectos/<int:proyecto_id>/objetivo/<int:objetivo_id>/toggle')
def toggle_objetivo(proyecto_id, objetivo_id):
    if proyecto_id in proyectos_objetivos and 0 <= objetivo_id < len(proyectos_objetivos[proyecto_id]):
        proyectos_objetivos[proyecto_id][objetivo_id]['cumplido'] = not proyectos_objetivos[proyecto_id][objetivo_id]['cumplido']
    return redirect(url_for('proyecto_detalle', proyecto_id=proyecto_id))

@app.route('/cursos/<int:course_id>/delete', methods=['POST'])
def delete_curso(course_id):
    if 0 <= course_id < len(courses):
        courses.pop(course_id)
        # Eliminar también las tareas asociadas a ese curso
        if course_id in course_tasks:
            del course_tasks[course_id]
        # Reindexar course_tasks para mantener consistencia de IDs
        new_course_tasks = {}
        for idx, key in enumerate(sorted(course_tasks.keys())):
            new_course_tasks[idx] = course_tasks[key]
        course_tasks.clear()
        course_tasks.update(new_course_tasks)
        flash('Curso eliminado correctamente.', 'warning')
    else:
        flash('No se pudo eliminar el curso.', 'danger')
    return redirect(url_for('cursos'))

# Configuración para la carga de archivos estáticos
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Crear carpeta uploads si no existe
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Establecer carpeta uploads como carpeta de carga
app.config['UPLOAD_FOLDER'] = 'uploads'

if __name__ == '__main__':
    app.run(debug=True)
