import requests
from requests.auth import HTTPBasicAuth
import json
import logging
import sys

class Integration(object):

    def __init__(self, url_upsource="", login_upsource="", pass_upsource="", url_onevizion="", login_onevizion="", pass_onevizion="", project_name="", project_onevizion=""):
        self.url_upsource = url_upsource
        self.login_upsource = login_upsource
        self.pass_upsource = pass_upsource
        self.url_onevizion = url_onevizion
        self.login_onevizion = login_onevizion
        self.pass_onevizion = pass_onevizion
        self.project_name = project_name
        self.project_onevizion = project_onevizion
        
        self.auth_upsource = HTTPBasicAuth(login_upsource, pass_upsource)
        self.auth_onevizion = HTTPBasicAuth(login_onevizion, pass_onevizion)
        self.headers = {'Content-type':'application/json','Content-Encoding':'utf-8'}

        self.revision_list()
        self.create_review()

    #Returns the list of revisions in a given project
    def revision_list(self):
        log = self.get_logger()
        log.info('Started upsource integration')
        log.info('Started updating the status of issues')

        skip_number = 0
        while skip_number != None:
            url = self.url_upsource + '~rpc/getRevisionsList'
            data = {"projectId":self.project_name, "limit":1, "skip":skip_number}
            answer = requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
            response = answer.json()
            readble_json = response['result']

            if 'revision' in readble_json:
                skip_number = skip_number + 1
                revision_id = readble_json['revision'][0]['revisionId']

                review_info = self.review_info(revision_id)

                if review_info == [{}]:
                    print('This revision has no review')
                else:
                    review_title = self.get_issue_title(review_info[0]['reviewInfo']['title'])
                    review_status = review_info[0]['reviewInfo']['state']
                    review_branche = self.revision_branche(revision_id)

                    self.check_status(review_title, review_status, review_branche)
            else:
                skip_number = None

        log.info('Finished updating the status of issues')

    #Returns short review information for a set of revisions
    def review_info(self, revision_id):
        url = self.url_upsource + '~rpc/getRevisionReviewInfo'
        data = {"projectId":self.project_name, "revisionId":revision_id}
        answer = requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
        response = answer.json()
        readble_json = response['result']['reviewInfo']
        return readble_json

    #Returns issue title
    def get_issue_title(self, issue_title):
        if 'Revert \"' in issue_title:
            return None
        elif 'Review of ' in issue_title:
            return None
        elif 'Merge branch \"' in issue_title:
            return None
        elif 'Merge branch \'master\' into ' in issue_title:
            return None
        else:
            return issue_title[issue_title.find('') : issue_title.find(' ')]
    
    #Returns the list of branches a revision is part of
    def revision_branche(self, revision_id):
        url = self.url_upsource + '~rpc/getRevisionBranches'
        data = {"projectId":self.project_name, "revisionId":revision_id}
        answer = requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
        response = answer.json()
        readble_json = response['result']['branchName']
        return readble_json
    
    #Checks review status and run update_issue
    def check_status(self, issue, status, branch):
        log = self.get_logger()

        if issue == 'None':
            return None
        else:
            if status == 2 and branch == 'master':
                self.update_issue(issue, 'Ready for Merge')
            elif status == 2 and branch != 'master':
                self.update_issue(issue, 'Ready for Test')
            else: log.info('Review ' + str(issue) + ' is not yet closed')

    #Updates issue status if review status = 2 (closed)
    def update_issue(self, issue, status):
        log = self.get_logger()

        issue_title = self.check_issue(issue)
        if issue_title['VQS_IT_STATUS'] == 'Ready for Review' and status == 'Ready for Merge':
            url = self.url_onevizion + 'api/v3/trackors/' + str(issue_title['TRACKOR_ID'])
            data = {"VQS_IT_STATUS":status}
            requests.put(url, headers=self.headers, data=json.dumps(data), auth=self.auth_onevizion)
            log.info('Issue ' + issue_title['TRACKOR_KEY'] + ' updated status to "Ready for Merge"')
        elif issue_title['VQS_IT_STATUS'] == 'Ready for Review' and status == "Ready for Test":
            url = self.url_onevizion + 'api/v3/trackors/' + str(issue_title['TRACKOR_ID'])
            data = {"VQS_IT_STATUS":status}
            requests.put(url, headers=self.headers, data=json.dumps(data), auth=self.auth_onevizion)
            log.info('Issue ' + issue_title['TRACKOR_KEY'] + ' updated status to "Ready for Test"')
        else: log.info('Issue ' + issue_title['TRACKOR_KEY'] + ' has already been updated')

    #Checks issue status
    def check_issue(self, issue):
        if issue == '':
            url = self.url_onevizion + 'api/v3/trackor_types/Issue/trackors'
            params = {"fields":"TRACKOR_KEY, VQS_IT_STATUS, Product.TRACKOR_KEY", "Product.TRACKOR_KEY":self.project_onevizion}
            answer = requests.get(url, headers=self.headers, params=params, auth=self.auth_onevizion)
            response = answer.json()
            return response
        else:
            url = self.url_onevizion + 'api/v3/trackor_types/Issue/trackors'
            params = {"fields":"TRACKOR_KEY, VQS_IT_STATUS, Product.TRACKOR_KEY", "TRACKOR_KEY":issue, "Product.TRACKOR_KEY":self.project_onevizion}
            answer = requests.get(url, headers=self.headers, params=params, auth=self.auth_onevizion)
            response = answer.json()
            return response

    #Creates review if issue status = 'Ready for Review'
    def create_review(self):
        log = self.get_logger()
        log.info('Started creating reviews')

        for issue in self.check_issue(''):
            if issue['VQS_IT_STATUS'] != "Ready for Review":
                log.info('No need to create a review for this issue - ' + str(issue['TRACKOR_KEY']))
            else:
                for revision_id in self.filtered_revision_list(issue['TRACKOR_KEY']):
                    review_info = self.review_info(revision_id['revisionId'])
                    
                    if review_info != [{}]:
                        log.info('Review already exists')
                    else:
                        url = self.url_upsource + '~rpc/createReview'
                        data = {"projectId":self.project_name, "revisions":revision_id['revisionId']}
                        requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
                        log.info('Review for ' + str(issue['TRACKOR_KEY']) + ' created')
                        
                        self.add_review_label(review_info[0]['reviewInfo']['reviewId']['reviewId'])
                        log.info('Label "ready for review" added to review ' + str(issue['TRACKOR_KEY']))

                        self.delete_reviewer(review_info[0]['reviewInfo']['reviewId']['reviewId'])
                        log.info('Default reviewer deleted')

                        for file_extension in self.get_revision_file_extension(revision_id['revisionId']):

                            if file_extension['fileIcon'][5:] == 'sql':
                                self.add_reviewer(review_info[0]['reviewInfo']['reviewId']['reviewId'], "840cb243-75a1-4bba-8fad-5859779db1df")
                                log.info('Mikhail Knyazev added in reviewers')

                            elif file_extension['fileIcon'][5:] == 'java':
                                self.add_reviewer(review_info[0]['reviewInfo']['reviewId']['reviewId'], "c7b9b297-d3e0-4148-af30-df20d676a0fd")
                                log.info('Dmitry Nesmelov added in reviewers')

                            elif file_extension['fileIcon'][5:] == ['js', 'css', 'html']:
                                self.add_reviewer(review_info[0]['reviewInfo']['reviewId']['reviewId'], "9db3e4ca-5167-46b8-b114-5126af78d41c")
                                log.info('Alex Yuzvyak added in reviewers')

        log.info('Finished creating reviews')
        log.info('Finished upsource integration')

    #Returns the list of revisions that match the given search query
    def filtered_revision_list(self, issue):
        url = self.url_upsource + '~rpc/getRevisionsListFiltered'
        data = {"projectId":self.project_name, "limit":1, "query":issue}
        answer = requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
        response = answer.json()
        readble_json = response['result']['revision']
        return readble_json

    #Returns the list of changes (files that were added, removed, or modified) in a revision
    def get_revision_file_extension(self, revision_id):
        url = self.url_upsource + '~rpc/getRevisionChanges'
        data = {"revision":{"projectId":self.project_name, "revisionId":revision_id}, "limit":10}
        answer = requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
        response = answer.json()
        readble_json = response['result']['diff']
        unique_file_extension = {file_extension['fileIcon']:file_extension for file_extension in readble_json}.values()
        return unique_file_extension

    #Removes a default reviewer from a review
    def add_reviewer(self, review_id, user_id):
        url = self.url_upsource + '~rpc/addParticipantToReview'
        data = {"reviewId":{"projectId":self.project_name, "reviewId":review_id}, "participant":{"userId":user_id, "role":2}}
        answer = requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
        response = answer.json()
        return response

    #Removes a default reviewer from a review
    def delete_reviewer(self, review_id):
        url = self.url_upsource + '~rpc/removeParticipantFromReview'
        data = {"reviewId":{"projectId":self.project_name, "reviewId":review_id}, "participant":{"userId":"653c3d2e-394f-4c6b-8757-3e070c78c910", "role":2}}
        answer = requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
        response = answer.json()
        return response

    #Adds a label to a review
    def add_review_label(self, review_id):
        url = self.url_upsource + '~rpc/addReviewLabel'
        data = {"projectId":self.project_name, "reviewId":{"projectId":self.project_name, "reviewId":review_id}, "label":{"id":"ready", "name":"ready for review"}}
        answer = requests.post(url, headers=self.headers, data=json.dumps(data), auth=self.auth_upsource)
        response = answer.json()
        return response

    #Returns logging to stdout
    def get_logger(self, name=__file__, file='log.txt', encoding='utf-8'):
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)-8s %(message)s')
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(formatter)
        log.addHandler(sh)
        return log
