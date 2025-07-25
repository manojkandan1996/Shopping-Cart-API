from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, NotFound

app = Flask(__name__)
api = Api(app)

cart = []
item_id_counter = 1

class CartListResource(Resource):
    def get(self):
        return {"cart_items": cart}, 200

    def post(self):
        global item_id_counter
        data = request.get_json()

        if not data or 'product_name' not in data or 'quantity' not in data or 'price' not in data:
            raise BadRequest("Fields 'product_name', 'quantity', and 'price' are required.")

        try:
            quantity = int(data['quantity'])
            price = float(data['price'])
            if quantity <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            raise BadRequest("Quantity and price must be positive numbers.")

        item = {
            'id': item_id_counter,
            'product_name': data['product_name'],
            'quantity': quantity,
            'price': price
        }
        cart.append(item)
        item_id_counter += 1

        return {"message": "Item added to cart", "item": item}, 201

class CartItemResource(Resource):
    def put(self, id):
        data = request.get_json()
        item = next((i for i in cart if i['id'] == id), None)
        if not item:
            raise NotFound("Cart item not found.")

        if 'product_name' in data:
            item['product_name'] = data['product_name']
        if 'quantity' in data:
            try:
                qty = int(data['quantity'])
                if qty <= 0:
                    raise ValueError
                item['quantity'] = qty
            except ValueError:
                raise BadRequest("Quantity must be a positive integer.")
        if 'price' in data:
            try:
                pr = float(data['price'])
                if pr <= 0:
                    raise ValueError
                item['price'] = pr
            except ValueError:
                raise BadRequest("Price must be a positive number.")

        return {"message": "Cart item updated", "item": item}, 200

    def delete(self, id):
        global cart
        item = next((i for i in cart if i['id'] == id), None)
        if not item:
            raise NotFound("Cart item not found.")

        cart = [i for i in cart if i['id'] != id]
        return {"message": f"Item {id} removed from cart"}, 200

class CartTotalResource(Resource):
    def get(self):
        total = sum(i['quantity'] * i['price'] for i in cart)
        return {"total_price": total}, 200

# Register routes
api.add_resource(CartListResource, '/cart')
api.add_resource(CartItemResource, '/cart/<int:id>')
api.add_resource(CartTotalResource, '/cart/total')

if __name__ == '__main__':
    app.run(debug=True)
