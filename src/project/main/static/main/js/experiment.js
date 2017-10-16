function print_plot(data) {
    "use strict";
    var pvaluecutoff = $("#pvalue_cutoff").val();
    var fccutoff = $("#fc_cutoff").val();

    var margin = {top: 20, right: 20, bottom: 50, left: 50};
    var width = 750 - margin.left - margin.right;
    var height = 500 - margin.top - margin.bottom;

    var x = d3.scaleLinear().range([0, width]);

    var y = d3.scaleLinear().range([height, 0]);

    var xAxis = d3.axisBottom().scale(x);

    var yAxis = d3.axisLeft().scale(y);

    d3.select("svg").remove();
    var svg = d3.select("#volcanoplot").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("rect")
        .attr("class", "rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", width)
        .attr("height", height)
        .style("fill", d3.rgb(255, 255, 255));

    x.domain(d3.extent(data, function (d) {
        return d.x;
    })).nice();
    y.domain(d3.extent(data, function (d) {
        return -1.0 * Math.log10(d.y);
    })).nice();

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("transform", "translate(" + (width / 2) + "," + (height + (35)) + ")")
        .text("log2(FC)");

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("transform", "translate(-35," + (height / 2) + ")rotate(-90)")
        .text("-1.0 * log10(P-Value)");

    svg.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("r", 2)
        .attr("cx", function (d) {
            return x(d.x);
        })
        .attr("cy", function (d) {
            return y(-1.0 * Math.log10(d.y));
        })
        .style("fill", function (d) {
            if (d.y <= pvaluecutoff && Math.abs(d.x) >= fccutoff) {
                return d3.color("red");
            } else {
                return d3.color("black");
            }
        });

    var p;
    var p_end;
    var rectElement = svg.append("rect")
        .attr("class", "selection")
        .attr("rx", 0)
        .attr("ry", 0)
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", 0)
        .attr("height", 0);

    function dragStart() {
        p_end = d3.mouse(this);
        p = p_end;
    }

    function dragMove() {
        p_end = d3.mouse(this);
        if (p[0] >= 0 && p[0] <= width &&
            p[1] >= 0 && p[1] <= height) {
            if (p_end[0] < 0) {
                p_end[0] = 0;
            }
            if (p_end[1] < 0) {
                p_end[1] = 0;
            }
            if (p_end[0] > width) {
                p_end[0] = width;
            }
            if (p_end[1] > height) {
                p_end[1] = height;
            }
            var xPoint = p[0];
            if (p[0] > p_end[0]) {
                xPoint = p_end[0];
            }
            var yPoint = p[1];
            if (p[1] > p_end[1]) {
                yPoint = p_end[1];
            }
            rectElement
                .attr("x", xPoint)
                .attr("y", yPoint)
                .attr("width", Math.abs(p_end[0] - p[0]))
                .attr("height", Math.abs(p_end[1] - p[1]));
        }
    }

    function dragEnd() {
        if (p[0] >= 0 && p[0] <= width &&
            p[1] >= 0 && p[1] <= height &&
            p_end[0] >= 0 && p_end[0] <= width &&
            p_end[1] >= 0 && p_end[1] <= height &&
            p[0] !== p_end[0]) {
            var xmin = p[0];
            var xmax = p_end[0];
            var ymin = p[1];
            var ymax = p_end[1];
            if (p[0] > p_end[0]) {
                xmin = p_end[0];
                xmax = p[0];
            }
            if (p[1] > p_end[1]) {
                ymin = p_end[1];
                ymax = p[1];
            }
            $("#exp_div").attr("xmin", x.invert(xmin));
            $("#exp_div").attr("xmax", x.invert(xmax));
            $("#exp_div").attr("ymin", y.invert(ymin));
            $("#exp_div").attr("ymax", y.invert(ymax));
            retrieve_experiment_data();
        }
    }

    var dragBehavior = d3.drag()
        .on("drag", dragMove)
        .on("start", dragStart)
        .on("end", dragEnd);

    svg.call(dragBehavior);
}

function loadSVdata() {
    "use strict";
    console.log("loadSVdata");
    var modal = document.getElementById("intron-popup");
    var span = document.getElementsByClassName("close")[0];
    span.onclick = function () {
        modal.style.display = "none";
        $("#SV0").empty();
    };
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
            $("#SV0").empty();
        }
    };
    modal.style.display = "block";
    var app = SeqView.App.findAppByDivId('SV0') || new SeqView.App('SV0');
    app.reload("appname=testapp&amp;id=NC_000021");
}

function draw_intron_table(jsonData) {
    "use strict";
    var dashboard = new google.visualization.Dashboard(document.getElementById("intron_list_container"));
    var data = new google.visualization.DataTable(jsonData);
    var formatter1 = new google.visualization.NumberFormat({pattern: "0.0E00"});
    formatter1.format(data, 5);

    var tableWrapper = new google.visualization.ChartWrapper({
        "chartType": "Table",
        "containerId": "intron_table",
        "dataTable": data,
        "options": {
            "width": 750,
            "allowHtml": true,
            "page": "enable",
            "pageSize": 25,
            "sortColumn": 4,
            "sortAscending": true
        },
        "view": {"columns": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    });

    var textChrFilter = new google.visualization.ControlWrapper({
        "controlType": "StringFilter",
        "containerId": "chr_name_filer",
        "options": {
            "filterColumnLabel": "Chr",
            "matchType": "exact"
        }
    });
    $("#chrbox").change(function () {
        var value = "";
        if ($("#chrbox").val() !== "0") {
            value = "chr" + $("#chrbox").val();
        }
        textChrFilter.setState({
            "value": value
        });
        textChrFilter.draw();
    });
    var textGeneFilter = new google.visualization.ControlWrapper({
        "controlType": "StringFilter",
        "containerId": "gene_name_filer",
        "options": {
            "filterColumnLabel": "Gene",
            "matchType": "prefix"
        }
    });
    var tpm1RangeSlider = new google.visualization.ControlWrapper({
        "controlType": "NumberRangeFilter",
        "containerId": "tpm1_filter",
        "options": {
            "filterColumnLabel": "TPM1"
        }
    });
    var tpm2RangeSlider = new google.visualization.ControlWrapper({
        "controlType": "NumberRangeFilter",
        "containerId": "tpm2_filter",
        "options": {
            "filterColumnLabel": "TPM2"
        }
    });

    google.visualization.events.addListener(tableWrapper, "select", function () {
        var obj = tableWrapper.getChart().getSelection();
        var dt = tableWrapper.getDataTable();
        if (obj.length === 1) {
            console.log("Selecting: " + obj[0].row);
            var win = window.open("/intron/" + dt.getValue(obj[0].row, 0) + "/", "_blank");
            if (win) {
                //Browser has allowed it to be opened
                win.focus();
            } else {
                //Browser has blocked it
                alert("Please allow popups for this website");
            }
        }
    });


    google.visualization.events.addListener(tableWrapper, "ready", function () {
        var data_plot = [];
        var filtered_data = tableWrapper.getDataTable();
        var foundRows = filtered_data.getNumberOfRows();
        for (var y = 0; y < foundRows; y++) {
            data_plot.push({
                "x": filtered_data.getValue(y, 8),
                "y": filtered_data.getValue(y, 5)
            });
        }
        $("#loading_icon").removeClass("visible").addClass("invisible");
        print_plot(data_plot);
        $("#exp_div_data").removeClass("invisible").addClass("visible");
        $("#download_cvs").click(function () {
            var csv = google.visualization.dataTableToCsv(filtered_data);
            var blob = new Blob([csv], {type: "text/csv;charset=utf-8"});
            var url = window.URL || window.webkitURL;
            var link = document.createElementNS("http://www.w3.org/1999/xhtml", "a");
            link.href = url.createObjectURL(blob);
            link.download = "data.csv";

            var event = document.createEvent("MouseEvents");
            event.initEvent("click", true, false);
            link.dispatchEvent(event);
        });
    });

    dashboard.bind([textChrFilter, textGeneFilter, tpm1RangeSlider, tpm2RangeSlider], tableWrapper);
    dashboard.draw(data);
}


function retrieve_experiment_data_container() {
    "use strict";
    var query = {
        "exp_id": $("#exp_div").attr("exp_id")
    };
    var setResetButton = false;
    var minuslog10pvalue = $("#exp_div").attr("minuslog10pvalue");
    if (typeof minuslog10pvalue !== "undefined") {
        query.minuslog10pvalue = minuslog10pvalue;
        setResetButton = true;
    }
    var fc = $("#exp_div").attr("fc");
    if (typeof fc !== "undefined") {
        query.fc = fc;
        setResetButton = true;
    }
    var xmin = $("#exp_div").attr("xmin");
    if (typeof xmin !== "undefined") {
        query.xmin = xmin;
        setResetButton = true;
    }
    var xmax = $("#exp_div").attr("xmax");
    if (typeof xmax !== "undefined") {
        query.xmax = xmax;
        setResetButton = true;
    }
    var ymin = $("#exp_div").attr("ymin");
    if (typeof ymin !== "undefined") {
        query.ymin = ymin;
        setResetButton = true;
    }
    var ymax = $("#exp_div").attr("ymax");
    if (typeof ymax !== "undefined") {
        query.ymax = ymax;
        setResetButton = true;
    }
    if (setResetButton) {
        $("#resetplot").button("enable");
    } else {
        $("#resetplot").button("disable");
    }
    query.viewsig = $("#view_sig").prop("checked");
    query.pvalue_cutoff = $("#pvalue_cutoff").val();
    query.r_cutoff = $("#r_cutoff").val();
    query.fc_cutoff = $("#fc_cutoff").val();
    postAjax("/service/", "search", "expintron", JSON.stringify(query), function (ajax_data) {
        var modelData = JSON.parse(ajax_data.response.value);
        var pvalue_cutoff = $("#pvalue_cutoff").val();
        var fc_cutoff = $("#fc_cutoff").val();
        var background = "background-color: red;";
        var rows = [];
        for (var i = 0; i < modelData.length; i++) {
            if (modelData[i].fields.pvalue <= pvalue_cutoff && Math.abs(modelData[i].fields.fc) >= fc_cutoff) {
                rows.push({
                    "c": [
                        {"v": modelData[i].pk},
                        {"v": modelData[i].fields.chr},
                        {"v": modelData[i].fields.gene, "p": {"style": "background-color: red;color:yellow;"}},
                        {"v": modelData[i].fields.start},
                        {"v": modelData[i].fields.end},
                        {"v": modelData[i].fields.pvalue},
                        {"v": modelData[i].fields.TPM1},
                        {"v": modelData[i].fields.TPM2},
                        {"v": modelData[i].fields.fc},
                        {"v": modelData[i].fields.r1},
                        {"v": modelData[i].fields.r2},
                    ]
                });
            } else {
                rows.push({
                    "c": [
                        {"v": modelData[i].pk},
                        {"v": modelData[i].fields.chr},
                        {"v": modelData[i].fields.gene},
                        {"v": modelData[i].fields.start},
                        {"v": modelData[i].fields.end},
                        {"v": modelData[i].fields.pvalue},
                        {"v": modelData[i].fields.TPM1},
                        {"v": modelData[i].fields.TPM2},
                        {"v": modelData[i].fields.fc},
                        {"v": modelData[i].fields.r1},
                        {"v": modelData[i].fields.r2},
                    ]
                });
            }
        }
        var data = {
            "cols": [
                {"id": "id", "label": "ID", "type": "number"},
                {"id": "chr", "label": "Chr", "type": "string"},
                {"id": "gene", "label": "Gene", "type": "string"},
                {"id": "start", "label": "Start", "type": "number"},
                {"id": "end", "label": "End", "type": "number"},
                {"id": "pvalue", "label": "Pvalue", "type": "number"},
                {"id": "tpm1", "label": "TPM1", "type": "number"},
                {"id": "tpm2", "label": "TPM2", "type": "number"},
                {"id": "fc", "label": "log2FC", "type": "number"},
                {"id": "r1", "label": "R1", "type": "number"},
                {"id": "r2", "label": "R2", "type": "number"},
            ],
            "rows": rows
        };
        draw_intron_table(data);

    });
}

function retrieve_experiment_data() {
    google.load("visualization", "1", {
        "callback": retrieve_experiment_data_container,
        "packages": ["corechart", "table", "controls", "scatter"]
    });
}

