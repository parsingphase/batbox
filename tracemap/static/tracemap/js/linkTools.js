function mammalDiversitySpeciesUrl(speciesId) {
    return 'https://www.mammaldiversity.org/explore.html#species-id=' + speciesId;
}

function mammalDiversitySpeciesLink(speciesId) {
    const mdlink = mammalDiversitySpeciesUrl(speciesId);
    return `<a href="${mdlink}" target="_blank" title="More info at mammaldiversity.org"> ` +
        '<i class="fas fa-info-circle"></i></a>';
}

export {mammalDiversitySpeciesUrl, mammalDiversitySpeciesLink}