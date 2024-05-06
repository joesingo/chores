# chores

Really simple web app to keep track of a list of repeating chores.

Developed for my personal use only, and live at
[chores.joesingo.co.uk](https://chores.joesingo.co.uk).

## Setup

- Install dependencies:
  ```shell
  pip install -r requirements.txt
  ```
- Define chores in `chores.csv`. E.g.
  ```csv
  name, frequency
  hoover bedroom, 1 week
  brush dog, 3 days
  mow lawn, 4 weeks
  ```
- Generate a password:

  ```python
  from passlib.hash import pbkdf2_sha256
  pbkdf2_sha256.using(rounds=8000, salt_size=10).hash("my password here")
  ```
- Save password hash in `.passwd` (username is hardcoded in `webapp.py`)
- The web app uses Flask. For development simply run `./webapp.py`; in
  production use whatever you like to deploy WSGI applications

## Usage notes

- The site uses HTTP basic auth and consists of only a single page at `/`
- `chores.csv` is re-read on every page load, to support modifying the list of
  chores while the site is live
- The last completion date of each chore is saved in a JSON file at
  `last_completed.json`
