"""Tests for the data module."""

from collections import OrderedDict
import csv
import os
import tempfile
import uuid

import pandas as pd
import psycopg2
import pytest

import dallinger
from dallinger.config import get_config
from dallinger.utils import generate_random_id


class TestData(object):

    data_path = os.path.join(
        "tests",
        "datasets",
        "12eee6c6-f37f-4963-b684-da585acd77f1-data.zip"
    )

    config = get_config()

    def test_connection_to_s3(self):
        conn = dallinger.data._s3_connection()
        assert conn

    def test_user_s3_bucket_first_time(self):
        conn = dallinger.data._s3_connection()
        bucket = dallinger.data.user_s3_bucket(
            canonical_user_id=generate_random_id(),
        )
        assert bucket
        conn.delete_bucket(bucket)

    def test_user_s3_bucket_thrice(self):
        conn = dallinger.data._s3_connection()
        id = generate_random_id()
        for i in range(3):
            bucket = dallinger.data.user_s3_bucket(
                canonical_user_id=id,
            )
            assert bucket
        conn.delete_bucket(bucket)

    def test_user_s3_bucket_no_id_provided(self):
        bucket = dallinger.data.user_s3_bucket()
        assert bucket

    def test_dataset_creation(self):
        """Load a dataset."""
        dallinger.data.Data(self.data_path)

    def test_conversions(self):
        data = dallinger.data.Data(self.data_path)
        assert data.networks.csv
        assert data.networks.dict
        assert data.networks.df.shape
        assert data.networks.html
        assert data.networks.latex
        assert data.networks.list
        assert data.networks.ods
        assert data.networks.tsv
        assert data.networks.xls
        assert data.networks.xlsx
        assert data.networks.yaml

    def test_dataframe_conversion(self):
        data = dallinger.data.Data(self.data_path)
        assert data.networks.df.shape == (1, 13)

    def test_csv_conversion(self):
        data = dallinger.data.Data(self.data_path)
        assert data.networks.csv[0:3] == "id,"

    def test_tsv_conversion(self):
        data = dallinger.data.Data(self.data_path)
        assert data.networks.tsv[0:3] == "id\t"

    def test_list_conversion(self):
        data = dallinger.data.Data(self.data_path)
        assert type(data.networks.list) is list

    def test_dict_conversion(self):
        data = dallinger.data.Data(self.data_path)
        assert type(data.networks.dict) is OrderedDict

    def test_df_conversion(self):
        data = dallinger.data.Data(self.data_path)
        assert type(data.networks.df) is pd.DataFrame

    def test_data_loading(self):
        data = dallinger.data.load("3b9c2aeb-0eb7-4432-803e-bc437e17b3bb")
        assert data
        assert data.networks.csv

    def test_export_of_nonexistent_database(self):
        nonexistent_local_db = str(uuid.uuid4())
        with pytest.raises(psycopg2.OperationalError):
            dallinger.data.copy_local_to_csv(nonexistent_local_db, "")

    def test_export_of_dallinger_database(self):
        export_dir = tempfile.mkdtemp()
        dallinger.data.copy_local_to_csv("dallinger", export_dir)
        assert os.path.isfile(os.path.join(export_dir, "network.csv"))

    def test_exported_database_includes_headers(self):
        export_dir = tempfile.mkdtemp()
        dallinger.data.copy_local_to_csv("dallinger", export_dir)
        network_table_path = os.path.join(export_dir, "network.csv")
        assert os.path.isfile(network_table_path)
        with open(network_table_path, 'rb') as f:
            reader = csv.reader(f, delimiter=',')
            header = next(reader)
            assert "creation_time" in header

    def test_scrub_pii(self):
        path_to_data = os.path.join("tests", "datasets", "pii")
        dallinger.data._scrub_participant_table(path_to_data)
        with open(os.path.join(path_to_data, "participant.csv"), 'rb') as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)  # Skip the header
            for row in reader:
                assert "PII" not in row
