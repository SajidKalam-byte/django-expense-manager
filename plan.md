1. Core Design Philosophy
Server-rendered app (Django templates + Bootstrap)  
Minimal JS (only where needed: charts, tables)  
Clean relational schema (no overengineering)  
Everything tied to cash flow + auditability  

2. Final Feature Decisions (Resolved)

✅ Categories  
Predefined defaults:  
Materials, Labor, Contractor, Permits, Equipment, Misc  
Allow custom categories + subcategories  

✅ Payments  
Payment modes:  
Cash  
Bank Transfer  
UPI  
Custom (user-defined)  

✅ Invoice Structure (Important Tradeoff)

👉 Chosen: Single total per invoice (NOT line items)

Reason:

Faster to build  
Matches your real use case (you care about totals)  
Can extend later if needed  

✅ File Uploads  
Supported:  
PDF  
Images (JPG, PNG)  
Stored locally (/media/invoices/)  

✅ Time Model  
Every expense has:  
date (mandatory)  
phase (foundation, finishing, etc.)

👉 Phase system included but lightweight  

✅ Budget + Projection  
You will define:  
Total project budget  

System calculates:  

Total spent  
Remaining budget  
Burn rate (daily + monthly)  
Forecast completion cost  

✅ Wallet System (Critical Feature)

You described a cash account simulation. Implementing:

Wallet  
Example: “Main Account”  
Initial balance (e.g., ₹200,000)  

Behavior:  
When expense is created:  
Select wallet  
Amount gets deducted automatically  

Wallet shows:  
Current balance  
Transaction history  

👉 This ensures:  

Your “real-world cash” = system data  

✅ Multi-User (Future-proof)  
Django auth system  

Roles:  
Admin  
Accountant  
Viewer  

(MVP: only admin UI needed)  

✅ Filters & Reports  
Filter by:  
Date range  
Vendor  
Category  

Export:  
PDF summary (Phase 3)  

3. Database Schema (Clean + Extendable)

Expense  
id  
title  
amount  
category_id  
subcategory  
vendor_id  
payment_mode  
wallet_id  
invoice_number  
date  
phase_id (nullable)  
notes  
file  
created_at  

Category  
id  
name  
parent_id (nullable)  

Vendor  
id  
name  
contact  
type  

Wallet  
id  
name  
initial_balance  
current_balance  

WalletTransaction  
id  
wallet_id  
amount  
type (debit/credit)  
reference (expense_id)  
date  

Budget  
id  
total_budget  
start_date  
end_date  

Phase  
id  
name  

4. Core Business Logic  

Expense Creation Flow  

User creates expense  
Selects wallet  

System:  

Deducts amount from wallet  
Creates wallet transaction  
Saves expense  

Wallet Balance Calculation  

current_balance = initial_balance - sum(expenses linked)

(or stored + updated on each transaction)

Burn Rate  

Daily:  

total_spent / days_since_start  

Monthly:  

total_spent / months_elapsed  

Projection  

estimated_total = avg_daily_spend * total_project_days  

5. UI Pages (Django Templates)  

Dashboard  
Total spent  
Remaining budget  
Wallet balance  
Burn rate  
Recent expenses  
Charts (Phase 2)  

Expenses  
Table view (Bootstrap)  
Filters  
Add/Edit/Delete  

Wallet  
Balance  
Transaction history  

Vendors  

Budget & Settings  

6. Tech Stack (Locked)  

Backend  
Django  
SQLite (MVP)  
Django ORM  

Frontend  
Django Templates  
Bootstrap 5  
Minimal JS  

Charts (Phase 2)  
Chart.js  

7. Development Phases (Strict)  

🔹 Phase 1 (MVP – Build First)  

Goal: Working system fast  

Expense CRUD  
Wallet system (fully working)  
Basic dashboard:  
total spent  
wallet balance  
SQLite  
Bootstrap UI  

🔹 Phase 2  

Filters (date/category/vendor)  
Vendor module  
Charts:  
category breakdown  
spending over time  

🔹 Phase 3  

Budget tracking  
Burn rate + projection  
File uploads  
PDF reports  

8. Folder Structure  

project_root/  
  manage.py  
  core/  
  expenses/  
  wallets/  
  vendors/  
  templates/  
  static/  
  media/  

9. Key Implementation Notes (Important for AI Agent)  

🔹 Keep It Simple  
No React  
No APIs unless needed  
Use Django forms  

🔹 Use Signals or Service Layer  

For wallet deduction:  

def create_expense():  
    save_expense()  
    deduct_wallet()  
    create_wallet_transaction()  

🔹 Avoid Overengineering  
No async  
No microservices  
No complex permissions (yet)  

🔹 Use Django Admin  
For quick data control during development  

10. Edge Cases to Handle  

Wallet balance cannot go negative (optional toggle)  
Editing expense:  
Must adjust wallet delta  
Deleting expense:  
Refund wallet  