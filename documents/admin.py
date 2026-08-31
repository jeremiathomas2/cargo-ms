from django.contrib import admin
from .models import DocumentTemplate, Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ('version_number', 'file', 'notes', 'created_by', 'created_at')


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'document_type', 'is_active', 'organization', 'created_at')
    list_filter = ('document_type', 'is_active')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_number', 'title', 'document_type', 'status', 'version', 'organization', 'created_at')
    list_filter = ('document_type', 'status')
    search_fields = ('document_number', 'title')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DocumentVersionInline]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'created_by', 'created_at')
    list_filter = ()
    search_fields = ('document__document_number',)
    readonly_fields = ('created_at',)
