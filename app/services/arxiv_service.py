import arxiv
from datetime import date
from typing import List, Optional
from app.models.paper import Paper, PaperDetail, AISummary


class ArxivService:
    """使用 arxiv Python 库获取论文的服务类"""

    @staticmethod
    def fetch_papers(
        start_date: Optional[date] = None,
        max_results: int = 100,
        category: Optional[str] = None
    ) -> List[Paper]:
        """使用 arxiv Python 库获取论文"""
        # 如果没有指定开始日期，默认使用当日
        today = date.today()
        if start_date is None:
            start_date = today
        
        if category:
            query = f'cat:{category}'
        else:
            query = 'all'
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
        try:
            for result in search.results():
                paper = Paper(
                    arxiv_id=result.entry_id.split('/')[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    summary=result.summary,
                    published=result.published,
                    updated=result.updated,
                    pdf_url=result.pdf_url,
                    categories=result.categories,
                    entry_id=result.entry_id
                )
                papers.append(paper)
        except arxiv.UnexpectedEmptyPageError:
            pass
        
        return papers

    @staticmethod
    def fetch_paper_by_id(arxiv_id: str) -> Optional[PaperDetail]:
        """根据 arXiv ID 获取论文详情"""
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            results = list(search.results())
            
            if not results:
                return None
            
            result = results[0]
            
            paper = Paper(
                arxiv_id=result.entry_id.split('/')[-1],
                title=result.title,
                authors=[author.name for author in result.authors],
                summary=result.summary,
                published=result.published,
                updated=result.updated,
                pdf_url=result.pdf_url,
                categories=result.categories,
                entry_id=result.entry_id
            )
            
            # 生成 AI 摘要（目前使用 mock 数据）
            ai_summary = ArxivService._generate_ai_summary(paper)
            
            paper_detail = PaperDetail(
                **paper.dict(),
                ai_summary=ai_summary
            )
            
            return paper_detail
            
        except Exception:
            return None

    @staticmethod
    def _generate_ai_summary(paper: Paper) -> AISummary:
        """
        生成 AI 摘要（目前使用 mock 数据）
        
        Args:
            paper: 论文对象
            
        Returns:
            AI 摘要对象
        """
        # TODO: 后续接入真实的 AI 服务生成摘要
        return AISummary(
            overview=f"这是一篇关于 {paper.title} 的研究论文。该论文探讨了相关领域的重要问题，并提出了创新的解决方案。",
            background=f"在 {paper.categories[0] if paper.categories else '相关'} 领域，{paper.title} 的研究背景涉及多个重要方面。当前的研究现状存在一些挑战和局限性，需要进一步探索和改进。",
            methods=f"本研究采用了先进的方法和技术来解决提出的问题。核心方法包括数据收集、模型设计和实验验证等关键步骤，确保了研究的科学性和可靠性。",
            results=f"实验结果表明，所提出的方法在多个指标上取得了显著的改进。这些结果不仅验证了方法的有效性，还为后续研究提供了有价值的参考和启示。"
        )

