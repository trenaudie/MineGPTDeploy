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


def testupload(session: requests.Session, access_token :str, file_id:str):

    url = "http://localhost:5000/upload"
    with open('backend/testarticles/MMC_PC1.pdf', 'rb') as f:
        files = {
            "document":  f,
        }
        #session_id =  session.cookies.get('session', None) not useful with jwt
        data = {'file_id': file_id} #different for every file, even if same
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        print(f"inside testupload, access_token: {access_token}")
        response = session.post(url, data=data, files=files, headers=headers)
        assert response.status_code == 200


def testdelete(session: requests.Session, access_token :str,file_id:str):
    url = "http://localhost:5000/delete"
    json = {'file_id': file_id}
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = session.post(url, json=json, headers=headers)
    assert response.status_code == 200




def register_for_tests(email: str, password: str):
    url = "http://localhost:5000/register"
    headers = {'Content-type': 'application/json'}
    data = {'email': email,
            'password': password}
    session = requests.Session()
    response = session.post(url, headers=headers, data=json.dumps(data))

    print("-------------")
    print("Register test")
    print("-------------")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    response_json = response.json()
    status = response_json['status']
    if not status == 'registration successful!':
        raise Exception('Register failed')

    access_token = response_json['access_token']
    return session, access_token


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
    print(f"Inside login for tests : response: {response.text}")
    response_json = response.json()
    status = response_json['status']
    if not status == 'authenticated':
        raise Exception('Login failed')

    access_token = response_json['access_token']

    return session, access_token

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




def testquestion(question:str,session:requests.Session, access_token:str):

    headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-type': 'application/json'
        }
    print('--------------')
    print('Question test', question)
    print('--------------')
    data = {'prompt': question, 'chathistory':[]}
    url = 'http://localhost:5000/qa'
    response = session.post(url, headers=headers, json=data)


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



def test_download(filename_base:str,session, access_token:str):
    url = f"http://localhost:5000/download/{filename_base}"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = session.get(url, headers=headers)
    print("-------------")
    print("Download test")
    print("-------------")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    print(response)



bad_email,good_email,good_password,bad_password = 'guigui.jarry@gmail.com','guigui.jarry@etu.minesparis.psl.eu','guigui', 'broken_bitch'
tanguyemail, tanguypw = 'tan4@etu.minesparis.psl.eu', 'r'
if __name__ == "__main__":
    # session, access_token = register_for_tests(good_email,good_password)
    session, access_token = login_for_tests(tanguyemail,tanguypw)
    fileid = 'blablaid'
    # testupload(session,access_token,fileid)
    # testdelete(session,access_token,fileid)

    # test_download('Probabilite1.pdf', session, access_token)
    testquestion('what is energy?',session, access_token)

    # session = requests.Session()
    # testupload(session, "")