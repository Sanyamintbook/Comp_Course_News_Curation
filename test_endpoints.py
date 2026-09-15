import asyncio
import sys
import os

# Ensure the root directory is in the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.routers.dashboard import get_courses, get_competitive, get_leisure, StudentProfile

async def test_courses():
    profile = StudentProfile(
        grade_level='Grade 12',
        target_career='Engineer',
        favorite_subjects=['Mathematics', 'Chemistry', 'Physics'],
        hobbies=['Drawing', 'Chess']
    )
    print("Testing Courses...")
    try:
        results = await get_courses(profile)
        for r in results:
            print(r.get('title'), r.get('link'))
    except Exception as e:
        print(f"Error: {e}")
        
    print("\nTesting Competitive...")
    try:
        results = await get_competitive(profile)
        for r in results:
            print(r.get('title'), r.get('link'))
    except Exception as e:
        print(f"Error: {e}")
        
    print("\nTesting Leisure...")
    try:
        results = await get_leisure(profile)
        for r in results:
            print(r.get('title'), r.get('link'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_courses())
