# Odoo eCommerce API Documentation

**Module:** `website_sale_api`

This document describes the custom REST endpoints exposed by the `website_sale_api` Odoo module. All routes are plain HTTP JSON endpoints (`type="http"`, `auth="public"`, `csrf=False`), so requests should send `Content-Type: application/json` and a raw JSON body where noted.

---

## 1. Base URL

```
http://localhost:8069
```

All endpoint paths below are relative to this base URL.

## 2. Authentication

The API uses **two layers** of authentication, both enforced via decorators on the controller methods.

### 2.1 API Key (required on almost every endpoint)

Every route decorated with `@ApiKeyService.api_key_required()` requires a static API key header:

| Header | Value |
|---|---|
| `eco-smei-api-key` | Your API key |

If missing or invalid, the API returns:

```json
// 401
{ "error": "unauthorized", "message": "API key required. Please provide 'eco-smei-api-key' in headers", "code": 401 }
```

> ⚠️ The key is currently hard-coded in `api_key_service.py`. Treat it as a shared secret and replace it before any production deployment.

### 2.2 JWT Bearer Token (required on user-specific endpoints)

Routes decorated with `@JWTService.jwt_required()` additionally require a JWT obtained from `/api/auth/login` or `/api/auth/register`:

| Header | Value |
|---|---|
| `Authorization` | `Bearer <token>` |

- Token expiry: **120 minutes**
- Algorithm: `HS256`
- Payload: `{ uid, login, website_id, exp, iat }`
- On failure, returns `401` with `{ "status": "fail", "message": "..." }`

**Order of decorators on protected routes:** `@ApiKeyService.api_key_required()` → `@JWTService.jwt_required()`. Both headers must be present together on those routes.

## 3. Response Envelope

**Success (`BaseAPI._success`)** — HTTP 200:
```json
{ "status": "success", ...fields merged or nested under "data"... }
```

**Error (`BaseAPI._error`)** — configurable status code (usually 400/401/403/500):
```json
{ "status": "fail", "message": "Description of the error" }
```

**Paginated resources** (products, categories via list, orders, invoices, reviews) share this shape:
```json
{
  "status": "success",
  "data": [ /* array of items */ ],
  "total": 42,
  "page": 1,
  "size": 10,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```
Pagination query params: `page` (default `1`), `size` (default `10`).

---

## 4. Endpoints

### 4.1 Authentication — `/api/auth/*`

#### POST `/api/auth/login`
Auth: API key only.
**Body:**
```json
{ "login": "user@example.com", "password": "secret" }
```
**Response 200:**
```json
{ "status": "success", "token": "<jwt>" }
```
**Response 401:** `{ "status": "fail", "message": "Login & Password Incorrect!" }`

#### POST `/api/auth/register`
Auth: API key only.
**Body:**
```json
{ "name": "John Doe", "login": "user@example.com", "password": "secret" }
```
**Response 200:** `{ "status": "success", "token": "<jwt>" }`
**Errors:** `400` (validation/user error), `500` (unexpected)

#### POST `/api/auth/request_reset_password`
Auth: API key only. Sends an OTP code to the user's email.
**Body:** `{ "login": "user@example.com" }`
**Response 200:** `{ "status": "success", "message": "OTP code is sent to this email user@example.com" }`

#### POST `/api/auth/otp_verity`
Auth: API key only. Verifies the OTP code sent above.
**Body:** `{ "login": "user@example.com", "code": "123456" }`
**Response 200:** `{ "status": "success", "message": "<validation message>" }`
**Response 400:** invalid/expired code

#### POST `/api/auth/reset_password`
Auth: API key only. Sets a new password (typically called after OTP verification).
**Body:** `{ "login": "user@example.com", "password": "newSecret" }`
**Response 200:** `{ "status": "success", "message": "Password changed successfully" }`

#### POST `/api/auth/logout`
Auth: API key + JWT.
**Response 200:** `{ "status": "success", "message": "Logout successful" }`

#### POST `/api/auth/refresh`
Auth: API key + JWT (**expired tokens are accepted** — `skip_expiry=True`).
**Response 200:** `{ "status": "success", "token": "<new jwt>" }`

#### POST `/api/auth/change_password`
Auth: API key + JWT.
**Body:** `{ "old_password": "secret", "new_password": "newSecret" }`
**Response 200:** `{ "status": "success", "message": "Password changed successfully." }`
**Errors:** `403` old password incorrect, `400` new/old identical or validation, `500` unexpected

---

### 4.2 Profile — `/api/auth/profile*`

#### GET `/api/auth/profile`
Auth: API key + JWT.
**Response 200:**
```json
{
  "status": "success",
  "data": {
    "id": 1, "login": "user@example.com", "name": "John Doe",
    "email": "user@example.com", "phone": "+959...",
    "street": "...", "city": "...", "country_id": 1,
    "company_id": 1, "company_name": "My Company",
    "image_url": "<url>"
  }
}
```

Profile fields are currently read-only through this API. There is no
`PUT /api/auth/profile` route in the current implementation.

#### PUT `/api/auth/profile/image`
Auth: API key + JWT.
**Body:** `multipart/form-data` with a file field named `image_url` (max 5 MB).
**Response 200:** `{ "status": "success", "id": 1, "message": "Profile Image updated successfully" }`

---

### 4.3 Addresses — `/api/countries/*`, `/api/my/address*`, `/api/order/address`

All require API key + JWT.

#### GET `/api/countries/{country_id}/states`
**Response 200:**
```json
{ "status": "success", "country_id": 1, "states": [{ "id": 1, "name": "Yangon" }] }
```

#### GET `/api/countries/{country_id}/townships`
**Response 200:**
```json
{ "status": "success", "country_id": 1, "townships": [{ "id": 1, "name": "Bahan", "state_id": 1 }] }
```

#### GET `/api/my/address`
Returns the authenticated user's own partner record plus all child addresses.
**Response 200:**
```json
{
  "status": "success",
  "addresses": [
    { "id": 12, "name": "John Doe", "email": "j@x.com", "phone": "...", "street": "...", "city": "...", "zip": "...", "type": "delivery", "country": 1, "state": 1, "township": 3 }
  ]
}
```

#### POST `/api/my/address`
Creates a new child address (shipping/billing) under the current user's partner.
**Body:** any valid `res.partner` fields, e.g. `{ "name": "...", "street": "...", "city": "...", "zip": "...", "country_id": 1, "state_id": 1, "township_id": 3, "type": "delivery" }`
**Response 200:** `{ "status": "success", "id": 15, "message": "New Address is created" }`

#### PUT `/api/my/address/{address_id}`
Updates an existing address. Must belong to the authenticated user (`address_id` in `user.child_ids`).
**Body:** partial `res.partner` fields to update.
**Response 200:** `{ "status": "success", "id": 15, "message": "Address updated successfully" }`
**Response 400:** `"Partner not allow"` if not owned by the user.

#### DELETE `/api/my/address/{partner_id}`
Deletes an address owned by the authenticated user.
**Response 200:** `{ "status": "success", "id": 15, "message": "Address deleted successfully" }`
**Response 400:** `"User not found"` if not owned by the user.

#### PUT `/api/order/address`
Updates the shipping/billing address fields directly on the current cart (`sale.order`).
**Body:** e.g. `{ "partner_shipping_id": 15, "partner_invoice_id": 15 }`
**Response 200:** `{ "status": "success", "order_id": 21, "message": "Address update successfully" }`

---

### 4.4 Categories — `/api/categories`

#### GET `/api/categories`
Auth: API key only.
**Query params:** `page`, `size`
**Response 200:**
```json
{
  "status": "success",
  "data": [
    { "id": 4, "name": "Shoes", "parent_id": null, "image_256": "<url>", "child_ids": [10, 11] }
  ]
}
```
> Note: this endpoint does not go through the pagination envelope (`total`/`page`/etc. are not returned) — it returns `data` only.

---

### 4.5 Products — `/api/products*`

#### GET `/api/products`
Auth: API key only.
**Query params:** `page` (default 1), `size` (default 10)
**Response 200:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 5, "name": "Running Shoe", "description": "...",
      "price": 100.0, "sale_price": 90.0, "discount_amount": 10.0, "discount_type": "percentage",
      "currency": "USD", "currency_id": 1, "category_id": [4],
      "rating": 4.5, "review_count": 12,
      "allow_out_of_stock_order": false, "stock_qty": 20.0,
      "images": "<url>"
    }
  ],
  "total": 30, "page": 1, "size": 10, "total_pages": 3, "has_next": true, "has_prev": false
}
```

#### GET `/api/products/{product_id}`
Auth: API key only. Returns all sellable variants for the given `product.template` id.
**Response 200:**
```json
{
  "status": "success",
  "data": {
    "id": 5,
    "variants": [
      {
        "id": 55, "name": "Running Shoe (Red, 42)", "description": "...",
        "price": 100.0, "sale_price": 90.0, "discount_amount": 10.0, "discount_type": "percentage",
        "currency": "USD", "currency_id": 1, "category_id": [4],
        "rating": 4.5, "review_count": 12, "allow_out_of_stock_order": false, "stock_qty": 5.0,
        "attributes": { "Color": "Red,#ff0000", "Size": "42" },
        "images": ["<url1>", "<url2>"]
      }
    ]
  }
}
```
**Response 400:** `"No Product found!"` if the template doesn't exist / isn't published on this website.

---

### 4.6 Product Reviews — `/api/product/{id}/reviews`, `/api/reviews/{rating_id}`

#### GET `/api/product/{product_template_id}/reviews`
Auth: API key only.
**Query params:** `page`, `size`
**Response 200:**
```json
{
  "status": "success",
  "average_rating": 4.3,
  "data": [
    { "id": 9, "customer_id": 3, "customer_name": "Jane", "rating": 5.0, "date": "2026-01-01T10:00:00", "comment": "Great!", "image": "<url>" }
  ],
  "total": 8, "page": 1, "size": 10, "total_pages": 1, "has_next": false, "has_prev": false
}
```

#### POST `/api/product/{product_template_id}/reviews`
Auth: API key + JWT.
**Body:** `{ "rating_value": 5, "feedback": "Loved it" }` (`feedback` optional)
**Response 200:** `{ "status": "success", "id": 21, "message": "Comment created successfully" }`

#### PUT `/api/reviews/{rating_id}`
Auth: API key + JWT. Only the review's owner may edit it.
**Body:** `{ "feedback": "Updated comment" }`
**Response 200:** `{ "status": "success", "id": 21, "message": "Comment updated successfully" }`

#### DELETE `/api/reviews/{rating_id}`
Auth: API key + JWT. Only the review's owner may delete it.
**Response 200:** `{ "status": "success", "id": 21, "message": "Comment deleted successfully" }`

---

### 4.7 Banners & Ribbons

#### GET `/api/banners`
Auth: API key only.
**Response 200:**
```json
{ "status": "success", "data": [ { "id": 1, "description": "Summer Sale", "image_1920": "<url>" } ] }
```

#### GET `/api/product/ribbons`
Auth: API key only.
**Response 200:**
```json
{
  "status": "success",
  "data": [
    { "id": 1, "name": "Sale", "text_color": "#fff", "bg_color": "#f00", "position": "left", "style": "ribbon", "assign": "manual" }
  ]
}
```

---

### 4.8 Wishlist — `/api/wishlists*`

All require API key + JWT.

#### GET `/api/wishlists`
**Response 200:**
```json
{ "status": "success", "data": [ { "id": 7, "product_id": 5, "product_variant_id": 55 } ] }
```

#### POST `/api/wishlists`
**Body:** `{ "product_id": 55 }` (this is the `product.product` variant id)
**Response 200:** `{ "status": "success", "id": 7, "message": "Wishlist added" }`

#### DELETE `/api/wishlists/{wishlist_id}`
**Response 200:** `{ "status": "success", "id": 7, "message": "Wishlist deleted successfully" }`
**Response 400:** `"Wishlist not found"`

---

### 4.9 Cart — `/api/cart*`

All require API key + JWT.

#### GET `/api/cart`
**Response 200:**
```json
{
  "status": "success",
  "order_id": 21,
  "items": [
    { "line_id": 100, "product_id": 5, "product_variant_id": 55, "variant_name": "Running Shoe (Red, 42)", "product_name": "Running Shoe", "image_url": "<url>", "quantity": 2, "unit_price": 90.0, "subtotal": 180.0 }
  ],
  "untax_total": 180.0, "total": 180.0, "currency": "USD",
  "items_count": 1, "discount": 0, "shipping_fee": 0
}
```
If there's no order/cart yet: `{ "status": "success", "message": "No order found" }`. If the order has no lines: `{ "status": "success", "message": "No cart items found" }`.

#### POST `/api/cart`
Adds (or increments) a line in the user's cart, creating the cart/order if needed.
**Body:** `{ "product_id": 55, "qty": 2 }` (`product_id` here is the `product.product` variant id, matching Odoo's `_cart_add`)
**Response 200:** `{ "status": "success", "id": 21, "message": "Product added to cart" }`
**Response 400:** `"Product can't added to cart."`

#### DELETE `/api/cart/line/{line_id}`
Removes a specific order line from the current cart.
**Response 200:** `{ "status": "success", "id": 100, "message": "Order line deleted successfully" }`
**Response 400:** `"Order line {id} not found."`

---

### 4.10 Delivery Methods — `/api/delivery_methods`

All require API key + JWT.

#### GET `/api/delivery_methods`
Returns the delivery carriers available for the current cart.
**Response 200:**
```json
{
  "status": "success",
  "id": 3, "name": "Standard Delivery",
  "website_description": "...", "carrier_description": "...",
  "price": 5.0, "currency_id": 1
}
```
> Note: since `_success` merges dataclass fields directly (no `wrap_in_data`), the shape returned is the raw list content merged; in practice this route returns the delivery-method fields at top level per method in the underlying list.

#### POST `/api/delivery_methods`
Sets the delivery method on the current cart.
**Body:** `{ "delivery_method_id": 3 }`
**Response 200:**
```json
{ "status": "success", "order_id": 21, "delivery_amount": 5.0, "total_amount": 185.0, "message": "Delivery method has been added." }
```

---

### 4.11 Payment Methods — `/api/payment_methods`

Auth: API key + JWT.

#### GET `/api/payment_methods`
Returns payment methods available for the current cart's chosen delivery method / website.
**Response 200:**
```json
{ "status": "success", "data": [ { "id": 4, "name": "Credit Card" }, { "id": 6, "name": "Cash on Delivery" } ] }
```
**Response 400:** `"No payment methods found"`

---

### 4.12 Checkout — `/api/checkout`

Auth: API key + JWT.

#### POST `/api/checkout`
Runs the full checkout pipeline against the current cart: creates a payment transaction using the previously-selected payment method, processes it, validates the order (no pending payment errors, amounts match), and confirms it.
**Body:** whatever the underlying payment transaction needs, at minimum:
```json
{ "payment_method_id": 4 }
```
**Response 200:** `{ "status": "success", "id": 21, "message": "Checkout successfully" }`
**Response 400:** validation errors such as `"Your Cart is Empty!"`, `"The cart has been updated. Please refresh the page."`, or a payment error message.

---

### 4.13 Orders — `/api/orders*`

All require API key + JWT. Only confirmed orders (`state = "sale"`) belonging to the authenticated partner on the current website are returned.

#### GET `/api/orders`
**Query params:** `page`, `size`
**Response 200:**
```json
{
  "status": "success",
  "data": [
    { "id": 21, "name": "S00021", "reference": "...", "date_order": "2026-01-01T10:00:00", "status": "sale", "currency": "USD", "delivery_status": "...", "total": 185.0, "item_count": 1 }
  ],
  "total": 5, "page": 1, "size": 10, "total_pages": 1, "has_next": false, "has_prev": false
}
```

#### GET `/api/orders/{order_id}`
**Response 200:**
```json
{
  "status": "success",
  "data": {
    "id": 21, "name": "S00021", "reference": "...", "date_order": "2026-01-01T10:00:00",
    "status": "sale", "currency": "USD", "delivery_status": "...", "total": 185.0, "item_count": 1,
    "customer_id": 3, "billing_address_id": 12, "shipping_address_id": 15,
    "line": [ { "product_name": "Running Shoe", "quantity": 2, "price": 90.0, "subtotal": 180.0 } ]
  }
}
```
**Response 400:** `"Order not found"`

---

### 4.14 Invoices — `/api/invoices*`

All require API key + JWT. Returns customer invoices (`move_type = "out_invoice"`) for the authenticated partner (including child contacts) on the current website.

#### GET `/api/invoices`
**Query params:** `page`, `size`
**Response 200:**
```json
{
  "status": "success",
  "data": [
    { "id": 30, "name": "INV/2026/0001", "reference": "...", "customer_id": 3, "invoice_date": "2026-01-02", "currency": "USD", "total": 185.0, "due_amount": 0.0, "due_date": "2026-01-16", "payment_status": "paid" }
  ],
  "total": 2, "page": 1, "size": 10, "total_pages": 1, "has_next": false, "has_prev": false
}
```

#### GET `/api/invoices/{invoice_id}`
**Response 200:**
```json
{
  "status": "success",
  "data": {
    "id": 30, "name": "INV/2026/0001", "reference": "...", "customer_id": 3,
    "invoice_date": "2026-01-02", "currency": "USD", "total": 185.0, "due_amount": 0.0,
    "due_date": "2026-01-16", "payment_status": "paid",
    "shipping_address_id": 15,
    "line": [ { "name": "Running Shoe", "quantity": 2, "price": 90.0, "subtotal": 180.0 } ]
  }
}
```
**Response 400:** `"Invoice not found"`

---

### 4.15 Notifications — `/api/noti_messages*`

All notification endpoints require API key + JWT and return notifications
belonging to the authenticated user.

#### GET `/api/noti_messages`
Returns notification records created by the Firebase notification helper.
**Query params:** `page` (default `1`), `size` (default `10`)
**Response 200:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 12,
      "name": "Notification",
      "receiver_id": 3,
      "receiver_name": "John Doe",
      "read_status": "unread",
      "status": "success",
      "create_date": "2026-01-01 10:00:00",
      "title": "Sale order has been confirmed",
      "body": "Your order S00021 has been confirmed!"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "total_pages": 1,
  "has_next": false,
  "has_prev": false
}
```

#### PUT `/api/noti_messages/bulk`
Marks the specified notification IDs as read.
**Body:** `{ "ids": [12, 13] }`
**Response 200:**
```json
{ "status": "success", "ids": [12, 13], "message": "Successfully marked as read" }
```
**Response 400:** `{ "status": "fail", "message": "Failed to update notification status" }`

---

## 5. Endpoint Summary Table

| Method | Path | Auth                       |
|---|---|----------------------------|
| POST | `/api/auth/login` | API key                    |
| POST | `/api/auth/register` | API key                    |
| POST | `/api/auth/request_reset_password` | API key                    |
| POST | `/api/auth/otp_verity` | API key                    |
| POST | `/api/auth/reset_password` | API key                    |
| POST | `/api/auth/logout` | API key + JWT              |
| POST | `/api/auth/refresh` | API key + JWT (expired OK) |
| POST | `/api/auth/change_password` | API key + JWT              |
| GET | `/api/auth/profile` | API key + JWT              |
| PUT | `/api/auth/profile/image` | API key + JWT              |
| GET | `/api/countries/{cid}/states` | API key + JWT              |
| GET | `/api/countries/{cid}/townships` | API key + JWT              |
| GET | `/api/my/address` | API key + JWT              |
| POST | `/api/my/address` | API key + JWT              |
| PUT | `/api/my/address/{address_id}` | API key + JWT              |
| DELETE | `/api/my/address/{partner_id}` | API key + JWT              |
| PUT | `/api/order/address` | API key + JWT              |
| GET | `/api/categories` | API key                    |
| GET | `/api/products` | API key                    |
| GET | `/api/products/{product_id}` | API key                    |
| GET | `/api/product/{product_template_id}/reviews` | API key                    |
| POST | `/api/product/{product_template_id}/reviews` | API key + JWT              |
| PUT | `/api/reviews/{rating_id}` | API key + JWT              |
| DELETE | `/api/reviews/{rating_id}` | API key + JWT              |
| GET | `/api/banners` | API key                    |
| GET | `/api/product/ribbons` | API key                    |
| GET | `/api/wishlists` | API key + JWT              |
| POST | `/api/wishlists` | API key + JWT              |
| DELETE | `/api/wishlists/{wishlist_id}` | API key + JWT              |
| GET | `/api/cart` | API key + JWT              |
| POST | `/api/cart` | API key + JWT              |
| DELETE | `/api/cart/line/{line_id}` | API key + JWT              |
| GET | `/api/delivery_methods` | API key + JWT              |
| POST | `/api/delivery_methods` | API key + JWT              |
| GET | `/api/payment_methods` | API key + JWT              |
| POST | `/api/checkout` | API key + JWT              |
| GET | `/api/orders` | API key + JWT              |
| GET | `/api/orders/{order_id}` | API key + JWT              |
| GET | `/api/invoices` | API key + JWT              |
| GET | `/api/invoices/{invoice_id}` | API key + JWT              |
| GET | `/api/noti_messages` | API key + JWT              |
| PUT | `/api/noti_messages/bulk` | API key + JWT              |


---

## 6. Suggested Client Flow (Guest → Purchase)

1. `POST /api/auth/register` or `/api/auth/login` → obtain a JWT.
2. `POST /api/auth/reset_password` or `/api/auth/change_password` → manage the password.
3. `GET /api/categories` and `GET /api/products` → browse the catalog.
4. `GET /api/products/{id}` → view product variants and details.
5. `POST /api/wishlists` and `POST /api/product/{id}/reviews` (optional) → save or review products.
6. `POST /api/cart` → add variants to the cart; `GET /api/cart` → review it.
7. `GET /api/my/address` / `POST /api/my/address` → ensure a shipping address exists.
8. `PUT /api/order/address` → attach the selected address to the cart.
9. `GET /api/delivery_methods` → list carriers; `POST /api/delivery_methods` → select one.
10. `GET /api/payment_methods` → list payment options.
11. `POST /api/checkout` → create the transaction, validate, and confirm the order.
12. `GET /api/orders`, `GET /api/invoices`, and `GET /api/noti_messages` → track post-purchase activity.

---
