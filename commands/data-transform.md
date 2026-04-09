# data-transform

> Transform, clean, reshape, and preprocess data using pandas and numpy. Works with ANY LLM provider (GPT, Gemini, Claude, etc.).

# Data Transformation (Universal)

## Overview
This skill enables you to perform comprehensive data transformations including cleaning, normalization, reshaping, filtering, and feature engineering. Unlike cloud-hosted solutions, this skill uses standard Python data manipulation libraries (**pandas**, **numpy**, **sklearn**) and executes **locally** in your environment, making it compatible with **ALL LLM providers** including GPT, Gemini, Claude, DeepSeek, and Qwen.

## When to Use This Skill
- Clean and preprocess raw data
- Normalize or scale numeric features
- Reshape data between wide and long formats
- Handle missing values
- Filter and subset datasets
- Merge multiple datasets
- Create new features from existing ones
- Convert data types and formats

## How to Use

### Step 1: Import Required Libraries
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import warnings
warnings.filterwarnings('ignore')
```

### Step 2: Data Cleaning
```python
# Load data
df = pd.read_csv('data.csv')

# Check for missing values
print("Missing values per column:")
print(df.isnull().sum())

# Remove duplicates
df_clean = df.drop_duplicates()
print(f"Removed {len(df) - len(df_clean)} duplicate rows")

# Remove rows with any missing values
df_clean = df_clean.dropna()

# Or fill missing values
df_clean = df.copy()
df_clean['numeric_col'] = df_clean['numeric_col'].fillna(df_clean['numeric_col'].median())
df_clean['categorical_col'] = df_clean['categorical_col'].fillna('Unknown')

# Remove outliers using IQR method
def remove_outliers(df, column, multiplier=1.5):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

df_clean = remove_outliers(df_clean, 'expression_level')
print(f"✅ Data cleaned: {len(df_clean)} rows remaining")
```

### Step 3: Normalization and Scaling
```python
# Select numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns

# Method 1: Z-score normalization (StandardScaler)
scaler = StandardScaler()
df_normalized = df.copy()
df_normalized[numeric_cols] = scaler.fit_transform(df[numeric_cols])

print("Z-score normalized (mean=0, std=1)")
print(df_normalized[numeric_cols].describe())

# Method 2: Min-Max scaling (0-1 range)
scaler_minmax = MinMaxScaler()
df_scaled = df.copy()
df_scaled[numeric_cols] = scaler_minmax.fit_transform(df[numeric_cols])

print("\nMin-Max scaled (range 0-1)")
print(df_scaled[numeric_cols].describe())

# Method 3: Robust scaling (resistant to outliers)
scaler_robust = RobustScaler()
df_robust = df.copy()
df_robust[numeric_cols] = scaler_robust.fit_transform(df[numeric_cols])

print("\nRobust scaled (median=0, IQR=1)")
print(df_robust[numeric_cols].describe())

# Method 4: Log transformation
df_log = df.copy()
df_log['log_expression'] = np.log1p(df_log['expression'])  # log1p(x) = log(1+x)

print("✅ Data normalized and scaled")
```

### Step 4: Data Reshaping
```python
# Convert wide format to long format (melt)
# Wide format: columns are different conditions/samples
# Long format: one column for variable, one for value

df_wide = pd.DataFrame({
    'gene': ['GENE1', 'GENE2', 'GENE3'],
    'sample_A': [10, 20, 15],
    'sample_B': [12, 18, 14],
    'sample_C': [11, 22, 16]
})

df_long = df_wide.melt(
    id_vars=['gene'],
    var_name='sample',
    value_name='expression'
)

print("Long format:")
print(df_long)

# Convert long format to wide format (pivot)
df_wide_reconstructed = df_long.pivot(
    index='gene',
    columns='sample',
    values='expression'
)

print("\nWide format (reconstructed):")
print(df_wide_reconstructed)

# Pivot table with aggregation
df_pivot = df_long.pivot_table(
    index='gene',
    columns='sample',
    values='expression',
    aggfunc='mean'  # Can use sum, median, etc.
)

print("✅ Data reshaped")
```

### Step 5: Filtering and Subsetting
```python
# Filter rows by condition
high_expression = df[df['expression'] > 100]

# Multiple conditions (AND)
filtered = df[(df['expression'] > 50) & (df['qvalue'] < 0.05)]

# Multiple conditions (OR)
filtered = df[(df['celltype'] == 'T cell') | (df['celltype'] == 'B cell')]

# Filter by list of values
selected_genes = ['GENE1', 'GENE2', 'GENE3']
filtered = df[df['gene'].isin(selected_genes)]

# Filter by string pattern
filtered = df[df['gene'].str.startswith('MT-')]  # Mitochondrial genes

# Select specific columns
selected_cols = df[['gene', 'log2FC', 'pvalue', 'qvalue']]

# Select columns by pattern
numeric_cols = df.select_dtypes(include=[np.number])
categorical_cols = df.select_dtypes(include=['object', 'category'])

# Sample random rows
df_sample = df.sample(n=1000, random_state=42)  # 1000 random rows
df_sample_frac = df.sample(frac=0.1, random_state=42)  # 10% of rows

# Top N rows
top_genes = df.nlargest(10, 'expression')
bottom_genes = df.nsmallest(10, 'pvalue')

print(f"✅ Filtered dataset: {len(filtered)} rows")
```

### Step 6: Merging and Joining Datasets
```python
# Inner join (only matching rows)
merged = pd.merge(df1, df2, on='gene', how='inner')

# Left join (all rows from df1)
merged = pd.merge(df1, df2, on='gene', how='left')

# Outer join (all rows from both)
merged = pd.merge(df1, df2, on='gene', how='outer')

# Join on multiple columns
merged = pd.merge(df1, df2, on=['gene', 'sample'], how='inner')

# Join on different column names
merged = pd.merge(
    df1, df2,
    left_on='gene_name',
    right_on='gene_id',
    how='inner'
)

# Concatenate vertically (stack DataFrames)
combined = pd.concat([df1, df2], axis=0, ignore_index=True)

# Concatenate horizontally (side-by-side)
combined = pd.concat([df1, df2], axis=1)

print(f"✅ Merged datasets: {len(merged)} rows")
```

## Advanced Features

### Handling Missing Values
```python
# Check missing value patterns
missing_summary = pd.DataFrame({
    'column': df.columns,
    'missing_count': df.isnull().sum(),
    'missing_percent': (df.isnull().sum() / len(df) * 100).round(2)
})

print("Missing value summary:")
print(missing_summary[missing_summary['missing_count'] > 0])

# Strategy 1: Fill with statistical measures
df_filled = df.copy()
df_filled['numeric_col'].fillna(df_filled['numeric_col'].median(), inplace=True)
df_filled['categorical_col'].fillna(df_filled['categorical_col'].mode()[0], inplace=True)

# Strategy 2: Forward fill (use previous value)
df_filled = df.fillna(method='ffill')

# Strategy 3: Interpolation (for time-series)
df_filled = df.copy()
df_filled['expression'] = df_filled['expression'].interpolate(method='linear')

# Strategy 4: Drop columns with too many missing values
threshold = 0.5  # Drop if >50% missing
df_cleaned = df.dropna(thresh=len(df) * threshold, axis=1)

print("✅ Missing values handled")
```

### Feature Engineering
```python
# Create new features from existing ones

# 1. Binning continuous variables
df['expression_category'] = pd.cut(
    df['expression'],
    bins=[0, 10, 50, 100, np.inf],
    labels=['Very Low', 'Low', 'Medium', 'High']
)

# 2. Create ratio features
df['gene_to_umi_ratio'] = df['n_genes'] / df['n_counts']

# 3. Create interaction features
df['interaction'] = df['feature1'] * df['feature2']

# 4. Extract datetime features
df['date'] = pd.to_datetime(df['timestamp'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day_of_week'] = df['date'].dt.dayofweek

# 5. One-hot encoding for categorical variables
df_encoded = pd.get_dummies(df, columns=['celltype', 'condition'], prefix=['cell', 'cond'])

# 6. Label encoding (ordinal)
le = LabelEncoder()
df['celltype_encoded'] = le.fit_transform(df['celltype'])

# 7. Create polynomial features
df['expression_squared'] = df['expression'] ** 2
df['expression_cubed'] = df['expression'] ** 3

# 8. Create lag features (time-series)
df['expression_lag1'] = df.groupby('gene')['expression'].shift(1)
df['expression_lag2'] = df.groupby('gene')['expression'].shift(2)

print("✅ New features created")
```

### Grouping and Aggregation
```python
# Group by single column and aggregate
cluster_stats = df.groupby('cluster').agg({
    'expression': ['mean', 'median', 'std', 'count'],
    'n_genes': 'mean',
    'n_counts': 'sum'
})

print("Cluster statistics:")
print(cluster_stats)

# Group by multiple columns
stats = df.groupby(['cluster', 'celltype']).agg({
    'expression': 'mean',
    'qvalue': lambda x: (x < 0.05).sum()  # Count significant
})

# Apply custom function
def custom_stats(group):
    return pd.Series({
        'mean_expr': group['expression'].mean(),
        'cv': group['expression'].std() / group['expression'].mean(),  # Coefficient of variation
        'n_cells': len(group)
    })

cluster_custom = df.groupby('cluster').apply(custom_stats)

print("✅ Data aggregated")
```

### Data Type Conversions
```python
# Convert column to different type
df['cluster'] = df['cluster'].astype(str)
df['expression'] = df['expression'].astype(float)
df['significant'] = df['significant'].astype(bool)

# Convert to categorical (saves memory)
df['celltype'] = df['celltype'].astype('category')

# Parse dates
df['date'] = pd.to_datetime(df['date_string'], format='%Y-%m-%d')

# Convert numeric to categorical
df['expression_level'] = pd.cut(df['expression'], bins=3, labels=['Low', 'Medium', 'High'])

# String operations
df['gene_upper'] = df['gene'].str.upper()
df['is_mitochondrial'] = df['gene'].str.startswith('MT-')

print("✅ Data types converted")
```

## Common Use Cases

### AnnData to DataFrame Conversion
```python
# Convert AnnData .obs (cell metadata) to DataFrame
df_cells = adata.obs.copy()

# Convert .var (gene metadata) to DataFrame
df_genes = adata.var.copy()

# Extract expression matrix to DataFrame
# Warning: This can be memory-intensive for large datasets
df_expression = pd.DataFrame(
    adata.X.toarray() if hasattr(adata.X, 'toarray') else adata.X,
    index=adata.obs_names,
    columns=adata.var_names
)

# Extract specific layer
if 'normalized' in adata.layers:
    df_normalized = pd.DataFrame(
        adata.layers['normalized'],
        index=adata.obs_names,
        columns=adata.var_names
    )

print("✅ AnnData converted to DataFrames")
```

### Gene Expression Matrix Transformation
```python
# Transpose: genes as rows, cells as columns → cells as rows, genes as columns
df_transposed = df.T

# Log-transform gene expression
df_log = np.log1p(df)  # log1p(x) = log(1+x), avoids log(0)

# Z-score normalize per gene (across cells)
df_zscore = df.apply(lambda x: (x - x.mean()) / x.std(), axis=1)

# Scale per cell (divide by library size)
library_sizes = df.sum(axis=1)
df_normalized = df.div(library_sizes, axis=0) * 1e6  # CPM normalization

# Filter low-expressed genes
min_cells = 10  # Gene must be expressed in at least 10 cells
gene_mask = (df > 0).sum(axis=0) >= min_cells
df_filtered = df.loc[:, gene_mask]

print(f"✅ Filtered to {df_filtered.shape[1]} genes")
```

### Differential Expression Results Processing
```python
# Assuming deg_df has columns: gene, log2FC, pvalue, qvalue

# Add significance labels
deg_df['regulation'] = 'Not Significant'
deg_df.loc[(deg_df['log2FC'] > 1) & (deg_df['qvalue'] < 0.05), 'regulation'] = 'Up-regulated'
deg_df.loc[(deg_df['log2FC'] < -1) & (deg_df['qvalue'] < 0.05), 'regulation'] = 'Down-regulated'

# Sort by significance
deg_df_sorted = deg_df.sort_values('qvalue')

# Top upregulated genes
top_up = deg_df[deg_df['regulation'] == 'Up-regulated'].nlargest(20, 'log2FC')

# Top downregulated genes
top_down = deg_df[deg_df['regulation'] == 'Down-regulated'].nsmallest(20, 'log2FC')

# Create summary table
summary = deg_df.groupby('regulation').agg({
    'gene': 'count',
    'log2FC': ['mean', 'median'],
    'qvalue': 'min'
})

print("DEG Summary:")
print(summary)

# Export results
deg_df_sorted.to_csv('deg_results_processed.csv', index=False)
print("✅ DEG results processed and saved")
```

### Batch Processing Multiple Files
```python
import glob

# Find all CSV files
file_paths = glob.glob('data/*.csv')

# Read and combine
dfs = []
for file_path in file_paths:
    df = pd.read_csv(file_path)
    # Add source file as column
    df['source_file'] = file_path.split('/')[-1]
    dfs.append(df)

# Combine all
df_combined = pd.concat(dfs, ignore_index=True)

print(f"✅ Processed {len(file_paths)} files, total {len(df_combined)} rows")
```

## Best Practices

1. **Check Data First**: Always use `df.head()`, `df.info()`, `df.describe()` to understand data
2. **Copy Before Modify**: Use `df.copy()` to avoid modifying original data
3. **Chain Operations**: Use method chaining for readability: `df.dropna().drop_duplicates().reset_index(drop=True)`
4. **Index Management**: Reset index after filtering: `df.reset_index(drop=True)`
5. **Memory Efficiency**: Use categorical dtype for low-cardinality string columns
6. **Vectorization**: Avoid loops; use vectorized operations (numpy, pandas built-ins)
7. **Documentation**: Comment complex transformations
8. **Validation**: Check data after each major transformation

## Troubleshooting

### Issue: "SettingWithCopyWarning"
**Solution**: Use `.copy()` to create explicit copy
```python
df_subset = df[df['expression'] > 10].copy()
df_subset['new_col'] = values  # No warning
```

### Issue: "Memory error with large datasets"
**Solution**: Process in chunks
```python
chunk_size = 10000
chunks = []
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    # Process chunk
    processed = chunk[chunk['expression'] > 0]
    chunks.append(processed)

df = pd.concat(chunks, ignore_index=True)
```

### Issue: "Key error when merging"
**Solution**: Check column names and presence
```python
print("Columns in df1:", df1.columns.tolist())
print("Columns in df2:", df2.columns.tolist())

# Use left_on/right_on if names differ
merged = pd.merge(df1, df2, left_on='gene_name', right_on='gene_id')
```

### Issue: "Data types mismatch in merge"
**Solution**: Ensure consistent types
```python
df1['gene'] = df1['gene'].astype(str)
df2['gene'] = df2['gene'].astype(str)
merged = pd.merge(df1, df2, on='gene')
```

### Issue: "Index alignment errors"
**Solution**: Reset index or specify `ignore_index=True`
```python
df_combined = pd.concat([df1, df2], ignore_index=True)
```

## Critical API Reference - DataFrame vs Series Attributes

### IMPORTANT: `.dtype` vs `.dtypes` - Common Pitfall!

**CORRECT usage:**
```python
# For DataFrame - use .dtypes (PLURAL) to get all column types
df.dtypes  # Returns Series with column names as index, dtypes as values

# For a single column (Series) - use .dtype (SINGULAR)
df['column_name'].dtype  # Returns single dtype object

# Check specific column type
if df['expression'].dtype == 'float64':
    print("Expression is float64")

# Check all column types
print(df.dtypes)  # Shows dtype for each column
```

**WRONG - DO NOT USE:**
```python
# WRONG! DataFrame does NOT have .dtype (singular)
# df.dtype  # AttributeError: 'DataFrame' object has no attribute 'dtype'

# WRONG! This will fail
# if df.dtype == 'float64':  # ERROR!
```

### DataFrame Type Inspection Methods

```python
# Get dtypes for all columns
df.dtypes

# Get detailed info including dtypes
df.info()

# Check if column is numeric
pd.api.types.is_numeric_dtype(df['column'])

# Check if column is categorical
pd.api.types.is_categorical_dtype(df['column'])

# Select columns by dtype
numeric_cols = df.select_dtypes(include=['number'])
string_cols = df.select_dtypes(include=['object', 'string'])
```

### Series vs DataFrame - Key Differences

| Attribute/Method | Series | DataFrame |
|-----------------|--------|-----------|
| `.dtype` | ✅ Returns single dtype | ❌ AttributeError |
| `.dtypes` | ❌ AttributeError | ✅ Returns Series of dtypes |
| `.shape` | `(n,)` tuple | `(n, m)` tuple |
| `.values` | 1D array | 2D array |

## Technical Notes

- **Libraries**: Uses `pandas` (1.x+), `numpy`, `scikit-learn` (widely supported)
- **Execution**: Runs locally in the agent's sandbox
- **Compatibility**: Works with ALL LLM providers (GPT, Gemini, Claude, DeepSeek, Qwen, etc.)
- **Performance**: Pandas is optimized with C backend; most operations are fast for <1M rows
- **Memory**: Pandas DataFrames store data in memory; use chunking for very large files
- **Precision**: Numeric operations use float64 by default (can use float32 to save memory)

## References
- pandas documentation: https://pandas.pydata.org/docs/
- pandas user guide: https://pandas.pydata.org/docs/user_guide/index.html
- scikit-learn preprocessing: https://scikit-learn.org/stable/modules/preprocessing.html
- pandas cheat sheet: https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf
