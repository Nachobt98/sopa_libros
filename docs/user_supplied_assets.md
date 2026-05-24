# User-supplied assets workflow

SopaLibros should support images chosen by the user as the primary asset workflow.

The renderer should keep consuming `asset_manifest.json`; the manifest can be built from local user images instead of generated images.

## CLI workflow

Normalize a folder of reviewed images into the same manifest contract used by generated assets:

```powershell
sopa-libros-assets `
  --title "Ancient Egypt Word Search" `
  --input wordlists/book_block.txt `
  --user-assets-dir assets/user/egypt `
  --output assets/generated/egypt-user `
  --style reviewed-user-assets
```

Then pass the manifest to the thematic renderer:

```powershell
sopa-libros-thematic `
  --title "Ancient Egypt Word Search" `
  --input wordlists/book_block.txt `
  --theme-manifest assets/generated/egypt-user/asset_manifest.json
```

The asset command writes:

- `asset_manifest.json`: renderer-facing image references.
- `user_asset_sources.json`: traceability map from each normalized PNG back to the user's source image.
- `processed/*.png`: normalized page-size PNGs.

## Filename conventions

The user asset folder can contain `.png`, `.jpg`, `.jpeg`, or `.webp` files.

Book fallback background:

- `default_background.*`
- `book_default_background.*`
- `background.*`

Block background for a thematic block named `Ancient Egypt`:

- `block_01_ancient_egypt_background.*`
- `ancient_egypt_background.*`
- `ancient_egypt_bg.*`

Block cover background:

- `block_01_ancient_egypt_cover.*`
- `block_01_ancient_egypt_cover_background.*`
- `ancient_egypt_cover.*`
- `ancient_egypt_cover_background.*`

Missing block-specific images are warnings. The renderer can still fall back to the book default background when present.
