import arxiv
from datetime import date
from typing import List, Optional
from app.models.paper import Paper


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

