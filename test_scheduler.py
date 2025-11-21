"""Simple tests for bare bones scheduler."""

import math
import io
import sys
from scheduler import parse_time, load_csv, calculate_schedule, print_schedule


def test_parse_time_am():
    """Test parsing AM times."""
    assert parse_time("12AM") == 0   # midnight
    assert parse_time("1AM") == 1
    assert parse_time("9AM") == 9
    assert parse_time("11AM") == 11


def test_parse_time_pm():
    """Test parsing PM times."""
    assert parse_time("12PM") == 12  # noon
    assert parse_time("1PM") == 13
    assert parse_time("7PM") == 19
    assert parse_time("11PM") == 23


def test_parse_time_with_spaces():
    """Test parsing with extra spaces."""
    assert parse_time("  9AM  ") == 9
    assert parse_time(" 7PM ") == 19


def test_load_csv():
    """Test loading CSV file."""
    customers = load_csv("sample_input.csv")
    
    # Should have 6 customers
    assert len(customers) == 6
    
    # Check first customer
    first = customers[0]
    assert first['name'] == 'Stanford Hospital'
    assert first['duration'] == 300
    assert first['start'] == 9
    assert first['end'] == 19
    assert first['calls'] == 20000


def test_calculate_agents_single_customer():
    """Test agent calculation for one customer."""
    customers = [{
        'name': 'Test',
        'duration': 300,  # 5 minutes
        'start': 9,
        'end': 17,  # 8 hours
        'calls': 800
    }]
    
    schedule = calculate_schedule(customers)
    
    # Hours 0-8 should be empty
    for h in range(9):
        assert schedule[h]['total'] == 0
    
    # Hours 9-16 should have agents
    for h in range(9, 17):
        assert schedule[h]['total'] > 0
        assert 'Test' in schedule[h]['per_customer']
    
    # Hours 17-23 should be empty
    for h in range(17, 24):
        assert schedule[h]['total'] == 0


def test_calculate_agents_formula():
    """Test the core formula: ceil((calls/hours) * duration / 3600)."""
    # VNS: 40500 calls over 7 hours, 120s per call
    # Expected: ceil((40500/7) * 120 / 3600) = ceil(192.857) = 193
    
    customers = [{
        'name': 'VNS',
        'duration': 120,
        'start': 6,
        'end': 13,  # 7 hours
        'calls': 40500
    }]
    
    schedule = calculate_schedule(customers)
    
    # Any hour in the window should have 193 agents
    assert schedule[6]['per_customer']['VNS'] == 193
    assert schedule[12]['per_customer']['VNS'] == 193


def test_full_sample_data():
    """Test with the full sample data against expected values."""
    customers = load_csv("sample_input.csv")
    schedule = calculate_schedule(customers)
    
    # Test specific hours from problem statement
    assert schedule[6]['total'] == 193     # Hour 6
    assert schedule[7]['total'] == 877     # Hour 7
    assert schedule[11]['total'] == 2059   # Hour 11
    assert schedule[19]['total'] == 684    # Hour 19
    
    # Empty hours
    assert schedule[0]['total'] == 0
    assert schedule[23]['total'] == 0


def test_overlapping_customers():
    """Test that overlapping time windows work correctly."""
    customers = [
        {
            'name': 'Morning',
            'duration': 300,
            'start': 6,
            'end': 12,  # 6 hours
            'calls': 600
        },
        {
            'name': 'Afternoon',
            'duration': 300,
            'start': 10,
            'end': 18,  # 8 hours
            'calls': 800
        }
    ]
    
    schedule = calculate_schedule(customers)
    
    # Hour 6-9: only Morning
    for h in range(6, 10):
        assert 'Morning' in schedule[h]['per_customer']
        assert 'Afternoon' not in schedule[h]['per_customer']
    
    # Hour 10-11: both
    for h in range(10, 12):
        assert 'Morning' in schedule[h]['per_customer']
        assert 'Afternoon' in schedule[h]['per_customer']
    
    # Hour 12-17: only Afternoon
    for h in range(12, 18):
        assert 'Morning' not in schedule[h]['per_customer']
        assert 'Afternoon' in schedule[h]['per_customer']


def test_zero_hour_span():
    """Test customer with start_hour == end_hour."""
    customers = [{
        'name': 'Test',
        'duration': 300,
        'start': 9,
        'end': 9,  # No time span
        'calls': 100
    }]
    
    schedule = calculate_schedule(customers)
    
    # Should not crash and hour 9 should be empty
    assert schedule[9]['total'] == 0


def test_all_24_hours_present():
    """Test that all 24 hours are in the schedule."""
    customers = load_csv("sample_input.csv")
    schedule = calculate_schedule(customers)
    
    assert len(schedule) == 24
    for h in range(24):
        assert h in schedule
        assert 'total' in schedule[h]
        assert 'per_customer' in schedule[h]


def test_total_equals_sum():
    """Test that total = sum of per_customer values."""
    customers = load_csv("sample_input.csv")
    schedule = calculate_schedule(customers)
    
    for h in range(24):
        calculated_sum = sum(schedule[h]['per_customer'].values())
        assert schedule[h]['total'] == calculated_sum


def test_print_schedule_format():
    """Test that print_schedule outputs correct format."""
    customers = [{
        'name': 'Test',
        'duration': 300,
        'start': 6,
        'end': 8,
        'calls': 100
    }]
    
    schedule = calculate_schedule(customers)
    
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    print_schedule(schedule)
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    lines = output.strip().split('\n')
    
    # Should have 24 lines (one for each hour)
    assert len(lines) == 24


def test_print_schedule_hour_format():
    """Test that each line has correct format: HH:00 : total=N ; ..."""
    customers = [{
        'name': 'Test',
        'duration': 300,
        'start': 9,
        'end': 10,
        'calls': 100
    }]
    
    schedule = calculate_schedule(customers)
    
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    print_schedule(schedule)
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    lines = output.strip().split('\n')
    
    # Check first line format
    assert lines[0].startswith("00:00 : total=")
    assert " ; " in lines[0]
    
    # Check specific line (hour 9)
    assert lines[9].startswith("09:00 : total=")
    assert " ; " in lines[9]


def test_print_schedule_empty_hours():
    """Test that empty hours show 'none'."""
    customers = [{
        'name': 'Test',
        'duration': 300,
        'start': 9,
        'end': 10,
        'calls': 100
    }]
    
    schedule = calculate_schedule(customers)
    
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    print_schedule(schedule)
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    lines = output.strip().split('\n')
    
    # Hour 0 should have no agents
    assert lines[0] == "00:00 : total=0 ; none"
    
    # Hour 23 should have no agents
    assert lines[23] == "23:00 : total=0 ; none"


def test_print_schedule_with_customers():
    """Test that print_schedule shows customer names."""
    customers = [{
        'name': 'VNS',
        'duration': 120,
        'start': 6,
        'end': 13,
        'calls': 40500
    }]
    
    schedule = calculate_schedule(customers)
    
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    print_schedule(schedule)
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    lines = output.strip().split('\n')
    
    # Hour 6 should show VNS
    assert "VNS=" in lines[6]
    assert "total=193" in lines[6]
    
    # Hour 5 should show none
    assert lines[5] == "05:00 : total=0 ; none"


def test_print_schedule_multiple_customers():
    """Test print_schedule with multiple customers in same hour."""
    customers = [
        {
            'name': 'Customer A',
            'duration': 300,
            'start': 9,
            'end': 11,
            'calls': 100
        },
        {
            'name': 'Customer B',
            'duration': 300,
            'start': 9,
            'end': 11,
            'calls': 100
        }
    ]
    
    schedule = calculate_schedule(customers)
    
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    print_schedule(schedule)
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    lines = output.strip().split('\n')
    
    # Hour 9 should have both customers
    line9 = lines[9]
    assert "Customer A=" in line9
    assert "Customer B=" in line9
    assert "," in line9  # Should have comma separator


def test_print_schedule_sample_data():
    """Test print_schedule with full sample data."""
    customers = load_csv("sample_input.csv")
    schedule = calculate_schedule(customers)
    
    # Capture stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    print_schedule(schedule)
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    output = captured_output.getvalue()
    lines = output.strip().split('\n')
    
    # Should have 24 lines
    assert len(lines) == 24
    
    # Check specific lines match expected output
    assert "06:00 : total=193" in lines[6]
    assert "07:00 : total=877" in lines[7]
    assert "11:00 : total=2059" in lines[11]
    assert "19:00 : total=684" in lines[19]


if __name__ == '__main__':
    # Run with: python3 -m pytest test_scheduler.py -v
    print("Run tests with: python3 -m pytest test_scheduler.py -v")
