## <b> TUMMI </b>

### TARGET SHIP DATE: 2026-06-01

### Roster + Roles:

| Name | Email | Primary Role | Secondary Role |
|---|---|---|---|
|Sean Takahashi(PM)|seanyutot@nycstudents.net| | |
|Kalimul Kaif|kalimulk@nycstudents.net| | |
|Evan Khosh|evank43@nycstudents.net|MongoDB| |
|Thomas Mackey|thomasm292@nycstudents.net| | |

### Overview:
tummi will be a beli-clone that specifically caters towards Stuy students. On the app, users will be able to explore a map of restaurants/food options near Stuy and see other users' reviews of them. Users will also be able to add restaurants to the map or remove them to reflect new restaraurnt openings/closings. By registering an account, users will be able to leave ratings and reviews of restaurants and also create lists of places they want to try. On their profile, users will be able to see all the restaraunts they've reviewed and the places they want to try in both map and list forms.

## Problem Being Solved



## Target Users

Who will use this system?

- Stuyvesant students/faculty
- 


## Why This Project Matters


---

# Minimum Viable Product (MVP) Scope

## Core Features (Required for Final Submission)
Features that **must** be completed:
1. 
1. 
1. 

## Stretch Features (Only if MVP is Complete)
1. 
1. 
1. 

## Explicit Non-Goals

Features intentionally excluded:
- 
- 

---

# Technology Stack

| Layer | Selected Tool |
|---|---|
| Backend Framework | Flask / Node.js (choose one) |
| Frontend Framework | none / bootstrap / foundation / tailwind / other? (seek clearance) |
| Database | SQLite / MongoDB |
| Authentication | Flask sessions unless you have good reason/need to deviate |
| ORM / DB Library | optionally SQLAlchemy; initiate clearance protocol if interested |

## Why This Stack Was Chosen
{your summary/recap of team discussions here}

---

# Team Ownership Plan

Each member must own meaningful deliverables.

| Team Member | Primary Ownership | Secondary Ownership | Specific Deliverables |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |

---

# Component map

- Feed: See where other users/friends have recently visited and ranked. 
- Profile: Displays restaurants visited for the user and locations in bucket list. 
- Review: Rate restaurant visit based on several categories and compare preference versus other visited restaurants. 
- Discover: Find the most fit restaurants taylored to the user based on similar likes from previously visited restaurants

{Insert your mermaid(or equivalent)-generated diagram here}

# Site map

{Insert your mermaid(or equivalent)-generated diagram here}
eg...
```
Landing Page
   ↓
Login / Register
   ↓
Dashboard
   ├── Feature A
   ├── Feature B
   └── Profile
```

## Key User Stories
### eg0
As a Stuy kid looking for a quick lunch between periods, I want to view a feed of my friends' recent ratings in the area so that I can quickly find a reliable, student-approved, and budget-friendly spot without wasting my break time.

### eg1
As a NYC college student who enjoys exploring diverse cuisines, I want to create and manage a bucket list of restaurants I want to visit and enjoy.

### eg2
As a foodie enthusiast, I want to rank my restaurant visits and compare them against my previous favorites so that I can build a leaderboard of the best spots I've been to.



# Database Design

{Insert your table/document organizational structure here}


# Testing Plan
{Delineate here your plan for testing each component}

# Timeline
## Week 1 Goals:
## Week 2 Goals:
## Week 3 Goals:
## Internal Deadlines:
{List milestones your team has identified, in the order they must be completed. Set a target completion date for each.}


# Completion Criteria (_a.k.a._ "Definition of 'Done'")
Project is considered complete when all of the following are true:
1.
1.
1.

# Open Questions
{Delineate anything undecided here}

# Appendix
{Any relevant info that is useful but would have interrupted narrative flow above, or cluttered the information portrayed}

---

### Database Organization:
restaurants
- location
- ratings
- reviews
- open

users
- username
- password
- reviews {name : [rating, review]}
- wanttotry



### Dependencies:
HTML: 
Python: Flask, PyMongo
APIs:
