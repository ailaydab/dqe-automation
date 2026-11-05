*** Settings ***
Library           SeleniumLibrary
Library           helper.py
Test Teardown     Close All Browsers

*** Variables ***
${REPORT_FILE}       ${CURDIR}${/}..${/}report.html
${PARQUET_FOLDER}    ${CURDIR}${/}..${/}parquet_data${/}parquet_data${/}facility_type_avg_time_spent_per_visit_date
${FILTER_DATE}       2026-10-02
${DATE_COLUMN}       visit_date
${PLOTLY_OPTIONS}    add_argument("--headless=new");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")

*** Test Cases ***
HTML Report Should Match Parquet Dataset
    [Documentation]    Compares the table in report.html with the Parquet data.
    ${report_url}=    Evaluate    pathlib.Path(r"${REPORT_FILE}").resolve().as_uri()    modules=pathlib
    Open Browser    ${report_url}    chrome    options=${PLOTLY_OPTIONS}
    Wait Until Element Is Visible    css:.plotly-graph-div svg.main-svg    timeout=10s
    ${plot}=    Get WebElement    css:.plotly-graph-div
    ${html_df}=    Read Plotly Table To Dataframe    ${plot}    ${FILTER_DATE}    ${DATE_COLUMN}
    ${parquet_df}=    Read Partitioned Parquet    ${PARQUET_FOLDER}    ${FILTER_DATE}    ${DATE_COLUMN}
    ${diffs}=    Compare Dataframes    ${html_df}    ${parquet_df}
    Should Be Empty    ${diffs}    DataFrame differences found: ${diffs}