# flexai/executor/scripts/boolean_subtract_v2.py

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy


SUPPORTED_IMPORTS = {".stl", ".obj"}


def blender_script_args() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1 :]
    return []


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_mesh(path: Path, name: str) -> bpy.types.Object:
    extension = path.suffix.lower()
    if extension == ".stl":
        bpy.ops.wm.stl_import(filepath=str(path))
    elif extension == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    else:
        supported = ", ".join(sorted(SUPPORTED_IMPORTS))
        raise ValueError(f"Unsupported Blender import type '{extension}'. Supported: {supported}")

    selected = list(bpy.context.selected_objects)
    if not selected:
        raise RuntimeError(f"Import produced no selectable object: {path}")

    obj = selected[0]
    obj.name = name
    bpy.context.view_layer.objects.active = obj
    return obj


def boolean_difference(target: bpy.types.Object, cutter: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    modifier = target.modifiers.new(name="FlexAI Boolean Difference", type="BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.object = cutter
    modifier.solver = "EXACT"
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def export_stl(obj: bpy.types.Object, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=str(output_path), export_selected_objects=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Blender boolean difference operation.")
    parser.add_argument("--target", required=True, help="Input target STL/OBJ path")
    parser.add_argument("--cutter", required=True, help="Input cutter STL/OBJ path")
    parser.add_argument("--output", required=True, help="Output STL path")
    args = parser.parse_args(blender_script_args())

    target_path = Path(args.target).expanduser().resolve()
    cutter_path = Path(args.cutter).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    clear_scene()
    target = import_mesh(target_path, "FlexAI_Target")
    cutter = import_mesh(cutter_path, "FlexAI_Cutter")
    boolean_difference(target, cutter)
    bpy.data.objects.remove(cutter, do_unlink=True)
    export_stl(target, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
