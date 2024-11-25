from utils.response import responser, extract_content
from utils import logs
from prompts import SUMMARY_PROMPT, CLASSIFY_PROMPT
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor


class ArxivReader:
    def __init__(self, input_file, output_file, model="gpt-4o-mini"):
        self.input_file = input_file
        self.output_file = output_file
        self.model = model
        self.data = self._load_json(input_file)
        self.output_data = self._load_json(output_file, default={})
        self.total_entries = len(self.data)
        # 添加锁以确保文件写入的线程安全
        self._file_lock = asyncio.Lock()

    @staticmethod
    def _load_json(file_path, default=None):
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return default if default is not None else {}

    async def _save_entry(self, key, entry):
        """
        保存单个条目到输出文件
        :param key: 条目键
        :param entry: 条目内容
        """
        async with self._file_lock:
            self.output_data[key] = entry  # 更新内存中的数据
            # 直接写入全部数据
            with open(self.output_file, "w", encoding='utf-8') as file:
                json.dump(self.output_data, file, indent=4, ensure_ascii=False)
            logging.info(f"Entry {key} saved successfully.")

    async def _process_entry(self, key, entry):
        """
        处理单个条目
        :param key: 条目键
        :param entry: 条目内容
        :return: 处理后的条目
        """
        if key in self.output_data:
            logging.info(f"Skipping {key}, already exists in output.")
            return key, self.output_data[key]

        try:
            title = entry.get("title", "No title provided")
            abstract = entry.get("abstract", "No abstract provided")
            abstract_text = f"Title: {title}\nAbstract: {abstract}\n"
            summary_prompt = abstract_text + SUMMARY_PROMPT
            classify_prompt = abstract_text + CLASSIFY_PROMPT

            # 异步调用 LLM
            summary = await responser([{"role": "user", "content": summary_prompt}], self.model)
            classification = await responser([{"role": "user", "content": classify_prompt}], self.model)

            # 提取分类信息
            classify_type = extract_content(classification, "type")
            classify_method = extract_content(classification, "method")

            # 更新条目信息
            processed_entry = entry.copy()
            processed_entry.update({
                "summary": summary,
                "type": classify_type,
                "method": classify_method
            })

            # 立即保存这个条目
            await self._save_entry(key, processed_entry)
            return key, processed_entry

        except Exception as e:
            logging.error(f"Error processing entry {key}: {e}")
            return key, None

    async def summarize_all(self):
        sem = asyncio.Semaphore(30)  # 限制并发数量为10

        async def bounded_process(key, entry):
            async with sem:  # 使用信号量控制并发
                return await self._process_entry(key, entry)

        tasks = [bounded_process(key, entry)
                 for key, entry in self.data.items()]

        completed = 0
        for task in asyncio.as_completed(tasks):
            key, processed_entry = await task
            if processed_entry:
                completed += 1
                logging.info(f"Progress: {completed}/{self.total_entries}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    input_file = "abstracts.json"
    output_file = "abstracts_summary.json"

    reader = ArxivReader(input_file, output_file)
    asyncio.run(reader.summarize_all())