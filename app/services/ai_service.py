import json
from typing import Optional
from app.config.settings import settings
from app.models.paper import Paper, AISummary, AIScoreDetail, TokenUsage
from zai import ZhipuAiClient


class AIService:
    """AI 服务类"""

    def __init__(self):
        """初始化 AI 客户端"""
        self.client = None
        if settings.zhipu_api_key:
            try:
                self.client = ZhipuAiClient(api_key=settings.zhipu_api_key)
            except Exception as e:
                print(f"初始化智谱 AI 客户端失败: {str(e)}")

    def generate(self, paper: Paper) -> Optional[AISummary]:
        """使用智谱 GLM 4.6 API 生成论文摘要和评分"""
        if not self.client:
            return None

        try:
            paper_info = f"""
论文标题: {paper.title}
作者: {', '.join(paper.authors)}
分类: {', '.join(paper.categories) if paper.categories else '未分类'}
摘要: {paper.summary[:1000]}  # 限制长度避免 token 过多
"""

            response = self.client.chat.completions.create(
                model=settings.zhipu_model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的学术论文分析助手。请仔细分析论文内容，提供结构化的摘要和多维度评分。

评分维度包括：
1. 创新性（30分）：是否提出突破性方法、架构或见解，能否开创新方向。参考高分论文标准：体系结构层面创新、范式转变。
2. 技术深度（25分）：技术实现的复杂度、完整性，是否有可复用的技术原语。
3. 实用价值（20分）：对学术界和工业界的实际影响力，是否解决关键痛点。
4. 实验充分性（15分）：实验设计是否完善，结果是否有足够说服力和可复现性。对于纯数学论文，证明的完备性相当于实验充分性。
5. 可理解性（10分）：论文组织结构和表达清晰度，是否易于把握核心思想。

总分范围：0-100分。请给出详细的评分推理过程。

推荐建议只能是"推荐"或"强烈推荐"两个选项。"""
                    },
                    {
                        "role": "user",
                        "content": f"请分析以下论文并返回结构化信息：\n\n{paper_info}"
                    }
                ],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "analyze_paper",
                            "description": "分析论文并返回结构化的摘要和多维度评分",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "score": {
                                        "type": "number",
                                        "description": "论文综合评分，基于多个维度综合评分，范围0-100分"
                                    },
                                    "detail": {
                                        "type": "object",
                                        "description": "评分详情",
                                        "properties": {
                                            "total_score": {
                                                "type": "number",
                                                "description": "总分，各维度评分之和，范围0-100分"
                                            },
                                            "innovation_score": {
                                                "type": "number",
                                                "description": "创新性评分，评估论文的创新程度和原创性，是否提出突破性方法、架构或见解，能否开创新方向，范围0-30分"
                                            },
                                            "technical_depth_score": {
                                                "type": "number",
                                                "description": "技术深度评分，评估论文的技术深度和复杂度，技术实现的复杂度、完整性，是否有可复用的技术原语，范围0-25分"
                                            },
                                            "practical_value_score": {
                                                "type": "number",
                                                "description": "实用价值评分，评估对学术界和工业界的实际影响力，是否解决关键痛点，范围0-20分"
                                            },
                                            "experiments_score": {
                                                "type": "number",
                                                "description": "实验充分性评分，评估实验设计的完善程度，结果是否有足够说服力和可复现性，范围0-15分"
                                            },
                                            "writing_score": {
                                                "type": "number",
                                                "description": "可理解性/写作质量评分，评估论文组织结构和表达清晰度，是否易于把握核心思想，范围0-10分"
                                            },
                                            "summary": {
                                                "type": "string",
                                                "description": "论文总结，简要总结论文的核心内容、方法和主要贡献"
                                            },
                                            "strengths": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                                "description": "论文优点列表，列出论文的主要优点和亮点"
                                            },
                                            "weaknesses": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                                "description": "论文缺点列表，列出论文的主要不足和局限性"
                                            },
                                            "recommendation": {
                                                "type": "string",
                                                "enum": ["推荐", "强烈推荐"],
                                                "description": "推荐建议"
                                            },
                                            "reasoning": {
                                                "type": "string",
                                                "description": "评分推理过程，详细说明评分依据和思考过程"
                                            }
                                        },
                                        "required": ["total_score", "innovation_score", "technical_depth_score", "practical_value_score", "experiments_score", "writing_score", "summary", "strengths", "weaknesses", "recommendation", "reasoning"]
                                    }
                                },
                                "required": ["score", "detail"]
                            }
                        }
                    }
                ],
                temperature=settings.zhipu_temperature
            )

            # 解析函数调用结果
            if response.choices and response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                if tool_call.function.name == "analyze_paper":
                    arguments = json.loads(tool_call.function.arguments)
                    detail_data = arguments.get("detail", {})
                    
                    # 构建 AIScoreDetail 对象
                    detail = AIScoreDetail(
                        total_score=detail_data.get("total_score"),
                        innovation_score=detail_data.get("innovation_score"),
                        technical_depth_score=detail_data.get("technical_depth_score"),
                        practical_value_score=detail_data.get("practical_value_score"),
                        experiments_score=detail_data.get("experiments_score"),
                        writing_score=detail_data.get("writing_score"),
                        summary=detail_data.get("summary"),
                        strengths=detail_data.get("strengths", []),
                        weaknesses=detail_data.get("weaknesses", []),
                        recommendation=detail_data.get("recommendation"),
                        reasoning=detail_data.get("reasoning"),
                        paper_id=paper.arxiv_id,
                        api_model=settings.zhipu_model,
                        api_request_id=getattr(response, 'id', None),
                        api_created_timestamp=getattr(response, 'created', None)
                    )
                    
                    # 获取 token 使用情况
                    token_usage = None
                    if hasattr(response, 'usage'):
                        usage = response.usage
                        token_usage = TokenUsage(
                            prompt_tokens=getattr(usage, 'prompt_tokens', None),
                            completion_tokens=getattr(usage, 'completion_tokens', None),
                            total_tokens=getattr(usage, 'total_tokens', None),
                            reasoning_length=getattr(usage, 'reasoning_length', None),
                            content_length=getattr(usage, 'content_length', None)
                        )
                    
                    return AISummary(
                        score=arguments.get("score"),
                        detail=detail,
                        token_usage=token_usage
                    )

            return None

        except Exception as e:
            print(f"AI 服务调用失败: {str(e)}")
            return None


ai_service = AIService()

