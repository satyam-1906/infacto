import os
from django.contrib import admin
from .models import TeamRegistration

@admin.action(description='Approve selected teams and generate credentials')
def approve_teams(modeladmin, request, queryset):
    for team in queryset.filter(is_approved=False):
        team.is_approved = True
        team.save()
    modeladmin.message_user(request, "Successfully approved selected teams. Excel roster dynamically synchronized.")


@admin.register(TeamRegistration)
class TeamRegistrationAdmin(admin.ModelAdmin):
    # E. Admin Dashboard Display Configuration
    list_display = ('team_name', 'primary_name', 'institution', 'experience', 'add_merch', 'primary_tshirt_size', 'teammate_tshirt_size', 'debate_topic', 'stance', 'debate_date', 'debate_time', 'classroom', 'is_approved')
    list_editable = ('add_merch', 'primary_tshirt_size', 'teammate_tshirt_size', 'debate_topic', 'stance', 'debate_date', 'debate_time', 'classroom', 'is_approved')
    actions = [approve_teams]
    search_fields = ('team_name', 'generated_username')
