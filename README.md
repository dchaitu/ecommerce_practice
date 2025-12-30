# Ecommerce Practice API

## Authentication

### Register
**POST** `/register/`
```json
{
    "username": "testuser",
    "password": "testpassword123",
    "email": "test@example.com"
}
```

### Login
**POST** `/login/`
```json
{
    "username": "testuser",
    "password": "testpassword123"
}
```
*Returns: `access` and `refresh` tokens (if using JWT) or session cookies depending on setup. Assuming session auth for this example given `IsAuthenticated` usage without explicit JWT setup shown in snippets.*

---

## Products

### List Products
**GET** `/products/`
**Query Params:**
- `gender`: Men, Women, Kids, Unisex
- `category`: topwear, bottomwear, etc.
- `brand`: Brand Name
- `min_price`: 10
- `max_price`: 100

### Get Product Details
**GET** `/products/<id>/`

---

## Cart

### View Cart
**GET** `/cart/`
*Requires Authentication*

### Add to Cart
**POST** `/cart/`
*Requires Authentication*
```json
{
    "product_id": 1,
    "quantity": 2
}
```
*Note: Ensure `product_id` corresponds to an existing product ID.*

### Clear Cart
**DELETE** `/cart/`
*Requires Authentication*

---

## Orders

### Create Order / Initialize Payment
**POST** `/payment-create/`
*Requires Authentication*

This endpoint initializes a Razorpay order based on the current user's cart total. 

**Request Body:**
No specific parameters are required in the body as it uses the authenticated user's active cart. You can send an empty JSON object.
```json
{}
```

**Response:**
```json
{
    "order_id": "order_Kz...",
    "amount": 5000,
    "currency": "INR",
    "key": "rzp_test_...",
    "prefill": {
        "name": "testuser",
        "email": "test@example.com"
    }
}
```
*Creates a local Order record and returns Razorpay order details used to open the payment modal.*

### Verify Payment
**POST** `/payment-verify/`
*Requires Authentication*
```json
{
    "razorpay_order_id": "order_Kz...",
    "razorpay_payment_id": "pay_Lb...",
    "razorpay_signature": "e96..."
}
```
*On success, updates Order to `is_paid=True` and clears the Cart.*
