from tools.file_op import create_data_path, os

create_data_path("", data_path="logs")
create_data_path("", data_path="data")

pairs_metadata_path = os.path.join("pairs", "pairs_meta_data.json")
