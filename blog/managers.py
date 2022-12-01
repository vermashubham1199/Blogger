from django.db import models

class CategoryManager(models.Manager):

    def user_recomendation(self):
        cat = self.get_queryset().raw('''WITH x 
                                          AS(
                                            SELECT 
                                                 c.id AS c_id
                                                ,c.name AS c_name
                                                ,b.name AS b_name
                                                ,b.id AS b_id
                                                ,l.id AS l_id
                                                ,*
                                                ,COUNT(l.like) OVER(PARTITION BY c.id, b.id) AS like_count
                                          FROM blog_category AS c
                                          JOIN blog_likecat AS f On f.category_id = c.id
                                          JOIN blog_blog AS b ON b.category_id = c.id 
                                          JOIN blog_like As l ON b.id = l.blog_id
                                          WHERE l.like = True
                                          ),
                                          y AS
                                          (SELECT 
                                                *,
                                                DENSE_RANK() OVER(PARTITION BY x.c_id, x.b_id ORDER BY like_count DESC) AS rank
                                          FROM x)
                                          SELECT * FROM y WHERE y.rank <= 5''')
        temp_dict = {}
        for c in cat:
            if c.b_id not in temp_dict:
                temp_dict[c.b_id] = c
        return [t for t in temp_dict.values()]

    def anonymous_recomendation(self):
        cat = self.get_queryset().raw('''WITH x 
                                          AS(
                                            SELECT 
                                                 c.id AS c_id
                                                ,c.name AS c_name
                                                ,b.name AS b_name
                                                ,b.id AS b_id
                                                ,l.id AS l_id
                                                ,*
                                                ,COUNT(l.like) OVER(PARTITION BY c.id, b.id) AS like_count
                                          FROM blog_category AS c 
                                          JOIN blog_blog AS b ON b.category_id = c.id 
                                          JOIN blog_like As l ON b.id = l.blog_id
                                          WHERE l.like = True
                                          ),
                                          y AS
                                          (SELECT 
                                                *,
                                                DENSE_RANK() OVER(PARTITION BY x.c_id, x.b_id ORDER BY like_count DESC) AS rank
                                          FROM x)
                                          SELECT * FROM y WHERE y.rank <= 5''')
        temp_dict = {}
        for c in cat:
            if c.b_id not in temp_dict:
                temp_dict[c.b_id] = c
        return [t for t in temp_dict.values()]