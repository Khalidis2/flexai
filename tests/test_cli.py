# tests/test_cli.py

from __future__ import annotations

from flexai.cli import build_parser


def test_cli_parses_analyze_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["analyze", "model.stl"])

    assert args.command == "analyze"
    assert args.path == "model.stl"


def test_cli_parses_apply_twist_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["apply-twist", "input.stl", "output.stl", "--keep-cutter"])

    assert args.command == "apply-twist"
    assert args.input == "input.stl"
    assert args.output == "output.stl"
    assert args.keep_cutter is True
    assert args.blender is None


def test_cli_parses_explicit_blender_path() -> None:
    parser = build_parser()
    args = parser.parse_args([
        "apply-twist",
        "input.stl",
        "output.stl",
        "--blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
    ])

    assert args.command == "apply-twist"
    assert args.blender == "/Applications/Blender.app/Contents/MacOS/Blender"
