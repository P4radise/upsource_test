from install_package import Package
import json


with open('settings.json', "rb") as PFile:
    setting_data = json.loads(PFile.read().decode('utf-8'))

required_package = setting_data["packages"]
Package(required_package).install()


from jsonschema import validate
from integration_log import build_logger
from upsource_integration import Issue, IssueTask, Review, Integration, IntegrationError
import re


with open('settings_schema.json', "rb") as PFile:
    data_schema = json.loads(PFile.read().decode('utf-8'))

try:
    validate(instance=setting_data, schema=data_schema)
except Exception as e:
    raise IntegrationError(f'Incorrect value in the settings file\n{str(e)}')

url_upsource = setting_data["urlUpsource"]
user_name_upsource = setting_data["userNameUpsource"]
token_upsource = setting_data["tokenUpsource"]
products = setting_data["products"]
reviewers = setting_data["reviewers"]

if re.search('https', setting_data["urlOneVizion"]) is None:
    url_onevizion_without_protocol = re.sub("^http://", "", setting_data["urlOneVizion"][:-1])
else:
    url_onevizion_without_protocol = re.sub("^https://", "", setting_data["urlOneVizion"][:-1])

url_onevizion = setting_data["urlOneVizion"]
login_onevizion = setting_data["loginOneVizion"]
pass_onevizion = setting_data["passOneVizion"]
issue_trackor_type = setting_data["issueTrackorType"]
issue_task_trackor_type = setting_data["issueTaskTrackorType"]

issue_statuses = setting_data["issueStatuses"]
issue_fields = setting_data["issueFields"]
issue_task_fields = setting_data["issueTaskFields"]
issue_task_types = setting_data["issueTaskTypes"]
issue_task_statuses = setting_data["issueTaskStatuses"]

logger = build_logger()
issue = Issue(url_onevizion_without_protocol, login_onevizion, pass_onevizion,
              issue_trackor_type, issue_statuses, issue_fields)
issue_task = IssueTask(url_onevizion_without_protocol, login_onevizion, pass_onevizion, issue_trackor_type, issue_task_trackor_type,
                       issue_fields, issue_task_fields, issue_task_types, issue_task_statuses)
review = Review(url_upsource, user_name_upsource, token_upsource, reviewers, logger)
integration = Integration(url_onevizion, products, issue, issue_task, review, logger)

integration.start_integration()