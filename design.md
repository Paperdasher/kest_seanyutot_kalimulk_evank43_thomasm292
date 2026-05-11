## <b> TUMMI </b>

### TARGET SHIP DATE: 2026-06-01

### Roster + Roles:

| Name | Email | Primary Role | Secondary Role |
|---|---|---|---|
|Sean Takahashi(PM)|seanyutot@nycstudents.net| Flask | Review + Profile|
|Kalimul Kaif|kalimulk@nycstudents.net| Restaurant map| HTML|
|Evan Khosh|evank43@nycstudents.net|MongoDB| Maintenance of VM/publicly facing site|
|Thomas Mackey|thomasm292@nycstudents.net| Gather data of all nearby food locations| Populate DB with reviews|

### Overview:
tummi will be a beli-clone that specifically caters towards Stuy students. On the app, users will be able to explore a map of restaurants/food options near Stuy and see other users' reviews of them. Users will also be able to add restaurants to the map or remove them to reflect new restaraurnt openings/closings. By registering an account, users will be able to leave ratings and reviews of restaurants and also create lists of places they want to try. On their profile, users will be able to see all the restaraunts they've reviewed and the places they want to try in both map and list forms.

## Problem Being Solved
Many students around stuy don't know where to go when going out for lunch or just keep on going to the same place over and over again. With tummi, stuy students who love food but don't know where to go for lunch will be able to learn about a variety of places to eat which they may have not known about earlier and try new things. 


## Target Users

- Food Reviewers: Primarily to review restaurants and add new restaurants
- Regular Diners: Primarily to find good restaurants to eat at


## Why This Project Matters
Tummi will be able to give students who love food access to many resturants, delis, or shops that they might've not known about before, allowing these students to try new things. This project is for users who love eating and tired of going to the same place for lunch over and over again. 

---

# Minimum Viable Product (MVP) Scope

## Core Features (Required for Final Submission)
Features that **must** be completed:
1. Map containing all the restaurants in the area around stuy
2. Review function where users can add reviews to restaurants
3. Users can create list of restaurants of what they want to try

## Stretch Features (Only if MVP is Complete)
1. Users can add restaurants or food carts not listed
2. Users can view other users' profiles and see their reviews as well as the list of what they want to try
3. Ranking of most reviewed/visited

## Explicit Non-Goals

Features intentionally excluded:
- 
- 

---

# Technology Stack

| Layer | Selected Tool |
|---|---|
| Backend Framework | Flask |
| Frontend Framework | none / bootstrap / foundation / tailwind |
| Database | MongoDB |
| Authentication | Flask sessions |

## Why This Stack Was Chosen

We will be using Flask as our Backend Framework because it is what all members of the team are most experienced with and it will fulfill the purpose we need it to for this project. We will be using [FEF NAME] as our Frontend Framework because [REASON]. We will be using MongoDB as out Database because a document-based database is more compatable for storing restaraunt  and review information which needs to be flexible and all bundled together as one document per restaurant. Evan also already worked on setting up MongoDB last project, so recreating the setup will take minimal time. We will be using Flask sessions as our Authentication because we do not have any strong requirements that would make it unviable.

---

# Team Ownership Plan

Each member must own meaningful deliverables.

| Team Member | Primary Ownership | Secondary Ownership | Specific Deliverables |
|---|---|---|---|
|Sean Takahashi(PM)| Flask | Review + Profile| Ability to rate restaurant and view profile with reviewed restaurants|
|Kalimul Kaif| Restaurant map| HTML| Functioning map showing all added restaurants; pages with explanation|
|Evan Khosh|MongoDB| Maintenance of VM/publicly facing site| Properly loading live site with all inputted data|
|Thomas Mackey| Gather data of all nearby food locations| Populate DB with reviews| Abundant amount of restaurants and some personal reviews of different restaurants|

---

# Component Map

- Feed: See where other users/friends have recently visited and ranked. 
- Profile: Displays restaurants visited for the user and locations in bucket list. 
- Review: Rate restaurant visit based on several categories and compare preference versus other visited restaurants. 
- Discover: Find the most fit restaurants taylored to the user based on similar likes from previously visited restaurants

![Component Map](/design/component_map.png)

# Site Map

![Site Map](/design/site_map.png)

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

---

### Database Organization:
restaurants
- location
- ratings
- reviews
- open
- service speed

users
- username
- password
- reviews {name : [rating, review]}
- wanttotry

### Dependencies:
HTML: 
Python: Flask, PyMongo
APIs:
