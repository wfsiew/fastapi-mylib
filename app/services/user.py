from asyncpg.pool import Pool
from asyncpg.connection import Connection
from ..models import User
import bcrypt

class UserService:
    
    def __init__(self, pool: Pool) -> None:
        self.pool = pool
        
    async def find_by_Id(self, id: int) -> User | None:
        o: User = None
        con: Connection
        async with self.pool.acquire() as con:
            res = await con.fetch('select * from "user" where id = $1 limit 1', id)
            if len(res) > 0:
                m = dict(res[0])
                o = User(**m)
                await o.set_roles(con)
                
        return o
    
    async def find_by_username(self, username: str) -> User | None:
        o: User = None
        con: Connection
        async with self.pool.acquire() as con:
            res = await con.fetch('select * from "user" where username = $1 limit 1', username)
            if len(res) > 0:
                m = dict(res[0])
                o = User(**m)
                await o.set_roles(con)
                
        return o
    
    async def save(self, o: User):
        con: Connection
        bpwd = bcrypt.hashpw(o.password.encode('utf-8'), bcrypt.gensalt(rounds=10))
        pwd = str(bpwd)
        async with self.pool.acquire() as con:
            async with con.transaction():
                res = await con.execute('''insert into "user" (id, username, password) values(nextval('user_id_seq'),$1,$2) returning id as user_id''', o.username, pwd)
                for r in o.roles:
                    await con.execute('insert into user_role (user_id, role_id) values($1, $2)', res[0]['user_id'], r.id)
                    
    def validate_credentials(self, user: User, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))