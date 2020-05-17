import pymysql
from app import app
from db_config import mysql
from flask import jsonify
from flask import flash, request


@app.route('/get_task_queue')
def get_task_queue():
    conn = mysql.connect()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM task_queue")
        rows = cursor.fetchall()
        resp = jsonify(rows)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    conn.close()


@app.route('/remove_task/<int:task_queue_id>')
def remove_task(task_queue_id):
    conn = mysql.connect()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM task_queue WHERE task_queue_id=%s", (task_queue_id,))
        conn.commit()
        resp = jsonify('User deleted successfully!')
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    conn.close()


@app.route('/get_task_definition/<int:task_def_id>')
def get_task_definition(task_def_id):
    conn = mysql.connect()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM task_definition WHERE task_def_id = %s", task_def_id)
        row = cursor.fetchone()
        resp = jsonify(row)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    conn.close()


@app.route('/insert_into_task_history', methods=['POST'])
def insert_into_task_history():
    conn = mysql.connect()
    try:
        _json = request.json
        _task_def_id = _json['task_def_id']
        _task_info = _json['task_info']
        _status_id = _json['status_id']
        if _task_def_id and _task_info and _status_id and request.method == 'POST':
            sql = "INSERT INTO task_history(task_def_id, task_info, status_id) VALUES(%s, %s, %s)"
            data = (_task_def_id, _task_info, _status_id,)
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            resp = jsonify('User added successfully!')
            resp.status_code = 200
            return resp
        else:
            return not_found()
    except Exception as e:
        print(e)
    conn.close()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == "__main__":
    app.run()
