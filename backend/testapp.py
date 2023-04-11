import requests
import json


def checkrequest(method: str, path: str, status: int, content: str = None, **kwargs):
    """Checks if the request to localhost returns the expected response"""
    url = f'http://localhost:5005{path}'
    response = requests.request(method, url, **kwargs)

    assert response.status_code == status
    if content is not None:
        assert response.content.decode('utf-8') == content


def test_homepage():
    checkrequest('GET', '/', 200, None)


def testnot():
    checkrequest('GET', '/not', 404, None)


def testupload(session: requests.Session):

    url = "http://localhost:5000/upload"
    with open('backend/testarticles/article15_2.txt', 'rb') as f:
        files = {
            "document":  f,
        }
        data = {'id': 12345, 'session_id': session.cookies.get('session', None) }
        print('inside testupload, session id: ', session.cookies.get('session', None))
        response = session.post(url, data=data, files=files)
        assert response.status_code == 200


def register_for_tests(email: str, password: str):
    url = "http://localhost:5000/register"
    headers = {'Content-type': 'application/json'}
    data = {'email': email,
            'password': password}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("-------------")
    print("Register test")
    print("-------------")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")


def login_for_tests(email: str, password: str):
    url = "http://localhost:5000/login"
    headers = {'Content-type': 'application/json'}
    data = {'email': email,
            'password': password}

    session = requests.Session()
    response = session.post(url, headers=headers, data=json.dumps(data))
    print("-------------")
    print("Login test")
    print("-------------")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    return session

def logout_for_tests():
    url = "http://localhost:5000/logout"
    headers = {
        'Content-type': 'application/json',
    }

    response = requests.post(url, headers=headers)
    print("-------------")
    print("Logout test")
    print("-------------")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")




def testquestion(session, question=None):

    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    if not question:
        question = 'Lisa Murkowsk is who?'
    print('--------------')
    print('Question test', question)
    print('--------------')
    data = {'question': question, 'session_id': session.cookies.get('session', None)}
    url = 'http://localhost:5000/qa'
    response = session.post(url, headers=headers, data=data)


    if response.ok:
        response_data = json.loads(response.content)
        processed_text:str = response_data['answer']
        sources:list = response_data['sources']
        print(processed_text)
        print('---------')
        for source in sources:
            print(source['filename'])
            print(source['text'])
            print('---------')

    else:
        print(f'Request failed with status code {response.status_code}')







bad_email,good_email,good_password,bad_password = 'guigui.jarry@gmail.com','guigui.jarry@etu.minesparis.psl.eu','guigui', 'broken_bitch'

if __name__ == "__main__":
    # register_for_tests(good_email,good_password)
    logout_for_tests()
    session = login_for_tests(good_email,good_password)

    sid = session.cookies.get('session')
    print("sid", sid, id(sid))
    testupload(session=session)
    testquestion(session)

