"""
sentry.web.forms.teams
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django import forms

from sentry.models import Team, TeamMember, PendingTeamMember
from sentry.web.forms.fields import UserField
from django.utils.translation import ugettext_lazy as _, ungettext


class RemoveTeamForm(forms.Form):
    pass


class NewTeamForm(forms.ModelForm):
    name = forms.CharField(label=_('Team Name'), max_length=200, widget=forms.TextInput(attrs={'placeholder': _('My Team Name')}))

    class Meta:
        fields = ('name',)
        model = Team


class NewTeamAdminForm(NewTeamForm):
    owner = UserField(required=False)

    class Meta:
        fields = ('name', 'owner')
        model = Team


class EditTeamForm(forms.ModelForm):
    class Meta:
        fields = ('name',)
        model = Team


class EditTeamAdminForm(EditTeamForm):
    owner = UserField(required=False)

    class Meta:
        fields = ('name', 'owner',)
        model = Team


class SelectTeamForm(forms.Form):
    team = forms.TypedChoiceField(choices=(), coerce=int)

    def __init__(self, team_list, data, *args, **kwargs):
        super(SelectTeamForm, self).__init__(data=data, *args, **kwargs)
        self.team_list = dict((str(t.pk), t) for t in team_list.itervalues())
        choices = []
        for team in self.team_list.itervalues():
            # TODO: optimize queries
            member_count = team.member_set.count()
            project_count = team.project_set.count()

            if member_count > 1 and project_count:
                label = _('%(team)s (%(members)s, %(projects)s)')
            elif project_count:
                label = _('%(team)s (%(projects)s)')
            else:
                label = _('%(team)s (%(members)s)')

            choices.append(
                (team.id, label % dict(
                    team=team.name,
                    members=ungettext('%d member', '%d members', member_count) % (member_count,),
                    projects=ungettext('%d project', '%d projects', project_count) % (project_count,),
                ))
            )

        choices.insert(0, (-1, '-' * 8))
        self.fields['team'].choices = choices
        self.fields['team'].widget.choices = self.fields['team'].choices

    def clean_team(self):
        value = self.cleaned_data.get('team')
        if not value or value == -1:
            return value
        return self.team_list.get(value)


class BaseTeamMemberForm(forms.ModelForm):
    class Meta:
        fields = ('type',)
        model = TeamMember

    def __init__(self, team, *args, **kwargs):
        self.team = team
        super(BaseTeamMemberForm, self).__init__(*args, **kwargs)


EditTeamMemberForm = BaseTeamMemberForm


class InviteTeamMemberForm(BaseTeamMemberForm):
    class Meta:
        fields = ('type', 'email')
        model = PendingTeamMember

    def clean_email(self):
        value = self.cleaned_data['email']
        if not value:
            return None

        if self.team.member_set.filter(user__email__iexact=value).exists():
            raise forms.ValidationError(_('There is already a member with this email address'))

        if self.team.pending_member_set.filter(email__iexact=value).exists():
            raise forms.ValidationError(_('There is already a pending invite for this user'))

        return value


class NewTeamMemberForm(BaseTeamMemberForm):
    user = UserField()

    class Meta:
        fields = ('type', 'user')
        model = TeamMember

    def clean_user(self):
        value = self.cleaned_data['user']
        if not value:
            return None

        if self.team.member_set.filter(user=value).exists():
            raise forms.ValidationError(_('User is already a member of this team'))

        return value


class AcceptInviteForm(forms.Form):
    pass
