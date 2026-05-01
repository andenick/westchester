# Sidewalk-to-Parcel Matching: Quick Start
## Visual Workflow Guide for Taylor

**Goal:** Match each sidewalk to its nearest tax parcel
**Time:** 90 minutes (first time)
**Tools:** ArcGIS Pro native tools only

---

## WORKFLOW AT A GLANCE

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: LOAD DATA (5 min)                                  │
│  • Drag westchester_sidewalks.geojson into ArcGIS Pro       │
│  • Drag WCGIS.tax-parcels.geojson into ArcGIS Pro           │
│  • Verify both layers display correctly                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: GENERATE NEAR TABLE (10 min)                       │
│  • Analysis → Tools → "Generate Near Table"                 │
│  • Input: sidewalks | Near: parcels                         │
│  • Search Radius: 75 feet                                   │
│  • Location: ✓ | Closest: ✓                                 │
│  • Output: sidewalk_parcel_matches.dbf                      │
│  • Click RUN                                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: REVIEW RESULTS (5 min)                             │
│  • Open sidewalk_parcel_matches table                       │
│  • Check: IN_FID, NEAR_FID, NEAR_DIST columns               │
│  • Right-click NEAR_DIST → Statistics                       │
│  • Mean should be 15-50 feet (typical)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: JOIN BACK TO SIDEWALKS (10 min)                    │
│  • Right-click sidewalks layer → Add Join                   │
│  • Join Field: OBJECTID                                     │
│  • Join Table: sidewalk_parcel_matches                      │
│  • Join Table Field: IN_FID                                 │
│  • Keep all features: ✓                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: EXPORT RESULTS (5 min)                             │
│  • Right-click sidewalks layer → Export Features            │
│  • Output: sidewalks_with_parcels.geojson                   │
│  • Click OK                                                  │
│  • DONE! ✓                                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## KEY PARAMETERS EXPLAINED

### SEARCH RADIUS: How far to look for parcels?

```
25 feet  → Tight match (urban, narrow streets)
50 feet  → Moderate match (typical suburban)
75 feet  → Recommended START (Westchester mix)
100 feet → Broad match (wide streets, large lots)
150 feet → Maximum useful (rural areas)
```

**RECOMMENDATION FOR WESTCHESTER: Start with 75 feet**

### OUTPUT FIELDS EXPLAINED

```
┌─────────────┬────────────────────────────────────────────┐
│ IN_FID      │ Your sidewalk ID (0, 1, 2, 3...)          │
├─────────────┼────────────────────────────────────────────┤
│ NEAR_FID    │ Matched parcel ID (45231, 45232...)       │
├─────────────┼────────────────────────────────────────────┤
│ NEAR_DIST   │ Distance in feet (15.7, 23.4...)          │
├─────────────┼────────────────────────────────────────────┤
│ NEAR_X      │ X coordinate of nearest point             │
├─────────────┼────────────────────────────────────────────┤
│ NEAR_Y      │ Y coordinate of nearest point             │
└─────────────┴────────────────────────────────────────────┘
```

---

## VALIDATION CHECKLIST

After running the workflow, complete these checks:

### ☐ CHECK 1: Distance Statistics (5 min)

1. Open `sidewalk_parcel_matches` table
2. Right-click `NEAR_DIST` → Statistics
3. Review:
   - **Mean:** Should be 20-50 feet ✓
   - **Min:** Should be close to 0 ✓
   - **Max:** Should be ≤ search radius ✓

**If mean > 75 feet:** Sidewalks far from parcels, verify data accuracy

### ☐ CHECK 2: Visual Spot Checks (15 min)

1. Zoom to 10 random locations
2. Select a sidewalk segment
3. Check its `NEAR_FID` value
4. Select that parcel
5. Verify: Does this match make sense? ✓

**Do this for urban, suburban, and rural areas**

### ☐ CHECK 3: Match Rate (5 min)

Count features:
- Sidewalks WITH matches (NEAR_FID ≠ NULL)
- Sidewalks WITHOUT matches (NEAR_FID = NULL)
- Calculate: Match Rate = (Matched / Total) × 100%

**Expected match rates:**
- Urban: 90-98% ✓
- Suburban: 85-95% ✓
- Rural: 70-85% ✓

**If < 70%:** Increase search radius and re-run

---

## TROUBLESHOOTING QUICK REFERENCE

### ❌ PROBLEM: Tool failed to execute

**SOLUTION:**
1. Check coordinate systems match
2. Run "Repair Geometry" on both layers
3. Close all attribute tables, restart ArcGIS Pro

### ❌ PROBLEM: No features matched (0 results)

**SOLUTION:**
1. Increase search radius to 200 feet (testing)
2. Verify layers overlap (Zoom to extent)
3. Check coordinate systems compatible

### ❌ PROBLEM: Results look wrong

**SOLUTION:**
1. Do visual spot checks (10 locations)
2. Check NEAR_DIST statistics (should be reasonable)
3. Recalculate with different search radius

### ❌ PROBLEM: Processing takes forever

**SOLUTION:**
1. Project to State Plane coordinate system (faster than lat/lon)
2. Process smaller areas using Select by Location
3. Simplify sidewalk geometry to reduce vertices

---

## SETTINGS CHEAT SHEET

### FOR WESTCHESTER COUNTY SPECIFICALLY:

```yaml
INPUT DATA:
  Sidewalks: westchester_sidewalks.geojson
  Parcels: WCGIS.tax-parcels.geojson
  Coordinate System: EPSG:4326 (will auto-convert)

GENERATE NEAR TABLE SETTINGS:
  Input Features: westchester_sidewalks
  Near Features: WCGIS.tax-parcels
  Search Radius: 75 Feet
  Location: ✓ (checked)
  Angle: ☐ (unchecked)
  Closest: ✓ (checked)
  Output: sidewalk_parcel_matches.dbf

EXPECTED RESULTS:
  Mean Distance: 25-45 feet
  Match Rate: 88-94%
  Processing Time: 2-8 minutes
  Output Records: ~Same as sidewalk count
```

---

## ALTERNATIVE: SPATIAL JOIN METHOD

If Generate Near Table doesn't work for you, use Spatial Join:

```
STEP 1: Buffer sidewalks (50 feet)
   ↓
STEP 2: Spatial Join buffers to parcels (INTERSECT)
   ↓
STEP 3: Export results
   ↓
DONE!
```

**When to use Spatial Join instead:**
- Need intersection-based matching (not distance)
- Want to identify parcels completely without sidewalks
- Generate Near Table has performance issues

See full guide for detailed Spatial Join instructions.

---

## AFTER MATCHING: WHAT'S NEXT?

Once you have sidewalk-to-parcel matches, you can:

### ANALYSIS OPTIONS:

1. **Property Value Correlation**
   - Join parcel assessed values
   - Analyze relationship between sidewalks and property values

2. **Gap Analysis**
   - Identify parcels without nearby sidewalks
   - Prioritize by density, schools, transit

3. **Maintenance Planning**
   - Assign responsibility by parcel ownership
   - Create maintenance zones

4. **Cost Estimation**
   - Calculate linear feet needed per parcel
   - Estimate construction costs by area

5. **Accessibility Mapping**
   - Calculate access to schools, parks, transit
   - Support ADA compliance

---

## FILE LOCATIONS

### YOUR DATA:
```
D:\Arcanum\Projects\Westchester\
├── Technical\data\raw\infrastructure\
│   ├── westchester_sidewalks.geojson ← Load this
│   └── westchester_sidewalks_comprehensive.geojson
└── Output\Taylor Deliverables 2025.10.28\
    └── GEOSPATIAL_DATA\boundaries\
        └── WCGIS.tax-parcels.geojson ← Load this
```

### DOCUMENTATION:
```
D:\Arcanum\Projects\Westchester\Technical\docs\
├── ARCGIS_PRO_SIDEWALK_TO_PARCEL_GUIDE.md ← Full guide (15 pages)
└── SIDEWALK_PARCEL_MATCHING_QUICK_START.md ← This document
```

---

## KEYBOARD SHORTCUTS (ARCGIS PRO)

```
Ctrl + F     → Open Search (find tools)
Ctrl + N     → New project
Ctrl + O     → Open project
Ctrl + S     → Save project
F2           → Zoom to full extent
F9           → Open attribute table
Ctrl + ↑/↓   → Cycle through layers
Space        → Pan tool
Z            → Zoom tool
C            → Zoom to previous extent
```

---

## TIME ESTIMATES BY EXPERIENCE LEVEL

### FIRST TIME (LEARNING):
- Reading guide: 15 min
- Loading data: 5 min
- Running tool: 10 min
- Reviewing results: 10 min
- Validation: 20 min
- Export: 5 min
- Spot checks: 15 min
**TOTAL: ~90 minutes**

### SECOND TIME (FAMILIAR):
- Loading data: 3 min
- Running tool: 5 min
- Quick validation: 5 min
- Export: 3 min
**TOTAL: ~15 minutes**

### AUTOMATED (MODEL BUILDER):
- Run model: 2 min
- Review results: 5 min
**TOTAL: ~7 minutes**

---

## NEXT STEPS

1. ✓ Read this quick start guide
2. ☐ Open full guide: `ARCGIS_PRO_SIDEWALK_TO_PARCEL_GUIDE.md`
3. ☐ Load your data in ArcGIS Pro
4. ☐ Run Generate Near Table with 75-foot radius
5. ☐ Complete validation checklist
6. ☐ Export final results
7. ☐ Document your settings/decisions
8. ☐ Begin analysis (property values, gaps, etc.)

---

## SUPPORT

**Questions about this workflow:**
- Full Guide: `ARCGIS_PRO_SIDEWALK_TO_PARCEL_GUIDE.md`
- Data Catalog: `TAYLOR_DATA_CATALOG.md`
- Email: support@arcanumpm.com

**ArcGIS Pro technical support:**
- Esri Support: https://support.esri.com
- Community: https://community.esri.com

**Westchester County GIS:**
- Email: gis@westchestergov.com
- Phone: (914) 995-4700
- Portal: https://gis.westchestergov.com

---

## VISUAL REFERENCE: ARCGIS PRO INTERFACE

```
┌─────────────────────────────────────────────────────────────┐
│ [File] [Map] [Insert] [ANALYSIS] [View] [Edit] [Imagery]   │ ← Top ribbon
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌────────────────────────────────────┐  │
│  │ CONTENTS     │  │                                     │  │
│  │              │  │                                     │  │
│  │ ☐ Sidewalks  │  │          MAP VIEW                  │  │
│  │ ☐ Parcels    │  │                                     │  │
│  │              │  │                                     │  │
│  │              │  │                                     │  │
│  └──────────────┘  └────────────────────────────────────┘  │
│   ↑ Layers            ↑ Your map                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**To open Generate Near Table:**
1. Click **ANALYSIS** tab
2. Click **Tools** button
3. Search: "Generate Near Table"
4. Double-click the tool to open

---

## VERSION INFO

| Version | Date | Updates |
|---------|------|---------|
| 1.0 | 2025-11-07 | Initial quick start guide |

---

**Ready to start? Open the full guide and follow Step 1!**

Full Guide: `D:\Arcanum\Projects\Westchester\Technical\docs\ARCGIS_PRO_SIDEWALK_TO_PARCEL_GUIDE.md`
