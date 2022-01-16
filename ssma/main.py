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

import asyncio
import requests
import aiohttp
import argparse
from typing import List, Awaitable

parser = argparse.ArgumentParser(
    description="Tool that helps you collect your badges in a satr platform."
)
parser.add_argument(
    "--username",
    "-u",
    metavar="",
    action="store",
    required=True,
    type=str,
    help="The username you want to get badges for.",
)
parser.add_argument(
    "--size",
    "-s",
    metavar="",
    action="store",
    type=float,
    default=90.0,
    help="The size of badge in html (default 90.0).",
)

args = parser.parse_args()

safcsp_api = "https://api.safcsp.cloud/"

badge_endpoint = safcsp_api + "badge/public/{user_id}"
courses_endpoint = (
    safcsp_api + "course/search/courses?course_type=COURSE&q={course_name}"
)
profile_endpoint = "https://api.coderhub.sa/api/profile/public/{username}/"

course_url = "https://satr.codes/courses/{url_code}/view"


async def get_course_url(course_name: str, session: aiohttp.ClientSession) -> str:
    """Return course url from name

    Args:
        course_name (str): name of course

    Returns:
        Optional[str]: url of course
    """
    response = await session.get(courses_endpoint.format(course_name=course_name))
    if response.status == 200:
        courses = list(
            filter(
                lambda course: course["title"].lower() == course_name.lower(),
                await response.json(),
            )
        )
        if courses:
            return course_url.format(url_code=courses[0].get("url_id"))
    return "https://satr.codes/courses"


async def course_parse(
    badge: dict, size: float, session: aiohttp.ClientSession
) -> Awaitable[str]:
    """make image and url for course badge

    Args:
        badges (dict): course badge
        size (float): size of badge

    Returns:
        str: badge with course url as html
    """
    text = "<h2 align='center'>Completed <a href='https://Satr.codes'>Satr</a> courses</h2>\n\n<div align='center'>"
    course_name = "".join(filter(str.isascii, badge["title"])).strip()
    badge_text = f"""<a target='_blank' href='{await get_course_url(course_name, session)}'>
        \r    <img align='center' alt='{course_name}' src='{badge['image_url']}' width='{size}' height='{size}'/>
        \r</a>\n"""
    text += badge_text
    return text + "</div>"


def get_courses_badge_tasks(
    badges: List[dict], size: float, session: aiohttp.ClientSession
) -> List[Awaitable[str]]:
    return [course_parse(badge, size, session) for badge in badges]


async def courses_parse(
    badges: List[dict], size: float, session: aiohttp.ClientSession
) -> str:
    """make image and url for courses badge

    Args:
        badges (List[dict]): courses badge
        size (float): size of badge

    Returns:
        str: badges with courses url as html
    """
    tasks = get_courses_badge_tasks(badges, size, session)
    texts = await asyncio.gather(*tasks)
    return "\n".join(texts)


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


async def main():
    async with aiohttp.ClientSession() as session:
        badges = get_courses_badge(args.username)
        print(await courses_parse(badges=badges, size=args.size, session=session))


if __name__ == "__main__":
    asyncio.run(main())
