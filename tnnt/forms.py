from django import forms
import unicodedata

# Helper function for common checks on unvalidated user input strings
def text_field_clean(input_str, input_type):
    # refuse slashes, since this will mess up routing to /clan/<clanname>
    # endpoints
    # (post 2021 TODO: we could probably improve this by making the clan name
    # a GET parameter rather than part of the URL)
    if '/' in input_str:
        raise forms.ValidationError('%s cannot contain slashes' % input_type)

    # allow diacritics, but only one combining character per regular character
    # (otherwise ZALGO style clan names can be created which mess up other
    # parts of the page)
    prevcombine = False
    for char in input_str:
        nowcombine = unicodedata.combining(char)
        if nowcombine and prevcombine:
            raise forms.ValidationError(
                '%s cannot have more than two consecutive combining characters' % input_type)
        prevcombine = nowcombine

    # don't allow non-printable characters
    if not input_str.isprintable():
        raise forms.ValidationError(
            '%s cannot contain non-printable characters' % input_type)

    # TODO: remove this requirement once we can get the MySQL database
    # converted to utf8mb4 instead of utf8mb3, so that 4-byte characters will
    # work.  If a certain subset of 4-byte characters should still be blocked
    # it can be replaced with a more narrowly scoped test.
    for char in input_str:
        if len(char.encode('utf-8')) >= 4:
            raise forms.ValidationError(
                ('%s cannot contain 4-byte UTF-8 characters (such as emoji)'
                 % input_type))

    return input_str

class CreateClanForm(forms.Form):
    clan_name = forms.CharField(max_length = 127, label='Create a clan:')

    # Custom validator for the clan_name field. Enforces some constraints we
    # don't want to allow in clan names.
    def clean_clan_name(self):
        data = self.cleaned_data['clan_name']
        return text_field_clean(data, "Clan names")

class InviteMemberForm(forms.Form):
    invitee = forms.CharField(max_length = 32, label='Invite:')

    def clean_invitee(self):
        data = self.cleaned_data['invitee']
        return text_field_clean(data, "Invitees")
