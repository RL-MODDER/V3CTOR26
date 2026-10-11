# 🪪 Meridian Market — IDOR / BOLA

<p align="center">
  <img src="https://img.shields.io/badge/CTF-V3CT0R%202026-7C3AED?style=for-the-badge" alt="V3CT0R CTF 2026" />
  <img src="https://img.shields.io/badge/Category-Web%20Application%20Security-2563EB?style=for-the-badge" alt="Web Application Security" />
  <img src="https://img.shields.io/badge/CWE-639-0F766E?style=for-the-badge" alt="CWE-639" />
</p>

---

| **Assessment Detail** | **Information** |
|:---|:---|
| **Target** | [Meridian Market](https://web3.cybernexus.live/) |
| **Category** | Web Application Security |
| **Vulnerability** | Insecure Direct Object Reference (IDOR) / Broken Object-Level Authorization (BOLA) |
| **CWE** | CWE-639 — Authorization Bypass Through User-Controlled Key |
| **OWASP API Security** | API1:2023 — Broken Object Level Authorization |
| **Result** | Unauthorized access to another customer's order |
| **Flag** | `V3ct0r{1D0R_0rd3r_1003}` |

## 📑 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Scope and Methodology](#2-scope-and-methodology)
3. [Technical Vulnerability Analysis](#3-technical-vulnerability-analysis)
4. [Exploitation Walkthrough](#4-exploitation-walkthrough)
5. [Impact Assessment](#5-impact-assessment)
6. [Root Cause](#6-root-cause)
7. [Remediation](#7-remediation)
8. [Conclusion](#8-conclusion)

---

## 1. Executive Summary

During the V3CT0R CTF 2026 competition, an assessment of the Meridian Market customer portal identified an Insecure Direct Object Reference (IDOR) vulnerability in the order-management functionality.

The application allowed an authenticated customer to view their own order through a route containing the order identifier. However, the individual order endpoint did not adequately enforce ownership authorization, according to the observed challenge behavior.

The dashboard displayed Order #1001 for the authenticated customer. By changing the order identifier in the URL to `/order/1003` while retaining the same authenticated session, it was possible to retrieve an invoice associated with another customer.

The response exposed information that should have been restricted to the record's owner and contained the challenge flag.

This finding demonstrates that authentication alone is insufficient to protect customer records. Every request for a specific object must also verify that the authenticated user is authorized to access that object.

---

## 2. Scope and Methodology

### 2.1 Scope

The assessment focused on the Meridian Market customer portal and its order-management functionality.

**Target URL:** https://web3.cybernexus.live/

The investigation examined:

- Customer authentication.
- Dashboard order visibility.
- Individual order-detail routes.
- Object-level authorization.
- Access to another customer's invoice.

The testing was conducted in the context of an authorized CTF challenge.

### 2.2 Methodology

The investigation followed a straightforward web application testing process:

1. Authenticate using the challenge's customer credentials.
2. Inspect the dashboard and identify the order associated with the account.
3. Open the corresponding order-detail endpoint.
4. Modify the order identifier while maintaining the same authenticated session.
5. Compare the response with the authorized baseline.
6. Verify whether the returned invoice belonged to another customer.
7. Inspect the response for the challenge flag.

---

## 3. Technical Vulnerability Analysis

### 3.1 Insecure Direct Object Reference (IDOR)

**CWE-639 — Authorization Bypass Through User-Controlled Key**

IDOR occurs when an application uses a user-controlled identifier to retrieve an object without adequately checking whether the requester is authorized to access it.

In this challenge, the order-detail route followed this pattern:

```http
GET /order/<Order_ID>
```

The order identifier was supplied directly in the URL. The application needed to verify that the authenticated customer had permission to access the requested order.

According to the observed behavior, this ownership check was missing or ineffective.

### 3.2 Root Cause

The application distinguished between authentication and authorization incorrectly.

| **Authentication** | **Authorization** |
|:---|:---|
| Determines who the user is. | Determines what that user is permitted to access. |

The active session established that the requester was logged in. It did not establish ownership of every order in the system.

The dashboard displayed the customer's own order, but restricting the dashboard list did not protect the individual order endpoint. A user could request another record directly if the backend failed to validate access rights.

### 3.3 Security Impact

An attacker with a valid customer account could potentially access other customers' order records by modifying the object identifier.

Depending on the information stored in the invoices, this could expose customer identities, purchase histories, billing details, or other sensitive information.

In the demonstrated CTF scenario, accessing Order #1003 also exposed the challenge flag.

---

## 4. Exploitation Walkthrough

### Step 1 — Authenticate to the Customer Portal

The customer portal was accessed at:

**Target:** https://web3.cybernexus.live/

The login form displayed the identifier `John`. The supplied challenge credentials were:

```text
Username: John
Password: 123456
```

The following request represents the authentication flow documented in the challenge notes:

```http
POST /login HTTP/1.1
Host: web3.cybernexus.live
Content-Type: application/x-www-form-urlencoded

username=John&password=123456
```

The login succeeded, and the server established an authenticated session using a session cookie.

### Step 2 — Inspect the Dashboard and Authorized Order

After authentication, the dashboard displayed the customer's order history, including:

```text
Order ID: #1001
Order endpoint: /order/1001
```

Opening the order-detail route returned the invoice associated with the authenticated customer.

The corresponding request was:

```http
GET /order/1001 HTTP/1.1
Host: web3.cybernexus.live
Cookie: session=<SESSION_TOKEN>
```

This provided the baseline for testing whether the application enforced object-level authorization.

### Step 3 — Modify the Order Identifier

The next step was to test whether the application verified ownership when an authenticated user requested a different order.

The request path was changed from:

```http
GET /order/1001
```

to:

```http
GET /order/1003
```

The authenticated session remained unchanged.

The equivalent request, using a placeholder for the session cookie, was:

```bash
curl -i 'https://web3.cybernexus.live/order/1003' \
  -H 'Cookie: session=<SESSION_TOKEN>'
```

The placeholder was replaced with the active session cookie obtained during the authorized challenge session.

The server returned HTTP 200 and rendered an invoice associated with a different customer.

This demonstrated that the application did not adequately enforce ownership authorization for the requested order.

### Step 4 — Retrieve the Challenge Flag

Inspection of the HTML response for `/order/1003` revealed the challenge flag inside a `flag-box` element.

```text
V3ct0r{1D0R_0rd3r_1003}
```

This completed the exploitation chain and demonstrated unauthorized access to an order belonging to another customer in the CTF environment.

---

## 5. Impact Assessment

The vulnerability allowed an authenticated customer to access an order that was not associated with their account.

### Demonstrated Impact

- Unauthorized access to another customer's invoice.
- Bypass of intended object-level access restrictions.
- Exposure of information outside the authenticated customer's permitted scope.
- Retrieval of the challenge flag.

In a production e-commerce system, a similar vulnerability could expose other customers' personal information, order histories, billing records, or shipping details, depending on the application's data model.

The actual severity would depend on the sensitivity of the exposed records, the number of affected objects, and the privileges available to an attacker.

---

## 6. Root Cause

The primary root cause was insufficient object-level authorization in the order-detail endpoint.

The application accepted a client-supplied order identifier and returned the corresponding record without effectively ensuring that the authenticated user was permitted to access it.

The sequential nature of the identifiers made the issue easy to test, but sequential identifiers were not the fundamental vulnerability. Even an unpredictable identifier would not replace server-side authorization checks.

The essential failure was trusting the requested object identifier without enforcing access permissions.

---

## 7. Remediation

### 7.1 Enforce Object-Level Authorization

Every order-detail request should verify that the authenticated user is authorized to access the requested order.

For example, the backend should retrieve an order only when its ownership matches the authenticated user's identity, or when the user has an explicitly authorized administrative role.

Authorization must be enforced on the server, not only through dashboard filtering or frontend controls.

### 7.2 Scope Database Queries to the Authenticated User

Where appropriate, query for an order using both the requested identifier and the authenticated user's identity.

**Conceptual SQL example:**

```sql
SELECT *
FROM orders
WHERE id = :order_id
  AND customer_id = :authenticated_customer_id;
```

The actual query should use parameterized database access and the application's verified authentication context.

This ensures that knowing another order's identifier does not automatically grant access to its record.

### 7.3 Apply Authorization Consistently

The same authorization policy should apply to every endpoint that accesses orders, invoices, or related customer records.

An application should not protect the dashboard while leaving individual object endpoints accessible without equivalent checks.

### 7.4 Return Appropriate Responses

If a requested order is unavailable to the authenticated user, the application should deny access without disclosing the record's contents.

Depending on the application's design, it may return `403 Forbidden` or `404 Not Found`. The response should follow a consistent policy that avoids unnecessary information disclosure.

### 7.5 Add Authorization Tests

Automated tests should verify that:

- A customer can access their own order.
- A customer cannot access another customer's order.
- Changing an order identifier does not bypass authorization.
- Invoice and related-document endpoints enforce equivalent permissions.
- Administrative access is granted only through explicit authorization rules.

---

## 8. Conclusion

The Meridian Market challenge demonstrated an IDOR vulnerability caused by inadequate object-level authorization.

Although the application authenticated the customer and restricted the order list displayed on the dashboard, the individual order endpoint failed to adequately enforce ownership checks. Modifying the order identifier from `1001` to `1003` allowed access to another customer's invoice and revealed the challenge flag.

The primary lesson is that authentication and frontend restrictions do not replace server-side authorization. Every request for a protected object must verify that the requester has permission to access it.

---

<p align="center">
  <strong>🏁 V3ct0r{1D0R_0rd3r_1003}</strong>
  <br>
  <sub>V3CT0R CTF 2026 · Authorized challenge environment</sub>
</p>
