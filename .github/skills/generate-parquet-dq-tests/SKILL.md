---
name: generate-parquet-dq-tests
description: >-
  TODO: One or two sentences — what the skill generates, when to invoke it,
  and what it must refuse (framework/Jenkins/conftest). Example pattern:
  "Creates parquet_files test modules from docs/parquet-aggregated-data-mapping.md …"
disable-model-invocation: true
---

# Generate Parquet DQ tests

Complete this skill as **Step 2** of the PyTest DQ assignment. Read first:

- `PyTest DQ Framework/docs/test-automation-strategy.md` — **§5 Skill contract**, **§6 Test design standard**
- `docs/parquet-aggregated-data-mapping.md` — dataset definitions (expected SQL comes from here)

**Do not** paste expected SQL for the three named datasets into this skill.  
**Do not** instruct the agent to copy SQL from `data_dev/`.

When finished, every `TODO` below must be replaced. Run the **Skill review** checklist before using the skill to generate tests.

## When this skill applies

- Use this skill when generating automated PyTest Data Quality test modules for target Parquet datasets based strictly on data mapping specifications.
- Must only be used after framework infrastructure (`conftest.py`, connectors, `DataQualityLibrary`) is fully established.
- Target path for generated test modules: `PyTest DQ Framework/tests/dq checks/parquet_files/`.
- Refuse if mapping documentation is absent, if asked to use forbidden sources, or if requested to hardcode expected dataset outputs.

## Inputs you must have

- **Data Mapping Specifications**: Located at `docs/parquet-aggregated-data-mapping.md`, defining target columns, transformations, source tables, source columns, primary keys, non-null columns, and grouping/partition keys.
- **Action if missing**: Abort immediately and request the mapping document if it is missing.
- **Forbidden sources**: Do not use `data_dev/` scripts or parquet loader SQL as query templates.

## Hard rules

1. **File Path**: Place generated test modules exclusively under `PyTest DQ Framework/tests/dq checks/parquet_files/`.
2. **Source vs Target**: Compare PostgreSQL source query results against target Parquet dataset loaded via `parquet_reader`.
3. **Mapping-Only SQL**: Derive expected queries strictly and exclusively from `docs/parquet-aggregated-data-mapping.md`.
4. **No Dataset SQL in SKILL.md**: Keep SQL derivation rules entirely generic (joins, date casting, string concatenation, aggregates, GROUP BY).
5. **Library Methods Only**: Exclusively use `DataQualityLibrary` static methods (`check_dataset_is_not_empty`, `check_completeness`, `check_count`, `check_duplicates`, `check_not_null_values`).
6. **Markers**: Apply `@pytest.mark.parquet_data` decorator to all generated test functions or modules.
7. **Not-Null Validation**: Explicitly validate all columns specified as `not null` in the mapping.

## Workflow

1. Read the target dataset mapping definition from `docs/parquet-aggregated-data-mapping.md`.
2. Derive the expected PostgreSQL source query using tables, columns, transformations, and filters from the mapping.
3. Determine the corresponding Parquet target file path.
4. Generate the test module containing smoke, completeness, count, uniqueness, and not-null checks.
5. Apply `@pytest.mark.parquet_data` markers to all test cases.


## Template
```python
import pytest
 
@pytest.mark.parquet_data
def test_smoke_and_not_empty(parquet_reader, data_quality_library):
  target_path = "tests/dq checks/parquet_files/<dataset_name>.parquet"
  target_data = parquet_reader.process(target_path)
  data_quality_library.check_dataset_is_not_empty(target_data)
 
@pytest.mark.parquet_data
def test_completeness(parquet_reader, data_quality_library):
  target_path = "tests/dq checks/parquet_files/<dataset_name>.parquet"
  target_data = parquet_reader.process(target_path)
  data_quality_library.check_completeness(target_data, expected_columns=["<col1>", "<col2>"])
 
@pytest.mark.parquet_data
def test_count(db_connection, parquet_reader, data_quality_library):
  source_query = """
    SELECT ... FROM ... GROUP BY ...
  """
  source_data = db_connection.get_data_sql(source_query)
  target_path = "tests/dq checks/parquet_files/<dataset_name>.parquet"
  target_data = parquet_reader.process(target_path)
  data_quality_library.check_count(source_data, target_data)
 
@pytest.mark.parquet_data
def test_uniqueness(parquet_reader, data_quality_library):
  target_path = "tests/dq checks/parquet_files/<dataset_name>.parquet"
  target_data = parquet_reader.process(target_path)
  data_quality_library.check_duplicates(target_data, column_names=["<pk_col>"])
 
@pytest.mark.parquet_data
def test_not_null_values(parquet_reader, data_quality_library):
  target_path = "tests/dq checks/parquet_files/<dataset_name>.parquet"
  target_data = parquet_reader.process(target_path)
  data_quality_library.check_not_null_values(target_data, column_names=["<not_null_col>"])
```
## SQL derivation (generic)

- **Joins**: Connect source tables (e.g., `table.facilities`, `table.visits`, `table.patients`) using primary and foreign key relationships defined in `docs/parquet-aggregated-data-mapping.md`.
- **Dates & Formatting**: Format date/timestamp fields or apply date extractions according to mapping rules and partitioning keys.
- **Strings & Names**: Handle string concatenations (such as combining first name and last name with spaces) as specified in target column comments.
- **Aggregates & Rounding**: Apply aggregate functions (`MIN`, `AVG`, `SUM`) with exact target column aliases and proper rounding (e.g., rounding average values to two decimal places).
- **Grouping**: Include `GROUP BY` clauses for all non-aggregated columns that match the grouping or partitioning requirements in the mapping.

## After generation
- Run `pytest` commands using `-m parquet_data` only when explicitly requested by the user.
- Do NOT rewrite or manipulate expected SQL queries artificially to force green test runs if data mismatches occur; report any discrepancies as mapping or data issues.


## Skill review (self-check before Step 3)

Reject your own skill if any of these are true:

- [ ] Contains concrete expected SQL for `facility_name_min_time_spent_per_visit_date`, `facility_type_avg_time_spent_per_visit_date`, or `patient_sum_treatment_cost_per_facility_type`
- [ ] Tells the agent to use `data_dev/` or parquet loader SQL
- [ ] Omits completeness, count, uniqueness, or not-null
- [ ] Swaps Postgres vs Parquet fixtures or generates trivial always-pass checks
- [ ] Any section still says `TODO`
