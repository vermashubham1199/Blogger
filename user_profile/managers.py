from django.db.models import Manager, Count


class GraphManager(Manager):

    def count_total(self, user):
        total_value = self.get_queryset().filter(blog__owner=user).values('created_at__date').annotate(total=Count('id')).values('created_at__date', 'total').order_by('created_at__date')
        return total_value
    
    def count_blog_total(self, blog):
        total_value = self.get_queryset().filter(blog=blog).values('created_at__date').annotate(total=Count('id')).values('created_at__date', 'total').order_by('created_at__date')
        return total_value