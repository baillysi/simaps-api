from wsmain.app import app
import json

app.testing = True

# hike data payload
payload = {
    'name': 'hike_test',
    'distance': 10.5,
    'elevation': 500,
    'difficulty': 2,
    'duration': 5400,
    'description': 'hike_description',
    'zone_id': 1,
    'journey': {
        'id': 1,
        'name': 'boucle'
    },
}


def test_should_return_hello_world():
    """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is requested (GET)
        THEN check that the response is valid
    """
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Hello world'


def test_should_post_hike_data():
    """
        GIVEN a Flask application configured for testing
        WHEN the '/hikes' page is posted to (POST)
        THEN check that a '201' (Created) status code is returned
    """
    response = app.test_client().post(
        '/hikes',
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 201


def test_should_update_hike_data():
    """
        GIVEN a Flask application configured for testing
        WHEN the '/hikes' page is put to (PUT)
        THEN check that a '200' (OK) status code is returned
    """
    response = app.test_client().get(
        '/hikes/latest',
        headers={'Content-Type': 'application/json'},
    )
    hike_id = json.loads(response.data)['id']

    payload['elevation'] = 300

    response = app.test_client().put(
        f'/hikes/{hike_id}',
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 200


def test_should_get_hike_data():
    """
        GIVEN a Flask application configured for testing
        WHEN the '/hikes/latest' page is requested (GET)
        THEN check that a '200' (OK) status code is returned and that hike elevation has been updated
    """
    response = app.test_client().get(
        '/hikes/latest',
        headers={'Content-Type': 'application/json'},
    )
    assert json.loads(response.data)['elevation'] == 300
    assert response.status_code == 200


def test_should_delete_hike_data():
    """
        GIVEN a Flask application configured for testing
        WHEN the '/hikes/hike_id' page is deleted (DELETE)
        THEN check that a '204' (No-content) status code is returned
    """
    response = app.test_client().get(
        '/hikes/latest',
        headers={'Content-Type': 'application/json'},
    )
    hike_id = json.loads(response.data)['id']

    response = app.test_client().delete(
        f'/hikes/{hike_id}',
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 204


def test_should_not_post_hike_data():
    """
        GIVEN a Flask application configured for testing
        WHEN the '/' page is posted to (POST)
        THEN check that a '405' (Method Not Allowed) status code is returned
    """
    response = app.test_client().post(
        '/',
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 405
