import asyncio

from app.error_analysis.analyzer import analyze_error
from app.models import ErrorLog


async def main():
    error = ErrorLog(
        endpoint="/test",
        http_method="GET",
        exception_type="ValueError",
        error_message="This is a test error",
        stack_trace="""
Traceback (most recent call last):
    raise ValueError("This is a test error")
ValueError: This is a test error
""",
    )

    result = await analyze_error(error)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
