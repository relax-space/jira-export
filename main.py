from concurrent.futures import ThreadPoolExecutor
from jira import JIRA
from traceback import format_exc
from pandas import ExcelWriter, DataFrame, concat

from relax.util import f_date, gen_dir, to_hour
from os import path as os_path
from copy import deepcopy
from json import dump
import urllib3

urllib3.disable_warnings()


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
    projects_raw = jira.projects()

    projects = []
    project_simples = []
    for project in projects_raw:
        if hasattr(project, "archived") and project.archived:
            continue
        projects.append(project)
        project_simples.append({"key": project.key, "name": project.name})

    with open("project.json", mode="w", encoding="utf8") as f:
        dump(project_simples, f, ensure_ascii=False)

    if project_key:
        projects = [i for i in projects if i.key == project_key]
    pass

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(download, project, jira) for project in projects}
        df_list = []
        for f in futures:
            df = f.result()
            df_list.append(df)
        df = concat(df_list)
        name = f"{folder_name}/raw.xlsx"
        with ExcelWriter(name) as writer:
            df.to_excel(writer, sheet_name="sheet1", index=False)

    print("All issues downloaded successfully!")


def remove_blank(raw, blank_mark, replace_value):
    if (not raw) or raw == blank_mark:
        return replace_value
    return raw


def download(project, jira):
    try:
        return download_issues(project, jira)
    except Exception as e:
        print(e)
        # print(format_exc())


# Download issues for each project
def download_issues(project, jira):
    project_key = project.key
    issues = jira.search_issues(f"project={project_key}", maxResults=1000)
    if issues.total > 1000:
        for start in range(1000, issues.total, 1000):
            issues += jira.search_issues(
                f"project={project_key}", startAt=start, maxResults=1000
            )
    headers = [
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
        "项目秘钥",
        "项目类别",
        "解决时间",  # resolutiondate
        "创建时间",  # created
        "迭代编号",  # customfield_10020_id
        "迭代名称",  # customfield_10020_name
        "迭代状态",  # customfield_10020_state
        "迭代目标",  # customfield_10020_goal
        "迭代开始时间",  # customfield_10020_startDate
        "迭代结束时间",  # customfield_10020_endDate
        "日志编号",
        "日志创建人",
        "日志更新人",
        "日志记录工时",
        "日志内容",
        "日志创建时间",
        "日志更新时间",
    ]
    data = []
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
        row = [
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
            project.get("key"),
            project.get("projectCategory", {}).get("name", ""),
            f_date(issue_fields.get("resolutiondate", "")),
            f_date(issue_fields.get("created", "")),
        ]

        if customfield_10020s:
            idxmax = 0
            for i in customfield_10020s:
                cid = i.get("id", 0)
                if cid > idxmax:
                    idxmax = cid
            for i in customfield_10020s:
                cid = i.get("id", 0)
                if idxmax == cid:
                    row.extend(
                        [
                            cid,
                            i.get("name", ""),
                            i.get("state", ""),
                            i.get("goal", ""),
                            f_date(i.get("startDate", "")),
                            f_date(i.get("endDate", "")),
                        ]
                    )
        else:
            row.extend(
                [
                    0,
                    "",
                    "",
                    "",
                    None,
                    None,
                ]
            )
        if worklogs:
            for i in worklogs:
                row_new = deepcopy(row)
                row_new.extend(
                    [
                        i.get("id", ""),
                        i.get("author", {}).get("displayName", ""),
                        i.get("updateAuthor", {}).get("displayName", ""),
                        to_hour(i.get("timeSpentSeconds", "")),
                        i.get("comment", ""),
                        f_date(i.get("created", "")),
                        f_date(i.get("updated", "")),
                    ]
                )
                data.append(row_new)
        else:
            row.extend(
                [
                    0,
                    "",
                    "",
                    0,
                    "",
                    None,
                    None,
                ]
            )
            data.append(row)

    df1 = DataFrame(data, columns=headers)
    return df1


if __name__ == "__main__":
    server = "https://reddate123.atlassian.net"
    cookie = ""
    raw_folder = os_path.join("data1", "raw")
    gen_dir(raw_folder)
    start(server, cookie, "", raw_folder)

    # server = "https://udpn.atlassian.net"
    # cookie = ""
    # raw_folder = os_path.join("data2", "raw")
    # gen_dir(raw_folder)
    # start(server, cookie, "UDPN", raw_folder)
    pass
