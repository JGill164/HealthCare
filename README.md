# SIGNAL Health

A mental health crisis early warning system built with FastAPI and a simple HTML frontend.

---

## Setup Instructions

### Step 1: Go to your project folder

```bash
cd ~/Developer/personal_projects/HealthCare
```

### Step 2: Activate virtual environment

```bash
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install fastapi uvicorn transformers torch
```

### Step 4: Run the backend

```bash
uvicorn backend:app --reload --port 8000
```

Backend will run at:

```
http://127.0.0.1:8000
```

---

## Run the Frontend

### Step 5: Open a NEW terminal and run:

```bash
cd ~/Developer/personal_projects/HealthCare
open index.html
```

---

## Important (Use Your Own Computer Name)

When running commands, your terminal will show **your own computer name**, not mine.

Example (my computer):

```
(venv) (base) arbindkhaira@Arbinds-MacBook-Pro-3 HealthCare %
```

On your computer, it will look something like:

```
(venv) (base) yourname@Your-MacBook HealthCare %
```

👉 This is normal — just run the same commands.

---

## Full Run (All Steps Together)

```bash
cd ~/Developer/personal_projects/HealthCare
source venv/bin/activate
pip install fastapi uvicorn transformers torch
uvicorn backend:app --reload --port 8000
```

Then in another terminal:

```bash
cd ~/Developer/personal_projects/HealthCare
open index.html
```

---

## Tech Stack

* Python
* FastAPI
* Uvicorn
* Transformers
* Torch
* HTML / CSS / JavaScript

---

## Notes

* Keep the backend terminal running
* Always activate `venv` before running backend
* Use your own folder name if different
* Frontend and backend must run at the same time
