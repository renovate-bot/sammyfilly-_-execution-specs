from __future__ import annotations

import json
import os
from importlib import import_module
from typing import Any, Dict, List

from ethereum.base_types import U256, Uint
from ethereum.utils.hexadecimal import (
    hex_to_bytes,
    hex_to_bytes8,
    hex_to_bytes32,
    hex_to_hash,
    hex_to_u256,
    hex_to_uint,
)


class DifficultyTestLoader:
    """
    This class has all the methods and imports required to run
    the difficulty tests
    """

    def __init__(self, network: str, fork_name: str):
        self.network = network
        self.fork_name = fork_name
        self.test_dir = f"tests/fixtures/DifficultyTests/df{fork_name}"
        try:
            self.test_files = list(os.listdir(self.test_dir))
        except:
            self.test_files = []

        self.fork = self._module("fork")
        self.calculate_block_difficulty = self.fork.calculate_block_difficulty

    def _module(self, name: str) -> Any:
        return import_module(f"ethereum.{self.fork_name}.{name}")

    def load_test(self, test_file: str) -> List[Dict]:
        test_name = os.path.splitext(test_file)[0]
        path = os.path.join(self.test_dir, test_file)

        with open(path, "r") as fp:
            json_data = json.load(fp)[test_name][self.network]

        test_list = []
        for test_name in json_data:
            has_ommers = json_data[test_name]["parentUncles"]

            parent_has_ommers = has_ommers != "0x00"

            test = {
                "name": test_name,
                "inputs": {
                    "block_number": hex_to_uint(
                        json_data[test_name]["currentBlockNumber"]
                    ),
                    "block_timestamp": hex_to_u256(
                        json_data[test_name]["currentTimestamp"]
                    ),
                    "parent_timestamp": hex_to_u256(
                        json_data[test_name]["parentTimestamp"]
                    ),
                    "parent_difficulty": hex_to_uint(
                        json_data[test_name]["parentDifficulty"]
                    ),
                    "parent_has_ommers": parent_has_ommers,
                },
                "expected": hex_to_uint(
                    json_data[test_name]["currentDifficulty"]
                ),
            }
            test_list.append(test)

        return test_list
