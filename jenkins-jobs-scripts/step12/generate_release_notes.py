import calendar
import csv
import datetime
import fileinput
import glob
import os
import requests
import subprocess

from pathlib import Path


def get_previous_year_month(year, month):
    current_date = datetime.date(year, month, 1)
    previous_month = current_date.replace(day=1) - datetime.timedelta(days=1)
    return (previous_month.year, previous_month.month)


def get_second_friday(year, month):
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    monthcal = c.monthdatescalendar(year, month)
    fridays = [day for week in monthcal for day in week if day.weekday() == calendar.FRIDAY]
    return fridays[1]


def get_release_name(release_version):
    release_names_file = Path(__file__).parent.parent.parent / "release_names.csv"
    with open(release_names_file, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == release_version:
                return row[1]


def get_release_manifest(year, month):
    month_str = str(month).zfill(2)
    manifest_url = f"https://raw.githubusercontent.com/uc-cdis/cdis-manifest/master/releases/{year}/{month_str}/manifest.json"
    res = requests.get(manifest_url)
    if res.status_code == 200:
        return res.text
    else:
        raise Exception(f"Failed to fetch the previous manifest. Error code: {res.status_code}")


def generate_repo_release_notes(release_version, repo, start_date, end_date):
    command = [
        "gen3git", "--repo", f"uc-cdis/{repo}", "--github-access-token",
        os.environ.get("GITHUB_TOKEN"), "--from-date", f"{start_date}", "gen",
        "--to-date", f"{end_date}", "--file-name", f"{repo}_release_notes", "--markdown"
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, _ = process.communicate()  # Wait for process to finish
    print(output)


def generate_release_notes(release_version):
    repo_list_file = Path(__file__).parent.parent.parent / "repo_list.txt"
    release_name = get_release_name(release_version)
    release = f"Core Gen3 Release {release_version} ({release_name})"

    print("---- Fetching previous release manifest ----")
    curr_year = int(release_version.split(".")[0])
    curr_month = int(release_version.split(".")[1])
    prev_year, prev_month = get_previous_year_month(curr_year, curr_month)
    prev_prev_year, prev_prev_month = get_previous_year_month(prev_year, prev_month)
    prev_manifest = get_release_manifest(prev_year, prev_month)

    print("---- Update release version in the manifest and save to file ----")
    with open("manifest.json", "w") as f:
        f.write(prev_manifest.replace(f"{prev_year}.{str(prev_month).zfill(2)}", release_version))

    print("---- Compute start and end date ----")
    start_date = str(get_second_friday(prev_prev_year, prev_prev_month))
    end_date = str(get_second_friday(prev_year, prev_month))
    print(f"Start date - {start_date}")
    print(f"End date - {end_date}")

    print(f"---- Generating release notes for {release} ----")
    with open(repo_list_file, "r") as f:
        repos = [s.strip() for s in f.readlines()]

    for repo in repos:
        try:
            print(f"---- ---- Generating release notes for {repo} repo ----")
            generate_repo_release_notes(release_version, repo, start_date, end_date)
        except Exception:
            pass

    print("---- Combining repo release notes ----")
    files = sorted(glob.glob(f"{Path(__file__).parent.absolute()}/*.md"))
    all_notes = ""
    for file in files:
        with open(file, "r") as f:
            notes = f.read()
            if "####" in notes:
                print("---- ----- Getting notes from {file} ----")
                all_notes += notes
    with open('gen3-release-notes.md', 'w') as f:
        print(all_notes)
        f.write(all_notes)


if __name__ == "__main__":
    generate_release_notes(os.environ.get("RELEASE_VERSION"))
