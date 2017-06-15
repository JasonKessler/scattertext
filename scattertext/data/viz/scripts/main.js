buildViz = function (d3) {
    return function (widthInPixels = 800,
                     heightInPixels = 600,
                     max_snippets = null,
                     color = null,
                     sortByDist = true,
                     useFullDoc = false,
                     greyZeroScores = false,
                     asianMode = false,
                     nonTextFeaturesMode = false,
                     showCharacteristic = true,
                     wordVecMaxPValue = false,
                     saveSvgButton = false,
                     reverseSortScoresForNotCategory = false,
                     minPVal = 0.05,
                     pValueColors = false,
                     xLabelText = null,
                     yLabelText = null) {
        var divName = 'd3-div-1';

        // Set the dimensions of the canvas / graph
        var margin = {top: 30, right: 20, bottom: 30, left: 50},
            width = widthInPixels - margin.left - margin.right,
            height = heightInPixels - margin.top - margin.bottom;

        // Set the ranges
        var x = d3.scaleLinear().range([0, width]);
        var y = d3.scaleLinear().range([height, 0]);

        console.log('X Label');
        console.log(xLabelText);
        console.log('Y Label');
        console.log(yLabelText);
        console.log(yLabelText == null);
        console.log(yLabelText != null);
        console.log(yLabelText === undefined);
        console.log(yLabelText !== undefined);

        function axisLabelerFactory(axis) {
            if ((axis == "x" && xLabelText == null)
                || (axis == "y" && yLabelText == null))
                return function (d, i) {
                    return ["Infrequent", "Average", "Frequent"][i];
                };

            return function (d, i) {
                return ["Low", "Medium", "High"][i];
            }
        }

        var xAxis = d3.axisBottom(x).ticks(3).tickFormat(axisLabelerFactory('x'));
        var yAxis = d3.axisLeft(y).ticks(3).tickFormat(axisLabelerFactory('y'));

        // var label = d3.select("body").append("div")
        var label = d3.select('#' + divName).append("div")
            .attr("class", "label");

        var interpolateLightGreys = d3.interpolate(d3.rgb(230, 230, 230), d3.rgb(130, 130, 130));
        // setup fill color
        //var color = d3.interpolateRdYlBu;
        if (color == null) {
            color = d3.interpolateRdYlBu;
        }
        ;

        // Adds the svg canvas
        // var svg = d3.select("body")
        svg = d3.select('#' + divName)
            .append("svg")
            .attr("width", width + margin.left + margin.right + 200)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        var lastCircleSelected = null;

        function deselectLastCircle() {
            if (lastCircleSelected) {
                lastCircleSelected.style["stroke"] = null;
                lastCircleSelected = null;
            }
        }

        function getSentenceBoundaries(text) {
            // !!! need to use spacy's sentence splitter
            if (asianMode) {
                var sentenceRe = /\n/gmi;
            } else {
                var sentenceRe = /\(?[^\.\?\!\n\b]+[\n\.!\?]\)?/g;
            }
            var offsets = [];
            var match;
            while ((match = sentenceRe.exec(text)) != null) {
                offsets.push(match.index);
            }
            offsets.push(text.length);
            return offsets;
        }

        function getMatchingSnippet(text, boundaries, start, end) {
            var sentenceStart = null;
            var sentenceEnd = null;
            for (var i in boundaries) {
                var position = boundaries[i];
                if (position <= start && (sentenceStart == null || position > sentenceStart)) {
                    sentenceStart = position;
                }
                if (position >= end) {
                    sentenceEnd = position;
                    break;
                }
            }
            var snippet = (text.slice(sentenceStart, start) + "<b>" + text.slice(start, end)
            + "</b>" + text.slice(end, sentenceEnd)).trim();
            if (sentenceStart == null) {
                sentenceStart = 0;
            }
            return {'snippet': snippet, 'sentenceStart': sentenceStart};
        }

        function gatherTermContexts(d) {
            var category_name = fullData['info']['category_name'];
            var not_category_name = fullData['info']['not_category_name'];
            var matches = [[], []];
            if (fullData.docs === undefined) return matches;
            if (!nonTextFeaturesMode) {
                return searchInText(d);
            } else {
                return searchInExtraFeatures(d);
            }
        }

        function searchInExtraFeatures(d) {
            var matches = [[], []];
            var term = d.term;
            for (var i in fullData.docs.extra) {

                if (term in fullData.docs.extra[i]) {
                    var strength = fullData.docs.extra[i][term] /
                        Object.values(fullData.docs.extra[i]).reduce(
                            function (a, b) {
                                return a + b
                            });
                    var text = fullData.docs.texts[i];
                    if (!useFullDoc)
                        text = text.slice(0, 300);
                    var curMatch = {'id': i, 'snippets': [text], 'strength': strength};

                    curMatch['meta'] = fullData.docs.meta[i];
                    matches[fullData.docs.labels[i]].push(curMatch);
                }
            }
            for (var i in [0, 1]) {
                matches[i] = matches[i].sort(function (a, b) {
                    return a.strength < b.strength ? 1 : -1
                })
            }
            return {'contexts': matches, 'info': d};
        }

        function searchInText(d) {
            function stripNonWordChars(term) {
                //d.term.replace(" ", "[^\\w]+")
            }

            function buildMatcher(term) {
                var boundary = '\\b';
                var wordSep = "[^\\w]+";
                if (asianMode) {
                    boundary = '( |$|^)';
                    wordSep = ' ';
                }
                var regexp = new RegExp(boundary + '('
                    + term.replace(' ', wordSep, 'gim') + ')' + boundary, 'gim');
                try {
                    regexp.exec('X');
                } catch (err) {
                    console.log("Can't search " + term);
                    console.log(err);
                    return null;
                }
                return regexp;
            }

            var matches = [[], []];
            var pattern = buildMatcher(d.term);
            if (pattern !== null) {
                for (var i in fullData.docs.texts) {
                    if (fullData.docs.labels[i] > 1) continue;
                    var text = fullData.docs.texts[i];
                    //var pattern = new RegExp("\\b(" + stripNonWordChars(d.term) + ")\\b", "gim");
                    var match;
                    var sentenceOffsets = null;
                    var lastSentenceStart = null;
                    var matchFound = false;
                    var curMatch = {'id': i, 'snippets': []};
                    if (fullData.docs.meta) {
                        curMatch['meta'] = fullData.docs.meta[i];
                    }
                    while ((match = pattern.exec(text)) != null) {
                        if (sentenceOffsets == null) {
                            sentenceOffsets = getSentenceBoundaries(text);
                        }
                        var foundSnippet = getMatchingSnippet(text, sentenceOffsets,
                            match.index, pattern.lastIndex);
                        if (foundSnippet.sentenceStart == lastSentenceStart) continue; // ensure we don't duplicate sentences
                        lastSentenceStart = foundSnippet.sentenceStart;
                        curMatch.snippets.push(foundSnippet.snippet);
                        matchFound = true;
                    }
                    if (matchFound) {
                        if (useFullDoc) {
                            curMatch.snippets = [
                                text
                                    .replace(/\n$/g, '\n\n')
                                    .replace(
                                        //new RegExp("\\b(" + d.term.replace(" ", "[^\\w]+") + ")\\b",
                                        //    'gim'),
                                        pattern,
                                        '<b>$&</b>')
                            ];
                        }
                        matches[fullData.docs.labels[i]].push(curMatch);

                    }
                }
            }
            return {'contexts': matches, 'info': d};
        }

        function displayTermContexts(termInfo, jump=true) {
            var contexts = termInfo.contexts;
            var info = termInfo.info;
            if (contexts[0].length == 0 && contexts[1].length == 0) {
                return null;
            }
            //var categoryNames = [fullData.info.category_name,
            //    fullData.info.not_category_name];
            var catInternalName = fullData.info.category_internal_name;
            fullData.docs.categories
                .map(
                    function (catName, catIndex) {
                        if (max_snippets != null) {
                            var contextsToDisplay = contexts[catIndex].slice(0, max_snippets);
                        }
                        var divId = catName == catInternalName ? '#cat' : '#notcat';
                        var temp = d3.select(divId)
                            .selectAll("div").remove();
                        contexts[catIndex].forEach(function (context) {
                            var meta = context.meta ? context.meta : '&nbsp;';
                            d3.select(divId)
                                .append("div")
                                .attr('class', 'snippet_meta')
                                .html(meta);
                            context.snippets.forEach(function (snippet) {
                                d3.select(divId)
                                    .append("div")
                                    .attr('class', 'snippet')
                                    .html(snippet);
                            })

                        });
                    });
            d3.select('#termstats')
                .selectAll("div")
                .remove();
            d3.select('#termstats')
                .append('div')
                .attr("class", "snippet_header")
                .html('Term: <b>' + info.term + '</b>');
            var message = '';
            var cat_name = fullData.info.category_name;
            var ncat_name = fullData.info.not_category_name;

            function getFrequencyDescription(name, count25k, count) {
                var desc = name + ' frequency: <div class=text_subhead>' + count25k
                    + ' per 25,000 terms</div>';
                if (count == 0) {
                    desc += '<u>Not found in any ' + name + ' documents.</u>';
                } else {
                    desc += '<u>Some of the ' + count + ' mentions:</u>';
                }
                return desc;
            }

            d3.select('#cathead')
                .style('fill', color(1))
                .html(getFrequencyDescription(cat_name, info.cat25k, info.cat));
            d3.select('#notcathead')
                .style('fill', color(0))
                .html(getFrequencyDescription(ncat_name, info.ncat25k, info.ncat));
            console.log(info);
            if (jump) {
                if (window.location.hash == '#snippets') {
                    window.location.hash = '#snippetsalt';
                } else {
                    window.location.hash = '#snippets';
                }
            }
        }

        function showTooltip(d, pageX, pageY) {
            deselectLastCircle();
            var message = d.term + "<br/>" + d.cat25k + ":" + d.ncat25k + " per 25k words";
            if (!sortByDist) {
                message += '<br/>score: ' + d.os.toFixed(5);
            }
            /*
             if (d.p) {
             message += ';  (p:' + d.p.toFixed(5) +')';
             }*/

            tooltip.transition()
                .duration(0)
                .style("opacity", 1)
                .style("z-index", 10000000);
            tooltip.html(message)
                .style("left", (pageX) + "px")
                .style("top", (pageY - 28) + "px");

            tooltip.on('click', function () {
                tooltip.transition()
                    .style('opacity', 0)
            });
        }

        handleSearch = function (event) {
            deselectLastCircle();
            var searchTerm = document
                .getElementById("searchTerm")
                .value
                .toLowerCase()
                .replace("'", " '")
                .trim();
            showToolTipForTerm(searchTerm);
            var termInfo = termDict[searchTerm];
            if (termInfo != null) {
                displayTermContexts(gatherTermContexts(termInfo), false);
            }
            return false;
        };

        function showToolTipForTerm(searchTerm) {
            var searchTermInfo = termDict[searchTerm];
            if (searchTermInfo === undefined) {
                d3.select("#alertMessage")
                    .text(searchTerm + " didn't make it into the visualization.");
            } else {
                d3.select("#alertMessage").text("");
                var circle = mysvg._groups[0][searchTermInfo.i];
                var mySVGMatrix = circle.getScreenCTM()
                    .translate(circle.cx.baseVal.value, circle.cy.baseVal.value);
                var pageX = mySVGMatrix.e;
                var pageY = mySVGMatrix.f;
                circle.style["stroke"] = "black";
                showTooltip(searchTermInfo, pageX, pageY);
                lastCircleSelected = circle;

            }
        };

        function makeWordInteractive(domObj, term) {
            return domObj
                .on("mouseover", function (d) {
                    showToolTipForTerm(term);
                    d3.select(this).style("stroke", "black");
                })
                .on("mouseout", function (d) {
                    tooltip.transition()
                        .duration(0)
                        .style("opacity", 0);
                    d3.select(this).style("stroke", null);
                })
                .on("click", function (d) {
                    displayTermContexts(gatherTermContexts(termDict[term]));
                });
        }

        function processData(fullData) {
            var modelInfo = fullData['info'];
            /*
             categoryTermList.data(modelInfo['category_terms'])
             .enter()
             .append("li")
             .text(function(d) {return d;});
             */
            data = fullData['data'];
            termDict = Object();
            data.forEach(function (x, i) {
                termDict[x.term] = x;
                termDict[x.term].i = i;
            });

            console.log(data);
            // Scale the range of the data.  Add some space on either end.
            x.domain([-0.1, d3.max(data, function (d) {
                return d.x;
            }) + 0.1]);
            y.domain([-0.1, d3.max(data, function (d) {
                return d.y;
            }) + 0.1]);

            /*
             data.sort(function (a, b) {
             return Math.abs(b.os) - Math.abs(a.os)
             });
             */


            //var rangeTree = null; // keep boxes of all points and labels here
            var rectHolder = new RectangleHolder();
            // Add the scatterplot
            mysvg = svg
                .selectAll("dot")
                .data(data)
                .enter()
                .append("circle")
                .attr("r", function (d) {
                    if (pValueColors && d.p) {
                        return (d.p >= 1 - minPVal || d.p <= minPVal) ? 2 : 1.75;
                    }
                    return 2;
                })
                .attr("cx", function (d) {
                    return x(d.x);
                })
                .attr("cy", function (d) {
                    return y(d.y);
                })
                .style("fill", function (d) {
                    //.attr("fill", function (d) {
                    if (greyZeroScores && d.os == 0) {
                        return d3.rgb(230, 230, 230);
                    } else if (pValueColors && d.p) {
                        if (d.p >= 1 - minPVal) {
                            return d3.interpolateYlGnBu(d.s);
                        } else if (d.p <= minPVal) {
                            return d3.interpolateYlOrBr(d.s);
                        } else {
                            return interpolateLightGreys(d.s);
                        }
                    } else {
                        return color(d.s);
                    }
                })
                .on("mouseover", function (d) {
                    showTooltip(d, d3.event.pageX, d3.event.pageY);
                    d3.select(this).style("stroke", "black");
                })
                .on("click", function (d) {
                    displayTermContexts(gatherTermContexts(d));
                })
                .on("mouseout", function (d) {
                    tooltip.transition()
                        .duration(0)
                        .style("opacity", 0);
                    d3.select(this).style("stroke", null);
                });

            coords = Object();

            function censorPoints(datum) {
                var term = datum.term;
                var curLabel = svg.append("text")
                    .attr("x", x(datum.x))
                    .attr("y", y(datum.y) + 3)
                    .attr("text-anchor", "middle")
                    .text("x");
                var bbox = curLabel.node().getBBox();
                var borderToRemove = .5;
                var x1 = bbox.x + borderToRemove,
                    y1 = bbox.y + borderToRemove,
                    x2 = bbox.x + bbox.width - borderToRemove,
                    y2 = bbox.y + bbox.height - borderToRemove;
                //rangeTree = insertRangeTree(rangeTree, x1, y1, x2, y2, '~~' + term);
                rectHolder.add(new Rectangle(x1, y1, x2, y2));

                curLabel.remove();
            }

            function labelPointsIfPossible(i) {
                var term = data[i].term;

                var configs = [
                    {'anchor': 'end', 'xoff': -5, 'yoff': -3},
                    {'anchor': 'end', 'xoff': -5, 'yoff': 10},
                    {'anchor': 'start', 'xoff': 3, 'yoff': 10},
                    {'anchor': 'start', 'xoff': 3, 'yoff': -3},
                    {'anchor': 'start', 'xoff': 5, 'yoff': 10},
                    {'anchor': 'start', 'xoff': 5, 'yoff': -3},
                    {'anchor': 'start', 'xoff': 10, 'yoff': 15},
                    {'anchor': 'start', 'xoff': -10, 'yoff': -15},
                    {'anchor': 'start', 'xoff': 10, 'yoff': -15},
                    {'anchor': 'start', 'xoff': -10, 'yoff': 15},
                ];
                var matchedElement = null;
                for (var configI in configs) {
                    var config = configs[configI];
                    var curLabel = makeWordInteractive(
                        svg.append("text")
                            .attr("x", x(data[i].x) + config['xoff'])
                            .attr("y", y(data[i].y) + config['yoff'])
                            .attr('class', 'label')
                            .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                            .attr('font-size', '10px')
                            .attr("text-anchor", config['anchor'])
                            .text(term),
                        term
                    );
                    var bbox = curLabel.node().getBBox();
                    var borderToRemove = .5;
                    var x1 = bbox.x + borderToRemove,
                        y1 = bbox.y + borderToRemove,
                        x2 = bbox.x + bbox.width - borderToRemove,
                        y2 = bbox.y + bbox.height - borderToRemove;
                    //matchedElement = searchRangeTree(rangeTree, x1, y1, x2, y2);
                    var matchedElement = false;
                    rectHolder.findMatchingRectangles(x1, y1, x2, y2, function (elem) {
                        matchedElement = true;
                        return false;
                    });
                    if (matchedElement) {
                        curLabel.remove();
                    } else {
                        break;
                    }
                }

                if (!matchedElement || term == 'auto') {
                    coords[term] = [x1, y1, x2, y2];
                    //rangeTree = insertRangeTree(rangeTree, x1, y1, x2, y2, term);
                    rectHolder.add(new Rectangle(x1, y1, x2, y2));
                    return true;

                } else {
                    //curLabel.remove();
                    return false;
                }

            }

            var radius = 2;

            function euclideanDistanceSort(a, b) {
                var aCatDist = a.x * a.x + (1 - a.y) * (1 - a.y);
                var aNotCatDist = a.y * a.y + (1 - a.x) * (1 - a.x);
                var bCatDist = b.x * b.x + (1 - b.y) * (1 - b.y);
                var bNotCatDist = b.y * b.y + (1 - b.x) * (1 - b.x);
                return (Math.min(aCatDist, aNotCatDist) > Math.min(bCatDist, bNotCatDist)) * 2 - 1;
            }

            function euclideanDistanceSortForCategory(a, b) {
                var aCatDist = a.x * a.x + (1 - a.y) * (1 - a.y);
                var bCatDist = b.x * b.x + (1 - b.y) * (1 - b.y);
                return (aCatDist > bCatDist) * 2 - 1;
            }

            function euclideanDistanceSortForNotCategory(a, b) {
                var aNotCatDist = a.y * a.y + (1 - a.x) * (1 - a.x);
                var bNotCatDist = b.y * b.y + (1 - b.x) * (1 - b.x);
                return (aNotCatDist > bNotCatDist) * 2 - 1;
            }

            function scoreSort(a, b) {
                return a.s - b.s;
            }

            function scoreSortReverse(a, b) {
                return b.s - a.s;
            }

            function backgroundScoreSort(a, b) {
                return b.bg - a.bg;
            }

            function arePointsPredictiveOfDifferentCategories(a, b) {
                var aCatDist = a.x * a.x + (1 - a.y) * (1 - a.y);
                var bCatDist = b.x * b.x + (1 - b.y) * (1 - b.y);
                var aNotCatDist = a.y * a.y + (1 - a.x) * (1 - a.x);
                var bNotCatDist = b.y * b.y + (1 - b.x) * (1 - b.x);
                var aGood = aCatDist < aNotCatDist;
                var bGood = bCatDist < bNotCatDist;
                return {aGood: aGood, bGood: bGood};
            }

            function scoreSortForCategory(a, b) {
                var __ret = arePointsPredictiveOfDifferentCategories(a, b);
                var aGood = __ret.aGood;
                var bGood = __ret.bGood;
                if (aGood && !bGood) return -1;
                if (!aGood && bGood) return 1;
                return b.s - a.s;
            }

            function scoreSortForNotCategory(a, b) {
                var __ret = arePointsPredictiveOfDifferentCategories(a, b);
                var aGood = __ret.aGood;
                var bGood = __ret.bGood;
                if (aGood && !bGood) return 1;
                if (!aGood && bGood) return -1;
                if (reverseSortScoresForNotCategory)
                    return a.s - b.s;
                else
                    return b.s - a.s;
            }

            if (sortByDist) {
                data = data.sort(euclideanDistanceSort);
            } else {
                data = data.sort(scoreSort);
            }
            data.forEach(censorPoints);

            var myXAxis = svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            function registerFigureBBox(curLabel) {
                var bbox = curLabel.node().getBBox();
                var borderToRemove = 1.5;
                var x1 = bbox.x + borderToRemove,
                    y1 = bbox.y + borderToRemove,
                    x2 = bbox.x + bbox.width - borderToRemove,
                    y2 = bbox.y + bbox.height - borderToRemove;
                rectHolder.add(new Rectangle(x1, y1, x2, y2));
                //return insertRangeTree(rangeTree, x1, y1, x2, y2, '~~_other_');
            }

            //rangeTree = registerFigureBBox(myXAxis);
            var xLabel = svg.append("text")
                .attr("class", "x label")
                .attr("text-anchor", "end")
                .attr("x", width)
                .attr("y", height - 6)
                .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                .attr('font-size', '10px')
                .text(getLabelText('x'));

            //console.log('xLabel');
            //console.log(xLabel);

            //rangeTree = registerFigureBBox(xLabel);
            // Add the Y Axis
            var myYAxis = svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "30px")
                .attr("dy", "-13px")
                .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                .attr('font-size', '10px')
                .attr("transform", "rotate(-90)");
            registerFigureBBox(myYAxis);

            function getLabelText(axis) {
                if (axis == 'y') {
                    if (yLabelText == null)
                        return modelInfo['category_name'] + " Frequency";
                    else
                        return yLabelText;
                } else {
                    if (xLabelText == null)
                        return modelInfo['not_category_name'] + " Frequency";
                    else
                        return xLabelText;
                }
            }

            var yLabel = svg.append("text")
                .attr("class", "y label")
                .attr("text-anchor", "end")
                .attr("y", 6)
                .attr("dy", ".75em")
                .attr("transform", "rotate(-90)")
                .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                .attr('font-size', '10px')
                .text(getLabelText('y'));
            registerFigureBBox(yLabel);

            var catHeader = svg.append("text")
                .attr("text-anchor", "start")
                .attr("x", width)
                .attr("dy", "6px")
                .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                .attr('font-size', '12px')
                .attr('font-weight', 'bolder')
                .attr('font-decoration', 'underline')
                .text("Top " + fullData['info']['category_name']);
            registerFigureBBox(catHeader);
            console.log(catHeader);

            function showWordList(word, termDataList) {
                var maxWidth = word.node().getBBox().width;
                for (var i in termDataList) {
                    var curTerm = termDataList[i].term;
                    word = (function (word, curTerm) {
                        return makeWordInteractive(
                            svg.append("text")
                                .attr("text-anchor", "start")
                                .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                                .attr('font-size', '12px')
                                .attr("x", word.node().getBBox().x)
                                .attr("y", word.node().getBBox().y
                                    + 2 * word.node().getBBox().height)
                                .text(curTerm)
                            ,
                            curTerm);
                    })(word, curTerm);
                    if (word.node().getBBox().width > maxWidth)
                        maxWidth = word.node().getBBox().width;
                    registerFigureBBox(word);
                }
                return {
                    'word': word,
                    'maxWidth': maxWidth
                };
            }

            function pickEuclideanDistanceSortAlgo(category) {
                if (category == true) return euclideanDistanceSortForCategory;
                return euclideanDistanceSortForNotCategory;
            }

            function pickScoreSortAlgo(category) {
                console.log("PICK SCORE ALGO")
                console.log(category)
                if (category == true) {
                    return scoreSortForCategory;
                } else {
                    return scoreSortForNotCategory;
                }
            }

            function pickTermSortingAlgorithm(category) {
                if (sortByDist) return pickEuclideanDistanceSortAlgo(category);
                return pickScoreSortAlgo(category);
            }

            function showAssociatedWordList(header, isAssociatedToCategory, length=14) {
                var sortedData = null;
                var sortingAlgo = pickTermSortingAlgorithm(isAssociatedToCategory);
                sortedData = data.sort(sortingAlgo);
                if (wordVecMaxPValue) {
                    function signifTest(x) {
                        if (isAssociatedToCategory)
                            return x.p >= 1 - minPVal;
                        return x.p <= minPVal;
                    }

                    sortedData = sortedData.filter(signifTest)
                }
                return showWordList(header, sortedData.slice(0, length));

            }

            var wordListData = showAssociatedWordList(catHeader, true);
            var word = wordListData.word;
            var maxWidth = wordListData.maxWidth;

            catHeader = svg.append("text")
                .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                .attr('font-size', '12px')
                .attr('font-weight', 'bolder')
                .attr('font-decoration', 'underline')
                .attr("text-anchor", "start")
                .attr("x", width)
                .attr("y", word.node().getBBox().y + 4 * word.node().getBBox().height)
                .text("Top " + fullData['info']['not_category_name']);


            wordListData = showAssociatedWordList(catHeader, false);
            word = wordListData.word;
            if (wordListData.maxWidth > maxWidth) {
                maxWidth = wordListData.maxWidth;
            }


            if (!nonTextFeaturesMode && !asianMode && showCharacteristic) {
                var title = 'Characteristic';
                if (wordVecMaxPValue) {
                    title = 'Most similar';
                }
                word = svg.append("text")
                    .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                    .attr("text-anchor", "start")
                    .attr('font-size', '12px')
                    .attr('font-weight', 'bolder')
                    .attr('font-decoration', 'underline')
                    .attr("x", catHeader.node().getBBox().x + maxWidth + 10)
                    .attr("dy", "6px")
                    .text(title);
                var sortMethod = backgroundScoreSort;
                if (wordVecMaxPValue) {
                    sortMethod = scoreSortReverse;
                }
                var wordListData = showWordList(word, data.sort(sortMethod).slice(0, 30));
                ;

                word = wordListData.word;
                maxWidth = wordListData.maxWidth;
                console.log(maxWidth);
                console.log(word.node().getBBox().x + maxWidth);

                svg.attr('width', word.node().getBBox().x + 3 * maxWidth + 10);
            }

            var numPointsLabeled = 0;
            for (var i = 0; i < data.length; i++) {
                if (labelPointsIfPossible(i)) numPointsLabeled++;
            }
            console.log('numPointsLabeled');
            console.log(numPointsLabeled);


            function populateCorpusStats() {
                var wordCounts = {};
                var docCounts = {}
                fullData.docs.labels.forEach(function (x, i) {
                    var cnt = (
                        fullData.docs.texts[i]
                            .trim()
                            .replace(/['";:,.?¿\-!¡]+/g, '')
                            .match(/\S+/g) || []
                    ).length;
                    wordCounts[x] = wordCounts[x] ? wordCounts[x] + cnt : cnt
                });
                fullData.docs.labels.forEach(function (x) {
                    docCounts[x] = docCounts[x] ? docCounts[x] + 1 : 1
                });
                var messages = [];
                fullData.docs.categories.forEach(function (x, i) {
                    var name = fullData.info.not_category_name;
                    if (x == fullData.info.category_internal_name) {
                        name = fullData.info.category_name;
                    }

                    messages.push('<b>' + name + '</b> document count: '
                        + Number(docCounts[i]).toLocaleString('en')
                        + '; word count: '
                        + Number(wordCounts[i]).toLocaleString('en'));
                });

                d3.select('#corpus-stats')
                    .style('width', width + margin.left + margin.right + 200)
                    .append('div')
                    .html(messages.join('<br />'));
            };

            if (fullData.docs) {
                populateCorpusStats();
            }

            if (saveSvgButton) {
                // from http://stackoverflow.com/questions/23218174/how-do-i-save-export-an-svg-file-after-creating-an-svg-with-d3-js-ie-safari-an
                var svgElement = document.getElementById("d3-div-1");

                var serializer = new XMLSerializer();
                var source = serializer.serializeToString(svgElement);

                if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
                    source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
                }
                if (!source.match(/^<svg[^>]+"http\:\/\/www\.w3\.org\/1999\/xlink"/)) {
                    source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
                }

                source = '<?xml version="1.0" standalone="no"?>\r\n' + source;

                var url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);

                var downloadLink = document.createElement("a");
                downloadLink.href = url;
                downloadLink.download = fullData['info']['category_name'] + ".svg";
                downloadLink.innerText = 'Download SVG';
                document.body.appendChild(downloadLink);

            }

        };

        fullData = getDataAndInfo();
        processData(fullData);

        // The tool tip is down here in order to make sure it has the highest z-index
        var tooltip = d3.select('#' + divName)
            .append("div")
            .attr("class", sortByDist ? "tooltip" : "tooltipscore")
            .style("opacity", 0);
    };
}(d3);
