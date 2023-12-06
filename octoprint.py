# API abstraction for OctoPrint
import requests


class OctoPrint:
    key = None
    site = None

    def __init__(self, site, key):
        self.site = site
        self.key = key

    def headers(self):
        return {
            "X-Api-Key": self.key,
            "Content-Type": "application/json",
            "cache-control": "no-cache",
        }

    # Gets a list of all users
    def get_users(self):
        url = f"http://{self.site}/api/access/users"
        response = requests.request("GET", url, headers=self.headers())
        return response.json()

    # Checks if a user exists
    def user_exists(self, username):
        url = f"http://{self.site}/api/access/users/{username}"
        response = requests.request("GET", url, headers=self.headers())
        return response.status_code == 200

    # Creates a user with the given username and password
    # Optionally, you can specify additional groups and permissions
    def create_user(self, username, password, groups=["users"], permissions=[]):
        # Creates groups if they don't exist
        for group in groups:
            self.create_group_if_not_exists(group)

        url = f"http://{self.site}/api/access/users"
        payload = {
            "name": username,
            "password": password,
            "active": True,
            "groups": groups,
            "permissions": permissions,
        }

        response = requests.request("POST", url, json=payload, headers=self.headers())
        return response.status_code == 200

    # Deletes a user
    def delete_user(self, username):
        url = f"http://{self.site}/api/access/users/{username}"
        response = requests.request("DELETE", url, headers=self.headers())
        return response.status_code == 200

    # Resets a user's password
    # put--api-access-users-(string-username)-password
    def reset_password(self, username, password):
        url = f"http://{self.site}/api/access/users/{username}/password"
        payload = {
            "password": password,
        }

        response = requests.request("PUT", url, json=payload, headers=self.headers())
        return response.status_code == 200

    # Checks if a group exists
    def group_exists(self, groupname):
        url = f"http://{self.site}/api/access/groups/{groupname}"
        response = requests.request("GET", url, headers=self.headers())
        return response.status_code == 200

    # Creates a group with the given name
    # Optionally, you can specify additional permissions
    def create_group(self, groupname, permissions=[]):
        url = f"http://{self.site}/api/access/groups"
        payload = {
            "key": groupname,
            "name": groupname,
            "description": groupname,
            "permissions": permissions,
            "subgroups": [],
            "default": False,
        }

        response = requests.request("POST", url, json=payload, headers=self.headers())
        return response.status_code == 200

    # Create a group if it doesn't exist
    def create_group_if_not_exists(self, groupname, permissions=[]):
        if not self.group_exists(groupname):
            self.create_group(groupname, permissions)

    # Mass deletes users that match a group
    def mass_delete(self, groupname):
        users = self.get_users()["users"]
        for user in users:
            if groupname in user["groups"]:
                self.delete_user(user["name"])
