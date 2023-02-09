from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify
from ariadne \
    import gql, QueryType, MutationType, make_executable_schema, graphql_sync
from utils import WorkOrderType
import re


type_defs = gql(
    """
    type Query {
        work_orders: [WorkOrder],
        customer: [Customer]
    }

    type WorkOrder {
        work_order_id: ID!
        work_order_type: String!
        schedule: String!
        customer_id: ID!
        }  
    
    type Customer {
        id: ID!
        first_name: String!
        last_name: String!
        address: String!
        emaiL_address: String!
        phone_number: String!
        }

    type Mutation{add_work_order(work_order_type: String!, schedule: String!, 
    customer_id: String!): WorkOrder,
    work_order_by_id(work_order_id:ID!): WorkOrder}

    """

)


query = QueryType()
mutation = MutationType()


@query.field("work_orders")
def work_orders(*_):
    return [work_order.to_json() for work_order in WorkOrder.query.all()]


@mutation.field("work_order_by_id")
def work_order_by_id(_, info, work_order_id):
    try:
        work_order = db.session.get(WorkOrder,work_order_id)
        payload = work_order.to_json()
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Work order matching id {work_order_id} not found"]
        }
    return payload


@mutation.field("add_work_order")
def add_work_order(_, info, work_order_type, schedule, customer_id):
    if work_order_type not in set(item.value for item in WorkOrderType):
        raise Exception({"success": False,
                         "errors": "Work Order Type must be 'install' "
                                   "or 'service call'"})

    work_order = WorkOrder(work_order_type=WorkOrderType(work_order_type),
                           schedule=schedule, customer_id=customer_id)
    work_order.save()
    return work_order.to_json()


schema = make_executable_schema(type_defs, [query, mutation])

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    work_order = db.relationship('WorkOrder', backref='customer')

    def to_json(self):
        return {
               "id": self.id,
               "first_name": self.first_name,
               "last_name": self.last_name,
               "address": self.address,
               "email_address": self.email_address,
               "phone_number": self.phone_number,
         }

    def save(self):
        db.session.add(self)
        db.session.commit()


class WorkOrder(db.Model):
    work_order_id = db.Column(db.Integer, primary_key=True)
    work_order_type = db.Column(db.Enum(WorkOrderType),
                                default=WorkOrderType.service_call,
                                nullable=False)
    schedule = db.Column(db.TEXT, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

    def to_json(self):
        return {
            "work_order_id": self.work_order_id,
            "work_order_type": self.work_order_type.value,
            "schedule": self.schedule,
            "customer_id": self.customer_id
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data,
                                   context_value={"request": request})
    status_code = 200 if success else 400
    return jsonify(result), status_code


@app.route("/work_orders", methods=["GET"])
def get_all_work_orders():
    return [work_order.to_json() for work_order in WorkOrder.query.all()]


@app.route("/work_order/<string:work_order_id>", methods=["POST"])
def get_work_order_by_id(work_order_id):
    try:
        work_order = db.session.get(WorkOrder, work_order_id)
        payload = work_order.to_json()
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Work order matching id {work_order_id} not found."]
        }

    return payload


@app.route("/add/work_order", methods=["POST"])
def create_work_order():
    work_order_type = request.form.get('work_order_type')
    schedule = request.form.get('schedule')
    customer_id = request.form.get('customer_id')
    if work_order_type not in set(item.value for item in WorkOrderType):
        return {"success": False,
                "errors": "Work Order Type must be 'install' "
                          "or 'service call'"}
    if not db.session.get(Customer, customer_id):
        return {"success": False,
                "errors": f"Customer id {customer_id} not found."}
    try:
        work_order = WorkOrder(work_order_type=WorkOrderType(work_order_type),
                               schedule=schedule, customer_id=customer_id)
        work_order.save()
    except Exception as e:
        return {"success": False,
                "errors": f"Missing argument: {e}"}

    return work_order.to_json()


@app.route("/customers", methods=["GET"])
def get_all_customers():
    return [customer.to_json() for customer in Customer.query.all()]


@app.route("/customer/<string:customer_id>", methods=["POST"])
def get_customer_by_id(customer_id):
    try:
        customer = db.session.get(Customer, customer_id)
        payload = customer.to_json()
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Customer matching id {customer_id} not found."]
        }

    return payload


@app.route("/add/customer", methods=["POST"])
def create_customer():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    address = request.form.get("address")
    email_address = request.form.get("email_address")
    phone_number = request.form.get("phone_number")

    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    romanian_phone_number_regex = r'\+4\d{10}|\d{10}'
    if not re.match(email_regex, email_address):
        return {"success": False,
                "errors": "Email address seems invalid"}
    if not re.match(romanian_phone_number_regex, phone_number):
        return {"success": False,
                "errors": "Romanian phone number seems invalid"}

    try:
        customer = Customer(first_name=first_name, last_name=last_name,
                            address=address, email_address=email_address,
                            phone_number=phone_number)
        customer.save()
    except Exception as e:
        return {"success": False,
                "errors": f"Missing argument: {e}"}

    return customer.to_json()


if __name__ == "__main__":
    app.run(debug=True)
