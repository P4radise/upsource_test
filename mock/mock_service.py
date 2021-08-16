from flask import Flask, request, make_response
from flask_httpauth import HTTPTokenAuth
import constants
import json
import re


app = Flask(__name__)
token_auth = HTTPTokenAuth('Bearer')

@token_auth.verify_token
def verify_token(token):
    with open(constants.SETTINGS_FILENAME, "rb") as PFile:
        password_data = json.loads(PFile.read().decode('utf-8'))

    if token == password_data['tokenUpsource']:
        return token

@app.route('/~rpc/getRevisionsListFiltered',  methods=['POST'])
@token_auth.login_required
def get_filtered_revision_list():
    query = request.get_json()['query']

    if query not in (constants.Issue.IHUB_146144.issue_id, constants.Issue.DEPL_125306.issue_id):
        return make_response(f'Revision for {query} not found', constants.StatusCode.EXCEPTION.value)

    if query == constants.Issue.IHUB_146144.issue_id:
        json_data = {'result': {'revision': [{'revisionId': constants.Review.BLNK_CR_128.review_id, 
                'revisionCommitMessage': f'{constants.Issue.IHUB_146144.issue_id} {constants.Issue.IHUB_146144.summary}\n'}]}}
    elif query == constants.Issue.DEPL_125306.issue_id:
        json_data = {'result': {'revision': [{'revisionId': constants.Review.BLNK_CR_127.review_id, 
                'revisionCommitMessage': f'{constants.Issue.DEPL_125306.issue_id} {constants.Issue.DEPL_125306.summary}\n'}]}}
    else:
        json_data = {'result': {'query': f'{query}'}}

    return json_data

@app.route('/~rpc/closeReview',  methods=['POST'])
@token_auth.login_required
def close_review():
    review_id = request.get_json()['reviewId']['reviewId']

    if review_id not in constants.SUPPORTED_REVIEWS:
        return make_response(f'constants.Review {review_id} not found', constants.StatusCode.EXCEPTION.value)

    return review_id

@app.route('/~rpc/getBranches',  methods=['POST'])
@token_auth.login_required
def get_branch():
    query = request.get_json()['query']

    if query == constants.Issue.IHUB_146144.issue_id:
        json_data =  {'result': {'defaultBranch': 'master'}}
    elif query == constants.Issue.DEPL_125306.issue_id:
        json_data = {'result': {'branch': [{'name': constants.Issue.DEPL_125306.issue_id}]}}
    else:
        return make_response(f'Branch {query} not found', constants.StatusCode.EXCEPTION.value)

    return json_data

@app.route('/~rpc/startBranchTracking',  methods=['POST'])
@token_auth.login_required
def start_branch_tracking():
    review_id = request.get_json()['reviewId']['reviewId']

    if review_id not in constants.SUPPORTED_REVIEWS:
        return make_response(f'constants.Review {review_id} not found', constants.StatusCode.EXCEPTION.value)

    return review_id

@app.route('/~rpc/findUsers',  methods=['POST'])
@token_auth.login_required
def find_users():
    pattern = request.get_json()['pattern']

    if pattern == constants.User.ASMOISEENKO.user_name:
        json_data = {'result': {'infos': [{'userId': constants.User.ASMOISEENKO.user_id}]}}
    elif pattern == constants.User.VADIM.user_name:
        json_data = {'result': {'infos': [{'userId': constants.User.VADIM.user_id}]}}
    elif pattern == constants.User.ILYA_EMELYANOV.user_name:
        json_data = {'result': {'infos': [{'userId': constants.User.ILYA_EMELYANOV.user_id}]}}
    else:
        return make_response(f'Cannot resolve pattern {pattern}', constants.StatusCode.EXCEPTION.value)

    return json_data

@app.route('/~rpc/updateParticipantInReview',  methods=['POST'])
@token_auth.login_required
def update_participant_status():
    review_id = request.get_json()['reviewId']['reviewId']
    user_id = request.get_json()['userId']

    if review_id not in constants.SUPPORTED_REVIEWS:
        return make_response(f'constants.Review {review_id} not found', constants.StatusCode.EXCEPTION.value)

    if user_id not in constants.SUPPORTED_USERS:
        return make_response(f'Cannot resolve user id {user_id}', constants.StatusCode.EXCEPTION.value)

    return user_id

@app.route('/~rpc/addParticipantToReview',  methods=['POST'])
@token_auth.login_required
def add_reviewer():
    review_id = request.get_json()['reviewId']['reviewId']
    user_id = request.get_json()['participant']['userId']

    if review_id not in constants.SUPPORTED_REVIEWS:
        return make_response(f'constants.Review {review_id} not found', constants.StatusCode.EXCEPTION.value)

    if user_id not in constants.SUPPORTED_USERS:
        return make_response(f'Cannot resolve user id {user_id}', constants.StatusCode.EXCEPTION.value)

    return user_id

@app.route('/~rpc/removeParticipantFromReview',  methods=['POST'])
@token_auth.login_required
def remove_reviewer():
    review_id = request.get_json()['reviewId']['reviewId']
    user_id = request.get_json()['participant']['userId']

    if review_id not in constants.SUPPORTED_REVIEWS:
        return make_response(f'constants.Review {review_id} not found', constants.StatusCode.EXCEPTION.value)

    if user_id not in constants.SUPPORTED_USERS:
        return make_response(f'Cannot resolve user id {user_id}', constants.StatusCode.EXCEPTION.value)

    return user_id

@app.route('/~rpc/getReviews',  methods=['POST'])
@token_auth.login_required
def get_reviews():
    query = request.get_json()['query']

    if query not in (constants.Issue.IHUB_146144.issue_id, constants.Issue.DEPL_125306.issue_id, constants.Review.BLNK_CR_127.review_key, constants.Review.BLNK_CR_128.review_key, 'state: open'):
        return make_response(f'constants.Review for {query} not found', constants.StatusCode.EXCEPTION.value)

    with open(constants.SETTINGS_FILENAME, 'rb') as PFile:
        settings_url = json.loads(PFile.read().decode('utf-8'))['urlOneVizion']
    blnk_cr_127_review_json_data = json.loads(re.sub('settings_url/', settings_url, json.dumps(constants.BLNK_CR_127_REVIEW_JSON_DATA)))
    

    if query == constants.Issue.IHUB_146144.issue_id:
        json_data = {'result': {'hasMore': False, 'totalCount': 0}}
    elif query == constants.Review.BLNK_CR_128.review_key:
        json_data = {'result':{'reviews':[constants.BLNK_CR_128_REVIEW_JSON_DATA]}}
    elif query in (constants.Issue.DEPL_125306.issue_id, constants.Review.BLNK_CR_127.review_key):
        json_data = {'result':{'reviews':[blnk_cr_127_review_json_data]}}
    elif query == 'state: open':
        json_data = {'result':{'reviews':[blnk_cr_127_review_json_data, constants.BLNK_CR_128_REVIEW_JSON_DATA]}}
    else:
        json_data = {'result': {'hasMore': False, 'totalCount': 0}}

    return json_data

@app.route('/~rpc/renameReview',  methods=['POST'])
@token_auth.login_required
def rename_review():
    review_id = request.get_json()['reviewId']['reviewId']

    if review_id not in constants.SUPPORTED_REVIEWS:
        return make_response(f'constants.Review {review_id} not found', constants.StatusCode.EXCEPTION.value)

    return review_id

@app.route('/~rpc/createReview',  methods=['POST'])
@token_auth.login_required
def create_review():
    revisions = request.get_json()['revisions']

    if revisions == constants.Review.BLNK_CR_128.review_id:
        json_data = {'result':{'reviews':[constants.BLNK_CR_128_REVIEW_JSON_DATA]}}
    elif revisions == constants.Review.BLNK_CR_127.review_id:
        return make_response(f'Cannot create review because revision {revisions} is already in review constants.Review(reviewId=ReviewId[{constants.Review.BLNK_CR_127.review_id}], \
                                title=\'{constants.Issue.DEPL_125306.issue_id} {constants.Issue.DEPL_125306.summary}\'', constants.StatusCode.EXCEPTION.value)
    else:
        return make_response(f'Cannot resolve revision {revisions} in project blank', constants.StatusCode.EXCEPTION.value)

    return json_data

@app.route('/~rpc/editReviewDescription',  methods=['POST'])
@token_auth.login_required
def update_review_description():
    review_id = request.get_json()['reviewId']['reviewId']

    if review_id not in constants.SUPPORTED_REVIEWS:
        return make_response(f'constants.Review {review_id} not found', constants.StatusCode.EXCEPTION.value)

    return review_id


if __name__ == '__main__':
    app.run(debug=True)