// {# FIXME - set a config for base URL #}

function renderUnknown(defaultString) {
    return function (data, type, row) {
        if (type === "sort" || type === "type") {
            return data;
        }
        return data ? data : defaultString;
    }
}

export default class ListHandler {
    // noinspection JSUnusedGlobalSymbols

    constructor(targetElementId, mapHandler) {
        this.targetElement = $('#' + targetElementId);
        this.player = null;
        this.playingFile = null;
        this.map = mapHandler; // MapHandler instance
    }

    initTable(recordings) {
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
                            let date = moment(data).format("YYYY-MM-DD");
                            return '<a href="/byday/' + date + '">' + date + '</a> ' + moment(data).format('HH:mm');
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
                        return data ? '<span class="duration">' + data.toFixed(2) + ' s </span>' : '-'
                    },
                    className: 'recording-duration',
                },
                {
                    data: 'genus', title: 'Genus',
                    render: function (data, type, row) {
                        if (type === "sort" || type === "type") {
                            return data;
                        }
                        return data ? '<a href="/genus/' + data + '">' + data + '</a>' : '-'
                    }
                },
                {
                    data: 'species', title: 'Species', render: function (data, type, row) {
                        if (type === "sort" || type === "type") {
                            return data;
                        }
                        return data ? '<a href="/species/' + row.genus + '.' + row.species + '">' + data + '</a>' : '-'
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
                            let cellContent = '<a title="Play" class="audioTrigger" data-audio-src="' + row.url + '" ' +
                                'data-audio-ident="' + row.identifier + '">' +
                                '<i class="fas fa-play"></i></a>'
                                + ' <a title="Download" href="' + data + '"><i class="fas fa-download"></i></a>';

                            if (row.latlon) {
                                cellContent = cellContent + ' <a title="Show" href="#" class="panTrigger" data-audio-ident="' + row.identifier + '">' +
                                    '<i class="fas fa-map-marker-alt"></i></a>' +
                                    ' <a title="Focus" href="#" class="panTriggerZoom" data-audio-ident="' + row.identifier + '">' +
                                    '<i class="fas fa-search-location"></i></a>';
                            }

                            cellContent = cellContent + ' <a title="Permalink" class="float-right" href="/recording/' + row.id + '"><i class="fas fa-link"></i></a>';

                            return cellContent;
                        }
                },
            ]
        });
        this.resetRowControlTriggers();

        const that = this;
        table.on('search.dt', function () {
            const newAudioList = table.rows({filter: 'applied'}).data().toArray();
            this.map.replaceAudioMarkers(newAudioList);
            that.resetRowControlTriggers();
        });

        table.on('draw.dt', function () {
            that.resetRowControlTriggers();
        });
    }

    resetRowControlTriggers() {
        let $panTriggers = this.targetElement.find('.panTrigger');
        $panTriggers.off('click');
        const that=this;
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
        let $audioTriggers = this.targetElement.find('.audioTrigger');
        $audioTriggers.off('click');

        $audioTriggers.click(function () {
            let sourceElement = $(this);
            const id = sourceElement.data('audioIdent');
            const src = sourceElement.data('audioSrc');

            // Reset if we change sample
            if (that.playingFile !== id) {
                if (that.player) {
                    that.player.pause();
                }
                that.player = null;
                that.targetElement.find('.audioTrigger').html('<i class="fas fa-play"></i>');
            }

            that.playingFile = id;

            if (!that.player) {
                that.player = new Audio(src);
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
                that.player = null;
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
}

// https://stackoverflow.com/questions/33169649/how-to-get-filtered-data-result-set-from-jquery-datatable
// https://datatables.net/reference/api/toArray()

