# run_tests_with_coverage.py
import subprocess
import sys
import webbrowser
import os
def run_tests():
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "test_water_norm.py",
        "-v",
        "--cov=water_norm",
        "--cov=weather_service",
        "--cov-report=html",
        "--cov-report=term"
    ])
    if os.path.exists("htmlcov/index.html"):
        print("\nОтчет о покрытии: htmlcov/index.html")
        webbrowser.open("file://" + os.path.abspath("htmlcov/index.html"))

    return result.returncode
if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)