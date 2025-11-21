# First Cut Scheduler - MVP Only

Minimal implementation with just the essentials:
- CSV parsing
- Agent calculation  
- 24-hour output
- Tests

**No Fancy Features**

## Files

- `scheduler.py` - Single file with all the logic (~100 lines)
- `sample_input.csv` - Test data from the problem
- `test_scheduler.py` - 17 unit and integration tests
- `DESIGN.md` - Design document (architecture, trade-offs, testing)

## Usage

```bash
# Run the scheduler
python3 scheduler.py sample_input.csv

# Run the tests
python3 -m pytest test_scheduler.py -v
```

## Design

See `DESIGN.md` for:
- High-level architecture and data flow
- Core algorithm and trade-offs
- Testing and observability approach
- Future enhancement roadmap

## Output

```
00:00 : total=0 ; none
06:00 : total=193 ; VNS=193
07:00 : total=877 ; VNS=193, ANMC=684
...
```

## How It Works

1. **parse_time()** - Converts "9AM" → 9, "7PM" → 19
2. **load_csv()** - Reads CSV into a list of customer dicts
3. **calculate_schedule()** - For each customer, calculates `ceil((calls/hours) * duration / 3600)` agents per hour
4. **print_schedule()** - Outputs all 24 hours

## To Modify

- **Add validation**: Add checks in `load_csv()`
- **Add JSON output**: Add a function that exports to JSON
- **Add CSV output**: Add a function that exports to CSV
- **Add utilization**: Multiply agents by a factor in `calculate_schedule()`
- **Add tests**: Create `test_scheduler.py` with pytest

## Core Formula

```python
calls_per_hour = total_calls / hours_spanned
agents_per_hour = ceil((calls_per_hour * duration_seconds) / 3600)
```
