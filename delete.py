from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Post

async def clean_soft_deleted(session: AsyncSession):
    # Вычисляем даты для сравнения:
    # Пользователи, удалённые более 180 дней назад (6 месяцев)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    # Посты, удалённые более 7 дней назад (1 неделя)
    one_week_ago = datetime.utcnow() - timedelta(days=7)

    # Ищем пользователей, у которых установлен флаг удаления
    # и дата удаления более 6 месяцев назад
    users_to_delete = await session.execute(
        select(User)
        .where(User.is_deleted == True)
        .where(User.deleted_at <= six_months_ago)
    )
    # Проходим по найденным пользователям и физически удаляем их из БД
    for user in users_to_delete.scalars():
        await session.delete(user)

    # Аналогично для постов:
    # Ищем посты с флагом удаления и датой удаления более недели назад
    posts_to_delete = await session.execute(
        select(Post)
        .where(Post.is_deleted == True)
        .where(Post.deleted_at <= one_week_ago)
    )
    # Физически удаляем найденные посты
    for post in posts_to_delete.scalars():
        await session.delete(post)

    # Сохраняем изменения в базе данных
    await session.commit()
