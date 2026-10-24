import pytest

@pytest.mark.parquet_data
def test_smoke_and_not_empty(parquet_reader, data_quality_library):
    target_path =  "/workspaces/dqe-automation/parquet_data/facility_type_avg_time_spent_per_visit_date"
    target_data = parquet_reader.process(target_path)
    data_quality_library.check_dataset_is_not_empty(target_data)
 
@pytest.mark.parquet_data
def test_completeness(parquet_reader, data_quality_library):
    target_path =  "/workspaces/dqe-automation/parquet_data/facility_type_avg_time_spent_per_visit_date"
    target_data = parquet_reader.process(target_path)
    expected_columns = ["facility_type", "visit_date", "avg_time_spent"]
    data_quality_library.check_completeness(target_data, expected_columns=expected_columns)
 
@pytest.mark.parquet_data
def test_count(db_connection, parquet_reader, data_quality_library):
    source_query = """
        SELECT
            f.facility_type,
            CAST(v.visit_timestamp AS DATE) AS visit_date,
            ROUND(CAST(AVG(v.duration_minutes) AS NUMERIC), 2) AS avg_time_spent
        FROM facilities f
        JOIN visits v ON f.id = v.facility_id
        GROUP BY f.facility_type, CAST(v.visit_timestamp AS DATE)
    """
    source_data = db_connection.get_data_sql(source_query)
    target_path =  "/workspaces/dqe-automation/parquet_data/facility_type_avg_time_spent_per_visit_date"
    target_data = parquet_reader.process(target_path)
    data_quality_library.check_count(source_data, target_data)
 
@pytest.mark.parquet_data
def test_uniqueness(parquet_reader, data_quality_library):
    target_path =  "/workspaces/dqe-automation/parquet_data/facility_type_avg_time_spent_per_visit_date"
    target_data = parquet_reader.process(target_path)
    data_quality_library.check_duplicates(target_data, column_names=["facility_type", "visit_date"])
 
@pytest.mark.parquet_data
def test_not_null_values(parquet_reader, data_quality_library):
    target_path =  "/workspaces/dqe-automation/parquet_data/facility_type_avg_time_spent_per_visit_date"
    target_data = parquet_reader.process(target_path)
    not_null_columns = ["facility_type", "visit_date", "avg_time_spent"]
    data_quality_library.check_not_null_values(target_data, column_names=not_null_columns)