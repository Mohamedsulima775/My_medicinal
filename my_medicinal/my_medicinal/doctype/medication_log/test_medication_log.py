# Copyright (c) 2025, mohammedsuliman and Contributors
# See license.txt

# import frappe
#from frappe.tests.utils import FrappeTestCase


#class TestMedicationLog(FrappeTestCase):
#	pass


# Test medication log

import frappe
from datetime import datetime, timedelta

def test_log_medication():
    """Test logging medication"""
    
    # Log taken medication
    result = log_medication(
        patient_id="PAT-00001",
        medication_schedule_id="MED-Ahmed-0001",
        scheduled_time="2025-01-15 08:00:00",
        status="Taken",
        actual_time="2025-01-15 08:05:00",
        notes="Taken with breakfast"
    )
    
    print(f"Log created: {result['log_id']}")
    print(f"On time: {result['was_on_time']}")
    print(f"Time difference: {result['time_difference']} minutes")


def test_adherence_stats():
    """Test adherence calculation"""
    
    stats = get_adherence_stats("PAT-00001", days=30)
    
    print(f"Total doses: {stats['total_doses']}")
    print(f"Taken: {stats['taken']}")
    print(f"Missed: {stats['missed']}")
    print(f"Adherence rate: {stats['adherence_rate']}%")
    print(f"On-time rate: {stats['on_time_rate']}%")


def test_missed_doses():
    """Test getting missed doses"""
    
    missed = get_missed_doses("PAT-00001")
    
    print(f"Missed doses: {len(missed)}")
    for dose in missed:
        print(f"- {dose['medication_name']} at {dose['scheduled_time']} ({dose['hours_ago']} hours ago)")


# Run tests
test_log_medication()
test_adherence_stats()
test_missed_doses()