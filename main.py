import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from jira import JIRA
from traceback import format_exc
from copy import deepcopy

import pytz


def to_hour(second) -> float:
    if not isinstance(second, (int, float)):
        return 0
    h = round(second / 3600, 1)
    return h


def start(server, cookie, project_key, folder_name):
    host = server.replace("https://", "")
    options = {
        "verify": False,
        "headers": {
            "Content-Type": "application/json;charset=UTF-8",
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "host": host,
            "Cookie": cookie,
        },
    }

    # 创建Jira实例
    jira = JIRA(
        server=server,
        options=options,
    )

    # Get all projects
    projects = jira.projects()

    for i, project in enumerate(projects):
        print(f"{i} {project.key}   {project.name}")

    if project_key:
        projects = [i for i in projects if i.key == project_key]
    pass

    with ThreadPoolExecutor() as executor:
        for project in projects:
            executor.submit(download, project, jira, folder_name)

    print("All issues downloaded successfully!")


def remove_blank(raw, blank_mark, replace_value):
    if (not raw) or raw == blank_mark:
        return replace_value
    return raw


def download(project, jira, folder_name):
    try:
        download_issues(project, jira, folder_name)
    except Exception as e:
        print(format_exc())


# Download issues for each project
def download_issues(project, jira, folder_name):
    issues = jira.search_issues(f"project={project.key}", maxResults=1000)
    if issues.total > 1000:
        for start in range(1000, issues.total, 1000):
            issues += jira.search_issues(
                f"project={project.key}", startAt=start, maxResults=1000
            )
    with open(
        f"{folder_name}/{project.key}.csv", "w", newline="", encoding="utf-8-sig"
    ) as csvfile:
        writer = csv.writer(csvfile)
        headers = [
            "statuscategorychangedate",
            "parent_id",
            "parent_key",
            "主任务概述",  # parent_summary
            "parent_status",
            "parent_priority",
            "解决方案",  # resolution
            "customfield_10102",
            "原始估算",  # aggregatetimeoriginalestimate
            "aggregatetimespent",
            "经办人",  # assignee_displayName
            "是否在职",  # assignee_active
            "任务状态",  # status
            "issuetype_name",  # 任务类型
            "project_name",
            "解决时间",  # resolutiondate
            "创建时间",  # created
            "描述",  # summary
            "迭代ID",  # customfield_10020_id
            "迭代名称",  # customfield_10020_name
            "迭代状态",  # customfield_10020_state
            "迭代目标",  # customfield_10020_goal
            "迭代开始时间",  # customfield_10020_startDate
            "迭代结束时间",  # customfield_10020_endDate
            "工作日志创建者",
            "工作日志更新者",
            "花费时间",
            "日志",
            "工作日志id",
            "工作日志issueid",
            "创建时间",
            "更新时间",
        ]

        writer.writerow(headers)
        for issue in issues:
            issue_fields: dict = issue.raw["fields"]
            parent = issue_fields.get("parent", {})
            parent = remove_blank(parent, "{}", {})
            parent_fields = parent.get("fields", {})
            parent_fields = remove_blank(parent_fields, "{}", {})
            parent_fields_status = parent_fields.get("status", {})
            parent_fields_status = remove_blank(parent_fields_status, "{}", {})
            parent_fields_priority = parent_fields.get("priority", {})
            parent_fields_priority = remove_blank(parent_fields_priority, "{}", {})
            resolution = issue_fields.get("resolution", {})
            resolution = remove_blank(resolution, "{}", {})

            customfield_10102s = issue_fields.get("customfield_10102", [])
            customfield_10102s = remove_blank(customfield_10102s, "[]", [])
            customfield_10102 = (
                customfield_10102s.get("value", "")
                if isinstance(customfield_10102s, dict)
                else ""
            )
            aggregatetimeoriginalestimate = issue_fields.get(
                "aggregatetimeoriginalestimate", 0
            )
            aggregatetimeoriginalestimate = to_hour(
                remove_blank(aggregatetimeoriginalestimate, "[]", 0)
            )

            aggregatetimespent = issue_fields.get("aggregatetimespent", 0)
            aggregatetimespent = to_hour(remove_blank(aggregatetimespent, "{}", 0))
            assignee = issue_fields.get("assignee", {})
            assignee = remove_blank(assignee, "{}", {})

            status = issue_fields.get("status", {})
            status = remove_blank(status, "{}", {})

            issuetype = issue_fields.get("issuetype", {})
            issuetype = remove_blank(issuetype, "{}", {})

            project = issue_fields.get("project", {})
            project = remove_blank(project, "{}", {})

            customfield_10020s = issue_fields.get("customfield_10020", [])
            customfield_10020s = remove_blank(customfield_10020s, "[]", [])

            worklog_top = issue_fields.get("worklog", {})
            worklog_top = remove_blank(worklog_top, "{}", {})

            worklogs = worklog_top.get("worklogs", [])
            worklogs = remove_blank(worklogs, "[]", [])

            row_part = [
                f_date(issue_fields.get("statuscategorychangedate", "")),
                parent.get("id", ""),
                parent.get("key", ""),
                parent_fields.get("summary", ""),
                parent_fields_status.get("name", ""),
                parent_fields_priority.get("name", ""),
                resolution.get("name", ""),
                customfield_10102,
                aggregatetimeoriginalestimate,
                aggregatetimespent,
                assignee.get("displayName", ""),
                assignee.get("active", ""),
                status.get("name", ""),
                issuetype.get("name", ""),
                project.get("name"),
                f_date(issue_fields.get("resolutiondate", "")),
                f_date(issue_fields.get("created", "")),
                issue_fields.get("summary", ""),
            ]

            merge_rows = merge_list(customfield_10020s, worklogs)
            for i, j in merge_rows:
                row = deepcopy(row_part)
                row.append(i.get("id", 0))
                row.append(i.get("name", ""))
                row.append(i.get("state", ""))
                row.append(i.get("goal", ""))
                row.append(f_date(i.get("startDate", "")))
                row.append(f_date(i.get("endDate", "")))

                row.append(j.get("author", {}).get("displayName", ""))
                row.append(j.get("updateAuthor", {}).get("displayName", ""))
                row.append(to_hour(j.get("timeSpentSeconds", "")))
                row.append(j.get("comment", ""))
                row.append(j.get("id", ""))
                row.append(j.get("issueId", ""))
                row.append(f_date(j.get("created", "")))
                row.append(f_date(j.get("updated", "")))

                writer.writerow(row)


def f_date(original_time: str) -> str:
    # original_time = "2023-12-13T17:33:46.976+0800"
    try:
        if not original_time:
            return ""
        parsed_time = datetime.strptime(original_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        china_tz = pytz.timezone("Asia/Shanghai")
        china_time = parsed_time.astimezone(china_tz)
        return china_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(4, e)
        return ""


def merge_list(list1, list2):
    if not list1:
        list1 = [
            {
                "id": 0,
                "name": "",
                "state": "",
                "goal": "",
                "startDate": "",
                "endDate": "",
            }
        ]
    if not list2:
        list2 = [
            {
                "author": {},
                "updateAuthor": {},
                "timeSpentSeconds": "",
                "comment": "",
                "id": 0,
                "issueId": "",
                "created": "",
                "updated": "",
            }
        ]
    rows = []
    for i in list1:
        for j in list2:
            rows.append([i, j])
    return rows


if __name__ == "__main__":
    server = "https://reddate123.atlassian.net"
    cookie = ""
    start(server, cookie, "", "new1")

    # server = "https://udpn.atlassian.net"
    # cookie = ""
    # start(server, cookie, "UDPN", "new2")
    pass
