name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        env:
          DATABASE_URL: sqlite:///./ci_test.db
        run: pytest tests/ -v

  frontend-build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: frontend/package.json

      - name: Install dependencies
        run: npm install

      - name: Build
        run: npm run build

  docker-build:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-build]

    steps:
      - uses: actions/checkout@v4

      - name: Build backend image
        run: docker build -t carbon-analyzer-backend ./backend

      - name: Build frontend image
        run: docker build -t carbon-analyzer-frontend ./frontend
