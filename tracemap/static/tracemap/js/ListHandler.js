/* jshint -W069 */ // Url handler uses [] notation for consistency

function ucFirst(s) {
    if (typeof s !== 'string') return '';
    return s.charAt(0).toUpperCase() + s.slice(1);
}

function renderUnknown(defaultString) {
    return function (data, type, row) {
        if (type === "sort" || type === "type") {
            return data;
        }
        return data ? data : defaultString;
    };
}

export default class ListHandler {
    // noinspection JSUnusedGlobalSymbols

    constructor(targetElementId, mapHandler) {
        this.targetElement = $('#' + targetElementId);
        this.player = null;
        this.playingFile = null;
        this.map = mapHandler; // MapHandler instance
        this.userIsAuthenticated = false;
        this.urlRouter = null;
        this.defaultLowResAudio = false;
    }

    setUserAuthenticated(flag) {
        this.userIsAuthenticated = flag;
    }

    setUrlRouter(router) {
        this.urlRouter = router;
    }

    initTable(recordings) {
        if (!this.urlRouter) {
            throw new Error("URL router must be configured");
        }

        const that = this;
        const table = this.targetElement.DataTable({
            data: recordings,
            columns: [
                {
                    data: 'recorded_at',
                    title: 'Recorded At',
                    render: function (data, type, row) {
                        if (type === "sort" || type === "type") {
                            return data;
                        }
                        if (data) {
                            let date = moment.parseZone(data).format("YYYY-MM-DD");
                            const url = that.urlRouter['day_view'](date);
                            return '<a href="' + url + '">' + date + '</a> ' + moment.parseZone(data).format('HH:mm');
                        }
                        return '(no time available)';
                    }
                },
                {
                    data: 'duration', title: 'Duration',
                    render: function (data, type, row) {
                        if (type === "sort" || type === "type") {
                            return data;
                        }
                        return data ? '<span class="duration">' + data.toFixed(2) + ' s </span>' : '-';
                    },
                    className: 'recording-duration',
                },
                {
                    data: 'species_info', title: 'Name',
                    render: function (data, type, row) {
                        let output = '';

                        if (data) {
                            if (data['common_name']) {
                                output = data['common_name'];
                            } else if (data['genus']) {
                                output = '<i>' + data['genus'] + ' ' + data['species'] + '</i>';
                            }
                        }
                        return output;
                    }
                },
                {
                    data: 'genus', title: 'Genus',
                    render: function (data, type, row) {
                        if (type === "sort" || type === "type") {
                            return data;
                        }
                        const url = that.urlRouter['genus_view'](data);
                        let title = '';
                        if (row['species_info'] && row['species_info']['genus']) {
                            title = 'title="' + row['species_info']['genus'] + '"';
                        }
                        return data ? '<a ' + title + ' href="' + url + '">' + data + '</a>' : '-';
                    }
                },
                {
                    data: 'species', title: 'Species', render: function (data, type, row) {
                        if (type === "sort" || type === "type") {
                            return data;
                        }
                        let title = '';
                        if (row['species_info'] && row['species_info']['species']) {
                            title = 'title="' + ucFirst(row['species_info']['species']) + '"';
                        }
                        const url = that.urlRouter['species_view'](row.genus, row.species);
                        return data ? '<a ' + title + ' href="' + url + '">' + data + '</a>' : '-';
                    }
                },
                {
                    data: 'latitude', title: 'Latitude', render: renderUnknown('-')
                },
                {
                    data: 'longitude', title: 'Longitude', render: renderUnknown('-')
                },
                {
                    data: 'url',
                    title: 'Controls',
                    orderable: false,
                    render:
                        function (data, type, row) {
                            if (type === "sort" || type === "type") {
                                return data;
                            }

                            let cellContent = '<a title="Play" class="audioTrigger" ' +
                                'data-audio-src="' + row.url + '" ' +
                                'data-audio-src-lo="' + row.lo_url + '" ' +
                                'data-audio-ident="' + row.identifier + '">' +
                                '<i class="fas fa-play"></i></a> ' +
                                '<a title="Download" href="' + data + '"><i class="fas fa-download"></i></a>';

                            if (row.latlon) {
                                cellContent = cellContent + ' <a title="Show" href="#" class="panTrigger" data-audio-ident="' + row.identifier + '">' +
                                    '<i class="fas fa-map-marker-alt"></i></a>' +
                                    ' <a title="Focus" href="#" class="panTriggerZoom" data-audio-ident="' + row.identifier + '">' +
                                    '<i class="fas fa-search-location"></i></a>';
                            }

                            if (row.spectrogram_url) {
                                let spectrumTitle = 'Spectrum: ';
                                if (row.common_name) {
                                    spectrumTitle += row.common_name;
                                } else if (row.species_info.species) {
                                    spectrumTitle += row.species_info.genus + ' ' + row.species_info.species;
                                } else if (row.genus) {
                                    spectrumTitle += row.genus + ' ' + row.species;
                                } else {
                                    spectrumTitle += '(unidentified)';
                                }

                                if (row.recorded_at) {
                                    // spectrumTitle += ' RA: ' + row.recorded_at;
                                    spectrumTitle += ' ' + moment.parseZone(row.recorded_at).format("YYYY-MM-DD HH:mm");
                                }

                                cellContent = cellContent + ' <a data-descr="' + spectrumTitle + '" ' +
                                    'title="Spectrogram" ' +
                                    'href="' + row.spectrogram_url + '" ' +
                                    'class="spectrumTrigger" ' +
                                    'data-audio-src="' + row.url + '" ' +
                                    'data-audio-src-lo="' + row.lo_url + '" ' +
                                    'data-audio-ident="' + row.identifier + '" ' +
                                    'data-lightbox="' + row.identifier + '">' +
                                    '<i class="far fa-chart-bar"></i></a>';
                            }

                            if (row.species_info && row.species_info.mdd_id) {
                                cellContent += ' <a href="https://mammaldiversity.org/species-account/species-id=' +
                                    row.species_info.mdd_id + '" title="More info at mammaldiversity.org">' +
                                    '<i class="fas fa-info-circle"></i></a> ';
                            }

                            const permaUrl = that.urlRouter['single_view'](row.id);
                            cellContent = cellContent + ' <div class="float-right"><a title="Permalink" href="' + permaUrl + '"><i class="fas fa-link"></i></a>';
                            if (that.userIsAuthenticated) {
                                const editUrl = that.urlRouter['admin:tracemap_audiorecording_change'](row.id);
                                cellContent = cellContent + ' <a title="Edit" href="' + editUrl + '"><i class="fas fa-pencil-alt"></i></a>';
                            }
                            cellContent = cellContent + '</div>';

                            return cellContent;
                        }
                },
            ],
            language: {
                'search': 'Filter:'
            }
        });
        this.resetRowControlTriggers();

        table.on('search.dt', function () {
            const newAudioList = table.rows({filter: 'applied'}).data().toArray();
            that.map.replaceAudioMarkers(newAudioList);
            that.resetRowControlTriggers();
        });

        table.on('draw.dt', function () {
            that.resetRowControlTriggers();
        });
    }

    playSourceElementAction(sourceElement) {
        const that = this;
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
    }

    resetRowControlTriggers() {
        let $panTriggers = this.targetElement.find('.panTrigger');
        $panTriggers.off('click');
        $panTriggers.click(function () {
            const id = $(this).data('audioIdent');
            that.map.panMapToAudioFile(id);
            return false; // prevent link action
        });
        let $panZoomTriggers = this.targetElement.find('.panTriggerZoom');
        $panZoomTriggers.off('click');
        $panZoomTriggers.click(function () {
            const id = $(this).data('audioIdent');
            that.map.panMapToAudioFile(id, 15);
            return false; // prevent link action
        });

        let $spectrumTriggers = this.targetElement.find('.spectrumTrigger');
        $spectrumTriggers.each(
            function () {
                const e = $(this);
                const origTitle = e.data('descr');
                const anchor = $(
                    '<a/>',
                    {
                        id: 'specTrigger_' + e.data('audioIdent'),
                        /*jshint -W107 */
                        // Have to use script url in lightbox as it doesn't share a code context at generation
                        href: "javascript:playSpectrogramAudio(\'specTrigger_" + e.data('audioIdent') + "\')",
                        /*jshint +W107 */
                        'data-audio-src': e.data('audioSrc'),
                        'data-audio-src-lo': e.data('audioSrcLo'),
                        'data-audio-ident': e.data('audioIdent'),
                    }
                );
                anchor.html('<i class="fas fa-play"></i>');

                const anchorHolder = $('<div/>');
                anchor.appendTo(anchorHolder);

                e.attr(
                    'data-title',
                    origTitle + ' | ' + anchorHolder.html()
                );
            }
        );

        let $audioTriggers = this.targetElement.find('.audioTrigger');
        $audioTriggers.off('click');

        const that = this;
        $audioTriggers.click(function () {
            let sourceElement = $(this); // the 'a' tag
            that.playSourceElementAction(sourceElement);
        });
    }

    playElementAudio(id, that) {
        that.playSourceElementAction($('#' + id));
    }
}

// https://stackoverflow.com/questions/33169649/how-to-get-filtered-data-result-set-from-jquery-datatable
// https://datatables.net/reference/api/toArray()

