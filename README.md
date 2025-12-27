# E-commerce App Enhancement Walkthrough

I have successfully enhanced the e-commerce application with new models, serializers, views, and data population.

## Changes Verified

### 1. Data Models (`api/models.py`)
- **User**: Custom user model linked to `settings.AUTH_USER_MODEL`.
- **Product**: Added `gender` field and linked it to a custom `ProductQuerySet` via `ProductManager` for chainable filtering.
- **Cart & CartItem**: Implemented cart functionality linked to the user.

### 2. Serializers (`api/serializers.py`)
- Updated `ProductSerializer` to include new fields.
- Created `CartSerializer` and `CartItemSerializer` to handle cart operations.

### 3. API Views (`api/views.py`)
- **ProductListCreate**: Supports rich filtering and sorting:
    - `gender`: Filter by gender (e.g., `?gender=Men`).
    - `category`: Filter by category.
    - `brand`: Filter by brand name.
    - `min_price` / `max_price`: Filter by price range.
    - `ordering`: Sort by price (`?ordering=price` or `?ordering=-price`).
- **CartView**: Handles `GET` (view cart), `POST` (add item/update quantity), and `DELETE` (clear cart).

### 4. Data Population
- Created and executed a script `populate_data.py` that generated brands and random products.

## Verification Scenarios

### Product Filtering
Verified that products can be filtered by gender and price range.
```bash
curl "http://127.0.0.1:8000/api/products/?gender=Men&price=10&price__lt=100"
```

### Cart Operations
Verified adding items to the cart, retrieving the cart, and emptying the cart using a python script.

```python
# snippet from verify_cart.py
response = requests.post(
    f'{BASE_URL}/cart/',
    json={'product_id': product_id, 'quantity': 2},
    auth=AUTH
)
```

## Next Steps
- You can explore the API using `curl` or Postman.
- The server is currently running on port 8000.
