// Created using Cozy: github.com/uwplse/cozy
function Rectangle(ax1, ay1, ax2, ay2) {
    this.ax1 = ax1;
    this.ay1 = ay1;
    this.ax2 = ax2;
    this.ay2 = ay2;
    this._left7 = undefined;
    this._right8 = undefined;
    this._parent9 = undefined;
    this._min_ax12 = undefined;
    this._min_ay13 = undefined;
    this._max_ay24 = undefined;
    this._height10 = undefined;
}
function RectangleHolder() {
    this.my_size = 0;
    (this)._root1 = null;
}
RectangleHolder.prototype.size = function () {
    return this.my_size;
};
RectangleHolder.prototype.add = function (x) {
    ++this.my_size;
    var _idx69 = (x).ax2;
    (x)._left7 = null;
    (x)._right8 = null;
    (x)._min_ax12 = (x).ax1;
    (x)._min_ay13 = (x).ay1;
    (x)._max_ay24 = (x).ay2;
    (x)._height10 = 0;
    var _previous70 = null;
    var _current71 = (this)._root1;
    var _is_left72 = false;
    while (!((_current71) == null)) {
        _previous70 = _current71;
        if ((_idx69) < ((_current71).ax2)) {
            _current71 = (_current71)._left7;
            _is_left72 = true;
        } else {
            _current71 = (_current71)._right8;
            _is_left72 = false;
        }
    }
    if ((_previous70) == null) {
        (this)._root1 = x;
    } else {
        (x)._parent9 = _previous70;
        if (_is_left72) {
            (_previous70)._left7 = x;
        } else {
            (_previous70)._right8 = x;
        }
    }
    var _cursor73 = (x)._parent9;
    var _changed74 = true;
    while ((_changed74) && (!((_cursor73) == (null)))) {
        var _old__min_ax1275 = (_cursor73)._min_ax12;
        var _old__min_ay1376 = (_cursor73)._min_ay13;
        var _old__max_ay2477 = (_cursor73)._max_ay24;
        var _old_height78 = (_cursor73)._height10;
        /* _min_ax12 is min of ax1 */
        var _augval79 = (_cursor73).ax1;
        var _child80 = (_cursor73)._left7;
        if (!((_child80) == null)) {
            var _val81 = (_child80)._min_ax12;
            _augval79 = ((_augval79) < (_val81)) ? (_augval79) : (_val81);
        }
        var _child82 = (_cursor73)._right8;
        if (!((_child82) == null)) {
            var _val83 = (_child82)._min_ax12;
            _augval79 = ((_augval79) < (_val83)) ? (_augval79) : (_val83);
        }
        (_cursor73)._min_ax12 = _augval79;
        /* _min_ay13 is min of ay1 */
        var _augval84 = (_cursor73).ay1;
        var _child85 = (_cursor73)._left7;
        if (!((_child85) == null)) {
            var _val86 = (_child85)._min_ay13;
            _augval84 = ((_augval84) < (_val86)) ? (_augval84) : (_val86);
        }
        var _child87 = (_cursor73)._right8;
        if (!((_child87) == null)) {
            var _val88 = (_child87)._min_ay13;
            _augval84 = ((_augval84) < (_val88)) ? (_augval84) : (_val88);
        }
        (_cursor73)._min_ay13 = _augval84;
        /* _max_ay24 is max of ay2 */
        var _augval89 = (_cursor73).ay2;
        var _child90 = (_cursor73)._left7;
        if (!((_child90) == null)) {
            var _val91 = (_child90)._max_ay24;
            _augval89 = ((_augval89) < (_val91)) ? (_val91) : (_augval89);
        }
        var _child92 = (_cursor73)._right8;
        if (!((_child92) == null)) {
            var _val93 = (_child92)._max_ay24;
            _augval89 = ((_augval89) < (_val93)) ? (_val93) : (_augval89);
        }
        (_cursor73)._max_ay24 = _augval89;
        (_cursor73)._height10 = 1 + ((((((_cursor73)._left7) == null) ? (-1) : (((_cursor73)._left7)._height10)) > ((((_cursor73)._right8) == null) ? (-1) : (((_cursor73)._right8)._height10))) ? ((((_cursor73)._left7) == null) ? (-1) : (((_cursor73)._left7)._height10)) : ((((_cursor73)._right8) == null) ? (-1) : (((_cursor73)._right8)._height10)));
        _changed74 = false;
        _changed74 = (_changed74) || (!((_old__min_ax1275) == ((_cursor73)._min_ax12)));
        _changed74 = (_changed74) || (!((_old__min_ay1376) == ((_cursor73)._min_ay13)));
        _changed74 = (_changed74) || (!((_old__max_ay2477) == ((_cursor73)._max_ay24)));
        _changed74 = (_changed74) || (!((_old_height78) == ((_cursor73)._height10)));
        _cursor73 = (_cursor73)._parent9;
    }
    /* rebalance AVL tree */
    var _cursor94 = x;
    var _imbalance95;
    while (!(((_cursor94)._parent9) == null)) {
        _cursor94 = (_cursor94)._parent9;
        (_cursor94)._height10 = 1 + ((((((_cursor94)._left7) == null) ? (-1) : (((_cursor94)._left7)._height10)) > ((((_cursor94)._right8) == null) ? (-1) : (((_cursor94)._right8)._height10))) ? ((((_cursor94)._left7) == null) ? (-1) : (((_cursor94)._left7)._height10)) : ((((_cursor94)._right8) == null) ? (-1) : (((_cursor94)._right8)._height10)));
        _imbalance95 = ((((_cursor94)._left7) == null) ? (-1) : (((_cursor94)._left7)._height10)) - ((((_cursor94)._right8) == null) ? (-1) : (((_cursor94)._right8)._height10));
        if ((_imbalance95) > (1)) {
            if ((((((_cursor94)._left7)._left7) == null) ? (-1) : ((((_cursor94)._left7)._left7)._height10)) < (((((_cursor94)._left7)._right8) == null) ? (-1) : ((((_cursor94)._left7)._right8)._height10))) {
                /* rotate ((_cursor94)._left7)._right8 */
                var _a96 = (_cursor94)._left7;
                var _b97 = (_a96)._right8;
                var _c98 = (_b97)._left7;
                /* replace _a96 with _b97 in (_a96)._parent9 */
                if (!(((_a96)._parent9) == null)) {
                    if ((((_a96)._parent9)._left7) == (_a96)) {
                        ((_a96)._parent9)._left7 = _b97;
                    } else {
                        ((_a96)._parent9)._right8 = _b97;
                    }
                }
                if (!((_b97) == null)) {
                    (_b97)._parent9 = (_a96)._parent9;
                }
                /* replace _c98 with _a96 in _b97 */
                (_b97)._left7 = _a96;
                if (!((_a96) == null)) {
                    (_a96)._parent9 = _b97;
                }
                /* replace _b97 with _c98 in _a96 */
                (_a96)._right8 = _c98;
                if (!((_c98) == null)) {
                    (_c98)._parent9 = _a96;
                }
                /* _min_ax12 is min of ax1 */
                var _augval99 = (_a96).ax1;
                var _child100 = (_a96)._left7;
                if (!((_child100) == null)) {
                    var _val101 = (_child100)._min_ax12;
                    _augval99 = ((_augval99) < (_val101)) ? (_augval99) : (_val101);
                }
                var _child102 = (_a96)._right8;
                if (!((_child102) == null)) {
                    var _val103 = (_child102)._min_ax12;
                    _augval99 = ((_augval99) < (_val103)) ? (_augval99) : (_val103);
                }
                (_a96)._min_ax12 = _augval99;
                /* _min_ay13 is min of ay1 */
                var _augval104 = (_a96).ay1;
                var _child105 = (_a96)._left7;
                if (!((_child105) == null)) {
                    var _val106 = (_child105)._min_ay13;
                    _augval104 = ((_augval104) < (_val106)) ? (_augval104) : (_val106);
                }
                var _child107 = (_a96)._right8;
                if (!((_child107) == null)) {
                    var _val108 = (_child107)._min_ay13;
                    _augval104 = ((_augval104) < (_val108)) ? (_augval104) : (_val108);
                }
                (_a96)._min_ay13 = _augval104;
                /* _max_ay24 is max of ay2 */
                var _augval109 = (_a96).ay2;
                var _child110 = (_a96)._left7;
                if (!((_child110) == null)) {
                    var _val111 = (_child110)._max_ay24;
                    _augval109 = ((_augval109) < (_val111)) ? (_val111) : (_augval109);
                }
                var _child112 = (_a96)._right8;
                if (!((_child112) == null)) {
                    var _val113 = (_child112)._max_ay24;
                    _augval109 = ((_augval109) < (_val113)) ? (_val113) : (_augval109);
                }
                (_a96)._max_ay24 = _augval109;
                (_a96)._height10 = 1 + ((((((_a96)._left7) == null) ? (-1) : (((_a96)._left7)._height10)) > ((((_a96)._right8) == null) ? (-1) : (((_a96)._right8)._height10))) ? ((((_a96)._left7) == null) ? (-1) : (((_a96)._left7)._height10)) : ((((_a96)._right8) == null) ? (-1) : (((_a96)._right8)._height10)));
                /* _min_ax12 is min of ax1 */
                var _augval114 = (_b97).ax1;
                var _child115 = (_b97)._left7;
                if (!((_child115) == null)) {
                    var _val116 = (_child115)._min_ax12;
                    _augval114 = ((_augval114) < (_val116)) ? (_augval114) : (_val116);
                }
                var _child117 = (_b97)._right8;
                if (!((_child117) == null)) {
                    var _val118 = (_child117)._min_ax12;
                    _augval114 = ((_augval114) < (_val118)) ? (_augval114) : (_val118);
                }
                (_b97)._min_ax12 = _augval114;
                /* _min_ay13 is min of ay1 */
                var _augval119 = (_b97).ay1;
                var _child120 = (_b97)._left7;
                if (!((_child120) == null)) {
                    var _val121 = (_child120)._min_ay13;
                    _augval119 = ((_augval119) < (_val121)) ? (_augval119) : (_val121);
                }
                var _child122 = (_b97)._right8;
                if (!((_child122) == null)) {
                    var _val123 = (_child122)._min_ay13;
                    _augval119 = ((_augval119) < (_val123)) ? (_augval119) : (_val123);
                }
                (_b97)._min_ay13 = _augval119;
                /* _max_ay24 is max of ay2 */
                var _augval124 = (_b97).ay2;
                var _child125 = (_b97)._left7;
                if (!((_child125) == null)) {
                    var _val126 = (_child125)._max_ay24;
                    _augval124 = ((_augval124) < (_val126)) ? (_val126) : (_augval124);
                }
                var _child127 = (_b97)._right8;
                if (!((_child127) == null)) {
                    var _val128 = (_child127)._max_ay24;
                    _augval124 = ((_augval124) < (_val128)) ? (_val128) : (_augval124);
                }
                (_b97)._max_ay24 = _augval124;
                (_b97)._height10 = 1 + ((((((_b97)._left7) == null) ? (-1) : (((_b97)._left7)._height10)) > ((((_b97)._right8) == null) ? (-1) : (((_b97)._right8)._height10))) ? ((((_b97)._left7) == null) ? (-1) : (((_b97)._left7)._height10)) : ((((_b97)._right8) == null) ? (-1) : (((_b97)._right8)._height10)));
                if (!(((_b97)._parent9) == null)) {
                    /* _min_ax12 is min of ax1 */
                    var _augval129 = ((_b97)._parent9).ax1;
                    var _child130 = ((_b97)._parent9)._left7;
                    if (!((_child130) == null)) {
                        var _val131 = (_child130)._min_ax12;
                        _augval129 = ((_augval129) < (_val131)) ? (_augval129) : (_val131);
                    }
                    var _child132 = ((_b97)._parent9)._right8;
                    if (!((_child132) == null)) {
                        var _val133 = (_child132)._min_ax12;
                        _augval129 = ((_augval129) < (_val133)) ? (_augval129) : (_val133);
                    }
                    ((_b97)._parent9)._min_ax12 = _augval129;
                    /* _min_ay13 is min of ay1 */
                    var _augval134 = ((_b97)._parent9).ay1;
                    var _child135 = ((_b97)._parent9)._left7;
                    if (!((_child135) == null)) {
                        var _val136 = (_child135)._min_ay13;
                        _augval134 = ((_augval134) < (_val136)) ? (_augval134) : (_val136);
                    }
                    var _child137 = ((_b97)._parent9)._right8;
                    if (!((_child137) == null)) {
                        var _val138 = (_child137)._min_ay13;
                        _augval134 = ((_augval134) < (_val138)) ? (_augval134) : (_val138);
                    }
                    ((_b97)._parent9)._min_ay13 = _augval134;
                    /* _max_ay24 is max of ay2 */
                    var _augval139 = ((_b97)._parent9).ay2;
                    var _child140 = ((_b97)._parent9)._left7;
                    if (!((_child140) == null)) {
                        var _val141 = (_child140)._max_ay24;
                        _augval139 = ((_augval139) < (_val141)) ? (_val141) : (_augval139);
                    }
                    var _child142 = ((_b97)._parent9)._right8;
                    if (!((_child142) == null)) {
                        var _val143 = (_child142)._max_ay24;
                        _augval139 = ((_augval139) < (_val143)) ? (_val143) : (_augval139);
                    }
                    ((_b97)._parent9)._max_ay24 = _augval139;
                    ((_b97)._parent9)._height10 = 1 + (((((((_b97)._parent9)._left7) == null) ? (-1) : ((((_b97)._parent9)._left7)._height10)) > (((((_b97)._parent9)._right8) == null) ? (-1) : ((((_b97)._parent9)._right8)._height10))) ? (((((_b97)._parent9)._left7) == null) ? (-1) : ((((_b97)._parent9)._left7)._height10)) : (((((_b97)._parent9)._right8) == null) ? (-1) : ((((_b97)._parent9)._right8)._height10)));
                } else {
                    (this)._root1 = _b97;
                }
            }
            /* rotate (_cursor94)._left7 */
            var _a144 = _cursor94;
            var _b145 = (_a144)._left7;
            var _c146 = (_b145)._right8;
            /* replace _a144 with _b145 in (_a144)._parent9 */
            if (!(((_a144)._parent9) == null)) {
                if ((((_a144)._parent9)._left7) == (_a144)) {
                    ((_a144)._parent9)._left7 = _b145;
                } else {
                    ((_a144)._parent9)._right8 = _b145;
                }
            }
            if (!((_b145) == null)) {
                (_b145)._parent9 = (_a144)._parent9;
            }
            /* replace _c146 with _a144 in _b145 */
            (_b145)._right8 = _a144;
            if (!((_a144) == null)) {
                (_a144)._parent9 = _b145;
            }
            /* replace _b145 with _c146 in _a144 */
            (_a144)._left7 = _c146;
            if (!((_c146) == null)) {
                (_c146)._parent9 = _a144;
            }
            /* _min_ax12 is min of ax1 */
            var _augval147 = (_a144).ax1;
            var _child148 = (_a144)._left7;
            if (!((_child148) == null)) {
                var _val149 = (_child148)._min_ax12;
                _augval147 = ((_augval147) < (_val149)) ? (_augval147) : (_val149);
            }
            var _child150 = (_a144)._right8;
            if (!((_child150) == null)) {
                var _val151 = (_child150)._min_ax12;
                _augval147 = ((_augval147) < (_val151)) ? (_augval147) : (_val151);
            }
            (_a144)._min_ax12 = _augval147;
            /* _min_ay13 is min of ay1 */
            var _augval152 = (_a144).ay1;
            var _child153 = (_a144)._left7;
            if (!((_child153) == null)) {
                var _val154 = (_child153)._min_ay13;
                _augval152 = ((_augval152) < (_val154)) ? (_augval152) : (_val154);
            }
            var _child155 = (_a144)._right8;
            if (!((_child155) == null)) {
                var _val156 = (_child155)._min_ay13;
                _augval152 = ((_augval152) < (_val156)) ? (_augval152) : (_val156);
            }
            (_a144)._min_ay13 = _augval152;
            /* _max_ay24 is max of ay2 */
            var _augval157 = (_a144).ay2;
            var _child158 = (_a144)._left7;
            if (!((_child158) == null)) {
                var _val159 = (_child158)._max_ay24;
                _augval157 = ((_augval157) < (_val159)) ? (_val159) : (_augval157);
            }
            var _child160 = (_a144)._right8;
            if (!((_child160) == null)) {
                var _val161 = (_child160)._max_ay24;
                _augval157 = ((_augval157) < (_val161)) ? (_val161) : (_augval157);
            }
            (_a144)._max_ay24 = _augval157;
            (_a144)._height10 = 1 + ((((((_a144)._left7) == null) ? (-1) : (((_a144)._left7)._height10)) > ((((_a144)._right8) == null) ? (-1) : (((_a144)._right8)._height10))) ? ((((_a144)._left7) == null) ? (-1) : (((_a144)._left7)._height10)) : ((((_a144)._right8) == null) ? (-1) : (((_a144)._right8)._height10)));
            /* _min_ax12 is min of ax1 */
            var _augval162 = (_b145).ax1;
            var _child163 = (_b145)._left7;
            if (!((_child163) == null)) {
                var _val164 = (_child163)._min_ax12;
                _augval162 = ((_augval162) < (_val164)) ? (_augval162) : (_val164);
            }
            var _child165 = (_b145)._right8;
            if (!((_child165) == null)) {
                var _val166 = (_child165)._min_ax12;
                _augval162 = ((_augval162) < (_val166)) ? (_augval162) : (_val166);
            }
            (_b145)._min_ax12 = _augval162;
            /* _min_ay13 is min of ay1 */
            var _augval167 = (_b145).ay1;
            var _child168 = (_b145)._left7;
            if (!((_child168) == null)) {
                var _val169 = (_child168)._min_ay13;
                _augval167 = ((_augval167) < (_val169)) ? (_augval167) : (_val169);
            }
            var _child170 = (_b145)._right8;
            if (!((_child170) == null)) {
                var _val171 = (_child170)._min_ay13;
                _augval167 = ((_augval167) < (_val171)) ? (_augval167) : (_val171);
            }
            (_b145)._min_ay13 = _augval167;
            /* _max_ay24 is max of ay2 */
            var _augval172 = (_b145).ay2;
            var _child173 = (_b145)._left7;
            if (!((_child173) == null)) {
                var _val174 = (_child173)._max_ay24;
                _augval172 = ((_augval172) < (_val174)) ? (_val174) : (_augval172);
            }
            var _child175 = (_b145)._right8;
            if (!((_child175) == null)) {
                var _val176 = (_child175)._max_ay24;
                _augval172 = ((_augval172) < (_val176)) ? (_val176) : (_augval172);
            }
            (_b145)._max_ay24 = _augval172;
            (_b145)._height10 = 1 + ((((((_b145)._left7) == null) ? (-1) : (((_b145)._left7)._height10)) > ((((_b145)._right8) == null) ? (-1) : (((_b145)._right8)._height10))) ? ((((_b145)._left7) == null) ? (-1) : (((_b145)._left7)._height10)) : ((((_b145)._right8) == null) ? (-1) : (((_b145)._right8)._height10)));
            if (!(((_b145)._parent9) == null)) {
                /* _min_ax12 is min of ax1 */
                var _augval177 = ((_b145)._parent9).ax1;
                var _child178 = ((_b145)._parent9)._left7;
                if (!((_child178) == null)) {
                    var _val179 = (_child178)._min_ax12;
                    _augval177 = ((_augval177) < (_val179)) ? (_augval177) : (_val179);
                }
                var _child180 = ((_b145)._parent9)._right8;
                if (!((_child180) == null)) {
                    var _val181 = (_child180)._min_ax12;
                    _augval177 = ((_augval177) < (_val181)) ? (_augval177) : (_val181);
                }
                ((_b145)._parent9)._min_ax12 = _augval177;
                /* _min_ay13 is min of ay1 */
                var _augval182 = ((_b145)._parent9).ay1;
                var _child183 = ((_b145)._parent9)._left7;
                if (!((_child183) == null)) {
                    var _val184 = (_child183)._min_ay13;
                    _augval182 = ((_augval182) < (_val184)) ? (_augval182) : (_val184);
                }
                var _child185 = ((_b145)._parent9)._right8;
                if (!((_child185) == null)) {
                    var _val186 = (_child185)._min_ay13;
                    _augval182 = ((_augval182) < (_val186)) ? (_augval182) : (_val186);
                }
                ((_b145)._parent9)._min_ay13 = _augval182;
                /* _max_ay24 is max of ay2 */
                var _augval187 = ((_b145)._parent9).ay2;
                var _child188 = ((_b145)._parent9)._left7;
                if (!((_child188) == null)) {
                    var _val189 = (_child188)._max_ay24;
                    _augval187 = ((_augval187) < (_val189)) ? (_val189) : (_augval187);
                }
                var _child190 = ((_b145)._parent9)._right8;
                if (!((_child190) == null)) {
                    var _val191 = (_child190)._max_ay24;
                    _augval187 = ((_augval187) < (_val191)) ? (_val191) : (_augval187);
                }
                ((_b145)._parent9)._max_ay24 = _augval187;
                ((_b145)._parent9)._height10 = 1 + (((((((_b145)._parent9)._left7) == null) ? (-1) : ((((_b145)._parent9)._left7)._height10)) > (((((_b145)._parent9)._right8) == null) ? (-1) : ((((_b145)._parent9)._right8)._height10))) ? (((((_b145)._parent9)._left7) == null) ? (-1) : ((((_b145)._parent9)._left7)._height10)) : (((((_b145)._parent9)._right8) == null) ? (-1) : ((((_b145)._parent9)._right8)._height10)));
            } else {
                (this)._root1 = _b145;
            }
            _cursor94 = (_cursor94)._parent9;
        } else if ((_imbalance95) < (-1)) {
            if ((((((_cursor94)._right8)._left7) == null) ? (-1) : ((((_cursor94)._right8)._left7)._height10)) > (((((_cursor94)._right8)._right8) == null) ? (-1) : ((((_cursor94)._right8)._right8)._height10))) {
                /* rotate ((_cursor94)._right8)._left7 */
                var _a192 = (_cursor94)._right8;
                var _b193 = (_a192)._left7;
                var _c194 = (_b193)._right8;
                /* replace _a192 with _b193 in (_a192)._parent9 */
                if (!(((_a192)._parent9) == null)) {
                    if ((((_a192)._parent9)._left7) == (_a192)) {
                        ((_a192)._parent9)._left7 = _b193;
                    } else {
                        ((_a192)._parent9)._right8 = _b193;
                    }
                }
                if (!((_b193) == null)) {
                    (_b193)._parent9 = (_a192)._parent9;
                }
                /* replace _c194 with _a192 in _b193 */
                (_b193)._right8 = _a192;
                if (!((_a192) == null)) {
                    (_a192)._parent9 = _b193;
                }
                /* replace _b193 with _c194 in _a192 */
                (_a192)._left7 = _c194;
                if (!((_c194) == null)) {
                    (_c194)._parent9 = _a192;
                }
                /* _min_ax12 is min of ax1 */
                var _augval195 = (_a192).ax1;
                var _child196 = (_a192)._left7;
                if (!((_child196) == null)) {
                    var _val197 = (_child196)._min_ax12;
                    _augval195 = ((_augval195) < (_val197)) ? (_augval195) : (_val197);
                }
                var _child198 = (_a192)._right8;
                if (!((_child198) == null)) {
                    var _val199 = (_child198)._min_ax12;
                    _augval195 = ((_augval195) < (_val199)) ? (_augval195) : (_val199);
                }
                (_a192)._min_ax12 = _augval195;
                /* _min_ay13 is min of ay1 */
                var _augval200 = (_a192).ay1;
                var _child201 = (_a192)._left7;
                if (!((_child201) == null)) {
                    var _val202 = (_child201)._min_ay13;
                    _augval200 = ((_augval200) < (_val202)) ? (_augval200) : (_val202);
                }
                var _child203 = (_a192)._right8;
                if (!((_child203) == null)) {
                    var _val204 = (_child203)._min_ay13;
                    _augval200 = ((_augval200) < (_val204)) ? (_augval200) : (_val204);
                }
                (_a192)._min_ay13 = _augval200;
                /* _max_ay24 is max of ay2 */
                var _augval205 = (_a192).ay2;
                var _child206 = (_a192)._left7;
                if (!((_child206) == null)) {
                    var _val207 = (_child206)._max_ay24;
                    _augval205 = ((_augval205) < (_val207)) ? (_val207) : (_augval205);
                }
                var _child208 = (_a192)._right8;
                if (!((_child208) == null)) {
                    var _val209 = (_child208)._max_ay24;
                    _augval205 = ((_augval205) < (_val209)) ? (_val209) : (_augval205);
                }
                (_a192)._max_ay24 = _augval205;
                (_a192)._height10 = 1 + ((((((_a192)._left7) == null) ? (-1) : (((_a192)._left7)._height10)) > ((((_a192)._right8) == null) ? (-1) : (((_a192)._right8)._height10))) ? ((((_a192)._left7) == null) ? (-1) : (((_a192)._left7)._height10)) : ((((_a192)._right8) == null) ? (-1) : (((_a192)._right8)._height10)));
                /* _min_ax12 is min of ax1 */
                var _augval210 = (_b193).ax1;
                var _child211 = (_b193)._left7;
                if (!((_child211) == null)) {
                    var _val212 = (_child211)._min_ax12;
                    _augval210 = ((_augval210) < (_val212)) ? (_augval210) : (_val212);
                }
                var _child213 = (_b193)._right8;
                if (!((_child213) == null)) {
                    var _val214 = (_child213)._min_ax12;
                    _augval210 = ((_augval210) < (_val214)) ? (_augval210) : (_val214);
                }
                (_b193)._min_ax12 = _augval210;
                /* _min_ay13 is min of ay1 */
                var _augval215 = (_b193).ay1;
                var _child216 = (_b193)._left7;
                if (!((_child216) == null)) {
                    var _val217 = (_child216)._min_ay13;
                    _augval215 = ((_augval215) < (_val217)) ? (_augval215) : (_val217);
                }
                var _child218 = (_b193)._right8;
                if (!((_child218) == null)) {
                    var _val219 = (_child218)._min_ay13;
                    _augval215 = ((_augval215) < (_val219)) ? (_augval215) : (_val219);
                }
                (_b193)._min_ay13 = _augval215;
                /* _max_ay24 is max of ay2 */
                var _augval220 = (_b193).ay2;
                var _child221 = (_b193)._left7;
                if (!((_child221) == null)) {
                    var _val222 = (_child221)._max_ay24;
                    _augval220 = ((_augval220) < (_val222)) ? (_val222) : (_augval220);
                }
                var _child223 = (_b193)._right8;
                if (!((_child223) == null)) {
                    var _val224 = (_child223)._max_ay24;
                    _augval220 = ((_augval220) < (_val224)) ? (_val224) : (_augval220);
                }
                (_b193)._max_ay24 = _augval220;
                (_b193)._height10 = 1 + ((((((_b193)._left7) == null) ? (-1) : (((_b193)._left7)._height10)) > ((((_b193)._right8) == null) ? (-1) : (((_b193)._right8)._height10))) ? ((((_b193)._left7) == null) ? (-1) : (((_b193)._left7)._height10)) : ((((_b193)._right8) == null) ? (-1) : (((_b193)._right8)._height10)));
                if (!(((_b193)._parent9) == null)) {
                    /* _min_ax12 is min of ax1 */
                    var _augval225 = ((_b193)._parent9).ax1;
                    var _child226 = ((_b193)._parent9)._left7;
                    if (!((_child226) == null)) {
                        var _val227 = (_child226)._min_ax12;
                        _augval225 = ((_augval225) < (_val227)) ? (_augval225) : (_val227);
                    }
                    var _child228 = ((_b193)._parent9)._right8;
                    if (!((_child228) == null)) {
                        var _val229 = (_child228)._min_ax12;
                        _augval225 = ((_augval225) < (_val229)) ? (_augval225) : (_val229);
                    }
                    ((_b193)._parent9)._min_ax12 = _augval225;
                    /* _min_ay13 is min of ay1 */
                    var _augval230 = ((_b193)._parent9).ay1;
                    var _child231 = ((_b193)._parent9)._left7;
                    if (!((_child231) == null)) {
                        var _val232 = (_child231)._min_ay13;
                        _augval230 = ((_augval230) < (_val232)) ? (_augval230) : (_val232);
                    }
                    var _child233 = ((_b193)._parent9)._right8;
                    if (!((_child233) == null)) {
                        var _val234 = (_child233)._min_ay13;
                        _augval230 = ((_augval230) < (_val234)) ? (_augval230) : (_val234);
                    }
                    ((_b193)._parent9)._min_ay13 = _augval230;
                    /* _max_ay24 is max of ay2 */
                    var _augval235 = ((_b193)._parent9).ay2;
                    var _child236 = ((_b193)._parent9)._left7;
                    if (!((_child236) == null)) {
                        var _val237 = (_child236)._max_ay24;
                        _augval235 = ((_augval235) < (_val237)) ? (_val237) : (_augval235);
                    }
                    var _child238 = ((_b193)._parent9)._right8;
                    if (!((_child238) == null)) {
                        var _val239 = (_child238)._max_ay24;
                        _augval235 = ((_augval235) < (_val239)) ? (_val239) : (_augval235);
                    }
                    ((_b193)._parent9)._max_ay24 = _augval235;
                    ((_b193)._parent9)._height10 = 1 + (((((((_b193)._parent9)._left7) == null) ? (-1) : ((((_b193)._parent9)._left7)._height10)) > (((((_b193)._parent9)._right8) == null) ? (-1) : ((((_b193)._parent9)._right8)._height10))) ? (((((_b193)._parent9)._left7) == null) ? (-1) : ((((_b193)._parent9)._left7)._height10)) : (((((_b193)._parent9)._right8) == null) ? (-1) : ((((_b193)._parent9)._right8)._height10)));
                } else {
                    (this)._root1 = _b193;
                }
            }
            /* rotate (_cursor94)._right8 */
            var _a240 = _cursor94;
            var _b241 = (_a240)._right8;
            var _c242 = (_b241)._left7;
            /* replace _a240 with _b241 in (_a240)._parent9 */
            if (!(((_a240)._parent9) == null)) {
                if ((((_a240)._parent9)._left7) == (_a240)) {
                    ((_a240)._parent9)._left7 = _b241;
                } else {
                    ((_a240)._parent9)._right8 = _b241;
                }
            }
            if (!((_b241) == null)) {
                (_b241)._parent9 = (_a240)._parent9;
            }
            /* replace _c242 with _a240 in _b241 */
            (_b241)._left7 = _a240;
            if (!((_a240) == null)) {
                (_a240)._parent9 = _b241;
            }
            /* replace _b241 with _c242 in _a240 */
            (_a240)._right8 = _c242;
            if (!((_c242) == null)) {
                (_c242)._parent9 = _a240;
            }
            /* _min_ax12 is min of ax1 */
            var _augval243 = (_a240).ax1;
            var _child244 = (_a240)._left7;
            if (!((_child244) == null)) {
                var _val245 = (_child244)._min_ax12;
                _augval243 = ((_augval243) < (_val245)) ? (_augval243) : (_val245);
            }
            var _child246 = (_a240)._right8;
            if (!((_child246) == null)) {
                var _val247 = (_child246)._min_ax12;
                _augval243 = ((_augval243) < (_val247)) ? (_augval243) : (_val247);
            }
            (_a240)._min_ax12 = _augval243;
            /* _min_ay13 is min of ay1 */
            var _augval248 = (_a240).ay1;
            var _child249 = (_a240)._left7;
            if (!((_child249) == null)) {
                var _val250 = (_child249)._min_ay13;
                _augval248 = ((_augval248) < (_val250)) ? (_augval248) : (_val250);
            }
            var _child251 = (_a240)._right8;
            if (!((_child251) == null)) {
                var _val252 = (_child251)._min_ay13;
                _augval248 = ((_augval248) < (_val252)) ? (_augval248) : (_val252);
            }
            (_a240)._min_ay13 = _augval248;
            /* _max_ay24 is max of ay2 */
            var _augval253 = (_a240).ay2;
            var _child254 = (_a240)._left7;
            if (!((_child254) == null)) {
                var _val255 = (_child254)._max_ay24;
                _augval253 = ((_augval253) < (_val255)) ? (_val255) : (_augval253);
            }
            var _child256 = (_a240)._right8;
            if (!((_child256) == null)) {
                var _val257 = (_child256)._max_ay24;
                _augval253 = ((_augval253) < (_val257)) ? (_val257) : (_augval253);
            }
            (_a240)._max_ay24 = _augval253;
            (_a240)._height10 = 1 + ((((((_a240)._left7) == null) ? (-1) : (((_a240)._left7)._height10)) > ((((_a240)._right8) == null) ? (-1) : (((_a240)._right8)._height10))) ? ((((_a240)._left7) == null) ? (-1) : (((_a240)._left7)._height10)) : ((((_a240)._right8) == null) ? (-1) : (((_a240)._right8)._height10)));
            /* _min_ax12 is min of ax1 */
            var _augval258 = (_b241).ax1;
            var _child259 = (_b241)._left7;
            if (!((_child259) == null)) {
                var _val260 = (_child259)._min_ax12;
                _augval258 = ((_augval258) < (_val260)) ? (_augval258) : (_val260);
            }
            var _child261 = (_b241)._right8;
            if (!((_child261) == null)) {
                var _val262 = (_child261)._min_ax12;
                _augval258 = ((_augval258) < (_val262)) ? (_augval258) : (_val262);
            }
            (_b241)._min_ax12 = _augval258;
            /* _min_ay13 is min of ay1 */
            var _augval263 = (_b241).ay1;
            var _child264 = (_b241)._left7;
            if (!((_child264) == null)) {
                var _val265 = (_child264)._min_ay13;
                _augval263 = ((_augval263) < (_val265)) ? (_augval263) : (_val265);
            }
            var _child266 = (_b241)._right8;
            if (!((_child266) == null)) {
                var _val267 = (_child266)._min_ay13;
                _augval263 = ((_augval263) < (_val267)) ? (_augval263) : (_val267);
            }
            (_b241)._min_ay13 = _augval263;
            /* _max_ay24 is max of ay2 */
            var _augval268 = (_b241).ay2;
            var _child269 = (_b241)._left7;
            if (!((_child269) == null)) {
                var _val270 = (_child269)._max_ay24;
                _augval268 = ((_augval268) < (_val270)) ? (_val270) : (_augval268);
            }
            var _child271 = (_b241)._right8;
            if (!((_child271) == null)) {
                var _val272 = (_child271)._max_ay24;
                _augval268 = ((_augval268) < (_val272)) ? (_val272) : (_augval268);
            }
            (_b241)._max_ay24 = _augval268;
            (_b241)._height10 = 1 + ((((((_b241)._left7) == null) ? (-1) : (((_b241)._left7)._height10)) > ((((_b241)._right8) == null) ? (-1) : (((_b241)._right8)._height10))) ? ((((_b241)._left7) == null) ? (-1) : (((_b241)._left7)._height10)) : ((((_b241)._right8) == null) ? (-1) : (((_b241)._right8)._height10)));
            if (!(((_b241)._parent9) == null)) {
                /* _min_ax12 is min of ax1 */
                var _augval273 = ((_b241)._parent9).ax1;
                var _child274 = ((_b241)._parent9)._left7;
                if (!((_child274) == null)) {
                    var _val275 = (_child274)._min_ax12;
                    _augval273 = ((_augval273) < (_val275)) ? (_augval273) : (_val275);
                }
                var _child276 = ((_b241)._parent9)._right8;
                if (!((_child276) == null)) {
                    var _val277 = (_child276)._min_ax12;
                    _augval273 = ((_augval273) < (_val277)) ? (_augval273) : (_val277);
                }
                ((_b241)._parent9)._min_ax12 = _augval273;
                /* _min_ay13 is min of ay1 */
                var _augval278 = ((_b241)._parent9).ay1;
                var _child279 = ((_b241)._parent9)._left7;
                if (!((_child279) == null)) {
                    var _val280 = (_child279)._min_ay13;
                    _augval278 = ((_augval278) < (_val280)) ? (_augval278) : (_val280);
                }
                var _child281 = ((_b241)._parent9)._right8;
                if (!((_child281) == null)) {
                    var _val282 = (_child281)._min_ay13;
                    _augval278 = ((_augval278) < (_val282)) ? (_augval278) : (_val282);
                }
                ((_b241)._parent9)._min_ay13 = _augval278;
                /* _max_ay24 is max of ay2 */
                var _augval283 = ((_b241)._parent9).ay2;
                var _child284 = ((_b241)._parent9)._left7;
                if (!((_child284) == null)) {
                    var _val285 = (_child284)._max_ay24;
                    _augval283 = ((_augval283) < (_val285)) ? (_val285) : (_augval283);
                }
                var _child286 = ((_b241)._parent9)._right8;
                if (!((_child286) == null)) {
                    var _val287 = (_child286)._max_ay24;
                    _augval283 = ((_augval283) < (_val287)) ? (_val287) : (_augval283);
                }
                ((_b241)._parent9)._max_ay24 = _augval283;
                ((_b241)._parent9)._height10 = 1 + (((((((_b241)._parent9)._left7) == null) ? (-1) : ((((_b241)._parent9)._left7)._height10)) > (((((_b241)._parent9)._right8) == null) ? (-1) : ((((_b241)._parent9)._right8)._height10))) ? (((((_b241)._parent9)._left7) == null) ? (-1) : ((((_b241)._parent9)._left7)._height10)) : (((((_b241)._parent9)._right8) == null) ? (-1) : ((((_b241)._parent9)._right8)._height10)));
            } else {
                (this)._root1 = _b241;
            }
            _cursor94 = (_cursor94)._parent9;
        }
    }
};
RectangleHolder.prototype.remove = function (x) {
    --this.my_size;
    var _parent288 = (x)._parent9;
    var _left289 = (x)._left7;
    var _right290 = (x)._right8;
    var _new_x291;
    if (((_left289) == null) && ((_right290) == null)) {
        _new_x291 = null;
        /* replace x with _new_x291 in _parent288 */
        if (!((_parent288) == null)) {
            if (((_parent288)._left7) == (x)) {
                (_parent288)._left7 = _new_x291;
            } else {
                (_parent288)._right8 = _new_x291;
            }
        }
        if (!((_new_x291) == null)) {
            (_new_x291)._parent9 = _parent288;
        }
    } else if ((!((_left289) == null)) && ((_right290) == null)) {
        _new_x291 = _left289;
        /* replace x with _new_x291 in _parent288 */
        if (!((_parent288) == null)) {
            if (((_parent288)._left7) == (x)) {
                (_parent288)._left7 = _new_x291;
            } else {
                (_parent288)._right8 = _new_x291;
            }
        }
        if (!((_new_x291) == null)) {
            (_new_x291)._parent9 = _parent288;
        }
    } else if (((_left289) == null) && (!((_right290) == null))) {
        _new_x291 = _right290;
        /* replace x with _new_x291 in _parent288 */
        if (!((_parent288) == null)) {
            if (((_parent288)._left7) == (x)) {
                (_parent288)._left7 = _new_x291;
            } else {
                (_parent288)._right8 = _new_x291;
            }
        }
        if (!((_new_x291) == null)) {
            (_new_x291)._parent9 = _parent288;
        }
    } else {
        var _root292 = (x)._right8;
        var _x293 = _root292;
        var _descend294 = true;
        var _from_left295 = true;
        while (true) {
            if ((_x293) == null) {
                _x293 = null;
                break;
            }
            if (_descend294) {
                /* too small? */
                if (false) {
                    if ((!(((_x293)._right8) == null)) && (true)) {
                        if ((_x293) == (_root292)) {
                            _root292 = (_x293)._right8;
                        }
                        _x293 = (_x293)._right8;
                    } else if ((_x293) == (_root292)) {
                        _x293 = null;
                        break;
                    } else {
                        _descend294 = false;
                        _from_left295 = (!(((_x293)._parent9) == null)) && ((_x293) == (((_x293)._parent9)._left7));
                        _x293 = (_x293)._parent9;
                    }
                } else if ((!(((_x293)._left7) == null)) && (true)) {
                    _x293 = (_x293)._left7;
                    /* too large? */
                } else if (false) {
                    if ((_x293) == (_root292)) {
                        _x293 = null;
                        break;
                    } else {
                        _descend294 = false;
                        _from_left295 = (!(((_x293)._parent9) == null)) && ((_x293) == (((_x293)._parent9)._left7));
                        _x293 = (_x293)._parent9;
                    }
                    /* node ok? */
                } else if (true) {
                    break;
                } else if ((_x293) == (_root292)) {
                    _root292 = (_x293)._right8;
                    _x293 = (_x293)._right8;
                } else {
                    if ((!(((_x293)._right8) == null)) && (true)) {
                        if ((_x293) == (_root292)) {
                            _root292 = (_x293)._right8;
                        }
                        _x293 = (_x293)._right8;
                    } else {
                        _descend294 = false;
                        _from_left295 = (!(((_x293)._parent9) == null)) && ((_x293) == (((_x293)._parent9)._left7));
                        _x293 = (_x293)._parent9;
                    }
                }
            } else if (_from_left295) {
                if (false) {
                    _x293 = null;
                    break;
                } else if (true) {
                    break;
                } else if ((!(((_x293)._right8) == null)) && (true)) {
                    _descend294 = true;
                    if ((_x293) == (_root292)) {
                        _root292 = (_x293)._right8;
                    }
                    _x293 = (_x293)._right8;
                } else if ((_x293) == (_root292)) {
                    _x293 = null;
                    break;
                } else {
                    _descend294 = false;
                    _from_left295 = (!(((_x293)._parent9) == null)) && ((_x293) == (((_x293)._parent9)._left7));
                    _x293 = (_x293)._parent9;
                }
            } else {
                if ((_x293) == (_root292)) {
                    _x293 = null;
                    break;
                } else {
                    _descend294 = false;
                    _from_left295 = (!(((_x293)._parent9) == null)) && ((_x293) == (((_x293)._parent9)._left7));
                    _x293 = (_x293)._parent9;
                }
            }
        }
        _new_x291 = _x293;
        var _mp296 = (_x293)._parent9;
        var _mr297 = (_x293)._right8;
        /* replace _x293 with _mr297 in _mp296 */
        if (!((_mp296) == null)) {
            if (((_mp296)._left7) == (_x293)) {
                (_mp296)._left7 = _mr297;
            } else {
                (_mp296)._right8 = _mr297;
            }
        }
        if (!((_mr297) == null)) {
            (_mr297)._parent9 = _mp296;
        }
        /* replace x with _x293 in _parent288 */
        if (!((_parent288) == null)) {
            if (((_parent288)._left7) == (x)) {
                (_parent288)._left7 = _x293;
            } else {
                (_parent288)._right8 = _x293;
            }
        }
        if (!((_x293) == null)) {
            (_x293)._parent9 = _parent288;
        }
        /* replace null with _left289 in _x293 */
        (_x293)._left7 = _left289;
        if (!((_left289) == null)) {
            (_left289)._parent9 = _x293;
        }
        /* replace _mr297 with (x)._right8 in _x293 */
        (_x293)._right8 = (x)._right8;
        if (!(((x)._right8) == null)) {
            ((x)._right8)._parent9 = _x293;
        }
        /* _min_ax12 is min of ax1 */
        var _augval298 = (_x293).ax1;
        var _child299 = (_x293)._left7;
        if (!((_child299) == null)) {
            var _val300 = (_child299)._min_ax12;
            _augval298 = ((_augval298) < (_val300)) ? (_augval298) : (_val300);
        }
        var _child301 = (_x293)._right8;
        if (!((_child301) == null)) {
            var _val302 = (_child301)._min_ax12;
            _augval298 = ((_augval298) < (_val302)) ? (_augval298) : (_val302);
        }
        (_x293)._min_ax12 = _augval298;
        /* _min_ay13 is min of ay1 */
        var _augval303 = (_x293).ay1;
        var _child304 = (_x293)._left7;
        if (!((_child304) == null)) {
            var _val305 = (_child304)._min_ay13;
            _augval303 = ((_augval303) < (_val305)) ? (_augval303) : (_val305);
        }
        var _child306 = (_x293)._right8;
        if (!((_child306) == null)) {
            var _val307 = (_child306)._min_ay13;
            _augval303 = ((_augval303) < (_val307)) ? (_augval303) : (_val307);
        }
        (_x293)._min_ay13 = _augval303;
        /* _max_ay24 is max of ay2 */
        var _augval308 = (_x293).ay2;
        var _child309 = (_x293)._left7;
        if (!((_child309) == null)) {
            var _val310 = (_child309)._max_ay24;
            _augval308 = ((_augval308) < (_val310)) ? (_val310) : (_augval308);
        }
        var _child311 = (_x293)._right8;
        if (!((_child311) == null)) {
            var _val312 = (_child311)._max_ay24;
            _augval308 = ((_augval308) < (_val312)) ? (_val312) : (_augval308);
        }
        (_x293)._max_ay24 = _augval308;
        (_x293)._height10 = 1 + ((((((_x293)._left7) == null) ? (-1) : (((_x293)._left7)._height10)) > ((((_x293)._right8) == null) ? (-1) : (((_x293)._right8)._height10))) ? ((((_x293)._left7) == null) ? (-1) : (((_x293)._left7)._height10)) : ((((_x293)._right8) == null) ? (-1) : (((_x293)._right8)._height10)));
        var _cursor313 = _mp296;
        var _changed314 = true;
        while ((_changed314) && (!((_cursor313) == (_parent288)))) {
            var _old__min_ax12315 = (_cursor313)._min_ax12;
            var _old__min_ay13316 = (_cursor313)._min_ay13;
            var _old__max_ay24317 = (_cursor313)._max_ay24;
            var _old_height318 = (_cursor313)._height10;
            /* _min_ax12 is min of ax1 */
            var _augval319 = (_cursor313).ax1;
            var _child320 = (_cursor313)._left7;
            if (!((_child320) == null)) {
                var _val321 = (_child320)._min_ax12;
                _augval319 = ((_augval319) < (_val321)) ? (_augval319) : (_val321);
            }
            var _child322 = (_cursor313)._right8;
            if (!((_child322) == null)) {
                var _val323 = (_child322)._min_ax12;
                _augval319 = ((_augval319) < (_val323)) ? (_augval319) : (_val323);
            }
            (_cursor313)._min_ax12 = _augval319;
            /* _min_ay13 is min of ay1 */
            var _augval324 = (_cursor313).ay1;
            var _child325 = (_cursor313)._left7;
            if (!((_child325) == null)) {
                var _val326 = (_child325)._min_ay13;
                _augval324 = ((_augval324) < (_val326)) ? (_augval324) : (_val326);
            }
            var _child327 = (_cursor313)._right8;
            if (!((_child327) == null)) {
                var _val328 = (_child327)._min_ay13;
                _augval324 = ((_augval324) < (_val328)) ? (_augval324) : (_val328);
            }
            (_cursor313)._min_ay13 = _augval324;
            /* _max_ay24 is max of ay2 */
            var _augval329 = (_cursor313).ay2;
            var _child330 = (_cursor313)._left7;
            if (!((_child330) == null)) {
                var _val331 = (_child330)._max_ay24;
                _augval329 = ((_augval329) < (_val331)) ? (_val331) : (_augval329);
            }
            var _child332 = (_cursor313)._right8;
            if (!((_child332) == null)) {
                var _val333 = (_child332)._max_ay24;
                _augval329 = ((_augval329) < (_val333)) ? (_val333) : (_augval329);
            }
            (_cursor313)._max_ay24 = _augval329;
            (_cursor313)._height10 = 1 + ((((((_cursor313)._left7) == null) ? (-1) : (((_cursor313)._left7)._height10)) > ((((_cursor313)._right8) == null) ? (-1) : (((_cursor313)._right8)._height10))) ? ((((_cursor313)._left7) == null) ? (-1) : (((_cursor313)._left7)._height10)) : ((((_cursor313)._right8) == null) ? (-1) : (((_cursor313)._right8)._height10)));
            _changed314 = false;
            _changed314 = (_changed314) || (!((_old__min_ax12315) == ((_cursor313)._min_ax12)));
            _changed314 = (_changed314) || (!((_old__min_ay13316) == ((_cursor313)._min_ay13)));
            _changed314 = (_changed314) || (!((_old__max_ay24317) == ((_cursor313)._max_ay24)));
            _changed314 = (_changed314) || (!((_old_height318) == ((_cursor313)._height10)));
            _cursor313 = (_cursor313)._parent9;
        }
    }
    var _cursor334 = _parent288;
    var _changed335 = true;
    while ((_changed335) && (!((_cursor334) == (null)))) {
        var _old__min_ax12336 = (_cursor334)._min_ax12;
        var _old__min_ay13337 = (_cursor334)._min_ay13;
        var _old__max_ay24338 = (_cursor334)._max_ay24;
        var _old_height339 = (_cursor334)._height10;
        /* _min_ax12 is min of ax1 */
        var _augval340 = (_cursor334).ax1;
        var _child341 = (_cursor334)._left7;
        if (!((_child341) == null)) {
            var _val342 = (_child341)._min_ax12;
            _augval340 = ((_augval340) < (_val342)) ? (_augval340) : (_val342);
        }
        var _child343 = (_cursor334)._right8;
        if (!((_child343) == null)) {
            var _val344 = (_child343)._min_ax12;
            _augval340 = ((_augval340) < (_val344)) ? (_augval340) : (_val344);
        }
        (_cursor334)._min_ax12 = _augval340;
        /* _min_ay13 is min of ay1 */
        var _augval345 = (_cursor334).ay1;
        var _child346 = (_cursor334)._left7;
        if (!((_child346) == null)) {
            var _val347 = (_child346)._min_ay13;
            _augval345 = ((_augval345) < (_val347)) ? (_augval345) : (_val347);
        }
        var _child348 = (_cursor334)._right8;
        if (!((_child348) == null)) {
            var _val349 = (_child348)._min_ay13;
            _augval345 = ((_augval345) < (_val349)) ? (_augval345) : (_val349);
        }
        (_cursor334)._min_ay13 = _augval345;
        /* _max_ay24 is max of ay2 */
        var _augval350 = (_cursor334).ay2;
        var _child351 = (_cursor334)._left7;
        if (!((_child351) == null)) {
            var _val352 = (_child351)._max_ay24;
            _augval350 = ((_augval350) < (_val352)) ? (_val352) : (_augval350);
        }
        var _child353 = (_cursor334)._right8;
        if (!((_child353) == null)) {
            var _val354 = (_child353)._max_ay24;
            _augval350 = ((_augval350) < (_val354)) ? (_val354) : (_augval350);
        }
        (_cursor334)._max_ay24 = _augval350;
        (_cursor334)._height10 = 1 + ((((((_cursor334)._left7) == null) ? (-1) : (((_cursor334)._left7)._height10)) > ((((_cursor334)._right8) == null) ? (-1) : (((_cursor334)._right8)._height10))) ? ((((_cursor334)._left7) == null) ? (-1) : (((_cursor334)._left7)._height10)) : ((((_cursor334)._right8) == null) ? (-1) : (((_cursor334)._right8)._height10)));
        _changed335 = false;
        _changed335 = (_changed335) || (!((_old__min_ax12336) == ((_cursor334)._min_ax12)));
        _changed335 = (_changed335) || (!((_old__min_ay13337) == ((_cursor334)._min_ay13)));
        _changed335 = (_changed335) || (!((_old__max_ay24338) == ((_cursor334)._max_ay24)));
        _changed335 = (_changed335) || (!((_old_height339) == ((_cursor334)._height10)));
        _cursor334 = (_cursor334)._parent9;
    }
    if (((this)._root1) == (x)) {
        (this)._root1 = _new_x291;
    }
};
RectangleHolder.prototype.updateAx1 = function (__x, new_val) {
    if ((__x).ax1 != new_val) {
        /* _min_ax12 is min of ax1 */
        var _augval355 = new_val;
        var _child356 = (__x)._left7;
        if (!((_child356) == null)) {
            var _val357 = (_child356)._min_ax12;
            _augval355 = ((_augval355) < (_val357)) ? (_augval355) : (_val357);
        }
        var _child358 = (__x)._right8;
        if (!((_child358) == null)) {
            var _val359 = (_child358)._min_ax12;
            _augval355 = ((_augval355) < (_val359)) ? (_augval355) : (_val359);
        }
        (__x)._min_ax12 = _augval355;
        var _cursor360 = (__x)._parent9;
        var _changed361 = true;
        while ((_changed361) && (!((_cursor360) == (null)))) {
            var _old__min_ax12362 = (_cursor360)._min_ax12;
            var _old_height363 = (_cursor360)._height10;
            /* _min_ax12 is min of ax1 */
            var _augval364 = (_cursor360).ax1;
            var _child365 = (_cursor360)._left7;
            if (!((_child365) == null)) {
                var _val366 = (_child365)._min_ax12;
                _augval364 = ((_augval364) < (_val366)) ? (_augval364) : (_val366);
            }
            var _child367 = (_cursor360)._right8;
            if (!((_child367) == null)) {
                var _val368 = (_child367)._min_ax12;
                _augval364 = ((_augval364) < (_val368)) ? (_augval364) : (_val368);
            }
            (_cursor360)._min_ax12 = _augval364;
            (_cursor360)._height10 = 1 + ((((((_cursor360)._left7) == null) ? (-1) : (((_cursor360)._left7)._height10)) > ((((_cursor360)._right8) == null) ? (-1) : (((_cursor360)._right8)._height10))) ? ((((_cursor360)._left7) == null) ? (-1) : (((_cursor360)._left7)._height10)) : ((((_cursor360)._right8) == null) ? (-1) : (((_cursor360)._right8)._height10)));
            _changed361 = false;
            _changed361 = (_changed361) || (!((_old__min_ax12362) == ((_cursor360)._min_ax12)));
            _changed361 = (_changed361) || (!((_old_height363) == ((_cursor360)._height10)));
            _cursor360 = (_cursor360)._parent9;
        }
        (__x).ax1 = new_val;
    }
}
RectangleHolder.prototype.updateAy1 = function (__x, new_val) {
    if ((__x).ay1 != new_val) {
        /* _min_ay13 is min of ay1 */
        var _augval369 = new_val;
        var _child370 = (__x)._left7;
        if (!((_child370) == null)) {
            var _val371 = (_child370)._min_ay13;
            _augval369 = ((_augval369) < (_val371)) ? (_augval369) : (_val371);
        }
        var _child372 = (__x)._right8;
        if (!((_child372) == null)) {
            var _val373 = (_child372)._min_ay13;
            _augval369 = ((_augval369) < (_val373)) ? (_augval369) : (_val373);
        }
        (__x)._min_ay13 = _augval369;
        var _cursor374 = (__x)._parent9;
        var _changed375 = true;
        while ((_changed375) && (!((_cursor374) == (null)))) {
            var _old__min_ay13376 = (_cursor374)._min_ay13;
            var _old_height377 = (_cursor374)._height10;
            /* _min_ay13 is min of ay1 */
            var _augval378 = (_cursor374).ay1;
            var _child379 = (_cursor374)._left7;
            if (!((_child379) == null)) {
                var _val380 = (_child379)._min_ay13;
                _augval378 = ((_augval378) < (_val380)) ? (_augval378) : (_val380);
            }
            var _child381 = (_cursor374)._right8;
            if (!((_child381) == null)) {
                var _val382 = (_child381)._min_ay13;
                _augval378 = ((_augval378) < (_val382)) ? (_augval378) : (_val382);
            }
            (_cursor374)._min_ay13 = _augval378;
            (_cursor374)._height10 = 1 + ((((((_cursor374)._left7) == null) ? (-1) : (((_cursor374)._left7)._height10)) > ((((_cursor374)._right8) == null) ? (-1) : (((_cursor374)._right8)._height10))) ? ((((_cursor374)._left7) == null) ? (-1) : (((_cursor374)._left7)._height10)) : ((((_cursor374)._right8) == null) ? (-1) : (((_cursor374)._right8)._height10)));
            _changed375 = false;
            _changed375 = (_changed375) || (!((_old__min_ay13376) == ((_cursor374)._min_ay13)));
            _changed375 = (_changed375) || (!((_old_height377) == ((_cursor374)._height10)));
            _cursor374 = (_cursor374)._parent9;
        }
        (__x).ay1 = new_val;
    }
}
RectangleHolder.prototype.updateAx2 = function (__x, new_val) {
    if ((__x).ax2 != new_val) {
        var _parent383 = (__x)._parent9;
        var _left384 = (__x)._left7;
        var _right385 = (__x)._right8;
        var _new_x386;
        if (((_left384) == null) && ((_right385) == null)) {
            _new_x386 = null;
            /* replace __x with _new_x386 in _parent383 */
            if (!((_parent383) == null)) {
                if (((_parent383)._left7) == (__x)) {
                    (_parent383)._left7 = _new_x386;
                } else {
                    (_parent383)._right8 = _new_x386;
                }
            }
            if (!((_new_x386) == null)) {
                (_new_x386)._parent9 = _parent383;
            }
        } else if ((!((_left384) == null)) && ((_right385) == null)) {
            _new_x386 = _left384;
            /* replace __x with _new_x386 in _parent383 */
            if (!((_parent383) == null)) {
                if (((_parent383)._left7) == (__x)) {
                    (_parent383)._left7 = _new_x386;
                } else {
                    (_parent383)._right8 = _new_x386;
                }
            }
            if (!((_new_x386) == null)) {
                (_new_x386)._parent9 = _parent383;
            }
        } else if (((_left384) == null) && (!((_right385) == null))) {
            _new_x386 = _right385;
            /* replace __x with _new_x386 in _parent383 */
            if (!((_parent383) == null)) {
                if (((_parent383)._left7) == (__x)) {
                    (_parent383)._left7 = _new_x386;
                } else {
                    (_parent383)._right8 = _new_x386;
                }
            }
            if (!((_new_x386) == null)) {
                (_new_x386)._parent9 = _parent383;
            }
        } else {
            var _root387 = (__x)._right8;
            var _x388 = _root387;
            var _descend389 = true;
            var _from_left390 = true;
            while (true) {
                if ((_x388) == null) {
                    _x388 = null;
                    break;
                }
                if (_descend389) {
                    /* too small? */
                    if (false) {
                        if ((!(((_x388)._right8) == null)) && (true)) {
                            if ((_x388) == (_root387)) {
                                _root387 = (_x388)._right8;
                            }
                            _x388 = (_x388)._right8;
                        } else if ((_x388) == (_root387)) {
                            _x388 = null;
                            break;
                        } else {
                            _descend389 = false;
                            _from_left390 = (!(((_x388)._parent9) == null)) && ((_x388) == (((_x388)._parent9)._left7));
                            _x388 = (_x388)._parent9;
                        }
                    } else if ((!(((_x388)._left7) == null)) && (true)) {
                        _x388 = (_x388)._left7;
                        /* too large? */
                    } else if (false) {
                        if ((_x388) == (_root387)) {
                            _x388 = null;
                            break;
                        } else {
                            _descend389 = false;
                            _from_left390 = (!(((_x388)._parent9) == null)) && ((_x388) == (((_x388)._parent9)._left7));
                            _x388 = (_x388)._parent9;
                        }
                        /* node ok? */
                    } else if (true) {
                        break;
                    } else if ((_x388) == (_root387)) {
                        _root387 = (_x388)._right8;
                        _x388 = (_x388)._right8;
                    } else {
                        if ((!(((_x388)._right8) == null)) && (true)) {
                            if ((_x388) == (_root387)) {
                                _root387 = (_x388)._right8;
                            }
                            _x388 = (_x388)._right8;
                        } else {
                            _descend389 = false;
                            _from_left390 = (!(((_x388)._parent9) == null)) && ((_x388) == (((_x388)._parent9)._left7));
                            _x388 = (_x388)._parent9;
                        }
                    }
                } else if (_from_left390) {
                    if (false) {
                        _x388 = null;
                        break;
                    } else if (true) {
                        break;
                    } else if ((!(((_x388)._right8) == null)) && (true)) {
                        _descend389 = true;
                        if ((_x388) == (_root387)) {
                            _root387 = (_x388)._right8;
                        }
                        _x388 = (_x388)._right8;
                    } else if ((_x388) == (_root387)) {
                        _x388 = null;
                        break;
                    } else {
                        _descend389 = false;
                        _from_left390 = (!(((_x388)._parent9) == null)) && ((_x388) == (((_x388)._parent9)._left7));
                        _x388 = (_x388)._parent9;
                    }
                } else {
                    if ((_x388) == (_root387)) {
                        _x388 = null;
                        break;
                    } else {
                        _descend389 = false;
                        _from_left390 = (!(((_x388)._parent9) == null)) && ((_x388) == (((_x388)._parent9)._left7));
                        _x388 = (_x388)._parent9;
                    }
                }
            }
            _new_x386 = _x388;
            var _mp391 = (_x388)._parent9;
            var _mr392 = (_x388)._right8;
            /* replace _x388 with _mr392 in _mp391 */
            if (!((_mp391) == null)) {
                if (((_mp391)._left7) == (_x388)) {
                    (_mp391)._left7 = _mr392;
                } else {
                    (_mp391)._right8 = _mr392;
                }
            }
            if (!((_mr392) == null)) {
                (_mr392)._parent9 = _mp391;
            }
            /* replace __x with _x388 in _parent383 */
            if (!((_parent383) == null)) {
                if (((_parent383)._left7) == (__x)) {
                    (_parent383)._left7 = _x388;
                } else {
                    (_parent383)._right8 = _x388;
                }
            }
            if (!((_x388) == null)) {
                (_x388)._parent9 = _parent383;
            }
            /* replace null with _left384 in _x388 */
            (_x388)._left7 = _left384;
            if (!((_left384) == null)) {
                (_left384)._parent9 = _x388;
            }
            /* replace _mr392 with (__x)._right8 in _x388 */
            (_x388)._right8 = (__x)._right8;
            if (!(((__x)._right8) == null)) {
                ((__x)._right8)._parent9 = _x388;
            }
            /* _min_ax12 is min of ax1 */
            var _augval393 = (_x388).ax1;
            var _child394 = (_x388)._left7;
            if (!((_child394) == null)) {
                var _val395 = (_child394)._min_ax12;
                _augval393 = ((_augval393) < (_val395)) ? (_augval393) : (_val395);
            }
            var _child396 = (_x388)._right8;
            if (!((_child396) == null)) {
                var _val397 = (_child396)._min_ax12;
                _augval393 = ((_augval393) < (_val397)) ? (_augval393) : (_val397);
            }
            (_x388)._min_ax12 = _augval393;
            /* _min_ay13 is min of ay1 */
            var _augval398 = (_x388).ay1;
            var _child399 = (_x388)._left7;
            if (!((_child399) == null)) {
                var _val400 = (_child399)._min_ay13;
                _augval398 = ((_augval398) < (_val400)) ? (_augval398) : (_val400);
            }
            var _child401 = (_x388)._right8;
            if (!((_child401) == null)) {
                var _val402 = (_child401)._min_ay13;
                _augval398 = ((_augval398) < (_val402)) ? (_augval398) : (_val402);
            }
            (_x388)._min_ay13 = _augval398;
            /* _max_ay24 is max of ay2 */
            var _augval403 = (_x388).ay2;
            var _child404 = (_x388)._left7;
            if (!((_child404) == null)) {
                var _val405 = (_child404)._max_ay24;
                _augval403 = ((_augval403) < (_val405)) ? (_val405) : (_augval403);
            }
            var _child406 = (_x388)._right8;
            if (!((_child406) == null)) {
                var _val407 = (_child406)._max_ay24;
                _augval403 = ((_augval403) < (_val407)) ? (_val407) : (_augval403);
            }
            (_x388)._max_ay24 = _augval403;
            (_x388)._height10 = 1 + ((((((_x388)._left7) == null) ? (-1) : (((_x388)._left7)._height10)) > ((((_x388)._right8) == null) ? (-1) : (((_x388)._right8)._height10))) ? ((((_x388)._left7) == null) ? (-1) : (((_x388)._left7)._height10)) : ((((_x388)._right8) == null) ? (-1) : (((_x388)._right8)._height10)));
            var _cursor408 = _mp391;
            var _changed409 = true;
            while ((_changed409) && (!((_cursor408) == (_parent383)))) {
                var _old__min_ax12410 = (_cursor408)._min_ax12;
                var _old__min_ay13411 = (_cursor408)._min_ay13;
                var _old__max_ay24412 = (_cursor408)._max_ay24;
                var _old_height413 = (_cursor408)._height10;
                /* _min_ax12 is min of ax1 */
                var _augval414 = (_cursor408).ax1;
                var _child415 = (_cursor408)._left7;
                if (!((_child415) == null)) {
                    var _val416 = (_child415)._min_ax12;
                    _augval414 = ((_augval414) < (_val416)) ? (_augval414) : (_val416);
                }
                var _child417 = (_cursor408)._right8;
                if (!((_child417) == null)) {
                    var _val418 = (_child417)._min_ax12;
                    _augval414 = ((_augval414) < (_val418)) ? (_augval414) : (_val418);
                }
                (_cursor408)._min_ax12 = _augval414;
                /* _min_ay13 is min of ay1 */
                var _augval419 = (_cursor408).ay1;
                var _child420 = (_cursor408)._left7;
                if (!((_child420) == null)) {
                    var _val421 = (_child420)._min_ay13;
                    _augval419 = ((_augval419) < (_val421)) ? (_augval419) : (_val421);
                }
                var _child422 = (_cursor408)._right8;
                if (!((_child422) == null)) {
                    var _val423 = (_child422)._min_ay13;
                    _augval419 = ((_augval419) < (_val423)) ? (_augval419) : (_val423);
                }
                (_cursor408)._min_ay13 = _augval419;
                /* _max_ay24 is max of ay2 */
                var _augval424 = (_cursor408).ay2;
                var _child425 = (_cursor408)._left7;
                if (!((_child425) == null)) {
                    var _val426 = (_child425)._max_ay24;
                    _augval424 = ((_augval424) < (_val426)) ? (_val426) : (_augval424);
                }
                var _child427 = (_cursor408)._right8;
                if (!((_child427) == null)) {
                    var _val428 = (_child427)._max_ay24;
                    _augval424 = ((_augval424) < (_val428)) ? (_val428) : (_augval424);
                }
                (_cursor408)._max_ay24 = _augval424;
                (_cursor408)._height10 = 1 + ((((((_cursor408)._left7) == null) ? (-1) : (((_cursor408)._left7)._height10)) > ((((_cursor408)._right8) == null) ? (-1) : (((_cursor408)._right8)._height10))) ? ((((_cursor408)._left7) == null) ? (-1) : (((_cursor408)._left7)._height10)) : ((((_cursor408)._right8) == null) ? (-1) : (((_cursor408)._right8)._height10)));
                _changed409 = false;
                _changed409 = (_changed409) || (!((_old__min_ax12410) == ((_cursor408)._min_ax12)));
                _changed409 = (_changed409) || (!((_old__min_ay13411) == ((_cursor408)._min_ay13)));
                _changed409 = (_changed409) || (!((_old__max_ay24412) == ((_cursor408)._max_ay24)));
                _changed409 = (_changed409) || (!((_old_height413) == ((_cursor408)._height10)));
                _cursor408 = (_cursor408)._parent9;
            }
        }
        var _cursor429 = _parent383;
        var _changed430 = true;
        while ((_changed430) && (!((_cursor429) == (null)))) {
            var _old__min_ax12431 = (_cursor429)._min_ax12;
            var _old__min_ay13432 = (_cursor429)._min_ay13;
            var _old__max_ay24433 = (_cursor429)._max_ay24;
            var _old_height434 = (_cursor429)._height10;
            /* _min_ax12 is min of ax1 */
            var _augval435 = (_cursor429).ax1;
            var _child436 = (_cursor429)._left7;
            if (!((_child436) == null)) {
                var _val437 = (_child436)._min_ax12;
                _augval435 = ((_augval435) < (_val437)) ? (_augval435) : (_val437);
            }
            var _child438 = (_cursor429)._right8;
            if (!((_child438) == null)) {
                var _val439 = (_child438)._min_ax12;
                _augval435 = ((_augval435) < (_val439)) ? (_augval435) : (_val439);
            }
            (_cursor429)._min_ax12 = _augval435;
            /* _min_ay13 is min of ay1 */
            var _augval440 = (_cursor429).ay1;
            var _child441 = (_cursor429)._left7;
            if (!((_child441) == null)) {
                var _val442 = (_child441)._min_ay13;
                _augval440 = ((_augval440) < (_val442)) ? (_augval440) : (_val442);
            }
            var _child443 = (_cursor429)._right8;
            if (!((_child443) == null)) {
                var _val444 = (_child443)._min_ay13;
                _augval440 = ((_augval440) < (_val444)) ? (_augval440) : (_val444);
            }
            (_cursor429)._min_ay13 = _augval440;
            /* _max_ay24 is max of ay2 */
            var _augval445 = (_cursor429).ay2;
            var _child446 = (_cursor429)._left7;
            if (!((_child446) == null)) {
                var _val447 = (_child446)._max_ay24;
                _augval445 = ((_augval445) < (_val447)) ? (_val447) : (_augval445);
            }
            var _child448 = (_cursor429)._right8;
            if (!((_child448) == null)) {
                var _val449 = (_child448)._max_ay24;
                _augval445 = ((_augval445) < (_val449)) ? (_val449) : (_augval445);
            }
            (_cursor429)._max_ay24 = _augval445;
            (_cursor429)._height10 = 1 + ((((((_cursor429)._left7) == null) ? (-1) : (((_cursor429)._left7)._height10)) > ((((_cursor429)._right8) == null) ? (-1) : (((_cursor429)._right8)._height10))) ? ((((_cursor429)._left7) == null) ? (-1) : (((_cursor429)._left7)._height10)) : ((((_cursor429)._right8) == null) ? (-1) : (((_cursor429)._right8)._height10)));
            _changed430 = false;
            _changed430 = (_changed430) || (!((_old__min_ax12431) == ((_cursor429)._min_ax12)));
            _changed430 = (_changed430) || (!((_old__min_ay13432) == ((_cursor429)._min_ay13)));
            _changed430 = (_changed430) || (!((_old__max_ay24433) == ((_cursor429)._max_ay24)));
            _changed430 = (_changed430) || (!((_old_height434) == ((_cursor429)._height10)));
            _cursor429 = (_cursor429)._parent9;
        }
        if (((this)._root1) == (__x)) {
            (this)._root1 = _new_x386;
        }
        (__x)._left7 = null;
        (__x)._right8 = null;
        (__x)._min_ax12 = (__x).ax1;
        (__x)._min_ay13 = (__x).ay1;
        (__x)._max_ay24 = (__x).ay2;
        (__x)._height10 = 0;
        var _previous450 = null;
        var _current451 = (this)._root1;
        var _is_left452 = false;
        while (!((_current451) == null)) {
            _previous450 = _current451;
            if ((new_val) < ((_current451).ax2)) {
                _current451 = (_current451)._left7;
                _is_left452 = true;
            } else {
                _current451 = (_current451)._right8;
                _is_left452 = false;
            }
        }
        if ((_previous450) == null) {
            (this)._root1 = __x;
        } else {
            (__x)._parent9 = _previous450;
            if (_is_left452) {
                (_previous450)._left7 = __x;
            } else {
                (_previous450)._right8 = __x;
            }
        }
        var _cursor453 = (__x)._parent9;
        var _changed454 = true;
        while ((_changed454) && (!((_cursor453) == (null)))) {
            var _old__min_ax12455 = (_cursor453)._min_ax12;
            var _old__min_ay13456 = (_cursor453)._min_ay13;
            var _old__max_ay24457 = (_cursor453)._max_ay24;
            var _old_height458 = (_cursor453)._height10;
            /* _min_ax12 is min of ax1 */
            var _augval459 = (_cursor453).ax1;
            var _child460 = (_cursor453)._left7;
            if (!((_child460) == null)) {
                var _val461 = (_child460)._min_ax12;
                _augval459 = ((_augval459) < (_val461)) ? (_augval459) : (_val461);
            }
            var _child462 = (_cursor453)._right8;
            if (!((_child462) == null)) {
                var _val463 = (_child462)._min_ax12;
                _augval459 = ((_augval459) < (_val463)) ? (_augval459) : (_val463);
            }
            (_cursor453)._min_ax12 = _augval459;
            /* _min_ay13 is min of ay1 */
            var _augval464 = (_cursor453).ay1;
            var _child465 = (_cursor453)._left7;
            if (!((_child465) == null)) {
                var _val466 = (_child465)._min_ay13;
                _augval464 = ((_augval464) < (_val466)) ? (_augval464) : (_val466);
            }
            var _child467 = (_cursor453)._right8;
            if (!((_child467) == null)) {
                var _val468 = (_child467)._min_ay13;
                _augval464 = ((_augval464) < (_val468)) ? (_augval464) : (_val468);
            }
            (_cursor453)._min_ay13 = _augval464;
            /* _max_ay24 is max of ay2 */
            var _augval469 = (_cursor453).ay2;
            var _child470 = (_cursor453)._left7;
            if (!((_child470) == null)) {
                var _val471 = (_child470)._max_ay24;
                _augval469 = ((_augval469) < (_val471)) ? (_val471) : (_augval469);
            }
            var _child472 = (_cursor453)._right8;
            if (!((_child472) == null)) {
                var _val473 = (_child472)._max_ay24;
                _augval469 = ((_augval469) < (_val473)) ? (_val473) : (_augval469);
            }
            (_cursor453)._max_ay24 = _augval469;
            (_cursor453)._height10 = 1 + ((((((_cursor453)._left7) == null) ? (-1) : (((_cursor453)._left7)._height10)) > ((((_cursor453)._right8) == null) ? (-1) : (((_cursor453)._right8)._height10))) ? ((((_cursor453)._left7) == null) ? (-1) : (((_cursor453)._left7)._height10)) : ((((_cursor453)._right8) == null) ? (-1) : (((_cursor453)._right8)._height10)));
            _changed454 = false;
            _changed454 = (_changed454) || (!((_old__min_ax12455) == ((_cursor453)._min_ax12)));
            _changed454 = (_changed454) || (!((_old__min_ay13456) == ((_cursor453)._min_ay13)));
            _changed454 = (_changed454) || (!((_old__max_ay24457) == ((_cursor453)._max_ay24)));
            _changed454 = (_changed454) || (!((_old_height458) == ((_cursor453)._height10)));
            _cursor453 = (_cursor453)._parent9;
        }
        /* rebalance AVL tree */
        var _cursor474 = __x;
        var _imbalance475;
        while (!(((_cursor474)._parent9) == null)) {
            _cursor474 = (_cursor474)._parent9;
            (_cursor474)._height10 = 1 + ((((((_cursor474)._left7) == null) ? (-1) : (((_cursor474)._left7)._height10)) > ((((_cursor474)._right8) == null) ? (-1) : (((_cursor474)._right8)._height10))) ? ((((_cursor474)._left7) == null) ? (-1) : (((_cursor474)._left7)._height10)) : ((((_cursor474)._right8) == null) ? (-1) : (((_cursor474)._right8)._height10)));
            _imbalance475 = ((((_cursor474)._left7) == null) ? (-1) : (((_cursor474)._left7)._height10)) - ((((_cursor474)._right8) == null) ? (-1) : (((_cursor474)._right8)._height10));
            if ((_imbalance475) > (1)) {
                if ((((((_cursor474)._left7)._left7) == null) ? (-1) : ((((_cursor474)._left7)._left7)._height10)) < (((((_cursor474)._left7)._right8) == null) ? (-1) : ((((_cursor474)._left7)._right8)._height10))) {
                    /* rotate ((_cursor474)._left7)._right8 */
                    var _a476 = (_cursor474)._left7;
                    var _b477 = (_a476)._right8;
                    var _c478 = (_b477)._left7;
                    /* replace _a476 with _b477 in (_a476)._parent9 */
                    if (!(((_a476)._parent9) == null)) {
                        if ((((_a476)._parent9)._left7) == (_a476)) {
                            ((_a476)._parent9)._left7 = _b477;
                        } else {
                            ((_a476)._parent9)._right8 = _b477;
                        }
                    }
                    if (!((_b477) == null)) {
                        (_b477)._parent9 = (_a476)._parent9;
                    }
                    /* replace _c478 with _a476 in _b477 */
                    (_b477)._left7 = _a476;
                    if (!((_a476) == null)) {
                        (_a476)._parent9 = _b477;
                    }
                    /* replace _b477 with _c478 in _a476 */
                    (_a476)._right8 = _c478;
                    if (!((_c478) == null)) {
                        (_c478)._parent9 = _a476;
                    }
                    /* _min_ax12 is min of ax1 */
                    var _augval479 = (_a476).ax1;
                    var _child480 = (_a476)._left7;
                    if (!((_child480) == null)) {
                        var _val481 = (_child480)._min_ax12;
                        _augval479 = ((_augval479) < (_val481)) ? (_augval479) : (_val481);
                    }
                    var _child482 = (_a476)._right8;
                    if (!((_child482) == null)) {
                        var _val483 = (_child482)._min_ax12;
                        _augval479 = ((_augval479) < (_val483)) ? (_augval479) : (_val483);
                    }
                    (_a476)._min_ax12 = _augval479;
                    /* _min_ay13 is min of ay1 */
                    var _augval484 = (_a476).ay1;
                    var _child485 = (_a476)._left7;
                    if (!((_child485) == null)) {
                        var _val486 = (_child485)._min_ay13;
                        _augval484 = ((_augval484) < (_val486)) ? (_augval484) : (_val486);
                    }
                    var _child487 = (_a476)._right8;
                    if (!((_child487) == null)) {
                        var _val488 = (_child487)._min_ay13;
                        _augval484 = ((_augval484) < (_val488)) ? (_augval484) : (_val488);
                    }
                    (_a476)._min_ay13 = _augval484;
                    /* _max_ay24 is max of ay2 */
                    var _augval489 = (_a476).ay2;
                    var _child490 = (_a476)._left7;
                    if (!((_child490) == null)) {
                        var _val491 = (_child490)._max_ay24;
                        _augval489 = ((_augval489) < (_val491)) ? (_val491) : (_augval489);
                    }
                    var _child492 = (_a476)._right8;
                    if (!((_child492) == null)) {
                        var _val493 = (_child492)._max_ay24;
                        _augval489 = ((_augval489) < (_val493)) ? (_val493) : (_augval489);
                    }
                    (_a476)._max_ay24 = _augval489;
                    (_a476)._height10 = 1 + ((((((_a476)._left7) == null) ? (-1) : (((_a476)._left7)._height10)) > ((((_a476)._right8) == null) ? (-1) : (((_a476)._right8)._height10))) ? ((((_a476)._left7) == null) ? (-1) : (((_a476)._left7)._height10)) : ((((_a476)._right8) == null) ? (-1) : (((_a476)._right8)._height10)));
                    /* _min_ax12 is min of ax1 */
                    var _augval494 = (_b477).ax1;
                    var _child495 = (_b477)._left7;
                    if (!((_child495) == null)) {
                        var _val496 = (_child495)._min_ax12;
                        _augval494 = ((_augval494) < (_val496)) ? (_augval494) : (_val496);
                    }
                    var _child497 = (_b477)._right8;
                    if (!((_child497) == null)) {
                        var _val498 = (_child497)._min_ax12;
                        _augval494 = ((_augval494) < (_val498)) ? (_augval494) : (_val498);
                    }
                    (_b477)._min_ax12 = _augval494;
                    /* _min_ay13 is min of ay1 */
                    var _augval499 = (_b477).ay1;
                    var _child500 = (_b477)._left7;
                    if (!((_child500) == null)) {
                        var _val501 = (_child500)._min_ay13;
                        _augval499 = ((_augval499) < (_val501)) ? (_augval499) : (_val501);
                    }
                    var _child502 = (_b477)._right8;
                    if (!((_child502) == null)) {
                        var _val503 = (_child502)._min_ay13;
                        _augval499 = ((_augval499) < (_val503)) ? (_augval499) : (_val503);
                    }
                    (_b477)._min_ay13 = _augval499;
                    /* _max_ay24 is max of ay2 */
                    var _augval504 = (_b477).ay2;
                    var _child505 = (_b477)._left7;
                    if (!((_child505) == null)) {
                        var _val506 = (_child505)._max_ay24;
                        _augval504 = ((_augval504) < (_val506)) ? (_val506) : (_augval504);
                    }
                    var _child507 = (_b477)._right8;
                    if (!((_child507) == null)) {
                        var _val508 = (_child507)._max_ay24;
                        _augval504 = ((_augval504) < (_val508)) ? (_val508) : (_augval504);
                    }
                    (_b477)._max_ay24 = _augval504;
                    (_b477)._height10 = 1 + ((((((_b477)._left7) == null) ? (-1) : (((_b477)._left7)._height10)) > ((((_b477)._right8) == null) ? (-1) : (((_b477)._right8)._height10))) ? ((((_b477)._left7) == null) ? (-1) : (((_b477)._left7)._height10)) : ((((_b477)._right8) == null) ? (-1) : (((_b477)._right8)._height10)));
                    if (!(((_b477)._parent9) == null)) {
                        /* _min_ax12 is min of ax1 */
                        var _augval509 = ((_b477)._parent9).ax1;
                        var _child510 = ((_b477)._parent9)._left7;
                        if (!((_child510) == null)) {
                            var _val511 = (_child510)._min_ax12;
                            _augval509 = ((_augval509) < (_val511)) ? (_augval509) : (_val511);
                        }
                        var _child512 = ((_b477)._parent9)._right8;
                        if (!((_child512) == null)) {
                            var _val513 = (_child512)._min_ax12;
                            _augval509 = ((_augval509) < (_val513)) ? (_augval509) : (_val513);
                        }
                        ((_b477)._parent9)._min_ax12 = _augval509;
                        /* _min_ay13 is min of ay1 */
                        var _augval514 = ((_b477)._parent9).ay1;
                        var _child515 = ((_b477)._parent9)._left7;
                        if (!((_child515) == null)) {
                            var _val516 = (_child515)._min_ay13;
                            _augval514 = ((_augval514) < (_val516)) ? (_augval514) : (_val516);
                        }
                        var _child517 = ((_b477)._parent9)._right8;
                        if (!((_child517) == null)) {
                            var _val518 = (_child517)._min_ay13;
                            _augval514 = ((_augval514) < (_val518)) ? (_augval514) : (_val518);
                        }
                        ((_b477)._parent9)._min_ay13 = _augval514;
                        /* _max_ay24 is max of ay2 */
                        var _augval519 = ((_b477)._parent9).ay2;
                        var _child520 = ((_b477)._parent9)._left7;
                        if (!((_child520) == null)) {
                            var _val521 = (_child520)._max_ay24;
                            _augval519 = ((_augval519) < (_val521)) ? (_val521) : (_augval519);
                        }
                        var _child522 = ((_b477)._parent9)._right8;
                        if (!((_child522) == null)) {
                            var _val523 = (_child522)._max_ay24;
                            _augval519 = ((_augval519) < (_val523)) ? (_val523) : (_augval519);
                        }
                        ((_b477)._parent9)._max_ay24 = _augval519;
                        ((_b477)._parent9)._height10 = 1 + (((((((_b477)._parent9)._left7) == null) ? (-1) : ((((_b477)._parent9)._left7)._height10)) > (((((_b477)._parent9)._right8) == null) ? (-1) : ((((_b477)._parent9)._right8)._height10))) ? (((((_b477)._parent9)._left7) == null) ? (-1) : ((((_b477)._parent9)._left7)._height10)) : (((((_b477)._parent9)._right8) == null) ? (-1) : ((((_b477)._parent9)._right8)._height10)));
                    } else {
                        (this)._root1 = _b477;
                    }
                }
                /* rotate (_cursor474)._left7 */
                var _a524 = _cursor474;
                var _b525 = (_a524)._left7;
                var _c526 = (_b525)._right8;
                /* replace _a524 with _b525 in (_a524)._parent9 */
                if (!(((_a524)._parent9) == null)) {
                    if ((((_a524)._parent9)._left7) == (_a524)) {
                        ((_a524)._parent9)._left7 = _b525;
                    } else {
                        ((_a524)._parent9)._right8 = _b525;
                    }
                }
                if (!((_b525) == null)) {
                    (_b525)._parent9 = (_a524)._parent9;
                }
                /* replace _c526 with _a524 in _b525 */
                (_b525)._right8 = _a524;
                if (!((_a524) == null)) {
                    (_a524)._parent9 = _b525;
                }
                /* replace _b525 with _c526 in _a524 */
                (_a524)._left7 = _c526;
                if (!((_c526) == null)) {
                    (_c526)._parent9 = _a524;
                }
                /* _min_ax12 is min of ax1 */
                var _augval527 = (_a524).ax1;
                var _child528 = (_a524)._left7;
                if (!((_child528) == null)) {
                    var _val529 = (_child528)._min_ax12;
                    _augval527 = ((_augval527) < (_val529)) ? (_augval527) : (_val529);
                }
                var _child530 = (_a524)._right8;
                if (!((_child530) == null)) {
                    var _val531 = (_child530)._min_ax12;
                    _augval527 = ((_augval527) < (_val531)) ? (_augval527) : (_val531);
                }
                (_a524)._min_ax12 = _augval527;
                /* _min_ay13 is min of ay1 */
                var _augval532 = (_a524).ay1;
                var _child533 = (_a524)._left7;
                if (!((_child533) == null)) {
                    var _val534 = (_child533)._min_ay13;
                    _augval532 = ((_augval532) < (_val534)) ? (_augval532) : (_val534);
                }
                var _child535 = (_a524)._right8;
                if (!((_child535) == null)) {
                    var _val536 = (_child535)._min_ay13;
                    _augval532 = ((_augval532) < (_val536)) ? (_augval532) : (_val536);
                }
                (_a524)._min_ay13 = _augval532;
                /* _max_ay24 is max of ay2 */
                var _augval537 = (_a524).ay2;
                var _child538 = (_a524)._left7;
                if (!((_child538) == null)) {
                    var _val539 = (_child538)._max_ay24;
                    _augval537 = ((_augval537) < (_val539)) ? (_val539) : (_augval537);
                }
                var _child540 = (_a524)._right8;
                if (!((_child540) == null)) {
                    var _val541 = (_child540)._max_ay24;
                    _augval537 = ((_augval537) < (_val541)) ? (_val541) : (_augval537);
                }
                (_a524)._max_ay24 = _augval537;
                (_a524)._height10 = 1 + ((((((_a524)._left7) == null) ? (-1) : (((_a524)._left7)._height10)) > ((((_a524)._right8) == null) ? (-1) : (((_a524)._right8)._height10))) ? ((((_a524)._left7) == null) ? (-1) : (((_a524)._left7)._height10)) : ((((_a524)._right8) == null) ? (-1) : (((_a524)._right8)._height10)));
                /* _min_ax12 is min of ax1 */
                var _augval542 = (_b525).ax1;
                var _child543 = (_b525)._left7;
                if (!((_child543) == null)) {
                    var _val544 = (_child543)._min_ax12;
                    _augval542 = ((_augval542) < (_val544)) ? (_augval542) : (_val544);
                }
                var _child545 = (_b525)._right8;
                if (!((_child545) == null)) {
                    var _val546 = (_child545)._min_ax12;
                    _augval542 = ((_augval542) < (_val546)) ? (_augval542) : (_val546);
                }
                (_b525)._min_ax12 = _augval542;
                /* _min_ay13 is min of ay1 */
                var _augval547 = (_b525).ay1;
                var _child548 = (_b525)._left7;
                if (!((_child548) == null)) {
                    var _val549 = (_child548)._min_ay13;
                    _augval547 = ((_augval547) < (_val549)) ? (_augval547) : (_val549);
                }
                var _child550 = (_b525)._right8;
                if (!((_child550) == null)) {
                    var _val551 = (_child550)._min_ay13;
                    _augval547 = ((_augval547) < (_val551)) ? (_augval547) : (_val551);
                }
                (_b525)._min_ay13 = _augval547;
                /* _max_ay24 is max of ay2 */
                var _augval552 = (_b525).ay2;
                var _child553 = (_b525)._left7;
                if (!((_child553) == null)) {
                    var _val554 = (_child553)._max_ay24;
                    _augval552 = ((_augval552) < (_val554)) ? (_val554) : (_augval552);
                }
                var _child555 = (_b525)._right8;
                if (!((_child555) == null)) {
                    var _val556 = (_child555)._max_ay24;
                    _augval552 = ((_augval552) < (_val556)) ? (_val556) : (_augval552);
                }
                (_b525)._max_ay24 = _augval552;
                (_b525)._height10 = 1 + ((((((_b525)._left7) == null) ? (-1) : (((_b525)._left7)._height10)) > ((((_b525)._right8) == null) ? (-1) : (((_b525)._right8)._height10))) ? ((((_b525)._left7) == null) ? (-1) : (((_b525)._left7)._height10)) : ((((_b525)._right8) == null) ? (-1) : (((_b525)._right8)._height10)));
                if (!(((_b525)._parent9) == null)) {
                    /* _min_ax12 is min of ax1 */
                    var _augval557 = ((_b525)._parent9).ax1;
                    var _child558 = ((_b525)._parent9)._left7;
                    if (!((_child558) == null)) {
                        var _val559 = (_child558)._min_ax12;
                        _augval557 = ((_augval557) < (_val559)) ? (_augval557) : (_val559);
                    }
                    var _child560 = ((_b525)._parent9)._right8;
                    if (!((_child560) == null)) {
                        var _val561 = (_child560)._min_ax12;
                        _augval557 = ((_augval557) < (_val561)) ? (_augval557) : (_val561);
                    }
                    ((_b525)._parent9)._min_ax12 = _augval557;
                    /* _min_ay13 is min of ay1 */
                    var _augval562 = ((_b525)._parent9).ay1;
                    var _child563 = ((_b525)._parent9)._left7;
                    if (!((_child563) == null)) {
                        var _val564 = (_child563)._min_ay13;
                        _augval562 = ((_augval562) < (_val564)) ? (_augval562) : (_val564);
                    }
                    var _child565 = ((_b525)._parent9)._right8;
                    if (!((_child565) == null)) {
                        var _val566 = (_child565)._min_ay13;
                        _augval562 = ((_augval562) < (_val566)) ? (_augval562) : (_val566);
                    }
                    ((_b525)._parent9)._min_ay13 = _augval562;
                    /* _max_ay24 is max of ay2 */
                    var _augval567 = ((_b525)._parent9).ay2;
                    var _child568 = ((_b525)._parent9)._left7;
                    if (!((_child568) == null)) {
                        var _val569 = (_child568)._max_ay24;
                        _augval567 = ((_augval567) < (_val569)) ? (_val569) : (_augval567);
                    }
                    var _child570 = ((_b525)._parent9)._right8;
                    if (!((_child570) == null)) {
                        var _val571 = (_child570)._max_ay24;
                        _augval567 = ((_augval567) < (_val571)) ? (_val571) : (_augval567);
                    }
                    ((_b525)._parent9)._max_ay24 = _augval567;
                    ((_b525)._parent9)._height10 = 1 + (((((((_b525)._parent9)._left7) == null) ? (-1) : ((((_b525)._parent9)._left7)._height10)) > (((((_b525)._parent9)._right8) == null) ? (-1) : ((((_b525)._parent9)._right8)._height10))) ? (((((_b525)._parent9)._left7) == null) ? (-1) : ((((_b525)._parent9)._left7)._height10)) : (((((_b525)._parent9)._right8) == null) ? (-1) : ((((_b525)._parent9)._right8)._height10)));
                } else {
                    (this)._root1 = _b525;
                }
                _cursor474 = (_cursor474)._parent9;
            } else if ((_imbalance475) < (-1)) {
                if ((((((_cursor474)._right8)._left7) == null) ? (-1) : ((((_cursor474)._right8)._left7)._height10)) > (((((_cursor474)._right8)._right8) == null) ? (-1) : ((((_cursor474)._right8)._right8)._height10))) {
                    /* rotate ((_cursor474)._right8)._left7 */
                    var _a572 = (_cursor474)._right8;
                    var _b573 = (_a572)._left7;
                    var _c574 = (_b573)._right8;
                    /* replace _a572 with _b573 in (_a572)._parent9 */
                    if (!(((_a572)._parent9) == null)) {
                        if ((((_a572)._parent9)._left7) == (_a572)) {
                            ((_a572)._parent9)._left7 = _b573;
                        } else {
                            ((_a572)._parent9)._right8 = _b573;
                        }
                    }
                    if (!((_b573) == null)) {
                        (_b573)._parent9 = (_a572)._parent9;
                    }
                    /* replace _c574 with _a572 in _b573 */
                    (_b573)._right8 = _a572;
                    if (!((_a572) == null)) {
                        (_a572)._parent9 = _b573;
                    }
                    /* replace _b573 with _c574 in _a572 */
                    (_a572)._left7 = _c574;
                    if (!((_c574) == null)) {
                        (_c574)._parent9 = _a572;
                    }
                    /* _min_ax12 is min of ax1 */
                    var _augval575 = (_a572).ax1;
                    var _child576 = (_a572)._left7;
                    if (!((_child576) == null)) {
                        var _val577 = (_child576)._min_ax12;
                        _augval575 = ((_augval575) < (_val577)) ? (_augval575) : (_val577);
                    }
                    var _child578 = (_a572)._right8;
                    if (!((_child578) == null)) {
                        var _val579 = (_child578)._min_ax12;
                        _augval575 = ((_augval575) < (_val579)) ? (_augval575) : (_val579);
                    }
                    (_a572)._min_ax12 = _augval575;
                    /* _min_ay13 is min of ay1 */
                    var _augval580 = (_a572).ay1;
                    var _child581 = (_a572)._left7;
                    if (!((_child581) == null)) {
                        var _val582 = (_child581)._min_ay13;
                        _augval580 = ((_augval580) < (_val582)) ? (_augval580) : (_val582);
                    }
                    var _child583 = (_a572)._right8;
                    if (!((_child583) == null)) {
                        var _val584 = (_child583)._min_ay13;
                        _augval580 = ((_augval580) < (_val584)) ? (_augval580) : (_val584);
                    }
                    (_a572)._min_ay13 = _augval580;
                    /* _max_ay24 is max of ay2 */
                    var _augval585 = (_a572).ay2;
                    var _child586 = (_a572)._left7;
                    if (!((_child586) == null)) {
                        var _val587 = (_child586)._max_ay24;
                        _augval585 = ((_augval585) < (_val587)) ? (_val587) : (_augval585);
                    }
                    var _child588 = (_a572)._right8;
                    if (!((_child588) == null)) {
                        var _val589 = (_child588)._max_ay24;
                        _augval585 = ((_augval585) < (_val589)) ? (_val589) : (_augval585);
                    }
                    (_a572)._max_ay24 = _augval585;
                    (_a572)._height10 = 1 + ((((((_a572)._left7) == null) ? (-1) : (((_a572)._left7)._height10)) > ((((_a572)._right8) == null) ? (-1) : (((_a572)._right8)._height10))) ? ((((_a572)._left7) == null) ? (-1) : (((_a572)._left7)._height10)) : ((((_a572)._right8) == null) ? (-1) : (((_a572)._right8)._height10)));
                    /* _min_ax12 is min of ax1 */
                    var _augval590 = (_b573).ax1;
                    var _child591 = (_b573)._left7;
                    if (!((_child591) == null)) {
                        var _val592 = (_child591)._min_ax12;
                        _augval590 = ((_augval590) < (_val592)) ? (_augval590) : (_val592);
                    }
                    var _child593 = (_b573)._right8;
                    if (!((_child593) == null)) {
                        var _val594 = (_child593)._min_ax12;
                        _augval590 = ((_augval590) < (_val594)) ? (_augval590) : (_val594);
                    }
                    (_b573)._min_ax12 = _augval590;
                    /* _min_ay13 is min of ay1 */
                    var _augval595 = (_b573).ay1;
                    var _child596 = (_b573)._left7;
                    if (!((_child596) == null)) {
                        var _val597 = (_child596)._min_ay13;
                        _augval595 = ((_augval595) < (_val597)) ? (_augval595) : (_val597);
                    }
                    var _child598 = (_b573)._right8;
                    if (!((_child598) == null)) {
                        var _val599 = (_child598)._min_ay13;
                        _augval595 = ((_augval595) < (_val599)) ? (_augval595) : (_val599);
                    }
                    (_b573)._min_ay13 = _augval595;
                    /* _max_ay24 is max of ay2 */
                    var _augval600 = (_b573).ay2;
                    var _child601 = (_b573)._left7;
                    if (!((_child601) == null)) {
                        var _val602 = (_child601)._max_ay24;
                        _augval600 = ((_augval600) < (_val602)) ? (_val602) : (_augval600);
                    }
                    var _child603 = (_b573)._right8;
                    if (!((_child603) == null)) {
                        var _val604 = (_child603)._max_ay24;
                        _augval600 = ((_augval600) < (_val604)) ? (_val604) : (_augval600);
                    }
                    (_b573)._max_ay24 = _augval600;
                    (_b573)._height10 = 1 + ((((((_b573)._left7) == null) ? (-1) : (((_b573)._left7)._height10)) > ((((_b573)._right8) == null) ? (-1) : (((_b573)._right8)._height10))) ? ((((_b573)._left7) == null) ? (-1) : (((_b573)._left7)._height10)) : ((((_b573)._right8) == null) ? (-1) : (((_b573)._right8)._height10)));
                    if (!(((_b573)._parent9) == null)) {
                        /* _min_ax12 is min of ax1 */
                        var _augval605 = ((_b573)._parent9).ax1;
                        var _child606 = ((_b573)._parent9)._left7;
                        if (!((_child606) == null)) {
                            var _val607 = (_child606)._min_ax12;
                            _augval605 = ((_augval605) < (_val607)) ? (_augval605) : (_val607);
                        }
                        var _child608 = ((_b573)._parent9)._right8;
                        if (!((_child608) == null)) {
                            var _val609 = (_child608)._min_ax12;
                            _augval605 = ((_augval605) < (_val609)) ? (_augval605) : (_val609);
                        }
                        ((_b573)._parent9)._min_ax12 = _augval605;
                        /* _min_ay13 is min of ay1 */
                        var _augval610 = ((_b573)._parent9).ay1;
                        var _child611 = ((_b573)._parent9)._left7;
                        if (!((_child611) == null)) {
                            var _val612 = (_child611)._min_ay13;
                            _augval610 = ((_augval610) < (_val612)) ? (_augval610) : (_val612);
                        }
                        var _child613 = ((_b573)._parent9)._right8;
                        if (!((_child613) == null)) {
                            var _val614 = (_child613)._min_ay13;
                            _augval610 = ((_augval610) < (_val614)) ? (_augval610) : (_val614);
                        }
                        ((_b573)._parent9)._min_ay13 = _augval610;
                        /* _max_ay24 is max of ay2 */
                        var _augval615 = ((_b573)._parent9).ay2;
                        var _child616 = ((_b573)._parent9)._left7;
                        if (!((_child616) == null)) {
                            var _val617 = (_child616)._max_ay24;
                            _augval615 = ((_augval615) < (_val617)) ? (_val617) : (_augval615);
                        }
                        var _child618 = ((_b573)._parent9)._right8;
                        if (!((_child618) == null)) {
                            var _val619 = (_child618)._max_ay24;
                            _augval615 = ((_augval615) < (_val619)) ? (_val619) : (_augval615);
                        }
                        ((_b573)._parent9)._max_ay24 = _augval615;
                        ((_b573)._parent9)._height10 = 1 + (((((((_b573)._parent9)._left7) == null) ? (-1) : ((((_b573)._parent9)._left7)._height10)) > (((((_b573)._parent9)._right8) == null) ? (-1) : ((((_b573)._parent9)._right8)._height10))) ? (((((_b573)._parent9)._left7) == null) ? (-1) : ((((_b573)._parent9)._left7)._height10)) : (((((_b573)._parent9)._right8) == null) ? (-1) : ((((_b573)._parent9)._right8)._height10)));
                    } else {
                        (this)._root1 = _b573;
                    }
                }
                /* rotate (_cursor474)._right8 */
                var _a620 = _cursor474;
                var _b621 = (_a620)._right8;
                var _c622 = (_b621)._left7;
                /* replace _a620 with _b621 in (_a620)._parent9 */
                if (!(((_a620)._parent9) == null)) {
                    if ((((_a620)._parent9)._left7) == (_a620)) {
                        ((_a620)._parent9)._left7 = _b621;
                    } else {
                        ((_a620)._parent9)._right8 = _b621;
                    }
                }
                if (!((_b621) == null)) {
                    (_b621)._parent9 = (_a620)._parent9;
                }
                /* replace _c622 with _a620 in _b621 */
                (_b621)._left7 = _a620;
                if (!((_a620) == null)) {
                    (_a620)._parent9 = _b621;
                }
                /* replace _b621 with _c622 in _a620 */
                (_a620)._right8 = _c622;
                if (!((_c622) == null)) {
                    (_c622)._parent9 = _a620;
                }
                /* _min_ax12 is min of ax1 */
                var _augval623 = (_a620).ax1;
                var _child624 = (_a620)._left7;
                if (!((_child624) == null)) {
                    var _val625 = (_child624)._min_ax12;
                    _augval623 = ((_augval623) < (_val625)) ? (_augval623) : (_val625);
                }
                var _child626 = (_a620)._right8;
                if (!((_child626) == null)) {
                    var _val627 = (_child626)._min_ax12;
                    _augval623 = ((_augval623) < (_val627)) ? (_augval623) : (_val627);
                }
                (_a620)._min_ax12 = _augval623;
                /* _min_ay13 is min of ay1 */
                var _augval628 = (_a620).ay1;
                var _child629 = (_a620)._left7;
                if (!((_child629) == null)) {
                    var _val630 = (_child629)._min_ay13;
                    _augval628 = ((_augval628) < (_val630)) ? (_augval628) : (_val630);
                }
                var _child631 = (_a620)._right8;
                if (!((_child631) == null)) {
                    var _val632 = (_child631)._min_ay13;
                    _augval628 = ((_augval628) < (_val632)) ? (_augval628) : (_val632);
                }
                (_a620)._min_ay13 = _augval628;
                /* _max_ay24 is max of ay2 */
                var _augval633 = (_a620).ay2;
                var _child634 = (_a620)._left7;
                if (!((_child634) == null)) {
                    var _val635 = (_child634)._max_ay24;
                    _augval633 = ((_augval633) < (_val635)) ? (_val635) : (_augval633);
                }
                var _child636 = (_a620)._right8;
                if (!((_child636) == null)) {
                    var _val637 = (_child636)._max_ay24;
                    _augval633 = ((_augval633) < (_val637)) ? (_val637) : (_augval633);
                }
                (_a620)._max_ay24 = _augval633;
                (_a620)._height10 = 1 + ((((((_a620)._left7) == null) ? (-1) : (((_a620)._left7)._height10)) > ((((_a620)._right8) == null) ? (-1) : (((_a620)._right8)._height10))) ? ((((_a620)._left7) == null) ? (-1) : (((_a620)._left7)._height10)) : ((((_a620)._right8) == null) ? (-1) : (((_a620)._right8)._height10)));
                /* _min_ax12 is min of ax1 */
                var _augval638 = (_b621).ax1;
                var _child639 = (_b621)._left7;
                if (!((_child639) == null)) {
                    var _val640 = (_child639)._min_ax12;
                    _augval638 = ((_augval638) < (_val640)) ? (_augval638) : (_val640);
                }
                var _child641 = (_b621)._right8;
                if (!((_child641) == null)) {
                    var _val642 = (_child641)._min_ax12;
                    _augval638 = ((_augval638) < (_val642)) ? (_augval638) : (_val642);
                }
                (_b621)._min_ax12 = _augval638;
                /* _min_ay13 is min of ay1 */
                var _augval643 = (_b621).ay1;
                var _child644 = (_b621)._left7;
                if (!((_child644) == null)) {
                    var _val645 = (_child644)._min_ay13;
                    _augval643 = ((_augval643) < (_val645)) ? (_augval643) : (_val645);
                }
                var _child646 = (_b621)._right8;
                if (!((_child646) == null)) {
                    var _val647 = (_child646)._min_ay13;
                    _augval643 = ((_augval643) < (_val647)) ? (_augval643) : (_val647);
                }
                (_b621)._min_ay13 = _augval643;
                /* _max_ay24 is max of ay2 */
                var _augval648 = (_b621).ay2;
                var _child649 = (_b621)._left7;
                if (!((_child649) == null)) {
                    var _val650 = (_child649)._max_ay24;
                    _augval648 = ((_augval648) < (_val650)) ? (_val650) : (_augval648);
                }
                var _child651 = (_b621)._right8;
                if (!((_child651) == null)) {
                    var _val652 = (_child651)._max_ay24;
                    _augval648 = ((_augval648) < (_val652)) ? (_val652) : (_augval648);
                }
                (_b621)._max_ay24 = _augval648;
                (_b621)._height10 = 1 + ((((((_b621)._left7) == null) ? (-1) : (((_b621)._left7)._height10)) > ((((_b621)._right8) == null) ? (-1) : (((_b621)._right8)._height10))) ? ((((_b621)._left7) == null) ? (-1) : (((_b621)._left7)._height10)) : ((((_b621)._right8) == null) ? (-1) : (((_b621)._right8)._height10)));
                if (!(((_b621)._parent9) == null)) {
                    /* _min_ax12 is min of ax1 */
                    var _augval653 = ((_b621)._parent9).ax1;
                    var _child654 = ((_b621)._parent9)._left7;
                    if (!((_child654) == null)) {
                        var _val655 = (_child654)._min_ax12;
                        _augval653 = ((_augval653) < (_val655)) ? (_augval653) : (_val655);
                    }
                    var _child656 = ((_b621)._parent9)._right8;
                    if (!((_child656) == null)) {
                        var _val657 = (_child656)._min_ax12;
                        _augval653 = ((_augval653) < (_val657)) ? (_augval653) : (_val657);
                    }
                    ((_b621)._parent9)._min_ax12 = _augval653;
                    /* _min_ay13 is min of ay1 */
                    var _augval658 = ((_b621)._parent9).ay1;
                    var _child659 = ((_b621)._parent9)._left7;
                    if (!((_child659) == null)) {
                        var _val660 = (_child659)._min_ay13;
                        _augval658 = ((_augval658) < (_val660)) ? (_augval658) : (_val660);
                    }
                    var _child661 = ((_b621)._parent9)._right8;
                    if (!((_child661) == null)) {
                        var _val662 = (_child661)._min_ay13;
                        _augval658 = ((_augval658) < (_val662)) ? (_augval658) : (_val662);
                    }
                    ((_b621)._parent9)._min_ay13 = _augval658;
                    /* _max_ay24 is max of ay2 */
                    var _augval663 = ((_b621)._parent9).ay2;
                    var _child664 = ((_b621)._parent9)._left7;
                    if (!((_child664) == null)) {
                        var _val665 = (_child664)._max_ay24;
                        _augval663 = ((_augval663) < (_val665)) ? (_val665) : (_augval663);
                    }
                    var _child666 = ((_b621)._parent9)._right8;
                    if (!((_child666) == null)) {
                        var _val667 = (_child666)._max_ay24;
                        _augval663 = ((_augval663) < (_val667)) ? (_val667) : (_augval663);
                    }
                    ((_b621)._parent9)._max_ay24 = _augval663;
                    ((_b621)._parent9)._height10 = 1 + (((((((_b621)._parent9)._left7) == null) ? (-1) : ((((_b621)._parent9)._left7)._height10)) > (((((_b621)._parent9)._right8) == null) ? (-1) : ((((_b621)._parent9)._right8)._height10))) ? (((((_b621)._parent9)._left7) == null) ? (-1) : ((((_b621)._parent9)._left7)._height10)) : (((((_b621)._parent9)._right8) == null) ? (-1) : ((((_b621)._parent9)._right8)._height10)));
                } else {
                    (this)._root1 = _b621;
                }
                _cursor474 = (_cursor474)._parent9;
            }
        }
        (__x).ax2 = new_val;
    }
}
RectangleHolder.prototype.updateAy2 = function (__x, new_val) {
    if ((__x).ay2 != new_val) {
        /* _max_ay24 is max of ay2 */
        var _augval668 = new_val;
        var _child669 = (__x)._left7;
        if (!((_child669) == null)) {
            var _val670 = (_child669)._max_ay24;
            _augval668 = ((_augval668) < (_val670)) ? (_val670) : (_augval668);
        }
        var _child671 = (__x)._right8;
        if (!((_child671) == null)) {
            var _val672 = (_child671)._max_ay24;
            _augval668 = ((_augval668) < (_val672)) ? (_val672) : (_augval668);
        }
        (__x)._max_ay24 = _augval668;
        var _cursor673 = (__x)._parent9;
        var _changed674 = true;
        while ((_changed674) && (!((_cursor673) == (null)))) {
            var _old__max_ay24675 = (_cursor673)._max_ay24;
            var _old_height676 = (_cursor673)._height10;
            /* _max_ay24 is max of ay2 */
            var _augval677 = (_cursor673).ay2;
            var _child678 = (_cursor673)._left7;
            if (!((_child678) == null)) {
                var _val679 = (_child678)._max_ay24;
                _augval677 = ((_augval677) < (_val679)) ? (_val679) : (_augval677);
            }
            var _child680 = (_cursor673)._right8;
            if (!((_child680) == null)) {
                var _val681 = (_child680)._max_ay24;
                _augval677 = ((_augval677) < (_val681)) ? (_val681) : (_augval677);
            }
            (_cursor673)._max_ay24 = _augval677;
            (_cursor673)._height10 = 1 + ((((((_cursor673)._left7) == null) ? (-1) : (((_cursor673)._left7)._height10)) > ((((_cursor673)._right8) == null) ? (-1) : (((_cursor673)._right8)._height10))) ? ((((_cursor673)._left7) == null) ? (-1) : (((_cursor673)._left7)._height10)) : ((((_cursor673)._right8) == null) ? (-1) : (((_cursor673)._right8)._height10)));
            _changed674 = false;
            _changed674 = (_changed674) || (!((_old__max_ay24675) == ((_cursor673)._max_ay24)));
            _changed674 = (_changed674) || (!((_old_height676) == ((_cursor673)._height10)));
            _cursor673 = (_cursor673)._parent9;
        }
        (__x).ay2 = new_val;
    }
}
RectangleHolder.prototype.update = function (__x, ax1, ay1, ax2, ay2) {
    var _parent682 = (__x)._parent9;
    var _left683 = (__x)._left7;
    var _right684 = (__x)._right8;
    var _new_x685;
    if (((_left683) == null) && ((_right684) == null)) {
        _new_x685 = null;
        /* replace __x with _new_x685 in _parent682 */
        if (!((_parent682) == null)) {
            if (((_parent682)._left7) == (__x)) {
                (_parent682)._left7 = _new_x685;
            } else {
                (_parent682)._right8 = _new_x685;
            }
        }
        if (!((_new_x685) == null)) {
            (_new_x685)._parent9 = _parent682;
        }
    } else if ((!((_left683) == null)) && ((_right684) == null)) {
        _new_x685 = _left683;
        /* replace __x with _new_x685 in _parent682 */
        if (!((_parent682) == null)) {
            if (((_parent682)._left7) == (__x)) {
                (_parent682)._left7 = _new_x685;
            } else {
                (_parent682)._right8 = _new_x685;
            }
        }
        if (!((_new_x685) == null)) {
            (_new_x685)._parent9 = _parent682;
        }
    } else if (((_left683) == null) && (!((_right684) == null))) {
        _new_x685 = _right684;
        /* replace __x with _new_x685 in _parent682 */
        if (!((_parent682) == null)) {
            if (((_parent682)._left7) == (__x)) {
                (_parent682)._left7 = _new_x685;
            } else {
                (_parent682)._right8 = _new_x685;
            }
        }
        if (!((_new_x685) == null)) {
            (_new_x685)._parent9 = _parent682;
        }
    } else {
        var _root686 = (__x)._right8;
        var _x687 = _root686;
        var _descend688 = true;
        var _from_left689 = true;
        while (true) {
            if ((_x687) == null) {
                _x687 = null;
                break;
            }
            if (_descend688) {
                /* too small? */
                if (false) {
                    if ((!(((_x687)._right8) == null)) && (true)) {
                        if ((_x687) == (_root686)) {
                            _root686 = (_x687)._right8;
                        }
                        _x687 = (_x687)._right8;
                    } else if ((_x687) == (_root686)) {
                        _x687 = null;
                        break;
                    } else {
                        _descend688 = false;
                        _from_left689 = (!(((_x687)._parent9) == null)) && ((_x687) == (((_x687)._parent9)._left7));
                        _x687 = (_x687)._parent9;
                    }
                } else if ((!(((_x687)._left7) == null)) && (true)) {
                    _x687 = (_x687)._left7;
                    /* too large? */
                } else if (false) {
                    if ((_x687) == (_root686)) {
                        _x687 = null;
                        break;
                    } else {
                        _descend688 = false;
                        _from_left689 = (!(((_x687)._parent9) == null)) && ((_x687) == (((_x687)._parent9)._left7));
                        _x687 = (_x687)._parent9;
                    }
                    /* node ok? */
                } else if (true) {
                    break;
                } else if ((_x687) == (_root686)) {
                    _root686 = (_x687)._right8;
                    _x687 = (_x687)._right8;
                } else {
                    if ((!(((_x687)._right8) == null)) && (true)) {
                        if ((_x687) == (_root686)) {
                            _root686 = (_x687)._right8;
                        }
                        _x687 = (_x687)._right8;
                    } else {
                        _descend688 = false;
                        _from_left689 = (!(((_x687)._parent9) == null)) && ((_x687) == (((_x687)._parent9)._left7));
                        _x687 = (_x687)._parent9;
                    }
                }
            } else if (_from_left689) {
                if (false) {
                    _x687 = null;
                    break;
                } else if (true) {
                    break;
                } else if ((!(((_x687)._right8) == null)) && (true)) {
                    _descend688 = true;
                    if ((_x687) == (_root686)) {
                        _root686 = (_x687)._right8;
                    }
                    _x687 = (_x687)._right8;
                } else if ((_x687) == (_root686)) {
                    _x687 = null;
                    break;
                } else {
                    _descend688 = false;
                    _from_left689 = (!(((_x687)._parent9) == null)) && ((_x687) == (((_x687)._parent9)._left7));
                    _x687 = (_x687)._parent9;
                }
            } else {
                if ((_x687) == (_root686)) {
                    _x687 = null;
                    break;
                } else {
                    _descend688 = false;
                    _from_left689 = (!(((_x687)._parent9) == null)) && ((_x687) == (((_x687)._parent9)._left7));
                    _x687 = (_x687)._parent9;
                }
            }
        }
        _new_x685 = _x687;
        var _mp690 = (_x687)._parent9;
        var _mr691 = (_x687)._right8;
        /* replace _x687 with _mr691 in _mp690 */
        if (!((_mp690) == null)) {
            if (((_mp690)._left7) == (_x687)) {
                (_mp690)._left7 = _mr691;
            } else {
                (_mp690)._right8 = _mr691;
            }
        }
        if (!((_mr691) == null)) {
            (_mr691)._parent9 = _mp690;
        }
        /* replace __x with _x687 in _parent682 */
        if (!((_parent682) == null)) {
            if (((_parent682)._left7) == (__x)) {
                (_parent682)._left7 = _x687;
            } else {
                (_parent682)._right8 = _x687;
            }
        }
        if (!((_x687) == null)) {
            (_x687)._parent9 = _parent682;
        }
        /* replace null with _left683 in _x687 */
        (_x687)._left7 = _left683;
        if (!((_left683) == null)) {
            (_left683)._parent9 = _x687;
        }
        /* replace _mr691 with (__x)._right8 in _x687 */
        (_x687)._right8 = (__x)._right8;
        if (!(((__x)._right8) == null)) {
            ((__x)._right8)._parent9 = _x687;
        }
        /* _min_ax12 is min of ax1 */
        var _augval692 = (_x687).ax1;
        var _child693 = (_x687)._left7;
        if (!((_child693) == null)) {
            var _val694 = (_child693)._min_ax12;
            _augval692 = ((_augval692) < (_val694)) ? (_augval692) : (_val694);
        }
        var _child695 = (_x687)._right8;
        if (!((_child695) == null)) {
            var _val696 = (_child695)._min_ax12;
            _augval692 = ((_augval692) < (_val696)) ? (_augval692) : (_val696);
        }
        (_x687)._min_ax12 = _augval692;
        /* _min_ay13 is min of ay1 */
        var _augval697 = (_x687).ay1;
        var _child698 = (_x687)._left7;
        if (!((_child698) == null)) {
            var _val699 = (_child698)._min_ay13;
            _augval697 = ((_augval697) < (_val699)) ? (_augval697) : (_val699);
        }
        var _child700 = (_x687)._right8;
        if (!((_child700) == null)) {
            var _val701 = (_child700)._min_ay13;
            _augval697 = ((_augval697) < (_val701)) ? (_augval697) : (_val701);
        }
        (_x687)._min_ay13 = _augval697;
        /* _max_ay24 is max of ay2 */
        var _augval702 = (_x687).ay2;
        var _child703 = (_x687)._left7;
        if (!((_child703) == null)) {
            var _val704 = (_child703)._max_ay24;
            _augval702 = ((_augval702) < (_val704)) ? (_val704) : (_augval702);
        }
        var _child705 = (_x687)._right8;
        if (!((_child705) == null)) {
            var _val706 = (_child705)._max_ay24;
            _augval702 = ((_augval702) < (_val706)) ? (_val706) : (_augval702);
        }
        (_x687)._max_ay24 = _augval702;
        (_x687)._height10 = 1 + ((((((_x687)._left7) == null) ? (-1) : (((_x687)._left7)._height10)) > ((((_x687)._right8) == null) ? (-1) : (((_x687)._right8)._height10))) ? ((((_x687)._left7) == null) ? (-1) : (((_x687)._left7)._height10)) : ((((_x687)._right8) == null) ? (-1) : (((_x687)._right8)._height10)));
        var _cursor707 = _mp690;
        var _changed708 = true;
        while ((_changed708) && (!((_cursor707) == (_parent682)))) {
            var _old__min_ax12709 = (_cursor707)._min_ax12;
            var _old__min_ay13710 = (_cursor707)._min_ay13;
            var _old__max_ay24711 = (_cursor707)._max_ay24;
            var _old_height712 = (_cursor707)._height10;
            /* _min_ax12 is min of ax1 */
            var _augval713 = (_cursor707).ax1;
            var _child714 = (_cursor707)._left7;
            if (!((_child714) == null)) {
                var _val715 = (_child714)._min_ax12;
                _augval713 = ((_augval713) < (_val715)) ? (_augval713) : (_val715);
            }
            var _child716 = (_cursor707)._right8;
            if (!((_child716) == null)) {
                var _val717 = (_child716)._min_ax12;
                _augval713 = ((_augval713) < (_val717)) ? (_augval713) : (_val717);
            }
            (_cursor707)._min_ax12 = _augval713;
            /* _min_ay13 is min of ay1 */
            var _augval718 = (_cursor707).ay1;
            var _child719 = (_cursor707)._left7;
            if (!((_child719) == null)) {
                var _val720 = (_child719)._min_ay13;
                _augval718 = ((_augval718) < (_val720)) ? (_augval718) : (_val720);
            }
            var _child721 = (_cursor707)._right8;
            if (!((_child721) == null)) {
                var _val722 = (_child721)._min_ay13;
                _augval718 = ((_augval718) < (_val722)) ? (_augval718) : (_val722);
            }
            (_cursor707)._min_ay13 = _augval718;
            /* _max_ay24 is max of ay2 */
            var _augval723 = (_cursor707).ay2;
            var _child724 = (_cursor707)._left7;
            if (!((_child724) == null)) {
                var _val725 = (_child724)._max_ay24;
                _augval723 = ((_augval723) < (_val725)) ? (_val725) : (_augval723);
            }
            var _child726 = (_cursor707)._right8;
            if (!((_child726) == null)) {
                var _val727 = (_child726)._max_ay24;
                _augval723 = ((_augval723) < (_val727)) ? (_val727) : (_augval723);
            }
            (_cursor707)._max_ay24 = _augval723;
            (_cursor707)._height10 = 1 + ((((((_cursor707)._left7) == null) ? (-1) : (((_cursor707)._left7)._height10)) > ((((_cursor707)._right8) == null) ? (-1) : (((_cursor707)._right8)._height10))) ? ((((_cursor707)._left7) == null) ? (-1) : (((_cursor707)._left7)._height10)) : ((((_cursor707)._right8) == null) ? (-1) : (((_cursor707)._right8)._height10)));
            _changed708 = false;
            _changed708 = (_changed708) || (!((_old__min_ax12709) == ((_cursor707)._min_ax12)));
            _changed708 = (_changed708) || (!((_old__min_ay13710) == ((_cursor707)._min_ay13)));
            _changed708 = (_changed708) || (!((_old__max_ay24711) == ((_cursor707)._max_ay24)));
            _changed708 = (_changed708) || (!((_old_height712) == ((_cursor707)._height10)));
            _cursor707 = (_cursor707)._parent9;
        }
    }
    var _cursor728 = _parent682;
    var _changed729 = true;
    while ((_changed729) && (!((_cursor728) == (null)))) {
        var _old__min_ax12730 = (_cursor728)._min_ax12;
        var _old__min_ay13731 = (_cursor728)._min_ay13;
        var _old__max_ay24732 = (_cursor728)._max_ay24;
        var _old_height733 = (_cursor728)._height10;
        /* _min_ax12 is min of ax1 */
        var _augval734 = (_cursor728).ax1;
        var _child735 = (_cursor728)._left7;
        if (!((_child735) == null)) {
            var _val736 = (_child735)._min_ax12;
            _augval734 = ((_augval734) < (_val736)) ? (_augval734) : (_val736);
        }
        var _child737 = (_cursor728)._right8;
        if (!((_child737) == null)) {
            var _val738 = (_child737)._min_ax12;
            _augval734 = ((_augval734) < (_val738)) ? (_augval734) : (_val738);
        }
        (_cursor728)._min_ax12 = _augval734;
        /* _min_ay13 is min of ay1 */
        var _augval739 = (_cursor728).ay1;
        var _child740 = (_cursor728)._left7;
        if (!((_child740) == null)) {
            var _val741 = (_child740)._min_ay13;
            _augval739 = ((_augval739) < (_val741)) ? (_augval739) : (_val741);
        }
        var _child742 = (_cursor728)._right8;
        if (!((_child742) == null)) {
            var _val743 = (_child742)._min_ay13;
            _augval739 = ((_augval739) < (_val743)) ? (_augval739) : (_val743);
        }
        (_cursor728)._min_ay13 = _augval739;
        /* _max_ay24 is max of ay2 */
        var _augval744 = (_cursor728).ay2;
        var _child745 = (_cursor728)._left7;
        if (!((_child745) == null)) {
            var _val746 = (_child745)._max_ay24;
            _augval744 = ((_augval744) < (_val746)) ? (_val746) : (_augval744);
        }
        var _child747 = (_cursor728)._right8;
        if (!((_child747) == null)) {
            var _val748 = (_child747)._max_ay24;
            _augval744 = ((_augval744) < (_val748)) ? (_val748) : (_augval744);
        }
        (_cursor728)._max_ay24 = _augval744;
        (_cursor728)._height10 = 1 + ((((((_cursor728)._left7) == null) ? (-1) : (((_cursor728)._left7)._height10)) > ((((_cursor728)._right8) == null) ? (-1) : (((_cursor728)._right8)._height10))) ? ((((_cursor728)._left7) == null) ? (-1) : (((_cursor728)._left7)._height10)) : ((((_cursor728)._right8) == null) ? (-1) : (((_cursor728)._right8)._height10)));
        _changed729 = false;
        _changed729 = (_changed729) || (!((_old__min_ax12730) == ((_cursor728)._min_ax12)));
        _changed729 = (_changed729) || (!((_old__min_ay13731) == ((_cursor728)._min_ay13)));
        _changed729 = (_changed729) || (!((_old__max_ay24732) == ((_cursor728)._max_ay24)));
        _changed729 = (_changed729) || (!((_old_height733) == ((_cursor728)._height10)));
        _cursor728 = (_cursor728)._parent9;
    }
    if (((this)._root1) == (__x)) {
        (this)._root1 = _new_x685;
    }
    (__x)._left7 = null;
    (__x)._right8 = null;
    (__x)._min_ax12 = (__x).ax1;
    (__x)._min_ay13 = (__x).ay1;
    (__x)._max_ay24 = (__x).ay2;
    (__x)._height10 = 0;
    var _previous749 = null;
    var _current750 = (this)._root1;
    var _is_left751 = false;
    while (!((_current750) == null)) {
        _previous749 = _current750;
        if ((ax2) < ((_current750).ax2)) {
            _current750 = (_current750)._left7;
            _is_left751 = true;
        } else {
            _current750 = (_current750)._right8;
            _is_left751 = false;
        }
    }
    if ((_previous749) == null) {
        (this)._root1 = __x;
    } else {
        (__x)._parent9 = _previous749;
        if (_is_left751) {
            (_previous749)._left7 = __x;
        } else {
            (_previous749)._right8 = __x;
        }
    }
    var _cursor752 = (__x)._parent9;
    var _changed753 = true;
    while ((_changed753) && (!((_cursor752) == (null)))) {
        var _old__min_ax12754 = (_cursor752)._min_ax12;
        var _old__min_ay13755 = (_cursor752)._min_ay13;
        var _old__max_ay24756 = (_cursor752)._max_ay24;
        var _old_height757 = (_cursor752)._height10;
        /* _min_ax12 is min of ax1 */
        var _augval758 = (_cursor752).ax1;
        var _child759 = (_cursor752)._left7;
        if (!((_child759) == null)) {
            var _val760 = (_child759)._min_ax12;
            _augval758 = ((_augval758) < (_val760)) ? (_augval758) : (_val760);
        }
        var _child761 = (_cursor752)._right8;
        if (!((_child761) == null)) {
            var _val762 = (_child761)._min_ax12;
            _augval758 = ((_augval758) < (_val762)) ? (_augval758) : (_val762);
        }
        (_cursor752)._min_ax12 = _augval758;
        /* _min_ay13 is min of ay1 */
        var _augval763 = (_cursor752).ay1;
        var _child764 = (_cursor752)._left7;
        if (!((_child764) == null)) {
            var _val765 = (_child764)._min_ay13;
            _augval763 = ((_augval763) < (_val765)) ? (_augval763) : (_val765);
        }
        var _child766 = (_cursor752)._right8;
        if (!((_child766) == null)) {
            var _val767 = (_child766)._min_ay13;
            _augval763 = ((_augval763) < (_val767)) ? (_augval763) : (_val767);
        }
        (_cursor752)._min_ay13 = _augval763;
        /* _max_ay24 is max of ay2 */
        var _augval768 = (_cursor752).ay2;
        var _child769 = (_cursor752)._left7;
        if (!((_child769) == null)) {
            var _val770 = (_child769)._max_ay24;
            _augval768 = ((_augval768) < (_val770)) ? (_val770) : (_augval768);
        }
        var _child771 = (_cursor752)._right8;
        if (!((_child771) == null)) {
            var _val772 = (_child771)._max_ay24;
            _augval768 = ((_augval768) < (_val772)) ? (_val772) : (_augval768);
        }
        (_cursor752)._max_ay24 = _augval768;
        (_cursor752)._height10 = 1 + ((((((_cursor752)._left7) == null) ? (-1) : (((_cursor752)._left7)._height10)) > ((((_cursor752)._right8) == null) ? (-1) : (((_cursor752)._right8)._height10))) ? ((((_cursor752)._left7) == null) ? (-1) : (((_cursor752)._left7)._height10)) : ((((_cursor752)._right8) == null) ? (-1) : (((_cursor752)._right8)._height10)));
        _changed753 = false;
        _changed753 = (_changed753) || (!((_old__min_ax12754) == ((_cursor752)._min_ax12)));
        _changed753 = (_changed753) || (!((_old__min_ay13755) == ((_cursor752)._min_ay13)));
        _changed753 = (_changed753) || (!((_old__max_ay24756) == ((_cursor752)._max_ay24)));
        _changed753 = (_changed753) || (!((_old_height757) == ((_cursor752)._height10)));
        _cursor752 = (_cursor752)._parent9;
    }
    /* rebalance AVL tree */
    var _cursor773 = __x;
    var _imbalance774;
    while (!(((_cursor773)._parent9) == null)) {
        _cursor773 = (_cursor773)._parent9;
        (_cursor773)._height10 = 1 + ((((((_cursor773)._left7) == null) ? (-1) : (((_cursor773)._left7)._height10)) > ((((_cursor773)._right8) == null) ? (-1) : (((_cursor773)._right8)._height10))) ? ((((_cursor773)._left7) == null) ? (-1) : (((_cursor773)._left7)._height10)) : ((((_cursor773)._right8) == null) ? (-1) : (((_cursor773)._right8)._height10)));
        _imbalance774 = ((((_cursor773)._left7) == null) ? (-1) : (((_cursor773)._left7)._height10)) - ((((_cursor773)._right8) == null) ? (-1) : (((_cursor773)._right8)._height10));
        if ((_imbalance774) > (1)) {
            if ((((((_cursor773)._left7)._left7) == null) ? (-1) : ((((_cursor773)._left7)._left7)._height10)) < (((((_cursor773)._left7)._right8) == null) ? (-1) : ((((_cursor773)._left7)._right8)._height10))) {
                /* rotate ((_cursor773)._left7)._right8 */
                var _a775 = (_cursor773)._left7;
                var _b776 = (_a775)._right8;
                var _c777 = (_b776)._left7;
                /* replace _a775 with _b776 in (_a775)._parent9 */
                if (!(((_a775)._parent9) == null)) {
                    if ((((_a775)._parent9)._left7) == (_a775)) {
                        ((_a775)._parent9)._left7 = _b776;
                    } else {
                        ((_a775)._parent9)._right8 = _b776;
                    }
                }
                if (!((_b776) == null)) {
                    (_b776)._parent9 = (_a775)._parent9;
                }
                /* replace _c777 with _a775 in _b776 */
                (_b776)._left7 = _a775;
                if (!((_a775) == null)) {
                    (_a775)._parent9 = _b776;
                }
                /* replace _b776 with _c777 in _a775 */
                (_a775)._right8 = _c777;
                if (!((_c777) == null)) {
                    (_c777)._parent9 = _a775;
                }
                /* _min_ax12 is min of ax1 */
                var _augval778 = (_a775).ax1;
                var _child779 = (_a775)._left7;
                if (!((_child779) == null)) {
                    var _val780 = (_child779)._min_ax12;
                    _augval778 = ((_augval778) < (_val780)) ? (_augval778) : (_val780);
                }
                var _child781 = (_a775)._right8;
                if (!((_child781) == null)) {
                    var _val782 = (_child781)._min_ax12;
                    _augval778 = ((_augval778) < (_val782)) ? (_augval778) : (_val782);
                }
                (_a775)._min_ax12 = _augval778;
                /* _min_ay13 is min of ay1 */
                var _augval783 = (_a775).ay1;
                var _child784 = (_a775)._left7;
                if (!((_child784) == null)) {
                    var _val785 = (_child784)._min_ay13;
                    _augval783 = ((_augval783) < (_val785)) ? (_augval783) : (_val785);
                }
                var _child786 = (_a775)._right8;
                if (!((_child786) == null)) {
                    var _val787 = (_child786)._min_ay13;
                    _augval783 = ((_augval783) < (_val787)) ? (_augval783) : (_val787);
                }
                (_a775)._min_ay13 = _augval783;
                /* _max_ay24 is max of ay2 */
                var _augval788 = (_a775).ay2;
                var _child789 = (_a775)._left7;
                if (!((_child789) == null)) {
                    var _val790 = (_child789)._max_ay24;
                    _augval788 = ((_augval788) < (_val790)) ? (_val790) : (_augval788);
                }
                var _child791 = (_a775)._right8;
                if (!((_child791) == null)) {
                    var _val792 = (_child791)._max_ay24;
                    _augval788 = ((_augval788) < (_val792)) ? (_val792) : (_augval788);
                }
                (_a775)._max_ay24 = _augval788;
                (_a775)._height10 = 1 + ((((((_a775)._left7) == null) ? (-1) : (((_a775)._left7)._height10)) > ((((_a775)._right8) == null) ? (-1) : (((_a775)._right8)._height10))) ? ((((_a775)._left7) == null) ? (-1) : (((_a775)._left7)._height10)) : ((((_a775)._right8) == null) ? (-1) : (((_a775)._right8)._height10)));
                /* _min_ax12 is min of ax1 */
                var _augval793 = (_b776).ax1;
                var _child794 = (_b776)._left7;
                if (!((_child794) == null)) {
                    var _val795 = (_child794)._min_ax12;
                    _augval793 = ((_augval793) < (_val795)) ? (_augval793) : (_val795);
                }
                var _child796 = (_b776)._right8;
                if (!((_child796) == null)) {
                    var _val797 = (_child796)._min_ax12;
                    _augval793 = ((_augval793) < (_val797)) ? (_augval793) : (_val797);
                }
                (_b776)._min_ax12 = _augval793;
                /* _min_ay13 is min of ay1 */
                var _augval798 = (_b776).ay1;
                var _child799 = (_b776)._left7;
                if (!((_child799) == null)) {
                    var _val800 = (_child799)._min_ay13;
                    _augval798 = ((_augval798) < (_val800)) ? (_augval798) : (_val800);
                }
                var _child801 = (_b776)._right8;
                if (!((_child801) == null)) {
                    var _val802 = (_child801)._min_ay13;
                    _augval798 = ((_augval798) < (_val802)) ? (_augval798) : (_val802);
                }
                (_b776)._min_ay13 = _augval798;
                /* _max_ay24 is max of ay2 */
                var _augval803 = (_b776).ay2;
                var _child804 = (_b776)._left7;
                if (!((_child804) == null)) {
                    var _val805 = (_child804)._max_ay24;
                    _augval803 = ((_augval803) < (_val805)) ? (_val805) : (_augval803);
                }
                var _child806 = (_b776)._right8;
                if (!((_child806) == null)) {
                    var _val807 = (_child806)._max_ay24;
                    _augval803 = ((_augval803) < (_val807)) ? (_val807) : (_augval803);
                }
                (_b776)._max_ay24 = _augval803;
                (_b776)._height10 = 1 + ((((((_b776)._left7) == null) ? (-1) : (((_b776)._left7)._height10)) > ((((_b776)._right8) == null) ? (-1) : (((_b776)._right8)._height10))) ? ((((_b776)._left7) == null) ? (-1) : (((_b776)._left7)._height10)) : ((((_b776)._right8) == null) ? (-1) : (((_b776)._right8)._height10)));
                if (!(((_b776)._parent9) == null)) {
                    /* _min_ax12 is min of ax1 */
                    var _augval808 = ((_b776)._parent9).ax1;
                    var _child809 = ((_b776)._parent9)._left7;
                    if (!((_child809) == null)) {
                        var _val810 = (_child809)._min_ax12;
                        _augval808 = ((_augval808) < (_val810)) ? (_augval808) : (_val810);
                    }
                    var _child811 = ((_b776)._parent9)._right8;
                    if (!((_child811) == null)) {
                        var _val812 = (_child811)._min_ax12;
                        _augval808 = ((_augval808) < (_val812)) ? (_augval808) : (_val812);
                    }
                    ((_b776)._parent9)._min_ax12 = _augval808;
                    /* _min_ay13 is min of ay1 */
                    var _augval813 = ((_b776)._parent9).ay1;
                    var _child814 = ((_b776)._parent9)._left7;
                    if (!((_child814) == null)) {
                        var _val815 = (_child814)._min_ay13;
                        _augval813 = ((_augval813) < (_val815)) ? (_augval813) : (_val815);
                    }
                    var _child816 = ((_b776)._parent9)._right8;
                    if (!((_child816) == null)) {
                        var _val817 = (_child816)._min_ay13;
                        _augval813 = ((_augval813) < (_val817)) ? (_augval813) : (_val817);
                    }
                    ((_b776)._parent9)._min_ay13 = _augval813;
                    /* _max_ay24 is max of ay2 */
                    var _augval818 = ((_b776)._parent9).ay2;
                    var _child819 = ((_b776)._parent9)._left7;
                    if (!((_child819) == null)) {
                        var _val820 = (_child819)._max_ay24;
                        _augval818 = ((_augval818) < (_val820)) ? (_val820) : (_augval818);
                    }
                    var _child821 = ((_b776)._parent9)._right8;
                    if (!((_child821) == null)) {
                        var _val822 = (_child821)._max_ay24;
                        _augval818 = ((_augval818) < (_val822)) ? (_val822) : (_augval818);
                    }
                    ((_b776)._parent9)._max_ay24 = _augval818;
                    ((_b776)._parent9)._height10 = 1 + (((((((_b776)._parent9)._left7) == null) ? (-1) : ((((_b776)._parent9)._left7)._height10)) > (((((_b776)._parent9)._right8) == null) ? (-1) : ((((_b776)._parent9)._right8)._height10))) ? (((((_b776)._parent9)._left7) == null) ? (-1) : ((((_b776)._parent9)._left7)._height10)) : (((((_b776)._parent9)._right8) == null) ? (-1) : ((((_b776)._parent9)._right8)._height10)));
                } else {
                    (this)._root1 = _b776;
                }
            }
            /* rotate (_cursor773)._left7 */
            var _a823 = _cursor773;
            var _b824 = (_a823)._left7;
            var _c825 = (_b824)._right8;
            /* replace _a823 with _b824 in (_a823)._parent9 */
            if (!(((_a823)._parent9) == null)) {
                if ((((_a823)._parent9)._left7) == (_a823)) {
                    ((_a823)._parent9)._left7 = _b824;
                } else {
                    ((_a823)._parent9)._right8 = _b824;
                }
            }
            if (!((_b824) == null)) {
                (_b824)._parent9 = (_a823)._parent9;
            }
            /* replace _c825 with _a823 in _b824 */
            (_b824)._right8 = _a823;
            if (!((_a823) == null)) {
                (_a823)._parent9 = _b824;
            }
            /* replace _b824 with _c825 in _a823 */
            (_a823)._left7 = _c825;
            if (!((_c825) == null)) {
                (_c825)._parent9 = _a823;
            }
            /* _min_ax12 is min of ax1 */
            var _augval826 = (_a823).ax1;
            var _child827 = (_a823)._left7;
            if (!((_child827) == null)) {
                var _val828 = (_child827)._min_ax12;
                _augval826 = ((_augval826) < (_val828)) ? (_augval826) : (_val828);
            }
            var _child829 = (_a823)._right8;
            if (!((_child829) == null)) {
                var _val830 = (_child829)._min_ax12;
                _augval826 = ((_augval826) < (_val830)) ? (_augval826) : (_val830);
            }
            (_a823)._min_ax12 = _augval826;
            /* _min_ay13 is min of ay1 */
            var _augval831 = (_a823).ay1;
            var _child832 = (_a823)._left7;
            if (!((_child832) == null)) {
                var _val833 = (_child832)._min_ay13;
                _augval831 = ((_augval831) < (_val833)) ? (_augval831) : (_val833);
            }
            var _child834 = (_a823)._right8;
            if (!((_child834) == null)) {
                var _val835 = (_child834)._min_ay13;
                _augval831 = ((_augval831) < (_val835)) ? (_augval831) : (_val835);
            }
            (_a823)._min_ay13 = _augval831;
            /* _max_ay24 is max of ay2 */
            var _augval836 = (_a823).ay2;
            var _child837 = (_a823)._left7;
            if (!((_child837) == null)) {
                var _val838 = (_child837)._max_ay24;
                _augval836 = ((_augval836) < (_val838)) ? (_val838) : (_augval836);
            }
            var _child839 = (_a823)._right8;
            if (!((_child839) == null)) {
                var _val840 = (_child839)._max_ay24;
                _augval836 = ((_augval836) < (_val840)) ? (_val840) : (_augval836);
            }
            (_a823)._max_ay24 = _augval836;
            (_a823)._height10 = 1 + ((((((_a823)._left7) == null) ? (-1) : (((_a823)._left7)._height10)) > ((((_a823)._right8) == null) ? (-1) : (((_a823)._right8)._height10))) ? ((((_a823)._left7) == null) ? (-1) : (((_a823)._left7)._height10)) : ((((_a823)._right8) == null) ? (-1) : (((_a823)._right8)._height10)));
            /* _min_ax12 is min of ax1 */
            var _augval841 = (_b824).ax1;
            var _child842 = (_b824)._left7;
            if (!((_child842) == null)) {
                var _val843 = (_child842)._min_ax12;
                _augval841 = ((_augval841) < (_val843)) ? (_augval841) : (_val843);
            }
            var _child844 = (_b824)._right8;
            if (!((_child844) == null)) {
                var _val845 = (_child844)._min_ax12;
                _augval841 = ((_augval841) < (_val845)) ? (_augval841) : (_val845);
            }
            (_b824)._min_ax12 = _augval841;
            /* _min_ay13 is min of ay1 */
            var _augval846 = (_b824).ay1;
            var _child847 = (_b824)._left7;
            if (!((_child847) == null)) {
                var _val848 = (_child847)._min_ay13;
                _augval846 = ((_augval846) < (_val848)) ? (_augval846) : (_val848);
            }
            var _child849 = (_b824)._right8;
            if (!((_child849) == null)) {
                var _val850 = (_child849)._min_ay13;
                _augval846 = ((_augval846) < (_val850)) ? (_augval846) : (_val850);
            }
            (_b824)._min_ay13 = _augval846;
            /* _max_ay24 is max of ay2 */
            var _augval851 = (_b824).ay2;
            var _child852 = (_b824)._left7;
            if (!((_child852) == null)) {
                var _val853 = (_child852)._max_ay24;
                _augval851 = ((_augval851) < (_val853)) ? (_val853) : (_augval851);
            }
            var _child854 = (_b824)._right8;
            if (!((_child854) == null)) {
                var _val855 = (_child854)._max_ay24;
                _augval851 = ((_augval851) < (_val855)) ? (_val855) : (_augval851);
            }
            (_b824)._max_ay24 = _augval851;
            (_b824)._height10 = 1 + ((((((_b824)._left7) == null) ? (-1) : (((_b824)._left7)._height10)) > ((((_b824)._right8) == null) ? (-1) : (((_b824)._right8)._height10))) ? ((((_b824)._left7) == null) ? (-1) : (((_b824)._left7)._height10)) : ((((_b824)._right8) == null) ? (-1) : (((_b824)._right8)._height10)));
            if (!(((_b824)._parent9) == null)) {
                /* _min_ax12 is min of ax1 */
                var _augval856 = ((_b824)._parent9).ax1;
                var _child857 = ((_b824)._parent9)._left7;
                if (!((_child857) == null)) {
                    var _val858 = (_child857)._min_ax12;
                    _augval856 = ((_augval856) < (_val858)) ? (_augval856) : (_val858);
                }
                var _child859 = ((_b824)._parent9)._right8;
                if (!((_child859) == null)) {
                    var _val860 = (_child859)._min_ax12;
                    _augval856 = ((_augval856) < (_val860)) ? (_augval856) : (_val860);
                }
                ((_b824)._parent9)._min_ax12 = _augval856;
                /* _min_ay13 is min of ay1 */
                var _augval861 = ((_b824)._parent9).ay1;
                var _child862 = ((_b824)._parent9)._left7;
                if (!((_child862) == null)) {
                    var _val863 = (_child862)._min_ay13;
                    _augval861 = ((_augval861) < (_val863)) ? (_augval861) : (_val863);
                }
                var _child864 = ((_b824)._parent9)._right8;
                if (!((_child864) == null)) {
                    var _val865 = (_child864)._min_ay13;
                    _augval861 = ((_augval861) < (_val865)) ? (_augval861) : (_val865);
                }
                ((_b824)._parent9)._min_ay13 = _augval861;
                /* _max_ay24 is max of ay2 */
                var _augval866 = ((_b824)._parent9).ay2;
                var _child867 = ((_b824)._parent9)._left7;
                if (!((_child867) == null)) {
                    var _val868 = (_child867)._max_ay24;
                    _augval866 = ((_augval866) < (_val868)) ? (_val868) : (_augval866);
                }
                var _child869 = ((_b824)._parent9)._right8;
                if (!((_child869) == null)) {
                    var _val870 = (_child869)._max_ay24;
                    _augval866 = ((_augval866) < (_val870)) ? (_val870) : (_augval866);
                }
                ((_b824)._parent9)._max_ay24 = _augval866;
                ((_b824)._parent9)._height10 = 1 + (((((((_b824)._parent9)._left7) == null) ? (-1) : ((((_b824)._parent9)._left7)._height10)) > (((((_b824)._parent9)._right8) == null) ? (-1) : ((((_b824)._parent9)._right8)._height10))) ? (((((_b824)._parent9)._left7) == null) ? (-1) : ((((_b824)._parent9)._left7)._height10)) : (((((_b824)._parent9)._right8) == null) ? (-1) : ((((_b824)._parent9)._right8)._height10)));
            } else {
                (this)._root1 = _b824;
            }
            _cursor773 = (_cursor773)._parent9;
        } else if ((_imbalance774) < (-1)) {
            if ((((((_cursor773)._right8)._left7) == null) ? (-1) : ((((_cursor773)._right8)._left7)._height10)) > (((((_cursor773)._right8)._right8) == null) ? (-1) : ((((_cursor773)._right8)._right8)._height10))) {
                /* rotate ((_cursor773)._right8)._left7 */
                var _a871 = (_cursor773)._right8;
                var _b872 = (_a871)._left7;
                var _c873 = (_b872)._right8;
                /* replace _a871 with _b872 in (_a871)._parent9 */
                if (!(((_a871)._parent9) == null)) {
                    if ((((_a871)._parent9)._left7) == (_a871)) {
                        ((_a871)._parent9)._left7 = _b872;
                    } else {
                        ((_a871)._parent9)._right8 = _b872;
                    }
                }
                if (!((_b872) == null)) {
                    (_b872)._parent9 = (_a871)._parent9;
                }
                /* replace _c873 with _a871 in _b872 */
                (_b872)._right8 = _a871;
                if (!((_a871) == null)) {
                    (_a871)._parent9 = _b872;
                }
                /* replace _b872 with _c873 in _a871 */
                (_a871)._left7 = _c873;
                if (!((_c873) == null)) {
                    (_c873)._parent9 = _a871;
                }
                /* _min_ax12 is min of ax1 */
                var _augval874 = (_a871).ax1;
                var _child875 = (_a871)._left7;
                if (!((_child875) == null)) {
                    var _val876 = (_child875)._min_ax12;
                    _augval874 = ((_augval874) < (_val876)) ? (_augval874) : (_val876);
                }
                var _child877 = (_a871)._right8;
                if (!((_child877) == null)) {
                    var _val878 = (_child877)._min_ax12;
                    _augval874 = ((_augval874) < (_val878)) ? (_augval874) : (_val878);
                }
                (_a871)._min_ax12 = _augval874;
                /* _min_ay13 is min of ay1 */
                var _augval879 = (_a871).ay1;
                var _child880 = (_a871)._left7;
                if (!((_child880) == null)) {
                    var _val881 = (_child880)._min_ay13;
                    _augval879 = ((_augval879) < (_val881)) ? (_augval879) : (_val881);
                }
                var _child882 = (_a871)._right8;
                if (!((_child882) == null)) {
                    var _val883 = (_child882)._min_ay13;
                    _augval879 = ((_augval879) < (_val883)) ? (_augval879) : (_val883);
                }
                (_a871)._min_ay13 = _augval879;
                /* _max_ay24 is max of ay2 */
                var _augval884 = (_a871).ay2;
                var _child885 = (_a871)._left7;
                if (!((_child885) == null)) {
                    var _val886 = (_child885)._max_ay24;
                    _augval884 = ((_augval884) < (_val886)) ? (_val886) : (_augval884);
                }
                var _child887 = (_a871)._right8;
                if (!((_child887) == null)) {
                    var _val888 = (_child887)._max_ay24;
                    _augval884 = ((_augval884) < (_val888)) ? (_val888) : (_augval884);
                }
                (_a871)._max_ay24 = _augval884;
                (_a871)._height10 = 1 + ((((((_a871)._left7) == null) ? (-1) : (((_a871)._left7)._height10)) > ((((_a871)._right8) == null) ? (-1) : (((_a871)._right8)._height10))) ? ((((_a871)._left7) == null) ? (-1) : (((_a871)._left7)._height10)) : ((((_a871)._right8) == null) ? (-1) : (((_a871)._right8)._height10)));
                /* _min_ax12 is min of ax1 */
                var _augval889 = (_b872).ax1;
                var _child890 = (_b872)._left7;
                if (!((_child890) == null)) {
                    var _val891 = (_child890)._min_ax12;
                    _augval889 = ((_augval889) < (_val891)) ? (_augval889) : (_val891);
                }
                var _child892 = (_b872)._right8;
                if (!((_child892) == null)) {
                    var _val893 = (_child892)._min_ax12;
                    _augval889 = ((_augval889) < (_val893)) ? (_augval889) : (_val893);
                }
                (_b872)._min_ax12 = _augval889;
                /* _min_ay13 is min of ay1 */
                var _augval894 = (_b872).ay1;
                var _child895 = (_b872)._left7;
                if (!((_child895) == null)) {
                    var _val896 = (_child895)._min_ay13;
                    _augval894 = ((_augval894) < (_val896)) ? (_augval894) : (_val896);
                }
                var _child897 = (_b872)._right8;
                if (!((_child897) == null)) {
                    var _val898 = (_child897)._min_ay13;
                    _augval894 = ((_augval894) < (_val898)) ? (_augval894) : (_val898);
                }
                (_b872)._min_ay13 = _augval894;
                /* _max_ay24 is max of ay2 */
                var _augval899 = (_b872).ay2;
                var _child900 = (_b872)._left7;
                if (!((_child900) == null)) {
                    var _val901 = (_child900)._max_ay24;
                    _augval899 = ((_augval899) < (_val901)) ? (_val901) : (_augval899);
                }
                var _child902 = (_b872)._right8;
                if (!((_child902) == null)) {
                    var _val903 = (_child902)._max_ay24;
                    _augval899 = ((_augval899) < (_val903)) ? (_val903) : (_augval899);
                }
                (_b872)._max_ay24 = _augval899;
                (_b872)._height10 = 1 + ((((((_b872)._left7) == null) ? (-1) : (((_b872)._left7)._height10)) > ((((_b872)._right8) == null) ? (-1) : (((_b872)._right8)._height10))) ? ((((_b872)._left7) == null) ? (-1) : (((_b872)._left7)._height10)) : ((((_b872)._right8) == null) ? (-1) : (((_b872)._right8)._height10)));
                if (!(((_b872)._parent9) == null)) {
                    /* _min_ax12 is min of ax1 */
                    var _augval904 = ((_b872)._parent9).ax1;
                    var _child905 = ((_b872)._parent9)._left7;
                    if (!((_child905) == null)) {
                        var _val906 = (_child905)._min_ax12;
                        _augval904 = ((_augval904) < (_val906)) ? (_augval904) : (_val906);
                    }
                    var _child907 = ((_b872)._parent9)._right8;
                    if (!((_child907) == null)) {
                        var _val908 = (_child907)._min_ax12;
                        _augval904 = ((_augval904) < (_val908)) ? (_augval904) : (_val908);
                    }
                    ((_b872)._parent9)._min_ax12 = _augval904;
                    /* _min_ay13 is min of ay1 */
                    var _augval909 = ((_b872)._parent9).ay1;
                    var _child910 = ((_b872)._parent9)._left7;
                    if (!((_child910) == null)) {
                        var _val911 = (_child910)._min_ay13;
                        _augval909 = ((_augval909) < (_val911)) ? (_augval909) : (_val911);
                    }
                    var _child912 = ((_b872)._parent9)._right8;
                    if (!((_child912) == null)) {
                        var _val913 = (_child912)._min_ay13;
                        _augval909 = ((_augval909) < (_val913)) ? (_augval909) : (_val913);
                    }
                    ((_b872)._parent9)._min_ay13 = _augval909;
                    /* _max_ay24 is max of ay2 */
                    var _augval914 = ((_b872)._parent9).ay2;
                    var _child915 = ((_b872)._parent9)._left7;
                    if (!((_child915) == null)) {
                        var _val916 = (_child915)._max_ay24;
                        _augval914 = ((_augval914) < (_val916)) ? (_val916) : (_augval914);
                    }
                    var _child917 = ((_b872)._parent9)._right8;
                    if (!((_child917) == null)) {
                        var _val918 = (_child917)._max_ay24;
                        _augval914 = ((_augval914) < (_val918)) ? (_val918) : (_augval914);
                    }
                    ((_b872)._parent9)._max_ay24 = _augval914;
                    ((_b872)._parent9)._height10 = 1 + (((((((_b872)._parent9)._left7) == null) ? (-1) : ((((_b872)._parent9)._left7)._height10)) > (((((_b872)._parent9)._right8) == null) ? (-1) : ((((_b872)._parent9)._right8)._height10))) ? (((((_b872)._parent9)._left7) == null) ? (-1) : ((((_b872)._parent9)._left7)._height10)) : (((((_b872)._parent9)._right8) == null) ? (-1) : ((((_b872)._parent9)._right8)._height10)));
                } else {
                    (this)._root1 = _b872;
                }
            }
            /* rotate (_cursor773)._right8 */
            var _a919 = _cursor773;
            var _b920 = (_a919)._right8;
            var _c921 = (_b920)._left7;
            /* replace _a919 with _b920 in (_a919)._parent9 */
            if (!(((_a919)._parent9) == null)) {
                if ((((_a919)._parent9)._left7) == (_a919)) {
                    ((_a919)._parent9)._left7 = _b920;
                } else {
                    ((_a919)._parent9)._right8 = _b920;
                }
            }
            if (!((_b920) == null)) {
                (_b920)._parent9 = (_a919)._parent9;
            }
            /* replace _c921 with _a919 in _b920 */
            (_b920)._left7 = _a919;
            if (!((_a919) == null)) {
                (_a919)._parent9 = _b920;
            }
            /* replace _b920 with _c921 in _a919 */
            (_a919)._right8 = _c921;
            if (!((_c921) == null)) {
                (_c921)._parent9 = _a919;
            }
            /* _min_ax12 is min of ax1 */
            var _augval922 = (_a919).ax1;
            var _child923 = (_a919)._left7;
            if (!((_child923) == null)) {
                var _val924 = (_child923)._min_ax12;
                _augval922 = ((_augval922) < (_val924)) ? (_augval922) : (_val924);
            }
            var _child925 = (_a919)._right8;
            if (!((_child925) == null)) {
                var _val926 = (_child925)._min_ax12;
                _augval922 = ((_augval922) < (_val926)) ? (_augval922) : (_val926);
            }
            (_a919)._min_ax12 = _augval922;
            /* _min_ay13 is min of ay1 */
            var _augval927 = (_a919).ay1;
            var _child928 = (_a919)._left7;
            if (!((_child928) == null)) {
                var _val929 = (_child928)._min_ay13;
                _augval927 = ((_augval927) < (_val929)) ? (_augval927) : (_val929);
            }
            var _child930 = (_a919)._right8;
            if (!((_child930) == null)) {
                var _val931 = (_child930)._min_ay13;
                _augval927 = ((_augval927) < (_val931)) ? (_augval927) : (_val931);
            }
            (_a919)._min_ay13 = _augval927;
            /* _max_ay24 is max of ay2 */
            var _augval932 = (_a919).ay2;
            var _child933 = (_a919)._left7;
            if (!((_child933) == null)) {
                var _val934 = (_child933)._max_ay24;
                _augval932 = ((_augval932) < (_val934)) ? (_val934) : (_augval932);
            }
            var _child935 = (_a919)._right8;
            if (!((_child935) == null)) {
                var _val936 = (_child935)._max_ay24;
                _augval932 = ((_augval932) < (_val936)) ? (_val936) : (_augval932);
            }
            (_a919)._max_ay24 = _augval932;
            (_a919)._height10 = 1 + ((((((_a919)._left7) == null) ? (-1) : (((_a919)._left7)._height10)) > ((((_a919)._right8) == null) ? (-1) : (((_a919)._right8)._height10))) ? ((((_a919)._left7) == null) ? (-1) : (((_a919)._left7)._height10)) : ((((_a919)._right8) == null) ? (-1) : (((_a919)._right8)._height10)));
            /* _min_ax12 is min of ax1 */
            var _augval937 = (_b920).ax1;
            var _child938 = (_b920)._left7;
            if (!((_child938) == null)) {
                var _val939 = (_child938)._min_ax12;
                _augval937 = ((_augval937) < (_val939)) ? (_augval937) : (_val939);
            }
            var _child940 = (_b920)._right8;
            if (!((_child940) == null)) {
                var _val941 = (_child940)._min_ax12;
                _augval937 = ((_augval937) < (_val941)) ? (_augval937) : (_val941);
            }
            (_b920)._min_ax12 = _augval937;
            /* _min_ay13 is min of ay1 */
            var _augval942 = (_b920).ay1;
            var _child943 = (_b920)._left7;
            if (!((_child943) == null)) {
                var _val944 = (_child943)._min_ay13;
                _augval942 = ((_augval942) < (_val944)) ? (_augval942) : (_val944);
            }
            var _child945 = (_b920)._right8;
            if (!((_child945) == null)) {
                var _val946 = (_child945)._min_ay13;
                _augval942 = ((_augval942) < (_val946)) ? (_augval942) : (_val946);
            }
            (_b920)._min_ay13 = _augval942;
            /* _max_ay24 is max of ay2 */
            var _augval947 = (_b920).ay2;
            var _child948 = (_b920)._left7;
            if (!((_child948) == null)) {
                var _val949 = (_child948)._max_ay24;
                _augval947 = ((_augval947) < (_val949)) ? (_val949) : (_augval947);
            }
            var _child950 = (_b920)._right8;
            if (!((_child950) == null)) {
                var _val951 = (_child950)._max_ay24;
                _augval947 = ((_augval947) < (_val951)) ? (_val951) : (_augval947);
            }
            (_b920)._max_ay24 = _augval947;
            (_b920)._height10 = 1 + ((((((_b920)._left7) == null) ? (-1) : (((_b920)._left7)._height10)) > ((((_b920)._right8) == null) ? (-1) : (((_b920)._right8)._height10))) ? ((((_b920)._left7) == null) ? (-1) : (((_b920)._left7)._height10)) : ((((_b920)._right8) == null) ? (-1) : (((_b920)._right8)._height10)));
            if (!(((_b920)._parent9) == null)) {
                /* _min_ax12 is min of ax1 */
                var _augval952 = ((_b920)._parent9).ax1;
                var _child953 = ((_b920)._parent9)._left7;
                if (!((_child953) == null)) {
                    var _val954 = (_child953)._min_ax12;
                    _augval952 = ((_augval952) < (_val954)) ? (_augval952) : (_val954);
                }
                var _child955 = ((_b920)._parent9)._right8;
                if (!((_child955) == null)) {
                    var _val956 = (_child955)._min_ax12;
                    _augval952 = ((_augval952) < (_val956)) ? (_augval952) : (_val956);
                }
                ((_b920)._parent9)._min_ax12 = _augval952;
                /* _min_ay13 is min of ay1 */
                var _augval957 = ((_b920)._parent9).ay1;
                var _child958 = ((_b920)._parent9)._left7;
                if (!((_child958) == null)) {
                    var _val959 = (_child958)._min_ay13;
                    _augval957 = ((_augval957) < (_val959)) ? (_augval957) : (_val959);
                }
                var _child960 = ((_b920)._parent9)._right8;
                if (!((_child960) == null)) {
                    var _val961 = (_child960)._min_ay13;
                    _augval957 = ((_augval957) < (_val961)) ? (_augval957) : (_val961);
                }
                ((_b920)._parent9)._min_ay13 = _augval957;
                /* _max_ay24 is max of ay2 */
                var _augval962 = ((_b920)._parent9).ay2;
                var _child963 = ((_b920)._parent9)._left7;
                if (!((_child963) == null)) {
                    var _val964 = (_child963)._max_ay24;
                    _augval962 = ((_augval962) < (_val964)) ? (_val964) : (_augval962);
                }
                var _child965 = ((_b920)._parent9)._right8;
                if (!((_child965) == null)) {
                    var _val966 = (_child965)._max_ay24;
                    _augval962 = ((_augval962) < (_val966)) ? (_val966) : (_augval962);
                }
                ((_b920)._parent9)._max_ay24 = _augval962;
                ((_b920)._parent9)._height10 = 1 + (((((((_b920)._parent9)._left7) == null) ? (-1) : ((((_b920)._parent9)._left7)._height10)) > (((((_b920)._parent9)._right8) == null) ? (-1) : ((((_b920)._parent9)._right8)._height10))) ? (((((_b920)._parent9)._left7) == null) ? (-1) : ((((_b920)._parent9)._left7)._height10)) : (((((_b920)._parent9)._right8) == null) ? (-1) : ((((_b920)._parent9)._right8)._height10)));
            } else {
                (this)._root1 = _b920;
            }
            _cursor773 = (_cursor773)._parent9;
        }
    }
    (__x).ax1 = ax1;
    (__x).ay1 = ay1;
    (__x).ax2 = ax2;
    (__x).ay2 = ay2;
}
RectangleHolder.prototype.findMatchingRectangles = function (bx1, by1, bx2, by2, __callback) {
    var _root967 = (this)._root1;
    var _x968 = _root967;
    var _descend969 = true;
    var _from_left970 = true;
    while (true) {
        if ((_x968) == null) {
            _x968 = null;
            break;
        }
        if (_descend969) {
            /* too small? */
            if ((false) || (((_x968).ax2) <= (bx1))) {
                if ((!(((_x968)._right8) == null)) && ((((true) && ((((_x968)._right8)._min_ax12) < (bx2))) && ((((_x968)._right8)._min_ay13) < (by2))) && ((((_x968)._right8)._max_ay24) > (by1)))) {
                    if ((_x968) == (_root967)) {
                        _root967 = (_x968)._right8;
                    }
                    _x968 = (_x968)._right8;
                } else if ((_x968) == (_root967)) {
                    _x968 = null;
                    break;
                } else {
                    _descend969 = false;
                    _from_left970 = (!(((_x968)._parent9) == null)) && ((_x968) == (((_x968)._parent9)._left7));
                    _x968 = (_x968)._parent9;
                }
            } else if ((!(((_x968)._left7) == null)) && ((((true) && ((((_x968)._left7)._min_ax12) < (bx2))) && ((((_x968)._left7)._min_ay13) < (by2))) && ((((_x968)._left7)._max_ay24) > (by1)))) {
                _x968 = (_x968)._left7;
                /* too large? */
            } else if (false) {
                if ((_x968) == (_root967)) {
                    _x968 = null;
                    break;
                } else {
                    _descend969 = false;
                    _from_left970 = (!(((_x968)._parent9) == null)) && ((_x968) == (((_x968)._parent9)._left7));
                    _x968 = (_x968)._parent9;
                }
                /* node ok? */
            } else if ((((true) && (((_x968).ax1) < (bx2))) && (((_x968).ay1) < (by2))) && (((_x968).ay2) > (by1))) {
                break;
            } else if ((_x968) == (_root967)) {
                _root967 = (_x968)._right8;
                _x968 = (_x968)._right8;
            } else {
                if ((!(((_x968)._right8) == null)) && ((((true) && ((((_x968)._right8)._min_ax12) < (bx2))) && ((((_x968)._right8)._min_ay13) < (by2))) && ((((_x968)._right8)._max_ay24) > (by1)))) {
                    if ((_x968) == (_root967)) {
                        _root967 = (_x968)._right8;
                    }
                    _x968 = (_x968)._right8;
                } else {
                    _descend969 = false;
                    _from_left970 = (!(((_x968)._parent9) == null)) && ((_x968) == (((_x968)._parent9)._left7));
                    _x968 = (_x968)._parent9;
                }
            }
        } else if (_from_left970) {
            if (false) {
                _x968 = null;
                break;
            } else if ((((true) && (((_x968).ax1) < (bx2))) && (((_x968).ay1) < (by2))) && (((_x968).ay2) > (by1))) {
                break;
            } else if ((!(((_x968)._right8) == null)) && ((((true) && ((((_x968)._right8)._min_ax12) < (bx2))) && ((((_x968)._right8)._min_ay13) < (by2))) && ((((_x968)._right8)._max_ay24) > (by1)))) {
                _descend969 = true;
                if ((_x968) == (_root967)) {
                    _root967 = (_x968)._right8;
                }
                _x968 = (_x968)._right8;
            } else if ((_x968) == (_root967)) {
                _x968 = null;
                break;
            } else {
                _descend969 = false;
                _from_left970 = (!(((_x968)._parent9) == null)) && ((_x968) == (((_x968)._parent9)._left7));
                _x968 = (_x968)._parent9;
            }
        } else {
            if ((_x968) == (_root967)) {
                _x968 = null;
                break;
            } else {
                _descend969 = false;
                _from_left970 = (!(((_x968)._parent9) == null)) && ((_x968) == (((_x968)._parent9)._left7));
                _x968 = (_x968)._parent9;
            }
        }
    }
    var _prev_cursor5 = null;
    var _cursor6 = _x968;
    for (; ;) {
        if (!(!((_cursor6) == null))) break;
        var _name971 = _cursor6;
        /* ADVANCE */
        _prev_cursor5 = _cursor6;
        do {
            var _right_min972 = null;
            if ((!(((_cursor6)._right8) == null)) && ((((true) && ((((_cursor6)._right8)._min_ax12) < (bx2))) && ((((_cursor6)._right8)._min_ay13) < (by2))) && ((((_cursor6)._right8)._max_ay24) > (by1)))) {
                var _root973 = (_cursor6)._right8;
                var _x974 = _root973;
                var _descend975 = true;
                var _from_left976 = true;
                while (true) {
                    if ((_x974) == null) {
                        _x974 = null;
                        break;
                    }
                    if (_descend975) {
                        /* too small? */
                        if ((false) || (((_x974).ax2) <= (bx1))) {
                            if ((!(((_x974)._right8) == null)) && ((((true) && ((((_x974)._right8)._min_ax12) < (bx2))) && ((((_x974)._right8)._min_ay13) < (by2))) && ((((_x974)._right8)._max_ay24) > (by1)))) {
                                if ((_x974) == (_root973)) {
                                    _root973 = (_x974)._right8;
                                }
                                _x974 = (_x974)._right8;
                            } else if ((_x974) == (_root973)) {
                                _x974 = null;
                                break;
                            } else {
                                _descend975 = false;
                                _from_left976 = (!(((_x974)._parent9) == null)) && ((_x974) == (((_x974)._parent9)._left7));
                                _x974 = (_x974)._parent9;
                            }
                        } else if ((!(((_x974)._left7) == null)) && ((((true) && ((((_x974)._left7)._min_ax12) < (bx2))) && ((((_x974)._left7)._min_ay13) < (by2))) && ((((_x974)._left7)._max_ay24) > (by1)))) {
                            _x974 = (_x974)._left7;
                            /* too large? */
                        } else if (false) {
                            if ((_x974) == (_root973)) {
                                _x974 = null;
                                break;
                            } else {
                                _descend975 = false;
                                _from_left976 = (!(((_x974)._parent9) == null)) && ((_x974) == (((_x974)._parent9)._left7));
                                _x974 = (_x974)._parent9;
                            }
                            /* node ok? */
                        } else if ((((true) && (((_x974).ax1) < (bx2))) && (((_x974).ay1) < (by2))) && (((_x974).ay2) > (by1))) {
                            break;
                        } else if ((_x974) == (_root973)) {
                            _root973 = (_x974)._right8;
                            _x974 = (_x974)._right8;
                        } else {
                            if ((!(((_x974)._right8) == null)) && ((((true) && ((((_x974)._right8)._min_ax12) < (bx2))) && ((((_x974)._right8)._min_ay13) < (by2))) && ((((_x974)._right8)._max_ay24) > (by1)))) {
                                if ((_x974) == (_root973)) {
                                    _root973 = (_x974)._right8;
                                }
                                _x974 = (_x974)._right8;
                            } else {
                                _descend975 = false;
                                _from_left976 = (!(((_x974)._parent9) == null)) && ((_x974) == (((_x974)._parent9)._left7));
                                _x974 = (_x974)._parent9;
                            }
                        }
                    } else if (_from_left976) {
                        if (false) {
                            _x974 = null;
                            break;
                        } else if ((((true) && (((_x974).ax1) < (bx2))) && (((_x974).ay1) < (by2))) && (((_x974).ay2) > (by1))) {
                            break;
                        } else if ((!(((_x974)._right8) == null)) && ((((true) && ((((_x974)._right8)._min_ax12) < (bx2))) && ((((_x974)._right8)._min_ay13) < (by2))) && ((((_x974)._right8)._max_ay24) > (by1)))) {
                            _descend975 = true;
                            if ((_x974) == (_root973)) {
                                _root973 = (_x974)._right8;
                            }
                            _x974 = (_x974)._right8;
                        } else if ((_x974) == (_root973)) {
                            _x974 = null;
                            break;
                        } else {
                            _descend975 = false;
                            _from_left976 = (!(((_x974)._parent9) == null)) && ((_x974) == (((_x974)._parent9)._left7));
                            _x974 = (_x974)._parent9;
                        }
                    } else {
                        if ((_x974) == (_root973)) {
                            _x974 = null;
                            break;
                        } else {
                            _descend975 = false;
                            _from_left976 = (!(((_x974)._parent9) == null)) && ((_x974) == (((_x974)._parent9)._left7));
                            _x974 = (_x974)._parent9;
                        }
                    }
                }
                _right_min972 = _x974;
            }
            if (!((_right_min972) == null)) {
                _cursor6 = _right_min972;
                break;
            } else {
                while ((!(((_cursor6)._parent9) == null)) && ((_cursor6) == (((_cursor6)._parent9)._right8))) {
                    _cursor6 = (_cursor6)._parent9;
                }
                _cursor6 = (_cursor6)._parent9;
                if ((!((_cursor6) == null)) && (false)) {
                    _cursor6 = null;
                }
            }
        } while ((!((_cursor6) == null)) && (!((((true) && (((_cursor6).ax1) < (bx2))) && (((_cursor6).ay1) < (by2))) && (((_cursor6).ay2) > (by1)))));
        if (__callback(_name971)) {
            var _to_remove977 = _prev_cursor5;
            var _parent978 = (_to_remove977)._parent9;
            var _left979 = (_to_remove977)._left7;
            var _right980 = (_to_remove977)._right8;
            var _new_x981;
            if (((_left979) == null) && ((_right980) == null)) {
                _new_x981 = null;
                /* replace _to_remove977 with _new_x981 in _parent978 */
                if (!((_parent978) == null)) {
                    if (((_parent978)._left7) == (_to_remove977)) {
                        (_parent978)._left7 = _new_x981;
                    } else {
                        (_parent978)._right8 = _new_x981;
                    }
                }
                if (!((_new_x981) == null)) {
                    (_new_x981)._parent9 = _parent978;
                }
            } else if ((!((_left979) == null)) && ((_right980) == null)) {
                _new_x981 = _left979;
                /* replace _to_remove977 with _new_x981 in _parent978 */
                if (!((_parent978) == null)) {
                    if (((_parent978)._left7) == (_to_remove977)) {
                        (_parent978)._left7 = _new_x981;
                    } else {
                        (_parent978)._right8 = _new_x981;
                    }
                }
                if (!((_new_x981) == null)) {
                    (_new_x981)._parent9 = _parent978;
                }
            } else if (((_left979) == null) && (!((_right980) == null))) {
                _new_x981 = _right980;
                /* replace _to_remove977 with _new_x981 in _parent978 */
                if (!((_parent978) == null)) {
                    if (((_parent978)._left7) == (_to_remove977)) {
                        (_parent978)._left7 = _new_x981;
                    } else {
                        (_parent978)._right8 = _new_x981;
                    }
                }
                if (!((_new_x981) == null)) {
                    (_new_x981)._parent9 = _parent978;
                }
            } else {
                var _root982 = (_to_remove977)._right8;
                var _x983 = _root982;
                var _descend984 = true;
                var _from_left985 = true;
                while (true) {
                    if ((_x983) == null) {
                        _x983 = null;
                        break;
                    }
                    if (_descend984) {
                        /* too small? */
                        if (false) {
                            if ((!(((_x983)._right8) == null)) && (true)) {
                                if ((_x983) == (_root982)) {
                                    _root982 = (_x983)._right8;
                                }
                                _x983 = (_x983)._right8;
                            } else if ((_x983) == (_root982)) {
                                _x983 = null;
                                break;
                            } else {
                                _descend984 = false;
                                _from_left985 = (!(((_x983)._parent9) == null)) && ((_x983) == (((_x983)._parent9)._left7));
                                _x983 = (_x983)._parent9;
                            }
                        } else if ((!(((_x983)._left7) == null)) && (true)) {
                            _x983 = (_x983)._left7;
                            /* too large? */
                        } else if (false) {
                            if ((_x983) == (_root982)) {
                                _x983 = null;
                                break;
                            } else {
                                _descend984 = false;
                                _from_left985 = (!(((_x983)._parent9) == null)) && ((_x983) == (((_x983)._parent9)._left7));
                                _x983 = (_x983)._parent9;
                            }
                            /* node ok? */
                        } else if (true) {
                            break;
                        } else if ((_x983) == (_root982)) {
                            _root982 = (_x983)._right8;
                            _x983 = (_x983)._right8;
                        } else {
                            if ((!(((_x983)._right8) == null)) && (true)) {
                                if ((_x983) == (_root982)) {
                                    _root982 = (_x983)._right8;
                                }
                                _x983 = (_x983)._right8;
                            } else {
                                _descend984 = false;
                                _from_left985 = (!(((_x983)._parent9) == null)) && ((_x983) == (((_x983)._parent9)._left7));
                                _x983 = (_x983)._parent9;
                            }
                        }
                    } else if (_from_left985) {
                        if (false) {
                            _x983 = null;
                            break;
                        } else if (true) {
                            break;
                        } else if ((!(((_x983)._right8) == null)) && (true)) {
                            _descend984 = true;
                            if ((_x983) == (_root982)) {
                                _root982 = (_x983)._right8;
                            }
                            _x983 = (_x983)._right8;
                        } else if ((_x983) == (_root982)) {
                            _x983 = null;
                            break;
                        } else {
                            _descend984 = false;
                            _from_left985 = (!(((_x983)._parent9) == null)) && ((_x983) == (((_x983)._parent9)._left7));
                            _x983 = (_x983)._parent9;
                        }
                    } else {
                        if ((_x983) == (_root982)) {
                            _x983 = null;
                            break;
                        } else {
                            _descend984 = false;
                            _from_left985 = (!(((_x983)._parent9) == null)) && ((_x983) == (((_x983)._parent9)._left7));
                            _x983 = (_x983)._parent9;
                        }
                    }
                }
                _new_x981 = _x983;
                var _mp986 = (_x983)._parent9;
                var _mr987 = (_x983)._right8;
                /* replace _x983 with _mr987 in _mp986 */
                if (!((_mp986) == null)) {
                    if (((_mp986)._left7) == (_x983)) {
                        (_mp986)._left7 = _mr987;
                    } else {
                        (_mp986)._right8 = _mr987;
                    }
                }
                if (!((_mr987) == null)) {
                    (_mr987)._parent9 = _mp986;
                }
                /* replace _to_remove977 with _x983 in _parent978 */
                if (!((_parent978) == null)) {
                    if (((_parent978)._left7) == (_to_remove977)) {
                        (_parent978)._left7 = _x983;
                    } else {
                        (_parent978)._right8 = _x983;
                    }
                }
                if (!((_x983) == null)) {
                    (_x983)._parent9 = _parent978;
                }
                /* replace null with _left979 in _x983 */
                (_x983)._left7 = _left979;
                if (!((_left979) == null)) {
                    (_left979)._parent9 = _x983;
                }
                /* replace _mr987 with (_to_remove977)._right8 in _x983 */
                (_x983)._right8 = (_to_remove977)._right8;
                if (!(((_to_remove977)._right8) == null)) {
                    ((_to_remove977)._right8)._parent9 = _x983;
                }
                /* _min_ax12 is min of ax1 */
                var _augval988 = (_x983).ax1;
                var _child989 = (_x983)._left7;
                if (!((_child989) == null)) {
                    var _val990 = (_child989)._min_ax12;
                    _augval988 = ((_augval988) < (_val990)) ? (_augval988) : (_val990);
                }
                var _child991 = (_x983)._right8;
                if (!((_child991) == null)) {
                    var _val992 = (_child991)._min_ax12;
                    _augval988 = ((_augval988) < (_val992)) ? (_augval988) : (_val992);
                }
                (_x983)._min_ax12 = _augval988;
                /* _min_ay13 is min of ay1 */
                var _augval993 = (_x983).ay1;
                var _child994 = (_x983)._left7;
                if (!((_child994) == null)) {
                    var _val995 = (_child994)._min_ay13;
                    _augval993 = ((_augval993) < (_val995)) ? (_augval993) : (_val995);
                }
                var _child996 = (_x983)._right8;
                if (!((_child996) == null)) {
                    var _val997 = (_child996)._min_ay13;
                    _augval993 = ((_augval993) < (_val997)) ? (_augval993) : (_val997);
                }
                (_x983)._min_ay13 = _augval993;
                /* _max_ay24 is max of ay2 */
                var _augval998 = (_x983).ay2;
                var _child999 = (_x983)._left7;
                if (!((_child999) == null)) {
                    var _val1000 = (_child999)._max_ay24;
                    _augval998 = ((_augval998) < (_val1000)) ? (_val1000) : (_augval998);
                }
                var _child1001 = (_x983)._right8;
                if (!((_child1001) == null)) {
                    var _val1002 = (_child1001)._max_ay24;
                    _augval998 = ((_augval998) < (_val1002)) ? (_val1002) : (_augval998);
                }
                (_x983)._max_ay24 = _augval998;
                (_x983)._height10 = 1 + ((((((_x983)._left7) == null) ? (-1) : (((_x983)._left7)._height10)) > ((((_x983)._right8) == null) ? (-1) : (((_x983)._right8)._height10))) ? ((((_x983)._left7) == null) ? (-1) : (((_x983)._left7)._height10)) : ((((_x983)._right8) == null) ? (-1) : (((_x983)._right8)._height10)));
                var _cursor1003 = _mp986;
                var _changed1004 = true;
                while ((_changed1004) && (!((_cursor1003) == (_parent978)))) {
                    var _old__min_ax121005 = (_cursor1003)._min_ax12;
                    var _old__min_ay131006 = (_cursor1003)._min_ay13;
                    var _old__max_ay241007 = (_cursor1003)._max_ay24;
                    var _old_height1008 = (_cursor1003)._height10;
                    /* _min_ax12 is min of ax1 */
                    var _augval1009 = (_cursor1003).ax1;
                    var _child1010 = (_cursor1003)._left7;
                    if (!((_child1010) == null)) {
                        var _val1011 = (_child1010)._min_ax12;
                        _augval1009 = ((_augval1009) < (_val1011)) ? (_augval1009) : (_val1011);
                    }
                    var _child1012 = (_cursor1003)._right8;
                    if (!((_child1012) == null)) {
                        var _val1013 = (_child1012)._min_ax12;
                        _augval1009 = ((_augval1009) < (_val1013)) ? (_augval1009) : (_val1013);
                    }
                    (_cursor1003)._min_ax12 = _augval1009;
                    /* _min_ay13 is min of ay1 */
                    var _augval1014 = (_cursor1003).ay1;
                    var _child1015 = (_cursor1003)._left7;
                    if (!((_child1015) == null)) {
                        var _val1016 = (_child1015)._min_ay13;
                        _augval1014 = ((_augval1014) < (_val1016)) ? (_augval1014) : (_val1016);
                    }
                    var _child1017 = (_cursor1003)._right8;
                    if (!((_child1017) == null)) {
                        var _val1018 = (_child1017)._min_ay13;
                        _augval1014 = ((_augval1014) < (_val1018)) ? (_augval1014) : (_val1018);
                    }
                    (_cursor1003)._min_ay13 = _augval1014;
                    /* _max_ay24 is max of ay2 */
                    var _augval1019 = (_cursor1003).ay2;
                    var _child1020 = (_cursor1003)._left7;
                    if (!((_child1020) == null)) {
                        var _val1021 = (_child1020)._max_ay24;
                        _augval1019 = ((_augval1019) < (_val1021)) ? (_val1021) : (_augval1019);
                    }
                    var _child1022 = (_cursor1003)._right8;
                    if (!((_child1022) == null)) {
                        var _val1023 = (_child1022)._max_ay24;
                        _augval1019 = ((_augval1019) < (_val1023)) ? (_val1023) : (_augval1019);
                    }
                    (_cursor1003)._max_ay24 = _augval1019;
                    (_cursor1003)._height10 = 1 + ((((((_cursor1003)._left7) == null) ? (-1) : (((_cursor1003)._left7)._height10)) > ((((_cursor1003)._right8) == null) ? (-1) : (((_cursor1003)._right8)._height10))) ? ((((_cursor1003)._left7) == null) ? (-1) : (((_cursor1003)._left7)._height10)) : ((((_cursor1003)._right8) == null) ? (-1) : (((_cursor1003)._right8)._height10)));
                    _changed1004 = false;
                    _changed1004 = (_changed1004) || (!((_old__min_ax121005) == ((_cursor1003)._min_ax12)));
                    _changed1004 = (_changed1004) || (!((_old__min_ay131006) == ((_cursor1003)._min_ay13)));
                    _changed1004 = (_changed1004) || (!((_old__max_ay241007) == ((_cursor1003)._max_ay24)));
                    _changed1004 = (_changed1004) || (!((_old_height1008) == ((_cursor1003)._height10)));
                    _cursor1003 = (_cursor1003)._parent9;
                }
            }
            var _cursor1024 = _parent978;
            var _changed1025 = true;
            while ((_changed1025) && (!((_cursor1024) == (null)))) {
                var _old__min_ax121026 = (_cursor1024)._min_ax12;
                var _old__min_ay131027 = (_cursor1024)._min_ay13;
                var _old__max_ay241028 = (_cursor1024)._max_ay24;
                var _old_height1029 = (_cursor1024)._height10;
                /* _min_ax12 is min of ax1 */
                var _augval1030 = (_cursor1024).ax1;
                var _child1031 = (_cursor1024)._left7;
                if (!((_child1031) == null)) {
                    var _val1032 = (_child1031)._min_ax12;
                    _augval1030 = ((_augval1030) < (_val1032)) ? (_augval1030) : (_val1032);
                }
                var _child1033 = (_cursor1024)._right8;
                if (!((_child1033) == null)) {
                    var _val1034 = (_child1033)._min_ax12;
                    _augval1030 = ((_augval1030) < (_val1034)) ? (_augval1030) : (_val1034);
                }
                (_cursor1024)._min_ax12 = _augval1030;
                /* _min_ay13 is min of ay1 */
                var _augval1035 = (_cursor1024).ay1;
                var _child1036 = (_cursor1024)._left7;
                if (!((_child1036) == null)) {
                    var _val1037 = (_child1036)._min_ay13;
                    _augval1035 = ((_augval1035) < (_val1037)) ? (_augval1035) : (_val1037);
                }
                var _child1038 = (_cursor1024)._right8;
                if (!((_child1038) == null)) {
                    var _val1039 = (_child1038)._min_ay13;
                    _augval1035 = ((_augval1035) < (_val1039)) ? (_augval1035) : (_val1039);
                }
                (_cursor1024)._min_ay13 = _augval1035;
                /* _max_ay24 is max of ay2 */
                var _augval1040 = (_cursor1024).ay2;
                var _child1041 = (_cursor1024)._left7;
                if (!((_child1041) == null)) {
                    var _val1042 = (_child1041)._max_ay24;
                    _augval1040 = ((_augval1040) < (_val1042)) ? (_val1042) : (_augval1040);
                }
                var _child1043 = (_cursor1024)._right8;
                if (!((_child1043) == null)) {
                    var _val1044 = (_child1043)._max_ay24;
                    _augval1040 = ((_augval1040) < (_val1044)) ? (_val1044) : (_augval1040);
                }
                (_cursor1024)._max_ay24 = _augval1040;
                (_cursor1024)._height10 = 1 + ((((((_cursor1024)._left7) == null) ? (-1) : (((_cursor1024)._left7)._height10)) > ((((_cursor1024)._right8) == null) ? (-1) : (((_cursor1024)._right8)._height10))) ? ((((_cursor1024)._left7) == null) ? (-1) : (((_cursor1024)._left7)._height10)) : ((((_cursor1024)._right8) == null) ? (-1) : (((_cursor1024)._right8)._height10)));
                _changed1025 = false;
                _changed1025 = (_changed1025) || (!((_old__min_ax121026) == ((_cursor1024)._min_ax12)));
                _changed1025 = (_changed1025) || (!((_old__min_ay131027) == ((_cursor1024)._min_ay13)));
                _changed1025 = (_changed1025) || (!((_old__max_ay241028) == ((_cursor1024)._max_ay24)));
                _changed1025 = (_changed1025) || (!((_old_height1029) == ((_cursor1024)._height10)));
                _cursor1024 = (_cursor1024)._parent9;
            }
            if (((this)._root1) == (_to_remove977)) {
                (this)._root1 = _new_x981;
            }
            _prev_cursor5 = null;
        }
    };
}
