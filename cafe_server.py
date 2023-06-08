from flask import Flask, jsonify, request
from flask_cors import cross_origin
import sqlite3
import json

app = Flask(__name__)
db_file = "db/cafe_v2.db"
prod = False  # if production or development
# GET REQUESTS


@app.route('/getOrders', methods=['GET'])
@cross_origin()
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
@cross_origin()
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
@cross_origin()
def get_total_sales():
    c = sqlite3.connect(db_file).cursor()
    c.execute("""select sum(item.price * order_item.quantity) as order_price from item
inner join order_item on item.item_id=order_item.item_id
inner join 'order' on 'order'.order_id=order_item.order_id where 'order'.status=2""")
    data = c.fetchone()
    return jsonify(data)

@app.route('/getItems', methods=['GET'])
@cross_origin()
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

@app.route('/getPrice/<order_id>', methods=['GET'])
@cross_origin()
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
@cross_origin()
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
# TODO - ignore out of bounds values and figure out what values we actually need, could add a status for "deleted"?
# TODO - add status for ready-to-hand-out


@app.route('/updateOrder/<order_id>', methods=['PUT', 'POST'])
@cross_origin()
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
@cross_origin()
def add_order():
    db = sqlite3.connect(db_file)
    c = db.cursor()
    c.execute("INSERT INTO 'order'(status) VALUES (?)", "0")
    order_id = c.lastrowid
    c.execute("SELECT MAX(item_id) FROM item")
    item_count = c.fetchone()[0]
    add_count = 0
    for item in request.form:  # item id and quantity
        if int(item) <= item_count:
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
        serve(app, host="0.0.0.0", port=80)
    else:
        app.run(debug=True, port=80, host='0.0.0.0')
