import arxiv
from datetime import datetime, timedelta, date
from typing import List, Optional
from app.models.paper import Paper


class ArxivService:

    @staticmethod
    def format_date_for_query(target_date: date) -> str:
        return target_date.strftime('%Y%m%d')

    @staticmethod
    def build_date_query(start_date: date, end_date: date) -> str:
        start_str = ArxivService.format_date_for_query(start_date)
        end_str = ArxivService.format_date_for_query(end_date)
        return f'submittedDate:[{start_str}*TO*{end_str}*]'

    @staticmethod
    def fetch_papers(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_results: int = 100,
        category: Optional[str] = None
    ) -> List[Paper]:
        """
        从 arXiv API 获取论文
        
        Args:
            start_date: 开始日期，默认为当日
            end_date: 结束日期，默认为当日
            max_results: 最大返回数量
            category: 论文类别（可选）
            
        Returns:
            论文列表
        """
        # 如果没有指定日期，默认使用当日
        today = date.today()
        if start_date is None:
            start_date = today
        if end_date is None:
            end_date = today
        
        date_query = ArxivService.build_date_query(start_date, end_date)
        
        if category:
            query = f'{date_query} AND cat:{category}'
        else:
            query = date_query
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = []
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
        
        return papers

