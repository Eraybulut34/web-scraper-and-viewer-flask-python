from flask import Flask, render_template, request, abort
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from config import Config
from utils import setup_logger, retry, truncate_text

logger = setup_logger(__name__)

app = Flask(__name__)

class DatabaseConnection:
    """Context manager for database connections."""
    
    def __init__(self):
        self.conn = None
        self.cur = None
    
    def __enter__(self):
        self.conn = psycopg2.connect(Config.get_database_url())
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        return self.cur
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()

@app.route('/')
def index():
    """Home page view."""
    try:
        category = request.args.get('category')
        with DatabaseConnection() as cur:
            if category:
                cur.execute(
                    'SELECT * FROM news WHERE category = %s ORDER BY created_at DESC',
                    (category,)
                )
            else:
                cur.execute('SELECT * FROM news ORDER BY created_at DESC')
            news = cur.fetchall()
            
            # Process news content
            for article in news:
                article['content'] = truncate_text(article['content'])
            
            return render_template('index.html', news=news, current_category=category)
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}")
        abort(500)

@app.route('/news/<int:id>')
def news_detail(id: int):
    """News detail view."""
    try:
        with DatabaseConnection() as cur:
            cur.execute('SELECT * FROM news WHERE id = %s', (id,))
            news = cur.fetchone()
            
            if not news:
                abort(404)
            
            # Get related articles
            cur.execute(
                'SELECT * FROM news WHERE category = %s AND id != %s ORDER BY created_at DESC LIMIT 3',
                (news['category'], id)
            )
            related_news = cur.fetchall()
            
            return render_template('detail.html', news=news, related_news=related_news)
    except Exception as e:
        logger.error(f"Error in detail view: {str(e)}")
        abort(500)

@app.route('/categories')
def categories():
    """Categories view."""
    try:
        with DatabaseConnection() as cur:
            cur.execute("""
                SELECT category, COUNT(*) as count 
                FROM news 
                GROUP BY category 
                ORDER BY count DESC
            """)
            categories = cur.fetchall()
            return render_template('categories.html', categories=categories)
    except Exception as e:
        logger.error(f"Error in categories view: {str(e)}")
        abort(500)

@app.errorhandler(404)
def page_not_found(e):
    """404 error handler."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 error handler."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 