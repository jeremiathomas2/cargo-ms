import uuid

from django.db import models


class USSDSession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        TIMEOUT = "timeout", "Timeout"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    tracking_number = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    responses = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "USSD Session"
        verbose_name_plural = "USSD Sessions"

    def __str__(self):
        return f"USSD {self.session_id} - {self.phone_number}"


class IVRCall(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    call_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    tracking_number = models.CharField(max_length=100)
    duration_seconds = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.COMPLETED)
    transcript = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "IVR Call"
        verbose_name_plural = "IVR Calls"

    def __str__(self):
        return f"IVR {self.call_id} - {self.phone_number}"


class OfflineSyncQueue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=100)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="offline_sync_items",
    )
    action_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)
    synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Offline Sync Queue"
        verbose_name_plural = "Offline Sync Queues"

    def __str__(self):
        return f"Sync {self.device_id} - {self.action_type}"


class Translation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language_code = models.CharField(max_length=5)
    key = models.CharField(max_length=200, unique=True)
    value = models.TextField()
    context = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["language_code", "key"]
        verbose_name = "Translation"
        verbose_name_plural = "Translations"

    def __str__(self):
        return f"[{self.language_code}] {self.key}"
