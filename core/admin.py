from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count

from .models import Structure, PaymentHistory, EditRequest


# =========================================================
# 🏗 STRUCTURE ADMIN (CLEAN + SYNCHED + FRAUD LIGHT)
# =========================================================
@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):

    list_display = (
        "ts_id",
        "owner_name",
        "owner_phone",
        "town",
        "structure_type",
        "permit_badge",
        "fraud_badge",
        "collector",
        "created_at",
    )

    search_fields = ("ts_id", "owner_name", "owner_phone", "ghana_card")

    # ✅ NEW FILTERS (VERY IMPORTANT FOR YOU)
    list_filter = (
        "town",
        "permit_status",
        "structure_type",
    )

    readonly_fields = [f.name for f in Structure._meta.fields]

    change_list_template = "admin/structure_changelist.html"

    # -------------------------
    # 🎯 PERMIT STATUS BADGE
    # -------------------------
    def permit_badge(self, obj):

        colors = {
            "PERMITTED": "#2ecc71",
            "NOT_PERMITTED": "#e74c3c",
            "PENDING": "#f39c12",
        }

        return format_html(
            '<span style="padding:5px 10px;border-radius:8px;color:white;background:{};font-weight:bold;">{}</span>',
            colors.get(obj.permit_status, "#95a5a6"),
            obj.permit_status or "UNKNOWN"
        )

    permit_badge.short_description = "Permit"

    # -------------------------
    # 🧠 LIGHT FRAUD INDICATOR (LESS NOISY)
    # -------------------------
    def fraud_badge(self, obj):

        issues = 0

        if Structure.objects.filter(owner_phone=obj.owner_phone).count() > 1:
            issues += 1

        if Structure.objects.filter(ghana_card=obj.ghana_card).count() > 1:
            issues += 1

        if Structure.objects.filter(
            owner_name=obj.owner_name,
            owner_phone=obj.owner_phone
        ).count() > 1:
            issues += 1

        if issues == 0:
            return format_html(
                '<span style="background:#2ecc71;color:white;padding:4px 8px;border-radius:6px;">CLEAN</span>'
            )

        return format_html(
            '<span style="background:#e67e22;color:white;padding:4px 8px;border-radius:6px;">RISK ({})</span>',
            issues
        )

    fraud_badge.short_description = "Risk"

    # -------------------------
    # 🔒 LOCK ADMIN EDITING
    # -------------------------
    def has_change_permission(self, request, obj=None):
        return False

    # -------------------------
    # 📊 DASHBOARD STATS
    # -------------------------
    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}

        extra_context["stats"] = {
            "total": Structure.objects.count(),
            "permitted": Structure.objects.filter(permit_status="PERMITTED").count(),
            "pending": Structure.objects.filter(permit_status="PENDING").count(),
            "not_permitted": Structure.objects.filter(permit_status="NOT_PERMITTED").count(),
        }

        return super().changelist_view(request, extra_context=extra_context)


# =========================================================
# 💰 PAYMENT ADMIN (SYNC STRUCTURE AUTOMATICALLY)
# =========================================================
@admin.register(PaymentHistory)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "structure",
        "collector",
        "amount",
        "status_badge",
        "created_at",
    )

    list_filter = ("status",)
    search_fields = ("structure__ts_id", "collector__username")

    actions = ["approve_payment", "reject_payment"]

    def status_badge(self, obj):

        colors = {
            "APPROVED": "#2ecc71",
            "REJECTED": "#e74c3c",
            "PENDING": "#f39c12",
        }

        return format_html(
            '<span style="padding:5px 10px;border-radius:8px;color:white;background:{};">{}</span>',
            colors.get(obj.status, "#95a5a6"),
            obj.status
        )

    status_badge.short_description = "Status"

    # -------------------------
    # ✅ APPROVE PAYMENT → PERMIT STRUCTURE
    # -------------------------
    @admin.action(description="Approve Payment → Permit Structure")
    def approve_payment(self, request, queryset):

        for obj in queryset:
            obj.status = "APPROVED"
            obj.save()

            obj.structure.permit_status = "PERMITTED"
            obj.structure.save()

    # -------------------------
    # ❌ REJECT PAYMENT → BLOCK STRUCTURE
    # -------------------------
    @admin.action(description="Reject Payment → Block Structure")
    def reject_payment(self, request, queryset):

        for obj in queryset:
            obj.status = "REJECTED"
            obj.save()

            obj.structure.permit_status = "NOT_PERMITTED"
            obj.structure.save()


# =========================================================
# ✏️ EDIT REQUEST ADMIN
# =========================================================
@admin.register(EditRequest)
class EditRequestAdmin(admin.ModelAdmin):

    list_display = (
        "structure",
        "field_name",
        "collector",
        "status",
        "created_at"
    )

    list_filter = ("status",)

    actions = ["approve_edit", "reject_edit"]

    @admin.action(description="Approve Edit")
    def approve_edit(self, request, queryset):

        for obj in queryset:
            structure = obj.structure
            setattr(structure, obj.field_name, obj.new_value)
            structure.save()

            obj.status = "APPROVED"
            obj.save()

    @admin.action(description="Reject Edit")
    def reject_edit(self, request, queryset):
        queryset.update(status="REJECTED")