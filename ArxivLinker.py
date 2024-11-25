import re


class ArxivLinkProcessor:
    def __init__(self, markdown_path):
        """
        初始化类，接受Markdown文件路径
        :param markdown_path: Markdown文件路径
        """
        self.markdown_path = markdown_path
        self.markdown_text = self._read_markdown_file()

    def _read_markdown_file(self):
        """
        从Markdown文件中读取内容
        :return: Markdown文本内容
        """
        try:
            with open(self.markdown_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise Exception(f"文件 {self.markdown_path} 未找到！")

    def _write_markdown_file(self, updated_text):
        """
        将更新后的Markdown文本写回文件
        :param updated_text: 更新后的Markdown文本
        """
        with open(self.markdown_path, 'w', encoding='utf-8') as file:
            file.write(updated_text)

    def extract_arxiv_links(self):
        """
        提取Markdown中的所有arXiv链接
        :return: 一个包含arXiv链接的列表
        """
        arxiv_link_pattern = r'https?://arxiv\.org/(?:abs|pdf)/[0-9]+\.[0-9]+(?:v[0-9]+)?'
        return re.findall(arxiv_link_pattern, self.markdown_text)

    def convert_to_pdf_links(self, links):
        """
        将arXiv的abs链接转换为pdf链接
        :param links: 包含arXiv链接的列表
        :return: 转换后的链接列表
        """
        converted_links = []
        for link in links:
            if '/abs/' in link:
                converted_links.append(link.replace('/abs/', '/pdf/'))
            else:
                converted_links.append(link)
        return converted_links

    def extract_arxiv_pdf_links(self):
        """
        提取和转换Markdown中的arXiv链接
        :return: 转换为pdf链接的列表
        """
        # 提取所有的arXiv链接
        arxiv_links = self.extract_arxiv_links()

        # 将所有的链接转换为pdf格式
        converted_links = self.convert_to_pdf_links(arxiv_links)

        return converted_links


# 使用示例
if __name__ == "__main__":
    # 假设Markdown文件路径为example.md
    markdown_file_path = "link.md"

    # 初始化类并处理文件
    processor = ArxivLinkProcessor(markdown_file_path)

    # 提取所有arXiv链接
    links = processor.extract_arxiv_links()
    print("提取到的arXiv链接:", links)

    # 更新文件内容
    links = processor.extract_arxiv_pdf_links()
