from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, session
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from functools import wraps
import csv
import io
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

ADMIN_PASSWORD = 'admin2026'

# Configuração da base de dados PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id SERIAL PRIMARY KEY,
                grau_satisfacao TEXT NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                dia_semana TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.commit()
    conn.close()

if DATABASE_URL:
    init_db()

DIAS_SEMANA = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registar', methods=['POST'])
def registar():
    data = request.get_json()
    grau = data.get('grau')
    
    if grau not in ['muito_satisfeito', 'satisfeito', 'insatisfeito']:
        return jsonify({'error': 'Grau inválido'}), 400
    
    agora = datetime.now()
    data_str = agora.strftime('%Y-%m-%d')
    hora_str = agora.strftime('%H:%M:%S')
    dia_semana = DIAS_SEMANA[agora.weekday()]
    
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO avaliacoes (grau_satisfacao, data, hora, dia_semana)
            VALUES (%s, %s, %s, %s)
        ''', (grau, data_str, hora_str, dia_semana))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Obrigado pela sua avaliação!'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Password incorreta'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin_2026')
@login_required
def admin():
    return render_template('admin.html')

@app.route('/admin_2026/estatisticas')
@login_required
def estatisticas():
    data_filtro = request.args.get('data', None)
    
    conn = get_db()
    with conn.cursor() as cur:
        if data_filtro:
            cur.execute('''
                SELECT grau_satisfacao, COUNT(*) as total
                FROM avaliacoes
                WHERE data = %s
                GROUP BY grau_satisfacao
            ''', (data_filtro,))
        else:
            cur.execute('''
                SELECT grau_satisfacao, COUNT(*) as total
                FROM avaliacoes
                GROUP BY grau_satisfacao
            ''')
        rows = cur.fetchall()
    
    stats = {
        'muito_satisfeito': 0,
        'satisfeito': 0,
        'insatisfeito': 0
    }
    
    for row in rows:
        stats[row['grau_satisfacao']] = row['total']
    
    total = sum(stats.values())
    percentagens = {}
    for k, v in stats.items():
        percentagens[k] = round((v / total * 100), 1) if total > 0 else 0
    
    conn.close()
    
    return jsonify({
        'totais': stats,
        'percentagens': percentagens,
        'total_geral': total
    })

@app.route('/admin_2026/historico')
@login_required
def historico():
    data_filtro = request.args.get('data', None)
    pagina = int(request.args.get('pagina', 1))
    limite = int(request.args.get('limite', 20))
    offset = (pagina - 1) * limite
    
    conn = get_db()
    with conn.cursor() as cur:
        if data_filtro:
            cur.execute('''
                SELECT * FROM avaliacoes
                WHERE data = %s
                ORDER BY data DESC, hora DESC
                LIMIT %s OFFSET %s
            ''', (data_filtro, limite, offset))
            rows = cur.fetchall()
            cur.execute('''
                SELECT COUNT(*) FROM avaliacoes WHERE data = %s
            ''', (data_filtro,))
            total_count = cur.fetchone()['count']
        else:
            cur.execute('''
                SELECT * FROM avaliacoes
                ORDER BY data DESC, hora DESC
                LIMIT %s OFFSET %s
            ''', (limite, offset))
            rows = cur.fetchall()
            cur.execute('SELECT COUNT(*) FROM avaliacoes')
            total_count = cur.fetchone()['count']
    
    registos = []
    for row in rows:
        registos.append({
            'id': row['id'],
            'grau_satisfacao': row['grau_satisfacao'],
            'data': row['data'],
            'hora': row['hora'],
            'dia_semana': row['dia_semana']
        })
    
    conn.close()
    
    return jsonify({
        'registos': registos,
        'total': total_count,
        'pagina': pagina,
        'total_paginas': (total_count + limite - 1) // limite
    })

@app.route('/admin_2026/datas')
@login_required
def datas_disponiveis():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute('''
            SELECT DISTINCT data FROM avaliacoes ORDER BY data DESC
        ''')
        rows = cur.fetchall()
    conn.close()
    
    datas = [row['data'] for row in rows]
    return jsonify({'datas': datas})

@app.route('/admin_2026/exportar/csv')
@login_required
def exportar_csv():
    data_filtro = request.args.get('data', None)
    
    conn = get_db()
    with conn.cursor() as cur:
        if data_filtro:
            cur.execute('''
                SELECT * FROM avaliacoes WHERE data = %s ORDER BY data DESC, hora DESC
            ''', (data_filtro,))
        else:
            cur.execute('''
                SELECT * FROM avaliacoes ORDER BY data DESC, hora DESC
            ''')
        rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['ID', 'Grau de Satisfação', 'Data', 'Hora', 'Dia da Semana'])
    
    grau_labels = {
        'muito_satisfeito': 'Muito Satisfeito',
        'satisfeito': 'Satisfeito',
        'insatisfeito': 'Insatisfeito'
    }
    
    for row in rows:
        writer.writerow([
            row['id'],
            grau_labels.get(row['grau_satisfacao'], row['grau_satisfacao']),
            row['data'],
            row['hora'],
            row['dia_semana']
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=avaliacoes.csv'}
    )

@app.route('/admin_2026/exportar/txt')
@login_required
def exportar_txt():
    data_filtro = request.args.get('data', None)
    
    conn = get_db()
    with conn.cursor() as cur:
        if data_filtro:
            cur.execute('''
                SELECT * FROM avaliacoes WHERE data = %s ORDER BY data DESC, hora DESC
            ''', (data_filtro,))
        else:
            cur.execute('''
                SELECT * FROM avaliacoes ORDER BY data DESC, hora DESC
            ''')
        rows = cur.fetchall()
    conn.close()
    
    grau_labels = {
        'muito_satisfeito': 'Muito Satisfeito',
        'satisfeito': 'Satisfeito',
        'insatisfeito': 'Insatisfeito'
    }
    
    lines = ['RELATÓRIO DE AVALIAÇÕES DE SATISFAÇÃO', '=' * 50, '']
    
    for row in rows:
        lines.append(f"ID: {row['id']}")
        lines.append(f"Satisfação: {grau_labels.get(row['grau_satisfacao'], row['grau_satisfacao'])}")
        lines.append(f"Data: {row['data']}")
        lines.append(f"Hora: {row['hora']}")
        lines.append(f"Dia: {row['dia_semana']}")
        lines.append('-' * 30)
    
    return Response(
        '\n'.join(lines),
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment; filename=avaliacoes.txt'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
