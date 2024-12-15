from fastapi.exceptions import HTTPException
from typing import Optional, Dict, Any


# class TemplateException(Exception):
#     def __init__(self, status_code: int, detail: Any = None, loc: str = None, 
#                  headers: Optional[Dict[str, Any]] = None
#     ) -> None:
#         self.status_code=status_code
#         self.detail=detail
#         self.loc=loc
#         self.headers=headers

class RedirectException(Exception):
    def __init__(self, status_code: int, detail: Any = None, loc: str = None, 
                 headers: Optional[Dict[str, Any]] = None
    ) -> None:
        self.status_code=status_code
        self.detail=detail
        self.loc=loc
        self.headers=headers