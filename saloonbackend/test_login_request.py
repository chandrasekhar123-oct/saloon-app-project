import requests

data = {
    'phone': '+919000012345',
    'password': 'user123'
}

response = requests.post('http://localhost:5000/user-portal/login', data=data, allow_redirects=False)

print(f"Status Code: {response.status_code}")
print(f"Location Header: {response.headers.get('Location')}")
if response.status_code == 302 and '/home' in response.headers.get('Location', ''):
    print("Login Success!")
else:
    print("Login Failed.")
