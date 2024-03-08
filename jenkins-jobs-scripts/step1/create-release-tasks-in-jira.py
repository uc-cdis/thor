from jira import JIRA
import re
import os
import sys
import datetime

release = os.environ["RELEASE_VERSION"]

options = {"server": "https://ctds-planx.atlassian.net"}
jira = JIRA(
    options, basic_auth=(os.environ["JIRA_SVC_ACCOUNT"].strip(), os.environ["JIRA_API_TOKEN"].strip())
)

tasks = [
    {
        "title": "0. Create RELEASE {} in JIRA".format(release),
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/create-gen3-release-in-jira/. Also to create release tasks in jira: https://jenkins.planx-pla.net/job/create-jiras-for-gen3-monthly-release/",
    },
    {
        "title": "1. Cut the integration branch integration{}".format(
            release.replace(".", "")
        ),
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/create-gen3-release-candidate-branch/",
    },
    {
        "title": "2. Check if integration branch quay images are successfully created",
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/check-quay-image/.",
    },
    {
        "title": "3. Check if integration branch images are successfully created in AWS ECR",
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/push-gen3-monthly-release-images-to-aws-ecr. Also double-check if the repos_list.txt is up-to-date.",
    },
    {
        "title": "4. Create gitops-qa PRs to deploy the integration branch to QA environments",
        "description": "Run the following command to apply the integration branch images against the target QA environment: python gen3release/env_cli.py apply -v integration2020<nn> -e ~/workspace/gitops-qa/qa-<environment>.planx-pla.net",
    },
    {
        "title": "SHARED: 5. Release testing round: automated tests and manual tests against qa envs",
        "description": 'Full list of tests tracked in the "Test Plan - Gen3 Releases" spreadsheet',
    },
    {
        "title": "6. Run load tests on jenkins-perf and store json files with results for benchmarking purposes",
        "description": "Run the following load scenarios: fence-presigned-url, sheepdog-import-clinical-metadata, metadata-service-create-and-query and metadata-service-filter-large-database. Just kick off this job https://jenkins.planx-pla.net/job/gen3-run-load-tests/ and store the result.json files accordingly.",
    },
    {
        "title": "7. Merge the integration branch into stable and tag the release",
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/merge-integration-branch-into-stable-and-tag/. Once the tag-based images are built in Quay, sanity check the images by creating a `gitops-qa` PR to deploy them against one of the QA environments.",
    },
    {
        "title": "8. Check if monthly release quay images are successfully created",
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/check-quay-image/.",
    },
    {
        "title": "9. Check if monthly release images are created in AWS ECR",
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/push-gen3-monthly-release-images-to-aws-ecr. Also double-check if the repos_list.txt is up-to-date.",
    },
    {
        "title": "10. Sanity Check the release ",
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/update-ci-env-with-latest-integration-branch/ with release version and the environment as parameters.",
    },
    {
        "title": "11. Generate release notes and publish release manifest into `cdis-manifest/<year>/<month>` folder",
        "description": "Generate the release notes with this Jenkins job: https://jenkins.planx-pla.net/job/gen3-qa-monthly-release-notes-generator. The cdis-manifest PR is tailored manually and it should include release notes and known bugs files (the PR must be labeled with `doc-only`).",
    },
    {
        "title": "SHARED: 12. Follow up with PMs to merge the PRs of respective commons",
        "description": "The `automerge` label is applied automatically to all PRs, once the PM approves it, the changes will be automatically merged and deployed to the environment. The QA engineers should monitor the PRs in case of any CI check failures.",
    },
    {
        "title": "13. Delete the integration-branch from ECR",
        "description": "Deleting the integration-branch will help lower the cost on the AWS",
    },
    {
        "title": "14. Mark the release as released",
        "description": "Kick off this job: https://jenkins.planx-pla.net/job/mark-gen3-monthly-release-as-released.",
    },
]

user_ids = ["5bedb75065b6ad1237756b4d", "5dbe0c65c32caa0daa4715f5", "712020:6bd84963-a4d5-4a67-95da-2e76641322b5"] # pragma: allowlist secret

team_members = [
    {"name": "krishnaa05", "id": user_ids[2]},
    {"name": "haraprasadj", "id": user_ids[1]},
    {"name": "atharvar", "id": user_ids[0]},
]

# set initial team member index based on the number of the month
# every month a diff team member will pick a diff task
year_and_month = re.search(r"([0-9]{4})\.([0-9]{2})", release)
team_member_index = int(year_and_month.group(2)) % len(team_members)

# get year
year = year_and_month.group(1)
# get month string
month = datetime.date(1900, int(year_and_month.group(2)), 1).strftime("%B")

PROJECT_NAME = os.environ["JIRA_PROJECT"]
RELEASE_TITLE = "{} {} Gen3 Core Release".format(month, year)
COMPONENTS = [
    {"name": "Team Catch(Err)"},
]

epic_dict = {
    "project": {
        "key": PROJECT_NAME,
    },
    "summary": RELEASE_TITLE,
    "description": "This story comprises all the tasks releated to {}".format(
        RELEASE_TITLE
    ),
    "issuetype": {"name": "Epic"},
    "assignee": {"accountId": team_members[team_member_index]["id"]},
}

new_story = jira.create_issue(fields=epic_dict)
RELEASE_EPIC = new_story.key

print("start adding tasks to " + RELEASE_TITLE)


def create_ticket(issue_dict, team_member_index):
    new_issue = jira.create_issue(fields=issue_dict)
    # jira.add_issues_to_epic(RELEASE_EPIC, [new_issue.key])
    print(
        team_members[team_member_index]["name"]
        + " has been assigned to "
        + task["title"]
    )
    return new_issue.key


for task in tasks:
    summary = task["title"]
    issue_dict = {
        "project": {
            "key": PROJECT_NAME,
        },
        "parent": {
            "key": RELEASE_EPIC,
        },
        "summary": summary,
        "description": task["description"],
        "issuetype": {
            "name": "Story"
        },
        "assignee": {
            "accountId": team_members[team_member_index]["id"]
        },
        "labels": [
            "core-product"
        ],
    }
    # Shared tasks required one ticket per team member
    if task["title"].split(":")[0] == "SHARED":
        summary = issue_dict["summary"]
        for i in range(0, len(team_members)):
            issue_dict["summary"] = summary + " - " + team_members[i]["name"]
            issue_dict["assignee"] = {"accountId": team_members[i]["id"]}
            jira_id = create_ticket(issue_dict, i)
    else:
        issue_dict["assignee"] = {"accountId": team_members[team_member_index]["id"]}
        team_member_index = (team_member_index + 1) % len(team_members)
        jira_id = create_ticket(issue_dict, team_member_index)

print("done")
