import httpx
import json
from typing import Dict, List
from storycraft.core.logger import setup_logger

logger = setup_logger()

class TextGenerator:
    """使用豆包/通义千问生成儿童故事"""

    def __init__(self, api_key: str, api_endpoint: str, model: str):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.model = model
        self.client = httpx.Client(timeout=60.0)

    def generate_story(self, idea: str, character: str, num_scenes: int, chinese_only: bool = False) -> Dict:
        """生成故事

        Args:
            idea: 故事点子/创意描述（用户输入的故事想法）
            character: 主角名字
            num_scenes: 场景数量
            chinese_only: 是否只生成中文（不生成英文翻译）

        Returns:
            包含场景列表和角色描述的字典
        """
        logger.info(f"开始生成故事: idea={idea[:50]}..., character={character}, num_scenes={num_scenes}, chinese_only={chinese_only}")

        if not idea or not character:
            raise ValueError("故事点子和主角名字不能为空")

        if num_scenes < 1 or num_scenes > 30:
            raise ValueError("场景数量必须在 1-30 之间")

        prompt = self._build_prompt(idea, character, num_scenes, chinese_only)
        logger.info(f"已构建提示词")

        response = self._call_api(prompt)
        logger.info(f"AI API 调用成功")

        result = self._parse_response(response, num_scenes)
        logger.info(f"成功解析 {len(result['scenes'])} 个场景")

        return result

    def _build_prompt(self, idea: str, character: str, num_scenes: int, chinese_only: bool = False) -> str:
        """构建 AI 提示词"""
        if chinese_only:
            # 只生成中文故事，不生成图片提示词
            prompt = f"""请为3-5岁的儿童创作一个绘本故事（仅中文版本）。

故事创意：{idea}
主角：{character}
场景数量：{num_scenes}个场景

要求：
1. 基于用户提供的"故事创意"展开完整故事
2. 语言简单易懂，适合3-5岁儿童理解
3. 有重复性元素，方便儿童记忆
4. 每个场景1-2句话，情节清晰
5. 充满温馨和正能量
6. 故事要有起承转合，逻辑连贯

请按照以下 JSON 格式输出（不要包含其他文字）：
{{
  "character_description": "主角的固定外貌特征描述（英文），包括毛发颜色、服装、配饰等细节",
  "scenes": [
    {{
      "text": "场景的文字描述（中文）"
    }}
  ]
}}"""
        else:
            # 生成中英文双语版本（包含图片提示词）
            prompt = f"""请为3-5岁的儿童创作一个绘本故事（中英文双语版本）。

故事创意：{idea}
主角：{character}
场景数量：{num_scenes}个场景

要求：
1. 基于用户提供的"故事创意"展开完整故事
2. 语言简单易懂，适合3-5岁儿童理解
3. 有重复性元素，方便儿童记忆
4. 每个场景1-2句话，情节清晰
5. 充满温馨和正能量
6. 故事要有起承转合，逻辑连贯
7. **重要**：每个场景需要提供中英文双语版本

**图片要求（重要）**：
- 首先为"{character}"设计固定外貌特征（毛发颜色、眼睛、服装、配饰等）
- 所有场景必须保持角色外貌完全一致
- 场景之间保持连续性，画面风格统一
- 每个场景的 image_prompt 必须包含角色的固定特征描述

请按照以下 JSON 格式输出（不要包含其他文字）：
{{
  "character_description": "主角的固定外貌特征描述（英文），包括毛发颜色、服装、配饰等细节",
  "scenes": [
    {{
      "text": "场景的文字描述（中文）",
      "text_en": "The scene description in English, simple and easy for children to understand",
      "image_prompt": "适合AI绘画的场景详细描述（英文），必须包含主角的固定特征，描述动作、表情、场景、构图等"
    }}
  ]
}}"""

        return prompt

    def _call_api(self, prompt: str) -> str:
        """调用 AI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的儿童绘本作家,擅长创作温馨、简单、富有教育意义的故事。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8
        }

        response = self.client.post(
            f"{self.api_endpoint}/chat/completions",
            headers=headers,
            json=payload
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    def _parse_response(self, response: str, num_scenes: int) -> Dict:
        """解析 API 响应"""
        try:
            # 尝试提取 JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]

            data = json.loads(json_str)
            scenes = data.get("scenes", [])
            character_description = data.get("character_description", "")

            if len(scenes) != num_scenes:
                # 如果场景数量不对，进行调整
                scenes = scenes[:num_scenes]

            return {
                "scenes": scenes,
                "character_description": character_description
            }

        except (json.JSONDecodeError, KeyError) as e:
            # 如果解析失败，返回默认场景
            logger.error(f"解析响应失败: {e}")
            return {
                "scenes": [
                    {
                        "text": f"场景 {i+1}",
                        "image_prompt": f"Scene {i+1} for children's book"
                    }
                    for i in range(num_scenes)
                ],
                "character_description": ""
            }

    def translate_scene(self, text: str) -> str:
        """翻译单个场景的文本为英文

        Args:
            text: 中文场景文本

        Returns:
            英文翻译
        """
        prompt = f"""请将以下儿童绘本的中文场景文本翻译成英文。

原文：{text}

要求：
1. 保持简单易懂，适合3-5岁儿童理解
2. 保持温馨和友好的语气
3. 不要改变原意，只做语言转换
4. 直接输出翻译结果，不要包含其他文字

英文翻译："""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的儿童文学翻译，擅长将中文故事翻译成简单易懂的英文。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3
        }

        response = self.client.post(
            f"{self.api_endpoint}/chat/completions",
            headers=headers,
            json=payload
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    def translate_scenes_batch(self, scenes: list) -> list:
        """批量翻译场景文本为英文

        Args:
            scenes: 场景列表，每个场景包含 'text' 字段

        Returns:
            英文翻译列表，与输入scenes顺序一致
        """
        # 构建批量翻译请求
        scenes_text = "\n".join([f"{idx+1}. {scene['text']}" for idx, scene in enumerate(scenes)])

        prompt = f"""请将以下儿童绘本的中文场景文本批量翻译成英文。

原文：
{scenes_text}

要求：
1. 保持简单易懂，适合3-5岁儿童理解
2. 保持温馨和友好的语气
3. 不要改变原意，只做语言转换
4. 按照原文顺序，每一行输出一个翻译结果
5. 只输出翻译结果，不要包含序号或其他文字

英文翻译："""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的儿童文学翻译，擅长将中文故事翻译成简单易懂的英文。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3
        }

        response = self.client.post(
            f"{self.api_endpoint}/chat/completions",
            headers=headers,
            json=payload
        )

        response.raise_for_status()
        data = response.json()

        # 解析批量翻译结果
        translations_text = data["choices"][0]["message"]["content"].strip()
        translations = [line.strip() for line in translations_text.split('\n') if line.strip()]

        # 确保翻译数量匹配，否则降级为逐个翻译
        if len(translations) != len(scenes):
            logger.warning(f"翻译数量({len(translations)})与场景数量({len(scenes)})不匹配，使用逐个翻译")
            return [self.translate_scene(scene['text']) for scene in scenes]

        return translations

    def generate_image_prompts_batch(self, scenes: list, character_description: str = "") -> list:
        """根据中文故事批量生成图片提示词

        Args:
            scenes: 场景列表，每个场景包含 'text' 字段
            character_description: 角色外貌描述，用于保持角色一致性

        Returns:
            图片提示词列表，与输入scenes顺序一致
        """
        # 构建批量请求
        scenes_text = "\n".join([f"{idx+1}. {scene['text']}" for idx, scene in enumerate(scenes)])

        character_desc_note = f"\n\n**角色固定特征（必须包含在所有图片提示词中）**：\n{character_description}" if character_description else ""

        prompt = f"""请为以下儿童绘本故事场景批量生成AI绘画提示词（英文）。

原文：
{scenes_text}
{character_desc_note}

要求：
1. 提示词必须是英文
2. 每个场景的提示词要详细描述画面内容、角色动作、表情、场景、构图、光线等
3. 如果提供了角色固定特征，必须在每个提示词中包含这些特征，确保所有图片中角色外貌一致
4. 画面风格要统一，适合儿童绘本
5. 温馨、明亮、色彩丰富
6. 按照原文顺序，每一行输出一个英文提示词
7. 只输出英文提示词，不要包含序号或其他文字

英文提示词："""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的儿童绘本插画设计师，擅长为儿童故事创作温馨、生动的AI绘画提示词。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }

        response = self.client.post(
            f"{self.api_endpoint}/chat/completions",
            headers=headers,
            json=payload
        )

        response.raise_for_status()
        data = response.json()

        # 解析批量提示词结果
        prompts_text = data["choices"][0]["message"]["content"].strip()
        image_prompts = [line.strip() for line in prompts_text.split('\n') if line.strip()]

        # 确保提示词数量匹配
        if len(image_prompts) != len(scenes):
            logger.warning(f"提示词数量({len(image_prompts)})与场景数量({len(scenes)})不匹配，使用逐个生成")
            # 降级为逐个生成
            return [self._generate_single_image_prompt(scene['text'], character_description) for scene in scenes]

        return image_prompts

    def _generate_single_image_prompt(self, text: str, character_description: str = "") -> str:
        """为单个场景生成图片提示词

        Args:
            text: 中文场景文本
            character_description: 角色外貌描述

        Returns:
            英文图片提示词
        """
        char_desc = f"\n\n角色固定特征（必须包含）：{character_description}" if character_description else ""

        prompt = f"""请为以下儿童绘本场景生成AI绘画提示词（英文）。

场景内容：{text}
{char_desc}

要求：
1. 提示词必须是英文
2. 详细描述画面内容、角色动作、表情、场景、构图、光线等
3. 如果提供了角色固定特征，必须包含这些特征
4. 画面风格要适合儿童绘本，温馨、明亮、色彩丰富
5. 直接输出英文提示词，不要包含其他文字

英文提示词："""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的儿童绘本插画设计师，擅长为儿童故事创作温馨、生动的AI绘画提示词。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }

        response = self.client.post(
            f"{self.api_endpoint}/chat/completions",
            headers=headers,
            json=payload
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    def __del__(self):
        """清理 HTTP 客户端"""
        if hasattr(self, 'client'):
            self.client.close()
