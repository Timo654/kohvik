from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import json
from pathlib import Path
import shutil

app = Flask(__name__, static_folder="./webgl_app/static",
            template_folder="./webgl_app/templates")
CORS(app)
script_dir = Path(__file__).parent
db_file = script_dir / "db" / "cafe.db"
empty_db = script_dir / "./db" / "empty_db.db"
if not db_file.exists():
    if empty_db.exists():
        shutil.copy(empty_db, db_file)

prod = False  # if production or development
# GET REQUESTS


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/getOrders', methods=['GET'])
def get_orders():
    c = sqlite3.connect(db_file).cursor()
    c.execute("select 'order'.order_id from 'order' where 'order'.status == 0")
    data = c.fetchall()
    new_data = list()
    for item in data:
        x = dict()
        x["ID"] = item[0]
        new_data.append(x)
    return new_data


@app.route('/getReadyOrders', methods=['GET'])
def get_ready_orders():
    c = sqlite3.connect(db_file).cursor()
    c.execute("select 'order'.order_id from 'order' where 'order'.status == 1")
    data = c.fetchall()
    new_data = list()
    for item in data:
        x = dict()
        x["ID"] = item[0]
        new_data.append(x)
    return new_data


@app.route('/totalSales', methods=['GET'])
def get_total_sales():
    c = sqlite3.connect(db_file).cursor()
    c.execute("""select sum(item.price * order_item.quantity * ((100 - 'order'.discount_percent) / 100.0)) as order_price from item
inner join order_item on item.item_id=order_item.item_id
inner join 'order' on 'order'.order_id=order_item.order_id where 'order'.status=2""")
    data = c.fetchone()[0]
    return jsonify(data)

@app.route('/getItems', methods=['GET'])
def get_items():
    c = sqlite3.connect(db_file).cursor()
    c.execute(
        "select item.item_id as id, item.name as item, item.price as item_price from item")
    data = c.fetchall()
    new_data = list()
    for item in data:
        x = dict()
        x["ID"] = item[0]
        x["Name"] = item[1]
        x["Price"] = item[2]
        new_data.append(x)
    return new_data

@app.route('/getMenuItems', methods=['GET'])
def get_menu_items():
    c = sqlite3.connect(db_file).cursor()
    c.execute(
        "select item.item_id as id, item.name as item, item.price as item_price from item where item.is_ingredient=0")
    data = c.fetchall()
    new_data = list()
    for item in data:
        x = dict()
        x["ID"] = item[0]
        x["Name"] = item[1]
        x["Price"] = item[2]
        new_data.append(x)
    return new_data

@app.route('/getPrice/<order_id>', methods=['GET'])
def get_order_price(order_id):
    order_id = int(order_id)
    c = sqlite3.connect(db_file).cursor()
    c.execute("""select sum(item.price * order_item.quantity) as order_price from item
inner join order_item on item.item_id=order_item.item_id
inner join 'order' on 'order'.order_id=order_item.order_id
where 'order'.order_id=?""", (order_id,))
    data = c.fetchone()
    return jsonify(data)


@app.route('/getOrderedItems/<order_id>', methods=['GET'])
def get_order_items(order_id):
    order_id = int(order_id)
    c = sqlite3.connect(db_file).cursor()
    c.execute("""select item.item_id as id, item.name as item, order_item.quantity as quantity from item
inner join order_item on item.item_id=order_item.item_id
inner join 'order' on 'order'.order_id=order_item.order_id
where 'order'.order_id=?""", (order_id,))
    data = c.fetchall()
    new_data = list()
    for item in data:
        x = dict()
        x["ID"] = item[0]
        x["Name"] = item[1]
        x["Count"] = item[2]
        new_data.append(x)
    return new_data

# PUT/POST REQUESTS

@app.route('/updateOrder/<order_id>', methods=['PUT', 'POST'])
def update_order_status(order_id):
    order_id = int(order_id)
    db = sqlite3.connect(db_file)
    c = db.cursor()
    status = int(request.form["status"])
    c.execute("UPDATE 'order' SET status = ? WHERE order_id=?",
              (status, order_id))
    db.commit()
    if status == 1:
        return json.dumps(f"Tellimus {order_id} märgiti valminuks.", ensure_ascii=False)
    elif status == 2:
        return json.dumps(f"Tellimus {order_id} üle antud.", ensure_ascii=False)
    else:
        return jsonify(f"Invalid status code.")


@app.route('/addOrder', methods=['POST'])
def add_order():
    db = sqlite3.connect(db_file)
    c = db.cursor()
    c.execute("INSERT INTO 'order'(status) VALUES (?)", "0")
    order_id = c.lastrowid
    c.execute("SELECT MAX(item_id) FROM item")
    item_count = c.fetchone()[0]
    add_count = 0
    for item in request.form:  # item id and quantity
        if item == "discount":
            c.execute(f"UPDATE 'order' SET discount_percent = {int(request.form[item])} where order_id = {order_id}")
        elif int(item) <= item_count:
            c.execute("INSERT INTO 'order_item' VALUES (?, ?, ?)",
                      (order_id, item, request.form[item]))
            add_count += 1
    if add_count:
        db.commit()
        return jsonify(order_id)
    else:
        db.rollback()
        return jsonify(False), 400


if __name__ == '__main__':
    if prod:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(debug=True, port=5000, host='0.0.0.0')
