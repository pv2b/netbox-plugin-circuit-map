from django import forms

from dcim.models import Site
from circuits.models import Provider
from utilities.forms import BootstrapMixin
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField


#class CircuitMapFilterForm(BootstrapMixin, forms.Form):
class CircuitMapFilterForm(forms.Form):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Site",
        help_text="Site for circuit selection"
    )
    hide_circuits = forms.BooleanField(
        required=False,
        label="Hide circuits between sites"
    )

class ConnectedCircuitsForm(forms.Form):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label="Site",
        help_text="Provider for circuit selection"
    )