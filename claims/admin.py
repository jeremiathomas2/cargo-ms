from django.contrib import admin
from .models import Claim, ClaimDocument


class ClaimDocumentInline(admin.TabularInline):
    model = ClaimDocument
    extra = 0
    readonly_fields = ('uploaded_by', 'created_at')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'claim_type', 'status', 'severity', 'claimed_value', 'approved_value', 'assigned_to', 'organization', 'created_at')
    list_filter = ('claim_type', 'status', 'severity')
    search_fields = ('claim_number', 'description')
    readonly_fields = ('resolved_at', 'created_at', 'updated_at')
    inlines = [ClaimDocumentInline]


@admin.register(ClaimDocument)
class ClaimDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'claim', 'document_type', 'uploaded_by', 'created_at')
    list_filter = ('document_type',)
    search_fields = ('title', 'claim__claim_number')
    readonly_fields = ('created_at',)
