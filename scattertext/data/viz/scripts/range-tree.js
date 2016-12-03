/**
 * Created by Jason Kessler. on 8/1/16.
 * Interval trees are based on code from http://www.geeksforgeeks.org/interval-tree/
 *
 * Please see testing function at the end of the file to test the commands.
 */

function newIntervalTree(low, hi, label) {
    return [[low, hi, hi, label], null, null];
}

function insertIntervalTree(root, low, high, label) {
    if (root == null) {
        return newIntervalTree(low, high, label);
    }
    // if interval is within current node, then don't insert range
    var rootLow = root[0][0];
    var rootHigh = root[0][1];

    // if root's low value is smaller, interval goes to left subtree
    if (rootLow < low) {
        root[2] = insertIntervalTree(root[2], low, high, label);
    } else { // else, new node goes to right subtree.
        root[1] = insertIntervalTree(root[1], low, high, label);
    }

    var rootMax = root[0][2];
    if (rootMax < high) {
        root[0][2] = high;
    }
    return root;
}

function overlaps(low1, high1, low2, high2) {
    return !(low1 >= high2 || low2 >= high1);
}

function searchIntervalTree(root, low, high) {
    if (root === null) return [];
    var rootLow = root[0][0];
    var rootHigh = root[0][1];
    var rootMax = root[0][2];
    var rootLabel = root[0][3];
    if (low >= rootMax) {
        return []; // null root or low >= max
    }
    var toRet = [];
    if (overlaps(rootLow, rootHigh, low, high))
        toRet = [rootLabel];

    var rootLeft = root[1];
    var rootRight = root[2];
    if (!(rootLeft === null) && rootLeft[0][2] >= low) {
        toRet = toRet.concat(searchIntervalTree(rootLeft, low, high));
    }
    if (!(rootRight === null)) {
        toRet = toRet.concat(searchIntervalTree(rootRight, low, high));
    }
    return toRet;
}

function newRangeTree(topLeftX, topLeftY, bottomRightX, bottomRightY, label) {
    return [
        newIntervalTree(
            Math.min(topLeftX, bottomRightX),
            Math.max(topLeftX, bottomRightX),
            label),
        newIntervalTree(
            Math.min(topLeftY, bottomRightY),
            Math.max(topLeftY, bottomRightY),
            label)
    ];
}

function insertRangeTree(root, topLeftX, topLeftY, bottomRightX, bottomRightY, label) {
    if (root === null) {
        return newRangeTree(topLeftX, topLeftY, bottomRightX, bottomRightY, label);
    }
    return [
        insertIntervalTree(
            root[0],
            Math.min(topLeftX, bottomRightX),
            Math.max(topLeftX, bottomRightX),
            label),
        insertIntervalTree(
            root[1],
            Math.min(topLeftY, bottomRightY),
            Math.max(topLeftY, bottomRightY),
            label)
    ]
}

// adapted from http://stackoverflow.com/questions/1885557/simplest-code-for-array-intersection-in-javascript
function doSortedArraysIntersect(a, b) {
    var ai = 0, bi = 0;
    while (ai < a.length && bi < b.length) {
        if (a[ai] < b[bi]) ai++;
        else if (a[ai] > b[bi]) bi++;
        else if (a[ai] == b[bi]) //return true;
            return a[ai];
    }
    return false;
}

function searchRangeTree(rangeTree, topLeftX, topLeftY, bottomRightX, bottomRightY) {
    if (rangeTree === null || typeof rangeTree === "undefined") {
        return false;
    }
    var xIntersects = searchIntervalTree(
        rangeTree[0],
        Math.min(topLeftX, bottomRightX),
        Math.max(topLeftX, bottomRightX));


    var yIntersects = searchIntervalTree(
        rangeTree[1],
        Math.min(topLeftY, bottomRightY),
        Math.max(topLeftY, bottomRightY));
    if (xIntersects.length == 0 || yIntersects.length == 0)
        return false;
    return doSortedArraysIntersect(xIntersects.sort(), yIntersects.sort());
}


(function () {
    console.assert(JSON.stringify(newIntervalTree(0, 6, 'a'))
        == JSON.stringify([[0, 6, 6, 'a'], null, null]));

    console.assert(overlaps(0, 1, 1, 2) == false);
    console.assert(overlaps(0, 1, 2, 3) == false);
    console.assert(overlaps(0, 2, 1, 3) == true);
    console.assert(overlaps(0, 2, 1, 2) == true);
    console.assert(overlaps(0, 2, 0, 1) == true);
    console.assert(overlaps(0, 2, -1, 1) == true);
    console.assert(overlaps(0, 2, -1, 0) == false);

    var root = newIntervalTree(15, 20, 'a');
    root = insertIntervalTree(root, 10, 30, 'b');
    root = insertIntervalTree(root, 10, 30, 'c');
    root = insertIntervalTree(root, 12, 15, 'd');
    root = insertIntervalTree(root, 17, 21, 'e');
    root = insertIntervalTree(root, 30, 40, 'f');
    root = insertIntervalTree(root, 5, 20, 'g');
    console.assert(JSON.stringify(root)
        == '[[15,20,40,"a"],[[10,30,30,"b"],[[10,30,30,"c"],[[5,20,20,"g"],null,null],null],[[12,15,15,"d"],null,null]],[[17,21,40,"e"],null,[[30,40,40,"f"],null,null]]]');
    console.assert(JSON.stringify(searchIntervalTree(root, 0, 46))
        == JSON.stringify(["a", "b", "c", "g", "d", "e", "f"]));
    console.assert(JSON.stringify(searchIntervalTree(root, 0, 2))
        == JSON.stringify([]));
    console.assert(JSON.stringify(searchIntervalTree(root, 0, 5))
        == JSON.stringify([]));
    console.assert(JSON.stringify(searchIntervalTree(root, 40, 45))
        == JSON.stringify([]));
    console.assert(JSON.stringify(searchIntervalTree(root, 39, 40))
        == JSON.stringify(['f']));
    console.assert(JSON.stringify(searchIntervalTree(root, 20, 39))
        == JSON.stringify(["b", "c", "e", "f"]));
    console.assert(JSON.stringify(searchIntervalTree(root, 0, 7))
        == JSON.stringify(['g']));
    console.assert(JSON.stringify(searchIntervalTree(root, 0, 10))
        == JSON.stringify(["g"]));
    console.assert(JSON.stringify(searchIntervalTree(root, 0, 14))
        == JSON.stringify(["b", "c", "g", "d"]));
    var rt = null;
    console.assert(searchRangeTree(rt, 2, 5, 5, 6) == false);
    rt = insertRangeTree(rt, 4, 2, 8, 4, 'a');
    rt = insertRangeTree(rt, 2, 5, 5, 6, 'b');
    console.assert(searchRangeTree(rt, 2, 5, 5, 6) == true);
    console.assert(searchRangeTree(rt, 0, 0, 100, 100) == true);
    console.assert(searchRangeTree(rt, 4, 2, 8, 4) == true);
    console.assert(searchRangeTree(rt, 6, 5, 10, 6) == false);
    console.assert(searchRangeTree(rt, 0, 0, 1, 1) == false);
})();



