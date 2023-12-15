import csv
from concurrent.futures import ThreadPoolExecutor
from jira import JIRA
from traceback import format_exc

server = "https://reddate123.atlassian.net"
options = {
    "verify": False,
    "headers": {
        "Content-Type": "application/json;charset=UTF-8",
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "host": "reddate123.atlassian.net",
        "Cookie": "",
    },
}


def to_hour(second) -> float:
    if not isinstance(second, (int, float)):
        return 0
    h = round(second / 3600, 1)
    return h


# 创建Jira实例
jira = JIRA(
    server=server,
    options=options,
)

# Get all projects
projects = jira.projects()
# projects = [projects[13]]


def remove_blank(raw, blank_mark, replace_value):
    if (not raw) or raw == blank_mark:
        return replace_value
    return raw


# Download issues for each project
def download_issues(project):
    issues = jira.search_issues(f"project={project.key}", maxResults=1000)
    if issues.total > 1000:
        for start in range(1000, issues.total, 1000):
            issues += jira.search_issues(
                f"project={project.key}", startAt=start, maxResults=1000
            )
    with open(
        f"new/{project.key}.csv", "w", newline="", encoding="utf-8-sig"
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
            "迭代ID",  # customfield_10020_id
            "迭代名称",  # customfield_10020_name
            "迭代状态",  # customfield_10020_state
            "迭代目标",  # customfield_10020_goal
            "迭代开始时间",  # customfield_10020_startDate
            "迭代结束时间",  # customfield_10020_endDate
            "描述",  # summary
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
            parent_fields_issuetype = parent_fields.get("issuetype", {})
            parent_fields_issuetype = remove_blank(parent_fields_issuetype, "{}", {})
            resolution = issue_fields.get("resolution", {})
            resolution = remove_blank(resolution, "{}", {})
            customfield_10107 = issue_fields.get("customfield_10107", {})
            customfield_10107 = remove_blank(customfield_10107, "{}", {})

            customfield_10102s = issue_fields.get("customfield_10102", [])
            customfield_10102s = remove_blank(customfield_10102s, "[]", [])
            customfield_10102 = (
                customfield_10102s.get("value", "")
                if isinstance(customfield_10102s, dict)
                else ""
            )

            labels = issue_fields.get("labels", 0)
            labels = remove_blank(labels, "[]", 0)

            timeestimate = issue_fields.get("timeestimate", 0)
            timeestimate = remove_blank(timeestimate, "[]", 0)

            aggregatetimeoriginalestimate = issue_fields.get(
                "aggregatetimeoriginalestimate", 0
            )
            aggregatetimeoriginalestimate = to_hour(
                remove_blank(aggregatetimeoriginalestimate, "[]", 0)
            )

            assignee = issue_fields.get("assignee", {})
            assignee = remove_blank(assignee, "{}", {})
            status = issue_fields.get("status", {})
            status = remove_blank(status, "{}", {})
            customfield_10058 = issue_fields.get("customfield_10058", 0)
            customfield_10058 = remove_blank(customfield_10058, "[]", 0)
            customfield_10058 = (
                customfield_10058
                if customfield_10058 and (not isinstance(customfield_10058, dict))
                else 0
            )

            customfield_10043 = issue_fields.get("customfield_10043", {})
            customfield_10043 = remove_blank(customfield_10043, "{}", {})
            customfield_10044 = issue_fields.get("customfield_10044", {})
            customfield_10044 = remove_blank(customfield_10044, "{}", {})
            aggregateprogress = issue_fields.get("aggregateprogress", {})
            aggregateprogress = remove_blank(aggregateprogress, "{}", {})
            progress = issue_fields.get("progress", {})
            progress = remove_blank(progress, "{}", {})
            issuetype = issue_fields.get("issuetype", {})
            issuetype = remove_blank(issuetype, "{}", {})
            project = issue_fields.get("project", {})
            project = remove_blank(project, "{}", {})
            aggregatetimespent = issue_fields.get("aggregatetimespent", 0)
            aggregatetimespent = to_hour(remove_blank(aggregatetimespent, "{}", 0))

            customfield_10020s = issue_fields.get("customfield_10020", [])
            customfield_10020s = remove_blank(customfield_10020s, "[]", [])
            customfield_10014 = issue_fields.get("customfield_10014", {})
            customfield_10014 = remove_blank(customfield_10014, "{}", {})
            customfield_10015 = issue_fields.get("customfield_10015", {})
            customfield_10015 = remove_blank(customfield_10015, "{}", {})
            timetracking = issue_fields.get("timetracking", {})
            timetracking = remove_blank(timetracking, "{}", {})
            customfield_10000 = issue_fields.get("customfield_10000", {})
            customfield_10000 = remove_blank(customfield_10000, "{}", {})
            customfield_10089 = issue_fields.get("customfield_10089", {})
            customfield_10089 = remove_blank(customfield_10089, "{}", {})
            customfield_10122 = issue_fields.get("customfield_10122", {})
            customfield_10122 = remove_blank(customfield_10122, "{}", {})
            customfield_10001 = issue_fields.get("customfield_10001", {})
            customfield_10001 = remove_blank(customfield_10001, "{}", {})
            for customfield_10020 in customfield_10020s:
                row = [
                    issue_fields.get("statuscategorychangedate", ""),
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
                    issue_fields.get("resolutiondate", ""),
                    issue_fields.get("created", ""),
                    customfield_10020.get("id", 0),
                    customfield_10020.get("name", ""),
                    customfield_10020.get("state", ""),
                    customfield_10020.get("goal", ""),
                    customfield_10020.get("startDate", ""),
                    customfield_10020.get("endDate", ""),
                    issue_fields.get("summary", ""),
                ]
                writer.writerow(row)


with ThreadPoolExecutor() as executor:
    for project in projects:
        try:
            executor.submit(download_issues, project)
        except Exception as e:
            print(format_exc())

print("All issues downloaded successfully!")
