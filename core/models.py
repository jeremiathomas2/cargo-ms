from django.db import models
from django.utils import timezone
from uuid import uuid4


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        return super().get_queryset()

    def deleted_only(self):
        return super().get_queryset().filter(is_deleted=True)

    def hard_delete_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def restore(self):
        return self.update(is_deleted=False, deleted_at=None)

    def with_deleted(self):
        return super().all()

    def deleted_only(self):
        return self.filter(is_deleted=True)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(TimeStampedModel):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta(TimeStampedModel.Meta):
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def hard_delete(self):
        super().delete()


class UUIDModel(TimeStampedModel):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        db_index=True,
    )

    class Meta(TimeStampedModel.Meta):
        abstract = True


class OrganizationScopedModel(TimeStampedModel):
    organization = models.ForeignKey(
        'saas_config.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
        related_name='%(app_label)s_%(class)s_set',
    )

    class Meta(TimeStampedModel.Meta):
        abstract = True
