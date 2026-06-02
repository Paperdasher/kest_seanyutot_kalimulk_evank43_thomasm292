# tummi by kest

## Roster/Roles:
- Sean Takahashi (PM): Flask + Review/Profile
- Kalimul Kaif: Restaurant map + HTML templates
- Evan Khosh: MongoDB + VM
- Thomas Mackey: Accumulating restaurant info + inputting personal reviews

## Description:
tummi is a beli-clone that specifically caters towards Stuy students. On the app, users will be able to explore a map of restaurants/food options near Stuy and see other users' reviews of them. Users will also be able to add restaurants to the map or remove them to reflect new restaraurnt openings/closings. By registering an account, users will be able to leave ratings and reviews of restaurants and also create lists of places they want to try. On their profile, users will be able to see all the restaraunts they've reviewed and the places they want to try in both map and list forms.

## Live Site:
Our program is hosted live [here](https://tummi.me)

Backup livesite is hosted [here](https://tummiz.me)

### FEATURE SPOTLIGHT
* Filter restaurants by name, max price, in view of current map
* See info of each restaurants and other user's reviews/profile page

### KNOWN BUGS/ISSUES
* Partially outdated data, some restaurants pre-filled may be reloacated/out of business

## Install Guide:

Click the green button on the repo, and choose the SSH clone option. Copy the link and open a terminal session. 
```
$ git clone git@github.com:Paperdasher/kest_seanyutot_kalimulk_evank43_thomasm292.git p5
$ cd p5
$ python -m venv venv
```
For Linux and Mac users

```
$ source venv/bin/activate
$ pip install -r requirements.txt
```

For Windows users

```
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

Now open on [localhost](http://127.0.0.0:5000)

## Launch Codes:
In terminal, access the project root directory and run the command:

```
~$ cd app
~$ python __init__.py
```
