#!/usr/bin/env python3
import random
import json
import sqlite3
import time

from flask import Flask, make_response, request, render_template, redirect, session, url_for
app = Flask(__name__)

def create_db():
    conn = sqlite3.connect('database.db')

    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS violations (id integer PRIMARY KEY, violation_text text, reporter text, ts integer)''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes (id integer PRIMARY KEY, violation_id integer, voter text, drunkenness integer, lack_of_love integer, obviousness, ts integer)''')
    conn.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM violations LEFT JOIN votes ON votes.violation_id = violations.id AND votes.voter = :username', {'username': session['username']})
    rows = c.fetchall()
    c.execute('SELECT violations.reporter, (SUM(votes.drunkenness) + SUM(votes.lack_of_love) + SUM(votes.obviousness)) AS score FROM violations JOIN votes ON votes.violation_id = violations.id AND votes.voter != violations.reporter GROUP BY violations.reporter ORDER BY score DESC')
    top = c.fetchall()
    return render_template('index.html', rows=rows, top=top)

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO violations (ts, reporter, violation_text) VALUES (:ts, :reporter, :text)', {'ts': time.time(), 'reporter': session['username'], 'text': request.form['violation_text']})
        conn.commit()
        return redirect('/')
    else:
        return render_template('report.html')

@app.route('/vote/<int:violation_id>', methods=['POST'])
def vote(violation_id):
    data = {'ts': time.time(), 'voter': session['username'],
            'id': violation_id,
        'drunkenness': request.form['drunkenness'],
        'lack_of_love': request.form['lack_of_love'],
        'obviousness': request.form['obviousness']}
    for key in 'drunkenness', 'lack_of_love', 'obviousness':
        val = data[key]
        if not val:
            return redirect('/')
        val = int(val)
        if not (1 <= val <= 5):
            return redirect('/')
        data[key] = val

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM votes WHERE violation_id = :id AND voter = :voter', data)
    c.execute('INSERT INTO votes (violation_id, voter, drunkenness, lack_of_love, obviousness, ts) VALUES (:id, :voter, :drunkenness, :lack_of_love, :obviousness, :ts)', data)
    conn.commit()
    return redirect('/')



if __name__ == '__main__':
    create_db()
    app.secret_key = 'WT5YorH6jDjS8Qdw6acPedeLnoVqi6dg216LzwR4M1F4fburo4DRSJ6aIaoq9hLV'
    app.run(host='::', port=8080, debug=True)

