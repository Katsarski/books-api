# Online Bookstore API Automation Testing

## Overview

This project provides API automationn test framework for the [FakeRestAPI](https://fakerestapi.azurewebsites.net/index.html) Online Bookstore, covering both **Books** and **Authors** endpoints. The framework is designed for maintainability, reusability, and clarity, trying to flollow SOLID principles and best practices. It includes test coverage for both happy paths and edge cases, reporting, and CI/CD integration.

## Assumptions:
- All method calls should function e.g. POST /books shall create new books that are available when calling GET /books
- GET methods returns ALL entries with no way to retrieve more (no pagination mechanism)

## API Improvement ideas
- 201 Created instead of 200 OK for newly created resources (POST requests)
- Unify the error messages for easier assertion of errors
- Improve defaulting to id 0 when no id is provided to POST /books -> e.g. use next available
- Improve defaulting to publishDate 0001-01-01T00:00:00 when no publishDate is provided to POST /books -> further investigation needed for what might be a suitable approach e.g. current date/time OR make it mandatory
- Add authentication mechanism to prevent unauthorized destructive usage

## Framework Improvement ideas
- Create more tests related to the various available headers
Further extend the PUT calls to test by updating each available property - not done due to this currently not working
- Run tests in parallel to decrease runtime

---

## Project Structure

```
.
├── config/                 # Configuration files and environment setup
├── schemas/                # JSON schemas for response validation
├── tests/                  # Test cases for Books and Authors APIs
│   ├── authors/
│   └── books/
├── utils/                  # Reusable utilities (API client, logger, schema validator)
├── .github/workflows/      # CI/CD pipeline definitions (GitHub Actions)
├── .env                    # Environment variables (not committed)
├── .gitignore
├── .pylintrc               # Linter configuration
├── pytest.ini              # Pytest configuration
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── reports/                # Generated test reports
```

---

## Features

- **Modular Design:**  
  Utilities and fixtures are reusable and separated by responsibility (API client, logging, schema validation, data generation).

- **SOLID Principles:**  
  The codebase is structured for maintainability and extensibility, with clear separation of concerns and dependency injection where appropriate.

- **Test Coverage:**  
  - **Books API:**  
    - GET, POST, PUT, DELETE endpoints
    - Valid and invalid IDs, missing fields, invalid data types, and content types
  - **Authors API:**  
    - GET, POST, PUT, DELETE endpoints
    - Valid and invalid IDs, missing fields, invalid data types, and content types

- **Schhema Validation:**  
  All API responses are validated against strict JSON schemas for correctness.

- **Reporting:**  
  Test runs generate an HTML report (`reports/report.html`) summarizing all test results.

- **Code Quality:**  
  - Enforced via `pylint` with a minimum score threshold (100%) in CI.

- **CI/CD Integration:**  
  - **Linting:** Runs on every pull request and push, blocking merges if code quality is below threshold. [![Lint](https://github.com/Katsarski/books-api/actions/workflows/pylint.yml/badge.svg)](https://github.com/Katsarski/books-api/actions/workflows/pylint.yml)

  - **Testing:** Manual trigger for full test suite and report generation.

---

## Setup & Usage

### 1. Clone the Repository

```sh
git clone <repo-url>
cd books-api
```

### 2. Install Dependencies

```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment

- Set environment variables in `.env` (root directory of the project) or via your shell.
- Example:
  ```
  BASE_URL=https://fakerestapi.azurewebsites.net/api/v1
  DEFAULT_TIMEOUT=10
  ```

### 4. Run Linter

```sh
pylint utils/ config/ schemas/ tests/
```

### 5. Run Tests

```sh
pytest --html=reports/report.html --self-contained-html
```

### 6. View Test Report

Open `reports/report.html` in your browser.

---

## CI/CD

- **Linting:**  
  `.github/workflows/pylint.yml` runs on every PR and push, enforcing a minimum pylint score of 98%.

- **Testing:**  
  `.github/workflows/tests.yml` can be triggered manually from the GitHub Actions UI to run the full test suite and upload the HTML report as an artifact.

---

## Extending the Framework

- Add new endpoints or test cases by creating new files in `tests/books/` or `tests/authors/`.
- Add or update JSON schemas in `schemas/`.
- Utilities in `utils/` are reusable for new resources or endpoints.

---

## Code Quality

- Follows SOLID principles for maintainability.
- Uses fixtures for setup/teardown and data generation.
- All code is type-annotated and documented.

---

## Troubleshooting

- Ensure all dependencies are installed.
- Check `.env` or environment variables for correct API base URL.
- For CI failures, review the uploaded linter and test reports in the GitHub Actions UI.

---

## License

This project is for educational and assessment purposes.

---