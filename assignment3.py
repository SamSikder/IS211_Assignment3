import csv
import re
import argparse
import requests
from collections import defaultdict
from datetime import datetime


def download_file(url):
    """Downloads the log file from the given URL"""
    response = requests.get(url)
    response.raise_for_status()

    file_content = response.text.splitlines()
    return file_content


def process_csv(data):
    """Processes CSV data and returns structured logs"""
    logs = []
    csv_reader = csv.reader(data)

    for row in csv_reader:
        if len(row) != 5:
            continue
        logs.append({
            "path": row[0],
            "datetime": row[1],
            "browser": row[2],
            "status": row[3],
            "size": row[4]
        })

    return logs


def count_image_requests(logs):
    """Counts image requests and calculates percentage"""
    image_pattern = re.compile(r".*\.(jpg|gif|png)$", re.IGNORECASE)

    total_requests = len(logs)
    image_requests = sum(1 for log in logs if image_pattern.match(log["path"]))

    percentage = (image_requests / total_requests) * 100 if total_requests > 0 else 0
    print(f"Image requests account for {percentage:.2f}% of all requests")


def find_most_popular_browser(logs):
    """Finds the most used browser"""
    browser_counts = defaultdict(int)

    for log in logs:
        if "Firefox" in log["browser"]:
            browser_counts["Firefox"] += 1
        elif "Chrome" in log["browser"]:
            browser_counts["Chrome"] += 1
        elif "MSIE" in log["browser"] or "Trident" in log["browser"]:
            browser_counts["Internet Explorer"] += 1
        elif "Safari" in log["browser"] and "Chrome" not in log["browser"]:
            browser_counts["Safari"] += 1

    if browser_counts:
        most_popular = max(browser_counts, key=browser_counts.get)
        print(f"The most popular browser is: {most_popular} ({browser_counts[most_popular]} hits)")
    else:
        print("No valid browser data found.")


def count_hits_by_hour(logs):
    """Counts hits per hour and sorts them"""
    hour_counts = defaultdict(int)

    for log in logs:
        try:
            access_time = datetime.strptime(log["datetime"], "%m/%d/%Y %H:%M:%S")
            hour_counts[access_time.hour] += 1
        except ValueError:
            continue

    sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)

    for hour, count in sorted_hours:
        print(f"Hour {hour:02d} has {count} hits")


def main():
    parser = argparse.ArgumentParser(description="Process a web log file")
    parser.add_argument("--url", required=True, help="URL to the web log file")
    args = parser.parse_args()

    try:
        print("Downloading file...")
        file_data = download_file(args.url)
        print("Processing file...")
        logs = process_csv(file_data)

        count_image_requests(logs)
        find_most_popular_browser(logs)
        count_hits_by_hour(logs)

    except requests.RequestException as e:
        print(f"Error downloading the file: {e}")


if __name__ == "__main__":
    main()
