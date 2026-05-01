# ArcGIS Pro: Sidewalk to Parcel Matching Guide
## Simple, Native Tools - Zero Python Required

**Prepared for:** Taylor
**Project:** Westchester County Sidewalk-to-Parcel Analysis
**Date:** November 7, 2025
**Author:** Arcanum Performance Monitoring

---

## QUICK START

**Goal:** Match each sidewalk segment to the nearest tax parcel
**Time Required:** 1-2 hours (one-time setup)
**Tools Used:** ArcGIS Pro native tools only (no Python scripting)
**Skill Level:** Beginner-friendly

---

## METHOD 1: GENERATE NEAR TABLE (RECOMMENDED - EASIEST)

This is the simplest approach that handles everything automatically.

### STEP 1: Load Your Data (5 minutes)

1. **Open ArcGIS Pro** → Create new project or open existing

2. **Add Sidewalk Data:**
   - Drag `westchester_sidewalks.geojson` directly into the map
   - ArcGIS Pro automatically imports GeoJSON (no conversion needed!)
   - Your layer appears as "westchester_sidewalks"

3. **Add Parcel Data:**
   - Drag `WCGIS.tax-parcels.geojson` into the map
   - Layer appears as "WCGIS.tax-parcels"

4. **Verify Coordinate Systems:**
   - Right-click each layer → Properties → Source tab
   - Both should show: **EPSG:4326 (WGS 1984)** or similar geographic coordinate system
   - If different, proceed to Step 1.5

**STEP 1.5: Project to Common Coordinate System (if needed)**

If your layers have different coordinate systems:

1. **Analysis** tab → **Tools** → Search "Project"
2. Select **Project (Data Management)**
3. Input: Your sidewalk layer
4. Output: `sidewalks_projected`
5. Coordinate System: Match your parcel layer (or use **NAD 1983 StatePlane New York East FIPS 3101 Feet**)
6. Repeat for parcel layer if needed

### STEP 2: Generate Near Table (10 minutes)

This single tool does all the proximity analysis automatically!

1. **Analysis** tab → **Tools** → Search "Generate Near Table"

2. **Configure Parameters:**

   **Input Features:** `westchester_sidewalks` (or your sidewalk layer)
   **Near Features:** `WCGIS.tax-parcels` (or your parcel layer)
   **Output Table:** `C:\YourFolder\sidewalk_parcel_matches.dbf`
   **Search Radius:** `100 Feet` (adjust as needed - see notes below)
   **Location:** ☑ Check this box (adds XY coordinates)
   **Angle:** ☐ Leave unchecked (not needed)
   **Closest:** ☑ Check this box (finds only the CLOSEST parcel)

3. **Click Run** - Processing time: 2-10 minutes depending on data size

### STEP 3: Review Results (5 minutes)

The output table contains:

| Column | Description | Example |
|--------|-------------|---------|
| `IN_FID` | Sidewalk segment ID | 0, 1, 2, 3... |
| `NEAR_FID` | Nearest parcel ID | 45231, 45232... |
| `NEAR_DIST` | Distance in map units (feet or meters) | 15.7, 23.4... |
| `NEAR_X` | X coordinate of nearest point | -73.503414 |
| `NEAR_Y` | Y coordinate of nearest point | 41.0478923 |

**Interpretation:**
- Each row = one sidewalk segment matched to its nearest parcel
- `NEAR_DIST` = how far the sidewalk is from the parcel
- Small distances (0-25 feet) = sidewalk likely serves that parcel
- Large distances (100+ feet) = may need manual review

### STEP 4: Join Results Back to Sidewalks (10 minutes)

Now connect the results back to your original sidewalk layer:

1. **Right-click** `westchester_sidewalks` layer → **Joins and Relates** → **Add Join**

2. **Configure Join:**

   **Input Join Field:** `OBJECTID` or `FID`
   **Join Table:** `sidewalk_parcel_matches`
   **Join Table Field:** `IN_FID`
   **Keep all target features:** ☑ Check this (keeps all sidewalks even without matches)

3. **Click OK**

4. **View Results:**
   - Open attribute table of sidewalks layer
   - New columns appear: `NEAR_FID`, `NEAR_DIST`, etc.
   - Each sidewalk now knows its nearest parcel!

### STEP 5: Export Final Dataset (5 minutes)

Save your results permanently:

1. **Right-click** `westchester_sidewalks` layer → **Data** → **Export Features**

2. **Output Location:** `C:\YourFolder\sidewalks_with_parcels.geojson`

3. **Click OK**

**DONE! You now have sidewalks matched to parcels!**

---

## METHOD 2: SPATIAL JOIN (ALTERNATIVE)

Use this if you want matches based on containment or intersection rather than proximity.

### STEP 1: Buffer Sidewalks (10 minutes)

Create zones around sidewalks:

1. **Analysis** tab → **Tools** → Search "Buffer"

2. **Configure:**

   **Input:** `westchester_sidewalks`
   **Output:** `sidewalks_buffered`
   **Distance:** `50 Feet` (adjust as needed)
   **Side Type:** `FULL` (buffer both sides)
   **End Type:** `ROUND`
   **Dissolve Type:** `NONE` (keep individual buffers)

3. **Click Run**

### STEP 2: Spatial Join to Parcels (5 minutes)

Match buffered sidewalks to parcels:

1. **Analysis** tab → **Tools** → Search "Spatial Join"

2. **Configure:**

   **Target Features:** `WCGIS.tax-parcels` (parcels)
   **Join Features:** `sidewalks_buffered`
   **Output:** `parcels_with_sidewalks`
   **Match Option:** `INTERSECT`
   **Keep All Target Features:** ☑ Check (keeps parcels without sidewalks)

3. **Click Run**

### STEP 3: Review Results

The output shows which parcels intersect with sidewalk buffers:

- **Join_Count > 0** = parcel has sidewalk nearby
- **Join_Count = 0** = no sidewalk within buffer distance
- Each parcel gets attributes from nearest sidewalk

**Export as needed using same method as Method 1, Step 5**

---

## CHOOSING SEARCH RADIUS / BUFFER DISTANCE

The key decision is how far sidewalks can be from parcels and still "match."

### RECOMMENDED DISTANCES:

| Scenario | Distance | Rationale |
|----------|----------|-----------|
| **Urban dense areas** | 25-50 feet | Narrow rights-of-way, close building setbacks |
| **Suburban areas** | 50-75 feet | Wider streets, moderate setbacks |
| **Rural/large lots** | 75-150 feet | Wide rights-of-way, large property setbacks |
| **Aggressive matching** | 200+ feet | Captures all potential associations |
| **Conservative matching** | 10-25 feet | Only very close sidewalks |

### HOW TO DECIDE:

1. **Measure typical street widths** in your area using ArcGIS Pro Measure tool
2. **Add typical setback distances** (building to property line)
3. **Use that sum as your search radius**

**Example Calculation:**
- Street width: 40 feet
- Sidewalk setback from road: 5 feet
- Property line to sidewalk: ~25 feet
- **Recommended radius: 50 feet** (provides margin for error)

### TESTING DIFFERENT DISTANCES:

Run Generate Near Table multiple times with different search radii:
- `sidewalk_parcel_matches_25ft.dbf` (search radius: 25 feet)
- `sidewalk_parcel_matches_50ft.dbf` (search radius: 50 feet)
- `sidewalk_parcel_matches_100ft.dbf` (search radius: 100 feet)

Compare results to find optimal distance for your area.

---

## VALIDATION & QUALITY CONTROL

### CHECK 1: Review Distance Distribution

1. **Open** `sidewalk_parcel_matches` table
2. **Right-click** `NEAR_DIST` column → **Statistics**
3. **Review:**
   - **Mean distance:** Should be 15-40 feet for typical suburban areas
   - **Maximum distance:** Should be less than your search radius
   - **Distribution:** Most values should be similar (tight cluster)

**Red flags:**
- Mean distance > 75 feet → sidewalks far from parcels, may need different approach
- Many values at maximum distance → search radius too small

### CHECK 2: Visual Spot Checks

1. **Zoom to random locations** on map
2. **Select sidewalk segment**
3. **Check joined `NEAR_FID` value** in attribute table
4. **Select corresponding parcel** using parcel layer
5. **Verify:** Does this parcel logically match this sidewalk?

**Do 10-20 spot checks across different area types (urban, suburban, rural)**

### CHECK 3: Count Unmatched Features

```plaintext
Sidewalks with matches = [Count where NEAR_FID IS NOT NULL]
Sidewalks without matches = [Count where NEAR_FID IS NULL]
Match rate = (Matched / Total) * 100%
```

**Expected match rates:**
- Urban areas: 90-98%
- Suburban areas: 85-95%
- Rural areas: 70-85%

If match rate is low, increase search radius and re-run.

---

## HANDLING EDGE CASES

### ISSUE 1: Sidewalk Matches Multiple Parcels

**Scenario:** Sidewalk runs between two properties

**Solution Options:**

**Option A: Keep Both Matches (Manual)**
1. In Generate Near Table, uncheck "Closest"
2. Use `CLOSEST_COUNT: 2` instead
3. Each sidewalk can match 2 nearest parcels
4. Manually review which side sidewalk serves

**Option B: Use Side Attributes (If Available)**
1. Check if sidewalk data has "left_side" / "right_side" attributes
2. Match left sidewalks to left parcels only
3. Match right sidewalks to right parcels only
4. Requires additional Selection queries

### ISSUE 2: Parcel Gets Multiple Sidewalks

**Scenario:** Large parcel borders 3 different sidewalk segments

**Solution:**
1. This is actually correct! Large parcels often have multiple sidewalk exposures
2. Use Spatial Join with "ONE_TO_MANY" relationship
3. Result: Parcel appears multiple times (once per sidewalk)
4. Use **Summary Statistics** to count sidewalks per parcel:
   - **Analysis → Tools → Summary Statistics**
   - **Case Field:** Parcel ID
   - **Statistics Field:** Sidewalk ID (Count)

### ISSUE 3: No Matches Found

**Scenario:** Generate Near Table returns 0 results

**Troubleshooting:**

1. **Check coordinate systems:** Both layers must have compatible projections
   - Solution: Use Project tool to align coordinate systems

2. **Check search radius:** May be too small
   - Solution: Increase to 200+ feet for initial test

3. **Check data extent:** Layers may not overlap geographically
   - Solution: Right-click layer → Zoom to Layer to verify coverage

4. **Check geometry validity:** Corrupt geometries can fail
   - Solution: Run "Check Geometry" and "Repair Geometry" tools

---

## EXPORTING RESULTS FOR EXTERNAL USE

### OPTION 1: Export to Excel

1. **Right-click** `sidewalk_parcel_matches` table → **Export**
2. **Output:** `sidewalk_parcel_matches.xlsx`
3. **Open in Excel** for pivot tables, charts, further analysis

### OPTION 2: Export to CSV

1. **Right-click** table → **Export**
2. **Output:** `sidewalk_parcel_matches.csv`
3. **Use in Python, R, SQL databases**

### OPTION 3: Export to GeoJSON (with geometry)

1. **Export joined sidewalk layer** (Method 1, Step 5)
2. **Format:** GeoJSON
3. **Contains:** Sidewalk geometries + parcel match information
4. **Use in:** Web maps, other GIS software, sharing

### OPTION 4: Export to Shapefile (legacy)

1. **Export joined sidewalk layer**
2. **Format:** Shapefile
3. **Note:** Shapefile has 10-character field name limit (some field names may be truncated)

---

## AUTOMATING THE WORKFLOW (FUTURE)

Once you validate this workflow works for your data, you can automate it:

### MODEL BUILDER (No Coding)

1. **Analysis → ModelBuilder**
2. **Drag tools into model:**
   - Project (if needed)
   - Generate Near Table
   - Add Join
   - Export Features
3. **Connect tools** with arrows
4. **Save model** for future re-use
5. **Run model** with one click

### PYTHON SCRIPT (Advanced)

If you later need Python automation, I can provide a script that:
- Runs Generate Near Table programmatically
- Handles multiple datasets in batch
- Automates validation checks
- Generates reports

**But start with manual workflow first to ensure it meets your needs!**

---

## UNDERSTANDING YOUR SIDEWALK DATA

Based on your current data (`westchester_sidewalks.geojson`):

### CURRENT ATTRIBUTES:
- `type`: "sidewalk"
- `name`: Street name or "Sidewalk"
- `highway`: "footway" or "path"
- `surface`: Surface material (dirt, concrete, etc. - often empty)
- `source`: "OpenStreetMap"

### WHAT'S MISSING:
- **Left/Right side designation** - not included
- **Road association** - not directly linked
- **Parcel association** - THIS IS WHAT WE'RE ADDING!

### AFTER MATCHING:
Your sidewalk data will have:
- All original attributes above
- `NEAR_FID`: Parcel ID it matches to
- `NEAR_DIST`: Distance to that parcel
- **Plus any parcel attributes you choose to join!**

---

## ADDING PARCEL ATTRIBUTES TO SIDEWALKS (BONUS)

Want to know parcel owner, property value, or other parcel info for each sidewalk?

### STEP 1: Join Parcel Attributes

After Method 1, Step 4 (joining results back to sidewalks):

1. **Right-click** `westchester_sidewalks` layer → **Joins and Relates** → **Add Join**

2. **Configure:**

   **Input Join Field:** `NEAR_FID` (from previous join)
   **Join Table:** `WCGIS.tax-parcels` (original parcel layer)
   **Join Table Field:** `OBJECTID` or parcel ID field

3. **Click OK**

### STEP 2: Select Useful Parcel Fields

Now sidewalks have ALL parcel attributes. To keep only useful ones:

1. **Export Features** (Method 1, Step 5)
2. **In Field Map**, keep only:
   - `NEAR_FID` (parcel ID)
   - `NEAR_DIST` (distance)
   - `owner_name` (if available)
   - `property_address` (if available)
   - `parcel_acres` (if available)
   - Other useful parcel attributes

This creates enriched sidewalk dataset with parcel ownership/characteristics!

---

## WESTCHESTER-SPECIFIC NOTES

### YOUR DATA CHARACTERISTICS:

1. **Data Source:** OpenStreetMap via your previous analysis
2. **Coverage:** County-wide (45 Metro-North stations area)
3. **Format:** GeoJSON (natively supported by ArcGIS Pro 2.4+)
4. **Coordinate System:** EPSG:4326 (WGS 1984)
5. **Parcel Data:** County tax parcels (also GeoJSON)

### RECOMMENDED SETTINGS FOR WESTCHESTER:

- **Search Radius:** Start with **75 feet** (Westchester has mix of urban/suburban)
- **Validation Zone:** Focus on New Rochelle, Yonkers, White Plains (different densities)
- **Expected Match Rate:** 88-94% (based on your coverage analysis results)

### KNOWN ISSUES:

1. **OpenStreetMap Gaps:** Some areas lack sidewalk coverage in OSM
   - Your analysis already identified priority gaps
   - Low match rates in gap areas are expected

2. **Parcel Geometry Issues:** Some tax parcels may have complex/invalid geometries
   - Run "Repair Geometry" on parcel layer before analysis
   - Check for multipart parcels (may need to explode)

3. **Right-of-Way vs. Parcel Boundaries:** Sidewalks in public ROW won't directly touch parcels
   - This is why we use proximity matching (Near Table)
   - Typical ROW width in Westchester: 50-66 feet

---

## TROUBLESHOOTING GUIDE

### PROBLEM: "Tool failed to execute"

**Possible Causes & Solutions:**

1. **Coordinate system mismatch**
   - Check: Right-click layer → Properties → Source
   - Fix: Project both layers to same coordinate system

2. **Invalid geometry**
   - Check: Run "Check Geometry" tool
   - Fix: Run "Repair Geometry" tool

3. **Locked file/dataset in use**
   - Check: Close attribute tables, remove previous joins
   - Fix: Restart ArcGIS Pro

4. **Insufficient memory**
   - Check: Task Manager (memory usage)
   - Fix: Process smaller areas (use Select by Location first)

### PROBLEM: "No features matched"

**Solutions:**

1. **Increase search radius** to 500 feet (testing)
2. **Verify layers overlap:** Zoom to extent of both layers
3. **Check coordinate systems:** Must be compatible projections
4. **Examine data quality:** Use Select tool to verify features exist

### PROBLEM: "Results look wrong"

**Validation Steps:**

1. **Visual inspection:** Zoom to 10-20 random locations, verify matches make sense
2. **Distance statistics:** Mean distance should be reasonable (20-50 feet typical)
3. **Match rate:** Calculate % of sidewalks with matches (should be 80%+)
4. **Edge case review:** Check complex intersections, cul-de-sacs, highways

### PROBLEM: "Processing takes forever"

**Speed Improvements:**

1. **Process smaller areas:**
   - Use Select by Location to subset data
   - Run Generate Near Table on subset
   - Merge results afterward

2. **Simplify geometry:**
   - Use "Simplify Line" tool on sidewalks
   - Reduces vertex count, speeds processing

3. **Use projected coordinate system:**
   - Geographic (lat/lon) is slower
   - Project to State Plane (feet) for 2-5x speed improvement

4. **Increase search radius less frequently:**
   - Smaller radius = faster processing
   - Start with 50 feet, increase only if needed

---

## ALTERNATIVE APPROACHES (IF NATIVE TOOLS INSUFFICIENT)

### WHEN TO USE PYTHON:

You might need Python scripts if:

1. **Batch processing 100+ datasets**
2. **Complex side-of-street logic** (left vs. right parcel assignment)
3. **Integration with external databases**
4. **Automated scheduled updates**
5. **Custom distance/weighting algorithms**

### WHEN TO USE OTHER GIS SOFTWARE:

Consider alternatives if:

1. **No ArcGIS Pro license** → Use QGIS (free, has similar tools)
2. **Web-based workflow** → Use ArcGIS Online spatial analysis
3. **Database-driven** → Use PostGIS spatial queries
4. **Performance critical** → Use specialized tools (FME, Safe Software)

But for most use cases, **native ArcGIS Pro tools are sufficient and simplest!**

---

## NEXT STEPS AFTER MATCHING

Once you have sidewalk-to-parcel matches, you can:

### ANALYSIS OPPORTUNITIES:

1. **Property Value Analysis:**
   - Join parcel assessed values
   - Calculate correlation between sidewalk presence and property values
   - Generate heatmaps of high-value parcels without sidewalks

2. **Gap Prioritization:**
   - Identify parcels without nearby sidewalks
   - Rank by property density, school proximity, transit access
   - Create investment priority maps

3. **Maintenance Responsibility:**
   - Use parcel ownership to identify maintenance responsibility
   - Create maintenance zones by property type (residential, commercial, municipal)

4. **Accessibility Analysis:**
   - Calculate sidewalk access for schools, parks, transit
   - Identify underserved areas
   - Support ADA compliance planning

5. **Cost Estimation:**
   - Calculate linear feet of sidewalk needed per parcel
   - Estimate construction costs by parcel value
   - Build financial models for gap closure

---

## RECOMMENDED WORKFLOW SUMMARY

**For first-time users, follow this sequence:**

1. ✓ **Read this guide** (15 minutes)
2. ✓ **Load data into ArcGIS Pro** (5 minutes)
3. ✓ **Run Generate Near Table** with 50-foot radius (10 minutes)
4. ✓ **Review results visually** (10 minutes)
5. ✓ **Check distance statistics** (5 minutes)
6. ✓ **Adjust search radius if needed** and re-run (10 minutes)
7. ✓ **Join results back to sidewalks** (10 minutes)
8. ✓ **Export final dataset** (5 minutes)
9. ✓ **Perform 10 spot checks** (15 minutes)
10. ✓ **Document your settings/results** (10 minutes)

**Total Time: ~90 minutes for complete workflow**

---

## ADDITIONAL RESOURCES

### OFFICIAL ESRI DOCUMENTATION:

- **Generate Near Table:** https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/generate-near-table.htm
- **Spatial Join:** https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/spatial-join.htm
- **Buffer:** https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/buffer.htm

### WESTCHESTER COUNTY GIS:

- **GeoHub Portal:** https://gis.westchestergov.com
- **Official Sidewalk Data:** https://gis.westchestergov.com/datasets/wcgis::sidewalks-1/about
- **Tax Parcel Data:** https://gis.westchestergov.com/datasets/wcgis::tax-parcels/about

### YOUR PROJECT DOCUMENTATION:

- **Data Catalog:** `TAYLOR_DATA_CATALOG.md`
- **Coverage Analysis:** `comprehensive_technical_analysis.pdf`
- **Implementation Guide:** `implementation_guide.pdf`

---

## CONTACT & SUPPORT

**For questions about this guide:**
- **Author:** Arcanum Performance Monitoring
- **Email:** support@arcanumpm.com
- **Project Reference:** Westchester County Sidewalk Coverage Analysis (2025)

**For ArcGIS Pro technical support:**
- **Esri Support:** https://support.esri.com
- **Community Forums:** https://community.esri.com

**For Westchester County data questions:**
- **GIS Department:** gis@westchestergov.com
- **Phone:** (914) 995-4700

---

## VERSION HISTORY

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-07 | Initial guide created | Arcanum PM |

---

## APPENDIX: GLOSSARY

**Feature:** A spatial object (point, line, or polygon) representing a real-world entity

**Near Table:** A table showing proximity relationships between two sets of features

**Spatial Join:** Combining attributes from two layers based on spatial relationship

**Buffer:** A zone of specified distance around a feature

**Search Radius:** Maximum distance to search for nearby features

**NEAR_FID:** Field containing the ID of the nearest feature

**NEAR_DIST:** Field containing the distance to nearest feature

**Join:** Combining attributes from two tables based on common field

**Coordinate System:** Mathematical framework for specifying locations on Earth

**Projection:** Method for representing curved Earth surface on flat map

**EPSG:4326:** Standard code for WGS 1984 geographic coordinate system

**State Plane:** Projected coordinate system optimized for specific US state/zone

---

**END OF GUIDE**

This workflow provides a simple, reliable method for matching sidewalks to parcels using native ArcGIS Pro tools. No Python scripting required! The Generate Near Table approach handles the hard work automatically, and you can validate results visually to ensure accuracy.

Start with the recommended settings, adjust as needed for your specific area, and you'll have complete sidewalk-to-parcel associations in under 2 hours.
