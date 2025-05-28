## Overview

This is the backend repository for **Proto** — a university project that serves as a proof of concept for employing agentic AI in the UX development process.

The app is built using an **API-based** and **domain-driven** approach, ensuring a modular architecture that can run independently of any frontend. This makes it easily testable using tools like Postman.

Below is a walkthrough of the app’s internal structure and instructions on how to test its endpoints.

## Overview

This is the backend repository for **Proto** — a university project that serves as a proof of concept for employing agentic AI in the UX development process.

The app is built using an API-based and domain-driven approach, ensuring a modular architecture that can run independently of any frontend. This makes it easily testable using tools like Postman.

Below is a walkthrough of the app’s internal structure and instructions on how to test its endpoints.

## Domains

Inside the `Domains/` folder, you’ll find five subfolders—each representing a distinct domain. In line with Domain-Driven Design (DDD) principles, a domain encapsulates a set of related functionalities.

```
Domains/
├── Auth         # Handles user authentication
├── Onboarding   # Handles user onboarding
├── ManageData   # Handles CRUD operations for user uploads
├── Results      # Core AI logic and result generation
└── Toolkit      # Utility functions used across the app
```

Below is a breakdown of each domain and its responsibilities:

---

### Auth

Handles authentication-related operations such as login, signup, and password management.

**Endpoints:**
- `POST /auth/login/`
- `POST /auth/signup/`
- `POST /auth/logout/`
- `POST /auth/change-password/`
- ...

---

### Onboarding

Manages the user onboarding process and populates user/business/page info in the database.

**Endpoints:**
- `POST /onboarding/user-onboard/`
- `POST /onboarding/business-onboard/`
- `POST /onboarding/page-onboard/`
- `POST /onboarding/upload-screenshot/`

---

### ManageData

Enables users to manage (Create, Read, Update, Delete) their uploaded data.

**Endpoints:**
- `POST /upload/create/`
- `DELETE /upload/delete/`
- `PUT /upload/update/`
- `GET /upload/show/`
- ...

---

### Results

This domain contains the core logic of the application, wrapping the AI-powered functionalities and endpoints that generate results.

*(Details to be filled if needed later.)*

---

### Toolkit

Provides helper functionalities utilized by the AI agents, such as taking screenshots, scraping HTML/CSS, and measuring web performance.

**Endpoints:**
- `GET /toolkit/take-screenshot/`
- `GET /toolkit/business-html/`
- `GET /toolkit/business-css/`
- `GET /toolkit/web-metrics/business/`
- ...
