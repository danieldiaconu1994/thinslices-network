# thinslices-network

This repository contains a simple Flask application with a SQLite database that
implements three endpoints: GET ALL, GET by ID, and POST for customers and
work orders. The application uses Flask, Flask-SQLAlchemy and Alembic for 
database migrations.

## Instalation
1. Clone the repository to your machine using link: 
https://github.com/danieldiaconu1994/thinslices-network.git
2. Go to the project directory: cd thinslices-network
3. Build the docker image using: docker build ./ -t thinslices_network
4. Run the docker container using: docker run -p 5000:5000 --name 
thinslices_network thinslices_network
5. After closing the session you can run by using: docker start thinslices_network

## Usage

The base link for the application is http://localhost:5000

### Add customer to the database
endpoint: /add/customer 

method: POST

BODY: form-data

Form fields: first_name:String, last_name:String, address:String, 
email_address:String, phone_number:String

If success responds with the newly created customer in json

### Get all customers from the database
endpoint: /customers

method: GET

If success responds with a list of all customers in json.

### Get customer by id

endpoint: /customer/id

id: In positive int included in the url

If success responds with the customer in json.

### Add work order to the database

endpoint: /add/work_order 

method: POST

BODY: form-data

Form fields: work_order_type:String (install/service call), 
schedule:String(the date to execute the work order),customer_id:Int(an existing 
customer id)


If success responds with the newly created customer in json.

### Get all work orders
endpoint: /work_orders

method: GET

If success responds with a list of all work orders in json.

### Get work order by id
endpoint: /work_order/id

id: In positive int included in the url

If success responds with the work order in json.

## Testing
If you want to run the unit tests manually without building the docker first run
init_db.sh using ./init_db.sh in the project directory then run python -m unittest discover