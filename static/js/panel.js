// Harita oluşturuluyor
var map = L.map('map').setView([51.505, -0.09], 13);

// OpenStreetMap katmanı ekleniyor
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Çizilen öğeleri tutacak grup oluşturuluyor
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Çizim kontrolü (sadece polygon çizimi aktif)
var drawControl = new L.Control.Draw({
  edit: { featureGroup: drawnItems },
  draw: { 
    polygon: true, 
    marker: false, 
    polyline: false, 
    rectangle: false, 
    circle: false, 
    circlemarker: false 
  }
});
map.addControl(drawControl);

// Yeni çizim yapıldığında önceki çizimleri temizleyip, yeni katmanı ekle
map.on('draw:created', function(e) {
  var layer = e.layer;
  drawnItems.clearLayers(); // Tek alan için önceki çizimleri temizle
  
  // Seçilen renk değerini al (varsayılan "#3388ff" olacak)
  var selectedColor = document.getElementById('color').value || "#3388ff";
  
  // Polygon stilini seçilen renge ayarla
  layer.setStyle({ color: selectedColor });
  drawnItems.addLayer(layer);
});

// "Alanı Kaydet" butonuna tıklanınca veriler toplanıyor
document.getElementById('save_area').onclick = function() {
  var areaName = document.getElementById('area_name').value;
  var waterPollution = document.getElementById('water_pollution').value;
  var radioactivity = document.getElementById('radioactivity').value;
  var soilQuality = document.getElementById('soil_quality').value;
  var livingQuality = document.getElementById('living_quality').value;
  var ph = document.getElementById('ph').value;
  var color = document.getElementById('color').value; // Renk seçici değeri

  if (!areaName) {
    alert('Alan ismi girmelisiniz!');
    return;
  }

  if (drawnItems.getLayers().length === 0) {
    alert('Lütfen haritada bir alan çizin!');
    return;
  }

  // Çizilen polygonun koordinatlarını al (lat, lng şeklinde)
  var coordinates = drawnItems.getLayers()[0].getLatLngs()[0].map(function(latlng) {
    return [latlng.lat, latlng.lng];
  });

  if (coordinates.length === 0) {
    alert('Koordinatlar alınamadı, lütfen alanı doğru çizdiğinizden emin olun.');
    return;
  }

  // Verileri sunucuya gönderme işlemi
  fetch('/save_area', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      coordinates: coordinates,
      area_name: areaName,
      water_pollution: waterPollution,
      radioactivity: radioactivity,
      soil_quality: soilQuality,
      living_quality: livingQuality,
      ph: ph,
      color: color
    })
  })
  .then(response => response.json())
  .then(data => {
    alert(data.message);
    // Formu ve çizimleri sıfırla
    drawnItems.clearLayers();
    document.getElementById('area_name').value = '';
    document.getElementById('water_pollution').value = '';
    document.getElementById('radioactivity').value = '';
    document.getElementById('soil_quality').value = '';
    document.getElementById('living_quality').value = '';
    document.getElementById('ph').value = '';
    document.getElementById('color').value = '#3388ff'; // Varsayılan renk
  })
  .catch(error => console.error('Hata:', error));
};
