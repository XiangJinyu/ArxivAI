SUMMARY_PROMPT = """
请用一句话总结以下学术论文摘要的核心创新点。你的总结应：
1. 突出研究的主要贡献和创新方法
2. 清晰阐述解决的关键问题
3. 使用简洁而信息丰富的语言
4. 遵循"[研究（论文的方法名）]通过[创新方法]解决了[关键问题]"的结构
5. 确保信息准确性
6. 严格控制在50个字以内

你的总结应让读者立即理解研究的核心创新和价值。
使用中文。
"""

CLASSIFY_PROMPT = """
**Method Category:**  
- **Reason:** Focused on logical reasoning and problem-solving  
- **Decision:** Focused on agents making choices between alternatives  
- **Plan:** Focused on agents formulating strategies and executing sequential actions  
- **Memory:** Focused on information storage and retrieval  
- **Tool:** Related to external tools used by agents/LLMs  
- **Reward:** Reinforcement learning and reward optimization  
- **World Model:** Environmental understanding and prediction capabilities  
- **Device-Operation:** Interaction capabilities with devices or systems, such as mobile phones, computers, and the internet  
- **Robotics:** Physical robotics  
- **Self-Improvement:** Self-learning, capability enhancement, and optimization of intelligent systems  
- **Multi-Agent:** Collaboration and interaction between intelligent agents  
- **Security:** Safety and security considerations  
- **Other:** Methods not covered in the above categories  

**Article Type Category:**  
- **Problem Solving:** (Primarily focused on solving problems)  
  - **Textual Reasoning:** Math, coding, and QA tasks  
  - **Multimodal Reasoning:** Cross-modal reasoning tasks  
  - **Textual Open-ended Tasks:** Creative text generation  
  - **Multimodal Open-ended Tasks:** Creative multimodal tasks  
- **Theory:** Theoretical research and frameworks (introducing a new method)  
- **Survey:** Literature reviews and field overviews  
- **Benchmark:** Datasets for performance evaluation and testing (introducing a new dataset)  
- **Other:** Types not covered in the above categories  

Output Format:
<method>[reason, decision, plan, memory, tool, reward, world_model, device_operation, robotics, self_improvement, multi_agent, security, other]</method>
<type>[textual_reasoning, multimodal_reasoning, textual_open_ended_tasks, multimodal_open_ended_tasks, theory, survey, benchmark, other]</type>

Analyze the abstract and classify it:
1. Key points (2-3 bullet points)
2. Main innovation (1 sentence)
3. Classification:
   <method>Select ONE</method>
   <type>Select ONE</type>
Provide concise responses in English. Strictly adhere to the format.
"""