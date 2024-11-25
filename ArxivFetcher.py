import os
import json
import jsonlines
import re
import requests


class ArxivAbstractFetcher:
    def __init__(self, links, storage_path="abstracts.json"):
        """
        初始化类，接受arXiv链接列表和存储路径
        :param links: arXiv链接列表
        :param storage_path: 存储JSON或JSONL文件的路径
        """
        self.links = links
        self.storage_path = storage_path
        self.processed_data = self._load_processed_data()

    def _load_processed_data(self):
        """
        加载已处理的链接及其摘要
        :return: 已处理的数据字典
        """
        if not os.path.exists(self.storage_path):
            return {}
        try:
            if self.storage_path.endswith('.json'):
                with open(self.storage_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            elif self.storage_path.endswith('.jsonl'):
                processed_data = {}
                with jsonlines.open(self.storage_path, 'r') as reader:
                    for item in reader:
                        processed_data[item["link"]] = item["abstract"]
                return processed_data
        except Exception as e:
            print(f"加载存储文件失败: {e}")
            return {}

    def _extract_arxiv_id(self, link):
        """
        从arXiv链接中提取ID
        :param link: arXiv链接
        :return: arXiv ID
        """
        pattern = r'arxiv\.org/(?:abs|pdf)/([0-9]+\.[0-9]+(?:v[0-9]+)?)'
        match = re.search(pattern, link)
        return match.group(1) if match else None

    def fetch_abstract(self, arxiv_id):
        """
        通过arXiv API获取论文摘要
        :param arxiv_id: arXiv ID
        :return: 摘要文本
        """
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()

            entry_match = re.search(r'<entry>(.*?)</entry>', response.text, re.DOTALL)
            if not entry_match:
                return {"error": "无法解析论文元数据"}

            entry = entry_match.group(1)
            title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            abstract = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            authors = re.findall(r'<name>(.*?)</name>', entry)
            categories = re.search(r'<category term="(.*?)"', entry)
            published = re.search(r'<published>(.*?)</published>', entry)

            return {
                "id": arxiv_id,
                'link': f"https://arxiv.org/pdf/{arxiv_id}",
                "title": title.group(1).strip() if title else "标题未找到",
                "abstract": abstract.group(1).strip() if abstract else "摘要未找到",
                "authors": authors,
                "categories": categories.group(1) if categories else "未知分类",
                "published": published.group(1) if published else "未知日期"
            }

        except requests.RequestException as e:
            return {"error": f"获取元数据失败: {e}"}

    def fetch_and_store_abstracts(self):
        """
        获取摘要并存储到文件中
        """
        for link in self.links:
            if link in self.processed_data:
                print(f"跳过已处理链接: {link}")
                continue

            arxiv_id = self._extract_arxiv_id(link)
            if arxiv_id:
                abstract = self.fetch_abstract(arxiv_id)
                self.processed_data[link] = abstract
                self._append_to_storage(link, abstract)
                print(f"处理完成: {link}")
            else:
                print(f"无效的arXiv链接: {link}")

    def _append_to_storage(self, link, abstract):
        """
        将新的链接及摘要追加到存储文件
        :param link: arXiv链接
        :param abstract: 摘要内容
        """
        try:
            if self.storage_path.endswith('.json'):
                with open(self.storage_path, 'w', encoding='utf-8') as file:
                    json.dump(self.processed_data, file, ensure_ascii=False, indent=4)
            elif self.storage_path.endswith('.jsonl'):
                with jsonlines.open(self.storage_path, mode='a') as writer:
                    writer.write({"link": link, "abstract": abstract})
        except Exception as e:
            print(f"存储失败: {e}")


# 主程序
if __name__ == "__main__":
    # 假设从前一个类获得的链接列表
    arxiv_links = [
        "https://arxiv.org/abs/2106.10356",
        "https://arxiv.org/pdf/2107.08171",
    ]

    # 使用摘要提取类
    storage_path = "abstracts.json"  # 或者使用 "abstracts.jsonl"
    fetcher = ArxivAbstractFetcher(arxiv_links, storage_path)

    # 获取摘要并存储
    fetcher.fetch_and_store_abstracts()
