# Thor
The Gen3 Release Orchestrator

![GitHub Logo](/images/logo.png)
_Image by [cromaconceptovisual](https://pixabay.com/users/cromaconceptovisual-4595909/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=4898879) from [Pixabay](https://pixabay.com/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=4898879)_

# Overview

this new tool should help us achieve a fully-automated hands-free Gen3 release. We need to eliminate “toil” from our day-to-day tasks so we can focus on project-specific tasks, maintenance of our CI/CD pipelines, expansion of the Gen3-QA framework, test coverage and innovation.

Manual and repetitive work is boring and error-prone, as software engineers, we can do better than this.


# Features

This new tool (THOR) has the following features:
* RESTful API to start the release flow and track the status of each step
* Coordinate each and every step of the Gen3 Release by working with:
  * The Jenkins API (kicking off Jenkins jobs and tracking its results)
  * Executing gen3-release-utils scripts & the gen3release-sdk CLI
  * Interacting with JIRA and Slack APIs
* Provide FULL transparency to the Gen3 Release process through a friendly GUI that should help any Project Manager (PM) observe the progress of the releases throughout the environments they own.
* Facilitate parameterization of our release automation and make it more flexible (e.g., change cadence / time-frame between releases).

# Architectural diagrams

TBD
