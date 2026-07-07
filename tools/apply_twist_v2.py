# tools/apply_twist_v2.py

from __future__ import annotations

import argparse

from app import twist_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compatibility wrapper for the primary FlexAI Twist CLI workflow."
    )
    parser.add_argument("input", help="Input STL, OBJ, or 3MF path")
    parser.add_argument("output", help="Output STL path")
    parser.add_argument("--blender", default=None, help="Optional explicit Blender executable path")
    parser.add_argument("--keep-cutter", action="store_true", help="Keep generated cutter STL beside output")
    parser.add_argument("--report", default=None, help="Optional path to write the JSON operation report")
    parser.add_argument("--artifacts-dir", default=None, help="Optional directory for default Twist artifacts")
    parser.add_argument(
        "--strict-recommendation",
        action="store_true",
        help="Fail if the planner does not recommend Twist for this model",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return twist_command(
        input_path=args.input,
        output_path=args.output,
        blender_path=args.blender,
        keep_cutter=args.keep_cutter,
        strict_recommendation=args.strict_recommendation,
        report_path=args.report,
        artifacts_dir=args.artifacts_dir,
    )


if __name__ == "__main__":
    raise SystemExit(main())
