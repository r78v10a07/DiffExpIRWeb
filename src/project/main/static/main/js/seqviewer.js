function seqviewer(id) {
    "use strict";
    console.log("Loading SeqViewer");
    var app = new SeqView.App(id);
    var str = "?embedded=true&appname=diffexpirweb&id=NC_000001.10";
    app.load(str);
}

function show_seqviewer(id, data) {
    "use strict";
    // var app = new SeqView.App("SeqViewer");
    // var str = "?embedded=true&appname=diffexpir&id=NC_000001.10";
    // str += "&tracks=[key:sequence_track,name:Sequence,display_name:Sequence,id:STD1,category:Sequence,annots:Sequence,ShowLabel:false,shown:true,order:1]";
    // str += "[key:gene_model_track,name:Genes,display_name:Genes,id:STD13,category:Genes,annots:Unnamed,Options:MergeAll,SNPs:false,CDSProductFeats:false,NtRuler:true,AaRuler:true,HighlightMode:2,shown:true,order:13]"
    // str += "&v=" + data.coord;
    // str += "&v=159900658:159900927&c=FFFF00&select=null&slim=0";
    // app.load(str);
    var app = SeqView.App.findAppByDivId(id) || new SeqView.App(id);
    app.reload("appname=testapp&amp;id=NC_000021");
}

var loadSV = function () {
    var app = SeqView.App.findAppByDivId('SV0') || new SeqView.App('SV0');
    app.reload("appname=testapp&amp;id=NC_000021");
}