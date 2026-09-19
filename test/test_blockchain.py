"""Test blockchain audit trail."""
import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def isolated_chain(tmp_path, monkeypatch):
    """Isolate chain ke temporary file."""
    from server.core import blockchain
    monkeypatch.setattr(blockchain, "CHAIN_PATH", tmp_path / "chain.jsonl")
    return blockchain


class TestBlockchain:
    def test_genesis_creation(self, isolated_chain):
        bc = isolated_chain
        bc.init_chain()
        info = bc.get_blockchain_info()
        assert info["length"] == 1
        assert info["initialized"] is True

    def test_append_block(self, isolated_chain):
        bc = isolated_chain
        bc.init_chain()
        block = bc.append_block({"tanggal": "2026-01-01", "wt": -10})
        assert block["index"] == 1
        assert block["block_hash"].startswith("0" * bc.DIFFICULTY)

    def test_chain_valid(self, isolated_chain):
        bc = isolated_chain
        bc.init_chain()
        for i in range(3):
            bc.append_block({"n": i})
        result = bc.verify_chain()
        assert result["valid"] is True
        assert result["length"] == 4  # genesis + 3

    def test_tamper_detection(self, isolated_chain, tmp_path):
        """Modifikasi data harus bikin chain invalid."""
        bc = isolated_chain
        bc.init_chain()
        bc.append_block({"wt": -10})
        bc.append_block({"wt": -15})

        # Tamper — baca, modifikasi, tulis ulang
        lines = bc.CHAIN_PATH.read_text().strip().split("\n")
        block1 = json.loads(lines[1])
        block1["data"]["wt"] = -999  # manipulasi
        lines[1] = json.dumps(block1)
        bc.CHAIN_PATH.write_text("\n".join(lines) + "\n")

        # Verify harus invalid
        result = bc.verify_chain()
        assert result["valid"] is False