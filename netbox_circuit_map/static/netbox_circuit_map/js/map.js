let default_marker_icon = {
  iconSize: [22, 33],
  shadowEnable: true,
  shadowOpacity: 0.25,
  shadowAngle: 27,
  shadowLength: 0.64,
  shadowBlur: 1.5
}
// TODO Maybe make different colours depending on site group?
// Also, maybe an idea to make this configurable instead of hardcoded?
// Maybe on a custom field on the site and/or circuit or circuit type or provider
// For now just leaving the original data commented as as a syntax hint
let marker_icon_configs = {
/*
  'access-switch': Object.assign({color: "#2da652"}, default_marker_icon),
  'core-switch': Object.assign({color: "#d30b0b"}, default_marker_icon),
  'distribution-switch': Object.assign({color: "#277fca"}, default_marker_icon),
  olt: Object.assign({color: "#c5ba26"}, default_marker_icon),
  router: Object.assign({color: "#26A69A"}, default_marker_icon),
  wifi: Object.assign({color: "#8111ea"}, default_marker_icon)
*/
}

const map_data = JSON.parse(document.getElementById('map-data').textContent)

let geomap = L.map(map_data.map_id,
  {
    crs: L.CRS[map_data.crs],
    layers: [L.tileLayer(map_data.tiles.url_template, map_data.tiles.options)],
    fullscreenControl: true,
    fullscreenControlOptions: {position: 'topright'}
  }
)
geomap.attributionControl.setPrefix(`<a href="https://leafletjs.com" title="A JavaScript library for interactive maps">Leaflet</a>`)
geomap.attributionControl.addAttribution(map_data.attribution)

let sidebar = L.control.sidebar('map-sidebar', {
  closeButton: true,
  position: 'left'
})
geomap.addControl(sidebar);

let bounds = new L.LatLngBounds()

// Preparing to place markers with the same coordinates in clusters
let markers = {}
Object.values(map_data.sites).forEach(function(entry) {
  let key = entry.position.toString()
  if (key in markers) {
    markers[key].push(entry)
  } else {
    markers[key] = [entry]
  }
})

let lines_by_site = {}

for (let key in markers) {
  const marker_parent_layer = markers[key].length > 1 ? L.markerClusterGroup() : geomap;
  for (let marker_data of markers[key]) {
    let iconOptions = {}
    if (marker_data.icon && marker_data.icon in marker_icon_configs) {
      iconOptions = marker_icon_configs[marker_data.icon]
    } else {
      iconOptions = default_marker_icon
    }
    let markerObj = L.marker(marker_data.position, {icon: L.divIcon.svgIcon(iconOptions), site: marker_data.site})
      .bindTooltip(`${marker_data.site.name}<br><span class="text-muted">${marker_data.site.tenant}</span>`)
    markerObj.on('click', function (event) {
      let site = event.target.options.site
      if (sidebar.isVisible() && (sidebar.displayed_site === site.id)) {
        sidebar.hide()
      } else {
        if (sidebar.displayed_site) {
          for (let line of lines_by_site[sidebar.displayed_site]) {
            line.setStyle(normalLineStyle)
          }
        }
        sidebar.displayed_site = site.id
        for (let line of lines_by_site[sidebar.displayed_site]) {
          line.setStyle(focusLineStyle)
        }
        document.querySelector('.sidebar-site-name').innerHTML = `<a href="${site.url}" target="_blank">${site.name}</a>`
        document.querySelector('.sidebar-site-tenant').innerText = site.tenant
        document.querySelector('.sidebar-site-address').innerText = site.address
        sidebar.show()
      }
    })
    bounds.extend(marker_data.position)
    marker_parent_layer.addLayer(markerObj)
  }
  if (markers[key].length > 1) {
    geomap.addLayer(marker_parent_layer)
  }
}

const normalLineStyle = {weight: 3, color: '#3388ff'}
const boldLineStyle = {weight: 5, color:'#0c10ff'};
const focusLineStyle = {weight: 3, color:'#ff8833'};
const boldFocusLineStyle = {weight: 5, color:'#ff100c'};

Object.keys(map_data.sites).forEach(function(id) {
  lines_by_site[id] = []
})

for (let circuit of map_data.circuits) {
  let site_a = circuit.site_a
  let site_z = circuit.site_z
  let pos_a = map_data.sites[site_a].position
  let pos_z = map_data.sites[site_z].position
  let line = L.polyline([pos_a, pos_z], normalLineStyle).addTo(geomap)
  line.on('mouseover', () => {
    const a = site_a;
    const z = site_z;
    if (sidebar.displayed_site == a || sidebar.displayed_site == z) {
      line.setStyle(boldFocusLineStyle);
    } else {
      line.setStyle(boldLineStyle);
    }
    line.bringToFront();
  })
  line.on('mouseout', () => {
    const a = site_a;
    const z = site_z;
    if (sidebar.displayed_site == a || sidebar.displayed_site == z) {
      line.setStyle(focusLineStyle);
    } else {
      line.setStyle(normalLineStyle);
    }
  })
  line.on('click', () => {
    document.location = `/circuits/circuits/${circuit.id}`
  })
  line.bindTooltip(`${circuit.cid}<br><span class="text-muted">${circuit.provider}</span>`, {sticky:true})
  lines_by_site[site_a].push(line)
  lines_by_site[site_z].push(line)
}

if (bounds.isValid()) {
  geomap.fitBounds(bounds)
} else {
  geomap.fitWorld()
}

sidebar.on('hide', function () {
  for (let line of lines_by_site[sidebar.displayed_site]) {
    line.setStyle(normalLineStyle)
  }
  sidebar.displayed_site = undefined
});
