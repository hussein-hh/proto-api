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

### Toolkit

Provides helper functionalities utilized by the AI agents, such as taking screenshots, scraping HTML/CSS, and measuring web performance.

**Endpoints:**
- `GET /toolkit/take-screenshot/`
- `GET /toolkit/business-html/`
- `GET /toolkit/business-css/`
- `GET /toolkit/web-metrics/business/`
- ...

---


## Results Domain

The `Results` domain is the core of the application, housing the AI-powered functionalities that drive meaningful insights. It is composed of three **logical subdomains**:

- **UI Architecture (`ui-subdomain`)**
- **User Behavior Analytics Architecture (`uba-subdomain`)**
- **Web Metrics Agent (`webmetrics-subdomain`)**

> Note: These subdomains are **behavioral**, not structural. The file organization does not reflect this split directly.

```
Results/
├── LLMs/
│   ├── agents.py      # Defines agent logic
│   └── prompts.py     # Stores prompts for each agent
│
└── views.py           # Wraps agents into API endpoints
```

### Agent Workflow

Each agent is defined in `agents.py` and its corresponding prompt is written in `prompts.py`. After an agent is created, it's exposed through an endpoint in `views.py`. Once all agents are tested independently via Postman, they are orchestrated together into a coherent flow to fulfill the purpose of their respective subdomain.

---

### UI Subdomain

![UI Architecture](pictures/ui-arch)

This subdomain starts by invoking two agents:
- One to extract the **component structure** of the page.
- Another to **describe its visuals** operationally.

These agents take as input:
- HTML
- CSS
- Screenshot

The data is gathered by calling relevant endpoints in the Toolkit domain.

The combined output is used to build a **UI Report**, which is then evaluated by a **UI Thinking Evaluator** based on a discrete set of UX criteria. The final result is sent to a **Formulator Agent** that rewrites it into a user-friendly tone.

---

### UBA Subdomain

![UBA Architecture](pictures/uba-arch)

This subdomain evaluates user-provided UBA (User Behavior Analytics) data.

- A **Thinking Evaluator** processes the analytics.
- The result is passed through two parallel pipelines:
  1. To a **Formulator Agent** for normalization and tone adjustment.
  2. To a **Web-Search Agent** that retrieves relevant papers, threads, and articles related to the findings.

The final output merges both results and is passed through the formulator to generate the user-facing summary.

---

### Web Metrics Subdomain

This subdomain operates with a single agent:

- It fetches **web performance metrics** (like LCP, CLS, etc.) by calling tools in the Toolkit domain.
- The agent evaluates those metrics to produce a concise report for the business.

