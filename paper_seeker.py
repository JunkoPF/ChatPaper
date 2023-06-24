import os
import time
import tempfile
import argparse

import requests
import tenacity

import chat_paper

SEARCH_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
GET_DETAILS_API_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
API_KEY = "RkqCd90Glr7ftwkLozojD2kYorSQ6H6c5OH7uYER"


class PaperInfo:
    title: str
    year: int
    url: str
    authors: str
    abstract: str
    is_open_access: bool
    open_access_pdf: str

    def __init__(self, info_dict: dict[str, any]):
        self.title = info_dict["title"]
        self.year = info_dict["year"]
        self.url = info_dict["url"]
        self.authors = ", ".join([author["name"] for author in info_dict["authors"]])
        self.abstract = info_dict["abstract"]
        self.is_open_access = info_dict["isOpenAccess"]
        if self.is_open_access:
            self.open_access_pdf = info_dict["openAccessPdf"]["url"]


fields = [
    "title",
    "year",
    "url",
    "authors",
    "abstract",
    "isOpenAccess",
    "openAccessPdf",
]


def search_papers(keywords: list[str], limit: int = 10, offset: int = 0) -> list[str]:
    try:
        response = requests.get(
            SEARCH_API_URL,
            headers={"x-api-key": API_KEY},
            params={
                "query": " ".join(keywords),
                "limit": limit,
                "offset": offset,
                "fields": "paperId",
                "openAccessPdf": "",
            },
        )

        results = response.json()

        total = results["total"]
        print(f"Found {total} results.")
        if total == 0:
            return []

        data: list[dict[str, str]] = results["data"]
        ids: list[str] = [item["paperId"] for item in data]
        return ids
    except Exception as e:
        print(e)
    return []


def get_papers_details(ids: list[str]) -> list[PaperInfo]:
    try:
        response = requests.post(
            GET_DETAILS_API_URL,
            params={"fields": ",".join(fields)},
            json={"ids": ids},
        )

        results = response.json()

        infos: list[PaperInfo] = []

        for item in results:
            info = PaperInfo(item)
            infos.append(info)

        return infos
    except Exception as e:
        print(e)
    return []


@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    stop=tenacity.stop_after_attempt(3),
    reraise=True,
)
def download_pdf(info: PaperInfo, dir_path: str):
    if not info.is_open_access:
        return

    try:
        print("downloading {} ...".format(info.title))
        response = requests.get(info.open_access_pdf)
        file_path = os.path.join(dir_path, info.title + ".pdf")

        with open(file_path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        raise e


temp_dir = tempfile.TemporaryDirectory()


def download_all_pdf(infos: list[PaperInfo], save_pdf: bool = True) -> str:
    dir_path = ""
    if not save_pdf:
        dir_path = temp_dir.name
    else:
        folder_name = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        dir_path = os.path.join("pdf", folder_name)
        os.makedirs(dir_path)

    for info in infos:
        if info.is_open_access:
            download_pdf(info, dir_path)

    return os.path.abspath(dir_path)


def main(args: argparse.Namespace):
    ids = search_papers(args.keywords.split(","), limit=args.limit)
    infos = get_papers_details(ids)
    dir_path = download_all_pdf(infos, args.save_pdf)

    os.system("python3 chat_paper.py --pdf_path {}".format(dir_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # keywords (use comma to seperate)
    parser.add_argument("--keywords", type=str, required=True)

    # save fetched pdf in pdf/xxx/...
    parser.add_argument("--save_pdf", action="store_true", default=False)

    # number of available papers
    parser.add_argument("--limit", type=int, default=5)

    main(parser.parse_args())
