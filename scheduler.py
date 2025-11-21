#!/usr/bin/env python3
"""Bare bones scheduler - minimal MVP implementation."""

import csv
import math
import sys


def parse_time(time_str):
    """Convert '9AM' or '7PM' to 0-23 hour format."""
    time_str = time_str.strip().upper()
    
    if time_str.endswith('AM'):
        hour = int(time_str[:-2])
        if hour == 12:
            hour = 0
    else:  # PM
        hour = int(time_str[:-2])
        if hour != 12:
            hour += 12
    
    return hour


def load_csv(filename):
    """Load customer requests from CSV."""
    customers = []
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            customers.append({
                'name': row['CustomerName'],
                'duration': int(row['AverageCallDurationSeconds']),
                'start': parse_time(row['StartTimePT']),
                'end': parse_time(row['EndTimePT']),
                'calls': int(row['NumberOfCalls']),
            })
    
    return customers


def calculate_schedule(customers):
    """Calculate agents needed for each hour."""
    # Initialize 24 hours
    schedule = {}
    for h in range(24):
        schedule[h] = {'total': 0, 'per_customer': {}}
    
    # For each customer, calculate agents per hour
    for customer in customers:
        hours_span = customer['end'] - customer['start']
        
        if hours_span <= 0:
            continue
        
        # Formula: ceil((calls / hours) * duration / 3600)
        calls_per_hour = customer['calls'] / hours_span
        agents_per_hour = math.ceil((calls_per_hour * customer['duration']) / 3600)
        
        # Assign to each hour in the customer's window
        for hour in range(customer['start'], customer['end']):
            schedule[hour]['per_customer'][customer['name']] = agents_per_hour
            schedule[hour]['total'] += agents_per_hour
    
    return schedule


def print_schedule(schedule):
    """Print the 24-hour schedule."""
    for hour in range(24):
        data = schedule[hour]
        total = data['total']
        
        if data['per_customer']:
            customers_str = ", ".join(
                f"{name}={agents}" 
                for name, agents in data['per_customer'].items()
            )
        else:
            customers_str = "none"
        
        print(f"{hour:02d}:00 : total={total} ; {customers_str}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scheduler.py <csv_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Load, calculate, and print
    customers = load_csv(filename)
    schedule = calculate_schedule(customers)
    print_schedule(schedule)


if __name__ == '__main__':
    main()
