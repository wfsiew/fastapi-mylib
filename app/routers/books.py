from fastapi import APIRouter, Response, Depends, HTTPException, status
from ..models import Pager, BooksBorrow, Book, User
from ..services.book import BookService
from ..services.user import UserService
from ..dto.book import RegisterBookDto
from ..dependencies import get_book_service, get_current_user, get_user_service
import logging

router = APIRouter(prefix='/book', tags=['book'])
logger = logging.getLogger(__name__)


@router.get('/available', response_model=list[Book])
async def list_books(
    response: Response, _page: int = 1, _limit: int = 20, 
    bookService: BookService = Depends(get_book_service)
):
    try:
        lx: list[Book] = []
        total: int = await bookService.count()
        pg = Pager(total, _page, _limit)
        lx = await bookService.find_all(pg.lowerbound, pg.pagesize)
        response.headers['x-total-count'] = str(total)
        response.headers['x-total-page'] = str(pg.totalpages)
        return lx
    
    except Exception as e:
        logger.error(e)
        raise

@router.get('/borrow/current', response_model=list[BooksBorrow])
async def list_books_current(
    response: Response, _page: int = 1, _limit: int = 20, 
    bookService: BookService = Depends(get_book_service), 
    current_user: User = Depends(get_current_user)
):
    try:
        lx: list[BooksBorrow] = []
        total: int = await bookService.count_current_books_borrow_by_userId(current_user.id)
        pg = Pager(total, _page, _limit)
        lx = await bookService.find_all_current_books_borrow_by_userId(current_user.id, pg.lowerbound, pg.pagesize)
        response.headers['x-total-count'] = str(total)
        response.headers['x-total-page'] = str(pg.totalpages)
        return lx
    
    except Exception as e:
        logger.error(e)
        raise

@router.get('/borrow/history', response_model=list[BooksBorrow])
async def list_books_history(
    response: Response, _page: int = 1, _limit: int = 20, 
    bookService: BookService = Depends(get_book_service), 
    current_user: User = Depends(get_current_user)
):
    try:
        lx: list[BooksBorrow] = []
        total: int = await bookService.count_history_books_borrow_by_userId(current_user.id)
        pg = Pager(total, _page, _limit)
        lx = await bookService.find_all_history_books_borrow_by_userId(current_user.id, pg.lowerbound, pg.pagesize)
        response.headers['x-total-count'] = str(total)
        response.headers['x-total-page'] = str(pg.totalpages)
        return lx
    
    except Exception as e:
        logger.error(e)
        raise

@router.get('/borrow/all', response_model=list[BooksBorrow])
async def list_books_all(
    response: Response, _page: int = 1, _limit: int = 20, 
    bookService: BookService = Depends(get_book_service), 
    current_user: User = Depends(get_current_user)
):
    try:
        lx: list[BooksBorrow] = []
        total: int = await bookService.count_all_books_borrow()
        pg = Pager(total, _page, _limit)
        lx = await bookService.find_all_books_borrow(pg.lowerbound, pg.pagesize)
        response.headers['x-total-count'] = str(total)
        response.headers['x-total-page'] = str(pg.totalpages)
        return lx
    
    except Exception as e:
        logger.error(e)
        raise

@router.post('/borrow/register')
async def register_book(
    data: RegisterBookDto, 
    bookService: BookService = Depends(get_book_service), 
    userService: UserService = Depends(get_user_service), 
    current_user: User = Depends(get_current_user)
):
    try:
        book = await bookService.find_by_ISBN(data.isbn)
        user = await userService.find_by_username(data.username)
        if book and user:
            x = await bookService.is_borrow_limit_reached(user.id)
            if x:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Maximum limit of borrow books reached'
                )
            
            b = await bookService.is_book_available(book.id)
            if b:
                await bookService.register_borrow(book.id, user.id)
                return {
                    'success': 1
                }
                
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Book not available'
                )
                
        else:
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Book not found'
                )
                
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='User not found'
                )
                
    except HTTPException:
        pass
    
    except Exception as e:
        logger.error(e)
        raise
            
@router.post('/borrow/return')
async def return_book(
    data: RegisterBookDto, 
    bookService: BookService = Depends(get_book_service), 
    userService: UserService = Depends(get_user_service), 
    current_user: User = Depends(get_current_user)
):
    try:
        book = await bookService.find_by_ISBN(data.isbn)
        user = await userService.find_by_username(data.username)
        if book and user:
            await bookService.return_borrow(book.id, user.id)
            return {
                'success': 1
            }
            
        else:
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Book not found'
                )
                
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='User not found'
                )
                
    except HTTPException:
        pass
                
    except Exception as e:
        logger.error(e)
        raise
            
@router.post('/borrow/renew/{id}/{book_id}')
async def renew_book(
    id: int,
    book_id: int,
    bookService: BookService = Depends(get_book_service), 
    current_user: User = Depends(get_current_user)
):
    try:
        await bookService.renew_borrow(id, book_id, current_user.id)
        return {
            'success': 1
        }
        
    except Exception as e:
        logger.error(e)
        raise