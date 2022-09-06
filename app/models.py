from asyncpg.connection import Connection
from pydantic import BaseModel
import math, datetime

class Role(BaseModel):
    id: int
    name: str
    
class User(BaseModel):
    id: int
    username: str
    password: str | None = None
    roles: list[Role] = []
    
    async def set_roles(self, con: Connection):
        lr: list[Role] = []
        lx = await con.fetch('select ur.user_id, ur.role_id, r.id, r.name from user_role ur inner join role r on ur.role_id = r.id where ur.user_id = $1', self.id)
        for x in lx:
            m = dict(x)
            role = Role(**m)
            lr.append(role)
            
        self.roles = lr
        
class UserOut(BaseModel):
    id: int
    username: str
    roles: list[Role] = []
    
    async def set_roles(self, con: Connection):
        lr: list[Role] = []
        lx = await con.fetch('select ur.user_id, ur.role_id, r.id, r.name from user_role ur inner join role r on ur.role_id = r.id where ur.user_id = $1', self.id)
        for x in lx:
            m = dict(x)
            role = Role(**m)
            lr.append(role)
            
        self.roles = lr

class Book(BaseModel):
    id: int
    isbn: str
    title: str
    author: str
    qty: int
    return_date: datetime.datetime | None = None
    
class BooksBorrow(BaseModel):
    id: int
    has_renew: bool
    start_date: datetime.datetime
    end_date: datetime.datetime
    return_date: datetime.datetime | None = None
    book_id: int
    user_id: int
    book: Book | None = None
    user: UserOut | None = None
    
    def set(self, m: dict):
        b = Book(**m)
        b.id = self.book_id
        u = UserOut(**m)
        u.id = self.user_id
        u.username = m['username']
        self.book = b
        self.user = u

class Pager(object):
    
    def __init__(self, total: int, pagenum: int, pagesize: int):
        self.total = total
        self.pagenum = pagenum
        self.setpagesize(pagesize)

    @property
    def pagesize(self):
        return self._pagesize
    
    @pagesize.setter
    def pagesize(self, v):
        self.setpagesize(v)
        
    @property
    def startrow(self):
        if self.pagenum == 1:
            return (self.pagenum - 1) * self.pagesize
        
        return ((self.pagenum - 1) * self.pagesize) + 1
    
    @property
    def endrow(self):
        return self.upperbound
        
    @property
    def lowerbound(self):
        return (self.pagenum - 1) * self.pagesize
    
    @property
    def upperbound(self):
        upperbound = self.pagenum * self.pagesize
        
        if self.total < upperbound:
            upperbound = self.total
            
        return upperbound
    
    @property
    def hasnext(self):
        return True if self.total > self.upperbound else False
    
    @property
    def hasprev(self):
        return True if self.lowerbound > 0 else False
        
    @property
    def totalpages(self):
        return int(math.ceil(self.total / float(self.pagesize)))

    def setpagesize(self, pagesize):
        if (self.total < pagesize or pagesize < 1) and self.total > 0:
            self._pagesize = self.total
            
        else:
            self._pagesize = pagesize
            
        if self.totalpages < self.pagenum:
            self.pagenum = self.totalpages
            
        if self.pagenum < 1:
            self.pagenum = 1