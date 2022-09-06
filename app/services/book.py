from asyncpg.pool import Pool
from asyncpg.connection import Connection
from ..models import Book, BooksBorrow, User

class BookService:
    
    def __init__(self, pool: Pool) -> None:
        self.pool = pool
    
    async def count(self) -> int:
        total: int = 0
        con: Connection
        async with self.pool.acquire() as con:
            total = await con.fetchval('select count(id) from book')
            
        return total
    
    async def find_all(self, offset: int, limit: int) -> list[Book]:
        lb: list[Book] = []
        con: Connection
        async with self.pool.acquire() as con:
            lx = await con.fetch('select * from book order by title offset $1 limit $2', offset, limit)
            for x in lx:
                m = dict(x)
                o = Book(**m)
                if o.qty < 1:
                    resx = await con.fetch('select end_date from books_borrow where book_id = $1 order by end_date limit 1', o.id)
                    if len(resx) > 0:
                        o.return_date = resx[0]['end_date']
                        
                lb.append(o)
                
        return lb
    
    async def count_current_books_borrow_by_userId(self, user_id: int) -> int:
        total: int = 0
        con: Connection
        async with self.pool.acquire() as con:
            total = await con.fetchval('select count(book_id) from books_borrow where user_id = $1 and return_date is NULL', user_id)
            
        return total
    
    async def find_all_current_books_borrow_by_userId(self, user_id: int, offset: int, limit: int) -> list[BooksBorrow]:
        lb: list[BooksBorrow] = []
        con: Connection
        async with self.pool.acquire() as con:
            lx = await con.fetch('select bb.*, b.title, b.author, b.qty, b.isbn, u.username from books_borrow bb inner join book b on bb.book_id = b.id inner join "user" u on bb.user_id = u.id where bb.user_id = $1 and bb.return_date is NULL order by bb.start_date offset $2 limit $3', user_id, offset, limit)
            for x in lx:
                m = dict(x)
                o = BooksBorrow(**m)
                o.set(m)
                lb.append(o)
                
        return lb
    
    async def count_history_books_borrow_by_userId(self, user_id: int) -> int:
        total: int = 0
        con: Connection
        async with self.pool.acquire() as con:
            total = await con.fetchval('select count(book_id) from books_borrow where user_id = $1 and return_date is not NULL', user_id)
            
        return total
    
    async def find_all_history_books_borrow_by_userId(self, user_id: int, offset: int, limit: int) -> list[BooksBorrow]:
        lb: list[BooksBorrow] = []
        con: Connection
        async with self.pool.acquire() as con:
            lx = await con.fetch('select bb.*, b.title, b.author, b.qty, b.isbn, u.username from books_borrow bb inner join book b on bb.book_id = b.id inner join "user" u on bb.user_id = u.id where bb.user_id = $1 and bb.return_date is not NULL order by bb.start_date offset $2 limit $3', user_id, offset, limit)
            for x in lx:
                m = dict(x)
                o = BooksBorrow(**m)
                o.set(m)
                lb.append(o)
                
        return lb
    
    async def count_all_books_borrow(self) -> int:
        total: int = 0
        con: Connection
        async with self.pool.acquire() as con:
            total = await con.fetchval('select count(book_id) from books_borrow')
            
        return total
    
    async def find_all_books_borrow(self, offset: int, limit: int) -> list[BooksBorrow]:
        lb: list[BooksBorrow] = []
        con: Connection
        async with self.pool.acquire() as con:
            lx = await con.fetch('select bb.*, b.*, u.username from books_borrow bb inner join book b on bb.book_id = b.id inner join "user" u on bb.user_id = u.id order by bb.start_date offset $1 limit $2', offset, limit)
            for x in lx:
                m = dict(x)
                o = BooksBorrow(**m)
                b = Book(**m)
                o.set(m)
                lb.append(o)
                
        return lb
    
    async def is_book_available(self, id: int) -> bool:
        b: bool = False
        con: Connection
        async with self.pool.acquire() as con:
            res = await con.fetch('select * from book where id = $1 and qty > 0 limit 1', id)
            if len(res) > 0:
                b = True
                
        return b
    
    async def is_borrow_limit_reached(self, user_id: int) -> bool:
        b: bool = False
        con: Connection
        async with self.pool.acquire() as con:
            n = await con.fetchval('select count(user_id) from books_borrow where user_id = $1 and return_date is NULL', user_id)
            if n == 10:
                b = True
                
        return b
    
    async def find_by_ISBN(self, isbn: str) -> Book | None:
        o: Book = None
        con: Connection
        async with self.pool.acquire() as con:
            res = await con.fetch('select * from book where isbn = $1 limit 1', isbn)
            if len(res) > 0:
                m = dict(res[0])
                o = Book(**m)
                
        return o
    
    async def return_borrow(self, book_id: int, user_id: int):
        con: Connection
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute('update books_borrow set return_date = now() where book_id = $1 and user_id = $2', book_id, user_id)
                await con.execute('update book set qty = qty + 1 where id = $1', book_id)
                
    async def register_borrow(self, book_id: int, user_id: int):
        con: Connection
        async with self.pool.acquire() as con:
            async with con.transaction():
                await con.execute("insert into books_borrow (has_renew, start_date, end_date, book_id, user_id) values(false, now(), now() + INTERVAL '30 day', $1, $2)", book_id, user_id)
                await con.execute('update book set qty = qty - 1 where id = $1', book_id)
                
    async def renew_borrow(self, id: int, book_id: int, user_id: int):
        con: Connection
        async with self.pool.acquire() as con:
            await con.execute("update books_borrow set has_renew = true, end_date = end_date + INTERVAL '30 day' where id = $1 and book_id = $2 and user_id = $3 and return_date is NULL and has_renew is not true", id, book_id, user_id)