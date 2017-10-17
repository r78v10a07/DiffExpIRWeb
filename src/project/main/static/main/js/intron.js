function loadseqviwer() {
    "use strict";
    console.log("loadSVdata");
    var app = SeqView.App.findAppByDivId('SV0') || new SeqView.App('SV0');
    var chr = $("#intron_div").attr("intron_chr");
    var coord = $("#intron_div").attr("intron_coord");
    console.log("Coord: " + coord);
    var str = "appname=diffexpir&amp;id=" + chr + "&amp;v=" + coord;
    app.reload(str);
}