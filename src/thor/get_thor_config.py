from json_templates import *


def get_thor_config(releaseName):
    json_tmp = JsonTemplates()
    result = json_tmp.load("thor_config.json")

    yearMonth = releaseName.replace(".", "")
    integrationBranch = f"integration{yearMonth}"

    if result[0]:
        new_config = json_tmp.generate(
            {
                "release_name": f"{releaseName}",
                "integration_branch": f"{integrationBranch}",
            }
        )

    return new_config
