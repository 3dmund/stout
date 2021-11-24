# main.py

from flask import Blueprint, render_template, redirect, url_for, request
# from flask import Flask, abort, request, jsonify, g, url_for, redirect, render_template, flash

from flask_login import login_required, current_user
from project import app
from requests import post, get

main = Blueprint('main', __name__)

EMAIL = 'stout@gmail.com'
PASSWORD = 'password'

@main.route('/')
@login_required
def index():
    # TODO: check if we have token in db and redirect to connect utility page if we don't

    unique_id = request.args.get('unique_id')

    if not unique_id:
        return redirect(url_for('main.connect_utility'))

    # TODO: query unique_account_ids here
    # unique_account_ids = ['123', '456']

    energy_account_ids = get_energy_accounts(unique_id)







@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/connect/utility')
def connect_utility():
    redirect_url = '{STOUT_URL}/redirect'.format(STOUT_URL=app.config.get('STOUT_URL'))
    return render_template('connect_utility.html', redirect_url=redirect_url)

@main.route('/pelm/authorize')
def connect_utility_post():
    print("authorizing user")
    url = "{host}/auth/consumer".format(host=app.config.get('PELM_API_URL'))
    print(url)

    # headers = {
    # 	'Authorization': 'Basic {}'.format(get_pelm_auth_token())
    # }
    #
    # response = post(url=url, headers=headers)
    # print(response)
    # print(type(response))
    # # print(response.get_data)

    token = get_pelm_auth_token()
    print(f"token: {token}")

    url_with_params = "{url}?auth_token={auth_token}&redirect_url={redirect_url}".format(
        url=url,
        auth_token=get_pelm_auth_token(),
        redirect_url="{}/stout/redirect".format(app.config.get("STOUT_URL"))
    )

    return redirect(url_with_params)

@main.route('/redirect', methods=['GET'])
def pelm_redirect():
    print("hit redirect")
    unique_id = request.args.get('unique_id')
    print(f"unique_id: {unique_id}")

    redirect_url = '{url}?unique_id={unique_id}'.format(
        url=url_for('main.index'),
        unique_id=unique_id
    )

    # return unique_id

    return redirect(redirect_url)



def get_pelm_auth_token():
    print("getting pelm auth token")
    url = '{PELM_API_URL}/auth/refresh'.format(
        PELM_API_URL=app.config.get('PELM_API_URL'),
    )

    data = {
        'email': EMAIL,
        'password': PASSWORD
    }

    response = post(url, data=data)
    response_json = response.json()

    print(response_json)
    return response_json.get('auth_token')


def get_energy_accounts(unique_id):
    print("get energy accounts")
    url = '{PELM_API_URL}/accounts/get?unique_id={unique_id}&auth_token={auth_token}'.format(
        PELM_API_URL=app.config.get('PELM_API_URL'),
        unique_id=unique_id,
        auth_token=get_pelm_auth_token()
    )

    # headers = {
    #     'Authorization': 'Basic {}'.format(get_pelm_auth_token())
    # }

    response = get(url)

    print("response")
    print(response)
    print(response.json())
    print(response.content)

    return response.content

