import csv
import datetime
import glob
import os
import subprocess

from pathlib import Path
from zoneinfo import ZoneInfo

from thor.dao.release_dao import (
    get_release_start_time,
    get_release_end_time,
    release_id_lookup_class,
)

def get_release_name(release_version):
    release_names_file = Path(__file__).parent.parent.parent / "release_names.csv"
    with open(release_names_file, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == release_version:
                return row[1]


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

    print(
        "---- Fetching release start and end time "
        "from database ----"
    )

    release_id = (
        release_id_lookup_class()
        .release_id_lookup(release_version)
    )

    if release_id is None:
        raise ValueError(
            f"Release {release_version} "
            f"was not found in the database."
        )

    release_start_time = get_release_start_time(
        release_id
    )

    release_end_time = get_release_end_time(
        release_id
    )

    if release_start_time is None:
        raise ValueError(
            f"release_start_time is not set for "
            f"release {release_version}"
        )

    if release_end_time is None:
        raise ValueError(
            f"release_end_time is not set for "
            f"release {release_version}"
        )

    central = ZoneInfo("America/Chicago")

    start_date = (
        release_start_time
        .astimezone(central)
        .strftime("%Y-%m-%d")
    )

    end_date = (
        (release_end_time + datetime.timedelta(days=1))
        .astimezone(central)
        .strftime("%Y-%m-%d")
    )

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
    files = sorted(glob.glob("/src/workspace/12/*.md"))
    all_notes = f"# {release}\n"
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
