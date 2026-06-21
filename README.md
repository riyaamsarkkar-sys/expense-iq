# ExpenseIQ

A full-stack personal finance management platform that helps users track expenses, analyze spending behavior, and gain actionable financial insights through interactive analytics and visual reporting.

## Live Application

**Demo:** https://expense-iq-sgze.onrender.com

## Overview

ExpenseIQ is a production-deployed web application built using Flask and PostgreSQL. The platform enables users to securely manage daily expenses, visualize spending patterns, and monitor financial activity through a responsive and user-friendly interface.

The application supports user authentication, category-wise expense tracking, monthly analytics, and historical spending analysis while maintaining complete data isolation between users.

---

## Key Features

### Authentication & Security

* User registration and login system
* Secure password hashing
* Session-based authentication
* User-specific data access control

### Expense Management

* Add and categorize expenses
* Track expense descriptions and dates
* Maintain complete spending records
* Real-time data persistence

### Analytics & Insights

* Current month spending summary
* Category-wise expense distribution
* Historical spending analysis
* Expense trend visualization
* Highest expense identification
* Monthly performance metrics

### User Experience

* Mobile-responsive design
* Clean dashboard interface
* Interactive charts and visualizations
* Optimized for desktop and mobile devices

---

## Technology Stack

### Backend

* Python
* Flask
* SQLAlchemy ORM
* PostgreSQL (Neon)

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

### Deployment & Infrastructure

* Render
* Gunicorn
* GitHub

---

## Architecture

Client Browser
       │
       ▼
Flask Application
       │
       ▼
SQLAlchemy ORM
       │
       ▼
PostgreSQL Database (Neon)


## Core Modules

### Dashboard

Provides navigation and access to analytics modules.

### Expense Entry

Allows users to record and categorize expenses.

### Current Month Analytics

Displays:

* Total expenses
* Total entries
* Average daily spending
* Category distribution

### Spending History

Provides:

* Historical expense records
* Trend analysis
* Category insights
* Expense summaries

---

## Project Highlights

* Production deployment with Render
* Cloud-hosted PostgreSQL database
* Secure authentication workflow
* Responsive mobile-first interface
* Interactive financial analytics
* Multi-user data segregation

---

## Future Enhancements

* Budget planning module
* Expense deletion and editing
* CSV export functionality
* Automated reports
* Financial forecasting

---

## Author

**Riyam Sarkar**

GitHub: https://github.com/riyaamsarkkar-sys

---

This project was developed as a practical implementation of full-stack web development concepts, database management, authentication systems, cloud deployment, and responsive user interface design.
