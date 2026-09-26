# Triggerbox – notes for Claude

This repository holds Dale's reference material for Unreal Engine work. Read this file first in every session.

## About Dale and how to work

- Dale uses **Unreal Engine 5.8**.
- **Prefer Blueprint solutions** for anything that can be done in Blueprints. Only suggest C++ when Blueprints genuinely can't do it, and say why.
- **Documents Dale asks for are delivered in Word format (.docx).** Save them using Dale's NAS folder structure. If the correct NAS folder isn't known, ask Dale for the path rather than guessing.

## Reference documentation

| Asset | Readable copy (use this) | Original |
|---|---|---|
| Ultra Modular Landscape (UML) | [`docs/uml/UML-Technical-Guide.md`](docs/uml/UML-Technical-Guide.md) | `Ultra Modular Landscape Documentation.docx` |

- For UML questions, search or read `docs/uml/UML-Technical-Guide.md` before answering. Screenshots are in `docs/uml/images/`.
- The `.docx` is the source of truth. The Markdown copy was generated from it and shouldn't be edited by hand.

### Version caveat: guide targets UE 5.6, Dale uses 5.8

The UML guide is written for **UE 5.6**. Menus, parameters and especially the **Known Bugs** section (for example the Nanite 64-component limit, and RVT output disabling material contact shadows in 5.7) may behave differently or already be fixed in 5.8. When an answer relies on version-specific behaviour or a bug workaround, say so and suggest Dale verify it in 5.8.

### UML quick facts

- **Three parts:** layered landscape material (`M_UML_Master`, layer asset `ML_UML_Layer`), Blueprint Prefab Mountains (`BP_UML_Prefab`), and EasyPCG.
- **Required plugins:** Landscape Patch (Prefab Mountains) and Procedural Content Generation Framework (EasyPCG).
- **Layer naming convention:** landscape paint layers must be named `Layer_1` … `Layer_13` for erosion maps and layer-based spawning to work with other materials. `Layer_1` is Epic's hard-coded "Background" layer.
- **Layer Info files:** Non Weight-blended is recommended.

## Adding more documentation

1. Upload the `.docx` to the repo.
2. Convert it with `python3 tools/docx_to_md.py "<file>.docx" docs/<name>/<Name>.md`. Images go into `docs/<name>/images/`.
3. Add a row to the **Reference documentation** table above.
