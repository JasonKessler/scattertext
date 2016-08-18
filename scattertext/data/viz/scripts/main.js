/**
 * Created by kesslej on 7/30/16.
 */

// Get the data
//d3.json('words.json', processData);
var divName = 'd3-div-1';

// Set the dimensions of the canvas / graph
var margin = {top: 30, right: 20, bottom: 30, left: 50},
    width = 800 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

//width = 800 - margin.left - margin.right,
//height = 600 - margin.top - margin.bottom;

// Set the ranges
var x = d3.scaleLinear().range([0, width]);
var y = d3.scaleLinear().range([height, 0]);

// Define the axes
/*
 var xAxis = d3.axisBottom().scale(x)
 .orient("bottom").ticks(5);
 */

function axisLabler(d, i) {
    return ["Infrequent", "Average", "Frequent"][i]
}

var xAxis = d3.axisBottom(x).ticks(3).tickFormat(axisLabler);

var yAxis = d3.axisLeft(y).ticks(3).tickFormat(axisLabler);

// Define the div for the tooltip
//var tooltip = d3.select("body").append("div")
var tooltip = d3.select('#' + divName).append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

//var label = d3.select("body").append("div")
var label = d3.select('#' + divName).append("div")
      .attr("class", "label");

// setup fill color
var color = d3.interpolateRdYlBu;

// Adds the svg canvas
//var svg = d3.select("body")
var svg = d3.select('#' + divName)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform",
        "translate(" + margin.left + "," + margin.top + ")");

/*
var categoryTermList = d3.select('#' + divName)
    .append("ul");
*/

function processData(jsonObject) {
    var modelInfo = jsonObject['info'];
    /*
    categoryTermList.data(modelInfo['category_terms'])
        .enter()
        .append("li")
        .text(function(d) {return d;});
    */
    var data = jsonObject['data'];
    console.log(data);
    // Scale the range of the data.  Add some space on either end.
    x.domain([-0.1, d3.max(data, function (d) {
        return d.x;
    }) + 0.1]);
    y.domain([-0.1, d3.max(data, function (d) {
        return d.y;
    }) + 0.1]);


    var rangeTree = null; // keep boxes of all points and labels here
    // Add the scatterplot
    svg.selectAll("dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("r", 2)
        .attr("cx", function (d) {
            return x(d.x);
        })
        .attr("cy", function (d) {
            return y(d.y);
        })
        .style("fill", function (d) {
            return color(d.s);
        })
        .on("mouseover", function (d) {
            tooltip.transition()
                .duration(0)
                .style("opacity", 1)
                .style("z-index", 1000000);
            tooltip.html(d.term + "<br/>" + d.cat25k + ":" + d.ncat25k + " per 25k words")
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function (d) {
            tooltip.transition()
                .duration(0)
                .style("opacity", 0);
        });


    console.log('dot');
    console.log(svg.selectAll('circle'));

    coords = Object();
    function censorPoints(datum) {
        var term = datum.term;
        //var curLabel = d3.select("body").append("div")
        var curLabel = d3.select('#' + divName).append("div")

            .attr("class", "label").html('L')
            .style("left", x(datum.x) + margin.left + 5 + 'px')
            .style("top", y(datum.y) + margin.top + 4 + 'px');
        var curDiv = curLabel._groups[0][0];

        var x1 = curDiv.offsetLeft - 2 + 2;
        var y1 = curDiv.offsetTop - 2 + 5;
        var x2 = curDiv.offsetLeft + 2 + 2;
        var y2 = curDiv.offsetTop + 2 + 5;
        /*
         var x1 = curDiv.offsetLeft - 2;
         var y1 = curDiv.offsetTop - 2;
         var x2 = curDiv.offsetLeft + 2;
         var y2 = curDiv.offsetTop + 2;
         */
        curLabel.remove();
        //if (!searchRangeTree(rangeTree, x1, y1, x2, y2)) {
        rangeTree = insertRangeTree(rangeTree, x1, y1, x2, y2, '~~' + term);
        //}

        if (term == 'an economy') {
            console.log("~~an economy " + " X" + x1 + ":" + x2 + " Y" + y1 + ":" + y2)
        }
        coords['~~' + term] = [x1, y1, x2, y2];
    }

    function labelPointBottomLeft(i) {
        var term = data[i].term;
        //var curLabel = d3.select("body").append("div")
        var curLabel = d3.select("#" + divName).append("div")
              .attr("class", "label").html(term)
            .style("left", x(data[i].x) + margin.left + 10 + 'px')
            .style("top", y(data[i].y) + margin.top + 8 + 'px');
        var curDiv = curLabel._groups[0][0];

        var x1 = curDiv.offsetLeft;
        var y1 = curDiv.offsetTop;
        var x2 = curDiv.offsetLeft + curDiv.offsetWidth;
        var y2 = curDiv.offsetTop + curDiv.offsetHeight;



        //move it to top right
        /*
         var width = curDiv.offsetWidth;
         var height = curDiv.offsetHeight;

         curLabel.remove();
         var curLabel = d3.select("body").append("div")
         .attr("class", "label").html(term)
         .style("left", x(data[i].x) + margin.left  + 10 - width + 'px')
         .style("top", y(data[i].y) + margin.top + 8  - height + 'px');
         var curDiv = curLabel._groups[0][0];

         var x2 = curDiv.offsetLeft;
         var y2 = curDiv.offsetTop;
         var x1 = curDiv.offsetLeft - curDiv.offsetWidth;
         var y1 = curDiv.offsetTop - curDiv.offsetHeight;
         */
        //console.log('x' + x(data[i].x) + margin.left + ' vs ' + curDiv.offsetLeft);
        //console.log(curDiv.offsetLeft - (10 + x(data[i].x) + margin.left));
        //console.log('y' + y(data[i].y) +  margin.top);
        //console.log(curDiv.offsetTop - (8 + y(data[i].y) +  margin.top));
        var matchedElement = searchRangeTree(rangeTree, x1, y1, x2, y2);
        if (term == 'affordable') {
            console.log(term + " " + " X" + x1 + ":" + x2 + " Y" + y1 + ":" + y2)
            var matchedCoord = coords[matchedElement];
            var mx1 = matchedElement[0];
            var my1 = matchedElement[1];
            var mx2 = matchedElement[2];
            var my2 = matchedElement[3];
            var x_diff = 0;
            var y_diff = 0;
            if(x1 >= mx1 && x1 < mx2) {
               x_diff = mx2 - x1;
            }
            if(x2 > mx1 && x2 <= mx2) {
               x_diff = mx1 - x2;
            }
            x1 += x_diff;
            x2 += x_diff;
            if(y1 >= my1 && y1 < my2) {
               y_diff = my2 - y1;
            }
            if(y2 > my1 && y2 <= my2) {
               y_diff = my1 - y2;
            }
            y1 += y_diff;
            y2 += y_diff;
            console.log(y_diff, x_diff)
            var matchedElement = searchRangeTree(rangeTree, x1, y1, x2, y2);
            console.log(term + " " + " X" + x1 + ":" + x2 + " Y" + y1 + ":" + y2)
            console.log('matchedElement ' + matchedElement)
            console.log('matchedElement ' + matchedCoord)

        }

        if (!matchedElement || term == 'affordable') {
            coords[term] = [x1, y1, x2, y2];
            rangeTree = insertRangeTree(rangeTree, x1, y1, x2, y2, term);
            return true;
        } else {
            curLabel.remove();
            return false;
        }

    }

    var radius = 2;
    console.log('Data length ' + data.length);
    // prevent intersections with points.. not quite working
    /*
    for (var i = 0; i < data.length; i++) {

        //if (!searchRangeTree(rangeTree, x1, y1, x2, y2)) {
        //    rangeTree = insertRangeTree(rangeTree, x1, y1, x2, y2, i);
        //}
    }*/

    //var nodes = Array.prototype.slice.call(svg.selectAll('circle')._groups[0],0);
    //console.log("NODES");console.log(nodes);

    /*
     var nodeI = 0;
     nodes.forEach(
     function (node) {
     var rect = node.getBoundingClientRect();
     rangeTree = insertRangeTree(rangeTree, rect.left, rect.top, rect.right, rect.bottom, nodeI++);
     }
     );*/
    //console.log("Range Tree");
    //console.log(rangeTree);
    data = data.sort(function (a, b) { // sort by euclidean distance
        var aCatDist = a.x * a.x + (1 - a.y) * (1 - a.y);
        var aNotCatDist = a.y * a.y + (1 - a.x) * (1 - a.x);
        var bCatDist = b.x * b.x + (1 - b.y) * (1 - b.y);
        var bNotCatDist = b.y * b.y + (1 - b.x) * (1 - b.x);
        return (Math.min(aCatDist, aNotCatDist) > Math.min(bCatDist, bNotCatDist)) * 2 - 1
    });

    console.log(data[0])
    console.log("censoring");
    //for (i = 0; i < data.length; censorPoints(i++));
    data.forEach(censorPoints)
    console.log("writing")
    for (i = 0; i < data.length; labelPointBottomLeft(i++));
    console.log("coords")
    console.log(coords)
    // Add the X Axis
    var myXAxis = svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    var xLabel = svg.append("text")
        .attr("class", "x label")
        .attr("text-anchor", "end")
        .attr("x", width)
        .attr("y", height - 6)
        .text(modelInfo['not_category_name'] + " Frequency");
    console.log('xLabel');
    console.log(xLabel);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "30px")
        .attr("dy", "-13px")
        .attr("transform", "rotate(-90)");

    svg.append("text")
        .attr("class", "y label")
        .attr("text-anchor", "end")
        .attr("y", 6)
        .attr("dy", ".75em")
        .attr("transform", "rotate(-90)")
        .text(modelInfo['category_name'] + " Frequency");
};

// from words.js
processData(getDataAndInfo());
