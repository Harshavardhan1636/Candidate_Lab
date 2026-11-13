"""Readable names for known demonstration records; identifiers stay unchanged."""
import re

SAMPLE_PROFILES = [
    'Python Developer - Inventory APIs', 'Python Developer - Data Pipelines',
    'Frontend Developer - React Dashboard', 'Data Analyst - Retail Reporting',
    'Backend Developer - Django Services', 'Java Developer - Order Services',
    'Machine Learning Developer - Data Analysis', 'Frontend Developer - Product Pages',
    'Python Developer - API Deployment', 'Data Analyst - Business Reporting',
    'Frontend Developer - Accessible Forms', 'Backend Developer - Database Services',
]

def job_name(value):
    if re.fullmatch(r'Evaluation Engineer\s+\d+', value, re.I):return 'Python Backend Engineer'
    if re.fullmatch(r'Workflow role\s+\d+', value, re.I):return 'Python Application Developer'
    return value

def profile_name(value):
    match=re.fullmatch(r'Research profile\s+(\d+)',value,re.I)
    if match and 1<=int(match[1])<=len(SAMPLE_PROFILES):return SAMPLE_PROFILES[int(match[1])-1]
    if re.fullmatch(r'Learning profile\s+\d+',value,re.I):return 'Python Developer - Project Experience'
    if re.fullmatch(r'Browser profile\s+\d+',value,re.I):return 'Python Developer - API Testing'
    return value
