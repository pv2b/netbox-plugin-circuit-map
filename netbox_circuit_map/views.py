import re

from dcim.models import Site
from circuits.models import Circuit
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q

from . import forms
from .geographical_map import configure_leaflet_map
from .helpers import get_site_location, get_connected_sites, get_connected_circuits
from .settings import plugin_settings


INTEGER_REGEXP = re.compile(r'\d+')


class MapView(PermissionRequiredMixin, View):
    permission_required = ('dcim.view_site', 'circuits.view_circuit', 'tenancy.view_tenant')
    template_name = 'netbox_circuit_map/main.html'
    form = forms.CircuitMapFilterForm

    def get(self, request):
        """Circuit map view"""
        form = self.form(request.GET)
        if form.is_valid():
            if sitename := form.cleaned_data['site']:
                site = Site.objects.get(name=sitename)
                sites = get_connected_sites(site)
            else:
                sites = Site.objects.all()

            geolocated_sites = {s: coords for s in sites if (coords := get_site_location(s))}
            non_geolocated_sites = set(sites) - set(geolocated_sites.keys())

            if form.cleaned_data['show_circuits']:
                if sitename:
                    circuits = get_connected_circuits(site)
                else:
                    circuits = Circuit.objects.all()
            else:
                circuits = []

            map_data = configure_leaflet_map("geomap", geolocated_sites, circuits)
            return render(request, self.template_name, context=dict(
                filter_form=form, map_data=map_data, non_geolocated_sites=non_geolocated_sites
            ))

        return render(
            request, self.template_name,
            context=dict(filter_form=self.form(initial=request.GET))
        )


class ConnectedCircuitAjaxView(PermissionRequiredMixin, View):
    permission_required = ('circuits.view_circuit', 'circuits.view_circuittermination')
    form = forms.ConnectedCircuitsForm

    def get(self, request, **kwargs):
        """List of circuits connected to the specified site"""
        try:
            site = Site.objects.get(pk=kwargs.get('pk'))
        except Device.DoesNotExist:
            return JsonResponse({'status': False, 'error': 'Device not found'}, status=404)
        form = self.form(request.GET)
        if form.is_valid():
            data = form.cleaned_data
            connected_circuits_qs = get_connected_circuits(site).order_by()
            connected_circuits = [dict(id=s.id, name=s.name, url=s.get_absolute_url(), address=s.physical_address, tenant=s.tenant.name)
                                 for s in connected_sites_qs]
            # Sorting list of circuits by the circuit provider and ID
            connected_circuit.sort(key=lambda c: (c.provider.name, c.id))
            return JsonResponse(dict(status=True, connected_circuits=connected_circuits,
                                     provider=circuit.provider.name))
        else:
            return JsonResponse({'status': False, 'error': 'Form fields filled out incorrectly',
                                 'form_errors': form.errors}, status=404)
