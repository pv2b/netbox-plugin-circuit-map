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
        print(repr(request.GET))
        if form.is_valid():
            if sitename := form.cleaned_data['site']:
                site = Site.objects.get(name=sitename)
                sites = get_connected_sites(site)
            else:
                sites = Site.objects.all()

            geolocated_sites = {s: coords for s in sites if (coords := get_site_location(s))}
            non_geolocated_sites = set(sites) - set(geolocated_sites.keys())

            if form.cleaned_data['hide_circuits']:
                circuits = []
            elif sitename:
                circuits = get_connected_circuits(site)
            else:
                circuits = Circuit.objects.all()

            map_data = configure_leaflet_map("geomap", geolocated_sites, circuits)
            return render(request, self.template_name, context=dict(
                filter_form=form, map_data=map_data, non_geolocated_sites=non_geolocated_sites
            ))

        return render(
            request, self.template_name,
            context=dict(filter_form=self.form(initial=request.GET))
        )