# jupyter-sqlglot

A Jupyter Notebook extension that automatically formats Spark SQL queries using [SQLGlot](https://github.com/tobymao/sqlglot). Similar to how `jupyter-black` formats Python code, `jupyter-sqlglot` formats SQL strings within your notebook cells.

## Features

- 🔄 **Automatic Formatting**: Formats SQL on cell execution
- 🎯 **Spark SQL Support**: Optimized for Spark SQL dialect
- 🔗 **F-String Compatible**: Preserves Python interpolations in f-strings
- 🤝 **Works with jupyter-black**: Designed to coexist peacefully
- ⚡ **Zero Configuration**: Works out of the box with sensible defaults

## Installation

### From PyPI (when published)

```bash
pip install jupyter-sqlglot
```

### From Source

```bash
git clone https://github.com/yourusername/jupyter-sqlglot.git
cd jupyter-sqlglot
pip install -e .
```

## Usage

### Basic Usage

Load the extension in your Jupyter notebook:

```python
%load_ext jupyter_sqlglot
```

Now any SQL in `spark.sql()` calls or `%%sql` magic cells will be automatically formatted when you execute the cell.

### With Configuration

```python
import jupyter_sqlglot

jupyter_sqlglot.init(
    dialect='spark',    # SQL dialect (default: 'spark')
    indent=4,          # Indentation spaces (default: 4)
    uppercase=True,    # Uppercase keywords (default: True)
    pretty=True,       # Pretty print (default: True)
    debug=False        # Print debug messages (default: False)
)
```

## Examples

### Example 1: Simple Query

**Before:**
```python
df = spark.sql("select * from users where age>25")
```

**After (automatically formatted):**
```python
df = spark.sql("""
SELECT
    *
FROM users
WHERE
    age > 25
""")
```

### Example 2: F-String with Variables

**Before:**
```python
table_name = "sales"
df = spark.sql(f"select sum(amount) from {table_name} where year=2024")
```

**After (automatically formatted):**
```python
table_name = "sales"
df = spark.sql(f"""
SELECT
    SUM(amount)
FROM {table_name}
WHERE
    year = 2024
""")
```

### Example 3: Magic Cell

**Before:**
```
%%sql
select customer_id,count(*) from orders group by customer_id
```

**After (automatically formatted):**
```
%%sql
SELECT
    customer_id,
    COUNT(*)
FROM orders
GROUP BY
    customer_id
```

## Using with jupyter-black

`jupyter-sqlglot` is designed to work alongside `jupyter-black`. Load them in this order:

```python
%load_ext jupyter_black
%load_ext jupyter_sqlglot
```

**Example with both extensions:**

**Input:**
```python
x=[1,2,3]
df=spark.sql(f"select * from {my_table} where id>10")
```

**Output (formatted by both):**
```python
x = [1, 2, 3]  # Formatted by Black
df = spark.sql(f"""  # SQL formatted by SQLGlot
SELECT
    *
FROM {my_table}
WHERE
    id > 10
""")
```

## How It Works

1. **Hooks into Cell Execution**: Uses IPython's `pre_run_cell` event
2. **Detects SQL**: Finds `spark.sql()` calls and `%%sql` magics
3. **Masks F-Strings**: Temporarily replaces `{variables}` with placeholders
4. **Formats with SQLGlot**: Applies SQL formatting
5. **Restores F-Strings**: Puts back the `{variables}`
6. **Updates Display**: Shows formatted code in the notebook

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dialect` | str | `"spark"` | SQL dialect for parsing |
| `indent` | int | `4` | Number of spaces for indentation |
| `uppercase` | bool | `True` | Uppercase SQL keywords |
| `pretty` | bool | `True` | Enable pretty printing |
| `debug` | bool | `False` | Print debug messages during formatting |

## Error Handling

If SQLGlot cannot parse your SQL (e.g., incomplete query while typing), the extension will:
- Log a warning (visible in console)
- **Allow your cell to execute unchanged**
- Never break your workflow

## Supported Patterns

Currently supports:
- ✅ `spark.sql("...")` with single quotes
- ✅ `spark.sql("...")` with double quotes
- ✅ `spark.sql("""...""")` with triple quotes
- ✅ `spark.sql(f"...")` with f-strings
- ✅ `%%sql` magic cells
- ✅ Complex Spark SQL (LATERAL VIEW, etc.)

## Requirements

- Python 3.8+
- IPython 7.0+
- SQLGlot 20.0+
- Jupyter Notebook or JupyterLab

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/jupyter-sqlglot.git
cd jupyter-sqlglot
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=jupyter_sqlglot --cov-report=html
```

### Build Wheel

```bash
python -m build
```

The `.whl` file will be in the `dist/` directory.

## Architecture

Inspired by [jupyter-black](https://github.com/n8henrie/jupyter-black), this extension:
- Uses `shell.set_next_input()` for cell updates (same as jupyter-black)
- Hooks into `pre_run_cell` for formatting before execution
- Designed for peaceful coexistence with other formatters

## Troubleshooting

### Extension not loading

Make sure you're in a Jupyter environment:
```python
from IPython import get_ipython
print(get_ipython())  # Should not be None
```

### SQL not formatting

Enable debug mode to see what's happening:
```python
import jupyter_sqlglot
jupyter_sqlglot.init(debug=True)
```

Then check that:
1. Your SQL is valid Spark SQL
2. You're using `spark.sql()` or `%%sql` magic
3. The debug messages show SQL is being detected and formatted

### Conflicts with jupyter-black

Load extensions in order:
```python
%load_ext jupyter_black  # First
%load_ext jupyter_sqlglot  # Second
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Inspired by [jupyter-black](https://github.com/n8henrie/jupyter-black)
- Uses [SQLGlot](https://github.com/tobymao/sqlglot) for SQL parsing and formatting

## Related Projects

- [jupyter-black](https://github.com/n8henrie/jupyter-black) - Python code formatter for Jupyter
- [SQLGlot](https://github.com/tobymao/sqlglot) - SQL parser and transpiler

## Changelog