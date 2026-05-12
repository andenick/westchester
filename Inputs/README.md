# Inputs Folder - User-Provided Original Files

**Created**: October 16, 2025
**Updated**: November 3, 2025
**Purpose**: Untouched reference baseline of all input files
**Status**: Read-only originals - NEVER modify files in this folder
**Compliance**: MANDATORY per Druck standards (Arcanum workspace requirement)
**Structure**: FLAT structure (updated October 29, 2025)

---

## Folder Philosophy

This `Inputs/` folder follows the **Druck standard** (Arcanum workspace best practice) by maintaining clean separation:

- **Inputs/** = Original files (this folder) - untouched, read-only
- **Technical/** = Processing, scripts, intermediate work - where AI agents work
- **Output/** = Final deliverables, reports, validated results

**Why This Matters**:
1. **Troubleshooting**: If processing goes wrong, clean originals exist here
2. **Provenance**: Clear record of what was provided vs what was generated
3. **Reproducibility**: Anyone can start from these originals and reproduce the work
4. **Druck Compliance**: MANDATORY per Arcanum workspace standards

---

## Folder Structure (UPDATED - Flat Structure)

```
Inputs/
├── README.md                           # This file
├── Westchester_[Category]_[filename]   # All files directly in root
└── [No subdirectories allowed]         # NEW: Flat structure only
```

**NEW REQUIREMENTS (October 29, 2025)**:
- **Flat structure only** - NO subdirectories allowed
- **Smart filename encoding** - Context preserved in filename
- **Automatic version control** - Sequential versions tracked

**Design**: Flat structure following updated Druck specifications.

---

## Current File Inventory

**Geographic Shapefiles** (County Data):
- `Westchester_CountyShapefiles_Roadways_Line_*` - County roadways (line format)
- `Westchester_CountyShapefiles_Roadways_Polygon_*` - County roadways (polygon format)
- `Westchester_CountyShapefiles_Sidewalks_Polygon_*` - County sidewalks (polygon format)

**File Types**:
- `.shp` - Shapefile geometry
- `.dbf` - Attribute data
- `.shx` - Shape index
- `.prj` - Coordinate system
- `.cpg` - Code page
- `.xml` - Metadata

---

## Usage Guidelines

### DO ✅
- Read files for analysis and processing
- Copy files to Technical/ or other work directories for processing
- Reference file paths in documentation
- Use as validation baseline

### DON'T ❌
- **NEVER modify files in this folder**
- Don't move files out (copy instead)
- Don't create new files here (this is inputs only)
- Don't create subdirectories (flat structure only)

### Processing Workflow
1. **Copy** file from `Inputs/` to appropriate work directory
2. **Work** on the copy (Technical/, Output/, etc.)
3. **Save** results to `Output/` or appropriate deliverables folder
4. **Never** overwrite originals in Inputs/

---

## Smart Filename Encoding

**Pattern**: `[ProjectName]_[Category]_[OriginalPath]_[OriginalFilename].[ext]`

**Examples**:
- `Westchester_CountyShapefiles_Roadways_Line_countyroads_line.shp`
- `Westchester_CountyShapefiles_Sidewalks_Polygon_countysidewalks_polygon.dbf`

**Benefits**:
- **Context Preservation**: Original path and filename maintained
- **Easy Sorting**: Files group by project and category
- **No Ambiguity**: Clear provenance for each file
- **Flat Structure Compatible**: No subdirectories needed

---

## Maintenance

**File Integrity**: All files in Inputs/ should remain byte-for-byte identical to originals provided.

**Adding New Inputs**: When new input files are provided:
1. Apply smart filename encoding: `[ProjectName]_[Category]_[OriginalPath]_[OriginalFilename].[ext]`
2. Place directly in Inputs/ root (NO subdirectories)
3. Update this README with file inventory if desired
4. Maintain organization and clarity

**Version Control**: The workspace automatically tracks sequential versions of all files in Inputs/.

**Verification**: Inputs/ serves as the authoritative source for all original materials.

---

## Related Documentation

- **Westchester README.md** - Project overview and documentation
- **Druck Standards** - ` for workspace requirements

---

**This folder contains original input materials for Westchester. Treat these files as authoritative originals and preserve their integrity.**

*Organized following updated Druck standards - Arcanum workspace best practices*
*Last Updated: November 3, 2025 - Migrated to flat structure*