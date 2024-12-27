# README

## Project Description

This project contains autotests that test the functionality of the API. All tests are developed using Python version **3.11.9**
## Preparing for launch

### Dependency installation

1. Make sure you have Python version 3.11.9 installed.
2. Install dependencies from the `requirements.txt`:
   ```bash
   pip install -r requirements.txt
## Setting up the environment
### Getting MAILSAC_API_KEY
To obtain an API key, go [here](https://mailsac.com/v2/credentials) and create a new key.
If the free monthly limit is not enough for testing, create a new account and generate a new key.
### Account EMPTY_BALANCE_USER_EMAIL
The **EMPTY_BALANCE_USER_EMAIL** account must have **two translation** configured:
1. With the ID specified in the `TRANSLATION_ID` variable.
2. With the ID specified in the `TRANSLATION_ID_NO_EDIT` variable.
Both translations must be successfully loaded and correctly configured. 

## GitHub Actions
To run tests in GitHub Actions, add secrets to the repositories. You can do this by following the link: https://github.com/юзернейм/репозиторий/settings/secrets/actions  
Add the following variables from `.env`:

* MAILSAC_API_KEY
* ADMIN_EMAIL
* ADMIN_PASSWORD
* EMPTY_BALANCE_USER_EMAIL
* EMPTY_BALANCE_USER_PASSWORD
* SOME_BALANCE_USER_EMAIL
* SOME_BALANCE_USER_PASSWORD
* TRANSLATION_ID
* TRANSLATION_ID_NO_EDIT
* URL  

### Running tests
### Local
To run all tests and generate an HTML report, execute:

`pytest --html=report.html --self-contained-html`.

To run tests from a specific file:

`pytest path/to/test_file.py --html=report.html --self-contained-html`.

The `report.html` report will be created in the current directory. 

### In GitHub Actions.

1. Click the Actions tab in your repository. 
2. Find the Workflow named Run API Tests and click on it. 
3. Click the Run workflow button. 
4. In the window that appears:
   1. If you want to run all tests, leave the test_file field blank. 
   2. If you want to run the tests from a specific file, specify only the file name, e.g.: `test_example.py`.
   3. The path to the file (tests/test_example.py) will be added automatically. 
   4. Click Run workflow to start the workflow.
5. After the Workflow completes execution:
6. Navigate to the Artifacts section of the run page. 
7. Download the pytest-html-report artifact. 
8. Unzip the archive and open the report.html file in any browser to view the results.
