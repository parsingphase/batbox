// noinspection JSUnusedGlobalSymbols
/* jshint -W069 */ // Url handler uses ['string'] notation
/**
 * @typedef AudioFile
 * @type {Object}
 * @property {string} identifier
 * @property {Array<number>} latlon
 */

import {mammalDiversitySpeciesLink} from './linkTools.js';

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
        this.targetElement = $('#' + targetElementId);
        this.mapboxToken = mapboxToken;
        // this.tileSet = 'mapbox.streets';
        this.tileSet = 'mapbox.satellite';
        this.audioMarkers = {};
        this.markersLayer = new L.FeatureGroup();
        this.urlRouter = null;
        this.userIsAuthenticated = false;
        return this;
    }

    setUrlRouter(router) {
        this.urlRouter = router;
        return this;
    }

    setUserAuthenticated(flag) {
        this.userIsAuthenticated = flag;
    }

    /**
     * Draw a map in-page at the configured DOM id
     *
     * @param {Array<Array>} bounds
     * @returns {MapHandler}
     */
    drawMapWithBounds(bounds) {
        this.map = L.map(this.targetElementId).fitBounds(bounds);
        return this.initMap();
    }

    /**
     * Draw a map in-page at the configured DOM id
     *
     * @param {Array} centre
     * @param {int} zoom
     * @returns {MapHandler}
     */
    drawMapWithView(centre, zoom) {
        document.getElementById(this.targetElementId).textContent = '';
        this.map = L.map(this.targetElementId);
        this.initMap();
        this.map.setView(centre, zoom);
        return this;
    }

    /**
     * Draw a map in-page at the configured DOM id
     *
     * @returns {MapHandler}
     */
    drawMapWithWorld() {
        this.map = L.map(this.targetElementId).fitWorld();
        return this.initMap();
    }

    initMap() {
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

    enableAudioControlsInMap() {
        const that = this;
        let $audioTriggers = this.targetElement.find('.audioTrigger');
        $audioTriggers.off('click');

        $audioTriggers.click(function () {
            let sourceElement = $(this);
            const src = sourceElement.data('audioSrc');
            const loSrc = sourceElement.data('audioSrcLo');
            let playSrc;

            if (loSrc && that.defaultLowResAudio) {
                playSrc = loSrc;
            } else {
                playSrc = src;
            }

            if (that.playingFile !== playSrc) {
                if (that.player) {
                    that.player.pause();
                }
                that.player = null;
                that.targetElement.find('.audioTrigger').html('<i class="fas fa-play"></i>');
            }

            that.playingFile = playSrc;

            if (!that.player) {
                that.player = new Audio(playSrc);
            }

            that.player.addEventListener('playing', () => {
                // The duration variable now holds the duration (in seconds) of the audio clip
                sourceElement.html('<i class="fas fa-pause"></i>');
            });

            that.player.addEventListener('ended', () => {
                // The duration variable now holds the duration (in seconds) of the audio clip
                sourceElement.html('<i class="fas fa-play"></i>');
                that.player = null;
            });

            that.player.addEventListener('error', () => {
                // The duration variable now holds the duration (in seconds) of the audio clip
                sourceElement.html('<abbr title="Failed"><i class="fas fa-exclamation-circle"></i></abbr>');
                let code = that.player.error.code;
                if (console) {
                    console.log('Error: ' + code + ' playing ' + playSrc);
                    if (!that.defaultLowResAudio) {
                        console.log('Device may not be able to play high sample rate files');
                    }
                }
                if ((code === 4) && !that.defaultLowResAudio && loSrc) {
                    if (console) {
                        console.log('Trying to play low rate file instead');
                    }
                    // if we failed to play full res, see if we've got a low-res file to try
                    playSrc = loSrc;
                    that.defaultLowResAudio = true;
                    that.playingFile = loSrc;
                    that.player.src = loSrc;
                    that.player.load();
                    that.player.play();
                } else {
                    that.player = null;
                }

            });
            if (that.player.paused) {
                sourceElement.html('<i class="fas fa-spinner fa-pulse"></i>');
                that.player.play();
            } else {
                sourceElement.html('<i class="fas fa-play"></i>');
                that.player.pause();
            }
        });
    }

    /**
     * Add the list of audiofiles as map markers
     *
     * @param {Array.<AudioFile>} audioFiles
     * @returns {MapHandler}
     */
    addAudioMarkers(audioFiles) {
        let icon = {};
        const that = this;
        this.markersLayer.on('popupopen', function (e) {
            that.enableAudioControlsInMap();
        });

        let marker;
        for (let i = 0; i < audioFiles.length; i++) {
            let trace = audioFiles[i];
            let id = trace.identifier;
            if (trace.latlon) {
                let colorKey = trace.genus + trace.species;
                if (!colorKey) {
                    colorKey = 'NULNUL';
                }
                icon[colorKey] = L.icon({
                    iconUrl: this.urlRouter['species_marker'](trace.genus || '-', trace.species || '-'),
                    shadowUrl: '/static/vendor/css/images/marker-shadow.png',

                    iconSize: [28, 44], // size of the icon
                    shadowSize: [41, 41], // size of the shadow
                    iconAnchor: [18, 44], // point of the icon which will correspond to marker's location
                    shadowAnchor: [10, 44],  // the same for the shadow
                    popupAnchor: [-4, -42] // point from which the popup should open relative to the iconAnchor
                });


                marker = L.marker(trace.latlon, {icon: icon[colorKey]});
                marker.bindPopup(this.formatTracePopup(trace));
                this.audioMarkers[id] = marker;
                this.markersLayer.addLayer(marker);

            }
        }

        return this;
    }


    formatTracePopup(trace) {
        let output = '<div class="recordingPopup">';
        if (trace.species) {
            let latinName = trace.genus + ' ' + trace.species + ' ';
            if (trace.species_info) {
                output += '<abbr title="' +
                    trace.species_info.genus + ' ' +
                    trace.species_info.species +
                    '">' + latinName + '</abbr>';
            } else {
                output += latinName;
            }
        } else {
            output += '(unknown) ';
        }

        output += moment.parseZone(trace.recorded_at).format('YYYY-MM-DD HH:mm');
        output += '<br />' + trace.duration.toFixed(2) + ' s';

        if (trace.species_info && trace.species_info.common_name) {
            output += '<br />' + trace.species_info.common_name;
        }

        output += '<br />';
        output += '<a title="Play" class="audioTrigger" ' +
            'data-audio-src="' + trace.url + '" ' +
            'data-audio-src-lo="' + trace.lo_url + '" ' +
            'data-audio-ident="' + trace.identifier + '">' +
            '<i class="fas fa-play"></i></a> ' +
            '<a title="Download" href="' + trace.url + '"><i class="fas fa-download"></i></a>';

        if (trace.spectrogram_url) {
            let spectrumTitle = 'Spectrum: ';
            if (trace.common_name) {
                spectrumTitle += trace.common_name;
            } else if (trace.species_info.species) {
                spectrumTitle += trace.species_info.genus + ' ' + trace.species_info.species;
            } else if (trace.genus) {
                spectrumTitle += trace.genus + ' ' + trace.species;
            } else {
                spectrumTitle += '(unidentified)';
            }

            if (trace.recorded_at) {
                spectrumTitle += ' ' + moment.parseZone(trace.recorded_at).format("YYYY-MM-DD HH:mm");
            }

            output += ' <a title="' + spectrumTitle + '" ' +
                'href="' + trace.spectrogram_url + '" ' +
                'class="spectrumTrigger" ' +
                'data-lightbox="' + trace.identifier + '">' +
                '<i class="far fa-chart-bar"></i></a>';
        }

        if (trace.species_info && trace.species_info.mdd_id) {
            const mdlink = mammalDiversitySpeciesLink(trace.species_info.mdd_id);
            output += ` ${mdlink} `;
        }

        const permaUrl = this.urlRouter['single_view'](trace.id);
        output = output + ' <div class="float-right"><a title="Permalink" href="' + permaUrl + '"><i class="fas fa-link"></i></a>';
        if (this.userIsAuthenticated) {
            const editUrl = this.urlRouter['admin:tracemap_audiorecording_change'](trace.id);
            output = output + ' <a title="Edit" href="' + editUrl + '"><i class="fas fa-pencil-alt"></i></a>';
        }
        output = output + '</div>';
        output = output + '</div>'; // close .recordingPopup

        return output;
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
                this.map.flyTo(this.audioMarkers[ident].getLatLng(), Math.max(this.map.getZoom(), zoomLevel));
            }
            this.audioMarkers[ident].openPopup();
            // document.getElementById('map-pane').scrollIntoView();
        }

        return this;
    }
}
