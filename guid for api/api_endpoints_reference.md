# RestroManager API Endpoints Reference

This document provides a quick reference of all available API endpoints in the RestroManager system.

## Authentication

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login/` | Authenticate user and get JWT token | Any |

## Menu Management

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|---------------|
| GET | `/api/restaurant/menu-items/` | List all menu items | Any |
| POST | `/api/restaurant/menu-items/` | Create a new menu item | Admin |
| PUT | `/api/restaurant/menu-items/{id}/` | Update a menu item | Admin |
| DELETE | `/api/restaurant/menu-items/{id}/` | Delete a menu item | Admin |

## Order Management

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|---------------|
| POST | `/api/restaurants/{restaurant_slug}/orders/` | Create a new order | Any |
| POST | `/api/captain/orders/create/` | Create an order (Captain) | Captain |
| GET | `/api/kitchen/orders/` | Get pending kitchen orders | Chef |
| POST | `/api/kitchen/order-items/{order_item_id}/` | Update order item status | Chef |

## Cashier Operations

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|---------------|
| GET | `/api/cashier/bills/` | Get bills ready for payment | Cashier |
| POST | `/api/cashier/bills/{bill_id}/pay/` | Mark bill as paid | Cashier |

## WebSocket Connections

| Connection URL | Description | Required Role |
|----------------|-------------|---------------|
| `ws://domain/ws/chef/{restaurant_slug}/` | Chef notifications | Chef |
| `ws://domain/ws/cashier/{restaurant_slug}/` | Cashier notifications | Cashier |
| `ws://domain/ws/customer/{table_number}/{restaurant_slug}/` | Customer notifications | Any |

## WebSocket Events

| Event | Description | Recipient |
|-------|-------------|----------|
| New Order | Notification when a new order is placed | Chef |
| Order Status Update | Notification when order status changes | Customer |
| Order Ready for Payment | Notification when all items in an order are completed | Cashier |

## Status Codes

| Status | Description |
|--------|-------------|
| PENDING | Order item is waiting to be processed |
| ACCEPTED | Chef has accepted the order item |
| COMPLETED | Order item is ready for serving |
| PAID | Bill has been paid |

## Payment Methods

| Method | Description |
|--------|-------------|
| CASH | Cash payment |
| CARD | Credit/Debit card payment |
| UPI | UPI payment |
| ONLINE | Online payment (general) |
| OFFLINE | Offline payment (general) |