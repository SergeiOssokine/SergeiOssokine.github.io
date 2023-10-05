import argparse
import hashlib
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

import pandasdmx as sdmx
from rich.logging import RichHandler
from rich.traceback import install

logger = logging.getLogger(__name__)
logger.addHandler(RichHandler(rich_tracebacks=True, markup=True))
logger.setLevel("INFO")
# Setup rich to get nice tracebacks
install()


def md5(fname: str) -> str:
    """Get the md5sum of a given file. Chunks to 4096 bytes to avoid problems
    with files that don't fit in RAM.
    See
    https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file


    Args:
        fname (str): The name of the file

    Returns:
        str: The hex hash
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_internal_metadata(dset: str, config: Dict[str, Any], fname: str,data_dir:str) -> None:
    """Create a simple metadata file that stores a few key things about
    the downloaded dataset.

    Args:
        dset (str): The name of the dataset
        config (Dict[str,Any]): The config option dict
        file (str): The file with the downloaded dataset
        datadir (str): Folder where data is to be saved
    """
    md5sum = md5(fname)
    meta = dict(
        dataset_code=dset,
        opts=config[dset],
        timestamp=str(datetime.now()),
        md5sum=md5sum,
    )
    output = os.path.join(data_dir,f"{dset}_meta_creation.json")
    with open(output, "w") as fw:
        json.dump(meta, fw, indent=4)


def create_metadata(dset: str, metadata: Any,data_dir:str) -> None:
    """Store a subset of the official dataset metadata.

    Args:
        dset (str): Name of the dataset
        metadata (sdmx.StructureMessage): The metadata structure
        data_dir(str): Folder where data is to be saved
    """
    res = metadata.to_pandas()
    mt = dict()
    mt.update(header={k: str(v) for k, v in metadata.header.dict().items()})
    for key, it in res["codelist"].items():
        mt[key] = it.to_json()
    output = os.path.join(data_dir,f"{dset}_metadata.json")
    with open(output, "w") as fw:
        json.dump(mt, fw, indent=4)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "--config-file",
        type=str,
        help="json file containing dataset code and any options",
    )
    p.add_argument("--data-dir",type=str,help="The folder in which to save the data",default="./")
    args = p.parse_args()
    try:
        with open(args.config_file, "r") as fp:
            config = json.load(fp)
    except OSError:
        logger.error(f"Couldn't find the config file, {args.config}")
        sys.exit(-1)

    for dset, opts in config.items():
        estat = sdmx.Request("ESTAT")

        logger.info(f"Downloading {dset} with the following options: {opts}")
        resp = estat.data(dset, key=opts)
        logger.info("Done")

        logger.info(f"Downloading the metadata for {dset}")
        metadata = estat.datastructure(dset)
        logger.info("Done")

        df = sdmx.to_pandas(resp)
        df = df.reset_index()
        fname = f"{dset}.json"
        logger.info(f"Writing the data file to {fname}")
        df.to_json(os.path.join(args.data_dir,fname), index=False, indent=4)
        logger.info(f"Writing the data set metadata to {dset}_metadata.json")
        create_metadata(dset, metadata,args.data_dir)
        logger.info(f"Writing the internal meta to {dset}_meta_creation.json")
        create_internal_metadata(dset, config, fname,args.data_dir)
