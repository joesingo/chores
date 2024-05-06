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
- Initialise chore completion dates JSON file:
  ```shell
  echo '{}' > last_completed.json
  ```
- Generate a password:

  ```python
  from passlib.hash import pbkdf2_sha256
  pbkdf2_sha256.using(rounds=8000, salt_size=10).hash("my password here")
  ```
- Save password hash in `.passwd` (username is hardcoded in `webapp.py`)
- The web app uses Flask. For development simply run `./webapp.py`; in
  production use whatever you like to deploy WSGI applications

## Docker deployment

```shell
docker build -t chores:v1 .
docker run \
    --rm \
    -v $(pwd)/chores.csv:/app/chores.csv \
    -v $(pwd)/last_completed.json:/app/last_completed.json \
    -v $(pwd)/.passwd:/app/.passwd \
    -p 5000:80 \
    chores:v1
```

## Usage notes

- Requires Python 3.10 or later
- The site uses HTTP basic auth and consists of only a single page at `/`
- `chores.csv` is re-read on every page load, to support modifying the list of
  chores while the site is live
