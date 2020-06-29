# inventory_management
a web app for managing sales, purchasing and production operations for small companies

Vist : [https://demoinventorymanagement.herokuapp.com/](https://demoinventorymanagement.herokuapp.com/) to access the app

## Instruction to install and run the application
1. Install python3
2. Download this repository by using
``` bash
git clone https://github.com/temi92/inventory_management.git
```
3. Install the dependencies by 
``` bash
cd inventory_management && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```
4. Set environment  `DATABASE_URL` to a PostgreSQL database for example <br/>
``` bash
  postgresql://username:password@localhost/dbname
```
5. Start the app using `python app.py`
6. Visit [http://localhost:5000/](http://localhost:5000/) from your browser to access the app.

### Credentials
1. Username - demo
2. Password - password


### *Functionalites*
1. Create and manage customers
2. Add, Edit or Delete stock from warehouse
3. Track production in warehouse
3. Issue invoice for payment for customers
4. Track how much customer has paid for product.
5. Print invoices
