# MIT License
#
# SSMA - Tool that helps you collect your badges in a satr platform
#
# Copyright (c) 2022 Awiteb <Awiteb@hotmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
from typing import List, Optional

safcsp_api = "https://api.safcsp.cloud/"

badge_endpoint = safcsp_api + "badge/public/{user_id}"
courses_endpoint = (
    safcsp_api + "course/search/courses?course_type=COURSE&q={course_name}"
)
profile_endpoint = "https://api.coderhub.sa/api/profile/public/{username}/"

course_url = "https://satr.codes/courses/{url_code}/view"


def _get_user_id(username: str) -> str:
    """Return user_id of username

    Args:
        username (str): username

    Raises:
        Exception: Invalid username

    Returns:
        str: user_id
    """
    response = requests.get(profile_endpoint.format(username=username))
    if response.status_code == 200:
        return response.json().get("user_information", {}).get("id")
    else:
        raise Exception(f"No information about {username}")


def get_courses_url(course_name: str) -> Optional[str]:
    """Return course url from name

    Args:
        course_name (str): name of course

    Returns:
        Optional[str]: url of course
    """
    response = requests.get(courses_endpoint.format(course_name=course_name))
    if response.status_code == 200:
        courses = list(
            filter(
                lambda course: course["title"].lower() == course_name.lower(),
                response.json(),
            )
        )
        if courses:
            return course_url.format(url_code=courses[0].get("url_id"))
    return "https://satr.codes/courses"


def get_courses_badge(username: str) -> List[dict]:
    """Return user courses badge

    Args:
        username (str): username of user

    Returns:
        List: badges
    """
    return [
        badge
        for badge in requests.get(
            badge_endpoint.format(user_id=_get_user_id(username=username))
        ).json()
        if badge.get("event") == "course_complated"
    ]


def courses_parse(badges: List[dict], size: int) -> str:
    """make image and url for courses badge

    Args:
        badges (List[dict]): courses badge
        size (int): size of badge

    Returns:
        str: badges with courses url as html
    """
    text = "<h2 align='center'>Completed <a href='https://Satr.codes'>Satr</a> courses</h2>\n\n<div align='center'>"
    for badge in badges:
        course_name = "".join(filter(str.isascii, badge["title"])).strip()
        badge_text = f"""<a target='_blank' href='{get_courses_url(course_name)}'>
            \r    <img align='center' alt='{course_name}' src='{badge['image_url']}' width='{size}' height='{size}'/>
            \r</a>\n"""
        text += badge_text
    return text + "</div>"


def main():
    username = input("Enter your username in satr.codes: ")
    badge_size = int(input("Enter badges size (default 90): ") or 90)
    badges = get_courses_badge(username=username)
    print(courses_parse(badges=badges, size=badge_size))


if __name__ == "__main__":
    main()
