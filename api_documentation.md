<!-- api_documentation.md -->
# RestroManager API Documentation

## Authentication APIs

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/auth/login/` | POST | Obtain authentication token | ✅ Working |
| `/api/auth/token/refresh/` | POST | Refresh authentication token | ✅ Working |
| `/api/auth/user/` | GET | Get authenticated user information | ✅ Working |
| `/api/auth/staff-credentials/` | GET | List staff credentials | ✅ Working |

## Menu APIs

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/restaurant/menu-items/` | GET | List menu items | ✅ Working |
| `/api/restaurant/categories/` | GET | List categories | ✅ Working |
| `/api/restaurant/food-types/` | GET | List food types | ✅ Working |
| `/api/restaurant/cuisines/` | GET | List cuisines | ✅ Working |
| `/api/restaurants/{restaurant_slug}/menu/` | GET | Public menu for a specific restaurant | ✅ Working |

## Order APIs

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/restaurant/orders/` | GET | List orders for restaurant | ✅ Working |
| `/api/captain/orders/create/` | POST | Create a new order as captain | ✅ Working |
| `/api/captain/bills/{bill_id}/reorder/` | POST | Add items to existing bill | ✅ Working |
| `/api/order-items/{item_id}/update-status/` | PUT | Update order item status | ✅ Working |
| `/api/restaurants/{restaurant_slug}/orders/` | POST | Reorder from customer frontend | ✅ Working |
| `/api/cashier/pending-bills/` | GET | List pending bills for cashier | ✅ Working |
| `/api/cashier/bills/{bill_id}/pay/` | POST | Mark bill as paid | ✅ Working |
| `/api/kitchen/orders/` | GET | List orders for kitchen | ✅ Working |

## Analytics APIs

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/restaurant/analytics/` | GET | Get restaurant analytics | ✅ Working |
| `/api/admin/analytics/` | GET | Get admin analytics | ✅ Working |
| `/api/restaurant/reports/orders/` | GET | Get order reports | ✅ Working |

## WebSocket Endpoints

| Endpoint | Description | Status |
|----------|-------------|--------|
| `/ws/chef/{restaurant_slug}/` | Chef notifications for new orders | ✅ Working |
| `/ws/customer/{bill_id}/` | Customer notifications for order status updates | ✅ Working |

<!-- ## Schema and Documentation

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/schema/` | GET | OpenAPI schema | ✅ Working |
| `/api/docs/` | GET | Swagger UI documentation | ✅ Working | -->

## Notes

- The system uses JWT authentication with token-based access.
- WebSocket connections are established for real-time notifications.
- Role-based permissions control access to different endpoints.
- The system supports geofencing for customer orders based on restaurant location.
- Redis connection is required for WebSocket functionality and real-time notifications.