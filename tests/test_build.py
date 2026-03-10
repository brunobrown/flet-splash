"""Tests for build.py web archive preservation."""

from __future__ import annotations

from pathlib import Path

from flet_splash.build import _restore_web_archive, _save_web_archive


class TestWebArchivePreservation:
    def test_save_returns_none_when_no_archive(self, tmp_path: Path) -> None:
        flutter_dir = tmp_path / "build" / "flutter"
        flutter_dir.mkdir(parents=True)
        assert _save_web_archive(flutter_dir) is None

    def test_save_reads_archive(self, tmp_path: Path) -> None:
        app_dir = tmp_path / "build" / "flutter" / "app"
        app_dir.mkdir(parents=True)
        app_zip = app_dir / "app.zip"
        app_zip.write_bytes(b"fake-zip-content")
        assert _save_web_archive(tmp_path / "build" / "flutter") == b"fake-zip-content"

    def test_restore_writes_to_both_locations(self, tmp_path: Path) -> None:
        flutter_dir = tmp_path / "build" / "flutter"
        (flutter_dir / "app").mkdir(parents=True)
        web_dir = tmp_path / "build" / "web" / "assets" / "app"
        web_dir.mkdir(parents=True)

        data = b"correct-archive-data"
        _restore_web_archive(data, flutter_dir, tmp_path)

        assert (flutter_dir / "app" / "app.zip").read_bytes() == data
        assert (web_dir / "app.zip").read_bytes() == data

    def test_restore_none_is_noop(self, tmp_path: Path) -> None:
        flutter_dir = tmp_path / "build" / "flutter"
        (flutter_dir / "app").mkdir(parents=True)
        _restore_web_archive(None, flutter_dir, tmp_path)
        assert not (flutter_dir / "app" / "app.zip").exists()

    def test_restore_skips_missing_directories(self, tmp_path: Path) -> None:
        flutter_dir = tmp_path / "build" / "flutter"
        (flutter_dir / "app").mkdir(parents=True)
        # web dir doesn't exist — should not raise
        _restore_web_archive(b"data", flutter_dir, tmp_path)
        assert (flutter_dir / "app" / "app.zip").read_bytes() == b"data"
