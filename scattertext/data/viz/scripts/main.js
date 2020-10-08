buildViz = function (d3) {
    return function (widthInPixels = 1000,
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
                     minPVal = 0.1,
                     pValueColors = false,
                     xLabelText = null,
                     yLabelText = null,
                     fullData = null,
                     showTopTerms = true,
                     showNeutral = false,
                     getTooltipContent = null,
                     xAxisValues = null,
                     yAxisValues = null,
                     colorFunc = null,
                     showAxes = true,
                     showExtra = false,
                     doCensorPoints = true,
                     centerLabelsOverPoints = false,
                     xAxisLabels = null,
                     yAxisLabels = null,
                     topic_model_preview_size = 10,
                     verticalLines = null,
                     horizontal_line_y_position = null,
                     vertical_line_x_position = null,
                     unifiedContexts = false,
                     showCategoryHeadings = true,
                     showCrossAxes = true,
                     divName = 'd3-div-1',
                     alternativeTermFunc = null,
                     includeAllContexts = false,
                     showAxesAndCrossHairs = false,
                     x_axis_values_format = '.3f',
                     y_axis_values_format = '.3f',
                     matchFullLine = false,
                     maxOverlapping = -1,
                     showCorpusStats = true,
                     sortDocLabelsByName = false,
                     alwaysJump = true,
                     highlightSelectedCategory = false) {
        //var divName = 'd3-div-1';
        // Set the dimensions of the canvas / graph
        var padding = {top: 30, right: 20, bottom: 30, left: 50};
        if (!showAxes) {
            padding = {top: 30, right: 20, bottom: 30, left: 50};
        }
        var margin = padding,
            width = widthInPixels - margin.left - margin.right,
            height = heightInPixels - margin.top - margin.bottom;
        fullData.data.forEach(function (x, i) {
            x.i = i
        });

        // Set the ranges
        var x = d3.scaleLinear().range([0, width]);
        var y = d3.scaleLinear().range([height, 0]);

        if (unifiedContexts) {
            document.querySelectorAll('#' + divName + '-' + 'notcol')
                .forEach(function (x) {
                    x.style.display = 'none'
                });
            document.querySelectorAll('.' + divName + '-' + 'contexts')
                .forEach(function (x) {
                    x.style.width = '90%'
                });
        } else if (showNeutral) {
            if (showExtra) {
                document.querySelectorAll('.' + divName + '-' + 'contexts')
                    .forEach(function (x) {
                        x.style.width = '25%'
                        x.style.float = 'left'
                    });

                ['notcol', 'neutcol', 'extracol'].forEach(function (columnName) {
                    document.querySelectorAll('#' + divName + '-' + columnName)
                        .forEach(function (x) {
                            x.style.display = 'inline'
                            x.style.float = 'left'
                            x.style.width = '25%'
                        });
                })

            } else {
                document.querySelectorAll('.' + divName + '-' + 'contexts')
                    .forEach(function (x) {
                        x.style.width = '33%'
                        x.style.float = 'left'
                    });

                ['notcol', 'neutcol'].forEach(function (columnName) {
                    document.querySelectorAll('#' + divName + '-' + columnName)
                        .forEach(function (x) {
                            x.style.display = 'inline'
                            x.style.float = 'left'
                            x.style.width = '33%'
                        });
                })


            }
        } else {
            document.querySelectorAll('.' + divName + '-' + 'contexts')
                .forEach(function (x) {
                    x.style.width = '45%'
                    //x.style.display = 'inline'
                    x.style.float = 'left'
                });

            ['notcol'].forEach(function (columnName) {
                document.querySelectorAll('#' + divName + '-' + columnName)
                    .forEach(function (x) {
                        //x.style.display = 'inline'
                        x.style.float = 'left'
                        x.style.width = '45%'
                    });
            })
        }

        var yAxis = null;
        var xAxis = null;

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


        function bs(ar, x) {
            function bsa(s, e) {
                var mid = Math.floor((s + e) / 2);
                var midval = ar[mid];
                if (s == e) {
                    return s;
                }
                if (midval == x) {
                    return mid;
                } else if (midval < x) {
                    return bsa(mid + 1, e);
                } else {
                    return bsa(s, mid);
                }
            }

            return bsa(0, ar.length);
        }


        console.log("fullData");
        console.log(fullData);


        var sortedX = fullData.data.map(x => x).sort(function (a, b) {
            return a.x < b.x ? -1 : (a.x == b.x ? 0 : 1);
        }).map(function (x) {
            return x.x
        });

        var sortedOx = fullData.data.map(x => x).sort(function (a, b) {
            return a.ox < b.ox ? -1 : (a.ox == b.ox ? 0 : 1);
        }).map(function (x) {
            return x.ox
        });

        var sortedY = fullData.data.map(x => x).sort(function (a, b) {
            return a.y < b.y ? -1 : (a.y == b.y ? 0 : 1);
        }).map(function (x) {
            return x.y
        });

        var sortedOy = fullData.data.map(x => x).sort(function (a, b) {
            return a.oy < b.oy ? -1 : (a.oy == b.oy ? 0 : 1);
        }).map(function (x) {
            return x.oy
        });
        console.log(fullData.data[0])

        function labelWithZScore(axis, axisName, tickPoints, axis_values_format) {
            var myVals = axisName === 'x' ? sortedOx : sortedOy;
            var myPlotedVals = axisName === 'x' ? sortedX : sortedY;
            var ticks = tickPoints.map(function (x) {
                return myPlotedVals[bs(myVals, x)]
            });
            return axis.tickValues(ticks).tickFormat(
                function (d, i) {
                    return d3.format(axis_values_format)(tickPoints[i]);
                })
        }

        if (xAxisValues) {
            xAxis = labelWithZScore(d3.axisBottom(x), 'x', xAxisValues, x_axis_values_format);
        } else if (xAxisLabels) {
            xAxis = d3.axisBottom(x)
                .ticks(xAxisLabels.length)
                .tickFormat(function (d, i) {
                    return xAxisLabels[i];
                });
        } else {
            xAxis = d3.axisBottom(x).ticks(3).tickFormat(axisLabelerFactory('x'));
        }
        if (yAxisValues) {
            yAxis = labelWithZScore(d3.axisLeft(y), 'y', yAxisValues, y_axis_values_format);
        } else if (yAxisLabels) {
            yAxis = d3.axisLeft(y)
                .ticks(yAxisLabels.length)
                .tickFormat(function (d, i) {
                    return yAxisLabels[i];
                });
        } else {
            yAxis = d3.axisLeft(y).ticks(3).tickFormat(axisLabelerFactory('y'));
        }

        // var label = d3.select("body").append("div")
        var label = d3.select('#' + divName).append("div")
            .attr("class", "label");


        var interpolateLightGreys = d3.interpolate(d3.rgb(230, 230, 230),
            d3.rgb(130, 130, 130));
        // setup fill color
        if (color == null) {
            color = d3.interpolateRdYlBu;
            //color = d3.interpolateWarm;
        }

        var pixelsToAddToWidth = 200;
        if (!showTopTerms && !showCharacteristic) {
            pixelsToAddToWidth = 0;
        }

        // Adds the svg canvas
        // var svg = d3.select("body")
        svg = d3.select('#' + divName)
            .append("svg")
            .attr("width", width + margin.left + margin.right + pixelsToAddToWidth)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");


        origSVGLeft = svg.node().getBoundingClientRect().left;
        origSVGTop = svg.node().getBoundingClientRect().top;
        var lastCircleSelected = null;

        function getCorpusWordCounts() {
            var binaryLabels = fullData.docs.labels.map(function (label) {
                return 1 * (fullData.docs.categories[label] != fullData.info.category_internal_name);
            });
            var wordCounts = {}; // word -> [cat counts, not-cat-counts]
            var wordCountSums = [0, 0];
            fullData.docs.texts.forEach(function (text, i) {
                text.toLowerCase().trim().split(/\W+/).forEach(function (word) {
                    if (word.trim() !== '') {
                        if (!(word in wordCounts))
                            wordCounts[word] = [0, 0];
                        wordCounts[word][binaryLabels[i]]++;
                        wordCountSums[binaryLabels[i]]++;
                    }
                })
            });
            return {
                avgDocLen: (wordCountSums[0] + wordCountSums[1]) / fullData.docs.texts.length,
                counts: wordCounts,
                sums: wordCountSums,
                uniques: [[0, 0]].concat(Object.keys(wordCounts).map(function (key) {
                    return wordCounts[key];
                })).reduce(function (a, b) {
                    return [a[0] + (b[0] > 0), a[1] + (b[1] > 0)]
                })
            };
        }

        function getContextWordCounts(query) {
            var wordCounts = {};
            var wordCountSums = [0, 0];
            var priorCountSums = [0, 0];
            gatherTermContexts(termDict[query])
                .contexts
                .forEach(function (contextSet, categoryIdx) {
                    contextSet.forEach(function (context) {
                        context.snippets.forEach(function (snippet) {
                            var tokens = snippet.toLowerCase().trim().replace('<b>', '').replace('</b>', '').split(/\W+/);
                            var matchIndices = [];
                            tokens.forEach(function (word, i) {
                                if (word === query) matchIndices.push(i)
                            });
                            tokens.forEach(function (word, i) {
                                if (word.trim() !== '') {
                                    var isValid = false;
                                    for (var matchI in matchIndices) {
                                        if (Math.abs(i - matchI) < 3) {
                                            isValid = true;
                                            break
                                        }
                                    }
                                    if (isValid) {
                                        //console.log([word, i, matchI, isValid]);
                                        if (!(word in wordCounts)) {
                                            var priorCounts = corpusWordCounts.counts[word]
                                            wordCounts[word] = [0, 0].concat(priorCounts);
                                            priorCountSums[0] += priorCounts[0];
                                            priorCountSums[1] += priorCounts[1];
                                        }
                                        wordCounts[word][categoryIdx]++;
                                        wordCountSums[categoryIdx]++;
                                    }
                                }
                            })
                        })
                    })
                });
            return {
                counts: wordCounts,
                priorSums: priorCountSums,
                sums: wordCountSums,
                uniques: [[0, 0]].concat(Object.keys(wordCounts).map(function (key) {
                    return wordCounts[key];
                })).reduce(function (a, b) {
                    return [a[0] + (b[0] > 0), a[1] + (b[1] > 0)];
                })
            }

        }

        function denseRank(ar) {
            var markedAr = ar.map((x, i) => [x, i]).sort((a, b) => a[0] - b[0]);
            var curRank = 1
            var rankedAr = markedAr.map(
                function (x, i) {
                    if (i > 0 && x[0] != markedAr[i - 1][0]) {
                        curRank++;
                    }
                    return [curRank, x[0], x[1]];
                }
            )
            return rankedAr.map(x => x).sort((a, b) => (a[2] - b[2])).map(x => x[0]);
        }


        function getDenseRanks(fullData, categoryNum) {
            var fgFreqs = Array(fullData.data.length).fill(0);
            var bgFreqs = Array(fullData.data.length).fill(0);
            var categoryTermCounts = fullData.termCounts[categoryNum];


            Object.keys(categoryTermCounts).forEach(
                key => fgFreqs[key] = categoryTermCounts[key][0]
            )
            fullData.termCounts.forEach(
                function (categoryTermCounts, otherCategoryNum) {
                    if (otherCategoryNum != categoryNum) {
                        Object.keys(categoryTermCounts).forEach(
                            key => bgFreqs[key] += categoryTermCounts[key][0]
                        )
                    }
                }
            )
            var fgDenseRanks = denseRank(fgFreqs);
            var bgDenseRanks = denseRank(bgFreqs);

            var maxfgDenseRanks = Math.max(...fgDenseRanks);
            var minfgDenseRanks = Math.min(...fgDenseRanks);
            var scalefgDenseRanks = fgDenseRanks.map(
                x => (x - minfgDenseRanks) / (maxfgDenseRanks - minfgDenseRanks)
            )

            var maxbgDenseRanks = Math.max(...bgDenseRanks);
            var minbgDenseRanks = Math.min(...bgDenseRanks);
            var scalebgDenseRanks = bgDenseRanks.map(
                x => (x - minbgDenseRanks) / (maxbgDenseRanks - minbgDenseRanks)
            )

            return {'fg': scalefgDenseRanks, 'bg': scalebgDenseRanks, 'bgFreqs': bgFreqs, 'fgFreqs': fgFreqs}
        }

        function getCategoryDenseRankScores(fullData, categoryNum) {
            var denseRanks = getDenseRanks(fullData, categoryNum)
            return denseRanks.fg.map((x, i) => x - denseRanks.bg[i]);
        }

        function getTermCounts(fullData) {
            var counts = Array(fullData.data.length).fill(0);
            fullData.termCounts.forEach(
                function (categoryTermCounts) {
                    Object.keys(categoryTermCounts).forEach(
                        key => counts[key] = categoryTermCounts[key][0]
                    )
                }
            )
            return counts;
        }

        function getContextWordLORIPs(query) {
            var contextWordCounts = getContextWordCounts(query);
            var ni_k = contextWordCounts.sums[0];
            var nj_k = contextWordCounts.sums[1];
            var n = ni_k + nj_k;
            //var ai_k0 = contextWordCounts.priorSums[0] + contextWordCounts.priorSums[1];
            //var aj_k0 = contextWordCounts.priorSums[0] + contextWordCounts.priorSums[1];
            var a0 = 0.00001 //corpusWordCounts.avgDocLen;
            var a_k0 = Object.keys(contextWordCounts.counts)
                .map(function (x) {
                    var counts = contextWordCounts.counts[x];
                    return a0 * (counts[2] + counts[3]) /
                        (contextWordCounts.priorSums[0] + contextWordCounts.priorSums[1]);
                })
                .reduce(function (a, b) {
                    return a + b
                });
            var ai_k0 = a_k0 / ni_k;
            var aj_k0 = a_k0 / nj_k;
            var scores = Object.keys(contextWordCounts.counts).map(
                function (word) {
                    var countData = contextWordCounts.counts[word];
                    var yi = countData[0];
                    var yj = countData[1];
                    //var ai = countData[2];
                    //var aj = countData[3];
                    //var ai = countData[2] + countData[3];
                    //var aj = ai;
                    //var ai = (countData[2] + countData[3]) * a0/ni_k;
                    //var aj = (countData[2] + countData[3]) * a0/nj_k;
                    var ai = a0 * (countData[2] + countData[3]) /
                        (contextWordCounts.priorSums[0] + contextWordCounts.priorSums[1]);
                    var aj = ai;
                    var deltahat_i_j =
                        +Math.log((yi + ai) * 1. / (ni_k + ai_k0 - yi - ai))
                        - Math.log((yj + aj) * 1. / (nj_k + aj_k0 - yj - aj));
                    var var_deltahat_i_j = 1. / (yi + ai) + 1. / (ni_k + ai_k0 - yi - ai)
                        + 1. / (yj + aj) + 1. / (nj_k + aj_k0 - yj - aj);
                    var zeta_ij = deltahat_i_j / Math.sqrt(var_deltahat_i_j);
                    return [word, yi, yj, ai, aj, ai_k0, zeta_ij];
                }
            ).sort(function (a, b) {
                return b[5] - a[5];
            });
            return scores;
        }

        function getContextWordSFS(query) {
            // from https://stackoverflow.com/questions/14846767/std-normal-cdf-normal-cdf-or-error-function
            function cdf(x, mean, variance) {
                return 0.5 * (1 + erf((x - mean) / (Math.sqrt(2 * variance))));
            }

            function erf(x) {
                // save the sign of x
                var sign = (x >= 0) ? 1 : -1;
                x = Math.abs(x);

                // constants
                var a1 = 0.254829592;
                var a2 = -0.284496736;
                var a3 = 1.421413741;
                var a4 = -1.453152027;
                var a5 = 1.061405429;
                var p = 0.3275911;

                // A&S formula 7.1.26
                var t = 1.0 / (1.0 + p * x);
                var y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
                return sign * y; // erf(-x) = -erf(x);
            }

            function scale(a) {
                return Math.log(a + 0.0000001);
            }

            var contextWordCounts = getContextWordCounts(query);
            var wordList = Object.keys(contextWordCounts.counts).map(function (word) {
                return contextWordCounts.counts[word].concat([word]);
            });
            var cat_freq_xbar = wordList.map(function (x) {
                return scale(x[0])
            }).reduce(function (a, b) {
                return a + b
            }) / wordList.length;
            var cat_freq_var = wordList.map(function (x) {
                return Math.pow((scale(x[0]) - cat_freq_xbar), 2);
            }).reduce(function (a, b) {
                return a + b
            }) / wordList.length;
            var cat_prec_xbar = wordList.map(function (x) {
                return scale(x[0] / (x[0] + x[1]));
            }).reduce(function (a, b) {
                return a + b
            }) / wordList.length;
            var cat_prec_var = wordList.map(function (x) {
                return Math.pow((scale(x[0] / (x[0] + x[1])) - cat_prec_xbar), 2);
            }).reduce(function (a, b) {
                return a + b
            }) / wordList.length;

            var ncat_freq_xbar = wordList.map(function (x) {
                return scale(x[0])
            }).reduce(function (a, b) {
                return a + b
            }) / wordList.length;
            var ncat_freq_var = wordList.map(function (x) {
                return Math.pow((scale(x[0]) - ncat_freq_xbar), 2);
            }).reduce(function (a, b) {
                return a + b
            }) / wordList.length;
            var ncat_prec_xbar = wordList.map(function (x) {
                return scale(x[0] / (x[0] + x[1]));
            }).reduce(function (a, b) {
                return a + b
            }) / wordList.length;
            var ncat_prec_var = wordList.map(function (x) {
                return Math.pow((scale(x[0] / (x[0] + x[1])) - ncat_prec_xbar), 2);
            }).reduce(function (a, b) {
                return a + b
            }) / wordList.length;

            function scaledFScore(cnt, other, freq_xbar, freq_var, prec_xbar, prec_var) {
                var beta = 1.5;
                var normFreq = cdf(scale(cnt), freq_xbar, freq_var);
                var normPrec = cdf(scale(cnt / (cnt + other)), prec_xbar, prec_var);
                return (1 + Math.pow(beta, 2)) * normFreq * normPrec / (Math.pow(beta, 2) * normFreq + normPrec);
            }

            var sfs = wordList.map(function (x) {
                cat_sfs = scaledFScore(x[0], x[1], cat_freq_xbar,
                    cat_freq_var, cat_prec_xbar, cat_prec_var);
                ncat_sfs = scaledFScore(x[1], x[0], ncat_freq_xbar,
                    ncat_freq_var, ncat_prec_xbar, ncat_prec_var);
                return [cat_sfs > ncat_sfs ? cat_sfs : -ncat_sfs].concat(x);

            }).sort(function (a, b) {
                return b[0] - a[0];
            });
            return sfs;
        }

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

        function gatherTermContexts(d, includeAll = true) {
            var category_name = fullData['info']['category_name'];
            var not_category_name = fullData['info']['not_category_name'];
            var matches = [[], [], [], []];
            console.log("searching")

            if (fullData.docs === undefined) return matches;
            if (!nonTextFeaturesMode) {
                return searchInText(d, includeAll);
            } else {
                return searchInExtraFeatures(d, includeAll);
            }
        }

        function searchInExtraFeatures(d) {
            var matches = [[], [], [], []];
            var term = d.term;
            var categoryNum = fullData.docs.categories.indexOf(fullData.info.category_internal_name);
            var notCategoryNumList = fullData.docs.categories.map(function (x, i) {
                if (fullData.info.not_category_internal_names.indexOf(x) > -1) {
                    return i;
                } else {
                    return -1;
                }
            }).filter(function (x) {
                return x > -1
            });
            var neutralCategoryNumList = fullData.docs.categories.map(function (x, i) {
                if (fullData.info.neutral_category_internal_names.indexOf(x) > -1) {
                    return i;
                } else {
                    return -1;
                }
            }).filter(function (x) {
                return x > -1
            });
            var extraCategoryNumList = fullData.docs.categories.map(function (x, i) {
                if (fullData.info.extra_category_internal_names.indexOf(x) > -1) {
                    return i;
                } else {
                    return -1;
                }
            }).filter(function (x) {
                return x > -1
            });

            var pattern = null;
            if ('metalists' in fullData && term in fullData.metalists) {
                // from https://stackoverflow.com/questions/3446170/escape-string-for-use-in-javascript-regex
                function escapeRegExp(str) {
                    return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|\']/g, "\\$&");
                }

                console.log('term');
                console.log(term);
                pattern = new RegExp(
                    '\\W(' + fullData.metalists[term].map(escapeRegExp).join('|') + ')\\W',
                    'gim'
                );
            }

            for (var i in fullData.docs.extra) {
                if (term in fullData.docs.extra[i]) {
                    var strength = fullData.docs.extra[i][term] /
                        Object.values(fullData.docs.extra[i]).reduce(
                            function (a, b) {
                                return a + b
                            });

                    var docLabel = fullData.docs.labels[i];
                    var numericLabel = -1;
                    if (docLabel == categoryNum) {
                        numericLabel = 0;
                    } else if (notCategoryNumList.indexOf(docLabel) > -1) {
                        numericLabel = 1;
                    } else if (neutralCategoryNumList.indexOf(docLabel) > -1) {
                        numericLabel = 2;
                    } else if (extraCategoryNumList.indexOf(docLabel) > -1) {
                        numericLabel = 3;
                    }
                    if (numericLabel == -1) {
                        continue;
                    }
                    var text = fullData.docs.texts[i];
                    if (!useFullDoc)
                        text = text.slice(0, 300);
                    if (pattern !== null) {
                        text = text.replace(pattern, '<b>$&</b>');
                    }
                    var curMatch = {
                        'id': i,
                        'snippets': [text],
                        'strength': strength,
                        'docLabel': docLabel,
                        'meta': fullData.docs.meta ? fullData.docs.meta[i] : ""
                    }

                    matches[numericLabel].push(curMatch);
                }
            }
            for (var i in [0, 1]) {
                matches[i] = matches[i].sort(function (a, b) {
                    return a.strength < b.strength ? 1 : -1
                })
            }
            return {'contexts': matches, 'info': d};
        }

        // from https://mathiasbynens.be/notes/es-unicode-property-escapes#emoji
        var emojiRE = (/(?:[\u261D\u26F9\u270A-\u270D]|\uD83C[\uDF85\uDFC2-\uDFC4\uDFC7\uDFCA-\uDFCC]|\uD83D[\uDC42\uDC43\uDC46-\uDC50\uDC66-\uDC69\uDC6E\uDC70-\uDC78\uDC7C\uDC81-\uDC83\uDC85-\uDC87\uDCAA\uDD74\uDD75\uDD7A\uDD90\uDD95\uDD96\uDE45-\uDE47\uDE4B-\uDE4F\uDEA3\uDEB4-\uDEB6\uDEC0\uDECC]|\uD83E[\uDD18-\uDD1C\uDD1E\uDD1F\uDD26\uDD30-\uDD39\uDD3D\uDD3E\uDDD1-\uDDDD])(?:\uD83C[\uDFFB-\uDFFF])?|(?:[\u231A\u231B\u23E9-\u23EC\u23F0\u23F3\u25FD\u25FE\u2614\u2615\u2648-\u2653\u267F\u2693\u26A1\u26AA\u26AB\u26BD\u26BE\u26C4\u26C5\u26CE\u26D4\u26EA\u26F2\u26F3\u26F5\u26FA\u26FD\u2705\u270A\u270B\u2728\u274C\u274E\u2753-\u2755\u2757\u2795-\u2797\u27B0\u27BF\u2B1B\u2B1C\u2B50\u2B55]|\uD83C[\uDC04\uDCCF\uDD8E\uDD91-\uDD9A\uDDE6-\uDDFF\uDE01\uDE1A\uDE2F\uDE32-\uDE36\uDE38-\uDE3A\uDE50\uDE51\uDF00-\uDF20\uDF2D-\uDF35\uDF37-\uDF7C\uDF7E-\uDF93\uDFA0-\uDFCA\uDFCF-\uDFD3\uDFE0-\uDFF0\uDFF4\uDFF8-\uDFFF]|\uD83D[\uDC00-\uDC3E\uDC40\uDC42-\uDCFC\uDCFF-\uDD3D\uDD4B-\uDD4E\uDD50-\uDD67\uDD7A\uDD95\uDD96\uDDA4\uDDFB-\uDE4F\uDE80-\uDEC5\uDECC\uDED0-\uDED2\uDEEB\uDEEC\uDEF4-\uDEF8]|\uD83E[\uDD10-\uDD3A\uDD3C-\uDD3E\uDD40-\uDD45\uDD47-\uDD4C\uDD50-\uDD6B\uDD80-\uDD97\uDDC0\uDDD0-\uDDE6])|(?:[#\*0-9\xA9\xAE\u203C\u2049\u2122\u2139\u2194-\u2199\u21A9\u21AA\u231A\u231B\u2328\u23CF\u23E9-\u23F3\u23F8-\u23FA\u24C2\u25AA\u25AB\u25B6\u25C0\u25FB-\u25FE\u2600-\u2604\u260E\u2611\u2614\u2615\u2618\u261D\u2620\u2622\u2623\u2626\u262A\u262E\u262F\u2638-\u263A\u2640\u2642\u2648-\u2653\u2660\u2663\u2665\u2666\u2668\u267B\u267F\u2692-\u2697\u2699\u269B\u269C\u26A0\u26A1\u26AA\u26AB\u26B0\u26B1\u26BD\u26BE\u26C4\u26C5\u26C8\u26CE\u26CF\u26D1\u26D3\u26D4\u26E9\u26EA\u26F0-\u26F5\u26F7-\u26FA\u26FD\u2702\u2705\u2708-\u270D\u270F\u2712\u2714\u2716\u271D\u2721\u2728\u2733\u2734\u2744\u2747\u274C\u274E\u2753-\u2755\u2757\u2763\u2764\u2795-\u2797\u27A1\u27B0\u27BF\u2934\u2935\u2B05-\u2B07\u2B1B\u2B1C\u2B50\u2B55\u3030\u303D\u3297\u3299]|\uD83C[\uDC04\uDCCF\uDD70\uDD71\uDD7E\uDD7F\uDD8E\uDD91-\uDD9A\uDDE6-\uDDFF\uDE01\uDE02\uDE1A\uDE2F\uDE32-\uDE3A\uDE50\uDE51\uDF00-\uDF21\uDF24-\uDF93\uDF96\uDF97\uDF99-\uDF9B\uDF9E-\uDFF0\uDFF3-\uDFF5\uDFF7-\uDFFF]|\uD83D[\uDC00-\uDCFD\uDCFF-\uDD3D\uDD49-\uDD4E\uDD50-\uDD67\uDD6F\uDD70\uDD73-\uDD7A\uDD87\uDD8A-\uDD8D\uDD90\uDD95\uDD96\uDDA4\uDDA5\uDDA8\uDDB1\uDDB2\uDDBC\uDDC2-\uDDC4\uDDD1-\uDDD3\uDDDC-\uDDDE\uDDE1\uDDE3\uDDE8\uDDEF\uDDF3\uDDFA-\uDE4F\uDE80-\uDEC5\uDECB-\uDED2\uDEE0-\uDEE5\uDEE9\uDEEB\uDEEC\uDEF0\uDEF3-\uDEF8]|\uD83E[\uDD10-\uDD3A\uDD3C-\uDD3E\uDD40-\uDD45\uDD47-\uDD4C\uDD50-\uDD6B\uDD80-\uDD97\uDDC0\uDDD0-\uDDE6])\uFE0F/g);

        function isEmoji(str) {
            if (str.match(emojiRE)) return true;
            return false;
        }

        function displayObscuredTerms(obscuredTerms, data, term, termInfo, div = '#' + divName + '-' + 'overlapped-terms') {
            d3.select('#' + divName + '-' + 'overlapped-terms')
                .selectAll('div')
                .remove();
            d3.select(div)
                .selectAll('div')
                .remove();
            if (obscuredTerms.length > 1 && maxOverlapping !== 0) {
                var obscuredDiv = d3.select(div)
                    .append('div')
                    .attr("class", "obscured")
                    .style('align', 'center')
                    .style('text-align', 'center')
                    .html("<b>\"" + term + "\" obstructs</b>: ");
                obscuredTerms.map(
                    function (term, i) {
                        if (maxOverlapping === -1 || i < maxOverlapping) {
                            makeWordInteractive(
                                data,
                                svg,
                                obscuredDiv.append("text").text(term),
                                term,
                                data.filter(t => t.term === term)[0],//termInfo
                                false
                            );
                            if (i < obscuredTerms.length - 1
                                && (maxOverlapping === -1 || i < maxOverlapping - 1)) {
                                obscuredDiv.append("text").text(", ");
                            }
                        } else if (i === maxOverlapping && i !== obscuredTerms.length - 1) {
                            obscuredDiv.append("text").text("...");
                        }
                    }
                )
            }
        }

        function displayTermContexts(data, termInfo, jump = alwaysJump, includeAll = false) {
            var contexts = termInfo.contexts;
            var info = termInfo.info;
            var notmatches = termInfo.notmatches;
            if (contexts[0].length + contexts[1].length + contexts[2].length + contexts[3].length == 0) {
                //return null;
            }
            //!!! Future feature: context words
            //var contextWords = getContextWordSFS(info.term);
            //var contextWords = getContextWordLORIPs(info.term);
            //var categoryNames = [fullData.info.category_name,
            //    fullData.info.not_category_name];
            var catInternalName = fullData.info.category_internal_name;


            function addSnippets(contexts, divId, isMatch = true) {
                var meta = contexts.meta ? contexts.meta : '&nbsp;';
                var headClass = 'snippet_meta docLabel' + contexts.docLabel;
                var snippetClass = 'snippet docLabel' + contexts.docLabel;
                if (!isMatch) {
                    headClass = 'snippet_meta not_match docLabel' + contexts.docLabel;
                    snippetClass = 'snippet not_match docLabel' + contexts.docLabel;
                }
                d3.select(divId)
                    .append("div")
                    .attr('class', headClass)
                    .html(meta);
                contexts.snippets.forEach(function (snippet) {
                    d3.select(divId)
                        .append("div")
                        .attr('class', snippetClass)
                        .html(snippet);
                })
            }

            if (unifiedContexts) {
                divId = '#' + divName + '-' + 'cat';
                var docLabelCounts = fullData.docs.labels.reduce(
                    function (map, label) {
                        map[label] = (map[label] || 0) + 1;
                        return map;
                    },
                    Object.create(null)
                );
                var numMatches = Object.create(null);
                var temp = d3.select(divId).selectAll("div").remove();
                var allContexts = contexts[0].concat(contexts[1]).concat(contexts[2]).concat(contexts[3]);
                allContexts.forEach(function (singleDoc) {
                    numMatches[singleDoc.docLabel] = (numMatches[singleDoc.docLabel] || 0) + 1;
                });
                var allNotMatches = notmatches[0].concat(notmatches[1]).concat(notmatches[2]).concat(notmatches[3]);

                /*contexts.forEach(function(context) {
                     context.forEach(function (singleDoc) {
                         numMatches[singleDoc.docLabel] = (numMatches[singleDoc.docLabel]||0) + 1;
                         addSnippets(singleDoc, divId);
                     });
                 });*/
                console.log("ORDERING !!!!!"); console.log(fullData.info.category_name); console.log(sortDocLabelsByName);
                var docLabelCountsSorted = Object.keys(docLabelCounts).map(key => (
                    {
                        "label": fullData.docs.categories[key],
                        "labelNum": key,
                        "matches": numMatches[key] || 0,
                        "overall": docLabelCounts[key],
                        'percent': (numMatches[key] || 0) * 100. / docLabelCounts[key]
                    }))
                    .sort(function (a, b) {
                        if(highlightSelectedCategory) {
                            if (a['label'] === fullData.info.category_name) {
                                return -1;
                            }
                            if (b['label'] === fullData.info.category_name) {
                                return 1;
                            }
                        }
                        if (sortDocLabelsByName) {
                            return a['label'] < b['label'] ? 1 : a['label'] > b['label'] ? -1 : 0;
                        } else {
                            return b.percent - a.percent;
                        }
                    });
                console.log("docLabelCountsSorted")
                console.log(docLabelCountsSorted);
                console.log(numMatches)
                console.log('#' + divName + '-' + 'categoryinfo')
                d3.select('#' + divName + '-' + 'categoryinfo').selectAll("div").remove();
                if (showCategoryHeadings) {
                    d3.select('#' + divName + '-' + 'categoryinfo').attr('display', 'inline');
                }

                function getCategoryStatsHTML(counts) {
                    return counts.matches + " document"
                        + (counts.matches == 1 ? "" : "s") + " out of " + counts.overall + ': '
                        + counts['percent'].toFixed(2) + '%';
                }

                function getCategoryInlineHeadingHTML(counts) {
                    return '<a name="' + divName + '-category'
                        + counts.labelNum + '"></a>'
                        + counts.label + ": <span class=topic_preview>"
                        + getCategoryStatsHTML(counts)
                        + "</span>";
                }


                docLabelCountsSorted.forEach(function (counts) {
                    var htmlToAdd = "<b>" + counts.label + "</b>: " + getCategoryStatsHTML(counts);

                    if (counts.matches > 0) {
                        var headerClassName = 'text_header';
                        if((counts.label === fullData.info.category_name) && highlightSelectedCategory) {
                            d3.select(divId)
                                .append('div')
                                .attr('class', 'separator')
                                .html("<b>Selected category</b>");
                        }
                        d3.select(divId)
                            .append("div")
                            .attr('class', headerClassName)
                            .html(getCategoryInlineHeadingHTML(counts));

                        allContexts
                            .filter(singleDoc => singleDoc.docLabel == counts.labelNum)
                            .forEach(function (singleDoc) {
                                addSnippets(singleDoc, divId);
                            });
                        if (includeAll) {
                            allNotMatches
                                .filter(singleDoc => singleDoc.docLabel == counts.labelNum)
                                .forEach(function (singleDoc) {
                                    addSnippets(singleDoc, divId, false);
                                });
                        }
                        if((counts.label === fullData.info.category_name) && highlightSelectedCategory) {
                            d3.select(divId).append('div').attr('class', 'separator').html("<b>End selected category</b>");
                            d3.select(divId).append('div').html("<br />");
                        }
                    }


                    if (showCategoryHeadings) {
                        d3.select('#' + divName + '-' + 'categoryinfo')
                            .attr('display', 'inline')
                            .append('div')
                            .html(htmlToAdd)
                            .on("click", function () {
                                window.location.hash = '#' + divName + '-' + 'category' + counts.labelNum
                            });
                    }

                })


            } else {
                var contextColumns = [
                    fullData.info.category_internal_name,
                    fullData.info.not_category_name
                ];
                if (showNeutral) {
                    if ('neutral_category_name' in fullData.info) {
                        contextColumns.push(fullData.info.neutral_category_name)
                    } else {
                        contextColumns.push("Neutral")
                    }
                    if (showExtra) {
                        if ('extra_category_name' in fullData.info) {
                            contextColumns.push(fullData.info.extra_category_name)
                        } else {
                            contextColumns.push("Extra")
                        }
                    }

                }
                contextColumns.map(
                    function (catName, catIndex) {
                        if (max_snippets != null) {
                            var contextsToDisplay = contexts[catIndex].slice(0, max_snippets);
                        }
                        console.log("CATCAT")
                        console.log(catName, catIndex)
                        //var divId = catName == catInternalName ? '#cat' : '#notcat';
                        var divId = null
                        if (fullData.info.category_internal_name == catName) {
                            divId = '#' + divName + '-' + 'cat'
                        } else if (fullData.info.not_category_name == catName) {
                            divId = '#' + divName + '-' + 'notcat'
                        } else if (fullData.info.neutral_category_name == catName) {
                            divId = '#' + divName + '-' + 'neut';
                        } else if (fullData.info.extra_category_name == catName) {
                            divId = '#' + divName + '-' + 'extra'
                        } else {
                            return;
                        }
                        console.log('divid');
                        console.log(divId)

                        var temp = d3.select(divId).selectAll("div").remove();
                        contexts[catIndex].forEach(function (context) {
                            addSnippets(context, divId);
                        });
                        if (includeAll) {
                            notmatches[catIndex].forEach(function (context) {
                                addSnippets(context, divId, false);
                            });
                        }
                    }
                );
            }

            var obscuredTerms = getObscuredTerms(data, termInfo.info);
            displayObscuredTerms(obscuredTerms, data, info.term, info, '#' + divName + '-' + 'overlapped-terms-clicked');

            d3.select('#' + divName + '-' + 'termstats')
                .selectAll("div")
                .remove();
            var termHtml = 'Term: <b>' + info.term + '</b>';
            if ('metalists' in fullData && info.term in fullData.metalists) {
                termHtml = 'Topic: <b>' + info.term + '</b>';
            }
            d3.select('#' + divName + '-' + 'termstats')
                .append('div')
                .attr("class", "snippet_header")
                .html(termHtml);
            if ('metalists' in fullData && info.term in fullData.metalists && topic_model_preview_size > 0) {
                d3.select('#' + divName + '-' + 'termstats')
                    .attr("class", "topic_preview")
                    .append('div')
                    .html("<b>Topic preview</b>: "
                        + fullData.metalists[info.term]
                            .slice(0, topic_model_preview_size)
                            .reduce(function (x, y) {
                                return x + ', ' + y
                            }));
            }
            if ('metadescriptions' in fullData && info.term in fullData.metadescriptions) {
                d3.select('#' + divName + '-' + 'termstats')
                    .attr("class", "topic_preview")
                    .append('div')
                    .html("<b>Description</b>: " + fullData.metadescriptions[info.term]);
            }
            var message = '';
            var cat_name = fullData.info.category_name;
            var ncat_name = fullData.info.not_category_name;


            var numCatDocs = fullData.docs.labels
                .map(function (x) {
                    return (x == fullData.docs.categories.indexOf(
                        fullData.info.category_internal_name)) + 0
                })
                .reduce(function (a, b) {
                    return a + b;
                }, 0);

            var notCategoryNumList = fullData.docs.categories.map(function (x, i) {
                if (fullData.info.not_category_internal_names.indexOf(x) > -1) {
                    return i;
                } else {
                    return -1;
                }
            }).filter(function (x) {
                return x > -1
            });


            var numNCatDocs = fullData.docs.labels
                .map(function (x) {
                    return notCategoryNumList.indexOf(x) > -1
                })
                .reduce(function (a, b) {
                    return a + b;
                }, 0);

            function getFrequencyDescription(name, count25k, count, ndocs) {
                var desc = name + ' frequency: <div class=text_subhead>' + count25k + ' per 25,000 terms</div>';
                if (!isNaN(Math.round(ndocs))) {
                    desc += '<div class=text_subhead>' + Math.round(ndocs) + ' per 1,000 docs</div>';
                }
                if (count == 0) {
                    desc += '<u>Not found in any ' + name + ' documents.</u>';
                } else {
                    if (!isNaN(Math.round(ndocs))) {
                        desc += '<u>Some of the ' + count + ' mentions:</u>';
                    } else {
                        desc += count + ' mentions';
                    }
                }
                /*
                desc += '<br><b>Discriminative:</b> ';

                desc += contextWords
                    .slice(cat_name === name ? 0 : contextWords.length - 3,
                        cat_name === name ? 3 : contextWords.length)
                    .filter(function (x) {
                        //return Math.abs(x[5]) > 1.96;
                        return true;
                    })
                    .map(function (x) {return x.join(', ')}).join('<br>');
                */
                return desc;
            }

            if (!unifiedContexts) {
                console.log("NOT UNIFIED CONTEXTS")
                d3.select('#' + divName + '-' + 'cathead')
                    .style('fill', color(1))
                    .html(
                        getFrequencyDescription(cat_name,
                            info.cat25k,
                            info.cat,
                            termInfo.contexts[0].length * 1000 / numCatDocs
                        )
                    );
                d3.select('#' + divName + '-' + 'notcathead')
                    .style('fill', color(0))
                    .html(
                        getFrequencyDescription(ncat_name,
                            info.ncat25k,
                            info.ncat,
                            termInfo.contexts[1].length * 1000 / numNCatDocs)
                    );
                console.log("TermINfo")
                console.log(termInfo);
                console.log(info)
                if (showNeutral) {
                    console.log("NEUTRAL")

                    var numList = fullData.docs.categories.map(function (x, i) {
                        if (fullData.info.neutral_category_internal_names.indexOf(x) > -1) {
                            return i;
                        } else {
                            return -1;
                        }
                    }).filter(function (x) {
                        return x > -1
                    });

                    var numDocs = fullData.docs.labels
                        .map(function (x) {
                            return numList.indexOf(x) > -1
                        })
                        .reduce(function (a, b) {
                            return a + b;
                        }, 0);

                    d3.select("#" + divName + "-neuthead")
                        .style('fill', color(0))
                        .html(
                            getFrequencyDescription(fullData.info.neutral_category_name,
                                info.neut25k,
                                info.neut,
                                termInfo.contexts[2].length * 1000 / numDocs)
                        );

                    if (showExtra) {
                        console.log("EXTRA")
                        var numList = fullData.docs.categories.map(function (x, i) {
                            if (fullData.info.extra_category_internal_names.indexOf(x) > -1) {
                                return i;
                            } else {
                                return -1;
                            }
                        }).filter(function (x) {
                            return x > -1
                        });

                        var numDocs = fullData.docs.labels
                            .map(function (x) {
                                return numList.indexOf(x) > -1
                            })
                            .reduce(function (a, b) {
                                return a + b;
                            }, 0);

                        d3.select("#" + divName + "-extrahead")
                            .style('fill', color(0))
                            .html(
                                getFrequencyDescription(fullData.info.extra_category_name,
                                    info.extra25k,
                                    info.extra,
                                    termInfo.contexts[3].length * 1000 / numDocs)
                            );

                    }
                }
            } else {
                // extra unified context code goes here
                console.log("docLabelCountsSorted")
                console.log(docLabelCountsSorted)

                docLabelCountsSorted.forEach(function (counts) {
                    var htmlToAdd = "<b>" + counts.label + "</b>: " + getCategoryStatsHTML(counts);
                    if (showCategoryHeadings) {
                        console.log("XXXX")
                        d3.select('#' + divName + '-' + 'contexts')
                            .append('div')
                            .html("XX" + htmlToAdd)
                            .on("click", function () {
                                window.location.hash = '#' + divName + '-' + 'category' + counts.labelNum
                            });
                    }
                })
            }
            if (jump) {
                if (window.location.hash == '#' + divName + '-' + 'snippets') {
                    window.location.hash = '#' + divName + '-' + 'snippetsalt';
                } else {
                    window.location.hash = '#' + divName + '-' + 'snippets';
                }
            }
        }

        function searchInText(d, includeAll = true) {
            function stripNonWordChars(term) {
                //d.term.replace(" ", "[^\\w]+")
            }

            function removeUnderScoreJoin(term) {
                /*
                '_ _asjdklf_jaksdlf_jaksdfl skld_Jjskld asdfjkl_sjkdlf'
                  ->
                "_ _asjdklf jaksdlf jaksdfl skld Jjskld asdfjkl_sjkdlf"
                 */
                return term.replace(/(\w+)(_)(\w+)/, "$1 $3")
                    .replace(/(\w+)(_)(\w+)/, "$1 $3")
                    .replace(/(\w+)(_)(\w+)/, "$1 $3");
            }

            function buildMatcher(term) {

                var boundary = '(?:\\W|^|$)';
                var wordSep = "[^\\w]+";
                if (asianMode) {
                    boundary = '( |$|^)';
                    wordSep = ' ';
                }
                if (isEmoji(term)) {
                    boundary = '';
                    wordSep = '';
                }
                if (matchFullLine) {
                    boundary = '($|^)';
                }
                var termToRegex = term;

                // https://stackoverflow.com/questions/3446170/escape-string-for-use-in-javascript-regex
                function escapeRegExp(string) {
                    return string.replace(/[#.*+?^${}()|[\]\\]'\%/g, '\\$&'); // $& means the whole matched string
                }

                /*
                ['[', ']', '(', ')', '{', '}', '^', '$', '|', '?', '"',
                    '*', '+', '-', '=', '~', '`', '{'].forEach(function (a) {
                    termToRegex = termToRegex.replace(a, '\\\\' + a)
                });
                ['.', '#'].forEach(function(a) {termToRegex = termToRegex.replace(a, '\\' + a)})
                */
                termToRegex = escapeRegExp(termToRegex);
                console.log("termToRegex")
                console.log(termToRegex)

                var regexp = new RegExp(boundary + '('
                    + removeUnderScoreJoin(
                        termToRegex.replace(' ', wordSep, 'gim')
                    ) + ')' + boundary, 'gim');
                console.log(regexp);
                try {
                    regexp.exec('X');
                } catch (err) {
                    console.log("Can't search " + term);
                    console.log(err);
                    return null;
                }
                return regexp;
            }

            var matches = [[], [], [], []];
            var notmatches = [[], [], [], []];
            var pattern = buildMatcher(d.term);
            var categoryNum = fullData.docs.categories.indexOf(fullData.info.category_internal_name);
            var notCategoryNumList = fullData.docs.categories.map(function (x, i) {
                if (fullData.info.not_category_internal_names.indexOf(x) > -1) {
                    return i;
                } else {
                    return -1;
                }
            }).filter(function (x) {
                return x > -1
            });
            var neutralCategoryNumList = fullData.docs.categories.map(function (x, i) {
                if (fullData.info.neutral_category_internal_names.indexOf(x) > -1) {
                    return i;
                } else {
                    return -1;
                }
            }).filter(function (x) {
                return x > -1
            });
            var extraCategoryNumList = fullData.docs.categories.map(function (x, i) {
                if (fullData.info.extra_category_internal_names.indexOf(x) > -1) {
                    return i;
                } else {
                    return -1;
                }
            }).filter(function (x) {
                return x > -1
            });
            console.log('extraCategoryNumList')
            console.log(extraCategoryNumList);
            console.log("categoryNum");
            console.log(categoryNum);
            console.log("categoryNum");
            if (pattern !== null) {
                for (var i in fullData.docs.texts) {
                    //var numericLabel = 1 * (fullData.docs.categories[fullData.docs.labels[i]] != fullData.info.category_internal_name);

                    var docLabel = fullData.docs.labels[i];
                    var numericLabel = -1;
                    if (docLabel == categoryNum) {
                        numericLabel = 0;
                    } else if (notCategoryNumList.indexOf(docLabel) > -1) {
                        numericLabel = 1;
                    } else if (neutralCategoryNumList.indexOf(docLabel) > -1) {
                        numericLabel = 2;
                    } else if (extraCategoryNumList.indexOf(docLabel) > -1) {
                        numericLabel = 3;
                    }
                    if (numericLabel == -1) {
                        continue;
                    }

                    var text = removeUnderScoreJoin(fullData.docs.texts[i]);
                    //var pattern = new RegExp("\\b(" + stripNonWordChars(d.term) + ")\\b", "gim");
                    var match;
                    var sentenceOffsets = null;
                    var lastSentenceStart = null;
                    var matchFound = false;
                    var curMatch = {'id': i, 'snippets': [], 'notsnippets': [], 'docLabel': docLabel};
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
                        matches[numericLabel].push(curMatch);
                    } else {
                        if (includeAll) {
                            curMatch.snippets = [
                                text.replace(/\n$/g, '\n\n')
                            ];
                            notmatches[numericLabel].push(curMatch);
                        }

                    }
                }
            }
            var toRet = {
                'contexts': matches,
                'notmatches': notmatches,
                'info': d,
                'docLabel': docLabel
            };
            return toRet;
        }

        function getDefaultTooltipContent(d) {
            var message = d.term + "<br/>" + d.cat25k + ":" + d.ncat25k + " per 25k words";
            message += '<br/>score: ' + d.os.toFixed(5);
            return message;
        }

        function getDefaultTooltipContentWithoutScore(d) {
            var message = d.term + "<br/>" + d.cat25k + ":" + d.ncat25k + " per 25k words";
            return message;
        }

        function getObscuredTerms(data, d) {
            //data = fullData['data']
            var matches = (data.filter(function (term) {
                    return term.x === d.x && term.y === d.y && (term.display === undefined || term.display === true);
                }).map(function (term) {
                    return term.term
                }).sort()
            );
            return matches;
        }

        function showTooltip(data, d, pageX, pageY, showObscured = true) {
            deselectLastCircle();

            var obscuredTerms = getObscuredTerms(data, d);
            var message = '';
            console.log("!!!!! " + obscuredTerms.length)
            console.log(showObscured)
            if (obscuredTerms.length > 1 && showObscured)
                displayObscuredTerms(obscuredTerms, data, d.term, d);
            if (getTooltipContent !== null) {
                message += getTooltipContent(d);
            } else {
                if (sortByDist) {
                    message += getDefaultTooltipContentWithoutScore(d);
                } else {
                    message += getDefaultTooltipContent(d);
                }
            }
            pageX -= (svg.node().getBoundingClientRect().left) - origSVGLeft;
            pageY -= (svg.node().getBoundingClientRect().top) - origSVGTop;
            tooltip.transition()
                .duration(0)
                .style("opacity", 1)
                .style("z-index", 10000000);
            tooltip.html(message)
                .style("left", (pageX - 40) + "px")
                .style("top", (pageY - 85 > 0 ? pageY - 85 : 0) + "px");
            tooltip.on('click', function () {
                tooltip.transition()
                    .style('opacity', 0)
            }).on('mouseout', function () {
                tooltip.transition().style('opacity', 0)
            });
        }

        handleSearch = function (event) {
            var searchTerm = document
                .getElementById(this.divName + "-searchTerm")
                .value;
            handleSearchTerm(searchTerm);
            return false;
        };

        function highlightTerm(searchTerm, showObscured) {
            deselectLastCircle();
            var cleanedTerm = searchTerm.toLowerCase()
                .replace("'", " '")
                .trim();
            if (this.termDict[cleanedTerm] === undefined) {
                cleanedTerm = searchTerm.replace("'", " '").trim();
            }
            if (this.termDict[cleanedTerm] !== undefined) {
                showToolTipForTerm(this.data, this.svg, cleanedTerm, this.termDict[cleanedTerm], showObscured);
            }
            return cleanedTerm;
        }

        function handleSearchTerm(searchTerm, jump = false) {
            console.log("Handle search term.");
            console.log(searchTerm);
            console.log("this");
            console.log(this)
            highlighted = highlightTerm.call(this, searchTerm, true);
            console.log("found searchTerm");
            console.log(searchTerm);
            if (this.termDict[searchTerm] != null) {
                var runDisplayTermContexts = true;
                if (alternativeTermFunc != null) {
                    runDisplayTermContexts = this.alternativeTermFunc(this.termDict[searchTerm]);
                }
                if (runDisplayTermContexts) {
                    displayTermContexts(
                        this.data,
                        this.gatherTermContexts(this.termDict[searchTerm], this.includeAllContexts),
                        alwaysJump,
                        this.includeAllContexts
                    );
                }
            }
        }

        function showToolTipForTerm(data, mysvg, searchTerm, searchTermInfo, showObscured = true) {
            //var searchTermInfo = termDict[searchTerm];
            console.log("showing tool tip")
            console.log(searchTerm)
            console.log(searchTermInfo)
            if (searchTermInfo === undefined) {
                console.log("can't show")
                d3.select("#" + divName + "-alertMessage")
                    .text(searchTerm + " didn't make it into the visualization.");
            } else {
                d3.select("#" + divName + "-alertMessage").text("");
                var circle = mysvg;
                console.log("mysvg");
                console.log(mysvg)
                if (circle.tagName !== "circle") { // need to clean this thing up
                    circle = mysvg._groups[0][searchTermInfo.ci];
                    if (circle === undefined || circle.tagName != 'circle') {
                        console.log("circle0")
                        if (mysvg._groups[0].children !== undefined) {
                            circle = mysvg._groups[0].children[searchTermInfo.ci];
                        }
                    }
                    if (circle === undefined || circle.tagName != 'circle') {
                        console.log("circle1");
                        if (mysvg._groups[0][0].children !== undefined) {
                            circle = Array.prototype.filter.call(
                                mysvg._groups[0][0].children,
                                x => (x.tagName == "circle" && x.__data__['term'] == searchTermInfo.term)
                            )[0];
                        }
                        console.log(circle)
                    }
                    if ((circle === undefined || circle.tagName != 'circle') && mysvg._groups[0][0].children !== undefined) {
                        console.log("circle2");
                        console.log(mysvg._groups[0][0])
                        console.log(mysvg._groups[0][0].children)
                        console.log(searchTermInfo.ci);
                        circle = mysvg._groups[0][0].children[searchTermInfo.ci];
                        console.log(circle)
                    }
                }
                if (circle) {
                    var mySVGMatrix = circle.getScreenCTM().translate(circle.cx.baseVal.value, circle.cy.baseVal.value);
                    var pageX = mySVGMatrix.e;
                    var pageY = mySVGMatrix.f;
                    circle.style["stroke"] = "black";
                    //var circlePos = circle.position();
                    //var el = circle.node()
                    //showTooltip(searchTermInfo, pageX, pageY, circle.cx.baseVal.value, circle.cx.baseVal.value);
                    showTooltip(
                        data,
                        searchTermInfo,
                        pageX,
                        pageY,
                        showObscured
                    );

                    lastCircleSelected = circle;
                }

            }
        };


        function makeWordInteractive(data, svg, domObj, term, termInfo, showObscured = true) {
            return domObj
                .on("mouseover", function (d) {
                    console.log("mouseover")
                    console.log(term)
                    console.log(termInfo)
                    showToolTipForTerm(data, svg, term, termInfo, showObscured);
                    d3.select(this).style("stroke", "black");
                })
                .on("mouseout", function (d) {
                    tooltip.transition()
                        .duration(0)
                        .style("opacity", 0);
                    d3.select(this).style("stroke", null);
                    if (showObscured) {
                        d3.select('#' + divName + '-' + 'overlapped-terms')
                            .selectAll('div')
                            .remove();
                    }
                })
                .on("click", function (d) {
                    var runDisplayTermContexts = true;
                    if (alternativeTermFunc != null) {
                        runDisplayTermContexts = alternativeTermFunc(termInfo);
                    }
                    if (runDisplayTermContexts) {
                        displayTermContexts(data, gatherTermContexts(termInfo, includeAllContexts), alwaysJump, includeAllContexts);
                    }
                });
        }

        function processData(fullData) {

            modelInfo = fullData['info'];
            /*
             categoryTermList.data(modelInfo['category_terms'])
             .enter()
             .append("li")
             .text(function(d) {return d;});
             */
            var data = fullData['data'];
            termDict = Object();
            data.forEach(function (x, i) {
                termDict[x.term] = x;
                //!!!
                //termDict[x.term].i = i;
            });

            var padding = 0;
            if (showAxes || showAxesAndCrossHairs) {
                padding = 0.1;
            }

            // Scale the range of the data.  Add some space on either end.
            x.domain([-1 * padding, d3.max(data, function (d) {
                return d.x;
            }) + padding]);
            y.domain([-1 * padding, d3.max(data, function (d) {
                return d.y;
            }) + padding]);

            /*
             data.sort(function (a, b) {
             return Math.abs(b.os) - Math.abs(a.os)
             });
             */


            //var rangeTree = null; // keep boxes of all points and labels here
            var rectHolder = new RectangleHolder();
            // Add the scatterplot
            data.forEach(function (d, i) {
                d.ci = i
            });
            //console.log('XXXXX'); console.log(data)
            var mysvg = svg
                .selectAll("dot")
                .data(data.filter(d => d.display === undefined || d.display === true))
                //.filter(function (d) {return d.display === undefined || d.display === true})
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
                    if (colorFunc) {
                        return colorFunc(d);
                    } else if (greyZeroScores && d.os == 0) {
                        return d3.rgb(230, 230, 230);
                    } else if (pValueColors && d.p) {
                        if (d.p >= 1 - minPVal) {
                            return wordVecMaxPValue ? d3.interpolateYlGnBu(d.s) : color(d.s);
                        } else if (d.p <= minPVal) {
                            return wordVecMaxPValue ? d3.interpolateYlGnBu(d.s) : color(d.s);
                        } else {
                            return interpolateLightGreys(d.s);
                        }
                    } else {
                        if (d.term == "psychological") {
                            console.log("COLS " + d.s + " " + color(d.s) + " " + d.term)
                            console.log(d)
                            console.log(color)
                        }
                        return color(d.s);
                    }
                })
                .on("mouseover", function (d) {
                    /*var mySVGMatrix = circle.getScreenCTM()n
                        .translate(circle.cx.baseVal.value, circle.cy.baseVal.value);
                    var pageX = mySVGMatrix.e;
                    var pageY = mySVGMatrix.f;*/

                    /*showTooltip(
                        d,
                        d3.event.pageX,
                        d3.event.pageY
                    );*/
                    console.log("point MOUSOEVER")
                    console.log(d)
                    showToolTipForTerm(data, this, d.term, d, true);
                    d3.select(this).style("stroke", "black");
                })
                .on("click", function (d) {
                    var runDisplayTermContexts = true;
                    if (alternativeTermFunc != null) {
                        runDisplayTermContexts = alternativeTermFunc(d);
                    }
                    if (runDisplayTermContexts) {
                        displayTermContexts(data, gatherTermContexts(d), alwaysJump, includeAllContexts);
                    }
                })
                .on("mouseout", function (d) {
                    tooltip.transition()
                        .duration(0)
                        .style("opacity", 0);
                    d3.select(this).style("stroke", null);
                    d3.select('#' + divName + '-' + 'overlapped-terms')
                        .selectAll('div')
                        .remove();
                })


            coords = Object();

            var pointStore = [];
            var pointRects = [];

            function censorPoints(datum, getX, getY) {
                var term = datum.term;
                var curLabel = svg.append("text")
                    .attr("x", x(getX(datum)))
                    .attr("y", y(getY(datum)) + 3)
                    .attr("text-anchor", "middle")
                    .text("x");
                var bbox = curLabel.node().getBBox();
                var borderToRemove = .5;
                var x1 = bbox.x + borderToRemove,
                    y1 = bbox.y + borderToRemove,
                    x2 = bbox.x + bbox.width - borderToRemove,
                    y2 = bbox.y + bbox.height - borderToRemove;
                //rangeTree = insertRangeTree(rangeTree, x1, y1, x2, y2, '~~' + term);
                var pointRect = new Rectangle(x1, y1, x2, y2);
                pointRects.push(pointRect);
                rectHolder.add(pointRect);
                pointStore.push([x1, y1]);
                pointStore.push([x2, y1]);
                pointStore.push([x1, y2]);
                pointStore.push([x2, y2]);
                curLabel.remove();
            }

            function censorCircle(xCoord, yCoord) {
                var curLabel = svg.append("text")
                    .attr("x", x(xCoord))
                    .attr("y", y(yCoord) + 3)
                    .attr("text-anchor", "middle")
                    .text("x");
                var bbox = curLabel.node().getBBox();
                var borderToRemove = .5;
                var x1 = bbox.x + borderToRemove,
                    y1 = bbox.y + borderToRemove,
                    x2 = bbox.x + bbox.width - borderToRemove,
                    y2 = bbox.y + bbox.height - borderToRemove;
                var pointRect = new Rectangle(x1, y1, x2, y2);
                pointRects.push(pointRect);
                rectHolder.add(pointRect);
                pointStore.push([x1, y1]);
                pointStore.push([x2, y1]);
                pointStore.push([x1, y2]);
                pointStore.push([x2, y2]);
                curLabel.remove();
            }

            function labelPointsIfPossible(datum, myX, myY) {
                var term = datum.term;
                if (term == "the")
                    console.log("TERM " + term + " " + myX + " " + myY)
                //console.log('xxx'); console.log(term); console.log(term.display !== undefined && term.display === false)
                //if(term.display !== undefined && term.display === false) {
                //    return false;
                //}
                var configs = [
                    {'anchor': 'end', 'xoff': -5, 'yoff': -3, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'end', 'xoff': -5, 'yoff': 10, 'alignment-baseline': 'ideographic'},

                    {'anchor': 'end', 'xoff': 10, 'yoff': 15, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'end', 'xoff': -10, 'yoff': -15, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'end', 'xoff': 10, 'yoff': -15, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'end', 'xoff': -10, 'yoff': 15, 'alignment-baseline': 'ideographic'},

                    {'anchor': 'start', 'xoff': 3, 'yoff': 10, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'start', 'xoff': 3, 'yoff': -3, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'start', 'xoff': 5, 'yoff': 10, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'start', 'xoff': 5, 'yoff': -3, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'start', 'xoff': 10, 'yoff': 15, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'start', 'xoff': -10, 'yoff': -15, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'start', 'xoff': 10, 'yoff': -15, 'alignment-baseline': 'ideographic'},
                    {'anchor': 'start', 'xoff': -10, 'yoff': 15, 'alignment-baseline': 'ideographic'},
                ];
                if (centerLabelsOverPoints) {
                    configs = [{'anchor': 'middle', 'xoff': 0, 'yoff': 0, 'alignment-baseline': 'middle'}];
                }
                var matchedElement = null;
                for (var configI in configs) {
                    var config = configs[configI];
                    var curLabel = svg.append("text")
                        //.attr("x", x(data[i].x) + config['xoff'])
                        //.attr("y", y(data[i].y) + config['yoff'])
                        .attr("x", x(myX) + config['xoff'])
                        .attr("y", y(myY) + config['yoff'])
                        .attr('class', 'label')
                        .attr('class', 'pointlabel')
                        .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                        .attr('font-size', '10px')
                        .attr("text-anchor", config['anchor'])
                        .attr("alignment-baseline", config['alignment'])
                        .text(term);
                    var bbox = curLabel.node().getBBox();
                    var borderToRemove = .25;
                    if (doCensorPoints) {
                        var borderToRemove = .5;
                    }

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
                        curLabel = makeWordInteractive(data, svg, curLabel, term, datum);
                        break;
                    }
                }

                if (!matchedElement) {
                    coords[term] = [x1, y1, x2, y2];
                    //rangeTree = insertRangeTree(rangeTree, x1, y1, x2, y2, term);
                    var labelRect = new Rectangle(x1, y1, x2, y2)
                    rectHolder.add(labelRect);
                    pointStore.push([x1, y1]);
                    pointStore.push([x2, y1]);
                    pointStore.push([x1, y2]);
                    pointStore.push([x2, y2]);
                    return {label: curLabel, rect: labelRect};
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
                if (b.bg === a.bg)
                    return (b.cat + b.ncat) - (a.cat + a.ncat);
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
                if (sortByDist) {
                    var aGood = __ret.aGood;
                    var bGood = __ret.bGood;
                    if (aGood && !bGood) return -1;
                    if (!aGood && bGood) return 1;
                }
                return b.s - a.s;
            }

            function scoreSortForNotCategory(a, b) {
                var __ret = arePointsPredictiveOfDifferentCategories(a, b);
                if (sortByDist) {
                    var aGood = __ret.aGood;
                    var bGood = __ret.bGood;
                    if (aGood && !bGood) return 1;
                    if (!aGood && bGood) return -1;
                }
                if (reverseSortScoresForNotCategory)
                    return a.s - b.s;
                else
                    return b.s - a.s;
            }

            var sortedData = data.map(x => x).sort(sortByDist ? euclideanDistanceSort : scoreSort);
            if (doCensorPoints) {
                for (var i in data) {
                    var d = sortedData[i];
                    censorPoints(
                        d,
                        function (d) {
                            return d.x
                        },
                        function (d) {
                            return d.y
                        }
                    );
                }
            }


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

            function drawXLabel(svg, labelText) {
                return svg.append("text")
                    .attr("class", "x label")
                    .attr("text-anchor", "end")
                    .attr("x", width)
                    .attr("y", height - 6)
                    .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                    .attr('font-size', '10px')
                    .text(labelText);
            }

            function drawYLabel(svg, labelText) {
                return svg.append("text")
                    .attr("class", "y label")
                    .attr("text-anchor", "end")
                    .attr("y", 6)
                    .attr("dy", ".75em")
                    .attr("transform", "rotate(-90)")
                    .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                    .attr('font-size', '10px')
                    .text(labelText);
                registerFigureBBox(yLabel);
            }

            d3.selection.prototype.moveToBack = function () {
                return this.each(function () {
                    var firstChild = this.parentNode.firstChild;
                    if (firstChild) {
                        this.parentNode.insertBefore(this, firstChild);
                    }
                });
            };

            if (verticalLines) {
                for (i in verticalLines) {
                    svg.append("g")
                        .attr("transform", "translate(" + x(verticalLines) + ", 1)")
                        .append("line")
                        .attr("y2", height)
                        .style("stroke", "#dddddd")
                        .style("stroke-width", "1px")
                        .moveToBack();
                }
            }

            if (showAxes || showAxesAndCrossHairs) {

                var myXAxis = svg.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + height + ")")
                    .call(xAxis);

                //rangeTree = registerFigureBBox(myXAxis);


                var xLabel = drawXLabel(svg, getLabelText('x'));

                //console.log('xLabel');
                //console.log(xLabel);

                //rangeTree = registerFigureBBox(xLabel);
                // Add the Y Axis

                if (!yAxisValues) {
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
                } else {
                    var myYAxis = svg.append("g")
                        .attr("class", "y axis")
                        .call(yAxis)
                        .selectAll("text")
                        .style("text-anchor", "end")
                        .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                        .attr('font-size', '10px');
                }
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

                var yLabel = drawYLabel(svg, getLabelText('y'))

            }
            if (!showAxes || showAxesAndCrossHairs) {
                horizontal_line_y_position_translated = 0.5;
                if (horizontal_line_y_position !== null) {
                    var loOy = null, hiOy = null, loY = null, hiY = null;
                    for (i in fullData.data) {
                        var curOy = fullData.data[i].oy;
                        if (curOy < horizontal_line_y_position && (curOy > loOy || loOy === null)) {
                            loOy = curOy;
                            loY = fullData.data[i].y
                        }
                        if (curOy > horizontal_line_y_position && (curOy < hiOy || hiOy === null)) {
                            hiOy = curOy;
                            hiY = fullData.data[i].y
                        }
                    }
                    horizontal_line_y_position_translated = loY + (hiY - loY) / 2.
                    if (loY === null) {
                        horizontal_line_y_position_translated = 0;
                    }
                }
                if (vertical_line_x_position === null) {
                    vertical_line_x_position_translated = 0.5;
                } else {
                    if (vertical_line_x_position !== null) {
                        var loOx = null, hiOx = null, loX = null, hiX = null;
                        for (i in fullData.data) {
                            var curOx = fullData.data[i].ox;
                            if (curOx < vertical_line_x_position && (curOx > loOx || loOx === null)) {
                                loOx = curOx;
                                loX = fullData.data[i].x;
                            }
                            if (curOx > vertical_line_x_position && (curOx < hiOx || hiOx === null)) {
                                hiOx = curOx;
                                hiX = fullData.data[i].x
                            }
                        }
                        vertical_line_x_position_translated = loX + (hiX - loX) / 2.
                        if (loX === null) {
                            vertical_line_x_position_translated = 0;
                        }
                    }
                }
                if (showCrossAxes) {
                    var x_line = svg.append("g")
                        .attr("transform", "translate(0, " + y(horizontal_line_y_position_translated) + ")")
                        .append("line")
                        .attr("x2", width)
                        .style("stroke", "#cccccc")
                        .style("stroke-width", "1px")
                        .moveToBack();
                    var y_line = svg.append("g")
                        .attr("transform", "translate(" + x(vertical_line_x_position_translated) + ", 0)")
                        .append("line")
                        .attr("y2", height)
                        .style("stroke", "#cccccc")
                        .style("stroke-width", "1px")
                        .moveToBack();
                }
            }

            function showWordList(word, termDataList) {
                var maxWidth = word.node().getBBox().width;
                var wordObjList = [];
                for (var i in termDataList) {
                    var curTerm = termDataList[i].term;
                    word = (function (word, curTerm) {
                        var curWordPrinted = svg.append("text")
                            .attr("text-anchor", "start")
                            .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                            .attr('font-size', '12px')
                            .attr("x", word.node().getBBox().x)
                            .attr("y", word.node().getBBox().y
                                + 2 * word.node().getBBox().height)
                            .text(curTerm);
                        wordObjList.push(curWordPrinted)
                        return makeWordInteractive(
                            termDataList, //data,
                            svg,
                            curWordPrinted,
                            curTerm,
                            termDataList[i]);
                    })(word, curTerm);
                    if (word.node().getBBox().width > maxWidth)
                        maxWidth = word.node().getBBox().width;
                    registerFigureBBox(word);
                }
                return {
                    'word': word,
                    'maxWidth': maxWidth,
                    'wordObjList': wordObjList
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

            function showAssociatedWordList(data, word, header, isAssociatedToCategory, length = 14) {
                var sortedData = null;
                var sortingAlgo = pickTermSortingAlgorithm(isAssociatedToCategory);
                sortedData = data.filter(term => (term.display === undefined || term.display === true)).sort(sortingAlgo);
                if (wordVecMaxPValue) {
                    function signifTest(x) {
                        if (isAssociatedToCategory)
                            return x.p >= 1 - minPVal;
                        return x.p <= minPVal;
                    }

                    sortedData = sortedData.filter(signifTest)
                }
                return showWordList(word, sortedData.slice(0, length));

            }

            var characteristicXOffset = width;

            function showCatHeader(startingOffset, catName, registerFigureBBox) {
                var catHeader = svg.append("text")
                    .attr("text-anchor", "start")
                    .attr("x", startingOffset //width
                    )
                    .attr("dy", "6px")
                    .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                    .attr('font-size', '12px')
                    .attr('font-weight', 'bolder')
                    .attr('font-decoration', 'underline')
                    .text(catName
                        //"Top " + fullData['info']['category_name']
                    );
                registerFigureBBox(catHeader);
                return catHeader;
            }

            function showNotCatHeader(startingOffset, word, notCatName) {
                console.log("showNotCatHeader")
                console.log(word)
                console.log(word.node().getBBox().y - word.node().getBBox().height)
                console.log(word.node().getBBox().y + word.node().getBBox().height)
                return svg.append("text")
                    .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                    .attr('font-size', '12px')
                    .attr('font-weight', 'bolder')
                    .attr('font-decoration', 'underline')
                    .attr("text-anchor", "start")
                    .attr("x", startingOffset)
                    .attr("y", word.node().getBBox().y + 3 * word.node().getBBox().height)
                    .text(notCatName);
            }

            function showTopTermsPane(data,
                                      registerFigureBBox,
                                      showAssociatedWordList,
                                      catName,
                                      notCatName,
                                      startingOffset) {
                data = data.filter(term => (term.display === undefined || term.display === true));
                //var catHeader = showCatHeader(startingOffset, catName, registerFigureBBox);
                var catHeader = svg.append("text")
                    .attr("text-anchor", "start")
                    .attr("x", startingOffset)
                    .attr("dy", "6px")
                    .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                    .attr('font-size', '12px')
                    .attr('font-weight', 'bolder')
                    .attr('font-decoration', 'underline')
                    .text(catName
                        //"Top " + fullData['info']['category_name']
                    );
                registerFigureBBox(catHeader);
                var word = catHeader;
                var wordListData = showAssociatedWordList(data, word, catHeader, true);
                word = wordListData.word;
                var maxWidth = wordListData.maxWidth;

                var notCatHeader = showNotCatHeader(startingOffset, word, notCatName);
                word = notCatHeader;
                characteristicXOffset = catHeader.node().getBBox().x + maxWidth + 10;

                var notWordListData = showAssociatedWordList(data, word, notCatHeader, false);
                word = wordListData.word;
                if (wordListData.maxWidth > maxWidth) {
                    maxWidth = wordListData.maxWidth;
                }
                return {
                    wordListData, notWordListData,
                    word, maxWidth, characteristicXOffset, startingOffset,
                    catHeader, notCatHeader, registerFigureBBox
                };
            }

            var payload = Object();
            if (showTopTerms) {
                payload.topTermsPane = showTopTermsPane(
                    data,
                    registerFigureBBox,
                    showAssociatedWordList,
                    "Top " + fullData['info']['category_name'],
                    "Top " + fullData['info']['not_category_name'],
                    width
                );
                payload.showTopTermsPane = showTopTermsPane;
                payload.showAssociatedWordList = showAssociatedWordList;
                payload.showWordList = showWordList;
                /*var wordListData = topTermsPane.wordListData;
                var word = topTermsPane.word;
                var maxWidth = topTermsPane.maxWidth;
                var catHeader = topTermsPane.catHeader;
                var notCatHeader = topTermsPane.notCatHeader;
                var startingOffset = topTermsPane.startingOffset;*/
                characteristicXOffset = payload.topTermsPane.characteristicXOffset;
            }


            if (!nonTextFeaturesMode && !asianMode && showCharacteristic) {
                var sortMethod = backgroundScoreSort;
                var title = 'Characteristic';
                if (wordVecMaxPValue) {
                    title = 'Most similar';
                    sortMethod = scoreSortReverse;
                } else if (data.reduce(function (a, b) {
                    return a + b.bg
                }, 0) === 0) {
                    title = 'Most frequent';
                }
                word = svg.append("text")
                    .attr('font-family', 'Helvetica, Arial, Sans-Serif')
                    .attr("text-anchor", "start")
                    .attr('font-size', '12px')
                    .attr('font-weight', 'bolder')
                    .attr('font-decoration', 'underline')
                    .attr("x", characteristicXOffset)
                    .attr("dy", "6px")
                    .text(title);

                var wordListData = showWordList(word, data.filter(term => (term.display === undefined || term.display === true)).sort(sortMethod).slice(0, 30));

                word = wordListData.word;
                maxWidth = wordListData.maxWidth;
                console.log(maxWidth);
                console.log(word.node().getBBox().x + maxWidth);

                svg.attr('width', word.node().getBBox().x + 3 * maxWidth + 10);
            }

            function performPartialLabeling(data, existingLabels, getX, getY) {
                for (i in existingLabels) {
                    rectHolder.remove(existingLabels[i].rect);
                    existingLabels[i].label.remove();
                }
                console.log('labeling 1')


                var labeledPoints = [];
                //var filteredData = data.filter(d=>d.display === undefined || d.display === true);
                //for (var i = 0; i < filteredData.length; i++) {
                data.forEach(function (datum, i) {
                    //console.log(datum.i, datum.ci, i)
                    //var label = labelPointsIfPossible(i, getX(filteredData[i]), getY(filteredData[i]));
                    if (datum.display === undefined || datum.display === true) {
                        if (datum.term == "the" || i == 1) {
                            console.log("trying to label datum # " + i + ": " + datum.term)
                            console.log(datum)
                            console.log([getX(datum), getY(datum)])
                        }
                        var label = labelPointsIfPossible(datum, getX(datum), getY(datum));
                        if (label !== false) {
                            //console.log("labeled")
                            labeledPoints.push(label)
                        }
                    }
                    //if (labelPointsIfPossible(i), true) numPointsLabeled++;
                })
                return labeledPoints;
            }

            //var labeledPoints = performPartialLabeling();
            var labeledPoints = [];
            labeledPoints = performPartialLabeling(data,
                labeledPoints,
                function (d) {
                    return d.x
                },
                function (d) {
                    return d.y
                });


            /*
            // pointset has to be sorted by X
            function convex(pointset) {
                function _cross(o, a, b) {
                    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
                }

                function _upperTangent(pointset) {
                    var lower = [];
                    for (var l = 0; l < pointset.length; l++) {
                        while (lower.length >= 2 && (_cross(lower[lower.length - 2], lower[lower.length - 1], pointset[l]) <= 0)) {
                            lower.pop();
                        }
                        lower.push(pointset[l]);
                    }
                    lower.pop();
                    return lower;
                }

                function _lowerTangent(pointset) {
                    var reversed = pointset.reverse(),
                        upper = [];
                    for (var u = 0; u < reversed.length; u++) {
                        while (upper.length >= 2 && (_cross(upper[upper.length - 2], upper[upper.length - 1], reversed[u]) <= 0)) {
                            upper.pop();
                        }
                        upper.push(reversed[u]);
                    }
                    upper.pop();
                    return upper;
                }

                var convex,
                    upper = _upperTangent(pointset),
                    lower = _lowerTangent(pointset);
                convex = lower.concat(upper);
                convex.push(pointset[0]);
                return convex;
            }

            console.log("POINTSTORE")
            console.log(pointStore);
            pointStore.sort();
            var convexHull = convex(pointStore);
            var minX = convexHull.sort(function (a,b) {
                return a[0] < b[0] ? -1 : 1;
            })[0][0];
            var minY = convexHull.sort(function (a,b) {
                return a[1] < b[1] ? -1 : 1;
            })[0][0];
            //svg.append("text").text("BLAH BLAH").attr("text-anchor", "middle").attr("cx", x(0)).attr("y", minY);
            console.log("POINTSTORE")
            console.log(pointStore);
            console.log(convexHull);
            for (i in convexHull) {
                var i = parseInt(i);
                if (i + 1 == convexHull.length) {
                    var nextI = 0;
                } else {
                    var nextI = i + 1;
                }
                console.log(i, ',', nextI);
                svg.append("line")
                    .attr("x2", width)
                    .style("stroke", "#cc0000")
                    .style("stroke-width", "1px")
                    .attr("x1", convexHull[i][0])     // x position of the first end of the line
                    .attr("y1", convexHull[i][1])      // y position of the first end of the line
                    .attr("x2", convexHull[nextI][0])     // x position of the second end of the line
                    .attr("y2", convexHull[nextI][1]);    // y position of the second end of the line
            }*/

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
                    var name = null;
                    if (unifiedContexts) {
                        var name = fullData.docs.categories[x];
                        wordCounts[name] = wordCounts[name] ? wordCounts[name] + cnt : cnt;
                    } else {
                        if (fullData.docs.categories[x] == fullData.info.category_internal_name) {
                            name = fullData.info.category_name;
                        } else if (fullData.info.not_category_internal_names.indexOf(fullData.docs.categories[x]) > -1) {
                            name = fullData.info.not_category_name;
                        } else if (fullData.info.neutral_category_internal_names.indexOf(fullData.docs.categories[x]) > -1) {
                            name = fullData.info.neutral_category_name;
                        } else if (fullData.info.extra_category_internal_names.indexOf(fullData.docs.categories[x]) > -1) {
                            name = fullData.info.extra_category_name;
                        }
                        if (name) {
                            wordCounts[name] = wordCounts[name] ? wordCounts[name] + cnt : cnt
                        }
                    }
                    //!!!

                });
                fullData.docs.labels.forEach(function (x) {

                    if (unifiedContexts) {
                        var name = fullData.docs.categories[x];
                        docCounts[name] = docCounts[name] ? docCounts[name] + 1 : 1
                    } else {
                        var name = null;
                        if (fullData.docs.categories[x] == fullData.info.category_internal_name) {
                            name = fullData.info.category_name;
                        } else if (fullData.info.not_category_internal_names.indexOf(fullData.docs.categories[x]) > -1) {
                            name = fullData.info.not_category_name;
                        } else if (fullData.info.neutral_category_internal_names.indexOf(fullData.docs.categories[x]) > -1) {
                            name = fullData.info.neutral_category_name;
                        } else if (fullData.info.extra_category_internal_names.indexOf(fullData.docs.categories[x]) > -1) {
                            name = fullData.info.extra_category_name;
                        }
                        if (name) {
                            docCounts[name] = docCounts[name] ? docCounts[name] + 1 : 1
                        }
                    }
                });
                console.log("docCounts");
                console.log(docCounts)
                var messages = [];
                if (unifiedContexts) {
                    fullData.docs.categories.forEach(function (x, i) {
                        if (docCounts[x] > 0) {
                            messages.push('<b>' + x + '</b> document count: '
                                + Number(docCounts[x]).toLocaleString('en')
                                + '; word count: '
                                + Number(wordCounts[x]).toLocaleString('en'));
                        }
                    });
                } else {
                    [fullData.info.category_name,
                        fullData.info.not_category_name,
                        fullData.info.neutral_category_name,
                        fullData.info.extra_category_name].forEach(function (x, i) {
                        if (docCounts[x] > 0) {
                            messages.push('<b>' + x + '</b> document count: '
                                + Number(docCounts[x]).toLocaleString('en')
                                + '; word count: '
                                + Number(wordCounts[x]).toLocaleString('en'));
                        }
                    });
                }

                if (showCorpusStats) {
                    d3.select('#' + divName + '-' + 'corpus-stats')
                        .style('width', width + margin.left + margin.right + 200)
                        .append('div')
                        .html(messages.join('<br />'));
                }
            }


            if (fullData.docs) {
                populateCorpusStats();
            }

            if (saveSvgButton) {
                // from https://stackoverflow.com/questions/23218174/how-do-i-save-export-an-svg-file-after-creating-an-svg-with-d3-js-ie-safari-an
                var svgElement = document.getElementById(divName);

                var serializer = new XMLSerializer();
                var source = serializer.serializeToString(svgElement);

                if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
                    source = source.replace(/^<svg/, '<svg xmlns="https://www.w3.org/2000/svg"');
                }
                if (!source.match(/^<svg[^>]+"http\:\/\/www\.w3\.org\/1999\/xlink"/)) {
                    source = source.replace(/^<svg/, '<svg xmlns:xlink="https://www.w3.org/1999/xlink"');
                }

                source = '<?xml version="1.0" standalone="no"?>\r\n' + source;

                var url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);

                var downloadLink = document.createElement("a");
                downloadLink.href = url;
                downloadLink.download = fullData['info']['category_name'] + ".svg";
                downloadLink.innerText = 'Download SVG';
                document.body.appendChild(downloadLink);

            }

            function rerender(xCoords, yCoords, color) {
                labeledPoints.forEach(function (p) {
                    p.label.remove();
                    rectHolder.remove(p.rect);
                });
                pointRects.forEach(function (rect) {
                    rectHolder.remove(rect);
                });
                pointRects = []
                /*
                var circles = d3.select('#' + divName).selectAll('circle')
                    .attr("cy", function (d) {return y(yCoords[d.i])})
                    .transition(0)
                    .attr("cx", function (d) {return x(xCoords[d.i])})
                    .transition(0);
                */
                d3.select('#' + divName).selectAll("dot").remove();
                d3.select('#' + divName).selectAll("circle").remove();
                console.log(this.fullData)
                console.log(this)
                console.log("X/Y coords")
                console.log(this.fullData.data.filter(d => d.display === undefined || d.display === true).map(d=>[d.x, d.y]))
                var circles = this.svg//.select('#' + divName)
                    .selectAll("dot")
                    .data(this.fullData.data.filter(d => d.display === undefined || d.display === true))
                    //.filter(function (d) {return d.display === undefined || d.display === true})
                    .enter()
                    .append("circle")
                    .attr("cy", d => d.y)
                    .attr("cx", d => d.x)
                    .attr("r", d => 2)
                    .on("mouseover", function (d) {
                        /*var mySVGMatrix = circle.getScreenCTM()n
                            .translate(circle.cx.baseVal.value, circle.cy.baseVal.value);
                        var pageX = mySVGMatrix.e;
                        var pageY = mySVGMatrix.f;*/

                        /*showTooltip(
                            d,
                            d3.event.pageX,
                            d3.event.pageY
                        );*/
                        console.log("point MOUSOEVER")
                        console.log(d)
                        showToolTipForTerm(data, this, d.term, d, true);
                        d3.select(this).style("stroke", "black");
                    })
                    .on("click", function (d) {
                        var runDisplayTermContexts = true;
                        if (alternativeTermFunc != null) {
                            runDisplayTermContexts = alternativeTermFunc(d);
                        }
                        if (runDisplayTermContexts) {
                            displayTermContexts(data, gatherTermContexts(d), alwaysJump, includeAllContexts);
                        }
                    })
                    .on("mouseout", function (d) {
                        tooltip.transition()
                            .duration(0)
                            .style("opacity", 0);
                        d3.select(this).style("stroke", null);
                        d3.select('#' + divName + '-' + 'overlapped-terms')
                            .selectAll('div')
                            .remove();
                    });

                if (color !== null) {
                    console.log("COLOR")
                    console.log(color)
                    circles.style("fill", d => color(d));
                }
                xCoords.forEach((xCoord, i) => censorCircle(xCoord, yCoords[i]))
                labeledPoints = [];
                labeledPoints = performPartialLabeling(
                    this.fullData.data,
                    labeledPoints,
                    (d => d.ox), //function (d) {return xCoords[d.ci]},
                    (d => d.oy) //function (d) {return yCoords[d.ci]}
                );
            }

            //return [performPartialLabeling, labeledPoints];
            return {
                ...payload,
                ...{
                    'rerender': rerender,
                    'performPartialLabeling': performPartialLabeling,
                    'showToolTipForTerm': showToolTipForTerm,
                    'svg': svg,
                    'data': data,
                    'xLabel': xLabel,
                    'yLabel': yLabel,
                    'drawXLabel': drawXLabel,
                    'drawYLabel': drawYLabel,
                    'populateCorpusStats': populateCorpusStats
                }
            };
        }


        //fullData = getDataAndInfo();
        if (fullData.docs) {
            var corpusWordCounts = getCorpusWordCounts();
        }
        var payload = processData(fullData);

        // The tool tip is down here in order to make sure it has the highest z-index
        var tooltip = d3.select('#' + divName)
            .append("div")
            //.attr("class", getTooltipContent == null && sortByDist ? "tooltip" : "tooltipscore")
            .attr("class", "tooltipscore")
            .style("opacity", 0);

        plotInterface = {}
        if (payload.topTermsPane) {
            plotInterface.topTermsPane = payload.topTermsPane;
            plotInterface.showTopTermsPane = payload.showTopTermsPane;
            plotInterface.showAssociatedWordList = payload.showAssociatedWordList;
        }
        plotInterface.includeAllContexts = includeAllContexts;
        plotInterface.divName = divName;
        plotInterface.displayTermContexts = displayTermContexts;
        plotInterface.gatherTermContexts = gatherTermContexts;
        plotInterface.xLabel = payload.xLabel;
        plotInterface.yLabel = payload.yLabel;
        plotInterface.drawXLabel = payload.drawXLabel;
        plotInterface.drawYLabel = payload.drawYLabel;
        plotInterface.svg = payload.svg;
        plotInterface.termDict = termDict;
        plotInterface.showToolTipForTerm = payload.showToolTipForTerm;
        plotInterface.fullData = fullData;
        plotInterface.data = payload.data;
        plotInterface.rerender = payload.rerender;
        plotInterface.populateCorpusStats = payload.populateCorpusStats;
        plotInterface.handleSearch = handleSearch;
        plotInterface.handleSearchTerm = handleSearchTerm;
        plotInterface.highlightTerm = highlightTerm;
        plotInterface.y = y;
        plotInterface.x = x;
        plotInterface.tooltip = tooltip;
        plotInterface.alternativeTermFunc = alternativeTermFunc;

        plotInterface.showTooltipSimple = function (term) {
            plotInterface.showToolTipForTerm(
                plotInterface.data,
                plotInterface.svg,
                term.replace("'", "\\'"),
                plotInterface.termDict[term.replace("'", "\\'")]
            )
        };

        plotInterface.drawCategoryAssociation = function (categoryNum, otherCategoryNum = null) {
            var rawLogTermCounts = getTermCounts(this.fullData).map(Math.log);
            var maxRawLogTermCounts = Math.max(...rawLogTermCounts);
            var minRawLogTermCounts = Math.min(...rawLogTermCounts);
            var logTermCounts = rawLogTermCounts.map(
                x => (x - minRawLogTermCounts) / maxRawLogTermCounts
            )

            //var rawScores = getCategoryDenseRankScores(this.fullData, categoryNum);
            //console.log("RAW SCORES")
            //console.log(rawScores);
            /*
            function logOddsRatioUninformativeDirichletPrior(fgFreqs, bgFreqs, alpha) {
                var fgVocabSize = fgFreqs.reduce((x,y) => x+y);
                var fgL = fgFreqs.map(x => (x + alpha)/((1+alpha)*fgVocabSize - x - alpha))
                var bgVocabSize = bgFreqs.reduce((x,y) => x+y);
                var bgL = bgFreqs.map(x => (x + alpha)/((1+alpha)*bgVocabSize - x - alpha))
                var pooledVar = fgFreqs.map(function(x, i) {
                    return (
                        1/(x + alpha)
                        + 1/((1+alpha)*fgVocabSize - x - alpha)
                        + 1/(bgFreqs[i] + alpha)
                        + 1/((1+alpha)*bgVocabSize - bgFreqs[i] - alpha))
                })
                return pooledVar.map(function(x, i) {
                    return (Math.log(fgL[i]) - Math.log(bgL[i]))/x;
                })
            }
            var rawScores = logOddsRatioUninformativeDirichletPrior(
                denseRanks.fgFreqs, denseRanks.bgFreqs, 0.01);
            */


            var denseRanks = getDenseRanks(this.fullData, categoryNum)
            console.log("denseRanks")
            console.log(denseRanks);
            if (otherCategoryNum !== null) {
                var otherDenseRanks = getDenseRanks(this.fullData, otherCategoryNum);
                console.log("otherDenseRanks");
                console.log(otherDenseRanks);
                denseRanks.bg = otherDenseRanks.fg;
                denseRanks.bgFreqs = otherDenseRanks.fgFreqs;

            }

            var rawScores = denseRanks.fg.map((x, i) => x - denseRanks.bg[i]);
            var minRawScores = Math.min(...rawScores);
            var maxRawScores = Math.max(...rawScores);

            var scores = rawScores.map(
                function (rawScore) {
                    if (rawScore == 0) {
                        return 0.5;
                    } else if (rawScore > 0) {
                        return rawScore / (2. * maxRawScores) + 0.5;
                    } else if (rawScore < 0) {
                        return 0.5 - rawScore / (2. * minRawScores);
                    }
                }
            )
            var fgFreqSum = denseRanks.fgFreqs.reduce((a, b) => a + b, 0)
            var bgFreqSum = denseRanks.bgFreqs.reduce((a, b) => a + b, 0)

            //!!! OLD and good
            var ox = denseRanks.bg;
            var oy = denseRanks.fg;

            var oxmax = Math.max(...ox)
            var oxmin = Math.min(...ox)
            var ox = ox.map(x => (x - oxmin) / (oxmax - oxmin))
            var oymax = Math.max(...oy)
            var oymin = Math.min(...oy)
            var oy = oy.map(x => (x - oymin) / (oymax - oymin))
            //var ox = logTermCounts
            //var oy = scores;
            var xf = this.x;
            var yf = this.y;

            this.fullData.data = this.fullData.data.map(function (term, i) {
                //term.ci = i;
                term.s = scores[i];
                term.os = rawScores[i];
                term.cat = denseRanks.fgFreqs[i];
                term.ncat = denseRanks.bgFreqs[i];
                term.cat25k = parseInt(denseRanks.fgFreqs[i] * 25000 / fgFreqSum);
                term.ncat25k = parseInt(denseRanks.bgFreqs[i] * 25000 / bgFreqSum);
                term.x = xf(ox[i]) // logTermCounts[term.i];
                term.y = yf(oy[i]) // scores[term.i];
                term.ox = ox[i];
                term.oy = oy[i];
                term.display = false;
                return term;
            })

            // Feature selection
            var targetTermsToShow = 1500;

            var sortedBg = denseRanks.bg.map((x, i) => [x, i]).sort((a, b) => b[0] - a[0]).map(x => x[1]).slice(0, parseInt(targetTermsToShow / 2));
            var sortedFg = denseRanks.fg.map((x, i) => [x, i]).sort((a, b) => b[0] - a[0]).map(x => x[1]).slice(0, parseInt(targetTermsToShow / 2));
            var sortedScores = denseRanks.fg.map((x, i) => [x, i]).sort((a, b) => b[0] - a[0]).map(x => x[1]);
            var myFullData = this.fullData

            sortedBg.concat(sortedFg)//.concat(sortedScores.slice(0, parseInt(targetTermsToShow/2))).concat(sortedScores.slice(-parseInt(targetTermsToShow/4)))
                .forEach(function (i) {
                    myFullData.data[i].display = true;
                })

            console.log('newly filtered')
            console.log(myFullData)

            // begin rescaling to ignore hidden terms
            /*
            function scaleDenseRanks(ranks) {
                var max = Math.max(...ranks);
                return ranks.map(x=>x/max)
            }
            var filteredData = myFullData.data.filter(d=>d.display);
            var catRanks = scaleDenseRanks(denseRank(filteredData.map(d=>d.cat)))
            var ncatRanks = scaleDenseRanks(denseRank(filteredData.map(d=>d.ncat)))
            var rawScores = catRanks.map((x,i) => x - ncatRanks[i]);
            function stretch_0_1(scores) {
                var max = 1.*Math.max(...rawScores);
                var min = -1.*Math.min(...rawScores);
                return scores.map(function(x, i) {
                    if(x == 0) return 0.5;
                    if(x > 0) return (x/max + 1)/2;
                    return (x/min + 1)/2;
                })
            }
            var scores = stretch_0_1(rawScores);
            console.log(scores)
            filteredData.forEach(function(d, i) {
                d.x = xf(catRanks[i]);
                d.y = yf(ncatRanks[i]);
                d.ox = catRanks[i];
                d.oy = ncatRanks[i];
                d.s = scores[i];
                d.os = rawScores[i];
            });
            console.log("rescaled");
            */
            // end rescaling


            this.rerender(//denseRanks.bg,
                fullData.data.map(x => x.ox), //ox
                //denseRanks.fg,
                fullData.data.map(x => x.oy), //oy,
                d => d3.interpolateRdYlBu(d.s));
            if (this.yLabel !== undefined) {
                this.yLabel.remove()
            }
            if (this.xLabel !== undefined) {
                this.xLabel.remove()
            }
            var leftName = this.fullData.info.categories[categoryNum];
            var bottomName = "Not " + this.fullData.info.categories[categoryNum];
            if (otherCategoryNum !== null) {
                bottomName = this.fullData.info.categories[otherCategoryNum];
            }


            this.yLabel = this.drawYLabel(this.svg, leftName + ' Frequncy Rank')
            this.xLabel = this.drawXLabel(this.svg, bottomName + ' Frequency Rank')
            if (this.topTermsPane !== undefined) {
                this.topTermsPane.catHeader.remove()
                this.topTermsPane.notCatHeader.remove()
                this.topTermsPane.wordListData.wordObjList.map(x => x.remove())
                this.topTermsPane.notWordListData.wordObjList.map(x => x.remove())
            }
            this.showWordList = payload.showWordList;


            this.showAssociatedWordList = function (data, word, header, isAssociatedToCategory, length = 14) {
                var sortedData = null;
                if (!isAssociatedToCategory) {
                    sortedData = data.map(x => x).sort((a, b) => scores[a.i] - scores[b.i])
                } else {
                    sortedData = data.map(x => x).sort((a, b) => scores[b.i] - scores[a.i])
                }
                console.log('sortedData');
                console.log(isAssociatedToCategory);
                console.log(sortedData.slice(0, length))
                console.log(payload)
                console.log(word)
                return payload.showWordList(word, sortedData.slice(0, length));
            }
            if (this.topTermsPane !== undefined)
                this.topTermsPane = payload.showTopTermsPane(
                    this.data,
                    this.topTermsPane.registerFigureBBox,
                    this.showAssociatedWordList,
                    "Top " + leftName,
                    "Top " + bottomName,
                    this.topTermsPane.startingOffset
                )

            fullData.info.category_name = leftName;
            fullData.info.not_category_name = bottomName;
            fullData.info.category_internal_name = this.fullData.info.categories[categoryNum];
            if (otherCategoryNum === null) {
                fullData.info.not_category_internal_names = this.fullData.info.categories
                    .filter(x => x !== this.fullData.info.categories[categoryNum]);
            } else {
                fullData.info.not_category_internal_names = this.fullData.info.categories
                    .filter(x => x === this.fullData.info.categories[otherCategoryNum]);

                fullData.info.neutral_category_internal_names = this.fullData.info.categories
                    .filter(x => (x !== this.fullData.info.categories[categoryNum]
                        && x !== this.fullData.info.categories[otherCategoryNum]));
                fullData.info.neutral_category_name = "All Others";

            }
            console.log("fullData.info.not_category_internal_names");
            console.log(fullData.info.not_category_internal_names);
            ['snippets', 'snippetsalt', 'termstats',
                'overlapped-terms-clicked', 'categoryinfo',
                'cathead', 'cat', 'corpus-stats', 'notcathead',
                'notcat', 'neuthead', 'neut'
            ].forEach(function (divSubName) {
                var mydiv = '#' + divName + '-' + divSubName;
                console.log("Clearing");
                console.log(mydiv);
                d3.select(mydiv).selectAll("*").remove();
                d3.select(mydiv).html("");

            });
            this.populateCorpusStats();

            console.log(fullData)
        };

        plotInterface.yAxisLogCounts = function (categoryName) {
            var categoryNum = this.fullData.docs.categories.indexOf(categoryName);
            var denseRanks = getDenseRanks(this.fullData, categoryNum)
            console.log("denseRanks")
            console.log(denseRanks);

            var rawScores = denseRanks.fg.map((x, i) => x - denseRanks.bg[i]);
            var minRawScores = Math.min(...rawScores);
            var maxRawScores = Math.max(...rawScores);

            var scores = rawScores.map(
                function (rawScore) {
                    if (rawScore == 0) {
                        return 0.5;
                    } else if (rawScore > 0) {
                        return rawScore / (2. * maxRawScores) + 0.5;
                    } else if (rawScore < 0) {
                        return 0.5 - rawScore / (2. * minRawScores);
                    }
                }
            )
            var fgFreqSum = denseRanks.fgFreqs.reduce((a, b) => a + b, 0)
            var bgFreqSum = denseRanks.bgFreqs.reduce((a, b) => a + b, 0)

            var oy = denseRanks.fgFreqs.map(count => Math.log(count + 1)/Math.log(2))

            var oymax = Math.max(...oy)
            var oymin = Math.min(...oy)
            oy = oy.map(y => (y - oymin) / (oymax - oymin))
            var xf = this.x;
            var yf = this.y;
            var ox = this.fullData.data.map(term => term.ox);
            var oxmax = Math.max(...ox)
            var oxmin = Math.min(...ox)
            ox = ox.map(y => (y - oxmin) / (oxmax - oxmin))


            this.fullData.data = this.fullData.data.map(function (term, i) {
                term.s = 1;//scores[i];
                term.os = rawScores[i];
                term.cat = denseRanks.fgFreqs[i];
                term.ncat = denseRanks.bgFreqs[i];
                term.cat25k = parseInt(denseRanks.fgFreqs[i] * 25000 / fgFreqSum);
                term.ncat25k = parseInt(denseRanks.bgFreqs[i] * 25000 / bgFreqSum);
                //term.x = xf(term.ox) // scores[term.i];
                //term.ox = term.ox;
                term.y = yf(oy[i]) // scores[term.i];
                term.oy = oy[i];
                term.x = xf(ox[i]) // scores[term.i];
                term.ox = ox[i];
                term.display = true;
                return term;
            })



            this.rerender(//denseRanks.bg,
                this.fullData.data.map(point => point.ox), //ox
                this.fullData.data.map(point => point.oy), //oy,
                d => d3.interpolateRdYlBu(d.s)
            );

            if (this.yLabel !== undefined) {
                this.yLabel.remove()
                this.yLabel = this.drawYLabel(this.svg, this.fullData.info.categories[categoryNum] + ' log freq.')
            }

            if (this.topTermsPane !== undefined) {
                this.topTermsPane.catHeader.remove()
                this.topTermsPane.notCatHeader.remove()
                this.topTermsPane.wordListData.wordObjList.map(x => x.remove())
                this.topTermsPane.notWordListData.wordObjList.map(x => x.remove())
            }
            this.showWordList = payload.showWordList;


            this.showAssociatedWordList = function (data, word, header, isAssociatedToCategory, length = 14) {
                var sortedData = null;
                if (!isAssociatedToCategory) {
                    sortedData = data.map(x => x).sort((a, b) => scores[a.i] - scores[b.i])
                } else {
                    sortedData = data.map(x => x).sort((a, b) => scores[b.i] - scores[a.i])
                }
                console.log('sortedData');
                console.log(isAssociatedToCategory);
                console.log(sortedData.slice(0, length))
                console.log(payload)
                console.log(word)
                return payload.showWordList(word, sortedData.slice(0, length));
            }
            var leftName = this.fullData.info.categories[categoryNum];
            var bottomName = "Not " + this.fullData.info.categories[categoryNum];

            if (this.topTermsPane !== undefined)
                this.topTermsPane = payload.showTopTermsPane(
                    this.data,
                    this.topTermsPane.registerFigureBBox,
                    this.showAssociatedWordList,
                    "Top " + leftName,
                    "Top " + bottomName,
                    this.topTermsPane.startingOffset
                )

            fullData.info.category_name = leftName;
            fullData.info.not_category_name = bottomName;
            fullData.info.category_internal_name = this.fullData.info.categories[categoryNum];
            fullData.info.not_category_internal_names = this.fullData.info.categories
                .filter(x => x !== this.fullData.info.categories[categoryNum]);

            console.log("fullData.info.not_category_internal_names");
            console.log(fullData.info.not_category_internal_names);
            ['snippets', 'snippetsalt', 'termstats',
                'overlapped-terms-clicked', 'categoryinfo',
                'cathead', 'cat', 'corpus-stats', 'notcathead',
                'notcat', 'neuthead', 'neut'
            ].forEach(function (divSubName) {
                var mydiv = '#' + divName + '-' + divSubName;
                console.log("Clearing");
                console.log(mydiv);
                d3.select(mydiv).selectAll("*").remove();
                d3.select(mydiv).html("");

            });
            this.populateCorpusStats();
        };

        return plotInterface
    };
}(d3);

