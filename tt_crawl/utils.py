import datetime
import csv


def check_date_range(start_date: str, end_date: str) -> bool:
    """
    Returns True if the date range is valid.

    Args:
        start_date (str): The start date of the search.
        end_date (str): The end date of the search.
    """
    start_datetime = datetime.datetime.strptime(start_date, "%Y%m%d")
    end_datetime = datetime.datetime.strptime(end_date, "%Y%m%d")
    delta = end_datetime - start_datetime

    if delta.days <= 30:
        return True
    else:
        return False


def generate_request_query(query: dict, start_date: str, end_date: str) -> dict:
    """
    Returns a request query object.

    Args:
        query (dict): The search query.
        start_date (str): The start date of the search.
        end_date (str): The end date of the search.
    """
    request_query = {
        "query": query.get("query"),
        "max_count": 100,
        "cursor": 0,
        "search_id": "",
        "start_date": start_date,
        "end_date": end_date,
    }
    return request_query


def generate_request_queries(query: int, start_date: str, end_date: str) -> list:
    """
    Returns a list of the request queries.
    """
    start_datetime = datetime.datetime.strptime(start_date, "%Y%m%d")
    end_datetime = datetime.datetime.strptime(end_date, "%Y%m%d")
    delta = end_datetime - start_datetime
    query_ranges = delta.days // 30 + 1

    request_queries = []
    for i in range(query_ranges):
        range_start = start_datetime + datetime.timedelta(days=i * 30)
        range_end = min(
            start_datetime + datetime.timedelta(days=(i + 1) * 30), end_datetime
        )
        request_query = generate_request_query(
            query, range_start.strftime("%Y%m%d"), range_end.strftime("%Y%m%d")
        )
        request_queries.append(request_query)

    return request_queries


def generate_search_key(query: dict) -> str:
    """
    Returns a string which can be used to identify the search Query.
    """
    search_key = ""
    for operator in ["and", "or", "not"]:
        for item in query["query"][operator]:
            search_key += f"{item['operation']} {item['field_name']} {' '.join(item['field_values'])} "
        search_key = search_key.rstrip() + " | "
    search_key = search_key.rstrip(" | ")
    return search_key


def process_data(
    data: dict, fields: list, search_key: str, queried_date: str, file_path: str
) -> None:
    """
    Writes the data into a csv file and stores it in the specified file path.
    The default file path is the current working directory.
    """
    video_data = data["data"]["videos"]

    if video_data:
        for data in video_data:
            for field in fields:
                if field not in data:
                    data[field] = None
            data["id"] = "'" + str(data["id"]) + "'"
            data["music_id"] = "'" + str(data["music_id"]) + "'"
            data["search_key"] = search_key
            data["queried_date"] = queried_date
            data["create_time"] = datetime.datetime.utcfromtimestamp(
                data["create_time"]
            ).strftime("%Y-%m-%d %H:%M:%S")

        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerows(video_data)
    else:
        print("No data to write to csv file")
        print(data)


def generate_date_string(day: int, month: int, year: int) -> str:
    """
    generates a date string in the format YYYYMMDD
    """
    date_str = str(year) + str(month).zfill(2) + str(day).zfill(2)
    return date_str
