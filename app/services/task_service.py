import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, Callable, Any
from enum import Enum
from app.models.paper import Paper, AISummary
from app.services.ai_service import ai_service
from app.services.arxiv_service import ArxivService


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskInfo:
    """任务信息类"""
    def __init__(self, task_id: str, arxiv_id: str):
        self.task_id = task_id
        self.arxiv_id = arxiv_id
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.result: Optional[AISummary] = None
        self.error_message: Optional[str] = None

    def update_status(self, status: TaskStatus):
        """更新任务状态"""
        self.status = status
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.completed_at = datetime.now()

    def set_result(self, result: AISummary):
        """设置任务结果"""
        self.result = result
        self.status = TaskStatus.COMPLETED

    def set_error(self, error_message: str):
        """设置错误信息"""
        self.error_message = error_message
        self.status = TaskStatus.FAILED


class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_concurrent: int = 5):
        """初始化任务管理器"""
        self.max_concurrent = max_concurrent
        self.task_queue = asyncio.Queue()
        self._workers = []
        self._started = False
        self.tasks: Dict[str, TaskInfo] = {}
    
    def start(self):
        """启动worker pool"""
        if self._started:
            return
        for _ in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker())
            self._workers.append(worker)
        self._started = True
    
    async def _worker(self):
        """Worker协程，从队列中获取任务并执行"""
        while True:
            coro_factory = await self.task_queue.get()
            try:
                await coro_factory()
            except Exception as e:
                print(f"Task failed: {e}")
            finally:
                self.task_queue.task_done()
    
    async def submit_task(self, coro_factory: Callable[[], Any]):
        """提交任务到队列"""
        await self.task_queue.put(coro_factory)
    
    def create_task(self, arxiv_id: str) -> str:
        """创建新任务并返回任务ID"""
        task_id = str(uuid.uuid4())
        task_info = TaskInfo(task_id, arxiv_id)
        self.tasks[task_id] = task_info
        return task_id
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    async def start_task(self, task_id: str, arxiv_id: str):
        """启动任务"""
        task_info = self.get_task(task_id)
        if not task_info:
            return
        
        async def run_task():
            """在 worker 中执行的任务"""
            try:
                task_info.update_status(TaskStatus.PROCESSING)
                
                # 在线程池中执行同步的 IO 操作
                loop = asyncio.get_event_loop()
                paper = await loop.run_in_executor(
                    None, 
                    ArxivService.fetch_paper_by_id, 
                    arxiv_id
                )
                
                if paper is None:
                    task_info.set_error(f"未找到 arXiv ID 为 {arxiv_id} 的论文")
                    return
                
                # AI 服务调用也在线程池中执行
                result = await loop.run_in_executor(
                    None,
                    ai_service.generate,
                    paper
                )
                
                if result:
                    task_info.set_result(result)
                else:
                    task_info.set_error("AI评分生成失败")
            except Exception as e:
                task_info.set_error(f"任务执行失败: {str(e)}")
        
        # 提交任务到队列
        await self.submit_task(run_task)
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务（可选，用于内存管理）"""
        current_time = datetime.now()
        tasks_to_remove = []
        for task_id, task_info in self.tasks.items():
            age = (current_time - task_info.created_at).total_seconds() / 3600
            if age > max_age_hours:
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]


# 创建全局任务管理器实例
task_service = AsyncTaskManager(max_concurrent=5)

