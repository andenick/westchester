---
description: "Run Druck standards validation on this project"
tools: [bash]
---

# Validation Suite

Run complete Druck compliance validation:

1. **Excel Validation**:
   ```bash
   python Technical/scripts/validate_excel.py
   ```
   - Verify ONE SHEET per file rule
   - Check machine-readable columns
   - Validate B&W formatting

2. **Output Validation**:
   ```bash
   python Technical/scripts/validate_outputs.py
   ```
   - Check LaTeX PDFs exist in Output/PDFs/
   - Verify Excel files in Output/Data/
   - Validate directory structure compliance

3. **Frontend Tests**:
   ```bash
   cd Technical/src/frontend
   npm run lint
   npm run build
   ```

4. **Backend Tests**:
   ```bash
   cd Technical
   python -m pytest tests/
   ```

5. **Fresh Environment Test**:
   - Follow procedure in `Technical/docs/TESTING_PROTOCOL.md`
   - Document results in HANDOFF_DOCUMENTATION.md

Report any violations found and provide remediation steps.

