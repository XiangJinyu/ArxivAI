from ArxivLinker import ArxivLinkProcessor
from ArxivFetcher import ArxivAbstractFetcher

# 假设Markdown文件路径为example.md
markdown_file_path = "link.md"
# 使用摘要提取类
storage_path = "abstracts.json"  # 或者使用 "abstracts.jsonl"


def main():
    # 初始化类并处理文件
    processor = ArxivLinkProcessor(markdown_file_path)

    # 提取所有arXiv链接
    links = processor.extract_arxiv_links()
    print("提取到的arXiv链接:", links)

    # 更新文件内容
    links = processor.extract_arxiv_pdf_links()

    fetcher = ArxivAbstractFetcher(links, storage_path)

    # 获取摘要并存储
    fetcher.fetch_and_store_abstracts()


if __name__ == "__main__":
    main()
