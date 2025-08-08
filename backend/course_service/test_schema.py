#!/usr/bin/env python3
"""
Test script to verify schema is working correctly
"""
import sys
import os
sys.path.insert(0, '.')

from app.schemas import CourseCreate, Course

# Test the schema
test_data = {
    "title": "Test Course",
    "description": "A test course", 
    "instructor": "Test Instructor",
    "category": "Test",
    "level": "Beginner",
    "duration": "4 weeks",
    "price": 29.99,
    "rating": 4.5,
    "students_enrolled": 100
}

try:
    course = CourseCreate(**test_data)
    print("✅ Schema validation successful!")
    print(f"Course: {course}")
    print(f"Fields: {list(course.model_fields.keys())}")
except Exception as e:
    print(f"❌ Schema validation failed: {e}")
    sys.exit(1) 