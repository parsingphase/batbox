// noinspection JSUnusedGlobalSymbols
/**
 * @typedef AudioFile
 * @type {Object}
 * @property {string} identifier
 * @property {Array<number>} latlon
 */

export default class MapHandler {
    // noinspection JSUnusedGlobalSymbols
    /**
     * Create a new instance
     *
     * @param {string} targetElementId ID of a DOM element to hold the map
     * @param {string} mapboxToken Mapbox token, see README.md for source
     * @returns {MapHandler}
     */
    constructor(targetElementId, mapboxToken) {
        this.targetElementId = targetElementId;
        this.mapboxToken = mapboxToken;
        this.tileSet = 'mapbox.satellite';
        this.audioMarkers = {};
        this.markersLayer = new L.FeatureGroup();
        return this;
    }

    /**
     * Draw a map in-page at the configured DOM id
     *
     * @param {Array<Array>} bounds
     * @returns {MapHandler}
     */
    drawMapWithBounds(bounds) {
        this.map = L.map(this.targetElementId).fitBounds(bounds);
        this.map.addLayer(this.markersLayer);
        L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © ' +
                '<a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            id: this.tileSet,
            accessToken: this.mapboxToken
        }).addTo(this.map);

        return this;
    }

    /**
     * Add the list of audiofiles as map markers
     *
     * @param {Array.<AudioFile>} audioFiles
     * @returns {MapHandler}
     */
    addAudioMarkers(audioFiles) {
        let marker;
        for (let i = 0; i < audioFiles.length; i++) {
            let trace = audioFiles[i];
            let id = trace.identifier;
            if (trace.latlon) {
                marker = L.marker(trace.latlon);
                marker.bindPopup('<a href="#recording-' + trace.identifier + '">' + trace.identifier + '</a>');
                this.audioMarkers[id] = marker;
                this.markersLayer.addLayer(marker);
            }
        }

        return this;
    }


    /**
     * Replace map markers with those specified
     *
     * @param {Array.<AudioFile>} audioFiles
     * @returns {MapHandler}
     */
    replaceAudioMarkers(audioFiles) {
        this.audioMarkers = {};
        this.map.removeLayer(this.markersLayer);
        this.markersLayer = new L.FeatureGroup();
        this.map.addLayer(this.markersLayer);

        return this.addAudioMarkers(audioFiles);
    }

    /**
     * Pan to the marker with the given ident, if it exists
     *
     * @param {string} ident
     * @param {number|null} zoomLevel
     * @returns {MapHandler}
     */
    panMapToAudioFile(ident, zoomLevel = null) {
        if (this.audioMarkers.hasOwnProperty(ident)) {
            // noinspection JSIncompatibleTypesComparison
            if (zoomLevel === null) {
                this.map.panTo(this.audioMarkers[ident].getLatLng());
            } else {
                this.map.flyTo(this.audioMarkers[ident].getLatLng(), zoomLevel);
            }
            this.audioMarkers[ident].openPopup();
            // document.getElementById('map-pane').scrollIntoView();
        }

        return this;
    }
}
