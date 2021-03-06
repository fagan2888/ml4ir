import os
import tensorflow as tf

from ml4ir.base.features.feature_config import FeatureConfig
from ml4ir.base.data import tfrecord_reader, tfrecord_writer
from ml4ir.base.io.file_io import FileIO

from typing import List

# Constants
TFRECORD_FILE = "file_0.tfrecord"


def read(
    data_dir: str,
    feature_config: FeatureConfig,
    tfrecord_type: str,
    tfrecord_dir: str,
    file_io: FileIO,
    batch_size: int = 128,
    preprocessing_keys_to_fns: dict = {},
    use_part_files: bool = False,
    max_sequence_size: int = 25,
    parse_tfrecord: bool = True,
    logger=None,
    **kwargs
) -> tf.data.TFRecordDataset:
    """
    - reads csv-formatted data from an input directory
    - selects relevant features
    - creates Dataset X and y

    Current execution plan:
        1. Load CSVs as pandas dataframes
        2. Convert each query into tf.train.SequenceExample protobufs
        3. Write the protobufs into a .tfrecord file
        4. Load .tfrecord file into a TFRecordDataset and parse the protobufs

    Args:
        - data_dir: Path to directory containing csv files to read
        - feature_config: ml4ir.config.features.FeatureConfig object extracted from the feature config
        - tfrecord_dir: Path to directory where the serialized .tfrecord files will be stored
        - batch_size: int value specifying the size of the batch
        - use_part_files: bool value specifying whether to look for part files
        - max_sequence_size: int value specifying max number of records per query
        - logger: logging object

    Returns:
        tensorflow TFRecordDataset
    """
    csv_files: List[str] = file_io.get_files_in_directory(
        data_dir,
        extension="" if use_part_files else ".csv",
        prefix="part-" if use_part_files else "",
    )

    # Create a directory for storing tfrecord files
    file_io.make_directory(tfrecord_dir, clear_dir=True)

    # Write tfrecord files
    tfrecord_writer.write_from_files(
        csv_files=csv_files,
        tfrecord_file=os.path.join(tfrecord_dir, TFRECORD_FILE),
        feature_config=feature_config,
        tfrecord_type=tfrecord_type,
        file_io=file_io,
        logger=logger,
    )

    dataset = tfrecord_reader.read(
        data_dir=tfrecord_dir,
        feature_config=feature_config,
        tfrecord_type=tfrecord_type,
        max_sequence_size=max_sequence_size,
        batch_size=batch_size,
        preprocessing_keys_to_fns=preprocessing_keys_to_fns,
        parse_tfrecord=parse_tfrecord,
        file_io=file_io,
        logger=logger,
    )

    return dataset
