import os
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import TeamRegistration


# ─── Custom Admin Actions ──────────────────────────────────────────────────────

@admin.action(description='✅ Approve selected teams and generate credentials')
def approve_teams(modeladmin, request, queryset):
    approved = 0
    for team in queryset.filter(is_approved=False):
        team.is_approved = True
        team.save()
        approved += 1
    if approved:
        modeladmin.message_user(
            request,
            f"✅ Successfully approved {approved} team(s). Credentials generated and Excel roster updated."
        )
    else:
        modeladmin.message_user(request, "ℹ️ All selected teams were already approved.", level='warning')


@admin.action(description='❌ Revoke approval for selected teams')
def revoke_teams(modeladmin, request, queryset):
    count = queryset.filter(is_approved=True).update(is_approved=False)
    modeladmin.message_user(request, f"❌ Revoked approval for {count} team(s).", level='warning')


@admin.action(description='🗑️ Permanently delete selected registrations (and linked user accounts)')
def delete_registrations(modeladmin, request, queryset):
    from django.contrib.auth.models import User
    deleted_count = 0
    for team in queryset:
        # Also remove the linked Django User so credentials are fully wiped
        if team.generated_username:
            User.objects.filter(username=team.generated_username).delete()
        team.delete()
        deleted_count += 1
    modeladmin.message_user(
        request,
        f"🗑️ Permanently deleted {deleted_count} registration(s) and their linked user account(s).",
        level='warning'
    )


# ─── TeamRegistration Admin ────────────────────────────────────────────────────

@admin.register(TeamRegistration)
class TeamRegistrationAdmin(admin.ModelAdmin):

    # ── List View ──────────────────────────────────────────────────────────────
    list_display = (
        'team_name',
        'primary_name',
        'institution',
        'referral_code',
        'payment_thumbnail',
        'add_merch',
        'primary_tshirt_size',
        'teammate_tshirt_size',
        'debate_topic',
        'stance',
        'debate_date',
        'debate_time',
        'classroom',
        'approval_badge',
    )

    list_editable = (
        'add_merch',
        'primary_tshirt_size',
        'teammate_tshirt_size',
        'debate_topic',
        'stance',
        'debate_date',
        'debate_time',
        'classroom',
    )

    list_filter = ('is_approved', 'add_merch', 'stance', 'institution')
    search_fields = ('team_name', 'primary_name', 'primary_email', 'generated_username', 'institution', 'referral_code')
    list_per_page = 25
    ordering = ('-id',)
    actions = [approve_teams, revoke_teams, delete_registrations]
    date_hierarchy = None

    # ── Read-only fields ───────────────────────────────────────────────────────
    readonly_fields = (
        'generated_username',
        'payment_screenshot_preview',
        'primary_email',
        'primary_mobile',
        'teammate_email',
        'teammate_mobile',
    )

    # ── Fieldsets (Detail View) ────────────────────────────────────────────────
    fieldsets = (
        ('👥 Team Details', {
            'fields': (
                ('team_name', 'institution'),
                ('primary_name', 'primary_email', 'primary_mobile'),
                ('teammate_name', 'teammate_email', 'teammate_mobile'),
                'experience',
                'referral_code',
            )
        }),
        ('💳 Payment', {
            'fields': (
                'payment_screenshot',
                'payment_screenshot_preview',
            )
        }),
        ('👕 Merchandise', {
            'fields': (
                'add_merch',
                ('primary_tshirt_size', 'teammate_tshirt_size'),
            ),
            'classes': ('collapse',),
        }),
        ('🗣️ Debate Assignment', {
            'description': 'Fill in the debate details for this team. These values are shown on the team\'s participant dashboard after login.',
            'fields': (
                'debate_topic',
                ('stance', 'classroom'),
                ('debate_date', 'debate_time'),
            )
        }),
        ('🔐 Admin & Credentials', {
            'fields': (
                'is_approved',
                'generated_username',
            ),
            'classes': ('collapse',),
        }),
    )

    # ─── Payment Screenshot Display ────────────────────────────────────────────
    #
    # payment_screenshot is a URLField containing a full Cloudinary HTTPS URL,
    # e.g. https://res.cloudinary.com/<cloud>/image/upload/v.../filename.jpg
    #
    # We render it directly as an <img> tag — no .url call, no file system needed.
    # ──────────────────────────────────────────────────────────────────────────

    @admin.display(description='📷 Screenshot')
    def payment_thumbnail(self, obj):
        """Small thumbnail shown in the list view."""
        url = (obj.payment_screenshot or '').strip()

        if url.startswith('https://') or url.startswith('http://'):
            return mark_safe(
                f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
                f'<img src="{url}" '
                f'     width="64" height="48" '
                f'     style="object-fit:cover;border-radius:6px;'
                f'            border:1px solid #555;display:block;" '
                f'     alt="Payment screenshot" />'
                f'</a>'
            )

        if url:
            # Old record with a local file path — can't be displayed
            return mark_safe(
                f'<span style="color:#f87171;font-size:11px;" '
                f'      title="Local path: {url}">⚠️ Pre-Cloudinary</span>'
            )

        return mark_safe('<span style="color:#6b7280;font-size:11px;">—</span>')

    @admin.display(description='📷 Payment Screenshot Preview')
    def payment_screenshot_preview(self, obj):
        """Large preview shown in the detail (edit) view."""
        url = (obj.payment_screenshot or '').strip()

        if url.startswith('https://') or url.startswith('http://'):
            return mark_safe(
                f'<div style="margin-top:8px;">'
                f'  <a href="{url}" target="_blank" rel="noopener noreferrer">'
                f'    <img src="{url}" '
                f'         style="max-height:320px;max-width:100%;'
                f'                border-radius:10px;border:1px solid #555;'
                f'                display:block;margin-bottom:8px;" '
                f'         alt="Payment screenshot" />'
                f'  </a>'
                f'  <a href="{url}" target="_blank" rel="noopener noreferrer" '
                f'     style="font-size:11px;color:#60a5fa;word-break:break-all;">'
                f'    {url}'
                f'  </a>'
                f'</div>'
            )

        if url:
            return mark_safe(
                f'<p style="color:#f87171;margin:0;">'
                f'  ⚠️ This record was created before Cloudinary integration.<br>'
                f'  Local path stored: <code style="color:#94a3b8;">{url}</code>'
                f'</p>'
            )

        return mark_safe('<em style="color:#6b7280;">No screenshot uploaded.</em>')

    # ── Status & Stance Badges ────────────────────────────────────────────────

    @admin.display(description='Status', boolean=False)
    def approval_badge(self, obj):
        if obj.is_approved:
            return mark_safe(
                '<span style="background:#16a34a;color:#fff;padding:3px 10px;'
                'border-radius:12px;font-size:12px;font-weight:bold;">✅ Approved</span>'
            )
        return mark_safe(
            '<span style="background:#b91c1c;color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:12px;font-weight:bold;">⏳ Pending</span>'
        )

    @admin.display(description='Stance')
    def stance_badge(self, obj):
        s = (obj.stance or '').lower()
        if 'for' in s or 'prop' in s or 'affirmative' in s:
            color = '#15803d'
        elif 'against' in s or 'oppo' in s or 'negative' in s:
            color = '#b91c1c'
        else:
            color = '#6b7280'
        return mark_safe(
            f'<span style="background:{color};color:#fff;padding:2px 8px;'
            f'border-radius:8px;font-size:11px;">{obj.stance or "—"}</span>'
        )

    # ── Stance dropdown for both list and detail views ─────────────────────────
    STANCE_CHOICES = [
        ('Pending', 'Pending'),
        ('For (Proposition)', 'For (Proposition)'),
        ('Against (Opposition)', 'Against (Opposition)'),
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        from django import forms
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'stance' and field is not None:
            field.widget = forms.Select(
                choices=[('', '— Select Stance —')] + self.STANCE_CHOICES,
                attrs={'style': 'min-width:160px;'}
            )
        return field
