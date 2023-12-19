import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from jira import JIRA
from traceback import format_exc
from copy import deepcopy
from pandas import ExcelWriter, DataFrame
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
    project_key = project.key
    issues = jira.search_issues(f"project={project_key}", maxResults=1000)
    if issues.total > 1000:
        for start in range(1000, issues.total, 1000):
            issues += jira.search_issues(
                f"project={project_key}", startAt=start, maxResults=1000
            )
    headers1 = [
        "状态变更时间",
        "主编号",
        "主秘钥",
        "主概述",  # parent_summary
        "主状态",
        "主优先级",
        "编号",
        "秘钥",
        "摘要",  # summary
        "类型",  # 任务类型
        "状态",  # status
        "解决方案",  # resolution
        "缺陷等级",
        "预估工时",  # aggregatetimeoriginalestimate
        "实际工时",
        "经办人",  # assignee_displayName
        "是否在职",  # assignee_active
        "项目名称",
        "解决时间",  # resolutiondate
        "创建时间",  # created
    ]
    headers2 = [
        "编号",  # customfield_10020_id
        "任务编号",
        "名称",  # customfield_10020_name
        "状态",  # customfield_10020_state
        "目标",  # customfield_10020_goal
        "开始时间",  # customfield_10020_startDate
        "结束时间",  # customfield_10020_endDate
    ]
    headers3 = [
        "编号",
        "任务编号",
        "创建人",
        "更新人",
        "记录工时",
        "内容",
        "创建时间",
        "更新时间",
    ]
    data1 = []
    data2 = []
    data3 = []
    for issue in issues:
        id = issue.raw.get("id", "")
        key = issue.raw.get("key", "")
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
        data1.append(
            [
                f_date(issue_fields.get("statuscategorychangedate", "")),
                parent.get("id", ""),
                parent.get("key", ""),
                parent_fields.get("summary", ""),
                parent_fields_status.get("name", ""),
                parent_fields_priority.get("name", ""),
                id,
                key,
                issue_fields.get("summary", ""),
                issuetype.get("name", ""),
                status.get("name", ""),
                resolution.get("name", ""),
                customfield_10102,
                aggregatetimeoriginalestimate,
                aggregatetimespent,
                assignee.get("displayName", ""),
                assignee.get("active", ""),
                project.get("name"),
                f_date(issue_fields.get("resolutiondate", "")),
                f_date(issue_fields.get("created", "")),
            ]
        )
        if customfield_10020s and len(customfield_10020s) > 2:
            for i in customfield_10020s:
                data2.append(
                    [
                        i.get("id", 0),
                        id,
                        i.get("name", ""),
                        i.get("state", ""),
                        i.get("goal", ""),
                        i.get("startDate", ""),
                        i.get("endDate", ""),
                    ]
                )
        if worklogs:
            for i in worklogs:
                data3.append(
                    [
                        i.get("id", ""),
                        i.get("issueId", ""),
                        i.get("author", {}).get("displayName", ""),
                        i.get("updateAuthor", {}).get("displayName", ""),
                        to_hour(i.get("timeSpentSeconds", "")),
                        i.get("comment", ""),
                        f_date(i.get("created", "")),
                        f_date(i.get("updated", "")),
                    ]
                )
    df1 = DataFrame(data1, columns=headers1)
    df2 = DataFrame(data2, columns=headers2)
    df3 = DataFrame(data3, columns=headers3)
    name = f"{folder_name}/{project_key}.xlsx"
    with ExcelWriter(name) as writer:
        df1.to_excel(writer, sheet_name="sheet1", index=False)
        df2.to_excel(writer, sheet_name="sheet2", index=False)
        df3.to_excel(writer, sheet_name="sheet3", index=False)
        pass


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


if __name__ == "__main__":
    server = "https://reddate123.atlassian.net"
    cookie = ""
    start(server, cookie, "NYL", "new1")

    # server = "https://udpn.atlassian.net"
    # cookie = ""
    # start(server, cookie, "UDPN", "new2")
    pass
