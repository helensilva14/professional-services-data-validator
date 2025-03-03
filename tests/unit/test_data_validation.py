# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import pandas
import pytest
import random
from datetime import datetime, timedelta
from unittest import mock
from google.cloud import bigquery

import ibis.expr.datatypes as dt

from data_validation import consts


SOURCE_TABLE_FILE_PATH = "source_table_data.json"
TARGET_TABLE_FILE_PATH = "target_table_data.json"

DUMMY_RUN_ID = "aa000000-0000-0000-0000-000000000001"

SOURCE_CONN_CONFIG = {
    consts.SOURCE_TYPE: "FileSystem",
    consts.CONFIG_TABLE_NAME: "my_table",
    "file_path": SOURCE_TABLE_FILE_PATH,
    "file_type": "json",
}

TARGET_CONN_CONFIG = {
    consts.SOURCE_TYPE: "FileSystem",
    consts.CONFIG_TABLE_NAME: "my_table",
    "file_path": TARGET_TABLE_FILE_PATH,
    "file_type": "json",
}

SAMPLE_CONFIG = {
    # BigQuery Specific Connection Config
    consts.CONFIG_SOURCE_CONN: SOURCE_CONN_CONFIG,
    consts.CONFIG_TARGET_CONN: TARGET_CONN_CONFIG,
    # Validation Type
    consts.CONFIG_TYPE: consts.COLUMN_VALIDATION,
    # Configuration Required Depending on Validator Type
    consts.CONFIG_SCHEMA_NAME: None,
    consts.CONFIG_TABLE_NAME: "my_table",
    consts.CONFIG_TARGET_SCHEMA_NAME: None,
    consts.CONFIG_TARGET_TABLE_NAME: "my_table",
    consts.CONFIG_GROUPED_COLUMNS: [],
    consts.CONFIG_AGGREGATES: [
        {
            "source_column": "col_a",
            "target_column": "col_a",
            "field_alias": "count_col_a",
            "type": "count",
        },
        {
            "source_column": "col_b",
            "target_column": "col_b",
            "field_alias": "count_col_b",
            "type": "count",
        },
    ],
    consts.CONFIG_THRESHOLD: 0.0,
    consts.CONFIG_RESULT_HANDLER: None,
    consts.CONFIG_FORMAT: "table",
    consts.CONFIG_FILTER_STATUS: None,
}

SAMPLE_THRESHOLD_CONFIG = {
    # BigQuery Specific Connection Config
    consts.CONFIG_SOURCE_CONN: SOURCE_CONN_CONFIG,
    consts.CONFIG_TARGET_CONN: TARGET_CONN_CONFIG,
    # Validation Type
    consts.CONFIG_TYPE: consts.COLUMN_VALIDATION,
    # Configuration Required Depending on Validator Type
    consts.CONFIG_SCHEMA_NAME: None,
    consts.CONFIG_TABLE_NAME: "my_table",
    consts.CONFIG_TARGET_SCHEMA_NAME: None,
    consts.CONFIG_TARGET_TABLE_NAME: "my_table",
    consts.CONFIG_GROUPED_COLUMNS: [],
    consts.CONFIG_AGGREGATES: [
        {
            "source_column": "col_a",
            "target_column": "col_a",
            "field_alias": "count_col_a",
            "type": "count",
        },
        {
            "source_column": "col_b",
            "target_column": "col_b",
            "field_alias": "count_col_b",
            "type": "count",
        },
    ],
    consts.CONFIG_THRESHOLD: 150.0,
    consts.CONFIG_RESULT_HANDLER: None,
    consts.CONFIG_FORMAT: "table",
    consts.CONFIG_FILTER_STATUS: None,
}

# Grouped Column Row config
SAMPLE_GC_CONFIG = {
    # BigQuery Specific Connection Config
    consts.CONFIG_SOURCE_CONN: SOURCE_CONN_CONFIG,
    consts.CONFIG_TARGET_CONN: TARGET_CONN_CONFIG,
    # Validation Type
    consts.CONFIG_TYPE: consts.COLUMN_VALIDATION,
    consts.CONFIG_MAX_RECURSIVE_QUERY_SIZE: 50,
    # Configuration Required Depending on Validator Type
    consts.CONFIG_SCHEMA_NAME: None,
    consts.CONFIG_TABLE_NAME: "my_table",
    consts.CONFIG_TARGET_SCHEMA_NAME: None,
    consts.CONFIG_TARGET_TABLE_NAME: "my_table",
    consts.CONFIG_GROUPED_COLUMNS: [
        {
            consts.CONFIG_FIELD_ALIAS: "date_value",
            consts.CONFIG_SOURCE_COLUMN: "date_value",
            consts.CONFIG_TARGET_COLUMN: "date_value",
            consts.CONFIG_CAST: "date",
        },
    ],
    consts.CONFIG_PRIMARY_KEYS: [
        {
            consts.CONFIG_FIELD_ALIAS: "id",
            consts.CONFIG_SOURCE_COLUMN: "id",
            consts.CONFIG_TARGET_COLUMN: "id",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_AGGREGATES: [
        {
            "source_column": "text_value",
            "target_column": "text_value",
            "field_alias": "count_text_value",
            "type": "count",
        },
    ],
    consts.CONFIG_RESULT_HANDLER: None,
    consts.CONFIG_FORMAT: "table",
    consts.CONFIG_FILTER_STATUS: None,
}

# Grouped Column Row config
SAMPLE_MULTI_GC_CONFIG = {
    # BigQuery Specific Connection Config
    consts.CONFIG_SOURCE_CONN: SOURCE_CONN_CONFIG,
    consts.CONFIG_TARGET_CONN: TARGET_CONN_CONFIG,
    # Validation Type
    consts.CONFIG_TYPE: consts.COLUMN_VALIDATION,
    consts.CONFIG_MAX_RECURSIVE_QUERY_SIZE: 50,
    # Configuration Required Depending on Validator Type
    consts.CONFIG_SCHEMA_NAME: None,
    consts.CONFIG_TABLE_NAME: "my_table",
    consts.CONFIG_TARGET_SCHEMA_NAME: None,
    consts.CONFIG_TARGET_TABLE_NAME: "my_table",
    consts.CONFIG_GROUPED_COLUMNS: [
        {
            consts.CONFIG_FIELD_ALIAS: "date_value",
            consts.CONFIG_SOURCE_COLUMN: "date_value",
            consts.CONFIG_TARGET_COLUMN: "date_value",
            consts.CONFIG_CAST: "date",
        },
        {
            consts.CONFIG_FIELD_ALIAS: "id",
            consts.CONFIG_SOURCE_COLUMN: "id",
            consts.CONFIG_TARGET_COLUMN: "id",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_PRIMARY_KEYS: [
        {
            consts.CONFIG_FIELD_ALIAS: "id",
            consts.CONFIG_SOURCE_COLUMN: "id",
            consts.CONFIG_TARGET_COLUMN: "id",
            consts.CONFIG_CAST: None,
        }
    ],
    consts.CONFIG_AGGREGATES: [
        {
            "source_column": "text_value",
            "target_column": "text_value",
            "field_alias": "count_text_value",
            "type": "count",
        },
    ],
    consts.CONFIG_RESULT_HANDLER: None,
    consts.CONFIG_FORMAT: "table",
    consts.CONFIG_FILTER_STATUS: None,
}

SAMPLE_GC_CALC_CONFIG = {
    # BigQuery Specific Connection Config
    consts.CONFIG_SOURCE_CONN: SOURCE_CONN_CONFIG,
    consts.CONFIG_TARGET_CONN: TARGET_CONN_CONFIG,
    # Validation Type
    consts.CONFIG_TYPE: consts.COLUMN_VALIDATION,
    consts.CONFIG_MAX_RECURSIVE_QUERY_SIZE: 50,
    # Configuration Required Depending on Validator Type
    consts.CONFIG_SCHEMA_NAME: None,
    consts.CONFIG_TABLE_NAME: "my_table",
    consts.CONFIG_TARGET_SCHEMA_NAME: None,
    consts.CONFIG_TARGET_TABLE_NAME: "my_table",
    consts.CONFIG_GROUPED_COLUMNS: [
        {
            consts.CONFIG_FIELD_ALIAS: "date_value",
            consts.CONFIG_SOURCE_COLUMN: "date_value",
            consts.CONFIG_TARGET_COLUMN: "date_value",
            consts.CONFIG_CAST: "date",
        },
    ],
    consts.CONFIG_PRIMARY_KEYS: [
        {
            consts.CONFIG_FIELD_ALIAS: "id",
            consts.CONFIG_SOURCE_COLUMN: "id",
            consts.CONFIG_TARGET_COLUMN: "id",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_CALCULATED_FIELDS: [
        {
            "source_calculated_columns": ["text_constant"],
            "target_calculated_columns": ["text_constant"],
            "field_alias": "length_text_constant",
            "type": "length",
            "depth": 0,
        },
        {
            "source_calculated_columns": ["text_constant"],
            "target_calculated_columns": ["text_constant"],
            "field_alias": "upper_text_constant",
            "type": "upper",
            "depth": 0,
        },
        {
            "source_calculated_columns": [
                "length_text_constant",
                "upper_text_constant",
            ],
            "target_calculated_columns": [
                "length_text_constant",
                "upper_text_constant",
            ],
            "field_alias": "concat_multi",
            "type": "concat",
            "depth": 1,
        },
        {
            "source_calculated_columns": ["concat_multi"],
            "target_calculated_columns": ["concat_multi"],
            "field_alias": "concat_length",
            "type": "length",
            "depth": 2,
        },
    ],
    consts.CONFIG_AGGREGATES: [
        {
            "source_column": "text_value",
            "target_column": "text_value",
            "field_alias": "count_text_value",
            "type": "count",
        },
        {
            "source_column": "length_text_constant",
            "target_column": "length_text_constant",
            "field_alias": "sum_length",
            "type": "sum",
        },
        {
            "source_column": "text_numeric",
            "target_column": "text_numeric",
            "field_alias": "sum_text_numeric",
            "type": "sum",
            "cast": "int64",
        },
        {
            "source_column": "concat_length",
            "target_column": "concat_length",
            "field_alias": "sum_concat_length",
            "type": "sum",
        },
    ],
    consts.CONFIG_RESULT_HANDLER: None,
    consts.CONFIG_FORMAT: "table",
    consts.CONFIG_FILTER_STATUS: None,
}


# Row config
SAMPLE_ROW_CONFIG = {
    # BigQuery Specific Connection Config
    consts.CONFIG_SOURCE_CONN: SOURCE_CONN_CONFIG,
    consts.CONFIG_TARGET_CONN: TARGET_CONN_CONFIG,
    # Validation Type
    consts.CONFIG_TYPE: consts.ROW_VALIDATION,
    # Configuration Required Depending on Validator Type
    consts.CONFIG_SCHEMA_NAME: None,
    consts.CONFIG_TABLE_NAME: "my_table",
    consts.CONFIG_TARGET_SCHEMA_NAME: None,
    consts.CONFIG_TARGET_TABLE_NAME: "my_table",
    consts.CONFIG_PRIMARY_KEYS: [
        {
            consts.CONFIG_FIELD_ALIAS: "id",
            consts.CONFIG_SOURCE_COLUMN: "id",
            consts.CONFIG_TARGET_COLUMN: "id",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_COMPARISON_FIELDS: [
        {
            consts.CONFIG_FIELD_ALIAS: "int_value",
            consts.CONFIG_SOURCE_COLUMN: "int_value",
            consts.CONFIG_TARGET_COLUMN: "int_value",
            consts.CONFIG_CAST: None,
        },
        {
            consts.CONFIG_FIELD_ALIAS: "text_value",
            consts.CONFIG_SOURCE_COLUMN: "text_value",
            consts.CONFIG_TARGET_COLUMN: "text_value",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_RESULT_HANDLER: {
        consts.CONFIG_TYPE: "BigQuery",
        consts.PROJECT_ID: "my-project",
        consts.TABLE_ID: "dataset.table_name",
    },
    consts.CONFIG_FORMAT: "text",
    consts.CONFIG_FILTER_STATUS: None,
}

# Row config
SAMPLE_JSON_ROW_CONFIG = {
    # BigQuery Specific Connection Config
    consts.CONFIG_SOURCE_CONN: SOURCE_CONN_CONFIG,
    consts.CONFIG_TARGET_CONN: TARGET_CONN_CONFIG,
    # Validation Type
    consts.CONFIG_TYPE: consts.ROW_VALIDATION,
    # Configuration Required Depending on Validator Type
    consts.CONFIG_SCHEMA_NAME: None,
    consts.CONFIG_TABLE_NAME: "my_table",
    consts.CONFIG_TARGET_SCHEMA_NAME: None,
    consts.CONFIG_TARGET_TABLE_NAME: "my_table",
    consts.CONFIG_PRIMARY_KEYS: [
        {
            consts.CONFIG_FIELD_ALIAS: "pkey",
            consts.CONFIG_SOURCE_COLUMN: "pkey",
            consts.CONFIG_TARGET_COLUMN: "pkey",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_COMPARISON_FIELDS: [
        {
            consts.CONFIG_FIELD_ALIAS: "col_b",
            consts.CONFIG_SOURCE_COLUMN: "col_b",
            consts.CONFIG_TARGET_COLUMN: "col_b",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_RESULT_HANDLER: None,
    consts.CONFIG_FORMAT: "table",
    consts.CONFIG_FILTER_STATUS: None,
}

# Row validation where we only care about failures and we write them to BQ
SAMPLE_ROW_CONFIG_BQ_FAILURES = {
    # BigQuery Specific Connection Config
    consts.CONFIG_SOURCE_CONN: SOURCE_CONN_CONFIG,
    consts.CONFIG_TARGET_CONN: TARGET_CONN_CONFIG,
    # Validation Type
    consts.CONFIG_TYPE: consts.ROW_VALIDATION,
    # Configuration Required Depending on Validator Type
    consts.CONFIG_SCHEMA_NAME: None,
    consts.CONFIG_TABLE_NAME: "my_table",
    consts.CONFIG_TARGET_SCHEMA_NAME: None,
    consts.CONFIG_TARGET_TABLE_NAME: "my_table",
    consts.CONFIG_PRIMARY_KEYS: [
        {
            consts.CONFIG_FIELD_ALIAS: "id",
            consts.CONFIG_SOURCE_COLUMN: "id",
            consts.CONFIG_TARGET_COLUMN: "id",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_COMPARISON_FIELDS: [
        {
            consts.CONFIG_FIELD_ALIAS: "int_value",
            consts.CONFIG_SOURCE_COLUMN: "int_value",
            consts.CONFIG_TARGET_COLUMN: "int_value",
            consts.CONFIG_CAST: None,
        },
        {
            consts.CONFIG_FIELD_ALIAS: "text_value",
            consts.CONFIG_SOURCE_COLUMN: "text_value",
            consts.CONFIG_TARGET_COLUMN: "text_value",
            consts.CONFIG_CAST: None,
        },
    ],
    consts.CONFIG_RESULT_HANDLER: {
        consts.CONFIG_TYPE: "BigQuery",
        consts.PROJECT_ID: "my-project",
        consts.TABLE_ID: "dataset.table_name",
    },
    consts.CONFIG_FORMAT: "text",
    consts.CONFIG_FILTER_STATUS: ["fail"],
    consts.CONFIG_RUN_ID: DUMMY_RUN_ID,
}

JSON_DATA = """[{"col_a":1,"col_b":"a"},{"col_a":1,"col_b":"b"}]"""
JSON_COLA_ZERO_DATA = """[{"col_a":null,"col_b":"a"}]"""
JSON_BAD_DATA = """[{"col_a":0,"col_b":"a"},{"col_a":1,"col_b":"b"},{"col_a":2,"col_b":"c"},{"col_a":3,"col_b":"d"},{"col_a":4,"col_b":"e"}]"""
JSON_PK_DATA = (
    """[{"pkey":1, "col_a":1,"col_b":"a"},{"pkey":2, "col_a":1,"col_b":"b"}]"""
)
JSON_PK_BAD_DATA = """[{"pkey":1, "col_a":0,"col_b":"b"},{"pkey":2, "col_a":1,"col_b":"c"},{"pkey":3, "col_a":2,"col_b":"d"},{"pkey":4, "col_a":3,"col_b":"e"},{"pkey":5, "col_a":4,"col_b":"f"}]"""

STRING_CONSTANT = "constant"

SOURCE_QUERY_DATA = [
    {
        "date": "2020-01-01",
        "int_val": 1,
        "double_val": 2.3,
        "text_constant": STRING_CONSTANT,
        "text_numeric": "2",
        "text_val": "hello",
        "text_val_two": "goodbye",
    }
]
SOURCE_DF = pandas.DataFrame(SOURCE_QUERY_DATA)
JOIN_ON_DATE_FIELDS = {"date": dt.Date()}
NON_OBJECT_FIELDS = pandas.Index(["int_val", "double_val"])

RANDOM_STRINGS = ["a", "b", "c", "d"]

CAPLOG_DF_HEADER = "validation_name validation_type source_table_name source_column_name source_agg_value target_agg_value pct_difference validation_status"


@pytest.fixture
def ibis_pandas():
    import ibis

    return ibis.pandas.connect()


@pytest.fixture
def module_under_test(ibis_pandas):
    import data_validation.data_validation

    return data_validation.data_validation


def _create_table_file(table_path, data):
    """Create JSON File"""
    with open(table_path, "w") as f:
        f.write(data)


def _generate_fake_data(
    rows=10, initial_id=0, second_range=60 * 60 * 24, int_range=100, random_strings=None
):
    """Return a list of dicts with given number of rows.

    Data Keys:
        id: a unique int per row
        timestamp_value: a random timestamp in the past {second_range} back
        date_value: a random date in the past {second_range} back
        int_value: a random int value inside 0 to {int_range}
        text_value: a random string from supplied list
    """
    data = []
    random_strings = random_strings or RANDOM_STRINGS
    for i in range(initial_id, initial_id + rows):
        rand_seconds = random.randint(0, second_range)
        rand_timestamp = datetime.now() - timedelta(seconds=rand_seconds)
        rand_date = rand_timestamp.date()

        row = {
            "id": i,
            "date_value": rand_date,
            "timestamp_value": rand_timestamp,
            "int_value": random.randint(0, int_range),
            "text_constant": STRING_CONSTANT,
            "text_numeric": "2",
            "text_value": random.choice(random_strings),
            "text_value_two": random.choice(random_strings),
        }
        data.append(row)

    return data


def _get_fake_json_data(data):
    for row in data:
        row["date_value"] = str(row["date_value"])
        row["timestamp_value"] = str(row["timestamp_value"])
        row["text_constant"] = row["text_constant"]
        row["text_numeric"] = row["text_numeric"]
        row["text_value"] = row["text_value"]
        row["text_value_two"] = row["text_value_two"]

    return json.dumps(data)


def test_import(module_under_test):
    assert True


def test_data_validation_client(module_under_test, fs):
    """Test getting a Data Validation Client"""
    _create_table_file(SOURCE_TABLE_FILE_PATH, JSON_DATA)
    _create_table_file(TARGET_TABLE_FILE_PATH, JSON_DATA)

    client = module_under_test.DataValidation(SAMPLE_CONFIG)
    result_df = client.execute()
    assert int(result_df.source_agg_value[0]) == 2


def test_zero_source_value(module_under_test, fs):
    _create_table_file(SOURCE_TABLE_FILE_PATH, JSON_COLA_ZERO_DATA)
    _create_table_file(TARGET_TABLE_FILE_PATH, JSON_DATA)

    client = module_under_test.DataValidation(SAMPLE_CONFIG)
    result_df = client.execute()

    col_a_result_df = result_df[result_df.validation_name == "count_col_a"]
    col_a_pct_diff = col_a_result_df.pct_difference.values[0]

    assert col_a_pct_diff == 100


def test_zero_target_value(module_under_test, fs):
    _create_table_file(SOURCE_TABLE_FILE_PATH, JSON_DATA)
    _create_table_file(TARGET_TABLE_FILE_PATH, JSON_COLA_ZERO_DATA)

    client = module_under_test.DataValidation(SAMPLE_CONFIG)
    result_df = client.execute()

    col_a_result_df = result_df[result_df.validation_name == "count_col_a"]
    col_a_pct_diff = col_a_result_df.pct_difference.values[0]

    assert col_a_pct_diff == -100


def test_zero_both_values(module_under_test, fs):
    _create_table_file(SOURCE_TABLE_FILE_PATH, JSON_COLA_ZERO_DATA)
    _create_table_file(TARGET_TABLE_FILE_PATH, JSON_COLA_ZERO_DATA)

    client = module_under_test.DataValidation(SAMPLE_CONFIG)
    result_df = client.execute()

    col_a_result_df = result_df[result_df.validation_name == "count_col_a"]
    col_a_pct_diff = col_a_result_df.pct_difference.values[0]

    assert col_a_pct_diff == 0.0


def test_status_success_validation(module_under_test, fs):
    _create_table_file(SOURCE_TABLE_FILE_PATH, JSON_DATA)
    _create_table_file(TARGET_TABLE_FILE_PATH, JSON_DATA)

    client = module_under_test.DataValidation(SAMPLE_CONFIG)
    result_df = client.execute()

    col_a_result_df = result_df[result_df.validation_name == "count_col_a"]
    col_a_pct_threshold = col_a_result_df.pct_threshold.values[0]
    col_a_status = col_a_result_df.validation_status.values[0]

    assert col_a_pct_threshold == 0.0
    assert col_a_status == consts.VALIDATION_STATUS_SUCCESS


def test_status_fail_validation(module_under_test, fs):
    _create_table_file(SOURCE_TABLE_FILE_PATH, JSON_DATA)
    _create_table_file(TARGET_TABLE_FILE_PATH, JSON_COLA_ZERO_DATA)

    client = module_under_test.DataValidation(SAMPLE_CONFIG)
    result_df = client.execute()
    col_a_result_df = result_df[result_df.validation_name == "count_col_a"]
    col_a_pct_threshold = col_a_result_df.pct_threshold.values[0]
    col_a_status = col_a_result_df.validation_status.values[0]

    assert col_a_pct_threshold == 0.0
    assert col_a_status == consts.VALIDATION_STATUS_FAIL


def test_threshold_equals_diff(module_under_test, fs):
    _create_table_file(SOURCE_TABLE_FILE_PATH, JSON_DATA)
    _create_table_file(TARGET_TABLE_FILE_PATH, JSON_BAD_DATA)

    client = module_under_test.DataValidation(SAMPLE_THRESHOLD_CONFIG)
    result_df = client.execute()
    col_a_result_df = result_df[result_df.validation_name == "count_col_a"]
    col_a_pct_diff = col_a_result_df.pct_difference.values[0]
    col_a_pct_threshold = col_a_result_df.pct_threshold.values[0]
    col_a_status = col_a_result_df.validation_status.values[0]

    assert col_a_pct_diff == 150.0
    assert col_a_pct_threshold == 150.0
    assert col_a_status == consts.VALIDATION_STATUS_SUCCESS


def test_grouped_column_level_validation_perfect_match(module_under_test, fs):
    data = _generate_fake_data(second_range=0)
    json_data = _get_fake_json_data(data)

    _create_table_file(SOURCE_TABLE_FILE_PATH, json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, json_data)

    client = module_under_test.DataValidation(SAMPLE_GC_CONFIG)
    result_df = client.execute()

    expected_date_result = '{"date_value": "%s"}' % str(datetime.now().date())
    assert expected_date_result == result_df["group_by_columns"].max()

    assert result_df["difference"].sum() == 0


def test_calc_field_validation_calc_match(module_under_test, fs):
    num_rows = 100
    data = _generate_fake_data(rows=num_rows, second_range=0)
    json_data = _get_fake_json_data(data)

    _create_table_file(SOURCE_TABLE_FILE_PATH, json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, json_data)

    client = module_under_test.DataValidation(SAMPLE_GC_CALC_CONFIG)
    result_df = client.execute()
    calc_val_df = result_df[result_df["validation_name"] == "sum_length"]
    calc_val_df2 = result_df[result_df["validation_name"] == "sum_concat_length"]
    calc_val_df3 = result_df[result_df["validation_name"] == "sum_text_numeric"]

    assert calc_val_df["source_agg_value"].sum() == str(num_rows * len(STRING_CONSTANT))

    assert calc_val_df2["source_agg_value"].sum() == str(
        num_rows * (len(STRING_CONSTANT + str(len(STRING_CONSTANT))))
    )

    assert calc_val_df3["source_agg_value"].sum() == str(num_rows * 2)


def test_grouped_column_level_validation_non_matching(module_under_test, fs):
    data = _generate_fake_data(rows=10, second_range=0)
    trg_data = _generate_fake_data(initial_id=11, rows=1, second_range=0)
    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(data + trg_data)

    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)
    client = module_under_test.DataValidation(SAMPLE_GC_CONFIG)
    result_df = client.execute()
    validation_df = result_df[result_df["validation_name"] == "count_text_value"]
    # TODO: this value is 0 because a COUNT() on no rows returns Null
    assert result_df["difference"].sum() == 1

    expected_date_result = '{"date_value": "%s"}' % str(datetime.now().date())
    grouped_column = validation_df["group_by_columns"].max()
    assert expected_date_result == grouped_column


def test_grouped_column_level_validation_smart_count(module_under_test, fs):
    data = _generate_fake_data(rows=100, second_range=0)

    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(data + data)

    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)

    client = module_under_test.DataValidation(SAMPLE_GC_CONFIG)
    result_df = client.execute()
    expected_date_result = '{"date_value": "%s"}' % str(datetime.now().date())

    assert expected_date_result == result_df["group_by_columns"].max()

    smart_count_df = result_df[result_df["validation_name"] == "count_text_value"]
    assert smart_count_df["source_agg_value"].astype(int).sum() == 100
    assert smart_count_df["target_agg_value"].astype(int).sum() == 200


def test_grouped_column_level_validation_multiple_aggregations(module_under_test):
    data = _generate_fake_data(rows=10, second_range=0)
    trg_data = _generate_fake_data(initial_id=11, rows=1, second_range=0)

    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(data + trg_data)

    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)

    client = module_under_test.DataValidation(SAMPLE_MULTI_GC_CONFIG)
    result_df = client.execute()
    validation_df = result_df  # [result_df["validation_name"] == "count_text_value"]
    # Expect 11 rows, one for each PK value
    assert len(validation_df) == 11
    assert validation_df["source_agg_value"].astype(float).sum() == 10
    assert validation_df["target_agg_value"].astype(float).sum() == 11


def test_row_level_validation(module_under_test, fs, monkeypatch):
    # Mock the big query client
    mock_bq_client = mock.create_autospec(bigquery.Client)
    monkeypatch.setattr(bigquery, "Client", value=mock_bq_client)
    # With some mocked data - source and target the same
    data = _generate_fake_data(rows=100, second_range=0)
    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(data)
    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)
    # When we validate
    client = module_under_test.DataValidation(SAMPLE_ROW_CONFIG)
    result_df = client.execute()
    # Then we expect
    str_comparison_df = result_df[result_df["validation_name"] == "text_value"]
    int_comparison_df = result_df[result_df["validation_name"] == "int_value"]
    assert len(result_df) == 200
    assert len(str_comparison_df) == 100
    assert len(int_comparison_df) == 100


def test_fail_row_level_validation(module_under_test, fs):
    _create_table_file(SOURCE_TABLE_FILE_PATH, JSON_PK_DATA)
    _create_table_file(TARGET_TABLE_FILE_PATH, JSON_PK_BAD_DATA)

    client = module_under_test.DataValidation(SAMPLE_JSON_ROW_CONFIG)
    result_df = client.execute()

    # based on shared keys
    fail_df = result_df[result_df["validation_status"] == consts.VALIDATION_STATUS_FAIL]
    assert len(fail_df) == 5


def test_bad_join_row_level_validation(module_under_test, fs, caplog, monkeypatch):
    # Mock the big query client
    mock_bq_client = mock.create_autospec(bigquery.Client)
    monkeypatch.setattr(bigquery, "Client", value=mock_bq_client)
    # With some mocked data - source and target different
    data = _generate_fake_data(rows=100, second_range=0)
    target_data = _generate_fake_data(initial_id=100, rows=1, second_range=0)
    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(target_data)
    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)
    # ... and the log level being DEBUG
    caplog.set_level(logging.DEBUG)
    # When we validate
    client = module_under_test.DataValidation(SAMPLE_ROW_CONFIG)
    result_df = client.execute()
    comparison_df = result_df[
        result_df["validation_status"] == consts.VALIDATION_STATUS_FAIL
    ]
    # Then we expect
    # 2 validations * (100 source + 1 target)
    assert len(result_df) == 202
    assert len(comparison_df) == 202
    # The "Results written" message happens + info about the failed data, all against a generated run_id
    # assert len(caplog.records) == 202
    run_id = result_df.iloc[0]["run_id"]
    assert run_id != DUMMY_RUN_ID
    assert any(
        _
        for _ in caplog.records
        if _.message == f"Results written to BigQuery, run id: {run_id}"
    )
    assert any(
        _
        for _ in caplog.records
        if "validation_name validation_type source_table_name source_column_name source_agg_value target_agg_value pct_difference validation_status"
        in _.message
    )
    assert any(_ for _ in caplog.records if f"fail {run_id}" in _.message)


def test_no_console_data_shown_for_validation_with_result_written_to_bq_in_info_mode(
    module_under_test, fs, caplog, monkeypatch
):
    # Mock the big query client
    mock_bq_client = mock.create_autospec(bigquery.Client)
    monkeypatch.setattr(bigquery, "Client", value=mock_bq_client)
    # With some mocked data - source and target different
    data = _generate_fake_data(rows=10, second_range=0)
    trg_data = _generate_fake_data(initial_id=11, rows=1, second_range=0)
    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(data + trg_data)
    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)
    # ... and the log level being INFO
    caplog.set_level(logging.INFO)
    # When we validate
    client = module_under_test.DataValidation(SAMPLE_ROW_CONFIG_BQ_FAILURES)
    result_df = client.execute()
    # Then...
    # 2 failures returned
    assert len(result_df) == 2
    fail_df = result_df[result_df["validation_status"] == consts.VALIDATION_STATUS_FAIL]
    assert len(fail_df) == 2
    # Only the "Results written" message happens
    # Important because the results could include sensitive data, which some users need to exclude
    caplog_messages = [_.message for _ in caplog.records]
    assert f"Results written to BigQuery, run id: {DUMMY_RUN_ID}" in caplog_messages


def test_no_console_data_shown_for_matching_validation_with_result_written_to_bq_in_info_mode(
    module_under_test, fs, caplog, monkeypatch
):
    # Mock the big query client
    mock_bq_client = mock.create_autospec(bigquery.Client)
    monkeypatch.setattr(bigquery, "Client", value=mock_bq_client)
    # With some mocked data - source and target the same
    data = _generate_fake_data(rows=10, second_range=0)
    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(data)
    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)
    # ... and the log level being INFO
    caplog.set_level(logging.INFO)
    # When we validate
    client = module_under_test.DataValidation(SAMPLE_ROW_CONFIG_BQ_FAILURES)
    result_df = client.execute()
    # Then...
    # 0 failures returned
    assert len(result_df) == 0
    # Only the "No results" message happens
    caplog_messages = [_.message for _ in caplog.records]
    assert not any([_ for _ in caplog_messages if CAPLOG_DF_HEADER in _])
    assert "No results to write to BigQuery" in caplog_messages


def test_console_data_shown_for_validation_with_result_written_to_bq_in_debug_mode(
    module_under_test, fs, caplog, monkeypatch
):
    # Mock the big query client
    mock_bq_client = mock.create_autospec(bigquery.Client)
    monkeypatch.setattr(bigquery, "Client", value=mock_bq_client)
    # With some mocked data - source and target different
    data = _generate_fake_data(rows=10, second_range=0)
    trg_data = _generate_fake_data(initial_id=11, rows=1, second_range=0)
    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(data + trg_data)
    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)
    # ... and the log level being DEBUG
    caplog.set_level(logging.DEBUG)
    # When we validate
    client = module_under_test.DataValidation(SAMPLE_ROW_CONFIG_BQ_FAILURES)
    result_df = client.execute()
    # Then...
    # 2 failures returned
    assert len(result_df) == 2
    fail_df = result_df[result_df["validation_status"] == consts.VALIDATION_STATUS_FAIL]
    assert len(fail_df) == 2
    # The "Results written" message happens + info about the failed data
    caplog_messages = [_.message for _ in caplog.records]
    assert f"Results written to BigQuery, run id: {DUMMY_RUN_ID}" in caplog_messages
    assert any([_ for _ in caplog_messages if CAPLOG_DF_HEADER in _])
    assert any([_ for _ in caplog_messages if f"fail {DUMMY_RUN_ID}" in _])


def test_console_data_shown_for_matching_validation_with_result_written_to_bq_in_debug_mode(
    module_under_test, fs, caplog, monkeypatch
):
    # Mock the big query client
    mock_bq_client = mock.create_autospec(bigquery.Client)
    monkeypatch.setattr(bigquery, "Client", value=mock_bq_client)
    # With some mocked data - source and target the same
    data = _generate_fake_data(rows=10, second_range=0)
    source_json_data = _get_fake_json_data(data)
    target_json_data = _get_fake_json_data(data)
    _create_table_file(SOURCE_TABLE_FILE_PATH, source_json_data)
    _create_table_file(TARGET_TABLE_FILE_PATH, target_json_data)
    # ... and the log level being DEBUG
    caplog.set_level(logging.DEBUG)
    # When we validate
    client = module_under_test.DataValidation(SAMPLE_ROW_CONFIG_BQ_FAILURES)
    result_df = client.execute()
    # Then...
    # 0 failures returned
    assert len(result_df) == 0
    # The "No results" message happens + "Empty DataFrame" because there are no failures to display
    caplog_messages = [_.message for _ in caplog.records]
    assert "No results to write to BigQuery" in caplog_messages
    assert any([_ for _ in caplog_messages if _.startswith("Empty DataFrame")])
