# RestroManager API Guide for Frontend Implementation

## Project Overview

RestroManager is a restaurant management system that handles menu management, order processing, kitchen operations, and billing. The system is designed with different user roles (Admin, Chef, Cashier, Captain) and provides real-time updates using WebSockets.

## System Architecture

### Components

1. **Backend Server**: Django REST Framework
2. **WebSocket Server**: Django Channels with Redis
3. **Database**: SQLite (can be migrated to PostgreSQL for production)
4. **Frontend**: Any framework can be used (React, Vue, Angular)

### User Roles

1. **Admin**: Manages menu, users, and has access to all features
2. **Chef**: Receives orders and updates their status
3. **Cashier**: Handles billing and payment
4. **Captain**: Takes orders from customers

## Authentication

### Login

```
POST /api/auth/login/
```

Request:
```json
{
  "username": "username",
  "password": "password123"
}
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NilsInR5cCI6IkpXVCJ9...",
  "user": {
    "name": "User Name",
    "role": "Role"
  }
}
```

### Authentication Header

For all authenticated requests, include the token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NilsInR5cCI6IkpXVCJ9...
```

## Core Workflows

### 1. Menu Management Workflow

#### Create Menu Item

```
POST /api/restaurant/menu-items/
```

Request:
```json
{
  "name": "Dish Name",
  "cuisine": [1, 2],  // Cuisine IDs
  "food_type": [1],   // Food Type IDs
  "category": 3,      // Category ID
  "is_available": true,
  "description": "Dish description",
  "variants": [
    {
      "variant_name": "Regular",
      "price": 450,
      "preparation_time": 20
    },
    {
      "variant_name": "Large",
      "price": 700,
      "preparation_time": 25
    }
  ]
}
```

#### Update Menu Item

```
PUT /api/restaurant/menu-items/{id}/
```

Request format is the same as create.

#### Delete Menu Item

```
DELETE /api/restaurant/menu-items/{id}/
```

### 2. Order Processing Workflow

#### Create Order (Frontend/Customer)

```
POST /api/restaurants/{restaurant_slug}/orders/
```

Request:
```json
{
  "table_number": "15",
  "customer_name": "Customer Name",
  "items": [
    {
      "menu_item_id": 42,
      "variant_name": "Regular",
      "quantity": 2
    }
  ]
}
```

Response:
```json
{
  "order_id": 123,
  "queue_number": "A15",
  "estimated_time": 25
}
```

#### Create Order (Captain)

```
POST /api/captain/orders/create/
```

Request:
```json
{
  "table_number": "15",
  "customer_name": "Customer Name",
  "order_items": [
    {
      "variant_id": 42,
      "quantity": 2
    }
  ]
}
```

### 3. Kitchen Workflow

#### Get Kitchen Orders

```
GET /api/kitchen/orders/
```

Response:
```json
[
  {
    "id": 123,
    "table_number": "15",
    "customer_name": "Customer Name",
    "created_at": "2023-09-04T12:30:10.890904+05:30",
    "order_items": [
      {
        "id": 456,
        "name": "Dish Name",
        "variant_name": "Regular",
        "quantity": 2,
        "status": "PENDING"
      }
    ]
  }
]
```

#### Update Order Item Status

```
POST /api/order-items/{item_id}/update-status/
```

Request:
```json
{
  "status": "ACCEPTED"
}
```

Valid status values: "PENDING", "ACCEPTED", "COMPLETED", "DECLINED"

### 4. Cashier Workflow

#### Get Pending Bills

```
GET /api/cashier/pending-bills/
```

Response:
```json
[
  {
    "id": 123,
    "table_number": "15",
    "customer_name": "Customer Name",
    "created_at": "2023-09-04T12:30:10.890904+05:30",
    "order_items": [
      {
        "id": 456,
        "name": "Dish Name",
        "variant_name": "Regular",
        "quantity": 2,
        "status": "COMPLETED"
      }
    ]
  }
]
```

#### Mark Bill as Paid

```
POST /api/cashier/bills/{bill_id}/pay/
```

Request:
```json
{
  "payment_method": "OFFLINE"
}
```

Valid payment_method values: "ONLINE", "OFFLINE"

## WebSocket Notifications

### Chef WebSocket

```
ws://domain/ws/chef/{restaurant_slug}/
```

Events:
- `new_order`: Notifies when a new order is placed

Example message format:
```json
{
  "table_number": "A1",
  "items": [
    {
      "id": 1,
      "name": "Item Name",
      "quantity": 2,
      "variant": "Variant Name",
      "special_instructions": "Extra spicy"
    }
  ]
}
```

### Customer WebSocket

```
ws://domain/ws/customer/{table_number}/{restaurant_slug}/
```

Events:
- `order_status_update`: Notifies when order status changes

Example message format:
```json
{
  "order_item_id": 1,
  "status": "ACCEPTED|COMPLETED",
  "item_name": "Item Name"
}
```

### Cashier WebSocket

```
ws://domain/ws/cashier/{restaurant_slug}/
```

Events:
- `order_ready_for_payment`: Notifies when all items in an order are completed

Example message format:
```json
{
  "table_number": "A1",
  "items": [
    {
      "name": "Item Name",
      "quantity": 2,
      "price": 10.99,
      "variant": "Variant Name"
    }
  ],
  "total_amount": 21.98
}
```

**Important Note**: The cashier WebSocket notification does not include a `type` field. Instead, check for the presence of `table_number` and `items` fields to identify an order ready for payment notification.

## Implementation Guidelines

### Frontend Setup

1. **Authentication**:
   - Implement JWT token storage and refresh
   - Add authentication headers to all API requests
   - Handle unauthorized responses

2. **WebSocket Integration**:
   - Connect to appropriate WebSocket endpoint based on user role
   - Handle connection errors and reconnection
   - Process incoming messages and update UI accordingly

3. **Role-Based UI**:
   - Admin: Menu management, analytics, user management
   - Chef: Order queue, status updates
   - Cashier: Pending bills, payment processing
   - Captain: Order creation, table management

### WebSocket Implementation Tips

1. **Connection Establishment**:
   ```javascript
   // Example using JavaScript WebSocket API
   const connectWebSocket = (role, restaurantSlug, tableNumber = null) => {
     let wsUrl;
     switch(role) {
       case 'chef':
         wsUrl = `ws://domain/ws/chef/${restaurantSlug}/`;
         break;
       case 'cashier':
         wsUrl = `ws://domain/ws/cashier/${restaurantSlug}/`;
         break;
       case 'customer':
         wsUrl = `ws://domain/ws/customer/${tableNumber}/${restaurantSlug}/`;
         break;
     }
     
     const socket = new WebSocket(wsUrl);
     
     socket.onopen = () => {
       console.log('WebSocket connection established');
     };
     
     socket.onmessage = (event) => {
       const data = JSON.parse(event.data);
       handleWebSocketMessage(role, data);
     };
     
     socket.onerror = (error) => {
       console.error('WebSocket error:', error);
     };
     
     socket.onclose = () => {
       console.log('WebSocket connection closed');
       // Implement reconnection logic here
     };
     
     return socket;
   };
   ```

2. **Message Handling**:
   ```javascript
   const handleWebSocketMessage = (role, data) => {
     switch(role) {
       case 'chef':
         // Handle new order notification
         if (data.table_number && data.items) {
           displayNewOrder(data);
         }
         break;
       case 'cashier':
         // Handle order ready for payment
         // Note: Check for table_number and items fields instead of a type field
         if (data.table_number && data.items) {
           displayOrderReadyForPayment(data);
         }
         break;
       case 'customer':
         // Handle order status update
         if (data.order_item_id && data.status) {
           updateOrderStatus(data);
         }
         break;
     }
   };
   ```

3. **Reconnection Logic**:
   ```javascript
   const reconnectWebSocket = (role, restaurantSlug, tableNumber = null, maxRetries = 5) => {
     let retries = 0;
     
     const attemptReconnect = () => {
       if (retries >= maxRetries) {
         console.error('Max reconnection attempts reached');
         return;
       }
       
       retries++;
       console.log(`Attempting to reconnect (${retries}/${maxRetries})...`);
       
       setTimeout(() => {
         const socket = connectWebSocket(role, restaurantSlug, tableNumber);
         socket.onclose = attemptReconnect;
       }, 2000 * retries); // Exponential backoff
     };
     
     return attemptReconnect;
   };
   ```

### Best Practices

1. **Error Handling**:
   - Implement proper error handling for API requests
   - Show user-friendly error messages
   - Log errors for debugging

2. **State Management**:
   - Use a state management solution (Redux, Vuex, etc.)
   - Keep WebSocket messages in sync with application state

3. **Responsive Design**:
   - Implement responsive design for different devices
   - Optimize for tablets for in-restaurant use

## Testing

A test script (`test_apis.py`) is available to verify API functionality. It tests:

1. Authentication
2. Menu item creation, update, and deletion
3. Order creation
4. Chef order status updates
5. Cashier bill payment
6. WebSocket notifications

Run the test script with:
```
python test_apis.py
```

## Deployment

### Requirements

1. Django server: `daphne restromanager.asgi:application`
2. Redis server: `redis-server --port 6380`

### Environment Variables

For production, configure the following environment variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False for production
- `ALLOWED_HOSTS`: List of allowed hosts
- `DATABASE_URL`: Database connection URL
- `REDIS_URL`: Redis connection URL

## Support

For any questions or issues, please contact the backend team.