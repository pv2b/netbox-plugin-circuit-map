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
map_data.markers.forEach(function(entry) {
  let key = entry.position.toString()
  if (key in markers) {
    markers[key].push(entry)
  } else {
    markers[key] = [entry]
  }
})

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
        sidebar.displayed_site = undefined
        sidebar.hide()
      } else {
        sidebar.displayed_site = site.id
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
const boldLineStyle ={weight: 5, color:'#0c10ff'};

for (let circuit of map_data.circuits) {
  let line = L.polyline(circuit.coords, normalLineStyle).addTo(geomap)
  line.on('mouseover', function () {this.setStyle(boldLineStyle); this.bringToFront()})
  line.on('mouseout', function () {this.setStyle(normalLineStyle)})
  line.bindTooltip(`${circuit.id}<br><span class="text-muted">${circuit.provider}</span>`, {sticky:true})
}

if (bounds.isValid()) {
  geomap.fitBounds(bounds)
} else {
  geomap.fitWorld()
}
