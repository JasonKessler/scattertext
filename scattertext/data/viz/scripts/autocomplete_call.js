
autocomplete(
    document.getElementById('{{id}}'),
    __plotInterface__.data.map(x => x.term).sort(),
    __plotInterface__
);
