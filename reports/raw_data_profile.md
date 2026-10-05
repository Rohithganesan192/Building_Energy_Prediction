# ASHRAE Raw Data Profile

## FACTS COMPUTED FROM DATA

### 1. Environment Details
- Python: 3.12.10
- Pandas: 3.0.6
- Numpy: 2.5.3
- Imports:
  - sklearn: Success
  - xgboost: Success
  - lightgbm: Success
  - catboost: Success
  - shap: Success

### 2. Dataset Files Summary
| File | Size (MB) | Rows | Columns |
|---|---|---|---|
| train.csv | 647.18 | 20216100 | 4 |
| test.csv | 1394.71 | 41697600 | 4 |
| building_metadata.csv | 0.04 | 1449 | 6 |
| weather_train.csv | 7.10 | 139773 | 9 |
| weather_test.csv | 14.10 | 277243 | 9 |
| sample_submission.csv | 426.83 | 41697600 | 2 |

### 3. TRAIN SCHEMA
| Column Name | Data Type | Example Value | Missing Count | Missing % |
|---|---|---|---|---|
| building_id | int64 | 0 | 0 | 0.00% |
| meter | int64 | 0 | 0 | 0.00% |
| timestamp | str | 2016-01-01 00:00:00 | 0 | 0.00% |
| meter_reading | float64 | 0.0 | 0 | 0.00% |

- **Temporal Coverage**: 2016-01-01 00:00:00 to 2016-12-31 23:00:00
- **Unique Buildings**: 1449
- **Target Stats (meter_reading)**: Count=20216100, Min=0.00, Max=21904700.00, Mean=2117.12, Approx Median=79.70, Std=153235.62

### 4. TEST SCHEMA
| Column Name | Data Type | Example Value | Missing Count | Missing % |
|---|---|---|---|---|
| row_id | int64 | 0 | 0 | 0.00% |
| building_id | int64 | 0 | 0 | 0.00% |
| meter | int64 | 0 | 0 | 0.00% |
| timestamp | str | 2017-01-01 00:00:00 | 0 | 0.00% |

- **Temporal Coverage**: 2017-01-01 00:00:00 to 2018-12-31 23:00:00
- **Unique Buildings**: 1449

### 5. BUILDING METADATA SCHEMA
| Column Name | Data Type | Example Value | Missing Count | Missing % |
|---|---|---|---|---|
| site_id | int64 | 0 | 0 | 0.00% |
| building_id | int64 | 0 | 0 | 0.00% |
| primary_use | str | Education | 0 | 0.00% |
| square_feet | int64 | 7432 | 0 | 0.00% |
| year_built | float64 | 2008.0 | 774 | 53.42% |
| floor_count | float64 | 5.0 | 1094 | 75.50% |

- **Unique Sites**: 16
- **Unique Buildings**: 1449
- **Primary Uses**: 16 categories
- **Year Built Range**: 1900.0 to 2017.0
- **Square Feet Range**: 283.0 to 875000.0
- **Floor Count Range**: 1.0 to 26.0

### 6. WEATHER TRAIN SCHEMA
| Column Name | Data Type | Example Value | Missing Count | Missing % |
|---|---|---|---|---|
| site_id | int64 | 0 | 0 | 0.00% |
| timestamp | str | 2016-01-01 00:00:00 | 0 | 0.00% |
| air_temperature | float64 | 25.0 | 55 | 0.04% |
| cloud_coverage | float64 | 6.0 | 69173 | 49.49% |
| dew_temperature | float64 | 20.0 | 113 | 0.08% |
| precip_depth_1_hr | float64 | -1.0 | 50289 | 35.98% |
| sea_level_pressure | float64 | 1019.7 | 10618 | 7.60% |
| wind_direction | float64 | 0.0 | 6268 | 4.48% |
| wind_speed | float64 | 0.0 | 304 | 0.22% |

- **Temporal Coverage**: 2016-01-01 00:00:00 to 2016-12-31 23:00:00
- **Unique Sites**: 16

### 7. WEATHER TEST SCHEMA
| Column Name | Data Type | Example Value | Missing Count | Missing % |
|---|---|---|---|---|
| site_id | int64 | 0 | 0 | 0.00% |
| timestamp | str | 2017-01-01 00:00:00 | 0 | 0.00% |
| air_temperature | float64 | 17.8 | 104 | 0.04% |
| cloud_coverage | float64 | 4.0 | 140448 | 50.66% |
| dew_temperature | float64 | 11.7 | 327 | 0.12% |
| precip_depth_1_hr | float64 | 0.0 | 95588 | 34.48% |
| sea_level_pressure | float64 | 1021.4 | 21265 | 7.67% |
| wind_direction | float64 | 100.0 | 12370 | 4.46% |
| wind_speed | float64 | 3.6 | 460 | 0.17% |

- **Temporal Coverage**: 2017-01-01 00:00:00 to 2018-12-31 23:00:00
- **Unique Sites**: 16

### 8. SAMPLE SUBMISSION SCHEMA
| Column Name | Data Type | Example Value | Missing Count | Missing % |
|---|---|---|---|---|
| row_id | int64 | 0 | 0 | 0.00% |
| meter_reading | int64 | 0 | 0 | 0.00% |

- **Identifier Column**: row_id

### 9. EXPLICIT DATASET RELATIONSHIPS

The following mapping illustrates exactly how the datasets relate to one another:

```text
train.csv / test.csv
    │
    │ (building_id)
    ▼
building_metadata.csv
    │
    │ (site_id)
    ▼
weather_train.csv / weather_test.csv  <── (site_id + timestamp)
```

**Relationship Verifications (computed from data):**
- Train buildings missing from metadata: 0
- Test buildings missing from metadata: 0
- Train site_ids lacking weather_train coverage: 0
- Test site_ids lacking weather_test coverage: 0

### 10. METER TYPES
The raw energy datasets (`train.csv`, `test.csv`) encode `meter` as integers (4 unique types). They correspond to the following categories:
- `0`: electricity
- `1`: chilledwater
- `2`: steam
- `3`: hotwater

---

## LIMITATIONS OF THE INSPECTION
- **Duplicate Detection**: A complete global duplicate check across all rows in train.csv and test.csv was not performed due to extreme memory constraints. Only duplicates within individual 2-million-row chunks were counted.
- **Median Calculation**: True median for `meter_reading` in train.csv cannot be computed precisely in chunks without excessive memory overhead. The reported median is an `approximate_median_from_sample` derived from random chunk subsamples.
- **Schema/Example Generation**: Example values are selected solely from the first available valid row in a given column.