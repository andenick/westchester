# Inputs Folder - User-Provided Original Files

**Created**: October 16, 2025
**Purpose**: Untouched reference baseline of all input files
**Status**: Read-only originals - NEVER modify files in this folder
**Compliance**: MANDATORY per Druck standards (Arcanum workspace requirement)

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

## Folder Structure

```
Inputs/
├── PDFs/         - Original PDF documents
├── Excel/        - Excel/spreadsheet files (.xlsx, .xls)
├── Documents/    - Text files, Word docs, README files
├── Images/       - PNG, JPG, diagrams, screenshots
└── Data/         - CSV, JSON, and other data files
```

**Design**: Standard 5-folder structure following Druck specifications.

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
- Don't reorganize structure (keep organized by type)

### Processing Workflow
1. **Copy** file from `Inputs/` to appropriate work directory
2. **Work** on the copy (Technical/, Output/, etc.)
3. **Save** results to `Output/` or appropriate deliverables folder
4. **Never** overwrite originals in Inputs/

---

## Maintenance

**File Integrity**: All files in Inputs/ should remain byte-for-byte identical to originals provided.

**Adding New Inputs**: When new input files are provided:
1. Determine file type (PDF, Excel, Document, Image, Data)
2. Place in appropriate subfolder
3. Update this README with file inventory if desired
4. Maintain organization and clarity

**Verification**: Inputs/ serves as the authoritative source for all original materials.

---

## Related Documentation

- **Westchester README.md** - Project overview and documentation
- **Druck Standards** - ` for workspace requirements

---

**This folder contains original input materials for Westchester. Treat these files as authoritative originals and preserve their integrity.**

*Organized following Druck standards - Arcanum workspace best practices*
*Last Updated: October 16, 2025*
