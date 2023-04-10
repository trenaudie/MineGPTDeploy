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


def testupload():
    url = "http://localhost:5006/upload"
    with open('backend/testarticles/articleIsrael.txt', 'rb') as f:
        file_data = {'document': f}
        response = requests.postt(url, files=file_data)
        assert response.status_code == 200


def test_register(email: str, password: str):
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


def test_login(email: str, password: str):
    url = "http://localhost:5000/login"
    headers = {'Content-type': 'application/json'}
    data = {'email': email,
            'password': password}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("-------------")
    print("Login test")
    print("-------------")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")


def testquestion(question=None):
    headers = {'Content-type': 'application/json'}
    if not question:
        question = 'What is the capital of France?'
    data = {'text': question}
    url = 'http://localhost:5000/qa'

    print('--------------')
    print('Question test')
    print('--------------')

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.ok:
        response_data = json.loads(response.content)
        processed_text = response_data['content']
        sources = response_data['source']
        print(processed_text)
        print(sources + '\n')
    else:
        print(f'Request failed with status code {response.status_code}')


if __name__ == "__main__":
    bad_email = 'guigui.jarry@gmail.com'

    good_email = 'guigui.jarry@etu.minesparis.psl.eu'
    good_password = 'guigui'

    bad_password = 'broken_bitch'
    test_register(good_email, good_password)
    test_register(bad_email, bad_password)

    test_login(good_email, good_password)
    test_login(good_email, bad_password)
    test_login(bad_email, good_password)

    testquestion()
