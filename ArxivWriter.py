import json
import csv
from datetime import datetime

class ArixvWriter:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.papers = []

    def clean_category(self, category, index=None):
        """
        清理分类字符串:
        1. 移除外层[]
        2. 如果内部有多个分类(逗号分隔)，取第一个
        3. 如果还有嵌套[]，也一并清理
        """
        # 记录问题数据
        has_issue = False

        # 移除外层[]并清理空格
        cleaned = category.strip('[]').strip()

        # 检查是否有多个分类
        if ',' in cleaned:
            has_issue = True
            cleaned = cleaned.split(',')[0].strip()

        # 检查是否有嵌套[]
        if '[' in cleaned or ']' in cleaned:
            has_issue = True
            cleaned = cleaned.replace('[', '').replace(']', '').strip()

        if has_issue and index is not None:
            print(f"Found problematic category at index {index}: {category}")

        return cleaned

    def process_data(self):
        """加载 JSON 文件并解析数据"""
        with open(self.json_file_path, 'r', encoding='utf-8') as file:
            self.json_data = json.load(file)

        for url, details in self.json_data.items():
            title = details.get('title', '').replace('\n', ' ')  # 移除换行符
            link = details.get('link', '')
            abstract = details.get('abstract', '')
            published_date = details.get('published', '')
            year_month = self._get_year_month(published_date)
            method_category = self.clean_category(details.get('method', ''), link)
            paper_category = self.clean_category(details.get('type', ''), link)
            summary = details.get('summary', '')

            self.papers.append({
                'Title': title,
                'Link': link,
                'Abs': abstract,
                'Year-Month': year_month,
                'Summary': summary,
                'Method Category': method_category,
                'Paper Category': paper_category,
            })

    @staticmethod
    def _get_year_month(date_string):
        try:
            date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
            return date_obj.strftime('%Y-%m')
        except ValueError:
            return "Unknown"

    def save_to_csv(self, file_name):
        """保存为CSV文件"""
        if not self.papers:
            print("No papers to save. Process the data first.")
            return

        keys = ['Title', 'Link', 'Abs', 'Year-Month', 'Summary', 'Method Category', 'Paper Category']
        with open(file_name, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.papers)

        print(f"CSV file saved as {file_name}")

    # def create_anchor(self, method, category=None):
    #     """创建唯一的锚点ID"""
    #     method = method.split(' (')[0].lower().replace(' ', '-')
    #     if category:
    #         category = category.split(' (')[0].lower().replace(' ', '-')
    #         return f"{method}-{category}"
    #     return method

    def save_to_markdown(self, file_name):
        """保存为Markdown文件"""
        if not self.papers:
            print("No papers to save. Process the data first.")
            return

        # 整理论文按方法和类别分类
        organized_papers = {}
        for paper in self.papers:
            method = paper['Method Category']
            category = paper['Paper Category']
            if method not in organized_papers:
                organized_papers[method] = {}
            if category not in organized_papers[method]:
                organized_papers[method][category] = []
            organized_papers[method][category].append(paper)

        def create_anchor(method, category=None):
            """创建唯一的锚点ID，包含层级信息"""
            anchor = method.lower().replace(' ', '-').replace('(', '').replace(')', '')
            if category:
                anchor += '-' + category.lower().replace(' ', '-').replace('(', '').replace(')', '')
            return anchor

        # 写入Markdown
        with open(file_name, mode='w', encoding='utf-8') as file:
            file.write("# Table of Contents\n\n")
            for method in organized_papers:
                clean_method = method.split(' (')[0]  # 移除括号中的说明
                method_anchor = create_anchor(method)
                file.write(f"- [{clean_method}](#{method_anchor})\n")
                for category in organized_papers[method]:
                    clean_category = category.split(' (')[0]  # 移除括号中的说明
                    category_anchor = create_anchor(method, category)
                    file.write(f"  - [{clean_category}](#{category_anchor})\n")
            file.write("\n")

            for method, categories in organized_papers.items():
                clean_method = method.split(' (')[0]
                method_anchor = create_anchor(method)
                file.write(f"# {clean_method}\n")
                file.write(f"<a id=\"{method_anchor}\"></a>\n\n")  # 添加与大纲一致的锚点

                for category, papers in categories.items():
                    clean_category = category.split(' (')[0]
                    category_anchor = create_anchor(method, category)
                    file.write(f"## {clean_category}\n")
                    file.write(f"<a id=\"{category_anchor}\"></a>\n\n")  # 添加与大纲一致的锚点

                    for idx, paper in enumerate(papers, start=1):
                        file.write(f"### {idx}. {paper['Title']}\n")
                        file.write(f"- **Link**: [{paper['Link']}]({paper['Link']})\n")
                        file.write(f"- **Summary**: {paper['Summary']})\n")
                        file.write(f"- **Abstract**: {paper['Abs']}\n")
                        file.write(f"- **Year-Month**: {paper['Year-Month']}\n\n")

        print(f"Markdown file saved as {file_name}")


# Usage Example:
# Specify the path to the JSON file
json_file_path = 'abstracts_summary.json'

processor = ArixvWriter(json_file_path)
processor.process_data()  # 加载并解析数据
processor.save_to_csv("papers.csv")       # 保存为 CSV
processor.save_to_markdown("papers.md")  # 保存为 Markdown
